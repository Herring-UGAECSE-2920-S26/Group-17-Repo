import time
import pigpio
import I2C_LCD_driver 

class Voltmeter:

    def __init__(self, pi):
        # --- Configuration ---
        self.GPIO_VIN_CTRL = 5  # Controls Vin MOSFET 
        self.GPIO_VREF_CTRL = 6 # Controls Vref MOSFET
        self.GPIO_COMP_IN = 4   # Comparator Output
        self.GPIO_CAP_RS = 12   # Capacitor reset switch

        self.pi = pi

        # Pin Setup
        self.pi.set_mode(self.GPIO_VIN_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN, pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS, pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_stop = 0
        self.cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    def comp_callback(self, gpio, level, tick):
        if level == 1:
            self.t2_stop = tick

    def run_measurement(self):
        self.t2_stop = 0  # Reset for new run
    
        # --- PHASE 0: RESET ---
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.05)           
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        self.pi.write(self.GPIO_VIN_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.01)           

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VIN_CTRL, 1) 
        time.sleep(.075)            
        self.pi.write(self.GPIO_VIN_CTRL, 0) 
        t1_stop = self.pi.get_current_tick()
    
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))
        time.sleep(0.001)          

        # --- PHASE 2: T2 (De-integration) ---
        t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1)
    
        timeout = time.time() + 0.5 
        while self.t2_stop == 0:
            if time.time() > timeout:
                self.pi.write(self.GPIO_VREF_CTRL, 0)
                return t1_actual, None 
            time.sleep(0.0001)

        self.pi.write(self.GPIO_VREF_CTRL, 0)
        t2_actual = float(pigpio.tickDiff(t2_start, self.t2_stop))
    
        return t1_actual, t2_actual

# --- Main Execution ---
if __name__ == "__main__":

    pi = pigpio.pi()
    lcd = I2C_LCD_driver.lcd()
    voltmeter = Voltmeter(pi)
    
    t1, t2 = voltmeter.run_measurement()

    if t2 is not None:
        # 1. Calculate Vin from T2
        vin = (0.000293 * t2) - 5.21
        
        # 2. Calculate Ohms from Vin (Using ** for power)
        ohms = 300 + (1042 * vin) + (236 * (vin**2))
    
        # --- Terminal Output ---
        print("-" * 30)
        print(f"T1: {t1:.0f} us | T2: {t2:.0f} us")
        print(f"Voltage: {vin:.4f} V")
        print(f"Resistance: {ohms:.2f} Ohms") 
        print("-" * 30)

        # --- LCD Output ---
        lcd.lcd_clear()
        lcd.lcd_display_string(f"Vin: {vin:.2f}V", 1)
        lcd.lcd_display_string(f"Res: {ohms:.1f} Ohm", 2)
    
        if vin > 1.5:
            print("Warning: Voltage is entering the nonlinear clipping region!")
    else:
        print("Measurement Timeout: Integrator did not ramp.")
