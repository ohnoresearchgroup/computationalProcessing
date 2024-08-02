import subprocess
import os
import pandas as pd
import numpy as np


#names of files
paramfile = "solv1.parm7"
trajfile = "prod_gs_1m1.dcd"

solutemask = "@1-42"

#in angstroms
thresholdInner = 4 #threshold distance for first layer
thresholdOuter = 8 #threshold distance to outside of second layer

#select frames
frames = np.arange(25,1225,25)


#nothing to edit below here
strthresholdInner = str(round(thresholdInner,1))
strthresholdOuter = str(round(thresholdOuter,1))


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
    
    #create cpptraj file that will remove ions outside of outer threshold
    with open('strip.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("reference " + frametrajfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip :WAT\n")
        file.write("strip !(@1-42<^"+ strthresholdOuter + ")&:Na+,Cl-\n")
        file.write("strip @1-42\n")
        file.write("trajout strippedOuter." + str(i) + ".xyz xyz nobox\n")
        file.write("go")   
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","strip.cpptraj"])
    os.remove("strip.cpptraj")

    
    #create cpptraj file that will remove ions outside of innner threshold      
    with open('strip.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("reference " + frametrajfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip :WAT\n")
        file.write("strip !(@1-42<^"+ strthresholdInner + ")&:Na+,Cl-\n")
        file.write("strip @1-42\n")
        file.write("trajout strippedInner." + str(i) + ".xyz xyz nobox\n")
        file.write("go")   

    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","strip.cpptraj"])
    os.remove("strip.cpptraj")
    
    #remove individual full frames
    if os.path.exists(frametrajfile):
        os.remove(frametrajfile)
    

dfIonCounts = pd.DataFrame(columns=["Frame","Inner Na+", "Inner Cl-","Inner Total","Outer Na+", "Outer Cl-","Outer Total"])


for i in frames:    
    outerfilename = "strippedOuter." + str(i) + ".xyz"
    innerfilename = "strippedInner." + str(i) + ".xyz"
    
    
    
    #remove file headers and remove from outer file lines that appear in inner files
    with open(innerfilename,'r') as innerfile:
        innerlines = set(innerfile.readlines()[2:])
    with open(outerfilename,'r') as outerfile:
        outerlines = set(outerfile.readlines()[2:])
    filteredlines = outerlines - innerlines
    with open(outerfilename,'w') as outerfile:
        outerfile.writelines(filteredlines)
    with open(innerfilename,'w') as innerfile:
        innerfile.writelines(innerlines)


    #read in inner file
    dfInner = pd.read_csv(innerfilename, sep='\\s+', names = ['atoms','x','y','z'],na_values=[], keep_default_na=False)   
    innerNa = (dfInner['atoms'] == 'NA').sum()
    innerCl = (dfInner['atoms'] == 'CL').sum() 
    innerTotal = innerNa + innerCl
    #delete the inner file
    if os.path.exists(innerfilename):
        os.remove(innerfilename)
        
    #read in the outer file
    dfOuter = pd.read_csv(outerfilename, sep='\\s+', names = ['atoms','x','y','z'],na_values=[], keep_default_na=False)       
    #calculate the charge of the low layer
    outerNa  = (dfOuter['atoms'] == 'NA').sum()
    outerCl = (dfOuter['atoms'] == 'Cl').sum() 
    outerTotal = outerNa + outerCl
    #delete the outer file
    if os.path.exists(outerfilename):
        os.remove(outerfilename)
        
    new_line = {'Frame': i,
                "Inner Na+": innerNa, "Inner Cl-": innerCl, "Inner Total": innerTotal, 
                "Outer Na+": outerNa, "Outer Cl-": outerCl, "Outer Total": outerTotal}
    
    dfIonCounts.loc[len(dfIonCounts)] = new_line


#output dataframe
dfIonCounts.to_csv("numberions.csv", sep= ',',index=False,float_format='%.8f')
    
