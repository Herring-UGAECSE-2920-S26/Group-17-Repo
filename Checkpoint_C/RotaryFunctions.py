import pigpio
import threading
#import asyncio
import time

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
        self.pi1.set_glitch_filter(self.rotaryA, 1000) # 1ms debounce
        
        self.pi1.set_mode(self.rotaryB, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryB, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryB, 1000) # 1ms debounce

        self.pi1.set_mode(self.switchPin, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.switchPin, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.switchPin, 10000) # 10ms debounce

        #set up other vars
        self.tally = 0
        self.readA = None
        self.readB = None
        self.prevA = None
        self.clockwise = None
        self.fast = False
        self.rotating = False
        self.clicked = False
        self.longClick = False

    #check direction and speed of encoder spinning    
    def checkRotary(self):
        last_clk = self.pi1.read(self.rotaryA)
        last_time = time.time()
        
        while True:
            current_clk = self.pi1.read(self.rotaryA)
            
            # If knob turned
            if current_clk != last_clk:
                current_time = time.time()
                
                # Check speed (Fast if < 50ms between clicks)
                self.fast = (current_time - last_time) < 0.05
                last_time = current_time

                # Check direction
                if current_clk != self.pi1.read(self.rotaryB):
                    self.tally += 1  # Clockwise
                else:
                    self.tally -= 1  # Counter-Clockwise
                    
                last_clk = current_clk
            
            # CRITICAL FIX: 1ms sleep prevents CPU lockup but catches fast rotation
            time.sleep(0.001)

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

                    #lets other coroutines run
                    #time.sleep(0.01)

                    #updates values
                    #self.clicked = False
                    #self.longClicked = False

                   #lets other coroutines run
                    time.sleep(0.0001)
                    
            #if button hasn't been pressed
            self.clicked = False
             #lets other coroutines run
            #time.sleep(0.01)

# --- For Testing ---
if __name__ == "__main__":

    #setup
    pi1 = pigpio.pi()
    rot = Rotary(18, 23, 24, pi1)
    
    #async def always(): 
        #create asynchronous tasks
        #rotarySpin = asyncio.create_task(rot.checkRotary())
        #buttonPress = asyncio.create_task(rot.checkButton())

        #perpetually run both tasks together
        #asyncio.gather(rotarySpin, buttonPress)

    #run the tasks in always()
    #asyncio.run(always())

    rotThread = threading.Thread(target=rot.checkRotary)
    buttonThread = threading.Thread(target=rot.checkButton)

    rotThread.start()
    buttonThread.start()


