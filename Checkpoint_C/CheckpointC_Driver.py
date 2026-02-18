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

#declare vars
state = "menu0"
digi0R = 100
digi1R = 100
minR = 100
maxR = 10000
menu0First = True
menu1First = True
digi0First = True
digi1First = True

try:

    while True:
        #updates values
        clockwise, fast = rotary.getRotary()
        clicked, longClick = rotary.getButton()
        #print("Clockwise:", clockwise)
        #print("Fast:", fast)
        #print("Clicked:", clicked)
        #print("LongClick:", longClick)

        #main menu part 0
        if state == "menu0":
            #updates led when something has changed
            if menu0First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("=> DigiPot0", 1)
                lcd.lcd_display_string("   DigiPot1", 2)
                print("=> DigiPot0    Digipot1")
                menu0First = False

            #switch to other menu option if rotating
            if clockwise != 0: 
                #print("Switch to menu1")
                state = "menu1"
                menu1First = True
            #switch to digipot 0 if clicked
            elif clicked == True:
                state = "digi0"
                digi0First = True
        
        #main menu part 1
        elif state == "menu1":
            #updates led when something has changed
            if menu1First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("   DigiPot0", 1)
                lcd.lcd_display_string("=> DigiPot1", 2)
                print("   DigiPot0 => Digipot1")
                menu1First = False
                
            #switch to other menu option if rotating
            if clockwise != 0: 
                #print("Switch to menu0")
                state = "menu0"
                menu0First = True 
            #switch to digipot1 if clicked  
            elif clicked == True:
                state = "digi1"
                digi1First = True

        #DigiPot0 handling
        elif state == "digi0":
            
            #updates led when something has changed
            if digi0First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 0 Resistance", 1)
                lcd.lcd_display_string(f"{digi0R} Ohms", 2)
                if digi0R == minR: 
                    step = Min_difference.min_difference(float(digi0R/1000))
                    digipot.set_step(step, 0)
                print(digi0R)
                digi0First = False

            #if rotating
            if clockwise != 0:
                #updates the onscreen resistor value
                stepSize = 100 if fast else 10 
                #print("StepSize:", stepSize)
                digi0R += (clockwise * stepSize)
                #print("Digi0R:", digi0R)

                #makes sure resistance is in range
                if digi0R > maxR: digi0R = maxR
                if digi0R < minR: digi0R = minR

                #updates lcd
                lcd.lcd_display_string(f"{digi0R} Ohms    ", 2)

            if clicked:
                #finds if longClick
                startTime = time.perf_counter()
                looped = pi1.read(rotary.switchPin)
        
                while looped != 1:
                    endTime = time.perf_counter()
                    if abs(startTime - endTime) >= 3:
                        longClick = True
                        looped = 1
                    else: looped = pi1.read(rotary.switchPin)
                #goes back to main menu
                if longClick:
                    state = "menu0"
                    menu0First = True
                #updates the digiPot
                else:
                    print("Updated DigiPot0")
                    step = Min_difference.min_difference(float(digi0R/1000))
                    digipot.set_step(step, 0)

                    
        #DigiPot1 handling
        elif state == "digi1":
            
            #updates led when something has changed
            if digi1First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 1 Resistance", 1)
                lcd.lcd_display_string(f"{digi1R} Ohms", 2)
                if digi1R == minR:
                    step = Min_difference.min_difference(float(digi1R/1000))
                    digipot.set_step(step, 1)
                print(digi1R)
                digi1First = False

            #if rotating
            if clockwise != 0:
                #updates the onscreen resistor value
                stepSize = 100 if fast else 10
                #print("StepSize:", stepSize)
                digi1R += (clockwise * stepSize)
                #print("Digi1R:", digi1R)

                #makes sure resistance is in range
                if digi1R > maxR: digi1R = maxR
                if digi1R < minR: digi1R = minR

                #updates lcd
                lcd.lcd_display_string(f"{digi1R} Ohms    ", 2)

            if clicked:
                #finds if longClick
                startTime = time.perf_counter()
                looped = pi1.read(rotary.switchPin)
        
                while looped != 1:
                    endTime = time.perf_counter()
                    if abs(startTime - endTime) >= 3:
                        longClick = True
                        looped = 1
                    else: looped = pi1.read(rotary.switchPin)
                #goes back to main menu
                if longClick:
                    state = "menu0"
                    menu0First = True
                #updates the digiPot
                else:
                    print("Updated DigiPot1")
                    step = Min_difference.min_difference(float(digi1R/1000))
                    digipot.set_step(step, 1)

        time.sleep(0.05)
        
#cleanly stops on keyboard interrupt 
except KeyboardInterrupt:
    rotary.cancel()
    lcd.lcd_clear()
