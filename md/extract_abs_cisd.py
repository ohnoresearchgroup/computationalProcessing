# -*- coding: utf-8 -*-
"""
Spyder Editor


"""

import re
import os

#function to go through the file and find the correct energy
def readFile(filename,frame_num):
    # Open the file in read mode
    with open(filename, 'r') as file:
        # Read all lines from the file
        lines = file.readlines()

    # Loop through each line to find first excited state and oscillator strength
    # currently assumes that the first state is the correct one, but it will print a warning
    # if the oscillator strength is below 0.6
    for line in lines:
        if line.startswith(" Excited State   1"):
            match = re.search(r'f\s*=\s*([-+]?\d*\.\d+|\d+)', line)
            if match:
                osc_str = float(match.group(1))
                if osc_str < 0.6:
                    print("oscillator strength for frame " + str(frame_num) + 'is low: ' + str(osc_str))
            break
    
    #find the cis(d) correction for the first state)
    found_first = False
    for line in lines:
        if not found_first:
            if line.startswith(" CIS(D) Correction to the CiSingles state  1"):
                found_first = True
        else:
            if line.startswith(" CIS(D) Exc. E:"):
                match = re.search(r'([-+]?\d*\.?\d+)\s*nm', line)
                if match:
                    wl = float(match.group(1))
                    return wl

#create list of subdirectories in directory
parentdir = "cisd"
directories = [os.path.join(parentdir, d) for d in os.listdir(parentdir) if os.path.isdir(os.path.join(parentdir, d))]

energies = {}
for d in directories:
    match = re.search(r'\d+', d)
    if match:
        frame_num = int(match.group())
    else:
        print("No frame number in folder.")
        break
    
    
    filenames = os.listdir(d)
    for filename in filenames:
        if filename[-4:] == ".log":
            wl  = readFile(os.path.join(d,filename),frame_num)
            energies[frame_num] = wl
            
            
print(energies)


