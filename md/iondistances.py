import subprocess
import os
import pandas as pd
import numpy as np

#names of files
paramfile = "solv1.parm7"
trajfile = "prod_gs_1m1.dcd"


#frames you are selecting (this is from 25 to 1200, every 25)
selectedframes = np.arange(25,1225,25)

names = ["wholesolute","ocarbonyl","nring","oring","ndiethyl"]
masks = ["@1-42","@1","@10","@15","@22"]

for mask in masks:
    with open('closest.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        file.write("solvent :Na+,Cl-\n")
        file.write("closest 1 " + mask + " closestout closestion" + mask[1:] + "\n" )
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","closest.cpptraj"])
    os.remove("closest.cpptraj")


for mask in masks:
    df = pd.read_csv("closestion" + mask[1:], sep='\\s+')
    df = df.drop(columns =["CLOSEST_00001[FirstAtm]","CLOSEST_00001[Mol]"])
    df = df.rename(columns={'#CLOSEST_00001[Frame]': 'frame', "CLOSEST_00001[Dist]": 'distance'})
    os.remove("closestion" + mask[1:])
    
    #only choose from selected frames
    filtereddf = df[df['frame'].isin(selectedframes)]
    
    #create allhbonds.csv
    filtereddf.to_csv("closestion" + mask[1:] + ".csv", sep= ',',index=False,float_format='%.8f')