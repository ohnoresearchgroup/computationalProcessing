import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def PlotAbsorption(filename):


    # Open the file in read mode
    targetstring = " Excitation energies and oscillator strengths:"
    linenumberlastexcitation = 0;
    with open(filename, 'r') as file:
        for linenumber, line in enumerate(file,1):
            if line.startswith(targetstring):
                linenumberlastexcitation = linenumber
                    
    #find each excited state    
    targetstring = " Excited State"
    excitedStates = []
    with open(filename, 'r') as file:
        for linenumber, line in enumerate(file,1):
            if linenumber < linenumberlastexcitation:
                continue
            if line.startswith(targetstring):                
                excitedStates.append(line.strip())

    

    column_names = ['Excited State', 'Quantum State',  'Energy', 'Wavelength', 'Oscillator Strength',  '<S**2>']
    df_es = pd.DataFrame(columns = column_names)
    for state in excitedStates:
        parts = state.split(' ')
        parts = [part.strip() for part in parts if part.strip()]
        new_row = {'Excited State': int(parts[2][:-1]), 'Quantum State': parts[3], 'Energy': float(parts[4]), 'Wavelength': float(parts[6]), 'Oscillator Strength': float(parts[8][2:]), '<S**2>': float(parts[9][7:])}
        new_row_df = pd.DataFrame([new_row])
        df_es = pd.concat([df_es, new_row_df], ignore_index=True)
    print(df_es)
        
    #print(df_es)
    df_es_nonzero = df_es[df_es['Oscillator Strength'] > 0]
    print(df_es_nonzero)

    wl = np.arange(300, 800, 1)
    ext = np.zeros(500)
    
    for index, row in df_es_nonzero.iterrows():
        wl0 = row['Wavelength']
        f = row['Oscillator Strength']
        thisosc = 1.3062974e8*f/(1e7/3099.6)*np.exp(-((1/wl -1/wl0)/(1/3099.6))**2)
        plt.figure()
        plt.plot(wl,thisosc)
        ext = ext + thisosc
    
    plt.figure()
    plt.plot(wl,ext)
    plt.xlabel('Wavelength [nm]')
    
    return [wl,ext]
