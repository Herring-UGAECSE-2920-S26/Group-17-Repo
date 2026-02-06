import pigpio
import asyncio
import spidev
import time
import sys
import I2C_LCD_driver

#class Digipot
class MCP4131:
    def __init__(self, bus=0, device=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000 

    def set_step(self, step, pot_num=0):
        """Set the wiper position (0 to 128). pot_num: 0 or 1"""
        if 0 <= step <= 128:
            cmd = 0x00 if pot_num == 0 else 0x10
            self.spi.xfer2([cmd, step])
        else:
            print("Step must be between 0 and 128.")

    def close(self):
        self.spi.close()
#class Rotary encoder
class Rotary:

    #min and max resistor values
    minR = 100
    maxR = 10000

    #initialize Rotary object
    def __init__(self, rotaryA, rotaryB, switchPin, pi1):
        self.rotaryA = rotaryA
        self.rotaryB = rotaryB
        self.switchPin = switchPin
        self.pi1 = pi1

        #set up rotary encoder
        self.pi1.set_mode(self.rotaryA, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryA, pigpio.PUD_UP)
        
        self.pi1.set_mode(self.rotaryB, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryB, pigpio.PUD_UP)

        self.pi1.set_mode(self.switchPin, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.switchPin, pigpio.PUD_UP)

        self.pi1.set_glitch_filter(switchPin, 50000)

        #set up other vars
        self.readA = None
        self.readB = None
        self.prevA = None
        self.clockwise = None
        self.fast = False
        self.resistance = 100
        self.changed = False

    #check direction and speed of encoder spinning    
    async def checkRotary(self):
        startTime = time.perf_counter()
        self.prevA = self.pi1.read(self.rotaryA)
        
        while True:
            self.readA = self.pi1.read(self.rotaryA) #find current A pin value

            #if rotary encoder is spinning
            if self.readA != self.prevA:
                endTime = time.perf_counter()
                print("End Time:", endTime)
                print("Click!")
                #checks speed
                if abs(startTime - endTime) >= 0.2:
                    self.fast = False
                    print("Slow")
                else:
                    self.fast = True
                    print("Fast")
                startTime = time.perf_counter()
                print("Start Time:", startTime)
                #checks direction
                if self.pi1.read(self.rotaryB) != self.readA:
                    self.clockwise = True
                    print("Clockwise")
                else:
                    self.clockwise = False
                    print("Counterclockwise")
                
                self.changed = True
            
            #update A value
            self.prevA = self.readA

            #lets other coroutines run
            await asyncio.sleep(0)

class MenuSystem:
    def __init__(self, rotary_obj, lcd_obj, pot_obj):
        self.rot = rotary_obj
        self.lcd = lcd_obj
        self.pot = pot_obj
        
        self.menu_options = ["Digipot 0", "Digipot 1"]
        self.current_selection = 0
        self.is_changing = False
        
        # Store resistance in Ohms
        self.pot_resistance = [self.rot.minR, self.rot.minR] 

    def update_ui(self):
        self.lcd.lcd_clear()
        if not self.is_changing:
            self.lcd.lcd_display_string("Select Digipot:", line=1)
            self.lcd.lcd_display_string(f"> {self.menu_options[self.current_selection]}", line=2)
        else:
            name = self.menu_options[self.current_selection]
            ohms = self.pot_resistance[self.current_selection]
            step = int((ohms / self.rot.maxR) * 128)
            
            self.lcd.lcd_display_string(f"{name} [{step}]", line=1)
            self.lcd.lcd_display_string(f"Res: {ohms} Ohms", line=2)

    async def run(self):
        self.update_ui()
        last_button_state = 1
        
        while True:
            # Switch between select and change mode
            button_state = self.rot.pi1.read(self.rot.switchPin)
            if button_state == 0 and last_button_state == 1:
                self.is_changing = not self.is_changing
                self.update_ui()
                await asyncio.sleep(0.8) # Debounce button press
            last_button_state = button_state
            
            # Rotation 
            if self.rot.changed: 
                if not self.is_changing:
                    # Change Digipot selection
                    move = 1 if self.rot.clockwise else -1
                    self.current_selection = (self.current_selection + move) % len(self.menu_options)
                else:
                    increment = 100 if self.rot.fast else 10
                    direction = 1 if self.rot.clockwise else -1
                    
                    new_ohms = self.pot_resistance[self.current_selection] + (direction * increment)
                    new_ohms = max(self.rot.minR, min(self.rot.maxR, new_ohms))
                    self.pot_resistance[self.current_selection] = new_ohms
                    
                    # Convert to step
                    step = int((new_ohms / self.rot.maxR) * 128)
                    
                    # spi call:
                    self.pot.set_step(step, pot_num=self.current_selection)
                
                self.update_ui()
                self.rot.changed = False # Reset flag

            await asyncio.sleep(0.01)

if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        print("Pigpio daemon not running. Run 'sudo pigpiod'")
        sys.exit()

    rotary = Rotary(18, 23, 24, pi) 
    pot = MCP4131()
    lcd = I2C_LCD_driver.lcd()
    
    menu = MenuSystem(rotary, lcd, pot)
    
    loop = asyncio.get_event_loop()
    loop.create_task(rotary.checkRotary())
    loop.run_until_complete(menu.run())
