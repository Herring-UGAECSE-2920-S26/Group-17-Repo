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

    def start_wave(self, freq, s=64):
        """
        Precomputes the 6-bit sine wave at FULL amplitude and offloads it to DMA.
        Now includes 3D dynamic DC offset compensation based on freq and step 's'.
        """
        steps = int(1000000 / (self.sample_rate_us * freq))
        if steps < 4:
            steps = 4

        pulses = []
        
        # 1. Convert Hz to kHz for the math
        f_kHz = freq / 1000.0

        # 2. Calculate the physical voltage error based on your data table
        #    V_error = (Slope_based_on_freq) * current_step
        v_error = (0.00092 * f_kHz - 0.00147) * s
        
        # 3. Divide by 10 to normalize it to your 10V hardware scale 
        offset = v_error / 10.0
        
        for i in range(steps):
            # 4. Apply the dynamic offset to the sine wave math
            sine_val = (math.sin(2 * math.pi * i / steps) + 1.0 - offset) / 2.0
            
            # 5. Scale to full 6-bit integer (0 to 63) ALWAYS. 
            dac_value = int(sine_val * 63)
            dac_value = max(0, min(63, dac_value)) 

            # 6. Create Bitmasks
            gpio_on = 0
            gpio_off = 0
            
            for bit in range(6):
                if dac_value & (1 << bit):
                    gpio_on |= (1 << self.pins[bit])
                else:
                    gpio_off |= (1 << self.pins[bit])

            # 7. Add pulse instruction to array
            pulses.append(pigpio.pulse(gpio_on, gpio_off, self.sample_rate_us))

        self.pi.wave_add_generic(pulses)
        new_wave_id = self.pi.wave_create()
        
        if self.current_wave_id is not None:
            self.pi.wave_send_using_mode(new_wave_id, pigpio.WAVE_MODE_REPEAT_SYNC) 
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
        sys.exit()
        
    sineWave = SineWave(pi1)

    try: 
        # State tracking variables so we don't lose one when we change the other!
        current_freq = 10000
        current_s = 64
        
        print(f"Generating {current_freq}Hz sine wave at full hardware resolution...")
        
        # Initialize hardware state
        pot.set_step(current_s, pot_num=0)
        sineWave.start_wave(freq=current_freq, s=current_s)
        
        print("\n--- Live Waveform Control ---")
        print("Commands:")
        print("  a <step> : Change Amplitude Step (0-128) -> e.g., 'a 100'")
        print("  f <freq> : Change Frequency (Hz)       -> e.g., 'f 5000'")
        print("  exit     : Quit program\n")

        # 3. Interactive loop for live dual-control
        while True:
            user_input = input("Enter command: ").strip().lower()
            
            if user_input == 'exit':
                break

            # Split the input into command and value
            parts = user_input.split()
            if len(parts) != 2:
                print("Invalid format. Please use 'a [step]' or 'f [freq]'.")
                continue

            command = parts[0]
            value_str = parts[1]

            try:
                val = int(value_str)
                
                if command == 'a':
                    if 0 <= val <= 128:
                        current_s = val
                        # 1. Update the physical hardware voltage divider
                        pot.set_step(current_s, pot_num=0) 
                        # 2. Update the software wave math
                        sineWave.start_wave(freq=current_freq, s=current_s)
                    else:
                        print("Invalid amplitude. Must be between 0 and 128.")
                        
                elif command == 'f':
                    if val > 0: 
                        current_freq = val
                        print(f"Frequency changed to {current_freq} Hz")
                        # Recalculate DMA wave for new frequency, keeping the current amplitude math
                        sineWave.start_wave(freq=current_freq, s=current_s)
                    else:
                        print("Frequency must be greater than 0.")
                        
                else:
                    print("Unknown command. Use 'a' for amplitude or 'f' for frequency.")
                    
            except ValueError:
                print("Invalid input. Please enter a whole number for the value.")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        print("\nCleaning up hardware...")
        sineWave.stop()
        pi1.stop()
        pot.close()
        print("Done.")
