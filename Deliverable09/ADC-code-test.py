import time
import pigpio

# --- Configuration ---
GPIO_VIN_CTRL = 5   # Controls Vin (Ramp Up)
GPIO_VREF_CTRL = 6  # Controls Vref (Ramp Down)
GPIO_COMP_IN = 4    # Comparator Output (LM339)
# Note: Ensure you have a way to discharge the capacitor 
# (e.g., a MOSFET across the cap or waiting for it to bleed)

pi = pigpio.pi()

if not pi.connected:
    exit("Could not connect to pigpio daemon!")

# Pin Setup
pi.set_mode(GPIO_VIN_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_VREF_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_COMP_IN, pigpio.INPUT)

# LM339 is open-collector; pull-up to 3.3V is mandatory
pi.set_pull_up_down(GPIO_COMP_IN, pigpio.PUD_UP)

# Global variables for the callback
t2_stop = 0

def comp_callback(gpio, level, tick):
    global t2_stop
    if level == 0:  # Falling edge detected
        t2_stop = tick

# Setup the callback
cb = pi.callback(GPIO_COMP_IN, pigpio.FALLING_EDGE, comp_callback)

def run_measurement():
    global t2_stop
    t2_stop = 0  # Reset
    
    # --- PHASE 0: RESET/DISCHARGE ---
    # Ensure all switches are off and cap is at baseline
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    time.sleep(0.5) # Allow time for residual charge to dissipate

    # --- PHASE 1: T1 (Integration) ---
    print("Starting Phase 1 (Integration)...")
    pi.write(GPIO_VIN_CTRL, 1)
    time.sleep(0.1)             # Fixed T1 = 100ms
    pi.write(GPIO_VIN_CTRL, 0)  # Stop charging

    # --- PRE-CHECK ---
    # If the comparator isn't HIGH here, the ramp never started or 
    # it's already below the threshold.
    if pi.read(GPIO_COMP_IN) == 0:
        print("Error: Comparator is LOW before T2 starts. Voltage too low or circuit issue.")
        return None

    # --- PHASE 2: T2 (De-integration) ---
    print("Starting Phase 2 (De-integration)...")
    t2_start = pi.get_current_tick() # Start the clock
    pi.write(GPIO_VREF_CTRL, 1)      # Apply Reference voltage
    
    # Wait for the falling edge with a 1-second timeout
    timeout_time = time.time() + 1.0
    while t2_stop == 0:
        if time.time() > timeout_time:
            pi.write(GPIO_VREF_CTRL, 0)
            print("Error: Timeout reached. Comparator never flipped.")
            return None
        time.sleep(0.001)
    
    pi.write(GPIO_VREF_CTRL, 0) # Turn off Reference

    # Calculate duration using hardware ticks (accurate to 1us)
    t2_duration = pigpio.tickDiff(t2_start, t2_stop)
    return t2_duration

# Main Loop
try:
    while True:
        result = run_measurement()
        if result is not None:
            print(f"De-integration time: {result} us")
        print("-" * 30)
        time.sleep(1) # Wait before next reading
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    pi.write(GPIO_VIN_CTRL, 0)
    pi.write(GPIO_VREF_CTRL, 0)
    cb.cancel()
    pi.stop()
