using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using Scenes.ModelDiffScene.Scripts;
using UnityEngine;
using UnityEngine.Serialization;
using Random = UnityEngine.Random;

public class Sensor : MonoBehaviour
{
    /// <summary>
    /// Scan resolution on x dimension
    /// </summary>
    public int RayRows = 128;
    /// <summary>
    /// Scan resolution on y dimension
    /// </summary>
    public int RayColumns = 128;
    /// <summary>
    /// Field of view in degree
    /// </summary>
    public float Fov = 20f;
    /// <summary>
    /// Percentage of outliers
    /// </summary>
    [Range(0f, 1f)]
    public float OutlierProbability = 0.001f;
    /// <summary>
    /// Standard deviation of gaussian noise used to perturb the point position
    /// </summary>
    public float BaseGaussianNoise = 0.01f; // 1cm
    /// <summary>
    /// Percentage of the distance added to the BaseGaussianNoise to calculate the standard deviation of the noise
    /// </summary>
    [Range(0f, 1f)]
    public float DistanceNoiseAmplitude = 0.001f; // 0.1% of distance

    /// <summary>
    /// Enable visual ray rendering
    /// </summary>
    public bool ShowRays = true;

    /// <summary>
    /// Material for the line renderers
    /// </summary>
    public Material RayMaterial;

    /// <summary>
    /// Width of the ray lines
    /// </summary>
    public float RayWidth = 0.01f;

    /// <summary>
    /// Color of the rays
    /// </summary>
    public Color RayColor = Color.red;

    /// <summary>
    /// Ray show time in seconds
    /// </summary>
    public float RayShowTime = 1f;

    /// <summary>
    /// Portion of actual rays that will be displayed
    /// </summary>
    [Range(0f, 1f)]
    public float VisualizedRayPercentage = 0.5f;

    private float _rayDistance = 300f;
    private readonly List<Vector3> _points = new List<Vector3>();
    private readonly List<Vector3> _normals = new List<Vector3>();
    private GameObject _rayGroup;
    private List<LineRenderer> _lineRenderers = new List<LineRenderer>();
    private float _lastScanningTimestamp = 0f;

    // Start is called before the first frame update
    void Start()
    {
        Clean();
        if (ShowRays)
        {
            InitLineRenderers();
        }
    }

    private void Update()
    {
        // if (Input.GetKeyDown(KeyCode.Space))
        // {
        //     ScanFrame();
        // }
        // if (Input.GetKeyUp("f"))
        // {
        //     GameManager.I.CompleteSimulation();
        // }

        //show ray for a limited amount of time
        if (Time.time - _lastScanningTimestamp > RayShowTime)
        {
            _rayGroup.SetActive(false);
        }
        else
        {
            //move ray to follow sensor
            foreach (var lineRenderer in _lineRenderers)
            {
                lineRenderer.SetPosition(0, transform.position);
            }
        }
    }

    public void Clean()
    {
        // remove previous points
        _points.Clear();
        _normals.Clear();
    }

    /// <summary>
    /// Execute a scan of the portion of the model under the fov angle
    /// </summary>
    /// <param name="debugOnly"></param>
    public void ScanFrame(bool debugOnly = false)
    {
        if (ShowRays)
        {
            _rayGroup.SetActive(true);
            _lastScanningTimestamp = Time.time;
        }

        //angle between rays
        float horizontalStep = Fov / (RayColumns - 1f);
        float verticalStep = Fov / (RayRows - 1f);

        var currentFramePoints = new List<(Vector3, Vector3)>();
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

                var point = LaunchRay(direction, i * RayRows + j, debugOnly);
                if (point != null)
                {
                    currentFramePoints.Add(point.Value);
                }
            }
        }
        if (currentFramePoints.Count > 0)
            GameManager.I.JsChannel.Publish("offFileSnippet", SensorUtils.CreateOffPoints(currentFramePoints));
    }

    (Vector3, Vector3)? LaunchRay(Vector3 direction, int rayIndex, bool debugOnly = false)
    {
        Debug.DrawRay(transform.position, direction * _rayDistance, new Color32(255, 0, 0, 28));

        Ray ray = new Ray(transform.position, direction);
        RaycastHit hit;
        bool didHit = Physics.Raycast(ray, out hit, _rayDistance);

        if (debugOnly)
            return null;

        // Create visual representation of the ray if enabled
        if (ShowRays && rayIndex % ((int)(1 / (VisualizedRayPercentage * VisualizedRayPercentage))) == 0)
        {
            //show only a percent of rays
            CreateRayVisual(direction, didHit, didHit ? hit.distance : _rayDistance, (int)(rayIndex * VisualizedRayPercentage * VisualizedRayPercentage));
        }

        if (!didHit)
            return null;

        var position = hit.point * 0.2f;
        var normal = hit.normal;

        if (Random.value > OutlierProbability)
        {
            //Deviation of the noise is the deviation + the distance normalized to 1 * amplitude
            var noise = SensorUtils.GenerateNoiseInDirection(direction, BaseGaussianNoise + hit.distance * DistanceNoiseAmplitude);
            position += noise;

            var normalNoise = SensorUtils.GenerateGaussianNoise(BaseGaussianNoise);
            normal += normalNoise;
            normal.Normalize();
        }
        else
        {
            //This is an outlier
            position = SensorUtils.GenerateRandomVector3(-0.5f, 0.5f);
        }
        _points.Add(position);
        _normals.Add(normal);
        return (position, normal);
    }

    private void InitLineRenderers()
    {
        _rayGroup = new GameObject("RayGroup");
        _rayGroup.transform.SetParent(transform);

        for (int i = 0; i < (int)RayRows * VisualizedRayPercentage; i++)
        {
            for (int j = 0; j < (int)RayColumns * VisualizedRayPercentage; j++)
            {
                GameObject rayObject = new GameObject("Ray");
                rayObject.transform.SetParent(_rayGroup.transform);

                LineRenderer lineRenderer = rayObject.AddComponent<LineRenderer>();
                // Set line renderer properties
                lineRenderer.material = RayMaterial ? RayMaterial : new Material(Shader.Find("Sprites/Default"));
                lineRenderer.startColor = RayColor;
                lineRenderer.endColor = RayColor;
                lineRenderer.positionCount = 2;

                lineRenderer.startWidth = 0;
                lineRenderer.endWidth = 0;
                lineRenderer.SetPosition(0, new Vector3(0, 0, 0));
                lineRenderer.SetPosition(1, new Vector3(0, 0, 0));

                _lineRenderers.Add(lineRenderer);
            }
        }
        _rayGroup.SetActive(false);
    }

    private void CreateRayVisual(Vector3 direction, bool didHit, float distance, int rayIndex)
    {
        if (rayIndex >= _lineRenderers.Count)
            return;

        var lineRenderer = _lineRenderers[rayIndex];

        if (!didHit)
        {
            lineRenderer.gameObject.SetActive(false);
            return;
        }
        lineRenderer.gameObject.SetActive(true);

        lineRenderer.startWidth = RayWidth;
        lineRenderer.endWidth = RayWidth;
        // Set line positions
        lineRenderer.SetPosition(0, transform.position);
        lineRenderer.SetPosition(1, transform.position + direction * distance);
    }

    public List<Vector3> GetPoints()
    {
        return _points;
    }

    public List<Vector3> GetNormals()
    {
        return _normals;
    }
}
