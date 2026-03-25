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
        
        # LM339 needs pull-up to 3.3V
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_stop = 0
        # Correctly setup the callback referencing the class method
        self.cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    def comp_callback(self, gpio, level, tick):
        # When the comparator crosses zero, record the 'tick'
        if level == 1:
            self.t2_stop = tick

    def run_measurement(self):
        self.t2_stop = 0  # Reset for new run
    
        # --- PHASE 0: RESET ---
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.05)           
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        # Ensure signal switches are OFF
        self.pi.write(self.GPIO_OHM_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.01)           

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_OHM_CTRL, 1) 
        time.sleep(0.075)            
        self.pi.write(self.GPIO_OHM_CTRL, 0) 
        t1_stop = self.pi.get_current_tick()
    
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))
        
        # --- DEAD TIME ---
        time.sleep(0.001)          

        # --- PHASE 2: T2 (De-integration) ---
        t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1)
    
        # Wait for comparator to flip
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
        """Diagnostic version: Prints raw T2 ticks for calibration."""
        t1, t2 = self.run_measurement()

        if t2 is not None:
            # We print the raw T2 value to the terminal
            print(f"DEBUG: Raw T2 Tick Count = {t2}")
            
            # Keep your old math here for now just to see it
            ohms = -8093 + (1.85 * t2) - (4.37e-05 * (t2**2))
            return ohms
        else:
            print("DEBUG: T2 Timeout - No ramp detected")
            return 0.0

# --- Internal test block ---
if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        print("Error: pigpiod not running!")
    else:
        ohm = Ohmmeter(pi)
        print("Testing Ohmmeter... Press Ctrl+C to stop.")
        try:
            while True:
                r = ohm.get_resistance()
                print(f"Resistance: {r:.2f} Ohms")
                time.sleep(0.5)
        except KeyboardInterrupt:
            pi.stop()
