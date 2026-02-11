import pigpio
import threading
#import asyncio
import time

class Rotary:
    minR = 100
    maxR = 10000

    def __init__(self, rotaryA, rotaryB, switchPin, pi1):
        self.rotaryA = rotaryA
        self.rotaryB = rotaryB
        self.switchPin = switchPin
        self.pi1 = pi1

        # Setup pins
        self.pi1.set_mode(self.rotaryA, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryA, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryA, 1000) 
        
        self.pi1.set_mode(self.rotaryB, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryB, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.rotaryB, 1000) 

        self.pi1.set_mode(self.switchPin, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.switchPin, pigpio.PUD_UP)
        self.pi1.set_glitch_filter(self.switchPin, 10000) 

        # NEW: Counter system
        self.tally = 0
        self.clicked = False
        self.longClicked = False
        self.fast = False 

    def checkRotary(self):
        last_clk = self.pi1.read(self.rotaryA)
        last_time = time.time()
        
        while True:
            current_clk = self.pi1.read(self.rotaryA)
            if current_clk != last_clk:
                current_time = time.time()
                # Speed Check
                self.fast = (current_time - last_time) < 0.05
                last_time = current_time

                # Direction Check
                if current_clk != self.pi1.read(self.rotaryB):
                    self.tally += 1 
                else:
                    self.tally -= 1
                last_clk = current_clk
            
            # 1ms sleep: Fast enough for direction, slow enough for CPU
            time.sleep(0.001)

    def checkButton(self):
        while True:
            # Wait for press
            if self.pi1.read(self.switchPin) == 0:
                start = time.time()
                while self.pi1.read(self.switchPin) == 0:
                    time.sleep(0.01)
                
                duration = time.time() - start
                if duration > 2.0: self.longClicked = True
                elif duration > 0.05: self.clicked = True
            time.sleep(0.05)

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

