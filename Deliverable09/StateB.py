import spidev #https://pypi.org/project/spidev/
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import time
import Dual_Digipot
import Rotary
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import Min_difference

#set up devices
rotary = Rotary.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)
lcd = I2C_LCD_driver.lcd()

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

def checkState(state):

    match state:

        #level 1
        case "FunGen":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                global menuFirst = False

            #switch to other menu option 
            if clockwise == 1: 
                global state = "Ohm"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGenT"
                global menuFirst = True

        #level 1
        case "Ohm":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("> Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunGen"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "Volt"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "OhmB"
                global menuFirst = True

        #level 1
        case "Volt":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("> Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "Ohm"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "DCRef"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "VoltS"
                global menuFirst = True

        #level 1
        case "DCRef":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("> DC Reference", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "Volt"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "Back"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "DCRefVolt"
                global menuFirst = True
                
        #level 1
        case "Back":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Ohmmeter", 1)
                lcd.lcd_display_string("  Voltmeter", 2)
                lcd.lcd_display_string("  DC Reference", 3)
                lcd.lcd_display_string("> Back", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCRef"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "Main"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "DCRef"
                global menuFirst = True

        #level 1
        case "Main":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Voltmeter", 1)
                lcd.lcd_display_string("  DC Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "Back"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 2 under FunGen
        case "FunGenT":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> Type", 1)
                lcd.lcd_display_string("  Frequency", 2)
                lcd.lcd_display_string("  Amplitude", 3)
                lcd.lcd_display_string("  Output", 4)
                global menuFirst = False
                                
            #switch to other menu option
            if clockwise == 1:
                global state = "FunGenF"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "TypeS"
                global menuFirst = True

        #level 2 under FunGen
        case "FunGenF":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Type", 1)
                lcd.lcd_display_string("> Frequency", 2)
                lcd.lcd_display_string("  Amplitude", 3)
                lcd.lcd_display_string("  Output", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunGenT"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FunGenA"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FreqI"
                global menuFirst = True

        #level 2 under FunGen
        case "FunGenA":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Type", 1)
                lcd.lcd_display_string("  Frequency", 2)
                lcd.lcd_display_string("> Amplitude", 3)
                lcd.lcd_display_string("  Output", 4)
                global menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunGenF"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FunGenO"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "AmpI"
                global menuFirst = True

        #level 2 under FunGen
        case "FunGenO":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Type", 1)
                lcd.lcd_display_string("  Frequency", 2)
                lcd.lcd_display_string("  Amplitude", 3)
                lcd.lcd_display_string("> Output", 4)
                global menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunGenA"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FenGenB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGenOutOn"
                global menuFirst = True

        #level 2 under FunGen
        case "FunGenB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Frequency", 1)
                lcd.lcd_display_string("  Amplitude", 2)
                lcd.lcd_display_string("  Output", 3)
                lcd.lcd_display_string("> Back", 4)
                global menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunGenO"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FunGenM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True
                
        #level 2 under FunGen
        case "FunGenM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Amplitude", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunGenB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 3 under FunGenT
        case "TypeS":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("> Square", 2)
                    lcd.lcd_display_string("  Back", 3)
                    lcd.lcd_display_string("  Main", 4)
                    global menuFirst = False
                else:
                    lcd.lcd_clear()
                    lcd.lcd_display_string("> Square", 1)
                    lcd.lcd_display_string("  Back", 2)
                    lcd.lcd_display_string("  Main", 3)
                    global menuFirst = False
                                
            #switch to other menu option
            if clockwise == 1:
                global state = "TypeB"
                global menuFirst = True
            #do action
            elif clicked == True:
                global square = True
                global menuFirst = True

        #level 3 under FunGenT
        case "TypeB":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("  Square", 2)
                    lcd.lcd_display_string("> Back", 3)
                    lcd.lcd_display_string("  Main", 4)
                    global menuFirst = False
                else:
                    lcd.lcd_clear()
                    lcd.lcd_display_string("  Square", 1)
                    lcd.lcd_display_string("> Back", 2)
                    lcd.lcd_display_string("  Main", 3)
                    global menuFirst = False
                                    
            #switch to other menu option 
            if clockwise == -1: 
                global state = "TypeS"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "TypeM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGenT"
                global menuFirst = True

        #level 3 under FunGenT
        case "TypeM":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("  Square", 2)
                    lcd.lcd_display_string("  Back", 3)
                    lcd.lcd_display_string("> Main", 4)
                    global menuFirst = False
                else:
                    lcd.lcd_clear()
                    lcd.lcd_display_string("  Square", 1)
                    lcd.lcd_display_string("  Back", 2)
                    lcd.lcd_display_string("> Main", 3)
                    global menuFirst = False
                                    
            #switch to other menu option 
            if clockwise == -1: 
                global state = "TypeB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 3 under FunGenF
        case "FreqI":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> Input Frequency", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("  Main", 3)
                global menuFirst = False

            #switch to other menu option
            if clockwise == 1:
                global state = "FreqB"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under FunGenF
        case "FreqB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Input Frequency", 1)
                lcd.lcd_display_string("> Back", 2)
                lcd.lcd_display_string("  Main", 3)
                global menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FreqI"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FreqM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGenF"
                global menuFirst = True

        #level 3 under FunGenF
        case "FreqM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Input Frequency", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("> Main", 3)
                global menuFirst = False
                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FreqB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 3 under FunGenA
        case "AmpI":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> Input Amplitude", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("  Main", 3)
                global menuFirst = False
                
            #switch to other menu option
            if clockwise == 1:
                global state = "AmpB"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under FunGenA
        case "AmpB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Input Amplitude", 1)
                lcd.lcd_display_string("> Back", 2)
                lcd.lcd_display_string("  Main", 3)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "AmpI"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "AmpM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGenA"
                global menuFirst = True

        #level 3 under FunGenA
        case "AmpM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Input Amplitude", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("> Main", 3)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "AmpB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 3 under FunGenO
        case "FunOutOn":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                global state = "FunOutOff"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under FunGenO
        case "FunOutOff":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("> Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunOutOn"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FunOutB"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under FunGenO
        case "FunOutB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunOutOff"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "FunOutM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGenO"
                global menuFirst = True

        #level 3 under FunGenO
        case "FunOutM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "FunOutB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 2 under Ohm
        case "OhmB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Reading", 1)
                lcd.lcd_display_string("  Threshold", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                global state = "OhmM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "Ohm"
                global menuFirst = True

        #level 2 under Ohm
        case "OhmM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Reading", 1)
                lcd.lcd_display_string("  Threshold", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "OhmB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 2 under Volt
        case "VoltS":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Reading   Threshold", 1)
                lcd.lcd_display_string("> Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                global state = "VoltB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "SourceEx"
                global menuFirst = True

        #level 2 under Volt
        case "VoltB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Reading   Threshold", 1)
                lcd.lcd_display_string("  Source", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "VoltS"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "VoltM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "Volt"
                global menuFirst = True
            
        #level 2 under Volt
        case "VoltM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Reading   Threshold", 1)
                lcd.lcd_display_string("  Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "VoltB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True
                
        #level 3 under VoltS
        case "SourceEx":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> External", 1)
                lcd.lcd_display_string("  Internal Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option
            elif clockwise == 1:
                global state = "SourceIn"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under VoltS
        case "SourceIn":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  External", 1)
                lcd.lcd_display_string("> Internal Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "SourceEx"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "SourceB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "DCRefVolt"
                global menuFirst = True

        #level 3 under VoltS
        case "SourceB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  External", 1)
                lcd.lcd_display_string("  Internal Reference", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "SourceIn"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "SourceM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "VoltS"
                global menuFirst = True

        #level 3 under VoltS
        case "SourceM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  External", 1)
                lcd.lcd_display_string("  Internal Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "SourceB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 2 under DCRef
        case "DCRefVolt":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> Voltage Value Input", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                global state = "DCRefOut"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 2 under DCRef
        case "DCRefOut":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Voltage Value Input", 1)
                lcd.lcd_display_string("> Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCRefVolt"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "DCRefB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "DCOutOn"
                global menuFirst = True

        #level 2 under DCRef
        case "DCRefB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Voltage Value Input", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCRefOut"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "DCRefM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "DCRef"
                global menuFirst = True

        #level 2 under DCRef
        case "DCRefM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  Voltage Value Input", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCRefB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True

        #level 3 under DCRefOut
        case "DCOutOn":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("> On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False

            #switch to other menu option
            if clockwise == 1:
                global state = "DCOutOff"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under DCRefOut
        case "DCOutOff":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("> Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCOutOn"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "DCOutB"
                global menuFirst = True
            #do action
            elif clicked == True:
                print("Implement later")

        #level 3 under DCRefOut
        case "DCOutB":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCOutOff"
                global menuFirst = True
            #switch to other menu option
            elif clockwise == 1:
                global state = "DCOutM"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "DCRefOut"
                global menuFirst = True

        #level 3 under DCRefOut
        case "DCOutM":
            #updates led when something has changed
            if menuFirst == True:
                lcd.lcd_clear()
                lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                global menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                global state = "DCOutB"
                global menuFirst = True
            #switch to other menu option
            elif clicked == True:
                global state = "FunGen"
                global menuFirst = True



try:

    while True:

        #updates values
        clockwise, fast = rotary.getRotary()
        clicked, longClick = rotary.getButton()

        checkState(state)

#cleanly stops on keyboard interrupt 
except KeyboardInterrupt:
    rotary.cancel()
    lcd.lcd_clear()
