# -*- coding: utf-8 -*-
"""
Spyder Editor


"""

import re

filename_gso = "C:\\Users\\peo0005\\OneDrive - Auburn University\\Documents\\GitHub\\computationalProcessing\\examplefiles\\gsopfreq-wat.gjf.log"
filename_ve = "file2.txt"


# Open the file in read mode
with open(filename_gso, 'r') as file:
    # Read all lines from the file
    lines = file.readlines()
    revlines = lines[::-1]

# Loop through each line and check if it starts with "string1"
for line in revlines:
    if line.startswith(" SCF Done"):
        # Split the line on spaces
        split_line = line.split()

        # Filter out substrings that represent floats
        floats = [x for x in split_line if re.match(r'^-?\d+\.?\d*$', x)]
        
        #find first float which is energy
        energy = float(floats[0])
        print(energy)

        break