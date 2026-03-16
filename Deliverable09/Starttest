import spidev #https://pypi.org/project/spidev/
import sys
import RPi.GPIO as GPIO  # Import the GPIO library

class MCP4131:
    def __init__(self, spi, bus=0, device=0):
        self.spi = spi
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000 

    #digipot values
    def set_step(self, step, pot_num=0):
        """Set the wiper position (0 to 128). pot_num: 0 or 1"""
        if 0 <= step <= 128:
            cmd = 0x00 if pot_num == 0 else 0x10
            self.spi.xfer2([cmd, step])
            print(f"Set Pot {pot_num} wiper to step {step}")
        else:
            print("Step must be between 0 and 128.")

    def close(self):
        self.spi.close()

#control for user input 
if __name__ == "__main__":
    # --- GPIO Setup ---
    GPIO_PIN = 19
    GPIO.setmode(GPIO.BCM) # Use broadcom pin numbering
    GPIO.setwarnings(False)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    GPIO.output(GPIO_PIN, GPIO.LOW) # Default to OFF
    
    # --- SPI Setup ---
    spi = spidev.SpiDev()
    pot = MCP4131(spi)
    
    print("--- Control Interface ---")
    print("Commands:")
    print("  pot <num> <step>  (e.g., 'pot 0 64' sets pot 0 to step 64)")
    print("  gpio on           (Turns GPIO 19 ON)")
    print("  gpio off          (Turns GPIO 19 OFF)")
    print("  exit              (Quit program)")

    try:
        while True:
            # Single input prompt allows for any command at any time
            user_input = input("\nEnter command: ").strip().lower()
            
            if user_input == 'exit':
                break
                
            # Handle GPIO commands
            elif user_input == 'gpio on':
                GPIO.output(GPIO_PIN, GPIO.HIGH)
                print(f"GPIO {GPIO_PIN} turned ON.")
            elif user_input == 'gpio off':
                GPIO.output(GPIO_PIN, GPIO.LOW)
                print(f"GPIO {GPIO_PIN} turned OFF.")
                
            # Handle Potentiometer commands
            elif user_input.startswith('pot'):
                parts = user_input.split()
                if len(parts) == 3:
                    try:
                        p = int(parts[1])
                        s = int(parts[2])
                        pot.set_step(s, pot_num=p)
                    except ValueError:
                        print("Invalid input. Pot and Step must be numbers.")
                else:
                    print("Invalid format. Use: pot <num> <step>")
            
            else:
                print("Unknown command. Please try again.")

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        # Cleanup both SPI and GPIO on exit
        pot.close()
        GPIO.cleanup() 
        print("SPI and GPIO connections closed.")
