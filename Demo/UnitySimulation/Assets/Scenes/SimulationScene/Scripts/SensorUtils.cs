using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEngine;
using Random = UnityEngine.Random;

namespace Scenes.ModelDiffScene.Scripts
{
    public class SensorUtils
    {

        /// <summary>
        /// generate a string of the point cloud in OFF format 
        /// </summary>
        /// <param name="points">List of points. Each point is a tuple of point position and normal vector</param>
        public static string CreateOffPoints(List<(Vector3, Vector3)> points)
        {
            var off = "";
            foreach (var (point, normal) in points)
            {
                off += $"{FormatFloat(point.x)} {FormatFloat(point.y)} {FormatFloat(point.z)} {FormatFloat(normal.x)} {FormatFloat(normal.y)} {FormatFloat(normal.z)} \n";
            }
            return off;
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
}
