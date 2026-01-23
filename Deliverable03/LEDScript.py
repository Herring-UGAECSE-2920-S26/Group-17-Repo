import pigpio
#import time
pi1 = pigpio.pi()

ledPin = 18
switchPin = 24

pi1.set_mode(ledPin, pigpio.OUTPUT)
pi1.set_mode(switchPin, pigpio.INPUT)
pi1.set_pull_up_down(switchPin, pigpio.PUD_UP)

pi1.set_glitch_filter(switchPin, 50000)

#print("LED Off")

#print("LED Pin:", pi1.read(ledPin))
#print("Switch Pin:", pi1.read(switchPin))

#pi1.write(ledPin, 0)
#print("LED Pin:", pi1.read(ledPin))
#print("Switch Pin:", pi1.read(switchPin))

#time.sleep(15)

#pi1.write(ledPin, 1)
#print("LED Pin:", pi1.read(ledPin))
#print("Switch Pin:", pi1.read(switchPin))

#print("End Script")

while True:
    pi1.wait_for_edge(switchPin)
    if pi1.read(ledPin) == 1:
        pi1.write(ledPin, 0)
        print("LED On")
    elif pi1.read(ledPin) == 0:
        pi1.write(ledPin, 1)
        print("LED Off")

