import pigpio # https://abyz.me.uk/rpi/pigpio/index.html
import math
import time

class SineWave:
    def __init__(self, pi):
        self.pi = pi
        
        # 6-bit resolution: GPIO 22 is the new LSB, 26 is still the MSB.
        # Ordered LSB to MSB for bitwise math.
        self.pins = [22, 16, 20, 21, 25, 26] 

        # Set up voltage pins
        for pin in self.pins:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            
        self.current_wave_id = None
        
        # The time delay between each hardware sample. 
        self.sample_rate_us = 1

    def start_wave(self, freq, maxV):
        """
        Precomputes the 6-bit sine wave and offloads it to the DMA hardware.
        """
        # Calculate how many steps fit into one full wave cycle
        steps = int(1000000 / (self.sample_rate_us * freq))
        if steps < 4:
            steps = 4 # Safety bound for frequencies that are too high

        pulses = []
        maxV = maxV/10
        for i in range(steps):
            # 1. Calculate sine wave from 0.0 to 1.0
            sine_val = ((maxV-0.05) * math.sin(2 * math.pi * i / steps) + (maxV+0.03)) / 2.0
            
            # 2. Scale to 6-bit integer (0 to 63) for your 6-pin resistor ladder
            dac_value = int(sine_val * 63)
            dac_value = max(0, min(63, dac_value)) # Clamp to prevent overflow

            # 3. Create Bitmasks
            gpio_on = 0
            gpio_off = 0
            
            # Iterate through all 6 bits
            for bit in range(6):
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
        print("Failed to connect to pigpio. Did you run 'sudo pigpiod -s 1'?")
        exit()
        
    sineWave = SineWave(pi1)

    try: 
        test_freq = 1000
        test_max = 1
        print(f"Generating {test_freq}Hz sine wave with 6-bit resolution...")
        
        # You only need to call this ONCE. 
        # The DMA hardware takes over and loops it forever.
        sineWave.start_wave(freq=test_freq, maxV=test_max)
        
        # Look at your CPU usage now! Your main loop doesn't have to do any math.
        while True:
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        sineWave.stop()
        pi1.stop()
