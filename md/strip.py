import subprocess
import os

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
        file.write("strip !(@1-42<^"+ strlimitits + ")&:Na+,Cl-\n")
        file.write("trajout strippedstep1" + frametrajfile + ".xyz xyz nobox\n")
        file.write("go")   
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","strip.cpptraj"])
    os.remove("strip.cpptraj")
    
    #check if file has ions remaining to set correct mask (otherwise will fail)
    hasions = False
    with open("strippedstep1" + frametrajfile + ".xyz", 'r') as file:
        content = file.read()
        if "NA" in content or "CL" in content:
            hasions = True
            
    os.remove("strippedstep1" + frametrajfile + ".xyz")
    
    #repeat stripping with correct mask        
    with open('strip.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("reference " + frametrajfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip !(@1-42<^"+ strlimitits + ")&:Na+,Cl-\n")
        if hasions:
            file.write("strip !((@1-42<^" + strlimitsts + ")|(:Na+,Cl-<^"+ strlimitsti + "))\n")
        else:
            file.write("strip !(@1-42<^" + strlimitsts + ")\n")
        file.write("trajout stripped" + frametrajfile[4:][:-4] + ".xyz xyz nobox\n")
        file.write("go")   

    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","strip.cpptraj"])
    os.remove("strip.cpptraj")