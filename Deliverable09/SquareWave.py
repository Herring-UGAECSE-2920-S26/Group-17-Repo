import spidev #https://pypi.org/project/spidev/
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import I2C_LCD_driver #https://gist.github.com/DenisFromHR/cc863375a6e19dce359d
import Dual_Digipot
import Rotary

#function that updates the frequency of the square wave
def updateFrequency(gpio, freq, pi):
    pi.hardware_PWM(gpio, freq, 500000)

#function that turns off the square wave
def waveOff(gpio, pi):
    pi.hardware_PWM(gpio, 0, 0)

#function that updates the amplitude of the square wave
def updateAmplitude(amplitude, digipot):
    print("Not Implemented") 

# --- For Testing ---
if __name__ == "__main__":
    
    #setup
    pi1 = pigpio.pi()
    spi1 = spidev.SpiDev()
    rotary = Rotary(18, 23, 24, pi1)
    digipot = Dual_Digipot.MCP4131(spi1)
    lcd = I2C_LCD_driver.lcd()
    waveOutPin = 19
    count = 0

    while True:
        #update values
        clockwise, fast = rotary.getRotary()
        clicked, longClick = rotary.getButton() 

        #initial message
        lcd.lcd_clear()
        lcd.lcd_display_string("Click Please UWU", 1)

        if clicked:
            count = count + 1
            if count > 12:
                count = 1

            if count == 1: #+5V 100Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: +5V", 1)
                lcd.lcd_display_string("Frequency: 100Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 100, pi1)
                updateAmplitude(5, digipot)
              
            elif count == 2: #+5V 5000Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: +5V", 1)
                lcd.lcd_display_string("Frequency: 5000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 5000, pi1)
                updateAmplitude(5, digipot)
              
            elif count == 3: #+5V 10Khz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: +5V", 1)
                lcd.lcd_display_string("Frequency: 10000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 10000, pi1)
                updateAmplitude(5, digipot)
              
            elif count == 4: #-5V 100Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: -5V", 1)
                lcd.lcd_display_string("Frequency: 100Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 100, pi1)
                updateAmplitude(-5, digipot)
              
            elif count == 5: #-5V 5000Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: -5V", 1)
                lcd.lcd_display_string("Frequency: 5000Hz", 2) 

                #update wave values
                updateFrequency(waveOutpin, 5000, pi1)
                updateAmplitude(-5, digipot)
                
            elif count == 6: #-5V 10kHz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: -5V", 1)
                lcd.lcd_display_string("Frequency: 10000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 10000, pi1)
                updateAmplitude(-5, digipot)
                
            elif count == 7: #+10V 100Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: +10V", 1)
                lcd.lcd_display_string("Frequency: 100Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 100, pi1)
                updateAmplitude(10, digipot)
                
            elif count == 8: #+10V 5000Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: +10V", 1)
                lcd.lcd_display_string("Frequency: 5000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 5000, pi1)
                updateAmplitude(10, digipot)
                
            elif count == 9: #+10V 10kHz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: +10V", 1)
                lcd.lcd_display_string("Frequency: 1000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 10000, pi1)
                updateAmplitude(10, digipot)
                
            elif count == 10: #-10V 100Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: -10V", 1)
                lcd.lcd_display_string("Frequency: 100Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 100, pi1)
                updateAmplitude(-10, digipot)
                
            elif count == 11: #-10V 5000Hz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: -10V", 1)
                lcd.lcd_display_string("Frequency: 5000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 5000, pi1)
                updateAmplitude(-10, digipot)
                
            elif count == 12: #-10V 10kHz
                #update lcd
                lcd.lcd_clear()
                lcd.lcd_display_string("Amplitude: -10V", 1)
                lcd.lcd_display_string("Frequency: 10000Hz", 2)

                #update wave values
                updateFrequency(waveOutpin, 10000, pi1)
                updateAmplitude(-10, digipot)



