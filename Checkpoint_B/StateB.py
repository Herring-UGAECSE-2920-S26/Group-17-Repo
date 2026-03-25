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

# --- Function that checks and updates the state ---
# Added clockwise and clicked as arguments
def checkState(thisState, fast, clockwise, clicked):
    global state, menuFirst, square, clear, voltage, resistance
    global refVoltage, realRef, waveFreq, waveVoltage, refStatus, waveStatus

    match thisState:
        # --- Level 1: Main Menu Options ---
        case "FunGen":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("> Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False

            if clockwise == 1: 
                state = "Ohm"
                menuFirst, clear = True, False
            elif clicked:
                state = "FunGenT"
                menuFirst, clear = True, True

        case "Ohm":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("> Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
                
            if clockwise == -1: 
                state = "FunGen"
                menuFirst, clear = True, False
            elif clockwise == 1:
                state = "Volt"
                menuFirst, clear = True, False
            elif clicked:
                state = "OhmB"
                menuFirst, clear = True, True

        case "Volt":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("> Voltmeter", 3)
                lcd.lcd_display_string("  DC Reference", 4)
                menuFirst = False
                
            if clockwise == -1: 
                state = "Ohm"
                menuFirst, clear = True, False
            elif clockwise == 1:
                state = "DCRef"
                menuFirst, clear = True, False
            elif clicked:
                state = "VoltS"
                menuFirst, clear = True, True

        case "DCRef":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Function Generator", 1)
                lcd.lcd_display_string("  Ohmmeter", 2)
                lcd.lcd_display_string("  Voltmeter", 3)
                lcd.lcd_display_string("> DC Reference", 4)
                menuFirst = False
                
            if clockwise == -1: 
                state = "Volt"
                menuFirst, clear = True, False
            elif clockwise == 1:
                state = "Back"
                menuFirst, clear = True, True
            elif clicked:
                state = "DCRefVolt"
                menuFirst, clear = True, True
                
        case "Back":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Ohmmeter", 1)
                lcd.lcd_display_string("  Voltmeter", 2)
                lcd.lcd_display_string("  DC Reference", 3)
                lcd.lcd_display_string("> Back", 4)
                menuFirst = False
                
            if clockwise == -1: 
                state = "DCRef"
                menuFirst, clear = True, True
            elif clockwise == 1:
                state = "Main"
                menuFirst, clear = True, True
            elif clicked:
                state = "DCRef"
                menuFirst, clear = True, True

        case "Main":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("  Voltmeter", 1)
                lcd.lcd_display_string("  DC Reference", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("> Main", 4)
                menuFirst = False
                
            if clockwise == -1: 
                state = "Back"
                menuFirst, clear = True, True
            elif clicked:
                state = "FunGen"
                menuFirst, clear = True, True

        # --- Ohm Measurement Logic ---
        case "OhmB":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Measuring...", 1)
                lcd.lcd_display_string("Threshold", 2)
                lcd.lcd_display_string("> Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False
            
            resistance = ohmmeter.get_resistance()
            lcd.lcd_display_string(f"{resistance:.2f} Ohms    ", 1)
                                                 
            if clockwise == 1:
                state = "OhmM"
                menuFirst, clear = True, False
            elif clicked:
                state = "Ohm"
                menuFirst, clear = True, True

        # --- Voltage Measurement Logic ---
        case "VoltS":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string("Measuring...", 1)
                lcd.lcd_display_string("> Source", 2)
                lcd.lcd_display_string("  Back", 3)
                lcd.lcd_display_string("  Main", 4)
                menuFirst = False

            voltage = voltmeter.get_voltage()
            lcd.lcd_display_string(f"{voltage:.3f} V        ", 1)
                                                 
            if clockwise == 1:
                state = "VoltB"
                menuFirst, clear = True, False
            elif clicked:
                state = "SourceEx"
                menuFirst, clear = True, True

        # --- Function Generator Logic ---
        case "FunOutOn":
            if menuFirst:
                if clear: lcd.lcd_clear()
                lcd.lcd_display_string(f"{waveFreq}Hz {waveStatus}", 1)
                lcd.lcd_display_string("> On", 2)
                lcd.lcd_display_string("  Off", 3)
                lcd.lcd_display_string("  Back", 4)
                menuFirst = False
                                                 
            if clockwise == 1:
                state = "FunOutOff"
                menuFirst, clear = True, False
            elif clicked:
                waveStatus = "On"
                SquareWave.updateFrequency(waveOutPin, waveFreq, pi1)
                SquareWave.updateVoltage(waveVoltage, digipot)
                lcd.lcd_display_string(f"{waveFreq}Hz {waveStatus}   ", 1)

        # ... (Include all other case blocks from your original file here) ...
        # (I have truncated them for brevity, but make sure they use 'clockwise' and 'clicked')

# ------ Main Running Code ------ #
try:
    while True:
        # Capture current inputs
        cw_input, is_fast = rotary.getRotary()
        btn_clicked, is_long = rotary.getButton()

        # Pass variables into the state checker
        checkState(state, is_fast, cw_input, btn_clicked)

        # Sleep to avoid 100% CPU usage
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nCleaning up...")
    rotary.cancel()
    lcd.lcd_clear()
    pi1.stop()
