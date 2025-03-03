import subprocess
import os
import pandas as pd
import numpy as np

#names of files
paramfile = "isolv.parm7"
trajfile = "prodimagedi.dcd"


#frames you are selecting
#selectedframes = np.arange(1,2500+1) #if doing for every frame
selectedframes = np.arange(25,2525,25)
masks = ["@1","@10","@15","@22"]

#closet X number of ions to consider
closestnum = 3


for mask in masks:
    #find closest 5 Na ions
    with open('closest.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        file.write("solvent :Na+\n")
        file.write("closest " + str(closestnum) + " " + mask + " closestout closestNa" + mask[1:] + "\n" )
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","closest.cpptraj"])
    os.remove("closest.cpptraj")
    
    #find closest 5 Cl ions
    with open('closest.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        file.write("solvent :Cl-\n")
        file.write("closest " + str(closestnum) + " " + mask + " closestout closestCl" + mask[1:] + "\n" )
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","closest.cpptraj"])
    os.remove("closest.cpptraj")


for mask in masks:
    df_Na = pd.read_csv("closestNa" + mask[1:], sep='\\s+')
    df_Na = df_Na.drop(columns =["CLOSEST_00001[FirstAtm]","CLOSEST_00001[Mol]"])
    df_Na = df_Na.rename(columns={'#CLOSEST_00001[Frame]': 'frame', "CLOSEST_00001[Dist]": 'distance_Na'})
    os.remove("closestNa" + mask[1:])
    
    df_Cl = pd.read_csv("closestCl" + mask[1:], sep='\\s+')
    df_Cl = df_Cl.drop(columns =["CLOSEST_00001[FirstAtm]","CLOSEST_00001[Mol]"])
    df_Cl = df_Cl.rename(columns={'#CLOSEST_00001[Frame]': 'frame', "CLOSEST_00001[Dist]": 'distance_Cl'})
    os.remove("closestCl" + mask[1:])
    
    df = df_Na
    df['distance_Cl'] = df_Cl['distance_Cl']
        
    #create closestion.csv
    df.to_csv("closestion" + mask[1:] + ".csv", sep= ',',index=False,float_format='%.8f')

#calculate fraction with ccip or ssip out of every frame
with open("ionpairsAll.txt", "w") as file:

    for mask in masks:
        line = 'Atom: ' + mask[1:] + '\n'
        file.write(line)
        df = pd.read_csv("closestion" + mask[1:] + ".csv")
        length = len(df)/closestnum
    
        na_CIP = len(df[df['distance_Na'] <= 3.0])
        na_SSIP = len(df[(df['distance_Na'] > 3.0) & (df['distance_Na'] <= 5.5)])
        
        cl_CIP = len(df[df['distance_Cl'] <= 3.0])
        cl_SSIP = len(df[(df['distance_Cl'] >= 3.0) & (df['distance_Cl'] <= 5.5)])
        
        line = 'Na+ CIP: ' + str(np.round(na_CIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Na+ SSIP: ' + str(np.round(na_SSIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Cl- CIP: ' + str(np.round(cl_CIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Cl- SSIP: ' + str(np.round(cl_SSIP/length*100,2)) + '%\n'
        file.write(line)

        file.write('\n')

#calculate fraction with ccip or ssip out of selected frames
with open("ionpairsSelected.txt", "w") as file:

    for mask in masks:
        line = 'Atom: ' + mask[1:] + '\n'
        file.write(line)
        df = pd.read_csv("closestion" + mask[1:] + ".csv")
        df = df[df['frame'].isin(selectedframes)]
        length = len(df)/closestnum
    
        na_CIP = len(df[df['distance_Na'] <= 3.0])
        na_SSIP = len(df[(df['distance_Na'] > 3.0) & (df['distance_Na'] <= 5.5)])
        
        cl_CIP = len(df[df['distance_Cl'] <= 3.0])
        cl_SSIP = len(df[(df['distance_Cl'] >= 3.0) & (df['distance_Cl'] <= 5.5)])
        
        line = 'Na+ CIP: ' + str(np.round(na_CIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Na+ SSIP: ' + str(np.round(na_SSIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Cl- CIP: ' + str(np.round(cl_CIP/length*100,2)) + '%\n'
        file.write(line)
        
        line = 'Cl- SSIP: ' + str(np.round(cl_SSIP/length*100,2)) + '%\n'
        file.write(line)

        file.write('\n')    
   
#create output to hold columns of number of sip and ccip for each frame
output_df = pd.DataFrame({'frame' : selectedframes})   
   
cutoff_cip = 3.0 #ang
cutoff_ssip = 5.5 #ang 


for mask in masks:
    #read in dataframe
    df = pd.read_csv("closestion" + mask[1:] + ".csv")
    
    output_df['cipNa' + mask[1:]] = None
    output_df['ssipNa' + mask[1:]] = None
    output_df['cipCl' + mask[1:]] = None
    output_df['ssipCl' + mask[1:]] = None
    
    #go through each frame and find lengths for that frame
    for frame in selectedframes:
        #take the subset that is just the frame under consideration
        subset = df[df['frame'] == frame]
        
        valuesNa = subset['distance_Na'].tolist()
        valuesCl = subset['distance_Cl'].tolist()       
        
        num_cipNa = sum(1 for x in valuesNa if x < cutoff_cip)
        num_cipCl = sum(1 for x in valuesCl if x < cutoff_cip)        
        
        num_ssipNa = sum(1 for x in valuesNa if cutoff_cip <= x < cutoff_ssip)
        num_ssipCl = sum(1 for x in valuesCl if cutoff_cip <= x < cutoff_ssip)
        
        output_df.loc[output_df['frame'] == frame,'cipNa' + mask[1:]] = num_cipNa
        output_df.loc[output_df['frame'] == frame,'ssipNa' + mask[1:]] = num_ssipNa
        output_df.loc[output_df['frame'] == frame,'cipCl' + mask[1:]] = num_cipCl
        output_df.loc[output_df['frame'] == frame,'ssipCl' + mask[1:]] = num_ssipCl
        
        #print(valuesNa)
        #print(num_cipNa)
        #print(num_ssipNa)
        
        #print(valuesCl)
        #print(num_cipCl)
        #print(num_ssipCl)
    
    os.remove("closestion" + mask[1:] + ".csv")
        
#create allionpairs.csv, only output selected frames
output_df.to_csv("allionpairs.csv", sep= ',',index=False,float_format='%.8f')
    

    
