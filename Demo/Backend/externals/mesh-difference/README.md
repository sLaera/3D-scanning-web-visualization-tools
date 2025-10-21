# Mesh difference visualizer

The goal of this project is to visualize the difference between two meshes with a heatmap surface.
The mesh is visualized in Unity With the Heatmap shader.

These scripts will produce the necessary textures needed for the
shader to correctly visualize the heatmap.

In details, the script loads two meshes, samples them, calculates the Chamfer distance and computes a color value for
each distance.
Then two different textures are generated:

- Points: A dotted colored texture that represents each sampled point's color as a pixel in uv coordinate
- Positions: A dotted black and white texture that marks the position of the points in uv space

# Installation

- Install pipenv and create virtual environment
    ```sh
    pip install --user pipenv
    
    mkdir .venv
    pipenv shell
    ```
- Activate virtual environment
    ``` sh
    pipenv shell
    # or
    source .venv/Scripts/activate
    ```
- Install packages
    ```sh
    pipenv install
    ```

## Troubleshooting

If pipenv is not recognized as a command, set `Script` folder of python --user installation directory in path

es. in windows it could be something like `C:\Users\<username>\AppData\Roaming\Python\Python311\Scripts`

# Usage

## Command-line Arguments

The script requires specific arguments to be provided for execution. Below is a list of the available arguments:

| Argument                       | Type  | Description                                                                      |
|--------------------------------|-------|----------------------------------------------------------------------------------|
| `--source_path`                | str   | Path to the source mesh file.                                                    |
| `--target_path`                | str   | Path to the target mesh file.                                                    |
| `--texture_dim`                | int   | Dimension of the texture map.                                                    |
| `--samples`                    | int   | Number of sample points extracted from the mesh.                                 |
| `--icp`                        | flag  | Enables the ICP algorithm for alignment.                                         |
| `--simplify`                   | flag  | Enables mesh simplification.                                                     |
| `--use_brk`                    | flag  | Enables the use of breakpoints for distance-based colorization.                  |
| `--p_brk1, --p_brk2, --p_brk3` | float | Positive breakpoints for distance mapping. From smaller to larger                |
| `--n_brk1, --n_brk2, --n_brk3` | float | Negative breakpoints for distance mapping. From larger to smaller (es 0, -1, -2) |
| `--output_path_dir`            | str   | Directory to save output files. Use different output for different mesh pairs    |

### Cache

Results are cached as intermediate files.
Cache is used to avoid re-sampling or re-compute distances to optimize times.
Execute the script with different output paths for different meshes in order to make cache works properly

### Example Command

```sh
python script.py --source_path ./models/source.obj --target_path ./models/target.obj --texture_dim 1024 --samples 5000 --icp --simplify --output_path_dir ./output
```

# General script workflow

**Steps:**

1. Loads and optionally simplifies the source and target meshes.
2. Generates UV maps and saves intermediate processed meshes.
3. Samples points from the meshes and caches results.
4. If enabled, applies ICP for alignment.
5. Computes Chamfer distances and caches results.
6. Normalizes distances and applies colorization.
7. Generates textures and saves output files.

# Output Files

The script generates the following output files in the specified output directory:

- Output files
    - `source.obj`: Processed source mesh.
    - `target.obj`: Processed target mesh.
    - `points.png`: Dotted colored texture of mapped points.
    - `positions.png`: Dotted black and white texture of points positions.
    - `info.json`: JSON file with distance statistics.
- Cache files
    - `sampled_source.npz`: Sampled source mesh data.
    - `sampled_target.npz`: Sampled target mesh data.
    - `distances.npz`: Distance calculations.

# Notes

- The input and target meshes must be composed of a single triangular mesh.
  For best results, the mesh should be composed
  of only an outer shell (no inner parts).
  This could be achieved by, for example, the remesh modifier in Blender
- Mesh processing might be computationally intensive depending on input size.
- ICP alignment requires sufficient similarities between source and target meshes for accurate results.
  It can still produce incorrect results, sometimes; manual alignment is necessary in these cases.

