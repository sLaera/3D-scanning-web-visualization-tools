using System;
using Plugin.JsChannel;
using Scenes.ModelDiffScene.Scripts.Classes;
using SharedScripts;
using UnityEngine;
using UnityEngine.Serialization;
using Random = UnityEngine.Random;

namespace Scenes.ModelDiffScene.Scripts
{
    public class GameManager : MonoBehaviour
    {
        public Sensor SensorObj;
        public Transform Servicer;
        public Transform Joint0;
        public Transform Joint1;
        public JsChannelBinding JsChannel;
        public PointCloudVisualizer PcdVisualizer;
        public ModelLoader ModelLoader;
        public OrbitalCamera Camera;

        private TelemetryData _currentData = null;
        private TelemetryData _prevData = null;
        private float _simulationTime = 0f;

        public static GameManager I { get; private set; }
        private void Awake()
        {
            if (I != null && I != this)
            {
                Debug.LogWarning("GameManager is a MonoBehaviour and there should be only one instance. Additional instances will be destroyed.");
                Destroy(this);
            }
            else
            {
                I = this;
            }

            JsChannel = new JsChannelBinding();
        }

        private void Start()
        {
            CleanUp();
            PcdVisualizer.gameObject.SetActive(false);
        }

        private void Update()
        {
            if (_prevData == null)
                return;
            
            Servicer.gameObject.SetActive(true);
            _simulationTime += Time.deltaTime;
            float t = (_simulationTime - _prevData.Timestamp) / (_currentData.Timestamp - _prevData.Timestamp);
            // t = Mathf.Clamp01(t);
            //interpolate position and rotation
            Servicer.position = Vector3.Lerp(_prevData.Position, _currentData.Position, t);
            Servicer.rotation = Quaternion.Slerp(Quaternion.Euler(_prevData.Rotation), Quaternion.Euler(_currentData.Rotation), t);
            Joint0.localRotation = Quaternion.Slerp(Quaternion.Euler(_prevData.ArmJoint0Rotation), Quaternion.Euler(_currentData.ArmJoint0Rotation), t);
            Joint1.localRotation = Quaternion.Slerp(Quaternion.Euler(_prevData.ArmJoint1Rotation), Quaternion.Euler(_currentData.ArmJoint1Rotation), t);
        }

        public void UpdateSimulation(string telemetryDataRaw)
        {
            //convert json to object
            var telemetryData = JsonUtility.FromJson<TelemetryData>(telemetryDataRaw);
            _prevData = _currentData;
            _currentData = telemetryData;

            if (_prevData != null)
            {
                Servicer.position = _prevData.Position;
                Servicer.rotation = Quaternion.Euler(_prevData.Rotation);
                Joint0.localRotation = Quaternion.Euler(_prevData.ArmJoint0Rotation);
                Joint1.localRotation = Quaternion.Euler(_prevData.ArmJoint1Rotation);
                if (_prevData.ScanFrame)
                {
                    SensorObj.ScanFrame();
                }
                _simulationTime = _prevData.Timestamp;
            }
        }

        public void CompleteSimulation()
        {
            JsChannel.Publish("createOffFile", SensorObj.GetPoints().Count);

            PcdVisualizer.Points = SensorObj.GetPoints();
            PcdVisualizer.Normals = SensorObj.GetNormals();
            PcdVisualizer.gameObject.SetActive(true);
            Camera.OrbitRadius = 15;
            
            CleanUp();
        }

        private void CleanUp()
        {
            // SensorObj.Clean();
            Servicer.gameObject.SetActive(false);
            ModelLoader.DestroyLoadedModel();
            _prevData = null;
            _currentData = null;
            _simulationTime = 0f;
        }
    }
}
