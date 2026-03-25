import spidev 
import pigpio 
import I2C_LCD_driver 
import Dual_Digipot
import Rotary
import Min_difference

def updateFrequency(gpio, freq, pi):
    """Updates the hardware PWM frequency."""
    pi.hardware_PWM(gpio, freq, 500000) # 50% duty cycle

def waveOff(gpio, pi):
    """Turns off the PWM signal."""
    pi.hardware_PWM(gpio, 0, 0)

def updateVoltage(voltage, digipot):
    """Updates the DigiPot step to change wave amplitude."""
    step = Min_difference.min_difference_volts(voltage)
    digipot.set_step(step, 1)

def changeFrequency(freq, clockwise, fast):
    """Calculates new frequency based on rotary input."""
    maxFreq, minFreq = 10000, 100
    stepSize = 100 if fast else 10 
    new_freq = freq + (clockwise * stepSize)
    return max(minFreq, min(maxFreq, new_freq))

def changeVoltage(voltage, clockwise, fast):
    """Calculates new voltage based on rotary input."""
    maxV, minV = 10, 0
    stepSize = 1
    new_v = voltage + (clockwise * stepSize)
    return max(minV, min(maxV, new_v))
