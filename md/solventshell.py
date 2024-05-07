import subprocess
import pandas as pd

paramfile = "solv.parm7"
trajfile = "prodimaged_0m.dcd"
solutemask = "@1-42"


filename_watershell = "watershell.dat"
limit = 4 #in angstroms

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
    
    #create cpptraj file to determine how many molecules within cutoff
    with open('watershell.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("watershell " + solutemask + " out watershell.dat" 
                   + " lower " + str(limit) +"\n")
        file.write("go")    
    
    #run cpptraj file to determine how many molecules within cutoff
    subprocess.run(["cpptraj","watershell.cpptraj"])
    
    df = pd.read_csv("watershell.dat",sep='\s+',
                     names=['frame','firstshell','secondshell'],
                     skiprows=1)
    firstshell = df['firstshell'].values[0]
    print(firstshell)
    
    #create cpptraj file to create output with cutoff
    with open('closest.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("closest " + str(firstshell) + " " + solutemask + " first "
                   "outprefix closest\n")
        file.write("trajout " + frametrajfile + ".pdb pdb nobox\n")
        file.write("go")

    subprocess.run(["cpptraj","closest.cpptraj"])

        

