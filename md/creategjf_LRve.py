import subprocess 
import pandas as pd
import os

### ENTER basename and frame numbers for existing xyz files
basename = "prodimaged_0m"
frames = [100,1000]

#iterate through each file
for i in frames:
    #assemble input and output file names
    filename = basename + ".frame." + str(i)
    filexyz = filename + ".xyz"
    filegjf = filename + ".gjf"
    
    #convert the file
    subprocess.run(["ase","convert","-i","xyz","-o","gaussian-in",filexyz,filegjf])

    #read in the file
    with open(filegjf,'r') as file:
        lines = file.readlines()
        
    #find the line before the coordinates start    
    index_zero = next((i for i, line in enumerate(lines) if line.startswith('0')), None)
    if index_zero is not None:
        lines_until_zero = index_zero
    
    #read in the coordinates
    df = pd.read_csv(filegjf, sep='\s+',skiprows = index_zero+1,names = ['atoms','x','y','z'])
    
    #calculate the charge
    count_na = (df['atoms'] == 'Na').sum()
    count_cl = (df['atoms'] == 'Cl').sum()
    charge = count_na-count_cl
    
    #delete the converted gjf
    if os.path.exists(filegjf):
        os.remove(filegjf)
        
    #create output gjf
    outputfilename = filename +'.LRve.gjf'
    #create header
    with open(outputfilename,'w') as file:
        file.write('%NProcShared=30\n')
        file.write('%Mem=50GB\n')
        file.write('%chk=' + outputfilename[:-4] + '.chk\n')
        file.write('#p td(50-50,nstates=6) cam-b3lyp/aug-cc-pvdz scrf=(smd,solvent=water) int=(ultrafine,acc2e=12)\n')
        file.write('\n')
        file.write('vertical excitation with LR\n')
        file.write('\n')
        file.write(str(charge) + " " + "1\n")
    #append coordinates
    df.to_csv(outputfilename, sep= ' ',index=False,mode='a',
              header=False,float_format='%.8f')
    #append empty spaces
    with open(outputfilename, 'a') as file:
        file.write('\n')
        file.write('\n')