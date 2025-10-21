# **Benchmark for synthetic LiDAR scanning and evaluating surface reconstruction algorithms for a custom dataset**
This project provides a framework to perform synthetic LiDAR scanning as well as performing evaluation and parameter tuning for well known surface reconstruction algorithms. 

This project is based on the following repositories:
- [dsr-bechmark](https://github.com/raphaelsulzer/dsr-benchmark)
- [mesh-tools](https://github.com/raphaelsulzer/mesh-tools)
- [PoissonRecon](https://github.com/mkazhdan/PoissonRecon)
- [Labatut reconstruction](https://github.com/fwilliams/surface-reconstruction-benchmark)

You can find more information in the `externals` and `dsr-benchmark` folder.

# Project structure
 - `classes`: necessary classes
    - BaseDataset.py: Base class from which dataset classes are built upon
 - dataset: Dataset files used to run tests
 - dsr-benchmark: library used to run tests
 - externals: remesh algorithms are here
 - test: Script to run test to check correct installation
 - results for default dataset: Pre computed results for the dataset
    - Best params: parameter for all tests and algorithm
    - images: images of reconstructed meshes
    - best params spsr.txt: Recommended params for screened poisson reconstruction
    - merged_results.csv: Result report
    - Time_results.json: Execution times


# Installation
The following installation steps are tested on Ubuntu

## Setup lidar scanning

Copy the content of `SyntheticLidarScanning` folder into the `MeshReconstructionBenchmark\externals\synthetic-lidar-unity` folder.

Open the project with Unity and build it for Linux (if using Linux - recommended) in the folder Build

## Install conda (Do if not already installed)
``` shell
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda-installer.sh
bash /opt/miniconda-installer.sh
rm /opt/miniconda-installer.sh
```
Now to test if the installation is correct, you should see a miniconda3 folder (or any other *conda named folder)

```sh
ls /opt | grep conda
```
Check if exists a bin folder in the miniconda (or any other *conda named folder) folder. 

Run the following command. Replace `miniconda3` if needed accordingly to what folder you found before
```sh
ls /opt/miniconda3/bin | grep conda #you should see conda listed
```

Add conda to Path:

Add at the end of fie `export PATH=/opt/miniconda3/bin:$PATH` (miniconda3/bin should be the name of the folder found in the previous steps)
```sh
nano ~/.bashrc #save with CTRL + O    exit with CTRL + x
source ~/.bashrc

conda info
```

Activate conda
``` sh
source /opt/miniconda3/bin/activate
conda init
```

Now close and reopen shell
<!-- 
## Clone repos
``` shell
git clone https://github.com/raphaelsulzer/dsr-benchmark.git
cd dsr-benchmark
git clone https://github.com/raphaelsulzer/mesh-tools.git
cd ..
``` -->
## Install mesh tool
Make sure to have g++ or Clang installed. Otherwise install it with 
```sudo apt install -y g++ && sudo apt install -y clang```

```shell
conda update -n base conda
#conda install -n base conda-libmamba-solver
#conda config --set solver libmamba
#---------- install dependencies---------
sudo apt install -y cmake
sudo apt install -y libboost-all-dev
sudo apt install -y zlib1g
sudo apt install -y libeigen3-dev

conda create -y --name xtensor python=3.10.10
conda activate xtensor
conda install conda-forge::xtensor
conda install conda-forge::xtensor-io

sudo apt-get install libgmp-dev libmpfr-dev

#--install CGAL--
sudo wget https://github.com/CGAL/cgal/releases/download/v6.0.1/CGAL-6.0.1.tar.xz -O /opt/CGAL-6.0.1.tar.xz
sudo tar xf /opt/CGAL-6.0.1.tar.xz -C /opt
(cd /opt/CGAL-6.0.1 && sudo cmake . -DCMAKE_BUILD_TYPE=RELEASE)
(cd /opt/CGAL-6.0.1 && sudo make install)
sudo rm /opt/CGAL-6.0.1.tar.xz
#----------------------------------------

cd externals/mesh-tools
mkdir build/release && cd build/release
cmake ../.. -DCMAKE_BUILD_TYPE=RELEASE
make -j

conda deactivate
```

## Install dsr benchmark
```sh
cd dsr-benchmark
conda init
chmod 755 install.sh
conda deactivate
./install.sh #this will require quite few minutes
pip install numpy==1.20.0 #downgrade for open3d
pip install pymeshlab
```

Restart the shell and check if everything is installed correctly
```shell
conda activate dsr

conda info --env #dsr should be active
python --version #should be 3.10.10
```
In Visual studio code set the python interpreter (Restart Visual studio before doing this steps):
* in console type `conda info --env` and then copy the env path of the dsr env
* press `ctrl` + `shift` + `p` in visual studio code and search python: interpreter
* paste the path to the conda env (if not already present in the submenu)

If you have multiple activations like `(base)(dsr)` you should run:
```sh
conda config --set auto_activate_base false
```
and restart the console
## Activate environment
Before run any script activate dsr environment
``` sh
conda activate dsr
```

## Test dsr-benchmark Installation
``` sh
python test.py benchmark
```

# Install and test remeshing algorithms
The methods for installing the various models used in the analysis are listed below.

To perform the tests, you can use the `test.py` script (as described method by method).

## Install SPSR
Install dependencies
```sh
sudo apt-get install -y libjpeg-dev
sudo apt-get install -y libpng-dev
sudo apt-get install -y libboost-dev
sudo apt install -y libboost-system-dev
```
Build poisson

```sh
cd externals/PoissonRecon
make -j 4
```
### Test screenedPoisson Installation
``` sh
python test.py spsr
```

## Install RESR
The RESR should be already installed by mesh'tools with the name of Labatut.

Check if the file labatut exists
``` sh
ls -l externals/mesh-tools/build/release/ | grep labatut
```
### Test Labatut Installation
``` sh
python test.py resr
```

## Install Advancing front and scale space surface reconstruction
CGAL is used to perform mesh reconstruction whit the advancing front and scale space algorithms.
This functions are implemented inside a c++ file under `externals/cgal-reconstruction` folder.

Firstly follow the instruction described in the previous chapters to install CGAL.

Then build the project
``` sh
cd externals/cgal-reconstruction
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=RELEASE
make
```

## Test all installations
Alternatively, you can test all the methods by:
``` sh
python test.py all
```

<details>
<summary>Install IGR <b>Unused</b> </summary>

Install dependencies
``` sh
cd externals
git clone https://github.com/amosgropp/IGR.git
pip install pyhocon plotly scikit-image trimesh
```
</details>


# Default Dataset
<!-- TODO: edit description -->
Default dataset is made of satellite ESA models.
The raw model is imported in Blender, positioned in the center of the scene and a remesh and decimate modifier is applied. After that is exported in off format with meshLab. This procedure create a single mesh with less than 100.000 vertices

The Dataset is composed of:
* .off files: model files cleaned up with Blender.
* classes.lst: the list with the names of the models (the name of the model matches the name of the file without the extension)
## Synthetic range scanning using Lidar simulation
``` sh
python scan_default_dataset.py
```

<div style="border: 1px solid #ddd; border-radius: 8px; padding: 8px; width: 100%; margin-bottom:8px">
  <div>
    <strong> <span style="font-size: 24px; margin-left: 8px; margin-right: 16px;">ℹ️</span> Models dimensions</strong>
    <p style="margin: 4px 0; padding: 0 8px;">Models' dimensions are normalized so that they are contained in the unit cube. They are then scaled up by 10 to match Unity dimensions</p>
  </div>
</div>
Point cloud are generated from a simulation of a lidar sensor using estimated parameters to achieve close to real results.

* *Parameters for simulations are set in `BaseDataset.py` line 434 (in `scan_lidar` function)*

  <details>
  <summary>Code snippet of the simulation's configurations</summary>

  ``` py
  # Models are scaled by 10 to match Unity dimensions
          # 1 unit = 2 m if the satellite is 2m large
          command = [str(self.lidar_exe),
                    "-in_path", str(input_path),
                    "-out_dir", output_folder,
                    "-gaussian_noise", "0.003",  # <1cm -> 2m * 0.0003unit = 0.6 cm
                    "-distance_noise_amplitude", "0.001",  # <0.1% of distance
                    "-outlier_probability", "0.0",
                    "-random_rotation", "true",
                    "-save_frames", "false",
                    "-rescans", "4",
                    "-rotation_for_rescan", "5",
                    "-fov", "20",
                    "-ray_rows", "128",
                    "-ray_col", "128",
                    "-sensor_speed", "0.1", # it's the percentage of the path traveled from one frame to the other
                    "-path_scale", "50"  # 50m distance -> 100m diameter path -> 50 unit * 2 = 100m
                    ]
  ```
  </details>

Generate pointclouds based on the following configurations:
* "0": Original point cloud size
    * No noise
* "1": Simplified point cloud
    * gaussian noise
* "2": Original point cloud size
    * gaussian noise

<details>
  <summary>MVS and Range scanning using methods described in the <a href="https://arxiv.org/abs/2301.13656">paper</a> [DOESN'T WORK WITH NON MANIFOLDS]</summary>

<div style="border: 1px solid #ddd; border-radius: 8px; padding: 8px; width: 100%; margin-bottom:8px">
  <div>
    <strong> <span style="font-size: 24px; margin-left: 8px; margin-right: 16px;">⚠️</span> Doesn't work with non manifold</strong>
    <p style="margin: 4px 0; padding: 0 8px;">The methods described below don't work with non manifold meshes. Generally complex meshes rarely are manifold. For example the Satellite models provided by ESA they aren't in fact manifold</p>
  </div>
</div>

## Synthetic MVS scanning
``` sh
python scan_default_dataset.py --mvs 1 --lidar 0
```
This should produce the same scans described above

## Synthetic range scanning
**There's no automatic script for this. Follow the reconbench README directions to generate the scans**

Range scanning is performed using reconbench implementation 
<!-- TODO: add cite -->
### Install reconbench
See the repo for more details `https://github.com/fwilliams/surface-reconstruction-benchmark.git`

install dependencies
``` sh
sudo apt-get install libpng-dev
sudo apt-get install liblapack-dev
sudo apt-get install libblas-dev
sudo apt-get install ffmpeg
sudo apt-get install gnuplot
sudo apt-get install texlive-font-utils
sudo apt-get install cmake
sudo apt-get install openexr
sudo apt-get install libtiff-dev
sudo apt-get install libopenexr-dev
sudo apt-get install libsuitesparse-dev
sudo apt-get install mesa-common-dev
sudo apt-get install libgl1-mesa-dev libglu1-mesa-dev
```
Build
``` sh
cd externals/surface-reconstruction-benchmark
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j 4
```

</details>

# Benchmark dataset
This script evaluates and optimizes different 3D mesh reconstruction methods using various algorithms:

- Screened Poisson surface reconstruction (spsr) [https://dl.acm.org/doi/10.1145/2487228.2487237]
- Robust and efficient surface reconstruction
from range data (resr) [https://www.cs.jhu.edu/~misha/ReadingSeminar/Papers/Labatut09.pdf]
- Ball pivoting Algorithm (bpivot) [https://ieeexplore.ieee.org/document/817351]
- Advancing front surface reconstruction (advancing) [https://www.cs.jhu.edu/~misha/Fall13b/Papers/Cazals06.pdf] [https://doc.cgal.org/latest/Advancing_front_surface_reconstruction/index.html]
- Scale space surface reconstruction (scale_space) [https://doc.cgal.org/latest/Scale_space_reconstruction_3/index.html]

It provides a framework for unoptimized and optimized evaluations of these reconstruction methods, using grid search for parameter tuning.

⚠️ You must perform the scanning procedure beforehand

## Usage
``` sh
python bechmark_default.py --search_only=<true/false> --spsr=<true/false> --resr=<true/false> --bpivot=<true/false> --advancig=<true/false> --scale_space=<true/false> --all=<true/false>
```
### Options
- **General Options**:
  - `--search_only`  
    Skips unoptimized reconstruction and performs only grid search.  
    Default: `False`

  - `--all`  
    Performs evaluations for all reconstruction algorithms.  
    Default: `False`

- **Algorithm-Specific Options**:
  - `--spsr`  
    Enables evaluations for the SPSR algorithm.  
    Default: `False`

  - `--resr`  
    Enables evaluations for the RESR algorithm.  
    Default: `False`

  - `--bpivot`  
    Enables evaluations for Ball Pivoting.  
    Default: `False`

  - `--advancing`  
    Enables evaluations for the Advancing Front algorithm.  
    Default: `False`

  - `--scale_space`  
    Enables evaluations for the Scale Space algorithm.  
    Default: `False`


### Examples
To perform evaluation for all the algorithms
``` sh
python bechmark_default.py --all=true
```

To perform only the grid search without evaluating the un-optimized methods
``` sh
python bechmark_default.py --search_only=true --all=true
```

To perform evaluation (un-optimized and optimized) for spsr only
``` sh
python bechmark_default.py --spsr=true
```

### Output

The script generates results in the following structure:

1. **Results Folder**:  
   The results for evaluations and optimizations are saved under the `results` directory inside the dataset folder.

2. **Files and folder description**:
   - `models`: Contains reconstructed models for both unoptimized and optimized runs.
   - `no_optimization.csv`: Metrics for unoptimized reconstruction.
   - `optimized.csv`: Metrics for optimized reconstruction.
   - `best_params_<method>_<config>.txt`: The best parameters found during grid search.

## Generate merged CSV
Each evaluation is saved in a different csv in a dedicated sub folder in the `result` folder.
To generate a merged csv with the combined results of each algorithm
``` sh
python generate_table.py
```
This will generate a merged CSV file with information of all the evaluations. The csv is saved in `results/merged_results.csv` 

## Calculate execution times
This script will generate a file in the result folder with execution times of the remesh methods
```sh
python exec_time_eval.py
``` 

# Create custom dataset
- Create a folder inside `dataset` folder with the name of the dataset
- Insert models in OFF file format
- Create a `classes.lst` file with the name of the models (model file name without extension)
  example :
  ``` lst
  model1
  model2
  model3
  ```
- Create a dataset class in `classes` folder as follow
  ``` python
  import sys
  import os
  from dsrb.eval import MeshEvaluator

  # fmt: off
  # yapf: disable
  sys.path.append(os.path.join(os.path.dirname(__file__), "."))
  from BaseDataset import BaseDataset
  # fmt: on
  # yapf: enable


  class CustomDataset(BaseDataset):
      def __init__(self, path=None, mesh_evaluator:MeshEvaluator = MeshEvaluator()):
          """Constructor of the Dataset Class

          Args:
              path (str, optional): Path of the dataset. Defaults to None.
              mesh_evaluator (MeshEvaluator, optional): Mesh evaluator object. Used for custom evaluation settings
          """
          super().__init__("dataset_folder", path, mesh_evaluator)
  ```
  Change `dataset_folder` accordingly to the dataset folder created before

- To use the `benchmark_default.py`, `exec_time_eval.py`, `generate_table.py` and `scan_default_dataset.py` scripts with the newly created dataset class, change the dataset initialization in the scripts:
  - In each script edit the line:
      ``` python
      ds = DefaultDataset( ... )
      ```
    With the above defined class. e.g:
      ```
      ds = CustomDataset( ... )
      ```
