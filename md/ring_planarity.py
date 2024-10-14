import numpy as np
import sys
import pandas as pd

xyz_file_basename = 'prodimagedi.frame.'
frames = [100,1000]
output_file =' planarity_rmsd_0M.dat'

atoms = [9, 10, 11, 21, 22, 23]
#accounting for zero indexing in python
atom_indices =  [x - 1 for x in atoms]


rmsd = []
#iterate over each frame 
for frame in frames:
    #fullname of file of individual frames
    fullname = xyz_file_basename + str(frame) + '.xyz'
    #read in xyz file
    df = pd.read_csv(fullname,skiprows=2,names=['atom','x','y','z'],sep='\\s+')
    
    #filter out only specified atoms and put in numpy array
    df = df.loc[atom_indices]
    df = df.drop(columns = ['atom'])    
    frame_coords = df.to_numpy()
    
    
    #print(frame_coords)
    
    #Fit a plane to a set of points using Singular Value Decomposition (SVD).
    #Returns the normal vector and a point on the plane (centroid).   
    centroid = np.mean(frame_coords, axis=0)
    centered_coords = frame_coords - centroid
    _, _, vh = np.linalg.svd(centered_coords)
    normal = vh[-1]    
    distance = np.sum(np.sqrt(np.dot(frame_coords - centroid, normal)**2))    
    rmsd.append(distance)

print(rmsd)