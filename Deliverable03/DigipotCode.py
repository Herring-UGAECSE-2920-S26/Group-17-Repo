import spidev
import time

# 1. Setup SPI for the Potentiometer
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Our 4 values to cycle through
resistances = [100, 1000, 5000, 10000]

def set_pot_resistance(target_ohms):
    # Calculate step (0-128) for the MCP4131
    # 10k ohms is the max capacity of this specific model
    step = int((target_ohms / 10000) * 128)
    
    # Send to MCP4131 via SPI
    # 0x00 is the write command for the Wiper 0 register
    spi.xfer2([0x00, step])
    print(f"Resistance set to: {target_ohms}Ω (Step: {step})")

try:
    print("Auto-cycling resistance levels. Press Ctrl+C to stop.")
    while True:
        for val in resistances:
            set_pot_resistance(val)
            # Wait 2 seconds before switching to the next level
            time.sleep(2) 

except KeyboardInterrupt:
    print("\nShutting down...")
    spi.close()
