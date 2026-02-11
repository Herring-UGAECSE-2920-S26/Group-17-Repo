import spidev #https://pypi.org/project/spidev/
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import time
import threading
import Dual_Digipot
import RotaryFunctions
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import Min_difference

#set up libraries
pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = RotaryFunctions.Rotary(18,23,24, pi1)
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

#set up threads
rotaryThread = threading.Thread(target=rotary.checkRotary)
buttonThread = threading.Thread(target=rotary.checkButton)

rotaryThread.start()
buttonThread.start()

while True:

    #main menu part 0
    while state == "menu0":
        #updates led when something has changed
        if menu0First == True:
            lcd.lcd_clear()
            lcd.lcd_display_string("=> DigiPot0", 1)
            lcd.lcd_display_string("   DigiPot1", 2)
            print("=> DigiPot0    Digipot1")
        #switch to other menu option if rotating
        if rotary.rotating == True: 
            state = "menu1"
            menu1First = True
        #switch to digipot 0 if clicked
        elif rotary.clicked == True:
            state = "digi0"
            digi0First = True
        menu0First = False
        
        #main menu part 1
        while state == "menu1":
            #updates led when something has changed
            if menu1First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("   DigiPot0", 1)
                lcd.lcd_display_string("=> DigiPot1", 2)
                print("   DigiPot0 => Digipot1")
            #switch to other menu option if rotating
            if rotary.rotating == True: 
                state = "menu0"
                menu0First = True
            #switch to digipot1 if clicked
            elif rotary.clicked == True:
                state = "digi1"
                digi1First = True
            menu1First = False

        #DigiPot0 handling
        while state == "digi0":
            if rotary.rotating == True:
                if rotary.clockwise == True: 
                    if digi0R < maxR:
                        #increases resistance by 100 if going clockwise fast and not max
                        if rotary.fast == True: 
                            #print("Plus 100")
                            digi0R = digi0R + 100 
                            if digi0R > maxR: #makes sure resistance doesn't go above max
                                digi0R = maxR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
                        else: #increases resistance by 10 if going clockwise slow and not max
                            #print("Plus 10")
                            digi0R = digi0R + 10 
                            if digi0R > maxR: #makes sure resistance doesn't go above max
                                digi0R = maxR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
                if rotary.clockwise == False:
                    if digi0R > minR:
                        #decreases resistance by 100 if going counterclockwise fast
                        if rotary.fast == True:
                            #print("Minus 100")
                            digi0R = digi0R - 100
                            if digi0R < minR: #makes sure resistance doesn't go below min
                                digi0R = minR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
                        else: #decreases resistance by 10 if going counterclockwise slow
                            #print("Minus 10")
                            digi0R = digi0R - 10
                            if digi0R < minR: #makes sure resistance doesn't go below min
                                digi0R = minR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
            #switches to menu0 if button long pressed
            if rotary.clicked == True:
                startTime = time.perf_counter()
                pi1.wait_for_edge(rotary.switchPin, pigpio.EITHER_EDGE)
                endTime = time.perf_counter()
                #print(abs(startTime - endTime))
                #print(abs(startTime - endTime) >= 3)
                if abs(startTime - endTime) >= 3:
                    state = "menu0"
                    menu0First = True
                    rotary.clicked = False
                else: #updates digipot value on short buttonpress
                    print("Updated DigiPot0")
                    rotary.clicked = False
                    step = Min_difference.min_difference(float(digi0R/1000))
                    digipot.set_step(step, 0)
            #updates led when something has changed
            if digi0First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 0 Resistance", 1)
                lcd.lcd_display_string(f"{digi0R} Ohms", 2)
                print(digi0R)
                digi0First = False

        #DigiPot1 handling
        while state == "digi1":
            if rotary.rotating == True:
                if rotary.clockwise == True: 
                    if digi1R < maxR:
                        #increases resistance by 100 if going clockwise fast and not max
                        if rotary.fast == True:
                            #print("Plus 100")
                            digi1R = digi1R + 100
                            if digi1R > maxR: #makes sure resistance doesn't go above max
                                digi1R = maxR
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                        else:
                            #print("Plus 10")
                            digi1R = digi1R + 10
                            if digi1R > maxR:
                                digi1R = maxR
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                if rotary.clockwise == False:
                    if digi1R > minR:
                        #decreases resistance by 100 if going counterclockwise fast
                        if rotary.fast == True:
                            #print("Minus 100")
                            digi1R = digi1R - 100
                            if digi1R < minR: #makes sure resistance doesn't go below min
                                digi1R = minR
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                        else: #decreases resistance by 10 if going counterclockwise slow
                            #print("Minus 10")
                            digi1R = digi1R - 10
                            if digi1R < minR: #makes sure resistance doesn't go below min
                                digi1R = minR
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
            #switches to menu0 if button long pressed
            if rotary.clicked == True:
                startTime = time.perf_counter()
                pi1.wait_for_edge(rotary.switchPin, pigpio.EITHER_EDGE)
                endTime = time.perf_counter()
                #print(abs(startTime - endTime))
                #print(abs(startTime - endTime) >= 3)
                if abs(startTime - endTime) >= 3:
                    state = "menu0"
                    menu0First = True
                    rotary.clicked = False
                else: #updates digipot value on short buttonpress
                    print("Updated DigiPot1")
                    rotary.clicked = False
                    step = Min_difference.min_difference(float(digi1R/1000))
                    digipot.set_step(step, 1)
            #updates led when something has changed
            if digi1First == True: 
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 1 Resistance", 1)
                lcd.lcd_display_string(f"{digi1R} Ohms", 2)
                print(digi1R)
                digi1First = False

    
