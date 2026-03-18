import spidev #https://pypi.org/project/spidev/
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import time
import Dual_Digipot
import Rotary
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import Min_difference
import SquareWave

#set up libraries
pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = Rotary.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)
lcd = I2C_LCD_driver.lcd()

digipot.set_step(60, 0)
SquareWave.waveOff(19, pi1)

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
                pi1.write(19, 1)
                step = Min_difference.min_difference_volts(abs(voltage))
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
        if voltage >= 0:
            pi1.write(19, 0)
        else: 
            pi1.write(19, 1)
        
        if voltage == 5: 
            digipot.set_step(59, 1)
        elif voltage == 4.375: 
            digipot.set_step(67, 1)
        elif voltage == 3.75: 
            digipot.set_step(76, 1)
        elif voltage == 3.125: 
            digipot.set_step(84, 1)
        elif voltage == 2.5: 
            digipot.set_step(92, 1)
        elif voltage == 1.875: 
            digipot.set_step(100, 1)
        elif voltage == 1.25: 
            digipot.set_step(108, 1)
        elif voltage == 0.625: 
            digipot.set_step(116, 1)
        elif voltage == 0: 
            digipot.set_step(128, 1)
        elif voltage == -5: 
            digipot.set_step(62, 1)
        elif voltage == -4.375: 
            digipot.set_step(71, 1)
        elif voltage == -3.75: 
            digipot.set_step(80, 1)
        elif voltage == -3.125: 
            digipot.set_step(91, 1)
        elif voltage == -2.5: 
            digipot.set_step(98, 1)
        elif voltage == -1.875: 
            digipot.set_step(107, 1)
        elif voltage == -1.25: 
            digipot.set_step(116, 1)
        elif voltage == -0.625: 
            digipot.set_step(125, 1)

          
