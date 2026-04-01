import RPi.GPIO as GPIO
import time
import spidev

# --- CONFIGURATION ---
FREQ_PIN = 19        # Schmitt Trigger Output
ADC_CHANNEL = 0     # Peak Detector Output
V_REF = 3.3         # Raspberry Pi Logic Level
DIVIDER_RATIO = 3.33 # (7k + 3k) / 3k to scale 3V back to 10V
DIODE_DROP = 0.7    # Voltage lost across 1N4148 diode

# --- SETUP ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(FREQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize SPI for ADC (MCP3008)
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Timing Variables
last_edge_time = 0
measured_freq = 0

# --- CALLBACK FOR FREQUENCY (Simulation 1) ---
def frequency_callback(channel):
    global last_edge_time, measured_freq
    current_time = time.time_ns()
    
    if last_edge_time > 0:
        # Calculate period in seconds
        period = (current_time - last_edge_time) / 1_000_000_000
        if period > 0:
            measured_freq = 1 / period
            
    last_edge_time = current_time

# Attach interrupt to the Schmitt Trigger pulse
GPIO.add_event_detect(FREQ_PIN, GPIO.RISING, callback=frequency_callback)

# --- FUNCTION FOR AMPLITUDE (Simulation 2) ---
def get_amplitude():
    # Read raw 10-bit value from ADC (0-1023)
    adc_raw = spi.xfer2([1, (8 + ADC_CHANNEL) << 4, 0])
    data = ((adc_raw[1] & 3) << 8) + adc_raw[2]
    
    # Convert to actual voltage seen at the Pi pin
    v_at_pi = (data * V_REF) / 1023
    
    # Reverse the hardware math: 
    # 1. Scale back up from the 7k/3k divider
    # 2. Add back the 0.7V lost to the diode
    v_actual = (v_at_pi * DIVIDER_RATIO) + DIODE_DROP
    
    # Requirement Check: Round to the nearest 0.625V step
    stepped_v = round(v_actual / 0.625) * 0.625
    
    # Clamp to project limits (0-10V)
    return max(0, min(10, stepped_v))

# --- MAIN LOOP ---
try:
    print("ECSE 2920 - Group 17 Measurement System")
    print("Press Ctrl+C to exit\n")
    
    while True:
        # Format frequency for 500Hz steps as per requirements
        display_freq = round(measured_freq / 500) * 500
        amp = get_amplitude()
        
        # Output to terminal/UI
        print(f"Measured Frequency: {display_freq:5} Hz | Measured Amplitude: {amp:.3f} V")
        
        time.sleep(0.5) # Update display twice per second

except KeyboardInterrupt:
    print("\nCleaning up GPIO...")
    spi.close()
    GPIO.cleanup()
