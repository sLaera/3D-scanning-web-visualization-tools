using System;
using System.Collections.Generic;
using System.IO;
using UnityCommandLineParser;
using UnityEngine;

public class CommandLineArguments
{
    public string OutputDir;
}

public class ArgsManager : MonoBehaviour
{
    public static ArgsManager I { get; private set; }
    
    [CommandLineArgument("out_dir", "Set the path of the output directory where to save the scans")]
    public static string OutDir;
    
    [CommandLineArgument("in_path", "Path to the lst file with the meshes names")]
    public static string InPath;
    /// <summary>
    /// Calculated dir path of InPath
    /// </summary>
    public static string InDir;
    
    [CommandLineArgument("save_frames", "Save point cloud of each frame of the scan procedure for each model ")]
    public static bool SaveFrames = true;
    
    [CommandLineArgument("random_rotation", "Rotate the sensor path to a random rotation")]
    public static bool RandomRotation = true;
    
    [CommandLineArgument("rescans", "Number of rescans")]
    public static int Rescans = 3;
    
    [CommandLineArgument("rotation_for_rescan", "Rotation in degree that is applied to the sensor path each rescan")]
    public static int RotationForRescan = 5;
    
    [CommandLineArgument("gaussian_noise", "Standard deviation of gaussian noise added to the scan points")]
    public static float GaussianNoise = 0.05f;
    
    [CommandLineArgument("distance_noise_amplitude", "Coefficient of amplitude added to the standard deviation of gaussian noise base on normalized distance: dev = dev + amp * dist")]
    public static float DistanceNoiseAmplitude = 0.05f;
    
    [CommandLineArgument("outlier_probability", "Probability that a point is an outlier")]
    public static float OutlierProbability = 0.01f;
    
    [CommandLineArgument("fov", "Field of view in degrees")]
    public static float Fov = 90f;
    
    [CommandLineArgument("ray_rows", "Number of rays per row")]
    public static int RayRows = 50;
    
    [CommandLineArgument("ray_col", "Number of rays per column")]
    public static int RayCol = 50;
    
    [CommandLineArgument("sensor_speed", "Speed of the sensor. Value Between 0 and 1. It's the percentage of the path tha the sensor is moved for every frame updater")]
    public static float SensorSpeed = 0.1f;
    
    [CommandLineArgument("path_scale", "Scale to the circular path of the sensor. scale = 1 gives a path of 1 in diameter")]
    public static float PathScale = 15f;
    
    private void Awake()
    {
        // If there is an instance, and it's not me, delete myself.

        if (I != null && I != this)
        {
            Destroy(this);
        }
        else
        {
            OutDir ??= Path.Combine(Application.streamingAssetsPath, "scans");
            InPath ??= Path.Combine(Application.streamingAssetsPath, "models", "list.lst");
            InDir = Path.GetDirectoryName(InPath);
            I = this;
        }
    }
}
