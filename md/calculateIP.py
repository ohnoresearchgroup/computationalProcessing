# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 16:48:19 2024

@author: peo0005
"""

import pandas as pd
import numpy as np

filename = "closestion"

masks = ["@1","@10","@15","@22"]

with open("ionpairs.txt", "w") as file:

    for mask in masks:
        line = 'Atom: ' + mask[1:] + '\n'
        file.write(line)
        df = pd.read_csv(filename + mask[1:]+".csv")
        length = len(df)
    
        na_CIP = len(df[df['distance_Na'] <= 3.0])
        na_SSIP = len(df[(df['distance_Na'] > 3.0) & (df['distance_Na'] <= 5.5)])
        
        cl_CIP = len(df[df['distance_Cl'] <= 3.0])
        cl_SSIP = len(df[(df['distance_Cl'] >= 3.0) & (df['distance_Cl'] <= 5.5)])
        
        line = 'Na+ CIP: ' + str(np.round(na_CIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Na+ SSIP: ' + str(np.round(na_SSIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Cl- CIP: ' + str(np.round(cl_CIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Cl- SSIP: ' + str(np.round(na_SSIP/length*100,2)) + '%\n'
        file.write(line)

        file.write('\n')