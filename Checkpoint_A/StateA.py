import spidev #https://pypi.org/project/spidev/
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import time
import Dual_Digipot
import DigipotCode
import Rotary
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import Min_difference
#import ADCvoltmeter
import adcCodeTest
#import ohmmeterTest
import VoltageReference
import SquareWave
import DigiSineWave
import measure_sinewave

#set up libraries
pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

#set up devices
rotary = Rotary.Rotary(18,23,24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)
digipot2 = DigipotCode.MCP4131(spi1, 0, 1)
lcd = I2C_LCD_driver.lcd()
voltmeter = adcCodeTest.Voltmeter(pi1)
#ohmmeter = ohmmeterTest.Ohmmeter(pi1)
voltageReference = VoltageReference.VoltageReference(digipot, pi1)
sineWave = DigiSineWave.SineWave(pi1)
measure_sinewave.setup()

#declare vars
state = "FunGen"
waveOutPin = 19
menuFirst = True
square = True
sine = False
clear = True
voltage = 0
resistance = 0
refVoltage = 0
realRef = -1
waveFreqSq = 5050
waveFreqSin = 4500
waveVoltageSq = 5
waveVoltageSin = 5
refStatus = "Off"
waveStatus = "Off"
frequency = 0

#function that checks and updates the state
def checkState(thisState, fast):

    #declare global vars
    global state
    global menuFirst
    global square
    global sine
    global clear
    global voltage
    global resistance
    global refVoltage
    global realRef
    global waveFreqSq
    global waveFreqSin
    global waveVoltageSq
    global waveVoltageSin
    global refStatus
    global waveStatus
    global frequency

    #match case statement that handles the states changing
    match thisState:

        #level 1
        case "FunGen":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter      ", 2)
                lcd.lcd_display_string("  Voltmeter    ", 3)
                lcd.lcd_display_string("  DC Reference     ", 4)
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

        #level 1
        case "Ohm":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("> Ohmmeter    ", 2)
                lcd.lcd_display_string("  Voltmeter    ", 3)
                lcd.lcd_display_string("  DC Reference     ", 4)
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
                state = "OhmB"
                menuFirst = True
                clear = True

        #level 1
        case "Volt":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter    ", 2)
                lcd.lcd_display_string("> Voltmeter    ", 3)
                lcd.lcd_display_string("  DC Reference     ", 4)
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
                lcd.lcd_display_string("  Ohmmeter          ", 2)
                lcd.lcd_display_string("  Voltmeter         ", 3)
                lcd.lcd_display_string("> DC Reference      ", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "Volt"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clockwise == 1:
                state = "FreqMes"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "DCRefVolt"
                menuFirst = True
                clear = True

            #level 1
        case "FreqMes":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Ohmmeter          ", 1)
                lcd.lcd_display_string("  Voltmeter         ", 2)
                lcd.lcd_display_string("  DC Reference      ", 3)
                lcd.lcd_display_string("> Freq. Measurement ", 4)
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
                state = "FreqMesB"
                menuFirst = True
                clear = True
                
        #level 1
        case "Back":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Voltmeter         ", 1)
                lcd.lcd_display_string("  DC Reference      ", 2)
                lcd.lcd_display_string("  Freq. Measurement ", 3)
                lcd.lcd_display_string("> Back    ", 4)
                menuFirst = False
                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FreqMes"
                menuFirst = True
                clear = True
            #switch to other menu option
            elif clockwise == 1:
                state = "Main"
                menuFirst = True 
                clear = True
            #switch to other menu option
            elif clicked == True:
                state = "FreqMes"
                menuFirst = True
                clear = True

        #level 1
        case "Main":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  DC Reference      ", 1)
                lcd.lcd_display_string("  Freq. Measurement ", 2)
                lcd.lcd_display_string("  Back    ", 3)
                lcd.lcd_display_string("> Main    ", 4)
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
        case "TypeSin":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("> Sine  ", 2)
                    lcd.lcd_display_string("  Square  ", 3)
                    lcd.lcd_display_string("  Back  ", 4)
                    #lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                elif sine: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Sine Selected", 1)
                    lcd.lcd_display_string("> Sine  ", 2)
                    lcd.lcd_display_string("  Square  ", 3)
                    lcd.lcd_display_string("  Back  ", 4)
                    #lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("> Sine  ", 1)
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("  Back  ", 3)
                    lcd.lcd_display_string("  Main  ", 4)
                    menuFirst = False
                                
            #switch to other menu option
            if clockwise == 1:
                state = "TypeS"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                square = False
                sine = True
                menuFirst = True
                clear = True

        #level 3 under FunGenT
        case "TypeS":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    if clear:
