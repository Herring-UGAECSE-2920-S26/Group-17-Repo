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
                lcd.lcd_display_string("  Ohmmeter", 2)
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
                lcd.lcd_display_string("  Ohmmeter    ", 2)
                lcd.lcd_display_string("  Voltmeter    ", 3)
                lcd.lcd_display_string("> DC Reference     ", 4)
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
                lcd.lcd_display_string("  Ohmmeter    ", 1)
                lcd.lcd_display_string("  Voltmeter    ", 2)
                lcd.lcd_display_string("  DC Reference     ", 3)
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
                lcd.lcd_display_string("  Voltmeter    ", 1)
                lcd.lcd_display_string("  DC Reference     ", 2)
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
                lcd.lcd_display_string("  DC Reference     ", 1)
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
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("  Sine  ", 2)
                    lcd.lcd_display_string("> Square  ", 3)
                    lcd.lcd_display_string("  Back  ", 4)
                    #lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                elif sine: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Sine Selected", 1)
                    lcd.lcd_display_string("  Sine  ", 2)
                    lcd.lcd_display_string("> Square  ", 3)
                    lcd.lcd_display_string("  Back  ", 4)
                    #lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("  Sine  ", 1)
                    lcd.lcd_display_string("> Square  ", 2)
                    lcd.lcd_display_string("  Back  ", 3)
                    lcd.lcd_display_string("  Main  ", 4)
                    menuFirst = False

             #switch to other menu option 
            if clockwise == -1: 
                state = "TypeSin"
                menuFirst = True
                clear = False
            #switch to other menu option
            if clockwise == 1:
                state = "TypeB"
                menuFirst = True
                clear = False
            #do action
            elif clicked == True:
                square = True
                sine = False
                menuFirst = True
                clear = True

        #level 3 under FunGenT
        case "TypeB":
            #updates led when something has changed
            if menuFirst == True:
                if square: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Square Selected", 1)
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("> Back  ", 3)
                    lcd.lcd_display_string("  Main  ", 4)
                    menuFirst = False
                elif sine: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Sine Selected", 1)
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("> Back  ", 3)
                    lcd.lcd_display_string("  Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("  Sine  ", 1)
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("> Back  ", 3)
                    lcd.lcd_display_string("  Main  ", 4)
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
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("  Back  ", 3)
                    lcd.lcd_display_string("> Main  ", 4)
                    menuFirst = False
                elif sine: 
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("Sine Selected", 1)
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("  Back  ", 3)
                    lcd.lcd_display_string("> Main", 4)
                    menuFirst = False
                else:
                    if clear: lcd.lcd_clear()
                    lcd.lcd_display_string("  Sine  ", 1)
                    lcd.lcd_display_string("  Square  ", 2)
                    lcd.lcd_display_string("  Back  ", 3)
                    lcd.lcd_display_string("> Main  ", 4)
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
            #go change wave frequency
            elif clicked == True:
                state = "FreqIn"
                menuFirst = True
                clear = False

        #changes wave frequency
        case "FreqIn":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                if square: 
                    lcd.lcd_display_string(f"> {waveFreqSq} Hz        ", 1)
                else: 
                    lcd.lcd_display_string(f"> {waveFreqSin} Hz        ", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False

            if square: 
                currentFreq = waveFreqSq #checks current frequency
                #changes frequency
                if clockwise != 0:
                    waveFreqSq = SquareWave.changeFrequency(waveFreqSq, clockwise, fast, sine)
                #updates lcd if necessary
                if currentFreq != waveFreqSq:
                    lcd.lcd_display_string(f"> {waveFreqSq} Hz        ", 1)
            else: 
                currentFreq = waveFreqSin #checks current frequency
                #changes frequency
                if clockwise != 0:
                    waveFreqSin = SquareWave.changeFrequency(waveFreqSin, clockwise, fast, sine)
                #updates lcd if necessary
                if currentFreq != waveFreqSin:
                    lcd.lcd_display_string(f"> {waveFreqSin} Hz        ", 1)

            #goes back to normal frequency menu if clicked
            if clicked == True:
                state = "FreqI"
                menuFirst = True
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
            #go change wave amplitude
            elif clicked == True:
                state = "AmpIn"
                menuFirst = True
                clear = False

        #changes wave amplitude
        case "AmpIn":
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                if square: 
                    lcd.lcd_display_string(f"> +/-{waveVoltageSq} Vp          ", 1)
                else: 
                    lcd.lcd_display_string(f"> +/-{waveVoltageSin} Vp          ", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False

            if square: 
                #checks current amplitude
                currentWaveVoltage = waveVoltageSq 
                #changes amplitude
                if clockwise != 0:
                    waveVoltageSq = SquareWave.changeVoltage(waveVoltageSq, clockwise, fast, sine)
                #updates lcd if necessary
                if currentWaveVoltage != waveVoltageSq:
                    lcd.lcd_display_string(f"> +/-{waveVoltageSq} Vp       ", 1)
            else: 
                #checks current amplitude
                currentWaveVoltage = waveVoltageSin 
                #changes amplitude
                if clockwise != 0:
                    waveVoltageSin = SquareWave.changeVoltage(waveVoltageSin, clockwise, fast, sine)
                #updates lcd if necessary
                if currentWaveVoltage != waveVoltageSin:
                    lcd.lcd_display_string(f"> +/-{waveVoltageSin} Vp       ", 1)

            #goes back to normal amplitude menu if clicked
            if clicked == True:
                state = "AmpI"
                menuFirst = True
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
                if square: 
                    lcd.lcd_display_string(f"{waveFreqSq}Hz +/-{waveVoltageSq}Vp {waveStatus} ", 1)
                else: 
                    lcd.lcd_display_string(f"{waveFreqSin}Hz +/-{waveVoltageSin}Vp {waveStatus} ", 1)
                lcd.lcd_display_string("> On   ", 2)
                lcd.lcd_display_string("  Off   ", 3)
                lcd.lcd_display_string("  Back   ", 4)
                #lcd.lcd_display_string("  Main", 4)
                menuFirst = False
                                                
            #switch to other menu option
            if clockwise == 1:
                state = "FunOutOff"
                menuFirst = True
                clear = False
            #turn on wave generator
            elif clicked == True:
                waveStatus = "On"
                if square:
                    SquareWave.updateFrequency(waveOutPin, waveFreqSq, pi1)
                    SquareWave.updateVoltage(waveVoltageSq, digipot)
                    lcd.lcd_display_string(f"{waveFreqSq}Hz +/-{waveVoltageSq}Vp {waveStatus} ", 1)
                if sine: 
                    sineWave.set_amplitude(waveVoltageSin, digipot2)
                    sineWave.start_wave(waveFreqSin)
                    lcd.lcd_display_string(f"{waveFreqSin}Hz +/-{waveVoltageSin}Vp {waveStatus} ", 1)
                clear = False

        #level 3 under FunGenO
        case "FunOutOff":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                if square: 
                    lcd.lcd_display_string(f"{waveFreqSq}Hz +/-{waveVoltageSq}Vp {waveStatus} ", 1)
                else: 
                    lcd.lcd_display_string(f"{waveFreqSin}Hz +/-{waveVoltageSin}Vp {waveStatus} ", 1)
                lcd.lcd_display_string("  On   ", 2)
                lcd.lcd_display_string("> Off   ", 3)
                lcd.lcd_display_string("  Back   ", 4)
                #lcd.lcd_display_string("  Main", 4)
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
            #turn off wave generator
            elif clicked == True:
                waveStatus = "Off"
                if square: SquareWave.waveOff(waveOutPin, pi1)
                if sine: sineWave.stop()
                voltageReference.setDigiPot(0)
                if square: 
                    lcd.lcd_display_string(f"{waveFreqSq}Hz +/-{waveVoltageSq}Vp {waveStatus} ", 1)
                else: 
                    lcd.lcd_display_string(f"{waveFreqSin}Hz +/-{waveVoltageSin}Vp {waveStatus} ", 1)
                clear = False

        #level 3 under FunGenO
        case "FunOutB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                if square: 
                    lcd.lcd_display_string(f"{waveFreqSq}Hz +/-{waveVoltageSq}Vp {waveStatus} ", 1)
                else: 
                    lcd.lcd_display_string(f"{waveFreqSin}Hz +/-{waveVoltageSin}Vp {waveStatus} ", 1)
                #lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off   ", 2)
                lcd.lcd_display_string("> Back   ", 3)
                lcd.lcd_display_string("  Main   ", 4)
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
                #turn off wave generator
                waveStatus = "Off"
                if square: SquareWave.waveOff(waveOutPin, pi1)
                if sine: sineWave.stop()
                voltageReference.setDigiPot(0)
                #change state
                state = "FunGenO"
                menuFirst = True
                clear = True

        #level 3 under FunGenO
        case "FunOutM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                if square: 
                    lcd.lcd_display_string(f"{waveFreqSq}Hz +/-{waveVoltageSq}Vp {waveStatus} ", 1)
                else: 
                    lcd.lcd_display_string(f"{waveFreqSin}Hz +/-{waveVoltageSin}Vp {waveStatus} ", 1)
                #lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("  Off   ", 2)
                lcd.lcd_display_string("  Back   ", 3)
                lcd.lcd_display_string("> Main   ", 4)
                menuFirst = False
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "FunOutB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                #turn off wave generator
                waveStatus = "Off"
                if square: SquareWave.waveOff(waveOutPin, pi1)
                if sine: sineWave.stop()
                voltageReference.setDigiPot(0)
                #change state
                state = "FunGen"
                menuFirst = True
                clear = True

        #level 2 under Ohm
        case "OhmB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                if resistance > abs(500000):
                    lcd.lcd_display_string(f"Infinite Ohms    ", 1)
                else: 
                    lcd.lcd_display_string(f"{resistance: .4f} Ohms    ", 1)
                lcd.lcd_display_string("+/-160 Ohms", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
            
            #update resistance measurement
            resistance = voltmeter.get_resistance()
            if resistance > 500000:
                lcd.lcd_display_string(f"Infinite Ohms    ", 1)
            else: 
                lcd.lcd_display_string(f"{resistance: .4f} Ohms    ", 1)
            #time.sleep(10) #sleepy
                                                
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
                if resistance > abs(500000):
                    lcd.lcd_display_string(f"Infinite Ohms    ", 1)
                else: 
                    lcd.lcd_display_string(f"{resistance: .4f} Ohms    ", 1)
                lcd.lcd_display_string("+/- 160 Ohms", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
            
            #update resistance measurement
            resistance = voltmeter.get_resistance()
            if resistance > 500000:
                lcd.lcd_display_string(f"Infinite Ohms    ", 1)
            else: 
                lcd.lcd_display_string(f"{resistance: .4f} Ohms    ", 1)
                                                
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
                lcd.lcd_display_string(f"{voltage: .4f} V +/- 0.15 V", 1)
                lcd.lcd_display_string("> Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            #update voltage measurement
            voltage = voltmeter.get_voltage()
            lcd.lcd_display_string(f"{voltage: .4f} V +/- 0.15 V", 1)
            #time.sleep(.10) #sleepy
                                                
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
                lcd.lcd_display_string(f"{voltage: .4f} V +/- 0.15 V", 1)
                lcd.lcd_display_string("  Source", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            #update voltage measurement
            voltage = voltmeter.get_voltage()
            lcd.lcd_display_string(f"{voltage: .4f} V +/- 0.15 V", 1)
                                                
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
                lcd.lcd_display_string(f"{voltage: .4f} V +/- 0.15 V", 1)
                lcd.lcd_display_string("  Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False

            #update voltage measurement
            voltage = voltmeter.get_voltage()
            lcd.lcd_display_string(f"{voltage: .4f} V +/- 0.15 V", 1)
            
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
                state = "VoltS"
                menuFirst = True
                clear = True
                #voltmeter.set_internal(0)

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
            #go input reference voltage
            elif clicked == True:
                state = "DCRefIn"
                menuFirst = True
                clear = False

        #input reference voltage
        case "DCRefIn":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string(f"> {refVoltage} V               ", 1)
                lcd.lcd_display_string("  Output", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            currentVoltage = refVoltage #checks current voltage
            #changes voltage
            if clockwise != 0:
                refVoltage = voltageReference.setVoltage(clockwise)
            #updates lcd if necessary
            if currentVoltage != refVoltage:
                lcd.lcd_display_string(f"> {refVoltage} V      ", 1)

            #goes back to normal voltage reference menu if clicked
            if clicked == True:
                state = "DCRefVolt"
                menuFirst = True
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
                if realRef == -1: realRef = refVoltage
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string("+/- 0.15 V  ", 2)
                lcd.lcd_display_string("> On    ", 3)
                lcd.lcd_display_string("  Off    ", 4)
                #lcd.lcd_display_string("  Back    ", 4)
                #lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            #update voltage
            if refStatus == "On": 
                realRef = voltmeter.get_voltage()
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
            
            #switch to other menu option
            if clockwise == 1:
                state = "DCOutOff"
                menuFirst = True
                clear = False
            #turn voltage reference on
            elif clicked == True:
                refStatus = "On"
                voltageReference.setDigiPot(refVoltage)
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                #voltmeter.set_internal(1)
                realRef = voltmeter.get_voltage()
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                clear = False

        #level 3 under DCRefOut
        case "DCOutOff":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string("+/- 0.15 V  ", 2)
                #lcd.lcd_display_string("  On    ", 2)
                lcd.lcd_display_string("> Off    ", 3)
                lcd.lcd_display_string("  Back    ", 4)
                #lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            #update voltage
            if refStatus == "On": 
                realRef = voltmeter.get_voltage()
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                                                
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
            #turn reference voltage off
            elif clicked == True:
                refStatus = "Off"
                voltageReference.setDigiPot(0)
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                realRef = voltmeter.get_voltage()
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                clear = False

        #level 3 under DCRefOut
        case "DCOutB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                #lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                #lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("+/- 0.15 V  ", 2)
                #lcd.lcd_display_string("  Off    ", 2)
                lcd.lcd_display_string("> Back    ", 3)
                lcd.lcd_display_string("  Main    ", 4)
                menuFirst = False

            #update voltage
            if refStatus == "On": 
                realRef = voltmeter.get_voltage()
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                                                
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
                #turn off reference voltage
                refStatus = "Off"
                voltageReference.setDigiPot(0) 
                #voltmeter.set_internal(0)
                #change state
                state = "DCRefOut"
                menuFirst = True
                clear = True

        #level 3 under DCRefOut
        case "DCOutM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                #lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                #lcd.lcd_display_string("  On", 1)
                lcd.lcd_display_string("+/- 0.15 V  ", 2)
                #lcd.lcd_display_string("  Off    ", 2)
                lcd.lcd_display_string("  Back    ", 3)
                lcd.lcd_display_string("> Main    ", 4)
                menuFirst = False

            #update voltage
            if refStatus == "On": 
                realRef = voltmeter.get_voltage()
                #lcd.lcd_display_string(f"Output: {refVoltage: .3f} V {refStatus} ", 1)
                lcd.lcd_display_string(f"Output: {realRef: .3f} V {refStatus} ", 1)
                                                
            #switch to other menu option 
            if clockwise == -1: 
                state = "DCOutB"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                #turn off reference voltage
                refStatus = "Off"
                voltageReference.setDigiPot(0) 
                #voltmeter.set_internal(0)
                #change state
                state = "FunGen"
                menuFirst = True
                clear = True
            
        #level 2 under FreqMes
        case "FreqMesB":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string(f"{frequency: .3f}Hz +50Hz  ", 1)
                lcd.lcd_display_string("> Back", 2)
                lcd.lcd_display_string("  Main", 3)
                menuFirst = False
                                                
            #frequency = 0
            frequency = measure_sinewave.takeSineMeasurement()
            lcd.lcd_display_string(f"{frequency: .3f}Hz +50Hz  ", 1)
            
            #switch to other menu option
            if clockwise == 1:
                state = "FreqMesM"
                menuFirst = True
                clear = False
            #switch to other menu option
            elif clicked == True:
                state = "FreqMes"
                menuFirst = True
                clear = True
            
        #level 2 under FreqMes
        case "FreqMesM":
            #updates led when something has changed
            if menuFirst == True:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string(f"{frequency: .3f}Hz +50Hz  ", 1)
                lcd.lcd_display_string("  Back", 2)
                lcd.lcd_display_string("> Main", 3)
                menuFirst = False

            #frequency = 0
            frequency = measure_sinewave.takeSineMeasurement()
            lcd.lcd_display_string(f"{frequency: .3f}Hz +50Hz  ", 1)
            
            #switch to other menu option 
            if clockwise == -1: 
                state = "FreqMesB"
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
        checkState(state, fast)

        #saves cpu
        time.sleep(0.05)

#cleanly stops on keyboard interrupt 
except KeyboardInterrupt:
    rotary.cancel()
    lcd.lcd_clear()
