import subprocess
import pandas as pd

paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"
solutemask = "@1-42"

limit = 5 #in angstroms

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
    with open('findions.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip :WAT\n")
        file.write("watershell " + solutemask + " out ionshell.dat" 
                   + " lower " + str(limit) + 
                   " upper " + str(limit) + " :Na+,Cl-\n")
        file.write("go")   
    
    #run cpptraj file to determine how many waters or ions within cutoff
    subprocess.run(["cpptraj","findions.cpptraj"])    
    
    df = pd.read_csv("ionshell.dat",sep='\s+',
                     names=['frame','firstshell','secondshell'],
                     skiprows=1)
    ionshell = df['firstshell'].values[0]
    print(ionshell)
    
    #create cpptraj file to create output with cutoff
    with open('closestion.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip :WAT\n")
        file.write("solvent :Na+,Cl-\n")
        file.write("closest " + str(ionshell) + " " + solutemask + 
                   " first " +"closestout ions.dat\n")
        file.write("trajout onlyions" + frametrajfile + ".pdb pdb nobox\n")
        file.write("go")

    subprocess.run(["cpptraj","closestion.cpptraj"])
    
    df = pd.read_csv("ions.dat",sep='\s+',
                     names=['frame','mol','dist','atom'],
                     skiprows=1)
    ions = ','.join(map(str, df['atom'].values))
    newmask = solutemask + "," + ions
    print(newmask)   
    
    #create cpptraj file to determine how many molecules within cutoff
    with open('watershell.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("watershell " + newmask + " out watershell.dat" 
                   + " lower " + str(limit)
                   + " upper " + str(limit) +"\n")
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
        file.write("closest " + str(firstshell) + " " + newmask + " first "
                   "outprefix closest\n")
        file.write("strip :Na+,Cl-&!@" + ions+ "\n")
        file.write("trajout " + frametrajfile + ".pdb pdb nobox\n")
        file.write("trajout " + frametrajfile + ".xyz xyz nobox\n")
        file.write("go")

    subprocess.run(["cpptraj","closest.cpptraj"])
    

        

