import spidev #https://pypi.org/project/spidev/
import sys
from gpiozero import OutputDevice # Modern GPIO library

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
    # OutputDevice automatically sets it as an output and defaults to off
    pin19 = OutputDevice(19, initial_value=False) 

    spi = spidev.SpiDev()
    pot = MCP4131(spi)
    
    print("manual digipot control")
    print("Type 'exit' to quit.")
    print("Type 'gpio on' or 'gpio off' at any prompt to control pin 19.")

    #code that allows the user to change the resistor value
    #through keyboard input
    try:
        while True:
            pot_input = input("\nEnter Pot Number (0 or 1): ").strip().lower()
            
            if pot_input == 'exit':
                break
            # Intercept GPIO command at prompt 1
            if pot_input in ['gpio on', 'gpio off']:
                if pot_input == 'gpio on':
                    pin19.on()
                else:
                    pin19.off()
                print(f"GPIO 19 is now {'ON' if pot_input == 'gpio on' else 'OFF'}")
                continue
            
            # Use a small loop here so a GPIO command doesn't wipe out the pot_
