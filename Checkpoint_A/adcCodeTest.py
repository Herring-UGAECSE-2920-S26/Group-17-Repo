import time         # Manages T1 and T2
import pigpio       # Controls GPIO pins
import I2C_LCD_driver # https://gist.github.com/DenisFromHR/cc863375a6e19dce359d

# class that allows the measurement of both voltage and resistance
class Voltmeter:
    # initialize Voltmeter object
    def __init__(self, pi):
        # --- Configuration ---
        self.GPIO_VIN_CTRL = 5  # Controls Vin MOSFET 
        self.GPIO_VREF_CTRL = 6 # Controls Vref MOSFET
        self.GPIO_COMP_IN = 4   # Comparator Output
        self.GPIO_CAP_RS = 12   # Capacitor reset switch
        self.GPIO_OHM_CTRL = 13 # Ohmmeter switch

        self.pi = pi

        # pin Setup
        self.pi.set_mode(self.GPIO_VIN_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN, pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_OHM_CTRL, pigpio.OUTPUT)

        # Turn off Ohmmeter GPIO
        self.pi.write(self.GPIO_OHM_CTRL, 0)

        # LM339 needs pull-up to 3.3V
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_start = 0
        self.t2_stop = 0
        self.vref = 6.0

        def comp_callback(GPIO, level, tick):
            # When the comparator crosses zero, record the 'tick'
            if level == 1:
                self.t2_stop = tick

        # Setup the callback to watch for the edge on GPIO 4
        self.cb = pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, comp_callback)

    def run_measurement(self):
        self.t2_stop = 0  # Reset for new run
    
        # --- PHASE 0: RESET (Must be at the start) ---
        # Discharge capacitor to ensure we start at exactly 0V
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.5)           # Give it 50ms to fully clear
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        # Ensure all signal switches are OFF
        self.pi.write(self.GPIO_VIN_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.1)           # Stability pause for the power supply

        # --- PHASE 1: T1 (Integration) ---
        self.t1_start = self.pi.get_current_tick()   # Capture hardware start tick
        self.pi.write(self.GPIO_VIN_CTRL, 1)         # Start ramp
        time.sleep(.075)                             # Target 200ms
        self.pi.write(self.GPIO_VIN_CTRL, 0)         # Stop ramp
        self.t1_stop = self.pi.get_current_tick()    # Capture hardware stop tick
    
        # Calculate actual T1 duration in microseconds
        t1_actual = float(pigpio.tickDiff(self.t1_start, self.t1_stop))

        # --- DEAD TIME ---
        # Increased to 1ms to allow MOSFETs to settle with your supply issues
        time.sleep(0.001)

        # --- PHASE 2: T2 (De-integration) ---
        self.t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1)        # Start reference ramp-down
    
        # Wait for comparator to flip (RISING_EDGE sets t2_stop in callback)
        timeout = time.time() + 15.0        # Increased timeout
        while self.t2_stop == 0:
            if time.time() > timeout:
                self.pi.write(self.GPIO_VREF_CTRL, 0)
                return None, None 
            time.sleep(0.0001)

        self.pi.write(self.GPIO_VREF_CTRL, 0)        # Turn off Reference

        # Calculate T2 in microseconds
        t2_actual = float(pigpio.tickDiff(self.t2_start, self.t2_stop))
    
        return t1_actual, t2_actual

    # function that finds and returns the measured voltage
    def get_voltage(self):
        t1, t2 = self.run_measurement()

        if t1 is not None:
            if t2 < 19552: #negative voltage
                vin = -6.34 + 2.99E-4 *t2 + 1.36E-9 *t2*t2 + 500
                print(f"Actual T1: {t1} us | Actual T2: {t2} us")
                print(f"Measured Vin: {vin:.4f} V")
            else: #positive voltage
                # Vin ( 0.000226* t2) - 5.56
                # Ensure the sign of Vref matches your integrator's direction
                vin = -6.45 +3.61E-4 *t2 + -1.58E-9 *t2*t2
                print(f"Actual T1: {t1} us | Actual T2: {t2} us")
                print(f"Measured Vin: {vin:.4f} V")
            if abs(vin) > 10: vin = 0
        else:
            print("Error: Measurement timed out. The comparator never triggered.")
            print("Check if GPIO 4 is connected and if the integrator is ramping.")
            vin = 0
          
        return vin

    # function that finds and returns the measured resistance
    def get_resistance(self):
        t1, t2 = self.run_measurement()
        
        if t1 is not None:
            # 2. Calculate Ohms from Vin (Using ** for power)
            rin = -22103 + 2.01*t2 + -6.62E-5 *t2*t2 + 9.89E-10 *t2*t2*t2
            print(f"Measured Rin: {rin:.4f} Ohms")
        else: 
            rin = 0
        
        return rin

# --- Main Execution ---
if __name__ == "__main__":
    pi = pigpio.pi()
    lcd = I2C_LCD_driver.lcd()

    voltmeter = Voltmeter(pi)
    voltmeter.get_voltage()
    print("------------")
    voltmeter.get_resistance()
