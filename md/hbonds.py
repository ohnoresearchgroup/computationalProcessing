import subprocess
import os
import pandas as pd
import numpy as np

#names of files
paramfile = "solv1.parm7"
trajfile = "prod_gs_1m1.dcd"


#frames you are selecting (this is from 25 to 1200, every 25)
selectedframes = np.arange(25,1225,25)

#atoms that are hbond acceptors
masks = ["@1","@10","@15","@22"]

for mask in masks:
    with open('hbond.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        file.write("hbond acceptormask " + mask + " solventdonor :WAT series uvseries uvhbonds"  + mask[1:] +".dat\n")
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","hbond.cpptraj"])
    os.remove("hbond.cpptraj")

fulldf = pd.DataFrame()
for mask in masks:
    df = pd.read_csv("uvhbonds" + mask[1:] +".dat", sep='\\s+')
    fulldf = pd.concat([fulldf, df], axis = 1)
    os.remove("uvhbonds" + mask[1:] +".dat")

#drop duplicate frames
fulldf = fulldf.loc[:, ~fulldf.columns.duplicated()]
fulldf['all'] = fulldf.drop(columns=['#Frame']).sum(axis=1)  

#only choose from selected frames
filtereddf = fulldf[fulldf['#Frame'].isin(selectedframes)]

#create allhbonds.csv
filtereddf.to_csv("allhbonds.csv", sep= ',',index=False,float_format='%.8f')