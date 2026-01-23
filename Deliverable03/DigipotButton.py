import spidev #https://pypi.org/project/spidev/
import sys
import pigpio #https://abyz.me.uk/rpi/pigpio/index.html
import DigipotCode

pi1 = pigpio.pi() #opens an instance of pigpio

#define vars
switchPin = 24
count = 0
pot = MCP4131() #create instance of class found in DigipotCode.py

#sets up the switch pin
pi1.set_mode(switchPin, pigpio.INPUT)
pi1.set_pull_up_down(switchPin, pigpio.PUD_UP)

#debounces the button
pi1.set_glitch_filter(switchPin, 50000)

#Transfer Function: KOhm = 0.0744x + 0.127

while True:
    pi1.wait_for_edge(switchPin) #following code happens on button press
    count += 1

    if count == 1:
        pot.set_step(0) #set digipot to 100
    elif count == 2:
        pot.set_step(12) #set digipot to 1000
    elif count == 3:
        pot.set_step(66) #set digipot to 5000
    elif count == 4:
        count = 0
        pot.set_step(128) #set digipot to 10000
    

