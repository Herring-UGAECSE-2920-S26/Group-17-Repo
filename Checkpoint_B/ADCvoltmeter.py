import time
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d

#class that allows the measurement of both voltage and resistance
class Voltmeter:

    #initialize Voltmeter object
    def __init__(self, pi):
    # --- Configuration ---
        self.GPIO_VIN_CTRL = 5  # Controls Vin MOSFET 
        self.GPIO_VREF_CTRL = 6 # Controls Vref MOSFET
        self.GPIO_COMP_IN = 4   # Comparator Output
        self.GPIO_CAP_RS = 12   # Capacitor reset switch
        self.GPIO_OHM_ON = 13   # Ohmmeter activated
        self.GPIO_INTERNAL = 16 # Selects internal/external measurements
        self.pi = pi

        # Pin Setup
        self.pi.set_mode(self.GPIO_VIN_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN, pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS, pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)
        self.pi.set_mode(self.GPIO_INTERNAL, pigpio.OUTPUT)

        # Callback variables
        self.t2_stop = 0

        cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    #callback function that keeps track of the stop time
    def comp_callback(self, gpio, level, tick):
        if level == 1:
            self.t2_stop = tick

    #helper function that finds and returns the ramp up and ramp down times
    def run_measurement(self, gpio):
        global t2_start, t2_stop
        t2_stop = 0  # Reset for new run
    
        # --- PHASE 0: RESET (Must be at the start) ---
        # Discharge capacitor to ensure we start at exactly 0V
        pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.5)           # Give it 50ms to fully clear
        pi.write(self.GPIO_CAP_RS, 0)
    
        # Ensure all signal switches are OFF
        pi.write(gpio, 0)
        pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.1)           # Stability pause for the power supply

        # --- PHASE 1: T1 (Integration) ---
        t1_start = pi.get_current_tick()   # Capture hardware start tick
        pi.write(gpio, 1)         # Start ramp
        time.sleep(.075)                    # Target 200ms
        pi.write(gpio, 0)         # Stop ramp
        t1_stop = pi.get_current_tick()    # Capture hardware stop tick
    
        # Calculate actual T1 duration in microseconds
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))

        # --- DEAD TIME ---
        # Increased to 1ms to allow MOSFETs to settle with your supply issues
        time.sleep(0.001)

        # --- PHASE 2: T2 (De-integration) ---
        t2_start = pi.get_current_tick()
        pi.write(self.GPIO_VREF_CTRL, 1)        # Start reference ramp-down
    
        # Wait for comparator to flip (RISING_EDGE sets t2_stop in callback)
        timeout = time.time() + 15.0        # Increased timeout
        while t2_stop == 0:
            if time.time() > timeout:
                pi.write(self.GPIO_VREF_CTRL, 0)
                return None, None 
            time.sleep(0.0001)

        pi.write(self.GPIO_VREF_CTRL, 0)        # Turn off Reference

        # Calculate T2 in microseconds
        t2_actual = float(pigpio.tickDiff(t2_start, t2_stop))
    
        return t1_actual, t2_actual

    #function that finds and returns the measured voltage
    def get_voltage(self):    
        t1, t2 = self.run_measurement(self.GPIO_VIN_CTRL)

        if t2 is not None:
            # --- Updated Empirical Calibration Curve ---
            # Vin = (slope * t2) + intercept
            vin = -6.83 + 2.71E-04 * t2 + 1.03E-08 * t2**2 - 4.56E-13 * t2**3 + 5.59E-18 * t2**4
        else:
            vin = 0

        return vin

    #function that finds and returns the measured resistance
    def get_resistance(self):
        t1, t2 = self.run_measurement(self.GPIO_OHM_ON)

        if t2 is not None:
            # 2. Calculate Ohms from Vin (Using ** for power)
            rin = -8093 + 1.85 * t2 - 4.37E-05 * t2**2
        else: 
            rin = 0
        
        return rin

    #function that selects either internal or external voltage input
    def set_internal(self, level): #1 = internal; 0 = external
        self.pi.write(self.GPIO_INTERNAL, level)

# --- Main Execution ---
if __name__ == "__main__":

    pi = pigpio.pi()
    lcd = I2C_LCD_driver.lcd()

    GPIO_VIN_CTRL = 5
    GPIO_OHM_ON = 13

    voltmeter = Voltmeter(pi)
    
    t1v, t2v = voltmeter.run_measurement(GPIO_VIN_CTRL)
    t1r, t2r = voltmeter.run_measurement(GPIO_OHM_ON)
    volt = voltmeter.get_voltage()
    ohm = voltmeter.get_resistance()

    if t2v is not None:
        # --- Updated Empirical Calibration Curve ---
        # Derived from your latest data: Vin = (slope * t2) + intercept
        # 1. Calculate Vin from T2
        vin = -6.83 + 2.71E-04 * t2 + 1.03E-08 * t2**2 - 4.56E-13 * t2**3 + 5.59E-18 * t2**4

        # 2. Calculate Ohms from Vin (Using ** for power)
        ohms = -8093 + 1.85 * t2r - 4.37E-05 * t2r**2
    
        # --- Terminal Output ---
        print("-" * 30)
        print(f"T1: {t1v:.0f} us | T2: {t2v:.0f} us")
        print(f"Voltage: {vin:.4f} V")
        print(f"Resistance: {ohms:.2f} Ohms") 
        print("-" * 30)
        print("Function Results")
        print(f"Voltage: {volt:.4f} V")
        print(f"Resistance: {ohm:.2f} Ohms")
        print("-" * 30)

        # --- LCD Output ---
        lcd.lcd_clear()
        lcd.lcd_display_string(f"Vin: {vin:.2f}V", 1)
        lcd.lcd_display_string(f"Res: {ohms:.1f} Ohm", 2)
    
        if vin > 1.5:
            print("Warning: Voltage is entering the nonlinear clipping region!")
    else:
        # If t2 is None, the callback never fired (usually means 0V output from shifter)
        print("Measurement Timeout: Integrator did not ramp. Likely at bottom limit (-5V).")
