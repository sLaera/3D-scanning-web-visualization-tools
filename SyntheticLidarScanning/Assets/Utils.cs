using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEngine;
using Random = UnityEngine.Random;

public class Utils
{
    /// <summary>
    /// Save point cloud in OFF format 
    /// </summary>
    /// <param name="filePath">Path of the file to save</param>
    /// <param name="points">List of points. Each point is a tuple of point position and normal vector</param>
    public static void SaveOffFile(string filePath, List<(Vector3, Vector3)> points)
    {
        //Create directory if needed
        string directoryPath = Path.GetDirectoryName(filePath);
        if (!Directory.Exists(directoryPath))
        {
            Directory.CreateDirectory(directoryPath ?? "./");
        }

        using (StreamWriter writer = new StreamWriter(filePath))
        {
            //NOFF FILE FORMAT:
            //NOFF
            //vertex_num, edges_num, faces_num
            //vertex_x, vertex_y,vertex_z norm_x,norm_y,norm_z
            writer.WriteLine("NOFF");
            writer.WriteLine($"{points.Count} 0 0");
            foreach (var (point, normal) in points)
            {
                writer.WriteLine($"{FormatFloat(point.x)} {FormatFloat(point.y)} {FormatFloat(point.z)} {FormatFloat(normal.x)} {FormatFloat(normal.y)} {FormatFloat(normal.z)}");
            }
        }

        Debug.Log($"OFF file saved: {filePath}");
    }

    /// <summary>
    /// Format float value according to OFF format
    /// </summary>
    /// <param name="value"></param>
    /// <returns></returns>
    public static string FormatFloat(float value)
    {
        //To save off value it need to be a 7-digit number excluding 0 value.
        //es:
        //1.729486  -> one unit followed by 6 decimals
        //0.6668437 -> no unit followed by 7 decimals
        int integerPart = (int)Math.Floor(Math.Abs(value));
        int integerDigits = integerPart > 0 ? integerPart.ToString().Length : 0;
        int decimalPlaces = 7 - integerDigits;

        string formatString = "F" + decimalPlaces;
        return value.ToString(formatString, CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// Read mesh names from .lst file
    /// </summary>
    /// <param name="filePath">path to the lst file</param>
    /// <returns>List of names</returns>
    public static List<string> ReadMeshNames(string filePath)
    {
        List<string> names = new List<string>();

        try
        {
            names = new List<string>(File.ReadAllLines(filePath));
        }
        catch (Exception ex)
        {
            Console.WriteLine("Reading lst file failed: " + ex.Message);
        }

        return names;
    }
    /// <summary>
    /// Box-Muller implementation of gaussian noise
    /// </summary>
    /// <returns></returns>
    public static float GaussianRandom(float standardDeviation, float mean)
    {
        float u1 = Random.value;
        float u2 = Random.value;
        float randStdNormal = Mathf.Sqrt(-2.0f * Mathf.Log(u1)) * Mathf.Sin(2.0f * Mathf.PI * u2);
        return mean + standardDeviation * randStdNormal;
    }

    /// <summary>
    /// Generate a Vector3 of noise 
    /// </summary>
    /// <param name="mean"></param>
    /// <param name="standardDeviation"></param>
    /// <returns></returns>
    public static Vector3 GenerateGaussianNoise(float standardDeviation, float mean = 0)
    {
        float offsetX = GaussianRandom(standardDeviation, mean);
        float offsetY = GaussianRandom(standardDeviation, mean);
        float offsetZ = GaussianRandom(standardDeviation, mean);
        return new Vector3(offsetX, offsetY, offsetZ);
    }

    public static Vector3 GenerateRandomVector3(float min, float max)
    {
        float x = Random.Range(min, max);
        float y = Random.Range(min, max);
        float z = Random.Range(min, max);

        return new Vector3(x, y, z);
    }

    public static Vector3 GenerateNoiseInDirection(Vector3 direction, float standardDeviation, float mean = 0)
    {
        Vector3 noiseVector = new Vector3(0, 0, GaussianRandom(standardDeviation, mean));
        Quaternion rotation = Quaternion.FromToRotation(Vector3.forward, direction);
        Vector3 rotatedNoise = rotation * noiseVector;
        return rotatedNoise;
    }
}
