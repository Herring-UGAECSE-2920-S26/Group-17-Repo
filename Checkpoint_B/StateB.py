import spidev 
import pigpio 
import time
import Dual_Digipot
import Rotary
import I2C_LCD_driver 
import Min_difference
import adcCodeTest
import ohmmeterTest
import VoltageReference
import SquareWave

# --- Hardware Setup ---
pi1 = pigpio.pi()
spi1 = spidev.SpiDev()

# Setup devices
rotary = Rotary.Rotary(18, 23, 24, pi1)
digipot = Dual_Digipot.MCP4131(spi1)
lcd = I2C_LCD_driver.lcd()
voltmeter = adcCodeTest.Voltmeter(pi1)
ohmmeter = ohmmeterTest.Ohmmeter(pi1)
voltageReference = VoltageReference.VoltageReference(digipot, pi1)

# --- State Variables ---
state = "FunGen"
waveOutPin = 19
menuFirst = True
square = False
clear = True
voltage = 0
resistance = 0
refVoltage = 0
realRef = -1
waveFreq = 5050
waveVoltage = 5
refStatus = "Off"
waveStatus = "Off"

def checkState(thisState, fast, clockwise, clicked):
    global state, menuFirst, square, clear, voltage, resistance
    global refVoltage, realRef, waveFreq, waveVoltage, refStatus, waveStatus

    match thisState:
        # --- Level 1: Main Menu ---
        case "FunGen":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
            if clockwise == 1: state = "Ohm"; menuFirst, clear = True, False
            elif clicked: state = "FunGenT"; menuFirst, clear = True, True

        case "Ohm":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("> Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
            if clockwise == -1: state = "FunGen"; menuFirst, clear = True, False
            elif clockwise == 1: state = "Volt"; menuFirst, clear = True, False
            elif clicked: state = "OhmB"; menuFirst, clear = True, True

        case "Volt":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("> Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
            if clockwise == -1: state = "Ohm"; menuFirst, clear = True, False
            elif clockwise == 1: state = "DCRef"; menuFirst, clear = True, False
            elif clicked: state = "VoltS"; menuFirst, clear = True, True

        case "DCRef":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("> DC Reference", 4)
                menuFirst = False
            if clockwise == -1: state = "Volt"; menuFirst, clear = True, False
            elif clicked: state = "DCRefVolt"; menuFirst, clear = True, True

        # --- Level 2: Function Generator Settings ---
        case "FunGenT":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Frequency", 1)
                lcd.lcd_display_string("  Amplitude", 2)
                lcd.lcd_display_string("  Output", 3)
                lcd.lcd_display_string("  Back", 4)
                menuFirst = False
            if clockwise == 1: state = "FunGenA"; menuFirst, clear = True, False
            elif clicked: state = "FreqIn"; menuFirst, clear = True, True

        case "FunGenA":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Frequency", 1)
                lcd.lcd_display_string("> Amplitude", 2)
                lcd.lcd_display_string("  Output", 3)
                lcd.lcd_display_string("  Back", 4)
                menuFirst = False
            if clockwise == -1: state = "FunGenT"; menuFirst, clear = True, False
            elif clockwise == 1: state = "FunGenO"; menuFirst, clear = True, False
            elif clicked: state = "AmpIn"; menuFirst, clear = True, True

        case "FunGenO":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Frequency", 1)
                lcd.lcd_display_string("  Amplitude", 2)
                lcd.lcd_display_string("> Output", 3)
                lcd.lcd_display_string("  Back", 4)
                menuFirst = False
            if clockwise == -1: state = "FunGenA"; menuFirst, clear = True, False
            elif clicked: state = "FunOutOn"; menuFirst, clear = True, True

        # --- Level 3: Changing Values ---
        case "FreqIn":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Set Freq:", 1)
                menuFirst = False
            if clockwise != 0:
                waveFreq = SquareWave.changeFrequency(waveFreq, clockwise, fast)
            lcd.lcd_display_string(f"{waveFreq} Hz      ", 2)
            if clicked: state = "FunGenT"; menuFirst, clear = True, True

        case "AmpIn":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Set Amplitude:", 1)
                menuFirst = False
            if clockwise != 0:
                waveVoltage = SquareWave.changeVoltage(waveVoltage, clockwise, fast)
            lcd.lcd_display_string(f"+/- {waveVoltage} Vp    ", 2)
            if clicked: state = "FunGenA"; menuFirst, clear = True, True

        # --- Sub-level Logic: Ohm Measurement ---
        case "OhmB":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Measuring Ohm...", 2)
                lcd.lcd_display_string("> Back", 3)
                menuFirst = False
            resistance = ohmmeter.get_resistance()
            lcd.lcd_display_string(f"{resistance:.2f} Ohms    ", 1)
            if clicked: state = "Ohm"; menuFirst, clear = True, True

        # --- Sub-level Logic: Volt Measurement ---
        case "VoltS":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Measuring Volt...", 2)
                lcd.lcd_display_string("> Source Select", 3)
                lcd.lcd_display_string("  Back", 4)
                menuFirst = False
            voltage = voltmeter.get_voltage()
            lcd.lcd_display_string(f"{voltage:.3f} V        ", 1)
            if clicked: state = "SourceEx"; menuFirst, clear = True, True

        case "SourceEx":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> External Pin", 1)
                lcd.lcd_display_string("  Internal Ref", 2)
                menuFirst = False
            if clockwise == 1: state = "SourceIn"; menuFirst, clear = True, False
            elif clicked: 
                voltmeter.set_internal(0)
                state = "VoltS"; menuFirst, clear = True, True

        case "SourceIn":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  External Pin", 1)
                lcd.lcd_display_string("> Internal Ref", 2)
                menuFirst = False
            if clockwise == -1: state = "SourceEx"; menuFirst, clear = True, False
            elif clicked:
                voltmeter.set_internal(1)
                state = "VoltS"; menuFirst, clear = True, True

        # --- Sub-level Logic: DC Reference ---
        case "DCRefVolt":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Set DC Ref:", 1)
                menuFirst = False
            if clockwise != 0:
                refVoltage = voltageReference.setVoltage(clockwise)
            lcd
