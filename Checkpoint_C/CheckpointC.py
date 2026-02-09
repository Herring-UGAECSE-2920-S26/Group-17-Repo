import smbus
from time import sleep

I2CBUS = 1
ADDRESS = 0x27

# LCD Constants (Omitted for brevity, use the ones from your original code)
# ... LCD_CLEARDISPLAY, LCD_RETURNHOME, etc ...

class i2c_device:
    def __init__(self, addr, port=I2CBUS):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

class LCD:
    def __init__(self, addr=0x27):
        self.lcd_device = i2c_device(addr)
        # Initialization sequence (From your original code)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)
        # ... rest of init ...

    def lcd_write(self, cmd, mode=0):
        # Implementation from your original code
        pass

    def lcd_display_string(self, string, line=1, pos=0):
        # Implementation from your original code
        pass

    def lcd_clear(self):
        # Implementation from your original code
        pass
