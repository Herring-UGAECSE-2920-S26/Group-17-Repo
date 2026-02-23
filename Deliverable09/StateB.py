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
state = "FunGen"
digi0R = 100
digi1R = 100
minR = 100
maxR = 10000
menuFirst = True
square = False
clear = True

def get_ohmmeter_reading():
    found_step = 0
    # Sweep through all steps to find the comparator flip on GPIO4
    for step in range(0, 129):
        digipot.set_step(step, pot_num=0) 
        time.sleep(0.01) # Settle time for C3 in your ADC schematic
        
        if pi1.read(4) == 0: 
            found_step = step
            break
    
    # R = 0.0732 * step + 0.124 (from your Min_difference characterization)
    resistance = (0.0732 * found_step) + 0.124
    return resistance
#function that checks and updates the state
def checkState(thisState):

    #declare global vars
    global state
    global menuFirst
    global square
    global clear

    #match case statement that handles the states changing
    match thisState:

        #level 1
        case "FunGen":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False

            #switch to other menu option 
            if clockwise == 1: 
                state = "Ohm"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGenT"
                menuFirst = True
                clear = True

      # level 1 - Navigation to the Ohmmeter Menu
        case "Ohm":
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("> Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
            
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunGen"
                menuFirst = True
                clear = False
            #switch to other menu option 
            elif clockwise == 1:
                state = "Volt"
                menuFirst = True
                clear = False
            #switch to other menu option 
            elif clicked == True:
                state = "OhmB" # Takes you into the measurement submenu
                menuFirst = True
                clear = True

    # level 2 under Ohm - MEASUREMENT TRIGGER
        case "OhmB":
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Reading", 1) # Highlight Reading
                lcd.lcd_display_string("  Threshold", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            #switch to other menu option 
            if clockwise == 1:
                state = "OhmM" # Scroll down to 'Main'
                menuFirst = True
                clear = False
            
            # --- THE LIVE MEASUREMENT TRIGGER ---
            elif clicked == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("Measuring...", 1)
                
                # Perform the sweep
                reading = get_ohmmeter_reading()
                
                # Display results for photo/deliverable
                lcd.lcd_clear()
                lcd.lcd_display_string("Result:", 1)
                lcd.lcd_display_string(f"{reading:.3f} kOhms", 2)
                lcd.lcd_display_string("Click to return", 4)
                
                # Stay here until user clicks again
                time.sleep(0.5) # Debounce delay
                while True:
                    if rotary.getButton()[0]: 
                        break
                    time.sleep(0.1)
                
                menuFirst = True
                clear = True

        #level 1
        case "Volt":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("> Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "Ohm"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "DCRef"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "VoltS"
                menuFirst = True
                clear = True

        #level 1
        case "DCRef":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("> DC Reference", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "Volt"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "Back"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "DCRefVolt"
                menuFirst = True
                clear = True
                
        #level 1
        case "Back":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Ohmmeter", 1)
                lcd.lcd_display_string("  Voltmeter", 2)
                lcd.lcd_display_string("  DC Reference", 3)
                lcd.lcd_display_string("> Back", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCRef"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clockwise == 1:
                state = "Main"
                menuFirst = True 
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "DCRef"
                menuFirst = True
                clear = True

        #level 1
        case "Main":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Voltmeter", 1)
                lcd.lcd_display_string("  DC Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "Back"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 2 under FunGen
        case "FunGenT":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Type", 1)
                lcd.lcd_display_string("  Frequency", 2)
                lcd.lcd_display_string("  Amplitude", 3)
                lcd.lcd_display_string("  Output", 4)
                menuFirst = False
                                
            #switch to other menu option
            if clockwise == 1:
                state = "FunGenF"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "TypeS"
                menuFirst = True
                clear = True

        #level 2 under FunGen
        case "FunGenF":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Type", 1)
                lcd.lcd_display_string("> Frequency", 2)
                lcd.lcd_display_string("  Amplitude", 3)
                lcd.lcd_display_string("  Output", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunGenT"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FunGenA"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FreqI"
                menuFirst = True
                clear = True

        #level 2 under FunGen
        case "FunGenA":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Type", 1)
                lcd.lcd_display_string("  Frequency", 2)
                lcd.lcd_display_string("> Amplitude", 3)
                lcd.lcd_display_string("  Output", 4)
                menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunGenF"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FunGenO"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "AmpI"
                menuFirst = True
                clear = True

        #level 2 under FunGen
        case "FunGenO":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Type", 1)
                lcd.lcd_display_string("  Frequency", 2)
                lcd.lcd_display_string("  Amplitude", 3)
                lcd.lcd_display_string("> Output", 4)
                menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunGenA"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FunGenB"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "FunOutOn"
                menuFirst = True
                clear = True

        #level 2 under FunGen
        case "FunGenB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Frequency", 1)
                lcd.lcd_display_string("  Amplitude", 2)
                lcd.lcd_display_string("  Output", 3)
                lcd.lcd_display_string("> Back", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunGenO"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clockwise == 1:
                state = "FunGenM"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True
                
        #level 2 under FunGen
        case "FunGenM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Amplitude", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunGenB"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 3 under FunGenT
        case "TypeS":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("> Square", 2)
                    lcd.lcd_display_string("  Back", 3)
                    lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("> Square", 1)
                    lcd.lcd_display_string("  Back", 2)
                    lcd.lcd_display_string("  Main", 3)
                    menuFirst = False
                                
            #switch to other menu option
            if clockwise == 1:
                state = "TypeB"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                square = True
                menuFirst = True
                clear = True

        #level 3 under FunGenT
        case "TypeB":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("  Square", 2)
                    lcd.lcd_display_string("> Back", 3)
                    lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("  Square", 1)
                    lcd.lcd_display_string("> Back", 2)
                    lcd.lcd_display_string("  Main", 3)
                    menuFirst = False
                                    
            #switch to other menu option 
            if clockwise == -1: 
                state = "TypeS"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "TypeM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGenT"
                menuFirst = True
                clear = True

        #level 3 under FunGenT
        case "TypeM":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("  Square", 2)
                    lcd.lcd_display_string("  Back", 3)
                    lcd.lcd_display_string("> Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("  Square", 1)
                    lcd.lcd_display_string("  Back", 2)
                    lcd.lcd_display_string("> Main", 3)
                    menuFirst = False
                                    
            #switch to other menu option 
            if clockwise == -1: 
                state = "TypeB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 3 under FunGenF
        case "FreqI":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Input Frequency", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False

            #switch to other menu option
            if clockwise == 1:
                state = "FreqB"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under FunGenF
        case "FreqB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Input Frequency", 1)
                lcd.lcd_display_string("> Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FreqI"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FreqM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGenF"
                menuFirst = True
                clear = True

        #level 3 under FunGenF
        case "FreqM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Input Frequency", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("> Main", 3)
                menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FreqB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 3 under FunGenA
        case "AmpI":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Input Amplitude", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False
                
            #switch to other menu option
            if clockwise == 1:
                state = "AmpB"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under FunGenA
        case "AmpB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Input Amplitude", 1)
                lcd.lcd_display_string("> Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "AmpI"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "AmpM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGenA"
                menuFirst = True
                clear = True

        #level 3 under FunGenA
        case "AmpM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Input Amplitude", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("> Main", 3)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "AmpB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 3 under FunGenO
        case "FunOutOn":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                state = "FunOutOff"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under FunGenO
        case "FunOutOff":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("> Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunOutOn"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FunOutB"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under FunGenO
        case "FunOutB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunOutOff"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FunOutM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGenO"
                menuFirst = True
                clear = True

        #level 3 under FunGenO
        case "FunOutM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunOutB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 2 under Ohm
        case "OhmB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Reading", 1)
                lcd.lcd_display_string("  Threshold", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                state = "OhmM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "Ohm"
                menuFirst = True
                clear = True

        #level 2 under Ohm
        case "OhmM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Reading", 1)
                lcd.lcd_display_string("  Threshold", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "OhmB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 2 under Volt
        case "VoltS":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Reading  Threshold", 1)
                lcd.lcd_display_string("> Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                state = "VoltB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "SourceEx"
                menuFirst = True
                clear = True

        #level 2 under Volt
        case "VoltB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Reading  Threshold", 1)
                lcd.lcd_display_string("  Source", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "VoltS"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "VoltM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "Volt"
                menuFirst = True
                clear = True
            
        #level 2 under Volt
        case "VoltM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Reading  Threshold", 1)
                lcd.lcd_display_string("  Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "VoltB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True
                
        #level 3 under VoltS
        case "SourceEx":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> External", 1)
                lcd.lcd_display_string("  Internal Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option
            elif clockwise == 1:
                state = "SourceIn"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under VoltS
        case "SourceIn":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  External", 1)
                lcd.lcd_display_string("> Internal Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "SourceEx"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "SourceB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "DCRefVolt"
                menuFirst = True
                clear = True

        #level 3 under VoltS
        case "SourceB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  External", 1)
                lcd.lcd_display_string("  Internal Reference", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "SourceIn"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "SourceM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "VoltS"
                menuFirst = True
                clear = True

        #level 3 under VoltS
        case "SourceM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  External", 1)
                lcd.lcd_display_string("  Internal Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "SourceB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 2 under DCRef
        case "DCRefVolt":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> VoltageValue Input", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                state = "DCRefOut"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 2 under DCRef
        case "DCRefOut":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  VoltageValue Input", 1)
                lcd.lcd_display_string("> Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCRefVolt"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "DCRefB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "DCOutOn"
                menuFirst = True
                clear = True

        #level 2 under DCRef
        case "DCRefB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  VoltageValue Input", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCRefOut"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "DCRefM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "DCRef"
                menuFirst = True
                clear = True

        #level 2 under DCRef
        case "DCRefM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  VoltageValue Input", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCRefB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 3 under DCRefOut
        case "DCOutOn":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            #switch to other menu option
            if clockwise == 1:
                state = "DCOutOff"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under DCRefOut
        case "DCOutOff":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("> Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCOutOn"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "DCOutB"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                print("Implement later")
                clear = False

        #level 3 under DCRefOut
        case "DCOutB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCOutOff"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "DCOutM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "DCRefOut"
                menuFirst = True
                clear = True

        #level 3 under DCRefOut
        case "DCOutM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCOutB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FunGen"
                menuFirst = True
                clear = True


#------ Main Running Code ------#
try:

    #keeps allowing the states to change
    while True:

        #updates values
        clockwise, fast = rotary.getRotary()
        clicked, longClick = rotary.getButton()

        #checks and changes state
        checkState(state)

        #saves cpu
        time.sleep(0.05)

#cleanly stops on keyboard interrupt 
except KeyboardInterrupt:
    rotary.cancel()
    lcd.lcd_clear()
