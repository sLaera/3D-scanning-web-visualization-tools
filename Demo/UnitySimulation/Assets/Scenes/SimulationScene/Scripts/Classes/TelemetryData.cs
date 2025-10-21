using System;
using UnityEngine;

namespace Scenes.ModelDiffScene.Scripts.Classes
{
    [Serializable]
    public class TelemetryData
    {
        public Vector3 Position;
        public Vector3 Rotation;
        public float Timestamp;
        public bool ScanFrame;
        public Vector3 ArmJoint0Rotation;
        public Vector3 ArmJoint1Rotation;
    }
}
