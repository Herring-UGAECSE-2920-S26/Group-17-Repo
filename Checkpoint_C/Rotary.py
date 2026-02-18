import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import time

#class that sets up the rotary encoder component and checks status of 
#rotary encoder and button
class Rotary:

    #initialize Rotary object
    def __init__(self, rotaryA, rotaryB, switchPin, pi1):
        self.rotaryA = rotaryA
        self.rotaryB = rotaryB
        self.switchPin = switchPin
        self.pi1 = pi1

        #set up rotary encoder
        self.pi1.set_mode(self.rotaryA, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryA, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryA, 1000) # 3ms debounce
        
        self.pi1.set_mode(self.rotaryB, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryB, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryB, 1000) # 3ms debounce

        self.pi1.set_mode(self.switchPin, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.switchPin, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.switchPin, 20000) # 20ms debounce

        #set up other vars
        self.clockwise = None
        self.fast = False
        self.clicked = False
        self.longClick = False
        self.lastTick = 0

        #create callbacks
        self.rotaryCallback = self.pi1.callback(self.rotaryA, pigpio.EITHER_EDGE, self.rotaryFunction)
        self.buttonCallback = self.pi1.callback(self.switchPin, pigpio.EITHER_EDGE, self.buttonFunction)
        

    def rotaryFunction(self, gpio, level, tick):

        if level == 1:
            print("Rotation Detected")
            
            self.fast = (50000 > pigpio.tickDiff(self.lastTick, tick))
            self.lastTick = tick

            if self.pi1.read(self.rotaryB) == 0:
                self.clockwise = 1 #clockwise
            else:
                self.clockwise = -1 #counterclockwise

                
    def buttonFunction(self, gpio, level, tick):

        if level == 0:
            print("Click Detected")
            self.clicked = True
            looped = True
            startTime = tick

            looped = self.pi1.read(self.switchPin)
        
            while looped != 1:
                endTime = self.pi1.get_current_tick()
                if (pigpio.tickDiff(startTime, endTime) > 3000000):
                    self.longClick = True
                    looped = 1
                else: looped = self.pi1.read(self.switchPin)
                
                

    def getRotary(self):
        
        readClockwise = self.clockwise
        readFast = self.fast

        self.clockwise = 0

        return readClockwise, readFast


    def getButton(self):

        readClicked = self.clicked
        readLongClick = self.longClick

        self.clicked = False
        self.longClick = False

        return readClicked, readLongClick


    def cancel(self):
        self.rotaryCallback.cancel()
        self.buttonCallback.cancel()

# --- For Testing ---
if __name__ == "__main__":

    #setup
    pi1 = pigpio.pi()
    rotary = Rotary(18, 23, 24, pi1)

    clockwise, fast = rotary.getRotary()
    clicked, longClick = rotary.getButton()

    print("Main Clockwise:", clockwise)
    print("Main Fast:", fast)
    print("Main Clicked:", clicked)
    print("Main LongClick:", longClick)

    prevClockwise = clockwise
    prevFast = fast 
    prevClicked = clicked
    prevLongClick = longClick
    
    while True:
        clockwise, fast = rotary.getRotary()
        clicked, longClick = rotary.getButton()
        
        if prevClockwise != clockwise: print("Main Clockwise:", clockwise)
        if prevFast != fast: print("Main Fast:", fast)
        if prevClicked != clicked: print("Main Clicked:", clicked)
        if prevLongClick != longClick: print("Main LongClick:", longClick)

        prevClockwise = clockwise
        prevFast = fast 
        prevClicked = clicked
        prevLongClick = longClick
        
        
            
            
