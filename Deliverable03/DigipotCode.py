import spidev

class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        # Slower speed is MUCH safer for digipots to prevent bit-shift errors
        self.spi.max_speed_hz = 50000 
        self.spi.mode = 0

    def set_step(self, step):
        # 1. Force the value to be an integer
        step = int(step)
        
        # 2. Limit the hardware range internally to 0-128 
        # to prevent overflow into the command bits
        if step > 128:
            step = 128
        if step < 0:
            step = 0

        # 3. Construct the Write Command
        # Address 0000 (Wiper 0), Command 00 (Write)
        # Byte 1 should be 0x00 (0000 0000)
        # Byte 2 is the actual step
        command_byte = 0x00 
        data_byte = step & 0xFF
        
        # Send as a 16-bit transaction
        self.spi.xfer2([command_byte, data_byte])
        print(f"Wiper set to: {step}")

    def close(self):
        self.spi.close()

# ... (rest of your input loop remains the same)
