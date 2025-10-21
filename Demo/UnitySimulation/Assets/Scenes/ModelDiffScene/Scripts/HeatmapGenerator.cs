using System;
using UnityEngine;

namespace Scenes.ModelDiffScene.Scripts
{
    public class HeatmapGenerator : MonoBehaviour
    {
        [Header("Material")]
        public Material material;

        [Header("Input Textures")]
        public Texture2D pointsTex;
        public Texture2D positionsTex;

        public GameObject SourceMesh;

        [Header("Parameters")]
        public int radiusSearch = 8;

        [Header("Output")]
        public RenderTexture resultTexture;


        void OnGUI()
        {
            // Mostra la texture finale nella GUI
            GUI.DrawTexture(new Rect(10, 10, 512, 512), resultTexture);
        }

        void Start()
        {
            Camera.main.depthTextureMode = DepthTextureMode.Depth;
            Setup();
        }

        private void Update()
        {
            if (Input.GetKeyDown("space"))
            {
                resultTexture?.Release();
                Setup();
            }
        }

        void Setup()
        {
            // Set static uniforms
            material.SetTexture("_PointsTex", pointsTex);
            material.SetTexture("_Positions", positionsTex);
            material.SetVector("_Resolution", new Vector2(pointsTex.width, pointsTex.height));

            material.SetInt("_RadiusSearch", radiusSearch);

            var mesh = SourceMesh.GetComponentInChildren<MeshFilter>().mesh;
            Vector2[] uv = mesh.uv;

            //------convert uvs in texture and pass as texture------
            int uvCount = uv.Length;
            int texWidth = Mathf.NextPowerOfTwo(Mathf.CeilToInt(Mathf.Sqrt(uvCount)));
            int texHeight = Mathf.CeilToInt((float)uvCount / texWidth);

            Texture2D uvTex = new Texture2D(texWidth, texHeight, TextureFormat.RGFloat, false);

            for (int i = 0; i < uvCount; i++)
            {
                int x = i % texWidth;
                int y = i / texWidth;
                uvTex.SetPixel(x, y, new Color(uv[i].x, uv[i].y, 0));
            }
            uvTex.Apply();

            material.SetTexture("_UVTex", uvTex);
            material.SetInt("_UV_length", uvCount);
            material.SetVector("_UVTexSize", new Vector2(texWidth, texHeight));
            //--------------------------------------------------------------

            // Prepare output RenderTexture
            resultTexture = new RenderTexture(pointsTex.width, pointsTex.height, 0, RenderTextureFormat.ARGB32) {
                enableRandomWrite = false
            };
            resultTexture.Create();

            // Perform the blit
            Graphics.Blit(null, resultTexture, material);

            SourceMesh.GetComponentInChildren<MeshRenderer>().material.mainTexture = resultTexture;
        }

        private void OnDestroy()
        {
            resultTexture?.Release();
        }
    }
}
