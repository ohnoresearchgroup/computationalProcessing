import subprocess
import pandas as pd

paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"
solutemask = "@1-42"

#in anstroms
limit_iontosolute = 4 #threshold distance from solute to keep ions
limit_solventtoion = 4 #threshold distance to an ion to keep waters
limit_solventtosolute = 4 #threshold distance to the solute to keep waters

strlimitits = str(round(limit_iontosolute,1))
strlimitsti = str(round(limit_solventtoion,1))
strlimitsts = str(round(limit_solventtosolute,1))

#select frames
frames = [100,1000]

with open('createframes.cpptraj','w') as file:
    file.write("parm " + paramfile + "\n")
    file.write("trajin " + trajfile + "\n")
    file.write("trajout frame pdb onlyframes " + 
               ','.join(map(str, frames)) + " multi\n")
    file.write("go")


subprocess.run(["cpptraj","createframes.cpptraj"])


for i in frames:
    #name of frame to examine
    frametrajfile = "frame." + str(i)
    
    #IONS
    #create cpptraj file to determine how many ions within cutoff
    with open('strip.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("reference " + frametrajfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip !(@1-42<^"+ strlimitits + ")&:Na+,Cl-\n")
        file.write("strip !((@1-42<^" + strlimitsts + ")|(:Na+,Cl-<^"+ strlimitsti + "))\n")
        file.write("trajout stripped" + frametrajfile + ".pdb pdb nobox\n")
        file.write("go")   
    
    #run cpptraj file to determine how many waters or ions within cutoff
    subprocess.run(["cpptraj","strip.cpptraj"])
