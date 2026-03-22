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

        self.pi = pi

        # Pin Setup
        self.pi.set_mode(self.GPIO_VIN_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN, pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS, pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_stop = 0

        cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    #callback function that keeps track of the stop time
    def comp_callback(self, gpio, level, tick):
        if level == 1:
            self.t2_stop = tick

    #helper function that finds and returns the ramp up and ramp down times
    def run_measurement(self):
        self.t2_stop = 0  # Reset for new run
    
        # --- PHASE 0: RESET ---
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.05)           # 50ms dead short
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        self.pi.write(self.GPIO_VIN_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.01)           # Settling time

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VIN_CTRL, 1) 
        time.sleep(.075)            # Fixed 75 ms run-up
        self.pi.write(self.GPIO_VIN_CTRL, 0) 
        t1_stop = self.pi.get_current_tick()
    
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))
        time.sleep(0.001)          # Dead time

        # --- PHASE 2: T2 (De-integration) ---
        t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1)
    
        timeout = time.time() + 0.5 # 500ms timeout 
        while self.t2_stop == 0:
            if time.time() > timeout:
                self.pi.write(self.GPIO_VREF_CTRL, 0)
                return t1_actual, None # Return None for t2 to indicate timeout
            time.sleep(0.0001)

        self.pi.write(self.GPIO_VREF_CTRL, 0)
        t2_actual = float(pigpio.tickDiff(t2_start, self.t2_stop))
    
        return t1_actual, t2_actual

    #function that finds and returns the measured voltage
    def get_voltage(self):    
        t1, t2 = self.run_measurement()

        if t2 is not None:
            # --- Updated Empirical Calibration Curve ---
            # Vin = (slope * t2) + intercept
            vin = (0.000293 * t2) - 5.21
        else:
            vin = 0

        return vin

#function that finds and returns the measured resistance
def get_resistance(self):
    vin = self.get_voltage()

    if vin != 0:
        # 2. Calculate Ohms from Vin (Using ** for power)
        rin = 300 + (1042 * vin) + (236 * (vin**2))
    else: 
        rin = 0
        
    return rin

# --- Main Execution ---
if __name__ == "__main__":

    pi = pigpio.pi()
    lcd = I2C_LCD_driver.lcd()

    voltmeter = Voltmeter(pi)
    
    t1, t2 = voltmeter.run_measurement()
    volt = voltmeter.get_voltage()
    ohm = voltmeter.get_resistance()

    if t2 is not None:
        # --- Updated Empirical Calibration Curve ---
        # Derived from your latest data: Vin = (slope * t2) + intercept
        # 1. Calculate Vin from T2
        vin = ( 0.000293* t2) - 5.21

        # 2. Calculate Ohms from Vin (Using ** for power)
        ohms = 300 + (1042 * vin) + (236 * (vin**2))
    
        # --- Terminal Output ---
        print("-" * 30)
        print(f"T1: {t1:.0f} us | T2: {t2:.0f} us")
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
