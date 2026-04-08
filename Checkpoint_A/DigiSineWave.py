import pigpio # https://abyz.me.uk/rpi/pigpio/index.html
import spidev # https://pypi.org/project/spidev/
import math
import time
import sys

class MCP4131:
    def __init__(self, spi, bus=0, device=1):
        self.spi = spi
        # bus=0, device=1 automatically uses GPIO 7 (SPI0 CE1) for Chip Select
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000 

    def set_step(self, step, pot_num=0):
        """Set the wiper position (0 to 128). pot_num: 0 or 1"""
        if 0 <= step <= 128:
            cmd = 0x00 if pot_num == 0 else 0x10
            self.spi.xfer2([cmd, step])
            print(f"Amplitude changed: Pot {pot_num} wiper set to step {step}")
        else:
            print("Error: Step must be between 0 and 128.")

    def close(self):
        self.spi.close()

class SineWave:
    def __init__(self, pi):
        self.pi = pi
        
        # 6-bit resolution: GPIO 22 is the LSB, 26 is the MSB.
        self.pins = [22, 16, 20, 21, 25, 26] 

        # Set up voltage pins
        for pin in self.pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            
        self.current_wave_id = None
        self.sample_rate_us = 1

    # ---> ADDED 's' AS AN ARGUMENT HERE WITH A DEFAULT OF 64
    def start_wave(self, freq, s=64):
        """
        Precomputes the 6-bit sine wave at FULL amplitude and offloads it to DMA.
        Now includes dynamic DC offset compensation based on digipot step 's'.
        """
        steps = int(1000000 / (self.sample_rate_us * freq))
        if steps < 4:
            steps = 4

        pulses = []
        
        for i in range(steps):
            # 1. Calculate sine wave from 0.0 to 1.0, subtracting your custom offset
            # By subtracting the offset here, we artificially pull the wave down in software 
            # so the capacitor pulls it back up to a perfect 0V in hardware.
            sine_val = (math.sin(2 * math.pi * i / steps) + 1.0 - (5.76E-4 * s + 0.00232)) / 2.0
            
            # 2. Scale to full 6-bit integer (0 to 63) ALWAYS. 
            dac_value = int(sine_val * 63)
            dac_value = max(0, min(63, dac_value)) 

            # 3. Create Bitmasks
            gpio_on = 0
            gpio_off = 0
            
            for bit in range(6):
                if dac_value & (1 << bit):
                    gpio_on |= (1 << self.pins[bit])
                else:
                    gpio_off |= (1 << self.pins[bit])

            # 4. Add pulse instruction to array
            pulses.append(pigpio.pulse(gpio_on, gpio_off, self.sample_rate_us))

        self.pi.wave_add_generic(pulses)
        new_wave_id = self.pi.wave_create()
        
        if self.current_wave_id is not None:
            self.pi.wave_send_using_mode(new_wave_id, pigpio.WAVE_MODE_REPEAT_SYNC) # <--- FIXED
            time.sleep(0.1) 
            self.pi.wave_delete(self.current_wave_id)
        else:
            self.pi.wave_send_repeat(new_wave_id)
            
        self.current_wave_id = new_wave_id

    def stop(self):
        self.pi.wave_tx_stop()
        self.pi.wave_clear()
        for pin in self.pins:
            self.pi.write(pin, 0)

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Setup SPI Digipot
    spi = spidev.SpiDev()
    pot = MCP4131(spi, bus=0, device=1)

    # 2. Setup DMA Sine Wave
    pi1 = pigpio.pi()
    if not pi1.connected:
        print("Failed to connect to pigpio. Did you run 'sudo pigpiod -s 1'?")
        pot.close()
        exit()
        
    sineWave = SineWave(pi1)

    try: 
        test_freq = 10000
        print(f"Generating {test_freq}Hz sine wave at full hardware resolution...")
        
        # Default pot to roughly 50% volume (step 64)
        initial_s = 64
        pot.set_step(initial_s, pot_num=0)
        
        # Start the wave, passing the initial 's' value so the math is right
        sineWave.start_wave(freq=test_freq, s=initial_s)
        
        print("\n--- Manual Amplitude Control ---")
        print("Type a step value (0-128) to change the wave amplitude.")
        print("Type 'exit' to quit.\n")

        # 3. Interactive loop for amplitude control
        while True:
            step_input = input("Enter Amplitude Step (0-128): ").strip().lower()
            if step_input == 'exit':
                break

            try:
                s = int(step_input)
                
                # 1. Update the physical hardware voltage divider
                pot.set_step(s, pot_num=0) 
                
                # 2. Update the software wave math to compensate for the new capacitor behavior!
                sineWave.start_wave(freq=test_freq, s=s)
                
            except ValueError:
                print("Invalid input. Please enter a whole number between 0 and 128.")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        print("\nCleaning up hardware...")
        sineWave.stop()
        pi1.stop()
        pot.close()
        print("Done.")
