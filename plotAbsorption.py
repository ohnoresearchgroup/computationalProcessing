import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def PlotAbsorption(filename):

    # find the beginning and end of the Excitation energies and oscillators strengths section
    with open(filename, 'r') as file:
        # Flag to indicate whether the desired line has been found
        found_desired_line = False
        
        # Read each line in the file and keep track of the line number
        for line_number, line in enumerate(file, start=1):
            # Check if the line contains the specified text
            if "Excitation energies and oscillator strengths:" in line:
                found_desired_line = True
                startline = line_number
            elif found_desired_line and line.startswith(" ****"):
                # Print the line number of the next line starting with ****
                endline = line_number
                break  # Exit the loop as the desired line has been found

    excitedStates = []
    # Open the file in read mode
    with open(filename, 'r') as file:
        # Read each line in the file and keep track of the line number
        for line_number, line in enumerate(file, start=1):
            # Check if the current line number is within the specified range
            if startline <= line_number <= endline:
                # Check if the line starts with "Excited State"
                if line.startswith(" Excited State"):
                    # Print or process the line as needed
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