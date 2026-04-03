import RPi.GPIO as GPIO
import time
GPIO_PIN = 27 

# Global variable to hold our pulse count
pulse_count = 0

# rising edge measurment
def edge_detected(channel):
    global pulse_count
    pulse_count += 1

def setup():
    GPIO.setmode(GPIO.BCM)
    
    #pin 27 configuration, no pull up/down resistors needed for input
    GPIO.setup(GPIO_PIN, GPIO.IN)
    
    # It will trigger the 'edge_detected' purely on the RISING edge of the square wave.
    GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=edge_detected)

def main():
    global pulse_count
    setup()
    print(f"Measuring frequency on GPIO {GPIO_PIN}...")
    print("Press CTRL+C to stop.\n")
    
    try:
        while True:
            # Reset count and capture start time with high precision
            pulse_count = 0 
            start_time = time.perf_counter()
            time.sleep(1.0)
            elapsed_time = time.perf_counter() - start_time
            
            # Calculate frequency 
            frequency = pulse_count / elapsed_time
            # 2 decimal places
            print(f"Detected Frequency: {frequency:.2f} Hz")
            
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
        
    finally:
        # Always clean up GPIO states on exit to prevent errors on the next run
        GPIO.cleanup()

if __name__ == '__main__':
    main()
