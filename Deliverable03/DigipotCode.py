import spidev
import time

class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        # MCP4131 supports mode 0,0 and 1,1. 
        # Max clock speed is roughly 10MHz, we'll use 1MHz for stability.
        self.spi.max_speed_hz = 1000000 

    def set_step(self, step):
        """
        Sets the wiper position (0 to 128).
        Command byte for MCP4131: 
        0000 (Address 0 for Volatile Wiper 0) + 00 (Write Command) + 00 (Padding) = 0x00
        """
        if not 0 <= step <= 128:
            raise ValueError("Step must be between 0 and 128")

        # Send [Command Byte, Data Byte]
        # For the 4131, the 9th bit of data is actually in the command byte, 
        # but for 128 steps, we only need the second byte.
        self.spi.xfer2([0x00, step])

    def close(self):
        self.spi.close()

# --- Main Execution ---
if __name__ == "__main__":
    pot = MCP4131()
    
    try:
        print("Cycling resistance from 0 to 128...")
        while True:
            # Sweep Up
            for s in range(0, 129, 10):
                print(f"Setting step to: {s}")
                pot.set_step(s)
                time.sleep(1)
            
            # Sweep Down
            for s in range(128, -1, -10):
                print(f"Setting step to: {s}")
                pot.set_step(s)
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pot.close()
