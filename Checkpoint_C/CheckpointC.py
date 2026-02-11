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

# --- FIX: Define this before the loop starts ---
last_tally = 0 
# -----------------------------------------------

#set up threads
rotaryThread = threading.Thread(target=rotary.checkRotary)
buttonThread = threading.Thread(target=rotary.checkButton)

rotaryThread.start()
buttonThread.start()

while True:
    current_tally = rotary.tally
    change = current_tally - last_tally
    last_tally = current_tally 
    
    # Speed Limiter
    if change > 5: change = 5
    if change < -5: change = -5

    # --- MENU 0 ---
    if state == "menu0":
        if menu0First == True:
            lcd.lcd_clear()
            lcd.lcd_display_string("=> DigiPot0", 1)
            lcd.lcd_display_string("   DigiPot1", 2)
            print("=> DigiPot0    Digipot1")
            menu0First = False
            
        if change != 0: 
            state = "menu1"
            menu1First = True
        elif rotary.clicked == True:
            rotary.clicked = False # Reset flag!
            state = "digi0"
            digi0First = True
        
    # --- MENU 1 ---
    if state == "menu1":
        if menu1First == True:
            lcd.lcd_clear()
            lcd.lcd_display_string("   DigiPot0", 1)
            lcd.lcd_display_string("=> DigiPot1", 2)
            print("   DigiPot0 => Digipot1")
            menu1First = False

        if change != 0: 
            state = "menu0"
            menu0First = True
        elif rotary.clicked == True:
            rotary.clicked = False # Reset flag!
            state = "digi1"
            digi1First = True

    # --- DIGIPOT 0 CONTROL ---
    if state == "digi0":
        if digi0First == True:
            lcd.lcd_clear()
            lcd.lcd_display_string("DigiPot 0 Resistance", 1)
            lcd.lcd_display_string(f"{digi0R} Ohms", 2)
            print(digi0R)
            digi0First = False

        if change != 0:
            step_size = 20 if rotary.fast else 5
            digi0R += (change * step_size)
            
            if digi0R > maxR: digi0R = maxR
            if digi0R < minR: digi0R = minR
            
            lcd.lcd_display_string(f"{digi0R} Ohms    ", 2)
            print(f"Digi0: {digi0R}")
        
        # Check buttons (non-blocking)
        if rotary.longClicked == True:
            rotary.longClicked = False
            state = "menu0"
            menu0First = True
        elif rotary.clicked == True:
            rotary.clicked = False
            print("Updated DigiPot0")
            step = Min_difference.min_difference(float(digi0R/1000))
            digipot.set_step(step, 0)

    # --- DIGIPOT 1 CONTROL ---
    if state == "digi1":
        if digi1First == True: 
            lcd.lcd_clear()
            lcd.lcd_display_string("DigiPot 1 Resistance", 1)
            lcd.lcd_display_string(f"{digi1R} Ohms", 2)
            print(digi1R)
            digi1First = False

        if change != 0:
            step_size = 20 if rotary.fast else 5
            
            # Use digi1R (Fixed copy-paste error)
            digi1R += (change * step_size)
            
            if digi1R > maxR: digi1R = maxR
            if digi1R < minR: digi1R = minR
            
            lcd.lcd_display_string(f"{digi1R} Ohms    ", 2)
            print(f"Digi1: {digi1R}")

        # Check buttons (non-blocking)
        if rotary.longClicked == True:
            rotary.longClicked = False
            state = "menu0"
            menu0First = True
        elif rotary.clicked == True:
            rotary.clicked = False
            print("Updated DigiPot1")
            step = Min_difference.min_difference(float(digi1R/1000))
            digipot.set_step(step, 1)

    time.sleep(0.05)
