using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Serialization;
using UnityEngine.UIElements;

namespace SharedScripts
{
    public class PointCloudVisualizer : MonoBehaviour
    {
        private static readonly int NormalNameID = Shader.PropertyToID("_Normal");
        private static readonly int ColorNameID = Shader.PropertyToID("_Color");
        private static readonly int PointScaleNameID = Shader.PropertyToID("_PointScale");
        
        public Mesh Mesh;
        public Material PointMaterial;
        public float PointSize = 1;
        public List<Vector3> Points;
        public List<Vector3> Normals;
        
        private CommandBuffer _commandBuffer;
        private Matrix4x4[] _matrices;

        void Start()
        {
            if (!SystemInfo.supportsInstancing)
            {
                Debug.LogError("GPU Instancing is not supported on this platform.");
                return;
            }
            
            var propertyBlock = new MaterialPropertyBlock();
            propertyBlock.SetVectorArray(NormalNameID, ConvertVector3ListToVector4List(Normals));
            
            _matrices = new Matrix4x4[Points.Count];
            for (int i = 0; i < Points.Count; i++)
            {
                Vector3 position = Points[i];
                _matrices[i] = Matrix4x4.TRS(position, Quaternion.identity, Vector3.one);
            }

            PointMaterial.SetFloat(PointScaleNameID, PointSize);
            _commandBuffer = new CommandBuffer { name = "Instanced Mesh Rendering" };
            _commandBuffer.DrawMeshInstanced(Mesh, 0, PointMaterial, 0, _matrices, Points.Count, propertyBlock);
        
            Camera.main?.AddCommandBuffer(CameraEvent.AfterForwardOpaque, _commandBuffer);
        }

        void OnDestroy()
        {
            if (_commandBuffer != null)
            {
                Camera.main?.RemoveCommandBuffer(CameraEvent.AfterForwardOpaque, _commandBuffer);
                _commandBuffer?.Release();
            }
        }
        
        List<Vector4> ConvertVector3ListToVector4List(List<Vector3> v3List, float w = 0f)
        {
            List<Vector4> result = new List<Vector4>();
        
            foreach (Vector3 v3 in v3List)
            {
                Vector4 v4 = new Vector4(v3.x, v3.y, v3.z, w);
                result.Add(v4);
            }
        
            return result;
        }
    }
}
