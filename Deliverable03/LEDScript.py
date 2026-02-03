import pigpio
# Importing Library

# Initializing the connection to the pigpio daemon
pi1 = pigpio.pi()

# Defining Pin Numbers
ledPin = 18 #LED
switchPin = 24 #Switch/encoder button

pi1.set_mode(ledPin, pigpio.OUTPUT) # Set LED Pin as output
pi1.set_mode(switchPin, pigpio.INPUT) #Set switch pin as input

# This keeps the input at 3.3V (HIGH) until the switch is pressed
pi1.set_pull_up_down(switchPin, pigpio.PUD_UP) 

# This ignores signal noise/bouncing for 50,000 microseconds to ensure clean triggering
pi1.set_glitch_filter(switchPin, 50000)

# Use hardware-timed edge detection to wait for a switch press, then toggle the LED's current state.
while True:
    pi1.wait_for_edge(switchPin)
    if pi1.read(ledPin) == 1:
        pi1.write(ledPin, 0)
        print("LED On")
    elif pi1.read(ledPin) == 0:
        pi1.write(ledPin, 1)
        print("LED Off")

