import spidev #https://pypi.org/project/spidev/
import sys


class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
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
    pot = MCP4131()
    
    print("manual digipot control")
    print("Type 'exit' to quit.")

    #code that allows the user to change the resistor value
    #through keyboard input
    try:
        while True:
            pot_input = input("\nEnter Pot Number (0 or 1): ").strip().lower()
            if pot_input == 'exit':
                break
            
            step_input = input("Enter Step Value (0-128): ").strip().lower()
            if step_input == 'exit':
                break

            try:
                p = int(pot_input)
                s = int(step_input)
                pot.set_step(s, pot_num=p)
            except ValueError:
                print("Invalid input. Please enter whole numbers.")

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        pot.close()
        print("SPI connection closed.")
