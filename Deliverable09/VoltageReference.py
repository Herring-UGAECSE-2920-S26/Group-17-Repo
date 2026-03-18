import spidev #https://pypi.org/project/spidev/
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import time
import Dual_Digipot
import Rotary
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import Min_difference

#set up libraries
pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = Rotary.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)
lcd = I2C_LCD_driver.lcd()

digipot.set_step(60, 0)

#declare vars
minV = -5.0
maxV = 5.0
stepSize = 0.625
voltage = -5.0
first = True

while True:

    #updates lcd when something has changed
    if first == True:
        lcd.lcd_clear()
        lcd.lcd_display_string("Voltage Reference", 1)
        lcd.lcd_display_string(f"{voltage:.4f} V", 2)
        if voltage == minV:
                step = Min_difference.min_difference_volts(voltage)
                digipot.set_step(step, 1)
                #print(digi1R)
                first = False
              
    #updates values
    clockwise, fast = rotary.getRotary()
    clicked, longClick = rotary.getButton()

    #if rotating
    if clockwise != 0:
          
        #updates the onscreen voltage value
        voltage += (clockwise * stepSize)

        #makes sure voltage is in range
        if voltage > maxV: voltage = maxV
        if voltage < minV: voltage = minV
            
        #updates lcd
        lcd.lcd_display_string(f"{voltage:.4f} V     ", 2)

    if clicked: 
        #update voltage values
        step = Min_difference.min_difference_volts(voltage)
        digipot.set_step(step, 1)

          
