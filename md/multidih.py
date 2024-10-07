import numpy as np

def generate_multidihedral_input(dihedrals, traj_file, parm_file, output_file="multidihedral_input.in"):
    """
    Generates a cpptraj input script for calculating multiple dihedral angles using multidihedral.

    Parameters:
    - dihedrals: List of tuples, where each tuple contains four atom indices for a dihedral angle.
    - traj_file: Path to the trajectory file.
    - parm_file: Path to the topology file.
    - output_file: Name of the cpptraj input file to generate (default is 'multidihedral_input.in').
    """
    with open(output_file, 'w') as f:
        # Load the topology file first
        f.write(f"parm {parm_file}\n")
        
        # Specify the trajectory
        f.write(f"trajin {traj_file}\n")  # Load all frames
        
        # Write dihedrals using the multidihedral command
        f.write("multidihedral ")
        for dihedral in dihedrals:
            atom_selection = f"@{dihedral[0]} @{dihedral[1]} @{dihedral[2]} @{dihedral[3]}"
            f.write(f"{atom_selection} ")  # Append atom selection for each dihedral
        
        f.write(f"out dihedral_angles.csv\n")  # Save results to CSV
        
        # Run the commands
        f.write("run\n")
    
    print(f"cpptraj input file '{output_file}' generated successfully.")
    print("Dihedral angles will be saved in 'multidihedral_angles.csv'.")

# Example usage 
if __name__ == "__main__":
    # Define the dihedrals for Nile Red using correct atom indices (ensure these are correct based on your topology)
    dihedrals = [
        (13, 14, 15, 16),  # Dihedral 1
        (20, 14, 15, 18),  # Dihedral 2
        (13, 14, 15, 18),  # Dihedral 3
        (20, 14, 15, 16)   # Dihedral 4
    ]
    
    # Specify your trajectory and topology files
    traj_file = "prod_gs_3m.dcd"  # Replace with your actual trajectory file (.dcd)
    parm_file = "solv.parm7"       # Replace with your actual topology file (.parm7)
    
    # Generate multidihedral input file
    generate_multidihedral_input(dihedrals, traj_file, parm_file)
