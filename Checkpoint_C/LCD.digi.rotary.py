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
   def __init__(self):
      self.lcd_device = i2c_device(0x27)

      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x02)

      self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
      self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
      self.lcd_write(LCD_CLEARDISPLAY)
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
      self.lcd_write(LCD_RETURNHOME)

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
                if abs(startTime - endTime) >= 2:
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
    lcd = lcd()
    
    menu = MenuSystem(rotary, lcd, pot)
    
    loop = asyncio.get_event_loop()
    loop.create_task(rotary.checkRotary())
    loop.run_until_complete(menu.run())
