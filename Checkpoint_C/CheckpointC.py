import spidev
import pigpio
import time
import threading
#import asyncio
import Dual_Digipot
import RotaryFunctions
#from transitions import AsyncMachine
# from RPLCD.i2c import CharLCD

pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = RotaryFunctions.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)

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
            if digi1First == True:
                #insert proper LCD updating code here
                print(digi1R)
            if rotary.rotating == True:
                if rotary.clockwise == True: 
                    if digi1R < maxR:
                        if rotary.fast == True:
                            #print("Plus 100")
                            digi1R = digi1R + 100
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                        else:
                            #print("Plus 10")
                            digi1R = digi1R + 10
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                if rotary.clockwise == False:
                    if digi1R > minR:
                        if rotary.fast == True:
                            #print("Minus 100")
                            digi1R = digi1R - 100
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
                        else:
                            #print("Minus 10")
                            digi1R = digi1R - 10
                            #print("digi1R:", digi1R)
                            rotary.rotating = False
                            digi1First = True
            if rotary.clicked == True:
                if rotary.longClick == True:
                    state = "menu1"
                    menu1First = True
                if rotary.longClick == False:
                    print("Updated DigiPot1")
                    #insert proper digipot updating code here
            if digi1First == True:
                print(digi1R)
                digi1First = False

        #DigiPot2 handling
        while state == "digi2":
            if digi2First == True:
                #insert proper LCD updating code here
                print(digi2R)
            if rotary.rotating == True:
                if rotary.clockwise == True and digi2R != maxR:
                    if rotary.fast == True:
                        digi2R = digi2R + 100
                        digi2First = True
                    else:
                        digi2R = digi2R + 10
                if rotary.clockwise == False and digi1R != minR:
                    if rotary.fast == True:
                        digi2R = digi2R - 100
                        digi2First = True
                    else:
                        digi2R = digi2R - 10
                        digi2First = True
            if rotary.clicked == True and rotary.longClick == False:
                print("Updated DigiPot2")
                #insert proper digipot updating code here
            if rotary.clicked == True and rotary.longClick == True:
                state = "menu1"
                menu1First = True
                #if rotary.longClick == True:
                    #state = "menu1"
                    #menu1First = True
                #elif rotary.longClick == False:
                    #print("Updated DigiPot2")
                    #insert proper digipot updating code here
            if rotary.rotating == False:
                digi2First = False
    
