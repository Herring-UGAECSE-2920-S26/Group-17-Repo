import pigpio
import time
import asyncio
import Dual_Digipot
import RotaryFunctions
#from transitions import AsyncMachine
# from RPLCD.i2c import CharLCD

pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = RotaryFunctions.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)

#create asynchronous tasks
rotarySpin = asyncio.create_task(rotary.checkRotary)
buttonPress = asyncio.create_task(rotary.checkButton)

#perpetually run both tasks together
asyncio.gather(rotarySpin, buttonPress)

#declare vars
state = "menu1"
digi1R = 100
digi2R = 100
minR = 100
maxR = 10000

while True:

    #main menu part 1
    while state == "menu1":
        print("=> DigiPot1    Digipot2")
        #insert proper LCD updating code here
        if rotary.rotating == True:
            state = "menu2"
        elif rotary.clicked == True:
            state = "digi1"

        #main menu part 2
        while state == "menu2":
            #insert proper LCD updating code here
            print("   DigiPot1 => Digipot2")
            if rotary.rotating == True:
                state = "menu1"
            elif rotary.clicked == True:
                state = "digi2"

        #DigiPot1 handling
        while state == "digi1":
            #insert proper LCD updating code here
            print(digi1R)
            if rotary.rotating == True:
                if rotary.clockwise == True and digi1R != maxR:
                    if rotary.fast == True:
                        digi1R = digi1R + 100
                    else:
                        digi1R = digi1R + 10
                if rotary.clockwise == False and digi1R != minR:
                    if rotary.fast == True:
                        digi1R = digi1R - 100
                    else:
                        digi1R = digi1R - 10
            elif rotary.clicked == True:
                if rotary.longClick == True:
                    state = "menu1"
                else:
                    print("Updated DigiPot1")
                    #insert proper digipot updating code here

        #DigiPot2 handling
        while state == "digi2":
            #insert proper LCD updating code here
            print(digi2R)
            if rotary.rotating == True:
                if rotary.clockwise == True and digi2R != maxR:
                    if rotary.fast == True:
                        digi2R = digi2R + 100
                    else:
                        digi2R = digi2R + 10
                if rotary.clockwise == False and digi1R != minR:
                    if rotary.fast == True:
                        digi2R = digi2R - 100
                    else:
                        digi2R = digi2R - 10
            elif rotary.clicked == True:
                if rotary.longClick == True:
                    state = "menu1"
                else:
                    print("Updated DigiPot2")
                    #insert proper digipot updating code here
    
