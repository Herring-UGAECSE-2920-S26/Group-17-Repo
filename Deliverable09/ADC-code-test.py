import time
import pigpio

# --- Configuration ---
GPIO_VIN_CTRL = 5   
GPIO_VREF_CTRL = 6  
GPIO_COMP_IN = 4    

# Constants for Calculation
VREF = 5.0          # Using absolute value for the ratio math
T1_SECONDS = 0.2    # Time spent charging
T1_US = T1_SECONDS * 1000000 

pi = pigpio.pi()

if not pi.connected:
    print("Error: pigpio daemon not running.")
    exit()

# Pin Setup
pi.set_mode(GPIO_VIN_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_VREF_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_COMP_IN, pigpio.INPUT)
pi.set_pull_up_down(GPIO_COMP_IN, pigpio.PUD_UP)

t2_stop = 0

def comp_callback(gpio, level, tick):
    global t2_stop
    if level == 0:
        t2_stop = tick

cb = pi.callback(GPIO_COMP_IN, pigpio.FALLING_EDGE, comp_callback)

def run_measurement():
    global t2_stop
    t2_stop = 0
    
    # 1. RESET PHASE (Ensures cap starts at 0)
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    time.sleep(0.3) 

    # 2. PHASE 1: INTEGRATION (T1)
    # The integrator output moves UP (Positive)
    print("Phase 1: Charging (T1)...")
    pi.write(GPIO_VIN_CTRL, 1)
    time.sleep(T1_SECONDS) 
    pi.write(GPIO_VIN_CTRL, 0)

    # 3. PRE-CHECK
    if pi.read(GPIO_COMP_IN) == 0:
        print("Error: Comparator LOW. Circuit didn't charge.")
        return None

    # 4. PHASE 2: DE-INTEGRATION (T2)
    # The -5V reference pulls the integrator back DOWN to zero
    print(f"Phase 2: Discharging with Vref (-5V)...")
    t2_start = pi.get_current_tick()
    pi.write(GPIO_VREF_CTRL, 1)
    
    # Timeout can be shorter now since Vref is stronger
    timeout_limit = 2.0 
    start_time = time.time()
    
    while t2_stop == 0:
        if (time.time() - start_time) > timeout_limit:
            pi.write(GPIO_VREF_CTRL, 0)
            print("Error: Timeout. The -5V reference didn't hit zero.")
            return None
        time.sleep(0.001)

    pi.write(GPIO_VREF_CTRL, 0) 

    # 5. CALCULATION
    # Formula: Vin = Vref * (T2 / T1)
    t2_duration_us = pigpio.tickDiff(t2_start, t2_stop)
    vin_calculated = VREF * (t2_duration_us / T1_US)
    
    return t2_duration_us, vin_calculated

# Main Loop
try:
    print(f"Monitoring Vin (Ref: -5V, T1: {T1_SECONDS}s)")
    while True:
        result = run_measurement()
        if result:
            t2_us, vin = result
            print(f">>> T2: {t2_us} us")
            print(f">>> Measured Vin: {vin:.4f} V")
        print("-" * 40)
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    cb.cancel()
    pi.stop()
