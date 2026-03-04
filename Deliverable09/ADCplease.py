import time
import pigpio
import I2C_LCD_driver  # LCD driver enabled

class Voltmeter:
    def __init__(self, pi):
        # --- Configuration ---
        self.GPIO_VIN_CTRL  = 5   # Controls Vin MOSFET
        self.GPIO_VREF_CTRL = 6   # Controls Vref MOSFET
        self.GPIO_COMP_IN   = 4   # Comparator Output
        self.GPIO_CAP_RS    = 12  # Capacitor reset switch
        self.GPIO_OHM_ON    = 13  # Ohmmeter activated
        self.pi = pi

        # LCD Setup
        self.lcd = I2C_LCD_driver.lcd()
        self.lcd.lcd_display_string("Voltmeter Ready", 1)
        self.lcd.lcd_display_string("Initializing...", 2)
        time.sleep(1)
        self.lcd.lcd_clear()

        # Pin Setup
        self.pi.set_mode(self.GPIO_VIN_CTRL,  pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN,   pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS,    pigpio.OUTPUT)
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_stop = 0
        self.cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    def comp_callback(self, gpio, level, tick):
        if level == 1:
            self.t2_stop = tick  # Fixed: use instance variable, not global

    def run_measurement(self):
        self.t2_stop = 0  # Reset for new run

        # --- PHASE 0: RESET ---
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.05)
        self.pi.write(self.GPIO_CAP_RS, 0)

        self.pi.write(self.GPIO_VIN_CTRL,  0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.01)

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VIN_CTRL, 1)
        time.sleep(0.075)
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

    def get_voltage(self):
        t1, t2 = self.run_measurement()
        if t2 is not None:
            vin = (0.0000293 * t2) - 5.21
        else:
            vin = 0
        return vin

    def get_resistance(self):
        t1, t2 = self.run_measurement()
        if t2 is not None:
                vin = (0.0000293 * t2) - 5.21
                resx = (vin * 10000) / 10000
        else:
            vin = 0
            

    def display_result(self, t1, t2):
        """Format and push measurement results to the LCD."""
        if t2 is not None:
            vin = (0.0000293 * t2) - 5.21

            # Line 1: voltage reading (16 chars max)
            line1 = f"Vin: {vin:+.4f} V"

            # Line 2: warning or timing info
            if vin > 1.5:
                line2 = "WARN: Nonlinear!"
            else:
                line2 = f"T1:{t1/1000:.1f} T2:{t2/1000:.1f}ms"

            self.lcd.lcd_display_string(line1[:16], 1)
            self.lcd.lcd_display_string(line2[:16], 2)

            # Also print to terminal
            print(f"Actual T1: {t1:.0f} us | Actual T2: {t2:.0f} us")
            print(f"Measured Vin: {vin:.4f} V")
            if vin > 1.5:
                print("Warning: Voltage is entering the nonlinear clipping region!")

        else:
            self.lcd.lcd_display_string("Timeout: No ramp", 1)
            self.lcd.lcd_display_string("Check input/GND ", 2)
            print("Measurement Timeout: Integrator did not ramp. Likely at bottom limit (-5V).")


# --- Main Execution ---
if __name__ == "__main__":
    pi = pigpio.pi()
    voltmeter = Voltmeter(pi)

    t1, t2 = voltmeter.run_measurement()
    voltmeter.display_result(t1, t2)
