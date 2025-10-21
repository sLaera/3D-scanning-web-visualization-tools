using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.Serialization;
using UnityEngine.Splines;
using Random = UnityEngine.Random;

public class Sensor : MonoBehaviour
{
    public SplineAnimate SplineAnimate;
    /// <summary>
    /// Scan resolution on x dimension
    /// </summary>
    private int RayRows = 5;
    /// <summary>
    /// Scan resolution on y dimension
    /// </summary>
    private int RayColumns = 5;
    /// <summary>
    /// Field of view in degree
    /// </summary>
    private float Fov = 90f;

    /// <summary>
    /// Move the sensor of this factor every scan. Value between 0 and 1
    /// </summary>
    private float MovementStep = 0.1f;

    public GameObject PointPrefab;
    public bool ShowDebugRaysGizmos = false;


    private float _rayDistance = 10f;
    private readonly List<(Vector3, Vector3)> _points = new List<(Vector3, Vector3)>();
    private readonly List<(Vector3, Vector3)> _noisyPoints = new List<(Vector3, Vector3)>();

    private readonly List<(Vector3, Vector3)> _singleFramePoints = new List<(Vector3, Vector3)>();
    private readonly List<(Vector3, Vector3)> _singleFrameNoisyPoints = new List<(Vector3, Vector3)>();

    private int _frameNumber = 0;
    private int _scanNumber = 0;
    private GameObject _pointGroup;

    // Start is called before the first frame update
    void Start()
    {
        SplineAnimate.Container.transform.localScale = Vector3.one * ArgsManager.PathScale;
        //Calculate the diameter of the spline circumference. This is the max length of a ray
        _rayDistance = SplineAnimate.Container.CalculateLength() / Mathf.PI + 5f;
        RayRows = ArgsManager.RayRows;
        RayColumns = ArgsManager.RayCol;
        Fov = ArgsManager.Fov;
        MovementStep = ArgsManager.SensorSpeed;
        Clean();
    }

    void Clean()
    {
        if (ArgsManager.RandomRotation)
        {
            // --- Rotate the sensor path randomly ---
            float randomX = Random.Range(0f, 360f);

            SplineAnimate.Container.gameObject.transform.rotation = Quaternion.Euler(randomX, 0, 0);
        }

        SplineAnimate.Restart(false);
        _scanNumber = 0;
        // remove previous points
        _points.Clear();
        _noisyPoints.Clear();
        _singleFramePoints.Clear();
        _singleFrameNoisyPoints.Clear();
        if (_pointGroup)
            Destroy(_pointGroup);
        _pointGroup = new GameObject("PointGroup") {
            transform = {
                position = ModelLoader.I.gameObject.transform.position, rotation = ModelLoader.I.gameObject.transform.rotation
            }
        };
    }

    public void StartNewScan()
    {
        Clean();
    }

    void Update()
    {
        if (SplineAnimate.ElapsedTime >= 1.0f)
        {
            _scanNumber++;
            if (_scanNumber >= ArgsManager.Rescans + 1)
            {
                //scan completed
                SaveOff();
                GameManager.I.StartNewScan();
                //gameObject.SetActive(false);
                return;
            }
            SplineAnimate.Container.transform.Rotate(new Vector3(1, 0, 0), ArgsManager.RotationForRescan);
            SplineAnimate.Restart(false);
        }
        ScanFrame();
        if (ArgsManager.SaveFrames)
            SaveFrame(_frameNumber);
        SplineAnimate.ElapsedTime += MovementStep;
        _frameNumber++;
    }

    void OnDrawGizmos()
    {
        if (ShowDebugRaysGizmos)
        {
            _rayDistance = SplineAnimate.Container.CalculateLength() / Mathf.PI + 0.5f;
            ScanFrame(true);
        }
    }

    /// <summary>
    /// Execute a scan of the portion of the model under the fov angle
    /// </summary>
    /// <param name="debugOnly"></param>
    private void ScanFrame(bool debugOnly = false)
    {
        _singleFramePoints.Clear();
        _singleFrameNoisyPoints.Clear();
        //angle between rays
        float horizontalStep = Fov / (RayColumns - 1f);
        float verticalStep = Fov / (RayRows - 1f);

        for (int i = 0; i < RayRows; i++)
        {
            for (int j = 0; j < RayColumns; j++)
            {
                // calculate the ray angle from the middle of the fov.
                float horizontalAngle = (j * horizontalStep) - (Fov / 2f);
                float verticalAngle = (i * verticalStep) - (Fov / 2f);

                // Direct the rays along the right vector of the object
                Quaternion rotation = transform.rotation * Quaternion.Euler(0, horizontalAngle, verticalAngle);
                Vector3 direction = rotation * Vector3.right;

                LaunchRay(direction, debugOnly);
            }
        }
    }

    void LaunchRay(Vector3 direction, bool debugOnly = false)
    {
        Debug.DrawRay(transform.position, direction * _rayDistance, new Color32(255, 0, 0, 28));

        if (debugOnly)
            return;

        Ray ray = new Ray(transform.position, direction);
        if (Physics.Raycast(ray, out var hit, _rayDistance))
        {
            var point = (hit.point * 0.1f, hit.normal);
            _points.Add(point); //save the point and scale down to match with the original dimension
            _singleFramePoints.Add(point);
            var position = point.Item1;
            var normal = point.Item2;

            if (Random.value > ArgsManager.OutlierProbability)
            {
                //Deviation of the noise is the deviation + the distance normalized to 1 * amplitude
                var noise = Utils.GenerateNoiseInDirection(direction, ArgsManager.GaussianNoise * 0.1f + hit.distance * 0.01f * ArgsManager.DistanceNoiseAmplitude);
                position += noise;

                var normalNoise = Utils.GenerateGaussianNoise(ArgsManager.GaussianNoise);
                normal += normalNoise;
                normal.Normalize();
            }
            else
            {
                //This is an outlier
                position = Utils.GenerateRandomVector3(-0.5f, 0.5f);
            }
            _noisyPoints.Add((position, normal));
            _singleFrameNoisyPoints.Add((position, normal));
            //Show point in space. Only a max of 500 points per scan are visualized
            if (Random.value > 1f - (500f / (RayRows * RayColumns)))
            {
                Instantiate(PointPrefab, position * 10f, Quaternion.LookRotation(normal), _pointGroup.transform);
            }
        }
    }

    private void SaveOff()
    {
        var filePath = Path.Combine(ArgsManager.OutDir, GameManager.I.CurrentModel.Item2, "scan.off");
        Utils.SaveOffFile(filePath, _points);

        filePath = Path.Combine(ArgsManager.OutDir, GameManager.I.CurrentModel.Item2, "scan_noisy.off");
        Utils.SaveOffFile(filePath, _noisyPoints);
    }

    private void SaveFrame(int i)
    {
        var filePath = Path.Combine(ArgsManager.OutDir, GameManager.I.CurrentModel.Item2, "frames", $"{i}.off");
        Utils.SaveOffFile(filePath, _singleFramePoints);

        filePath = Path.Combine(ArgsManager.OutDir, GameManager.I.CurrentModel.Item2, "frames", $"{i}_noisy.off");
        Utils.SaveOffFile(filePath, _singleFrameNoisyPoints);
    }
}
