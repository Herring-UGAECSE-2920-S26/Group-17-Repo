import time
import pigpio
# import I2C_LCD_driver # Un-comment when ready for LCD

# --- Configuration ---
GPIO_VIN_CTRL = 5  # Controls Vin MOSFET 
GPIO_VREF_CTRL = 6 # Controls Vref MOSFET
GPIO_COMP_IN = 4   # Comparator Output
GPIO_CAP_RS = 12   # Capacitor reset switch

pi = pigpio.pi()

# Pin Setup
pi.set_mode(GPIO_VIN_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_VREF_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_COMP_IN, pigpio.INPUT)
pi.set_mode(GPIO_CAP_RS, pigpio.OUTPUT)
pi.set_pull_up_down(GPIO_COMP_IN, pigpio.PUD_UP)

# Callback variables
t2_stop = 0

def comp_callback(gpio, level, tick):
    global t2_stop
    if level == 1:
        t2_stop = tick

cb = pi.callback(GPIO_COMP_IN, pigpio.RISING_EDGE, comp_callback)

def run_measurement():
    global t2_stop
    t2_stop = 0  # Reset for new run
    
    # --- PHASE 0: RESET ---
    pi.write(GPIO_CAP_RS, 1)
    time.sleep(0.05)           # 50ms is plenty for a dead short
    pi.write(GPIO_CAP_RS, 0)
    
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    time.sleep(0.01)           # Settling time

    # --- PHASE 1: T1 (Integration) ---
    t1_start = pi.get_current_tick()
    pi.write(GPIO_VIN_CTRL, 1) 
    time.sleep(.1)            # Fixed 100ms run-up
    pi.write(GPIO_VIN_CTRL, 0) 
    t1_stop = pi.get_current_tick()
    
    t1_actual = float(pigpio.tickDiff(t1_start, t1_stop))
    time.sleep(0.001)          # Dead time

    # --- PHASE 2: T2 (De-integration) ---
    t2_start = pi.get_current_tick()
    pi.write(GPIO_VREF_CTRL, 1)
    
    timeout = time.time() + 0.5 # 500ms timeout is plenty
    while t2_stop == 0:
        if time.time() > timeout:
            pi.write(GPIO_VREF_CTRL, 0)
            return t1_actual, None # Return None for t2 to indicate timeout
        time.sleep(0.0001)

    pi.write(GPIO_VREF_CTRL, 0)
    t2_actual = float(pigpio.tickDiff(t2_start, t2_stop))
    
    return t1_actual, t2_actual

# --- Main Execution ---
t1, t2 = run_measurement()

if t2 is not None:
    # --- Empirical Calibration Curve ---
    # Derived from breadboard data: Vin = (0.00008544 * t2) - 5.018
    vin = (0.00008544 * t2) - 5.018
    
    print(f"Actual T1: {t1:.0f} us | Actual T2: {t2:.0f} us")
    print(f"Measured Vin: {vin:.4f} V")
    
    if vin > 1.5:
        print("Warning: Voltage is entering the nonlinear clipping region!")
else:
    # If t2 is None, the callback never fired (usually means 0V output from shifter)
    print("Measurement Timeout: Integrator did not ramp. Likely at bottom limit (-5V).")
