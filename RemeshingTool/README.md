# Poisson Surface Reconstruction

## Overview

This project is composed of:

- A fork of [Screened Poisson Surface Reconstruction implementation](https://github.com/mkazhdan/PoissonRecon)
- A python script to handle execution of the reconstruction handling different input and output file types

## Python script for Mesh reconstruction

The Python script performs a remeshing on a given mesh file by Poisson surface reconstruction.
The final output is a reconstructed mesh saved in the specified format.

### Dependencies

Ensure that the following dependencies are installed before running the script:

- Python 3.x
- `pymeshlab` (for mesh processing)
- Poisson Recon (the installation is described in the next chapters)

Additionally, the Poisson reconstruction executable must be already compiled before executing the python script.

### Usage

The script is executed with the following required arguments:

```sh
python reconstruct.py [--poisson_recon_exe <path_to_poisson_exe>] --input <input_mesh> --out <output_mesh> --depth <depth_value> --bType <boundary_type>
```

### Arguments

- `--poisson_recon_exe`: Path to the Poisson reconstruction executable.
  If the argument is not provided the path will be `PoissonRecon/Bin/Linux` by default
- `--input`: Path to the input mesh file.
- `--out`: Path to save the output mesh file.
- `--depth`: Depth of the solver, affecting the quality of reconstruction (More details in the Poisson Recon README).
- `--bType`: Type of boundary constraints used in reconstruction (More details in the Poisson Recon README).

### Example

```sh
python reconstruct.py --poisson_recon_exe ./PoissonRecon/Bin/Linux --input model.obj --out output.obj --depth 8 --bType 2
```

This command reconstructs the surface of `model.obj` with a solver depth of 8 and boundary type 2, saving the final
result in `output.obj`.

### Notes

The script creates intermediate files, in the input and output directory, that should be automatically removed on script
competition.
Make sure to remove any temporary file if the script crashed beforehand.

## Installation - Docker

- A docker installation example is provided in the project README 

## Installation - Build Poisson recon locally

In order to make the python script work, the Poisson Recon should be compiled.
The compilation process described below is tested on Ubuntu:

- Install Dependencies:
    ```
  apt-get install -y libjpeg-dev libpng-dev libboost-dev libboost-system-dev make
  ```
- Compile:
    ```
  cd ./PoissonRecon
  make poissonrecon -j 3
  ```
  change `-j 3` base on the number of available threads. This could take up to 30 min
    - The compiled files should be available in the `./PoissonRecon/Bin/Linux` folder
