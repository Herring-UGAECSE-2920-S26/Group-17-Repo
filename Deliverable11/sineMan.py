import pigpio

# Configure GPIO pins for DAC
DAC1 = 16
DAC2 = 20
DAC3 = 21
DAC4 = 25
DAC5 = 26

pi = pigpio.pi()

# Pin Set-up
pi.set_mode(DAC1, pigpio.OUTPUT)
pi.set_mode(DAC2, pigpio.OUTPUT)
pi.set_mode(DAC3, pigpio.OUTPUT)
pi.set_mode(DAC4, pigpio.OUTPUT)
pi.set_mode(DAC5, pigpio.OUTPUT)

print("Manual DAC Tester")
print("-------------------------")

while True:
    try:
        user_input = int(input("\nEnter 1 (DAC1), 2 (DAC2), 3 (DAC3), 4 (DAC4), 5 (DAC5), 6 (Exit): "))
    except ValueError:
        print("Please enter a valid number.")
        continue

    if user_input == 1:
        print("Activating DAC1")
        pi.write(DAC1, 1)
        pi.write(DAC2, 0)
        pi.write(DAC3, 0)
        pi.write(DAC4, 0)
        pi.write(DAC5, 0)

    elif user_input == 2:
        print("Activating DAC2")
        pi.write(DAC2, 1)
        pi.write(DAC1, 0)
        pi.write(DAC3, 0)
        pi.write(DAC4, 0)
        pi.write(DAC5, 0)

    elif user_input == 3:
        print("Activating DAC3")
        pi.write(DAC3, 1)
        pi.write(DAC2, 0)
        pi.write(DAC1, 0)
        pi.write(DAC4, 0)
        pi.write(DAC5, 0)
    
    elif user_input == 4:
        print("Activating DAC4")
        pi.write(DAC4, 1)
        pi.write(DAC3, 0)
        pi.write(DAC2, 0)
        pi.write(DAC1, 0)
        pi.write(DAC5, 0)
    
    elif user_input == 5:
        print("Activating DAC5")
        pi.write(DAC5, 1)
        pi.write(DAC4, 0)
        pi.write(DAC3, 0)
        pi.write(DAC2, 0)
        pi.write(DAC1, 0)
    
    elif user_input == 6:
        print("Exiting and clearing pins.")
        pi.write(DAC5, 0)
        pi.write(DAC4, 0)
        pi.write(DAC3, 0)
        pi.write(DAC2, 0)
        pi.write(DAC1, 0)
        break 

    else:
        print("Invalid choice, try again.")

# Cleanup
pi.stop()
