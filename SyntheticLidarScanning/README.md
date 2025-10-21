# Synthetic LiDAR Scanning in Unity

This Unity project simulates a synthetic LiDAR scanning process, with a customizable sensor and path. The simulation generates point cloud data from 3D models as the LiDAR sensor moves along a predefined path. This project is ideal for testing LiDAR-based algorithms and generating synthetic datasets.

---

## **Features**
1. **LiDAR Sensor Simulation**  
   A configurable LiDAR sensor capable of scanning 3D models and simulating realistic noise effects.

2. **Model Loader**  
   Automatically loads OBJ models from a specified directory for scanning. Models are defined in a `.lst` file.

3. **Customizable Sensor Path**  
   The sensor follows a circular path, with options for scaling, rotation, and multiple rescans.

4. **Output Data**  
   Generates and saves point clouds for scanned frames in the specified output directory.

---

## **Command-Line Arguments**
The project uses command-line arguments for easy configuration. Below are the supported arguments:

| **Argument**                | **Description**                                                                                           | **Default**                  |
|------------------------------|-----------------------------------------------------------------------------------------------------------|------------------------------|
| `out_dir`                   | Path to the directory where scans are saved.                                                              | `StreamingAssets/scans`      |
| `in_path`                   | Path to the `.lst` file containing model filenames.                                                       | `StreamingAssets/models/list.lst` |
| `save_frames`               | Save point clouds for each scan frame.                                                                | `true`                       |
| `random_rotation`           | Randomly rotate the sensor path.                                                                          | `true`                       |
| `rescans`                   | Number of rescans performed on the same model.                                                            | `3`                          |
| `rotation_for_rescan`       | Rotation (in degrees) applied to the sensor path for each rescan. To completely cover the model use a rotation of 45° with 4 or more rescans                                        | `5`                          |
| `gaussian_noise`            | Standard deviation of Gaussian noise added to scan points.                                                | `0.05`                       |
| `distance_noise_amplitude`  | Noise amplitude proportional to the distance of scan points.                                              | `0.05`                       |
| `outlier_probability`       | Probability of generating outlier points in the scan.                                                     | `0.01`                       |
| `fov`                       | Field of view of the sensor (degrees).                                                                    | `90`                         |
| `ray_rows`                  | Number of rays in each row of the LiDAR sensor.                                                             | `50`                         |
| `ray_col`                   | Number of rays in each column of the LiDAR sensor.                                                          | `50`                         |
| `sensor_speed`              | Speed of the sensor as a percentage of the path covered per frame update.                                 | `0.1`                        |
| `path_scale`                | Scale of the circular path (diameter = scale).                                                            | `15`                         |

---

## **Project Components**

### **1. LiDAR Sensor**
- Simulates a LiDAR sensor with configurable field of view, resolution, and noise characteristics.
- Generates point cloud data for each scan frame.

### **2. Model Loader**
- Reads the `.lst` file specified in `in_path` to load 3D models in OBJ format for scanning.
- Supports multiple models for batch processing.

### **3. Sensor Path**
- Follows a circular path by default, with options for scaling, rotation, and randomization.
- Configurable rescanning behavior for capturing multiple scans with variations.

---

## **Usage Instructions**

### **1. Set Up the Project**
- Open the project in Unity.
- Ensure the `StreamingAssets` folder contains the required models and a valid `.lst` file to test the project inside the Unity editor

### **2. Configure Parameters**
- Use the command-line arguments listed above to configure the sensor and scanning behavior.
- Example `.lst` file structure:
  ```txt
  model1.obj
  model2.obj
  model3.obj
  ```

### **3. Run the Simulation**
- Run the Unity project using the Unity Editor or build an executable for standalone use.
- Pass command-line arguments to the executable to customize the behavior.

**Example Command** (Standalone Executable):
```bash
MyLiDARProject.exe --out_dir="C:/scans" --in_path="C:/models/list.lst" --random_rotation=false --rescans=5
```

---

## **Output**
The simulation generates the following output in the specified `out_dir`:
1. **Point Cloud Files**:  
   Point cloud Saved in OFF formats. two set of point cloud is generated for each model. A ground truth one and a noisy one
2. **Organized Folders**:  
   Each scan session is composed of multiple frames. You can find all the OFF file in the frames subfolder

---
