import pigpio # https://abyz.me.uk/rpi/pigpio/index.html
import math
import time

class SineWave:
    def __init__(self, pi):
        self.pi = pi
        
        # Based on your original code's binary string indexing, 
        # pin 16 is the Least Significant Bit (LSB) and 26 is the Most Significant Bit (MSB).
        # We order them LSB to MSB for easy bitwise math.
        self.pins = [16, 20, 21, 25, 26] 

        # Set up voltage pins
        for pin in self.pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            
        self.current_wave_id = None
        
        # The time delay between each hardware sample. 
        self.sample_rate_us = 1

    def start_wave(self, freq):
        """
        Precomputes the 5-bit sine wave and offloads it to the DMA hardware.
        """
        # Calculate how many steps fit into one full wave cycle
        steps = int(1000000 / (self.sample_rate_us * freq))
        if steps < 4:
            steps = 4 # Safety bound for frequencies that are too high

        pulses = []
        
        for i in range(steps):
            # 1. Calculate sine wave from 0.0 to 1.0
            sine_val = (math.sin(2 * math.pi * i / steps) + 1.0) / 2.0
            
            # 2. Scale to 5-bit integer (0 to 31) for your 5-pin resistor ladder
            dac_value = int(sine_val * 31)
            dac_value = max(0, min(31, dac_value)) # Clamp to prevent overflow

            # 3. Create Bitmasks (replaces the string comparison logic)
            gpio_on = 0
            gpio_off = 0
            
            for bit in range(5):
                if dac_value & (1 << bit):
                    # Bit is 1, turn pin ON
                    gpio_on |= (1 << self.pins[bit])
                else:
                    # Bit is 0, turn pin OFF
                    gpio_off |= (1 << self.pins[bit])

            # 4. Add pulse instruction to array
            pulses.append(pigpio.pulse(gpio_on, gpio_off, self.sample_rate_us))

        # Add generic waveform and get ID
        self.pi.wave_add_generic(pulses)
        new_wave_id = self.pi.wave_create()
        
        # Seamlessly swap waves if one is already running (Double Buffering)
        if self.current_wave_id is not None:
            self.pi.wave_send_using_mode(new_wave_id, pigpio.PI_WAVE_MODE_REPEAT_SYNC)
            time.sleep(0.1) # Wait for hardware to finish the old wave cycle
            self.pi.wave_delete(self.current_wave_id)
        else:
            self.pi.wave_send_repeat(new_wave_id)
            
        self.current_wave_id = new_wave_id

    def stop(self):
        """Stops the DMA wave and resets pins."""
        self.pi.wave_tx_stop()
        self.pi.wave_clear()
        for pin in self.pins:
            self.pi.write(pin, 0)

# --- For Testing ---
if __name__ == "__main__":
    # setup
    pi1 = pigpio.pi()
    if not pi1.connected:
        print("Failed to connect to pigpio. Did you run 'sudo pigpiod'?")
        exit()
        
    sineWave = SineWave(pi1)

    try: 
        print("Generating 500Hz sine wave...")
        
        # You only need to call this ONCE. 
        # The DMA hardware takes over and loops it forever.
        sineWave.start_wave(freq=500)
        
        # Look at your CPU usage now! Your main loop doesn't have to do any math.
        while True:
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        sineWave.stop()
        pi1.stop()
