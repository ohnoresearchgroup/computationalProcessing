import subprocess
import os
import pandas as pd



#names of files
paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"


dihed1 = (13, 14, 15, 16)  # Dihedral 1
dihed2 = (20, 14, 15, 18)  # Dihedral 2
dihed3 = (13, 14, 15, 18)  # Dihedral 3
dihed4 = (20, 14, 15, 16)   # Dihedral 4


#select frames
frames = [3750,3800,3850,3900,3950,4050,4100,4150,4200,4300,4350,4400,4450,4550,4600,4650,4700,4800,4850,4950]


#create cpptraj file to select certain frames and output as pdb
with open('dihedral.cpptraj','w') as file:
    file.write("parm " + paramfile + "\n")
    file.write("trajin " + trajfile + "\n")
    file.write("dihedral dihed1 @" + str(dihed1[0]) + " @" + 
               str(dihed1[1]) + " @" + str(dihed1[2]) + " @" + str(dihed1[3]) + " out dihed1.dat\n")
    file.write("dihedral dihed2 @" + str(dihed1[0]) + " @" + 
               str(dihed2[1]) + " @" + str(dihed2[2]) + " @" + str(dihed2[3]) + " out dihed2.dat\n")
    file.write("dihedral dihed3 @" + str(dihed3[0]) + " @" + 
                str(dihed3[1]) + " @" + str(dihed3[2]) + " @" + str(dihed3[3]) + " out dihed3.dat\n")
    file.write("dihedral dihed4 @" + str(dihed4[0]) + " @" + 
               str(dihed4[1]) + " @" + str(dihed4[2]) + " @" + str(dihed4[3]) + " out dihed4.dat\n")
    file.write("go")

#run cpptraj file, then delete it
subprocess.run(["cpptraj","dihedral.cpptraj"])
os.remove("dihedral.cpptraj")



df1 = pd.read_csv("dihed1.dat", sep='\\s+')
df2 = pd.read_csv("dihed2.dat", sep='\\s+')
df2 = df2.drop(columns=['#Frame'])
df3 = pd.read_csv("dihed3.dat", sep='\\s+')
df3 = df3.drop(columns=['#Frame'])
df4 = pd.read_csv("dihed4.dat", sep='\\s+')
df4 = df4.drop(columns=['#Frame'])

fulldf = pd.concat([df1, df2, df3, df4], axis = 1)

os.remove("dihed1.dat")
os.remove("dihed2.dat")
os.remove("dihed3.dat")
os.remove("dihed4.dat")

#only choose from selected frames
filtereddf = fulldf[fulldf['#Frame'].isin(frames)]

#create alldihedrals.csv
filtereddf.to_csv("alldihedrals.csv", sep= ',',index=False,float_format='%.8f')