import subprocess
import os
import pandas as pd
import numpy as np

#names of files
paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"


#frames you are selecting, None if all frames
selectedframes = None
#selectedframes = np.arange(25,1225,25)

masks = ["@1-42","@1","@10","@15","@22"]

for mask in masks:
    with open('closest.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        file.write("solvent :Na+\n")
        file.write("closest 1 " + mask + " closestout closestNa" + mask[1:] + "\n" )
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","closest.cpptraj"])
    os.remove("closest.cpptraj")
    
    with open('closest.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        file.write("solvent :Cl-\n")
        file.write("closest 1 " + mask + " closestout closestCl" + mask[1:] + "\n" )
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","closest.cpptraj"])
    os.remove("closest.cpptraj")


for mask in masks:
    df_Na = pd.read_csv("closestNa" + mask[1:], sep='\\s+')
    df_Na = df_Na.drop(columns =["CLOSEST_00001[FirstAtm]","CLOSEST_00001[Mol]"])
    df_Na = df_Na.rename(columns={'#CLOSEST_00001[Frame]': 'frame', "CLOSEST_00001[Dist]": 'distance_Na'})
    os.remove("closestNa" + mask[1:])
    
    df_Cl = pd.read_csv("closestCl" + mask[1:], sep='\\s+')
    df_Cl = df_Cl.drop(columns =["CLOSEST_00001[FirstAtm]","CLOSEST_00001[Mol]"])
    df_Cl = df_Cl.rename(columns={'#CLOSEST_00001[Frame]': 'frame', "CLOSEST_00001[Dist]": 'distance_Cl'})
    os.remove("closestCl" + mask[1:])
    
    df = df_Na
    df['distance_Cl'] = df_Cl['distance_Cl']
    
    
    #only choose from selected frames
    if selectedframes is not None:
        filtereddf = df[df['frame'].isin(selectedframes)]
    else:
        filtereddf = df
    
    #create allhbonds.csv
    filtereddf.to_csv("closestion" + mask[1:] + ".csv", sep= ',',index=False,float_format='%.8f')