import spidev
import sys

# 1. Setup SPI with hardened settings
spi = spidev.SpiDev()
spi.open(0, 0)

# FIX 1: Lower speed significantly. 
# Digipots are slow; 1MHz is often too fast for messy breadboard wires.
spi.max_speed_hz = 50000 

# FIX 2: Explicitly set SPI mode 0 (CPOL=0, CPHA=0)
spi.mode = 0

def set_pot_step(step):
    """Sends the step value with bit-safety for the MCP4131."""
    try:
        # Clamp value to 0-128
        step = max(0, min(128, int(step)))
        
        # FIX 3: Construct a clean 16-bit write command.
        # Address 0000 (Wiper 0) + Command 00 (Write) = 0x00
        # This ensures we NEVER accidentally hit the 'Shutdown' or 'TCON' registers.
        address_byte = 0x00 
        data_byte = step & 0xFF 
        
        spi.xfer2([address_byte, data_byte])
        
        # Feedback
        approx_ohms = int((step / 128) * 10000)
        print(f"Success: Step {step} (~{approx_ohms}Ω)")
        
    except Exception as e:
        print(f"Communication Error: {e}")

try:
    print("--- MCP4131 HARDENED CONTROLLER ---")
    print("Shielded against accidental Shutdown Mode entry.")
    
    while True:
        user_input = input("\nEnter step (0-128) or 'exit': ").strip().lower()

        if user_input == 'exit':
            break

        if user_input.isdigit():
            set_pot_step(user_input)
        else:
            print("Please enter a valid whole number.")

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    spi.close()
    sys.exit()
