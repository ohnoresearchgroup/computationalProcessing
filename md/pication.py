import subprocess
import os
import pandas as pd

paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"

limit = 6.2 #angstrom


#ring to look for ions interaction
ring = [11,12,13,14,20,21]
#ring = [9,10,11,21,22,23]
#ring = [2,3,8,9,23,24]
#ring = [3,4,5,6,7,8]

#select frames
frames = [3750,3800,3850,3900,3950,4050,4100,4150,4200,4300,4350,4400,4450,4550,4600,4650,4700,4800,4850,4950]
#frames = [100,1000]

#create cpptraj file to select certain frames and output as pdb
with open('createframes.cpptraj','w') as file:
    file.write("parm " + paramfile + "\n")
    file.write("trajin " + trajfile + "\n")
    file.write("trajout fullframe pdb onlyframes " + 
               ','.join(map(str, frames)) + " multi\n")
    file.write("go")

#run cpptraj file, then delete it
subprocess.run(["cpptraj","createframes.cpptraj"])
os.remove("createframes.cpptraj")

#rename pdb full frame pdb files to add extension
for i in frames:
    #name of frame to examine
    frametrajfile = "fullframe." + str(i)
    os.rename(frametrajfile,frametrajfile + ".pdb")


#go through each fullframe and strip them of specified molecules
for i in frames:
    #name of frame to examine
    frametrajfile = "fullframe." + str(i) + ".pdb"
    
    #create cpptraj file that will remove ions outside of threshold
    with open('strip.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("reference " + frametrajfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        for atom in ring:
            file.write("strip !(@" +str(atom) + "<^"+ str(limit) + ")&:Cl-\n")
            file.write("strip !(@" +str(atom) + "<^"+ str(limit) + ")&:Na+\n")
        file.write("strip :WAT\n")
        file.write("trajout strippedpiion." + str(i) + ".xyz xyz nobox\n")
        file.write("go")   

    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","strip.cpptraj"])
    os.remove("strip.cpptraj")


dfIonCounts = pd.DataFrame(columns=["Frame", "Na+", "Cl-"])

    
for i in frames:
    #name of frame to examine
    framexyzfile = "strippedpiion." + str(i) + ".xyz"
    
    df = pd.read_csv(framexyzfile,sep='\\s+',skiprows=2, names = ['atoms','x','y','z'],na_values=[], keep_default_na=False)
    
    Na  = (df['atoms'] == 'NA').sum()
    Cl = (df['atoms'] == 'CL').sum() 
    
    new_line = {'Frame': i, "Na+": Na, "Cl-": Cl}    
    dfIonCounts.loc[len(dfIonCounts)] = new_line
    

#output dataframe
dfIonCounts.to_csv("pi_ions.csv", sep= ',',index=False,float_format='%.8f')
        

    
