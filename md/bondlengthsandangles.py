# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 17:05:46 2025

@author: peo0005
"""

import pandas as pd
import re
import numpy as np

#specify the atoms in each bond, for which to calculate distance
bonds = ["C21-O22","C23-O22","C2-O1","C11-N10","C9-N10","C14-N15",
         "C16-N15","C18-N15","C11-C12","C12-C13","C13-C14","C14-C20",
         "C20-C21","C11-C21","C9-C23","C8-C9","C3-C8","C2-C3","C2-C24",
         "C23-C24","C7-C8","C3-C4","C4-C5","C5-C6","C6-C7","C16-C17",
         "C18-C19","C5-H26","C6-H27","C7-H28","C4-H25","C24-H42","C12-H29",
         "C13-H30","C20-H41","C18-H36","C18-H37","C19-H38","C19-H39",
         "C19-H40","C16-H32","C16-H31","C17-H34","C17-H33","C17-H35"]  

#create a dataframe with column names of each bond
distances = pd.DataFrame(columns=bonds)
distances.insert(0,'frame',[])


#specify file name
file_path = "gas.frame.25.LRve.gjf.log" 

#find the frame from the file name
frame = int(file_path.split('.')[2])

with open(file_path, "r") as file:
    lines = file.readlines()

#extract atomic coordinates, name atoms up from 1
atoms = []
pattern = re.compile(r"^\s*([A-Z][a-z]?)\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)")
count = 1
for line in lines:
    match = pattern.match(line)
    if match:
        atom, x, y, z = match.groups()
        unique_atom = f"{atom}{count}"
        atoms.append([unique_atom, float(x), float(y), float(z)])
        count = count + 1

#create dataframe to hold these coordinates
df = pd.DataFrame(atoms, columns=["Atom", "X", "Y", "Z"])


#function to calculate distance between two atoms
def calculate_distance(atom1, atom2):
    coords1 = df[df["Atom"] == atom1][["X", "Y", "Z"]].values
    coords2 = df[df["Atom"] == atom2][["X", "Y", "Z"]].values
    
    if len(coords1) == 0 or len(coords2) == 0:
        raise ValueError("One or both specified atoms not found in the DataFrame.")
    
    return np.round(np.linalg.norm(coords1[0] - coords2[0]),3)

#create the row that has each distance as an element
row = [frame]
for bond in bonds:
    atom1 = bond.split("-")[0]
    atom2 = bond.split("-")[1]
    distance = calculate_distance(atom1,atom2)
    row.append(distance)

#add that row to the distance
distances = pd.concat([distances, pd.DataFrame([row],columns = distances.columns)],
                      ignore_index=True)
#print the distances
print(distances)