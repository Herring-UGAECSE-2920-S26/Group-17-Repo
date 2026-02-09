import pigpio
import asyncio
import time
import sys

# Import custom modules based on your filenames
from DigipotCode import MCP4131
from RotaryFunctions import Rotary
from CheckpointC import LCD  # Assuming the LCD driver logic goes here

class MenuSystem:
    def __init__(self, rotary_obj, lcd_obj, pot_obj):
        self.rot = rotary_obj
        self.lcd = lcd_obj
        self.pot = pot_obj
        self.menu_options = ["Pot 0", "Pot 1"]
        self.current_selection = 0
        self.state = "SELECT" 
        self.pot_resistance = [self.rot.minR, self.rot.minR] 

    def ohms_to_step(self, ohms):
        step = int(((ohms - 78) / self.rot.maxR) * 128)
        return max(0, min(128, step))

    def update_ui(self):
        self.lcd.lcd_clear()
        if self.state == "SELECT":
            self.lcd.lcd_display_string("Select Digipot:", line=1)
            self.lcd.lcd_display_string(f"> {self.menu_options[self.current_selection]}", line=2)
        else:
            name = self.menu_options[self.current_selection]
            ohms = self.pot_resistance[self.current_selection]
            step = self.ohms_to_step(ohms)
            self.lcd.lcd_display_string(f"{name} Step:{step}", line=1)
            self.lcd.lcd_display_string(f"Res: {ohms} Ohms", line=2)

    async def run(self):
        self.update_ui()
        while True:
            # Button Logic
            if self.rot.pi1.read(self.rot.switchPin) == 0:
                press_start = time.time()
                long_press_triggered = False
                while self.rot.pi1.read(self.rot.switchPin) == 0:
                    await asyncio.sleep(0.05)
                    if self.state == "CONTROL" and not long_press_triggered:
                        if (time.time() - press_start > 3.0):
                            self.state = "SELECT"
                            self.update_ui()
                            long_press_triggered = True

                if not long_press_triggered:
                    if self.state == "CONTROL":
                        step = self.ohms_to_step(self.pot_resistance[self.current_selection])
                        self.pot.set_step(step, pot_num=self.current_selection)
                    elif self.state == "SELECT":
                        self.state = "CONTROL"
                        self.update_ui()

            # Rotation Logic
            if self.rot.changed: 
                if self.state == "SELECT":
                    move = 1 if self.rot.clockwise else -1
                    self.current_selection = (self.current_selection + move) % len(self.menu_options)
                elif self.state == "CONTROL":
                    increment = 100 if self.rot.fast else 10
                    direction = 1 if self.rot.clockwise else -1
                    new_ohms = self.pot_resistance[self.current_selection] + (direction * increment)
                    self.pot_resistance[self.current_selection] = max(self.rot.minR, min(self.rot.maxR, new_ohms))
                
                self.update_ui()
                self.rot.changed = False 

            await asyncio.sleep(0.01)

async def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Pigpio daemon not running. Run 'sudo pigpiod'")
        return

    rotary = Rotary(18, 23, 24, pi) 
    pot = MCP4131()
    
    try:
        lcd = LCD(0x27)
    except OSError:
        try:
            lcd = LCD(0x3F)
        except OSError:
            print("LCD not found.")
            return

    menu = MenuSystem(rotary, lcd, pot)

    await asyncio.gather(
        rotary.checkRotary(),
        menu.run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping...")
