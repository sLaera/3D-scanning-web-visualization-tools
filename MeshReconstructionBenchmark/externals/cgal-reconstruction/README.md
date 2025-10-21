# Advancing front and scale space surface reconstruction by CGAL library
This project is composed of a single c++ file that perform a surface reconstruction of a given point cloud with Advancing front or scale space surface reconstruction algorithms.
Tested on Ubuntu 

## Requirements
- CGAL library installed (with proper configuration for your environment).
- A C++17-compliant compiler.

## Install on Ubuntu
1. Firs install CGAL and all the dependencies
``` sh
sudo apt install -y cmake
sudo apt install -y libboost-all-dev
sudo apt install -y libeigen3-dev

#--install CGAL--
sudo wget https://github.com/CGAL/cgal/releases/download/v6.0.1/CGAL-6.0.1.tar.xz -O /opt/CGAL-6.0.1.tar.xz
sudo tar xf /opt/CGAL-6.0.1.tar.xz -C /opt
(cd /opt/CGAL-6.0.1 && sudo cmake . -DCMAKE_BUILD_TYPE=RELEASE)
(cd /opt/CGAL-6.0.1 && sudo make install)
sudo rm /opt/CGAL-6.0.1.tar.xz
```
2. Build the project
``` sh
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE
make
```

## Usage
Run the program with the following syntax:
```bash
cd build
./Reconstruct -in <input_file> -out <output_file> -method <0 or 1> [options]
```

### Parameters
- **`-in`**: Path to the input point cloud file.
- **`-out`**: Path to the output file (the program appends `.off` to the path string).
- **`-method`**: Reconstruction method:
  - `0`: Advancing Front Surface Reconstruction.
  - `1`: Scale Space Surface Reconstruction.

### Optional Parameters
- **`-remove_outlier`**: Removes outlier points from the input.
- **`-apply_smooth`**: Applies jet smoothing to the input points.
- **Advancing Front Parameters**:
  - **`-radius_ratio_bound <value>`**: Radius ratio bound for the advancing front algorithm (default: `2.0`).
  - **`-beta <value>`**: Beta value for advancing front (default: `0.125`).
- **Scale Space Parameters**:
  - **`-maximum_facet_length <value>`**: Maximum facet length for meshing (default: `0.5`).
  - **`-iterations <value>`**: Number of smoothing iterations (default: `4`).

### Example Commands
#### Advancing Front Reconstruction:
```bash
cd build
./Reconstruct -in input.ply -out output -method 0 -radius_ratio_bound 2.0 -beta 0.125 -remove_outlier -apply_smooth
```

#### Scale Space Reconstruction:
```bash
cd build
./reconstruct -in input.ply -out output -method 1 -maximum_facet_length 0.5 -iterations 4
```

## Output
- The program outputs a surface mesh file in `.off` format.
- Errors during execution (e.g., file not found, invalid parameters) will be printed to `stderr`.

## Notes
For additional help, run:
```bash
./Reconstruct help
```