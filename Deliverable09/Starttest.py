import spidev #https://pypi.org/project/spidev/
import sys
import pigpio # Swapped to pigpio per your example

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
    # --- Set up pigpio for GPIO 19 ---
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio. Did you run 'sudo pigpiod'?")
        sys.exit(1)
        
    pi.set_mode(19, pigpio.OUTPUT)
    pi.write(19, 0) # Default to off

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
                    pi.write(19, 1)
                    print("GPIO 19 is now ON")
                else:
                    pi.write(19, 0)
                    print("GPIO 19 is now OFF")
                continue
            
            # Use a small loop here so a GPIO command doesn't wipe out the pot_input
            while True:
                step_input = input("Enter Step Value (0-128): ").strip().lower()
                
                # Intercept GPIO command at prompt 2
                if step_input in ['gpio on', 'gpio off']:
                    if step_input == 'gpio on':
                        pi.write(19, 1)
                        print("GPIO 19 is now ON")
                    else:
                        pi.write(19, 0)
                        print("GPIO 19 is now OFF")
                    continue # Re-asks for the Step Value
                break # If it wasn't a GPIO command, break inner loop to process

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
        # Ensure GPIO pin is set to 0 and pigpio stops safely
        if pi.connected:
            pi.write(19, 0)
            pi.stop() 
        print("SPI and pigpio connections closed.")
