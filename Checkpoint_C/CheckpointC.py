import spidev
import pigpio
import time
import threading
#import asyncio
import Dual_Digipot
import RotaryFunctions
import I2C_LCD_driver
#from transitions import AsyncMachine
# from RPLCD.i2c import CharLCD
import Min_difference

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

#async def always(): 
    #create asynchronous tasks
    #rotarySpin = asyncio.create_task(rotary.checkRotary())
    #buttonPress = asyncio.create_task(rotary.checkButton())

    #perpetually run both tasks together
    #asyncio.gather(rotarySpin, buttonPress)

#run the tasks in always()
#asyncio.run(always())

rotaryThread = threading.Thread(target=rotary.checkRotary)
buttonThread = threading.Thread(target=rotary.checkButton)

rotaryThread.start()
buttonThread.start()

while True:

    #main menu part 0
    while state == "menu0":
        if menu0First == True:
            lcd.lcd_clear()
            lcd.lcd_display_string("=> DigiPot0", 1)
            lcd.lcd_display_string("   DigiPot1", 2)
            print("=> DigiPot0    Digipot1")
            #insert proper LCD updating code here
        if rotary.rotating == True: 
            state = "menu1"
            menu1First = True
        elif rotary.clicked == True:
            state = "digi0"
            digi0First = True
        menu0First = False

        #main menu part 1
        while state == "menu1":
            if menu1First == True:
                #insert proper LCD updating code here
                lcd.lcd_clear()
                lcd.lcd_display_string("   DigiPot0", 1)
                lcd.lcd_display_string("=> DigiPot1", 2)
                print("   DigiPot0 => Digipot1")
            if rotary.rotating == True: 
                state = "menu0"
                menu0First = True
            elif rotary.clicked == True:
                state = "digi1"
                digi1First = True
            menu1First = False

        #DigiPot0 handling
        while state == "digi0":
            #rotary.clicked = False
            #rotary.rotating = False
            #if digi0First == True:
                #insert proper LCD updating code here
                #print(digi0R)
            if rotary.rotating == True:
                if rotary.clockwise == True: 
                    if digi0R < maxR:
                        if rotary.fast == True:
                            #print("Plus 100")
                            digi0R = digi0R + 100
                            if digi0R > maxR:
                                digi0R = maxR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
                        else:
                            #print("Plus 10")
                            digi0R = digi0R + 10
                            if digi0R > maxR:
                                digi0R = maxR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
                if rotary.clockwise == False:
                    if digi0R > minR:
                        if rotary.fast == True:
                            #print("Minus 100")
                            digi0R = digi0R - 100
                            if digi0R < minR:
                                digi0R = minR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
                        else:
                            #print("Minus 10")
                            digi0R = digi0R - 10
                            if digi0R < minR:
                                digi0R = minR
                            #print("digi0R:", digi0R)
                            rotary.rotating = False
                            digi0First = True
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
           # elif rotary.clicked == True:
                else:
                    print("Updated DigiPot0")
                    rotary.clicked = False
                    #insert proper digipot updating code here
                    step = Min_difference.min_difference(float(digi0R/1000))
                    digipot.set_step(step, 0)
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
                        if rotary.fast == True:
                            #print("Plus 100")
                            digi1R = digi1R + 100
                            if digi1R > maxR:
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
                        if rotary.fast == True:
                            #print("Minus 100")
                            digi1R = digi1R - 100
                            if digi1R < minR:
                                digi1R = minR
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                        else:
                            #print("Minus 10")
                            digi1R = digi1R - 10
                            if digi1R < minR:
                                digi1R = minR
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
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
           # elif rotary.clicked == True:
                else:
                    print("Updated DigiPot1")
                    rotary.clicked = False
                    #insert proper digipot updating code here
                    step = Min_difference.min_difference(float(digi1R/1000))
                    digipot.set_step(step, 1)
            if digi1First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 1 Resistance", 1)
                lcd.lcd_display_string(f"{digi1R} Ohms", 2)
                print(digi1R)
                digi1First = False

    
