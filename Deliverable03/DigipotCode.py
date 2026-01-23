import spidev
import sys

class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000 

    def set_step(self, step):
        """Sets the wiper position (0 to 128)."""
        if 0 <= step <= 128:
            # MCP4131 Write Command to Address 0x00
            self.spi.xfer2([0x00, step])
            print(f"Successfully set wiper to step {step}")
        else:
            print("Error: Step must be between 0 and 128.")

    def close(self):
        self.spi.close()

# --- Interactive Control ---
if __name__ == "__main__":
    pot = MCP4131()
    
    print("--- MCP4131 Manual Control ---")
    print("Enter a step value between 0 and 128.")
    print("Type 'exit' or press Ctrl+C to quit.")
    
    try:
        while True:
            user_input = input("\nEnter step (0-128): ").strip().lower()
            
            if user_input == 'exit':
                break
            
            try:
                step_val = int(user_input)
                pot.set_step(step_val)
            except ValueError:
                print("Invalid input. Please enter a whole number.")

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        pot.close()
        print("SPI connection closed.")
