def min_difference(digi1R):
    select_resistance = digi1R
    min_difference = float(100000) #sets the value used to compare to differnce very high so that any mesured

    for i in range(0, 128): # 1 - 128 steps of digipot
        resistance = 0.0732*i + 0.124 # characteristic eqn of our dual digipot
        difference = abs(selected_resistance - resistance) # goes through difference between every resistance at each step and the resistance choosen by the user #

    if difference < min_difference: # goes through range and sets min_diff to smallest difference and sets i at that step
        min_difference = difference
        step = i

print(f"set to step: {step}")
if __name__ == "__main__":
    selected_resistance = float(input('resistance in kOhms'))
