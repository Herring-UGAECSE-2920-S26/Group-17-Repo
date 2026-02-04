import pigpio
import asyncio
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
        
        self.pi1.set_mode(self.rotaryB, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.rotaryB, pigpio.PUD_UP)

        self.pi1.set_mode(self.switchPin, pigpio.INPUT)
        self.pi1.set_pull_up_down(self.switchPin, pigpio.PUD_UP)

        self.pi1.set_glitch_filter(switchPin, 50000)

        #set up other vars
        self.readA = None
        self.readB = None
        self.prevA = None
        self.clockwise = None
        self.fast = False
        self.resistance = 100

    #check direction and speed of encoder spinning    
    async def checkRotary():
        startTime = time.perf_counter()
        self.prevA = self.p1.read(self.rotaryA)
        
        while True:
            self.readA = self.p1.read(self.rotaryA) #find current A pin value

            #if rotary encoder is spinning
            if self.readA != self.prevA:
                endTime = time.perf_Counter()
                print("Click!")
                #checks speed
                if startTime - endTime >= 1:
                    self.fast = False
                    print("Slow")
                else:
                    self.fast = True
                    print("Fast")

                #checks direction
                if self.pi1.read(self.rotaryB) != self.readA:
                    self.clockwise = True
                    print("Clockwise")
                else:
                    self.clockwise = False
                    print("Counterclockwise")

            #update values
            self.prevA = self.readA
            startTime = time.perf_counter()
            #lets other coroutines run
            await asyncio.sleep(0)

# --- For Testing ---
if __name__ == "__main__":

    pi1 = pigpio.pi()
    rot = Rotary(18, 23, 24, pi1)
    asyncio.run(rot.checkRotary())
