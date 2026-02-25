import time
import pigpio

# --- Configuration ---
GPIO_VIN_CTRL = 5   
GPIO_VREF_CTRL = 6  
GPIO_COMP_IN = 4    

pi = pigpio.pi()

if not pi.connected:
    print("Error: pigpio daemon not running. Run 'sudo pigpiod'")
    exit()

# Pin Setup
pi.set_mode(GPIO_VIN_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_VREF_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_COMP_IN, pigpio.INPUT)
pi.set_pull_up_down(GPIO_COMP_IN, pigpio.PUD_UP)

# Global for the callback
t2_stop = 0

def comp_callback(gpio, level, tick):
    global t2_stop
    if level == 0:  # Falling edge (crossing zero)
        t2_stop = tick

cb = pi.callback(GPIO_COMP_IN, pigpio.FALLING_EDGE, comp_callback)

def run_measurement():
    global t2_stop
    t2_stop = 0
    
    # 1. RESET PHASE
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    time.sleep(0.2) 

    # 2. PHASE 1: INTEGRATION (T1)
    print("Phase 1: Charging...")
    pi.write(GPIO_VIN_CTRL, 1)
    time.sleep(0.1)             # 100ms integration
    pi.write(GPIO_VIN_CTRL, 0)

    # 3. PRE-CHECK: Is the ramp actually above zero?
    comp_state = pi.read(GPIO_COMP_IN)
    if comp_state == 0:
        print("Error: Comparator is LOW before Phase 2. Ramp failed to rise.")
        return None

    # 4. PHASE 2: DE-INTEGRATION (T2)
    print(f"Phase 2: Discharging with Vref (-0.8V)...")
    t2_start = pi.get_current_tick()
    pi.write(GPIO_VREF_CTRL, 1)
    
    # Use a 3-second timeout because Vref is small (-0.8V)
    timeout_limit = 3.0
    start_time = time.time()
    
    while t2_stop == 0:
        elapsed = time.time() - start_time
        
        # Diagnostic: Print status every 500ms so we aren't "blind"
        if int(elapsed * 10) % 5 == 0 and elapsed > 0.1:
            print(f"  ...Still waiting. Pin {GPIO_COMP_IN} state: {pi.read(GPIO_COMP_IN)}")

        if elapsed > timeout_limit:
            pi.write(GPIO_VREF_CTRL, 0)
            print("Error: Timeout! Comparator never flipped to 0.")
            return None
        
        time.sleep(0.01) # Small sleep to prevent CPU hogging

    pi.write(GPIO_VREF_CTRL, 0) # Turn off Reference

    # 5. CALCULATION
    t2_duration = pigpio.tickDiff(t2_start, t2_stop)
    return t2_duration

# Main Loop
try:
    print("Starting Dual-Slope ADC Sequence. Press Ctrl+C to stop.")
    while True:
        result = run_measurement()
        if result:
            print(f">>> SUCCESS: T2 = {result} us")
        print("-" * 40)
        time.sleep(1.5)
except KeyboardInterrupt:
    print("\nCleaning up...")
finally:
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    cb.cancel()
    pi.stop()
