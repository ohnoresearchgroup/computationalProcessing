import subprocess
import os

paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"
solutemask = "@1-42"


#select frames
frames = [100,1000]
basename = "prodimagei"

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
        file.write("strip !(@1-42)\n")
        file.write("trajout " + basename + ".frame." + str(i) + ".xyz xyz nobox\n")
        file.write("go")   
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","strip.cpptraj"])
    os.remove("strip.cpptraj")