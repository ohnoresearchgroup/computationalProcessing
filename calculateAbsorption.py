# -*- coding: utf-8 -*-
"""
Spyder Editor


"""

import re

filename_gso = "C:\\Users\\peo0005\\OneDrive - Auburn University\\Documents\\GitHub\\computationalProcessing\\examplefiles\\gsopfreq-wat.gjf.log"
filename_ve = "C:\\Users\\peo0005\\OneDrive - Auburn University\\Documents\\GitHub\\computationalProcessing\\examplefiles\\water.gjf.log"

def calculateAbsorption(filename_gso,filename_ve):
    # Open the file in read mode
    with open(filename_gso, 'r') as file_gso:
        # Read all lines from the file
        lines = file_gso.readlines()
        revlines = lines[::-1]

    # Loop through each line and check if it starts with "string1"
    for line in revlines:
        if line.startswith(" SCF Done"):
            # Split the line on spaces
            split_line = line.split()
            
            # Filter out substrings that represent floats
            floats = [x for x in split_line if re.match(r'^-?\d+\.?\d*$', x)]
            
            #find first float which is energy
            energy1 = float(floats[0])
            
            break
    
    
    # Open the file in read mode
    with open(filename_ve, 'r') as file_ve:
        # Read all lines from the file
        lines = file_ve.readlines()

    # Loop through each line and check if it starts with "string1"
    for line in lines:
        if line.startswith(" After PCM"):
            # Split the line on spaces
            split_line = line.split()

            # Filter out substrings that represent floats
            floats = [x for x in split_line if re.match(r'^-?\d+\.?\d*$', x)]
        
            #find first float which is energy
            energy2 = float(floats[0])

            break
    
    energy = energy1 - energy2
    return energy