import subprocess
import os
import pandas as pd
import numpy as np

#names of files
paramfile = "solv1.parm7"
trajfile = "prod_gs_1m1.dcd"

threshold = 3

#frames you are selecting (this is from 25 to 1200, every 25)
selectedframes = np.arange(25,1225,25)

mask = "@1-42"


with open('watershell.cpptraj','w') as file:
    file.write("parm " + paramfile + "\n")
    file.write("trajin " + trajfile + "\n")
    file.write("solvent :Na+,Cl-\n")
    file.write("watershell " + mask + " out numberions" + str(threshold) + " lower " + str(threshold) + " upper " + str(threshold) + "\n" )
    file.write("go")
    
#run cpptraj file, then delete it
subprocess.run(["cpptraj","watershell.cpptraj"])
os.remove("watershell.cpptraj")



df = pd.read_csv("numberions" + str(threshold), sep='\\s+')
df = df.drop(columns =["WS_00001[upper]"])
df = df.rename(columns={'#Frame': 'frame', "WS_00001[lower]": '#ions'})
os.remove("numberions" + str(threshold))

#only choose from selected frames
filtereddf = df[df['frame'].isin(selectedframes)]

#create allhbonds.csv
filtereddf.to_csv("numberions" + str(threshold) + ".csv", sep= ',',index=False,float_format='%.8f')