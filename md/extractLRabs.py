# -*- coding: utf-8 -*-
"""
Spyder Editor


"""

import re
import os

#function to go through the file and find the correct energy
def readFile(filename):
    # Open the file in read mode
    with open(filename, 'r') as file:
        # Read all lines from the file
        lines = file.readlines()

    # Loop through each line and check if it starts with " After PCM"
    for line in lines:
        if line.startswith(" After PCM"):
            # Split the line on spaces
            split_line = line.split()

            # Filter out substrings that represent floats
            floats = [x for x in split_line if re.match(r'^-?\d+\.?\d*$', x)]
        
            #find first float which is energy
            energy = float(floats[0])

            break
        
    return energy

#create list of subdirectories in LRve directory
parentdir = "LRve"
directories = [os.path.join(parentdir, d) for d in os.listdir(parentdir) if os.path.isdir(os.path.join(parentdir, d))]

#go through that list of directories and read each energy
energies = []
for d in directories:
    filenames = os.listdir(d)
    for filename in filenames:
        if filename[-4:] == ".log":
            energy = readFile(filename)
            energies.append(energy)
            
print(energies)


