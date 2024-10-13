import numpy as np
import sys

def fit_plane(coords):
    """
    Fit a plane to a set of points using Singular Value Decomposition (SVD).
    Returns the normal vector and a point on the plane (centroid).
    """
    centroid = np.mean(coords, axis=0)
    centered_coords = coords - centroid
    _, _, vh = np.linalg.svd(centered_coords)
    normal = vh[-1]
    return normal, centroid

def calculate_distance(points, normal, centroid):
    """
    Calculate the perpendicular distance from each point to the plane.
    """
    return np.dot(points - centroid, normal)

def parse_xyz(file_path, atom_indices):
    """
    Parse an XYZ file and yield coordinates for specified atoms for each frame.
    """
    n_atoms = len(atom_indices)
    with open(file_path, 'r') as f:
        while True:
            try:
                line = f.readline()
                if not line:
                    break  # End of file
                num_atoms = int(line.strip())
                if num_atoms < max(atom_indices):
                    raise ValueError(f"Expected at least {max(atom_indices)} atoms, but got {num_atoms}")

                comment = f.readline()

                frame_coords = []
                for i in range(num_atoms):
                    parts = f.readline().split()
                    if len(parts) < 4:
                        raise ValueError("Incorrect XYZ format.")
                    x, y, z = map(float, parts[1:4])
                    if i in atom_indices:
                        frame_coords.append([x, y, z])

                yield np.array(frame_coords)
            except Exception as e:
                print(f"Error parsing XYZ file: {e}")
                break

def main():
    if len(sys.argv) != 3:
        print("Usage: python calculate_planarity.py <input_xyz_file> <output_dat_file>")
        sys.exit(1)

    xyz_file = sys.argv[1]      # e.g., 'ring1_0M.xyz'
    output_file = sys.argv[2]   # e.g., 'planarity_rmsd_0M.dat'

    atom_indices = [8, 9, 10, 20, 21, 22]  # Adjusted for zero-based indexing

    with open(output_file, 'w') as out_f:
        out_f.write("#Frame Planarity_RMSD(Å)\n")
        for frame_number, coords in enumerate(parse_xyz(xyz_file, atom_indices)):
            normal, centroid = fit_plane(coords)
            distances = calculate_distance(coords, normal, centroid)
            rmsd = np.sqrt(np.mean(distances**2))
            out_f.write(f"{frame_number} {rmsd:.4f}\n")

    print(f"Planarity RMSD per frame has been written to {output_file}")

if __name__ == "__main__":
    main()
