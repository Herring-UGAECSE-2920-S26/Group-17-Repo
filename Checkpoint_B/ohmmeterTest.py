import time         # Manages T1 and T2
import pigpio       # Controls GPIO pins
import I2C_LCD_driver 

class Ohmmeter:

    def __init__(self, pi):
        # --- Configuration ---
        self.GPIO_OHM_CTRL = 13  # Controls Ohmmeter MOSFET 
        self.GPIO_VREF_CTRL = 6  # Controls Vref MOSFET
        self.GPIO_COMP_IN = 4    # Comparator Output
        self.GPIO_CAP_RS = 12    # Capacitor reset switch

        self.pi = pi

        # Pin Setup
        self.pi.set_mode(self.GPIO_OHM_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN, pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS, pigpio.OUTPUT)
        
        # LM339 comparator needs pull-up to 3.3V logic levels
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_stop = 0
        # Correctly setup the hardware callback referencing the class method
        self.cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    def comp_callback(self, gpio, level, tick):
        # When the comparator crosses zero (RISING_EDGE), record the hardware tick
        if level == 1:
            self.t2_stop = tick

    def run_measurement(self):
        self.t2_stop = 0  # Reset tick tracker for new run
    
        # --- PHASE 0: RESET ---
        # Fully discharge capacitor to start at 0V
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.05)           
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        # Ensure signal switches are OFF before starting integration
        self.pi.write(self.GPIO_OHM_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.01)           

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_OHM_CTRL, 1)  # Apply unknown resistor
        time.sleep(0.075)                     # Integration time constant
        self.pi.write(self.GPIO_OHM_CTRL, 0)  # Stop charging
        t1_stop = self.pi.get_current_tick()
    
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))
        
        # Dead time to allow MOSFETs to fully settle
        time.sleep(0.001)          

        # --- PHASE 2: T2 (De-integration) ---
        t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1) # Start ramp-down with Vref
    
        # Wait for the hardware callback to trigger the comparator flip
        timeout = time.time() + 1.0 
        while self.t2_stop == 0:
            if time.time() > timeout:
                self.pi.write(self.GPIO_VREF_CTRL, 0)
                return t1_actual, None 
            time.sleep(0.0001)

        self.pi.write(self.GPIO_VREF_CTRL, 0)
        t2_actual = float(pigpio.tickDiff(t2_start, self.t2_stop))
    
        return t1_actual, t2_actual

    def get_resistance(self):
        """Calculates and returns resistance using your characterized equation."""
        t1, t2 = self.run_measurement()

        if t2 is not None:
            # Using the exact equation from your provided image:
            # ohms = -8093 + 1.85 * t2 - 4.37E-05 * t2^2
            ohms = -8093 + (1.85 * t2) - (4.37e-05 * (t2**2))
            
            # --- Terminal Output ---
            print("-" * 30)
            print(f"T1 (Charging): {t1:.0f} us")
            print(f"T2 (Discharge): {t2:.0f} us")
            print(f"Calculated Resistance: {ohms:.2f} Ohms") 
            print("-" * 30)
            
            # Keep reading realistic; if T2 is too low, don't return negative ohms
            return max(0, ohms)
        else:
            print("Ohmmeter Error: Measurement Timeout (Integrator did not ramp).")
            return 0.0

# --- Standalone Test Execution ---
if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        print("CRITICAL ERROR: Could not connect to pigpiod. Run 'sudo pigpiod' first.")
    else:
        ohm_meter = Ohmmeter(pi)
        print("Standalone Ohmmeter Mode Active. Press Ctrl+C to exit.")
        try:
            while True:
                res_value = ohm_meter.get_resistance()
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down ohmmeter.")
            pi.stop()
