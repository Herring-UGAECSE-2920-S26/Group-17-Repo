def min_difference(digi1R):
    select_resistance = digi1R
    #sets the value used to compare to differnce very high so that any mesured will be less
    min_difference = float(100000) 
    #print("start")

    for i in range(0, 128): # 1 - 128 steps of digipot
        resistance = 0.0732*i + 0.124 # characteristic eqn of our dual digipot
        # goes through difference between every resistance at each step and the resistance choosen by the user #
        difference = abs(select_resistance - resistance) 

        # goes through range and sets min_diff to smallest difference and sets i at that step
        if difference < min_difference: 
            min_difference = difference
            step = i
            #print("min difference:", min_difference)
            #print("step:", step)

    return step

#print(f"set to step: {step}")
if __name__ == "__main__":
    select_resistance = input("resistance in kOhms: ")
    selected_resistance = float(select_resistance)
    print(f"Selected {selected_resistance}")
    step = min_difference(selected_resistance)
    print(f"set to step: {step}")
    
