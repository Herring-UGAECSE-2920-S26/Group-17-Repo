import spidev
import sys

# 1. Setup SPI for the Potentiometer
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Resistance values (from your lesson)
resistances = [100, 1000, 5000, 10000]
idx = 0

def update_pot(target_ohms):
    # MCP4131 is a 7-bit device (0-128 steps)
    step = int((target_ohms / 10000) * 128)
    spi.xfer2([0x00, step])
    print(f"\n[ACTIVE] Resistance: {target_ohms}Ω | MCP4131 Step: {step}")

try:
    print("--- Digipot Keyboard Controller ---")
    print("Press ENTER to cycle to the next resistance.")
    print("Press Ctrl+C to exit.")
    
    # Set initial state
    update_pot(resistances[idx])

    while True:
        input("Press [Enter] for next level...")
        
        # Increment index and wrap around using modulo
        idx = (idx + 1) % len(resistances)
        update_pot(resistances[idx])

except KeyboardInterrupt:
    print("\n\nClosing SPI connection. Goodbye!")
    spi.close()
    sys.exit()
