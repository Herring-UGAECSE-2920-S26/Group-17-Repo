import time
import pigpio

# GPIO Pin Setup
GPIO_VIN_CTRL = 5
GPIO_VREF_CTRL = 6
GPIO_COMP_IN = 4
GPIO_CAP_RS = 12
GPIO_OHM_CTRL = 13  # New Ohmmeter Control

pi = pigpio.pi()

# Initialize Modes
pi.set_mode(GPIO_VIN_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_VREF_CTRL, pigpio.OUTPUT)
pi.set_mode(GPIO_COMP_IN, pigpio.INPUT)
pi.set_mode(GPIO_CAP_RS, pigpio.OUTPUT)
pi.set_mode(GPIO_OHM_CTRL, pigpio.OUTPUT) # Initialize Ohm pin

pi.set_pull_up_down(GPIO_COMP_IN, pigpio.PUD_UP)

print("Manual ADC & Ohmmeter Tester")
print("----------------------------")

while True:
    try:
        user_input = int(input("\nEnter 1 (Vref), 2 (Vin), 3 (Reset), 4 (Ohmmeter), 5 (Exit): "))
    except ValueError:
        print("Please enter a valid number.")
        continue

    # Option 1: Vref
    if user_input == 1:
        print("Activating Vref Switch...")
        pi.write(GPIO_VREF_CTRL, 1)
        pi.write(GPIO_VIN_CTRL, 0)
        pi.write(GPIO_CAP_RS, 0)
        pi.write(GPIO_OHM_CTRL, 0)

    # Option 2: Vin
    elif user_input == 2:
        print("Activating Vin Switch...")
        pi.write(GPIO_VIN_CTRL, 1)
        pi.write(GPIO_VREF_CTRL, 0)
        pi.write(GPIO_CAP_RS, 0)
        pi.write(GPIO_OHM_CTRL, 0)

    # Option 3: Reset
    elif user_input == 3:
        print("Resetting Capacitor...")
        pi.write(GPIO_CAP_RS, 1)
        pi.write(GPIO_VIN_CTRL, 0)
        pi.write(GPIO_VREF_CTRL, 0)
        pi.write(GPIO_OHM_CTRL, 0)

    # Option 4: Ohmmeter
    elif user_input == 4:
        print("Activating Ohmmeter Mode...")
        pi.write(GPIO_OHM_CTRL, 1)
        pi.write(GPIO_VIN_CTRL, 0)
        pi.write(GPIO_VREF_CTRL, 0)
        pi.write(GPIO_CAP_RS, 0)

    # Option 5: Exit
    elif user_input == 5:
        print("Exiting and clearing pins.")
        pi.write(GPIO_VIN_CTRL, 0)
        pi.write(GPIO_VREF_CTRL, 0)
        pi.write(GPIO_CAP_RS, 0)
        pi.write(GPIO_OHM_CTRL, 0)
        break 

    else:
        print("Invalid choice, try again.")

# Cleanup
pi.stop()
