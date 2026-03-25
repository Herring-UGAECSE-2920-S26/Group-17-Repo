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
        # Discharge capacitor
        self.pi.write(self.GPIO_CAP_RS, 1)
        time.sleep(0.05)           
        self.pi.write(self.GPIO_CAP_RS, 0)
    
        # Ensure signal switches are OFF
        self.pi.write(self.GPIO_OHM_CTRL, 0)
        self.pi.write(self.GPIO_VREF_CTRL, 0)
        time.sleep(0.01)           

        # --- PHASE 1: T1 (Integration) ---
        t1_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_OHM_CTRL, 1) # Start ramp using unknown resistor
        time.sleep(0.075)            
        self.pi.write(self.GPIO_OHM_CTRL, 0) # Stop ramp
        t1_stop = self.pi.get_current_tick()
    
        t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))
        
        # --- DEAD TIME ---
        time.sleep(0.001)          

        # --- PHASE 2: T2 (De-integration) ---
        t2_start = self.pi.get_current_tick()
        self.pi.write(self.GPIO_VREF_CTRL, 1) # Start ramp-down using Vref
    
        # Wait for comparator to flip (callback sets t2_stop)
        timeout = time.time() + 1.0 
        while self.t2_stop == 0:
            if time.time() > timeout:
                self.pi.write(self.GPIO_VREF_CTRL, 0)
                return t1_actual, None 
            time.sleep(0.0001)

        self.pi.write(self.GPIO_VREF_CTRL, 0)
        t2_actual = float(pigpio.tickDiff(t2_start, self.t2_stop))
    
        return t1_actual, t2_actual
