import subprocess
import os
import pandas as pd
import shutil


#name for outputfiles (will automatically append frame number and file extension)
outputname = 'prodimagedi.exp4a.pc8a.LRve'

paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"
solutemask = "@1-42"

#in angstroms
limit_iontosolute = 4 #threshold distance from solute to keep ions
limit_solventtoion = 4 #threshold distance to an ion to keep waters
limit_solventtosolute = 4 #threshold distance to the solute to keep waters

limit_pointcharges = 8 #threshold distance from solute to keep ions

#select frames
frames = [100,1000]

def determineCharge(atom):
    if atom == 'H':
        return 0.41
    if atom == 'O':
        return -0.82
    if atom == 'Na':
        return 1
    if atom == 'Cl':
        return -1

#nothing to edit below here
strlimitits = str(round(limit_iontosolute,1))
strlimitsti = str(round(limit_solventtoion,1))
strlimitsts = str(round(limit_solventtosolute,1))
strlimitpc = str(round(limit_pointcharges,1))


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

    #create cpptraj file to do mask for molecules that will become point charges
    with open('pointcharges.cpptraj', 'w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("reference " + frametrajfile + "\n")
        file.write("trajin " + frametrajfile + "\n")
        file.write("strip !(@1-42<^"+ strlimitpc + ")\n")
        file.write("trajout pointcharges" + frametrajfile[4:][:-4] + ".xyz xyz nobox\n")
        file.write("go")   
    
    #run cpptraj file and delete into
    subprocess.run(["cpptraj","pointcharges.cpptraj"])
    os.remove("pointcharges.cpptraj")
    


filelist = []
#iterate through each file
for i in frames:
    #assemble input and output file names for explicit file
    expfilename = "strippedframe." + str(i)
    expfilexyz = expfilename + ".xyz"
    expfilegjf = expfilename + ".gjf"    
    #convert the file
    subprocess.run(["ase","convert","-i","xyz","-o","gaussian-in",expfilexyz,expfilegjf])
    
    #assemble input and output file names for pc file
    pcfilename = "pointchargesframe." + str(i)
    pcfilexyz = pcfilename + ".xyz"
    pcfilegjf = pcfilename + ".gjf"    
    #convert the file
    subprocess.run(["ase","convert","-i","xyz","-o","gaussian-in",pcfilexyz,pcfilegjf])

    
    #remove all lines in the pointcharge file that match one in the explict file
    with open(expfilegjf,'r') as expfile:
        explines = set(expfile.readlines())
    with open(pcfilegjf,'r') as pcfile:
        pclines = set(pcfile.readlines())
    filteredlines = pclines - explines
    with open(pcfilegjf,'w') as outputfile:
        outputfile.writelines(filteredlines)

    #read in the explicit file
    with open(expfilegjf,'r') as file:
        lines = file.readlines()
        
    #find the line before the coordinates start    
    index_zero = next((i for i, line in enumerate(lines) if line.startswith('0')), None)
    if index_zero is not None:
        lines_until_zero = index_zero
    
    #read in the coordinates
    df = pd.read_csv(expfilegjf, sep='\s+',skiprows = index_zero+1,names = ['atoms','x','y','z'])
    
    #calculate the charge
    count_na = (df['atoms'] == 'Na').sum()
    count_cl = (df['atoms'] == 'Cl').sum()
    charge = count_na-count_cl
    
    #delete the explicit gjf
    if os.path.exists(expfilegjf):
        os.remove(expfilegjf)
        
    #create output gjf
    outputfilename = outputname + "." + str(i) + ".gjf"
    filelist.append(outputfilename)
    
    #create header
    with open(outputfilename,'w') as file:
        file.write('%NProcShared=16\n')
        file.write('%Mem=64GB\n')
        file.write('%chk=' + outputfilename[:-4] + '.chk\n')
        file.write('#p td(50-50,nstates=6) charge cam-b3lyp/aug-cc-pvdz int=(ultrafine,acc2e=12)\n')
        file.write('\n')
        file.write('vertical excitation with LR\n')
        file.write('\n')
        file.write(str(charge) + " " + "1\n")
    #append coordinates
    df.to_csv(outputfilename, sep= ' ',index=False,mode='a',
              header=False,float_format='%.8f')
    #append empty line
    with open(outputfilename, 'a') as file:
        file.write('\n')

        
    #read in the coordinates of the charges
    df = pd.read_csv(pcfilegjf, sep='\s+',names = ['atoms','x','y','z'])
    
    #delete the point charge gjf
    if os.path.exists(pcfilegjf):
        os.remove(pcfilegjf)
    
    #add specified charges
    df['charge'] = df['atoms'].apply(determineCharge)
    
    #remove atom labales
    df.drop('atoms', axis=1, inplace=True)
    
    #append coordinates of charges to file
    df.to_csv(outputfilename, sep= ' ',index=False,mode='a',
              header=False,float_format='%.8f')
    
    #append empty lines
    with open(outputfilename, 'a') as file:
        file.write('\n')
        file.write('\n')
        file.write('\n')
    
for file in filelist:  
    dirname = file[:-4]
    dirname = os.path.join("LRve",dirname)
    
    #check if directory exists, if not, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    #move that file into directory
    shutil.move(file, os.path.join(dirname, file))   

    
