import subprocess 
import pandas as pd
import os



basename = "frame"

frames = [100,1000]

for i in frames:
    filename = basename + "." + str(i)
    filexyz = filename + ".xyz"
    filegjf = filename + ".gjf"
    subprocess.run(["ase","convert","-i","xyz","-o","gaussian-in",filexyz,filegjf])

    with open(filegjf,'r') as file:
        lines = file.readlines()
        
    index_zero = next((i for i, line in enumerate(lines) if line.startswith('0')), None)

    if index_zero is not None:
        lines_until_zero = index_zero  # Number of lines until the line starting with '0'
    
    df = pd.read_csv(filegjf, sep='\s+',skiprows = index_zero+1,names = ['atoms','x','y','z'])
    count_na = (df['atoms'] == 'Na').sum()
    count_cl = (df['atoms'] == 'Cl').sum()
    charge = count_na-count_cl
    print(charge)
    
    if os.path.exists(filegjf):
        os.remove(filegjf)

    outputfilename = 'absorption_'+ filename +'.gjf'
    with open(outputfilename,'w') as file:
        file.write('%nprocshared=40\n')
        file.write('%mem=60GB\n')
        file.write('%chk=esopt-wat.chk\n')
        file.write('#p td=(50-50,nstates=6) cam-b3lyp/aug-cc-pvdz scrf=(iefpcm,solvent=water)\n')
        file.write('\n')
        file.write('Absorption - water\n')
        file.write('\n')
        file.write(str(charge) + " " + "1\n")
    
    df.to_csv(outputfilename, sep= ' ',index=False,mode='a',
              header=False,float_format='%.8f')

    with open(outputfilename, 'a') as file:
        file.write('\n')
        file.write('\n')