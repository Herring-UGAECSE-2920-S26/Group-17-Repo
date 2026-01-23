import spidev
import sys

# 1. Setup SPI for the Potentiometer
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def set_pot_step(step):
    """Sends the raw 0-128 step value to the MCP4131."""
    # Ensure step is within the 7-bit wiper range
    step = max(0, min(128, int(step)))
    spi.xfer2([0x00, step])
    
    # Calculate approximate Ohms for feedback (assuming 10k pot)
    approx_ohms = int((step / 128) * 10000)
    print(f"Success: Step set to {step} (~{approx_ohms}Ω)")

try:
    print("--- MCP4131 Manual Step Controller ---")
    print("The MCP4131 accepts values from 0 (min) to 128 (max).")
    print("Type 'exit' or press Ctrl+C to quit.")

    while True:
        user_input = input("\nEnter desired step (0-128): ").strip().lower()

        if user_input == 'exit':
            break

        try:
            val = int(user_input)
            if 0 <= val <= 128:
                write_pot(val)
            else:
                print("Error: Please enter a number between 0 and 128.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

except KeyboardInterrupt:
    print("\nClosing SPI connection.")
finally:
    spi.close()
    sys.exit()
