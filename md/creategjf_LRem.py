import subprocess 
import pandas as pd
import os
import shutil

### ENTER basename and frame numbers for existing xyz files
basename = "prodimaged_0m"
frames = [100,1000]

filelist = []
#iterate through each file
for i in frames:
    #assemble input and output file names
    filename = basename + ".frame." + str(i)
    filexyz = filename + ".xyz"
    filegjf = filename + ".gjf"
    
    #convert the file
    subprocess.run(["ase","convert","-i","xyz","-o","gaussian-in",filexyz,filegjf])

    #open it and read in all the lines
    with open(filegjf,'r') as file:
        lines = file.readlines()
        
    #find the line before the coordinates start    
    index_zero = next((i for i, line in enumerate(lines) if line.startswith('0')), None)
    if index_zero is not None:
        lines_until_zero = index_zero
    
    #read in the coordinates
    df = pd.read_csv(filegjf, sep='\\s+',skiprows = index_zero+1,names = ['atoms','x','y','z'])
    
    #calculate the charge from the positive and negative ions
    count_na = (df['atoms'] == 'Na').sum()
    count_cl = (df['atoms'] == 'Cl').sum()
    charge = count_na-count_cl
    
    #delete the converted gjf file
    if os.path.exists(filegjf):
        os.remove(filegjf)

    #create output file
    outputfilename = filename +'.LRem.gjf'
    filelist.append(outputfilename)
    #header
    with open(outputfilename,'w') as file:
        file.write('%NProcShared=30\n')
        file.write('%Mem=50GB\n')
        file.write('%chk=' + outputfilename[:-4] + '.chk\n')
        file.write('# td=(singlets,nstates=6,root=1) cam-b3lyp/aug-cc-pvdz scrf=(smd,solvent=water) int=(ultrafine,acc2e=12)\n')
        file.write('\n')
        file.write('vertical emission with LR\n')
        file.write('\n')
        file.write(str(charge) + " " + "1\n")
    #append coordinates
    df.to_csv(outputfilename, sep= ' ',index=False,mode='a',
              header=False,float_format='%.8f')
    #append empty lines
    with open(outputfilename, 'a') as file:
        file.write('\n')
        file.write('\n')
        
for file in filelist:  
    dirname = '.'.join(file.split(".")[:-2])
    dirname = os.path.join("LRem",dirname)
    
    #check if directory exists, if not, create it
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    #move that file into directory
    shutil.move(file, os.path.join(dirname, file))