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

# Variables for the loop
last_tally = 0

while True:
    # --- 1. READ THREAD & LIMIT SPEED ---
    current_tally = rotary.tally
    change = current_tally - last_tally
    last_tally = current_tally 
    
    # THE FIX: Limit max jump to 5 steps per loop
    if change > 5: change = 5
    if change < -5: change = -5

    # --- 2. LOGIC ---
    if state == "menu0":
        if menu0First:
             lcd.lcd_clear()
             lcd.lcd_display_string("=> DigiPot0", 1)
             lcd.lcd_display_string("   DigiPot1", 2)
             menu0First = False
        
        if change != 0: 
             state = "menu1"
             menu1First = True
        elif rotary.clicked:
             rotary.clicked = False
             state = "digi0"
             digi0First = True

    elif state == "menu1":
        if menu1First:
             lcd.lcd_clear()
             lcd.lcd_display_string("   DigiPot0", 1)
             lcd.lcd_display_string("=> DigiPot1", 2)
             menu1First = False

        if change != 0: 
             state = "menu0"
             menu0First = True
        elif rotary.clicked:
             rotary.clicked = False
             state = "digi1"
             digi1First = True

    elif state == "digi0":
        if digi0First:
             lcd.lcd_clear()
             lcd.lcd_display_string("DigiPot 0 Resistance", 1)
             lcd.lcd_display_string(f"{digi0R} Ohms", 2)
             digi0First = False

        if change != 0:
            # Smooth scaling: 20 if fast, 5 if slow
            step_size = 20 if rotary.fast else 5
            digi0R += (change * step_size)
            
            if digi0R > maxR: digi0R = maxR
            if digi0R < minR: digi0R = minR
            
            lcd.lcd_display_string(f"{digi0R} Ohms    ", 2)

        if rotary.longClicked:
            rotary.longClicked = False
            state = "menu0"
            menu0First = True
        elif rotary.clicked:
            rotary.clicked = False
            print("Updated DigiPot0 HW")
            step = Min_difference.min_difference(float(digi0R/1000))
            digipot.set_step(step, 0)
            time.sleep(0.2) 

    elif state == "digi1":
        # Same logic as digi0 but for digi1R
        if digi1First:
             lcd.lcd_clear()
             lcd.lcd_display_string("DigiPot 1 Resistance", 1)
             lcd.lcd_display_string(f"{digi1R} Ohms", 2)
             digi1First = False

        if change != 0:
            step_size = 20 if rotary.fast else 5
            digi1R += (change * step_size)
            
            if digi1R > maxR: digi1R = maxR
            if digi1R < minR: digi1R = minR
            
            lcd.lcd_display_string(f"{digi1R} Ohms    ", 2)

        if rotary.longClicked:
            rotary.longClicked = False
            state = "menu0"
            menu0First = True
        elif rotary.clicked:
            rotary.clicked = False
            print("Updated DigiPot1 HW")
            step = Min_difference.min_difference(float(digi1R/1000))
            digipot.set_step(step, 1)
            time.sleep(0.2)

    time.sleep(0.05)
