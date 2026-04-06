import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import math
import time

#class that allows the user to generate a sine wave
class SineWave:

    #initialize SineWave object
    def __init__(self, pi):
        #set vars
        self.pin0 = 26
        self.pin1 = 25
        self.pin2 = 21
        self.pin3 = 20
        self.pin4 = 16
        #self.pin0 = 16
        #self.pin1 = 20
        #self.pin2 = 21
        #self.pin3 = 25
        #self.pin4 = 26
        self.pi = pi

        #set up voltage pins
        self.pi.set_mode(self.pin0, pigpio.OUTPUT)
        self.pi.set_mode(self.pin1, pigpio.OUTPUT)
        self.pi.set_mode(self.pin2, pigpio.OUTPUT)
        self.pi.set_mode(self.pin3, pigpio.OUTPUT)
        self.pi.set_mode(self.pin4, pigpio.OUTPUT)

    #finds current point on sine wave given current time, frequency, and peak voltage
    def getSinePoint(self, time, freq, max):
      point = (max/2) + (max/2) * math.sin(2 * math.pi * freq * time)
      return point 

    #finds the binary number that corresponds with the given sine point
    def getBinary(self, sinePoint): 
        #set vars
        count = 0
        add = 0.3125
        prev = 0.3125 
        #handles zero
        if sinePoint <= add: return format(count, '05b')
        count = 1

        #returns the correct binary number as a string
        while count <= 31:
            if prev < sinePoint <= (prev + add): return format(count, '05b')
            prev = prev + add
            count += 1

    #writes to gpio pins to generate correct voltage
    def setSineVoltage(self, binaryString):
        #converts binary string to list
        binaryList = list(binaryString)

        #turns correct gpio pins on or off for each binary digit
        if binaryList[0] == '1': self.pi.write(self.pin0, 1)
        else: self.pi.write(self.pin0, 0)
          
        if binaryList[1] == '1': self.pi.write(self.pin1, 1)
        else: self.pi.write(self.pin1, 0)
          
        if binaryList[2] == '1': self.pi.write(self.pin2, 1)
        else: self.pi.write(self.pin2, 0)
          
        if binaryList[3] == '1': self.pi.write(self.pin3, 1)
        else: self.pi.write(self.pin3, 0)
          
        if binaryList[4] == '1': self.pi.write(self.pin4, 1)
        else: self.pi.write(self.pin4, 0)

    #completes the entire process of getting and setting correct sine voltages
    def runner(self, time, freq, max): 
        sinePoint = self.getSinePoint(time, freq, max)
        binaryString = self.getBinary(sinePoint)
        self.setSineVoltage(binaryString) 

# --- For Testing ---
if __name__ == "__main__":
    #setup
    pi1 = pigpio.pi()
    sineWave = SineWave(pi1)

    try: 
        #generates 500Hz 10V sine wave
        while True:
            currentTime = time.time()
            sineWave.runner(currentTime, 1000, 10)

    except KeyboardInterrupt:
        print("\nProgram interrupted.")
