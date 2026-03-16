import spidev #https://pypi.org/project/spidev/
import sys
import RPi.GPIO as GPIO # Added GPIO library

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
            print(f"set Pot {pot_num} wiper to step {step}")
        else:
            print("Step must be between 0 and 128.")

    def close(self):
        self.spi.close()

#control for user input 
if __name__ == "__main__":
    # --- Set up GPIO 19 ---
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(19, GPIO.OUT)
    GPIO.output(19, GPIO.LOW) # Default to off

    spi = spidev.SpiDev()
    pot = MCP4131(spi)
    
    print("manual digipot control")
    print("Type 'exit' to quit.")
    print("Type 'gpio on' or 'gpio off' at any prompt to control pin 19.") # Added instruction

    #code that allows the user
