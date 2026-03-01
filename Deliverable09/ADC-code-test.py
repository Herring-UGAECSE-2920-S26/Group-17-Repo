import time        # Manages T1 and T2
import pigpio	   # Controls GPIO pins

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

# LM339 needs pull-up to 3.3V
pi.set_pull_up_down(GPIO_COMP_IN, pigpio.PUD_UP)


# Callback variables
t2_start = 0
t2_stop = 0
vref = -6.0

def comp_callback(gpio, level, tick):
	global t2_stop
	# When the comparator crosses zero, record the 'tick'
	if level == 0:
		t2_stop = tick

# Setup the callback to watch for the edge on GPIO 4
cb = pi.callback(GPIO_COMP_IN, pigpio.FALLING_EDGE, comp_callback)

def run_measurement():
	global t2_start, t2_stop
	t2_stop = 0		# Reset for new run
	
	# Ensure everything is OFF before starting
	pi.write(GPIO_VIN_CTRL, 0)
	pi.write(GPIO_VREF_CTRL, 0)
	time.sleep(0.001)

	# --- PHASE 1: T1 (Set Time) ---
	pi.write(GPIO_VIN_CTRL, 1) 	# Start ramp-up
	time.sleep(0.2)			# Ramp-up for 200ms
	pi.write(GPIO_VIN_CTRL, 0)	# Stop ramp-up

	# --- DEAD TIME ---
	# Wait 10 microseconds to ensure P-channel is fully closed
	# time.sleep(0.00001)

	# --- PHASE 2: T2 (Measurement) ---
	t2_start = pi.get_current_tick()	# Hardware timestamp
	pi.write(GPIO_VREF_CTRL, 1)		# Start ramp-down
	
	# Wait for comparator to callback to update t2_stop
	# Use a timeout to prevent infinite loops if circuit fails
	timeout = time.time() + 0.5
	while t2_stop == 0:
		if time.time() > timeout:
			pi.write(GPIO_VREF_CTRL, 0)	# Stop
			return None # Error: Ramp never returned to 0
		time.sleep(0.0001)
	pi.write(GPIO_VREF_CTRL, 0) # Turn off Reference

	# Calculate T2 in microseconds
	t2_duration = pigpio.tickDiff(t2_start, t2_stop)
	return t2_duration

	pi.write(GPIO_CAP_RS, 1) # Turn on capacitor reset switch
	time.sleep(0.0001)
	pi.write(GPIO_CAP_RS, 0)

# Example Usage:
result = run_measurement()
print(f"De-integration time: {result} us")

vin = (-vref)(result/0.2)
print(f"Measured Vin: {vin} V")
