import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import threading
import time

#class that sets up the rotary encoder component and checks status of 
#rotary encoder and button
class Rotary:

    #min and max resistor values
    minR = 100
    maxR = 10000

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
        self.readA = None
        self.readB = None
        self.prevA = None
        self.clockwise = None
        self.fast = False
        self.rotating = False
        self.clicked = False
        self.longClick = False
        self.tally = 0

    #check direction and speed of encoder spinning    
   #check direction and speed of encoder spinning    
    def checkRotary(self):
        self.prevA = self.pi1.read(self.rotaryA)
        last_time = time.perf_counter()
        
        while True:
            self.readA = self.pi1.read(self.rotaryA)
            self.readB = self.pi1.read(self.rotaryB)

            # If the knob has moved (State Change)
            if self.readA != self.prevA:
                self.rotating = True
                current_time = time.perf_counter()
                
                # 1. Check Speed
                # If less than 0.05s (50ms) has passed, it is FAST
                if (current_time - last_time) < 0.05:
                    self.fast = True
                else:
                    self.fast = False
                
                last_time = current_time # Reset timer
                
                # 2. Check Direction
                # If Pin A != Pin B, it is Clockwise. Otherwise Counter-Clockwise.
                if self.readA != self.readB:
                    self.clockwise = True
                    self.tally += 1   # Increment for Main Loop
                else:
                    self.clockwise = False
                    self.tally -= 1   # Decrement for Main Loop

            else:
                self.rotating = False

            # Update previous state
            self.prevA = self.readA

            # Sleep 1ms (0.001) - Fast enough to catch spins, slow enough for CPU
            time.sleep(0.001)

    #checks if button is pressed and for how long
    def checkButton(self):

        while True:

            #if button has been pressed
            if self.pi1.wait_for_edge(self.switchPin, 1):
                self.clicked = True
                startTime = time.perf_counter()
                #print("Press")
                #print("Start Time Button:", startTime)

                #if button is no longer pressed
                if self.pi1.wait_for_edge(self.switchPin, pigpio.EITHER_EDGE):
                    endTime = time.perf_counter()
                    #print("Stop Press")
                    #print("End Time Button:", endTime)

                    #checks duration
                    if abs(startTime - endTime) >= 3:
                        self.longClicked = True
                        #print("Long")
                    else:
                        self.longClicked = False
                        #print("Short")

                   #lets other threads run
                    time.sleep(0.0001)
                    
            #if button hasn't been pressed
            self.clicked = False

# --- For Testing ---
if __name__ == "__main__":

    #setup
    pi1 = pigpio.pi()
    rot = Rotary(18, 23, 24, pi1)

    #threading
    rotThread = threading.Thread(target=rot.checkRotary)
    buttonThread = threading.Thread(target=rot.checkButton)

    rotThread.start()
    buttonThread.start()

