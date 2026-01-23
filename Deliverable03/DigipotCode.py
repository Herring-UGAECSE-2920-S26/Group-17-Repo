import spidev

class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 50000 

    def set_step(self, step):
        """
        Sends the raw integer to the MCP4131. 
        Note: Hardware limits are 0-128. 
        Values outside this may cause unexpected bit-shifting behavior.
        """
        # We use masking (& 0xFF) to ensure we only send one byte of data
        # even if the input is a very large number.
        self.spi.xfer2([0x00, step & 0xFF])
        print(f"Sent raw value {step} (Byte: {step & 0xFF}) to MCP4131")

    def close(self):
        self.spi.close()

if __name__ == "__main__":
    pot = MCP4131()
    
    print("--- MCP4131 Unrestricted Manual Control ---")
    print("Enter any integer. Type 'exit' to quit.")
    
    try:
        while True:
            user_input = input("\nEnter value: ").strip().lower()
            
            if user_input == 'exit':
                break
            
            try:
                # Converts input to integer and sends it regardless of size
                step_val = int(user_input)
                pot.set_step(step_val)
            except ValueError:
                print("That's not a number. Please enter an integer.")

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        pot.close()
