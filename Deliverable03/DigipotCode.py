#Digipot theoretical code
import RPi.GPIO as GPIO
import spidev
import time

# 1. Setup SPI for the Potentiometer
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# 2. Setup GPIO for the Button
BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
# Use internal pull-down so the pin is 0 until pressed
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Our 4 values from your lesson
resistances = [100, 1000, 5000, 10000]
current_index = 0

# --- THE INTERRUPT FUNCTION (The ISR) ---
def change_brightness_event(channel):
    global current_index
    
    # Move to the next resistance in the list
    current_index = (current_index + 1) % len(resistances)
    target = resistances[current_index]
    
    # Calculate step (0-128)
    step = int((target / 10000) * 128)
    
    # Send to MCP4131 via SPI
    spi.xfer2([0x00, step])
    
    print(f"Button Pressed! Interrupt Triggered. Resistance set to {target}Ω")

# --- ATTACH THE INTERRUPT ---
# We tell the Pi: "Watch for a RISING edge (0 to 1). When you see it, run the function."
# bouncetime=200 ignores fast 'noisy' clicks within 200ms
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, 
                      callback=change_brightness_event, 
                      bouncetime=200)

try:
    print("System Running. Press the button to change resistance...")
    while True:
        # The Pi is totally free to do other things here!
        time.sleep(1) 
        
except KeyboardInterrupt:
    GPIO.cleanup()
    spi.close()
