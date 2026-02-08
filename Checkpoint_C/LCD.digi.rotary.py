import pigpio
import asyncio
import spidev
import time
import sys
import smbus
from time import sleep
# i2c bus (0 -- original Pi, 1 -- Rev 2 Pi)
I2CBUS = 1

# LCD Address
ADDRESS = 0x27

class i2c_device:
   def __init__(self, addr, port=I2CBUS):
      self.addr = addr
      self.bus = smbus.SMBus(port)

# Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

# Write a command and argument
   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)

# Write a block of data
   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)

# Read a single byte
   def read(self):
      return self.bus.read_byte(self.addr)

# Read
   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)

# Read a block of data
   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)


# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class lcd:
   #initializes objects and lcd
   def __init__(self, addr=0x27):
      self.lcd_device = i2c_device(addr)

      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x02)

      self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
      self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
      self.lcd_write(LCD_CLEARDISPLAY)
      sleep(0.002) # Wait for clear to finish
      self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
      sleep(0.2)


   # clocks EN to latch command
   def lcd_strobe(self, data):
      self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
      sleep(.0005)
      self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
      sleep(.0001)

   def lcd_write_four_bits(self, data):
      self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
      self.lcd_strobe(data)

   # write a command to lcd
   def lcd_write(self, cmd, mode=0):
      self.lcd_write_four_bits(mode | (cmd & 0xF0))
      self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

   # write a character to lcd (or character rom) 0x09: backlight | RS=DR<
   # works!
   def lcd_write_char(self, charvalue, mode=1):
      self.lcd_write_four_bits(mode | (charvalue & 0xF0))
      self.lcd_write_four_bits(mode | ((charvalue << 4) & 0xF0))
  
   # put string function with optional char positioning
   def lcd_display_string(self, string, line=1, pos=0):
    if line == 1:
      pos_new = pos
    elif line == 2:
      pos_new = 0x40 + pos
    elif line == 3:
      pos_new = 0x14 + pos
    elif line == 4:
      pos_new = 0x54 + pos

    self.lcd_write(0x80 + pos_new)

    for char in string:
      self.lcd_write(ord(char), Rs)

   # clear lcd and set to home
   def lcd_clear(self):
      self.lcd_write(LCD_CLEARDISPLAY)
      sleep(0.002)

   # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
   def backlight(self, state): # for state, 1 = on, 0 = off
      if state == 1:
         self.lcd_device.write_cmd(LCD_BACKLIGHT)
      elif state == 0:
         self.lcd_device.write_cmd(LCD_NOBACKLIGHT)

   # add custom characters (0 - 7)
   def lcd_load_custom_chars(self, fontdata):
      self.lcd_write(0x40);
      for char in fontdata:
         for line in char:
            self.lcd_write_char(line)         
print("LCD is working")

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
    minR = 110
    maxR = 9422

    #initialize Rotary object to meet Menu System needs
    def __init__(self, rotaryA, rotaryB, switchPin, pi1):
        self.rotaryA = rotaryA
        self.rotaryB = rotaryB
        self.switchPin = switchPin
        self.pi1 = pi1

        #set up rotary encoder
        self.pi1.set_mode(self.rotaryA, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryA, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryA, 3000) # 3ms debounce
        
        self.pi1.set_mode(self.rotaryB, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryB, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryB, 3000) # 3ms debounce

        self.pi1.set_mode(self.switchPin, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.switchPin, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.switchPin, 20000) # 20ms debounce

        #set up vars
        self.readA = None
        self.readB = None
        self.prevA = None
        self.clockwise = False
        self.fast = False
        self.resistance = 100
        self.changed = False

    #check direction and speed of encoder spinning, still subject to noise, consult Sharon code    
    async def checkRotary(self):
        self.prevA = self.pi1.read(self.rotaryA)
        startTime = time.perf_counter()
        
        while True:
            self.readA = self.pi1.read(self.rotaryA)
            
            if self.readA != self.prevA:
                # Only trigger on falling edge 
                if self.readA == 0:
                    endTime = time.perf_counter()
                    
                    # Check speed (0.3s threshold)
                    if (endTime - startTime) < 0.2:
                        self.fast = True
                    else:
                        self.fast = False
                    startTime = endTime

                    # Check direction
                    # If B is high when A falls = Clockwise
                    #**subject to noise**
                    if self.pi1.read(self.rotaryB) == 1:
                        self.clockwise = True
                    else:
                        self.clockwise = False
                    
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
        
        self.menu_options = ["Pot 0", "Pot 1"]
        self.current_selection = 0
        
        # State: "CONTROL" or "SELECT"
        self.state = "SELECT" 
        
        # Track resistance (Ohms) directly
        self.pot_resistance = [self.rot.minR, self.rot.minR] 

    def ohms_to_step(self, ohms):
        """Converts resistance in Ohms to 0-128 step value."""
        step = int(((ohms - 78) / self.rot.maxR) * 128)
        return max(0, min(128, step))

    def update_ui(self):
        # lag prevention
        self.lcd.lcd_clear()
        
        if self.state == "SELECT":
            self.lcd.lcd_display_string("Select Digipot:", line=1)
            self.lcd.lcd_display_string(f"> {self.menu_options[self.current_selection]}", line=2)
        else: # CONTROL state
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
                
                # Wait while button is held
                while self.rot.pi1.read(self.rot.switchPin) == 0:
                    await asyncio.sleep(0.05)
                    
                    # Long Press (3s) to exit Control menu back to Select
                    if self.state == "CONTROL":
                        if not long_press_triggered and (time.time() - press_start > 3.0):
                            self.state = "SELECT"
                            self.update_ui()
                            long_press_triggered = True
                
                # Short Press logic
                if not long_press_triggered:
                    if self.state == "CONTROL":
                        # Commit changes to hardware
                        step = self.ohms_to_step(self.pot_resistance[self.current_selection])
                        self.pot.set_step(step, pot_num=self.current_selection)
                    elif self.state == "SELECT":
                        # Select Digipot and enter Control mode
                        self.state = "CONTROL"
                        self.update_ui()
            
            if self.rot.changed: 
                if self.state == "SELECT":
                    # Navigate Menu
                    move = 1 if self.rot.clockwise else -1
                    self.current_selection = (self.current_selection + move) % len(self.menu_options)
                    self.update_ui()
                    
                elif self.state == "CONTROL":
                    #Fast turn = 100 Ohms, Slow turn = 10 Ohms
                    increment = 100 if self.rot.fast else 10
                    direction = 1 if self.rot.clockwise else -1
                    
                    new_ohms = self.pot_resistance[self.current_selection] + (direction * increment)
                    # Constraint
                    self.pot_resistance[self.current_selection] = max(self.rot.minR, min(self.rot.maxR, new_ohms))
                    
                    self.update_ui()
                    
                self.rot.changed = False 

            await asyncio.sleep(0.01)


if __name__ == "__main__":
    pi = pigpio.pi()
    if not pi.connected:
        print("Pigpio daemon not running. Run 'sudo pigpiod'")
        sys.exit()

    rotary = Rotary(18, 23, 24, pi) 
    pot = MCP4131()
    try:
        lcd = lcd(0x27)
    except OSError:
        try:
            # Try fallback address 0x3F
            lcd = lcd(0x3F)
        except OSError:
            print("\n[ERROR] I2C Input/Output Error: LCD not found at address 0x27 or 0x3F.")
            print("this is so sad :9")
            sys.exit(1)
    
    menu = MenuSystem(rotary, lcd, pot)
    
    loop = asyncio.get_event_loop()
    loop.create_task(rotary.checkRotary())
    loop.run_until_complete(menu.run())
