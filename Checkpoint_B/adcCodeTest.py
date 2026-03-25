import time         # Manages T1 and T2
import pigpio       # Controls GPIO pins
import I2C_LCD_driver

class Voltmeter:

    # initialize Voltmeter object
    def __init__(self, pi):
        # --- Configuration ---
        self.GPIO_VIN_CTRL = 5   # Controls Vin MOSFET 
        self.GPIO_VREF_CTRL = 6  # Controls Vref MOSFET
        self.GPIO_COMP_IN = 4    # Comparator Output
        self.GPIO_CAP_RS = 12    # Capacitor reset switch
        self.GPIO_OHM_CTRL = 13  # Ohmmeter switch
        self.GPIO_INTERNAL = 16  # Pin used for Internal/External switching

        self.pi = pi

        # Pin Setup
        self.pi.set_mode(self.GPIO_VIN_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_VREF_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_COMP_IN, pigpio.INPUT)
        self.pi.set_mode(self.GPIO_CAP_RS, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_OHM_CTRL, pigpio.OUTPUT)
        self.pi.set_mode(self.GPIO_INTERNAL, pigpio.OUTPUT)

        # Ensure signals are OFF initially
        self.pi.write(self.GPIO_OHM_CTRL, 0)
        self.pi.write(self.GPIO_VIN_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)

        # LM339 needs pull-up to 3.3V
        self.pi.set_pull_up_down(self.GPIO_COMP_IN, pigpio.PUD_UP)

        # Callback variables
        self.t2_start = 0
        self.t2_stop = 0
        self.vref = 6.0

        # Correctly setup the callback referencing the class method
        self.cb = self.pi.callback(self.GPIO_COMP_IN, pigpio.RISING_EDGE, self.comp_callback)

    # Callback function moved outside __init__ so it can be accessed properly
    def comp_callback(self, gpio, level, tick):
        # When the comparator crosses zero, record the 'tick'
        if level == 1:
            self.t2_stop = tick

    # Added 'self' argument to fix the TypeError
    def run_measurement(self):
        self.t2_stop = 0  # Reset for new run
    
        # --- PHASE 0: RESET ---
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.5)           # Give it time to fully clear
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        # Ensure all signal switches are OFF
        self.pi.write(self.GPIO_VIN_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.1)           # Stability pause

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VIN_CTRL, 1)         # Start ramp
        time.sleep(0.075)                            # Fixed integration time
        self.pi.write(self.GPIO_VIN_CTRL, 0)         # Stop ramp
        t1_stop = self.pi.get_current_tick()
    
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))

        # --- DEAD TIME ---
        time.sleep(0.001)

        # --- PHASE 2: T2 (De-integration) ---
        self.t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1)        # Start reference ramp-down
    
        # Wait for comparator to flip
        timeout = time.time() + 5.0                  # Reduced timeout for responsiveness
        while self.t2_stop == 0:
            if time.time() > timeout:
                self.pi.write(self.GPIO_VREF_CTRL, 0)
                return t1_actual, None 
            time.sleep(0.0001)

        self.pi.write(self.GPIO_VREF_CTRL, 0)        # Turn off Reference

        # Calculate T2 in microseconds
        t2_actual = float(pigpio.tickDiff(self.t2_start, self.t2_stop))
    
        return t1_actual, t2_actual

    def get_voltage(self):
        t1, t2 = self.run_measurement()

        if t2 is not None:
            # Empirical Calibration Curve
            vin = -7.41 + 2.61E-04 * t2 + 1.5E-08 * t2**2 - 6.29E-13 * t2**3 + 7.32E-18 * t2**4
            print(f"Actual T1: {t1} us | Actual T2: {t2} us | Vin: {vin:.4f} V")
        else:
            print("Error: Measurement timed out.")
            vin = 0
          
        return vin

    def set_internal(self, level): # 1 = internal; 0 = external
        self.pi.write(self.GPIO_INTERNAL, level)
