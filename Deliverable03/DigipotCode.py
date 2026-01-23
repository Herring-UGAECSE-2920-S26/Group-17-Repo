import spidev
import time

class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 50000 # Slow and steady
        self.spi.mode = 0             # Try Mode 0 first; if fails, try mode 3
        self.spi.no_cs = False        # Ensure the Pi manages the CS pin

    def set_step(self, step):
        try:
            val = int(step)
            # Ensure we stay in hardware bounds
            if val < 0: val = 0
            if val > 128: val = 128
            
            # The MCP4131 uses 16-bit instructions
            # [Address/Command Byte] [Data Byte]
            # Address 0, Write = 0x00
            resp = self.spi.xfer2([0x00, val])
            
            print(f"Sent {val}. Hardware response: {resp}")
        except ValueError:
            print("Invalid input! Enter a number.")

    def close(self):
        self.spi.close()

if __name__ == "__main__":
    pot = MCP4131()
    try:
        while True:
            u_input = input("Enter Step (0-128) or 'q': ")
            if u_input.lower() == 'q':
                break
            pot.set_step(u_input)
    finally:
        pot.close()
