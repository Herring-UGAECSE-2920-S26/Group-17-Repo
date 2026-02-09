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

pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = RotaryFunctions.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)
lcd = I2C_LCD_driver.lcd()

#declare vars
state = "menu1"
digi1R = 100
digi2R = 100
minR = 100
maxR = 10000
menu1First = True
menu2First = True
digi1First = True
digi2First = True

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

    #main menu part 1
    while state == "menu1":
        if menu1First == True:
            lcd.lcd_clear()
            lcd.lcd_display_string("=> DigiPot1", 1)
            lcd.lcd_display_string("   Digipot2", 2)
            print("=> DigiPot1    Digipot2")
            #insert proper LCD updating code here
        if rotary.rotating == True:
            state = "menu2"
            menu2First = True
        elif rotary.clicked == True:
            state = "digi1"
            digi1First = True
        menu1First = False

        #main menu part 2
        while state == "menu2":
            if menu2First == True:
                #insert proper LCD updating code here
                lcd.lcd_clear()
                lcd.lcd_display_string("   DigiPot1", 1)
                lcd.lcd_display_string("=> Digipot2", 2)
                print("   DigiPot1 => Digipot2")
            if rotary.rotating == True:
                state = "menu1"
                menu1First = True
            elif rotary.clicked == True:
                state = "digi2"
                digi2First = True
            menu2First = False

        #DigiPot1 handling
        while state == "digi1":
            #rotary.clicked = False
            #rotary.rotating = False
            #if digi1First == True:
                #insert proper LCD updating code here
                #print(digi1R)
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
                    state = "menu1"
                    menu1First = True
                    rotary.clicked = False
           # elif rotary.clicked == True:
                else:
                    print("Updated DigiPot1")
                    rotary.clicked = False
                    #insert proper digipot updating code here
                    step = int(((digi1R - 78) / maxR) * 128)
                    digipot.set_step(step, 0)
            if digi1First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 1 Resistance", 1)
                lcd.lcd_display_string("{digi1R} Ohms", 2)
                print(digi1R)
                digi1First = False

        #DigiPot2 handling
        while state == "digi2":
            if rotary.rotating == True:
                if rotary.clockwise == True: 
                    if digi2R < maxR:
                        if rotary.fast == True:
                            #print("Plus 100")
                            digi2R = digi2R + 100
                            if digi2R > maxR:
                                digi2R = maxR
                            #print("digi2R:", digi2R)
                            rotary.rotating = False
                            digi2First = True
                        else:
                            #print("Plus 10")
                            digi2R = digi2R + 10
                            if digi2R > maxR:
                                digi2R = maxR
                            #print("digi2R:", digi2R)
                            rotary.rotating = False
                            digi2First = True
                if rotary.clockwise == False:
                    if digi2R > minR:
                        if rotary.fast == True:
                            #print("Minus 100")
                            digi2R = digi2R - 100
                            if digi2R < minR:
                                digi2R = minR
                            #print("digi2R:", digi2R)
                            rotary.rotating = False
                            digi2First = True
                        else:
                            #print("Minus 10")
                            digi2R = digi2R - 10
                            if digi2R < minR:
                                digi2R = minR
                            #print("digi2R:", digi2R)
                            rotary.rotating = False
                            digi2First = True
            if rotary.clicked == True:
                startTime = time.perf_counter()
                pi1.wait_for_edge(rotary.switchPin, pigpio.EITHER_EDGE)
                endTime = time.perf_counter()
                #print(abs(startTime - endTime))
                #print(abs(startTime - endTime) >= 3)
                if abs(startTime - endTime) >= 3:
                    state = "menu1"
                    menu1First = True
                    rotary.clicked = False
           # elif rotary.clicked == True:
                else:
                    print("Updated DigiPot2")
                    rotary.clicked = False
                    #insert proper digipot updating code here
                    step = int(((digi2R - 78) / maxR) * 128)
                    digipot.set_step(step, 1)
            if digi2First == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("DigiPot 2 Resistance", 1)
                lcd.lcd_display_string("{digi2R} Ohms", 2)
                print(digi2R)
                digi2First = False

    
