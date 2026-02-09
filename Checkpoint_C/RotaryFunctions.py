import pigpio
import time
import asyncio

class Rotary:
    minR = 110
    maxR = 9422

    def __init__(self, rotaryA, rotaryB, switchPin, pi1):
        self.rotaryA = rotaryA
        self.rotaryB = rotaryB
        self.switchPin = switchPin
        self.pi1 = pi1

        for pin in [rotaryA, rotaryB, switchPin]:
            self.pi1.set_mode(pin, pigpio.INPUT)
            self.pi1.set_pull_up_down(pin, pigpio.PUD_UP)

        self.pi1.set_glitch_filter(self.rotaryA, 3000)
        self.pi1.set_glitch_filter(self.rotaryB, 3000)
        self.pi1.set_glitch_filter(self.switchPin, 20000)

        self.changed = False
        self.clockwise = False
        self.fast = False
        self.prevA = None

    async def checkRotary(self):
        self.prevA = self.pi1.read(self.rotaryA)
        startTime = time.perf_counter()
        
        while True:
            readA = self.pi1.read(self.rotaryA)
            if readA != self.prevA and readA == 0:
                endTime = time.perf_counter()
                self.fast = (endTime - startTime) < 0.2
                startTime = endTime
                self.clockwise = (self.pi1.read(self.rotaryB) == 1)
                self.changed = True
            
            self.prevA = readA
            await asyncio.sleep(0.001)
