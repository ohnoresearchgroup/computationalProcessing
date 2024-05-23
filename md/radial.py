import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt


#paramfile = "isolv.parm7"
#trajfile = "prodimagedi.dcd"

paramfile = "solv.parm7"
trajfile = "prodimaged_0m.dcd"

ions = False

names = ["wholesolute","ocarbonyl","nring","oring","ndiethyl"]
masks = ["@1-42","@1","@10","@15","@22"]

for index, mask in enumerate(masks):
    #create cpptraj file to select certain frames and output as pdb
    with open('radial.cpptraj','w') as file:
        file.write("parm " + paramfile + "\n")
        file.write("trajin " + trajfile + "\n")
        if ions:
            file.write("radial out na.dat 0.1 15.0 " + mask + " :Na+\n")
            file.write("radial out cl.dat 0.1 15.0 " + mask + " :Cl-\n")
        file.write("radial out o.dat 0.1 15.0 " + mask + " !@1-42&@O\n")
        file.write("radial out h.dat 0.1 15.0 " + mask + " !@1-42&!@O\n")
        file.write("go")
    
    #run cpptraj file, then delete it
    subprocess.run(["cpptraj","radial.cpptraj"])
    os.remove("radial.cpptraj")
    
    df = pd.read_csv("o.dat", sep='\\s+',skiprows = 1, names = ['distance','o'])
    distance = df['distance']
    o = df['o']
    df = pd.read_csv("h.dat", sep='\\s+',skiprows = 1, names = ['distance','h'])
    h = df['h']
    
    os.remove('o.dat')
    os.remove('h.dat')
    
    if ions:
        df = pd.read_csv("na.dat", sep='\\s+',skiprows = 1, names = ['distance','na'])     
        na = df['na']
        df = pd.read_csv("cl.dat", sep='\\s+',skiprows = 1, names = ['distance','cl'])
        cl = df['cl']

        os.remove('na.dat')
        os.remove('cl.dat')

    if ions:
        result = pd.concat([distance,o,h,na,cl], axis=1)
    else:
        result = pd.concat([distance,o,h], axis=1)
    
    plt.figure()
    plt.plot(result['distance'],result['o'],label='o')
    plt.plot(result['distance'],result['h'],label='h')
    if ions:
        plt.plot(result['distance'],result['na'],label='na')
        plt.plot(result['distance'],result['cl'],label='cl')
    plt.legend()
    
    plt.savefig(names[index] + '.png',bbox_inches='tight')
    result.to_csv(names[index] + ".csv", sep= ',',index=False,float_format='%.8f')