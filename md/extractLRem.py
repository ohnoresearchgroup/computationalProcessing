# -*- coding: utf-8 -*-
"""
Spyder Editor


"""

import os

#function to go through the file and find the correct energy
def readFile(filename):
    # Open the file in read mode
    targetstring = " Excitation energies and oscillator strengths:"
    linenumberlastexcitation = 0;
    with open(filename, 'r') as file:
        for linenumber, line in enumerate(file,1):
            if line.startswith(targetstring):
                linenumberlastexcitation = linenumber
                
    
    targetstring = " Excited State"
    oscstrengths = []
    wavelengths = []
    with open(filename, 'r') as file:
        for linenumber, line in enumerate(file,1):
            if linenumber < linenumberlastexcitation:
                continue
            if line.startswith(targetstring):                
                #print(line)
                split_line = line.split()
                oscstrengths.append(float(split_line[8][2:]))
                wavelengths.append(float(split_line[6]))

    maxindex = oscstrengths.index(max(oscstrengths))
    print("Found excited state #"  + str(maxindex+1),
          " with osc strength =",oscstrengths[maxindex],
          "and wavelength =", wavelengths[maxindex], "nm")
    
    return wavelengths[maxindex]

#create list of subdirectories in LRve directory
parentdir = "LRem"
directories = [os.path.join(parentdir, d) for d in os.listdir(parentdir) if os.path.isdir(os.path.join(parentdir, d))]

#go through that list of directories and read each energy
wls = []
for d in directories:
    filenames = os.listdir(d)
    for filename in filenames:
        if filename[-4:] == ".log":
            wl = readFile(filename)
            wls.append(wl)

print(wls)


