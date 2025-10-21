using System;
using System.Collections;
using System.Collections.Generic;
using Scenes.ModelDiffScene.Scripts;
using Scenes.ModelDiffScene.Scripts.Classes;
using SharedScripts;
using UnityEngine;
using UnityEngine.UI;
using System.Threading.Tasks;
using SharedScripts.Classes;
using UnityEngine.Networking;
using UnityEngine.Serialization;

public class HeatmapVisualizer
{
    public static async Task VisualizeHeatmap(Texture2D pointsTexture, Texture2D  positionsTexture, GameObject sourceModel, GameObject targetModel, Material heatmapComputeMaterial)
    {
        //----Compute Heatmap Texture------
        //Create result texture
        heatmapTexture = new RenderTexture(pointsTexture.width / 4, pointsTexture.height / 4, 0, RenderTextureFormat.ARGBHalf);
        heatmapTexture.Create();

        //set shader parameters
        heatmapComputeMaterial.SetTexture("_PointsTex", pointsTexture);
        heatmapComputeMaterial.SetTexture("_Positions", positionsTexture);
        heatmapComputeMaterial.SetVector("_Resolution", new Vector2(pointsTexture.width, pointsTexture.height));
        heatmapComputeMaterial.SetInt("_RadiusSearch", 25);

        //---convert uvs in texture---
        var mesh = sourceModel.GetComponentInChildren<MeshFilter>().mesh;
        Vector2[] uv = mesh.uv;
        int uvCount = uv.Length;

        //create a texture sqrt(uvCount) x uvCount/sqrt(uvCount)
        int texWidth = Mathf.NextPowerOfTwo(Mathf.CeilToInt(Mathf.Sqrt(uvCount)));
        int texHeight = Mathf.CeilToInt((float)uvCount / texWidth);
        //texture 2 channels float
        Texture2D uvTex = new Texture2D(texWidth, texHeight, TextureFormat.RGFloat, false);
        for (int i = 0; i < uvCount; i++)
        {
            //uvs are stored in texture sequentially
            int x = i % texWidth;
            int y = i / texWidth;
            uvTex.SetPixel(x, y, new Color(uv[i].x, uv[i].y, 0));
        }
        uvTex.Apply();

        heatmapComputeMaterial.SetTexture("_UVTex", uvTex);
        heatmapComputeMaterial.SetInt("_UV_length", uvCount);
        heatmapComputeMaterial.SetVector("_UVTexSize", new Vector2(texWidth, texHeight));
        //------
        //create texture
        Graphics.Blit(null, heatmapTexture, heatmapComputeMaterial);
        //--------------------------------

        //---set property block for fill holes material---
        var propertyBlock = new MaterialPropertyBlock();
        propertyBlock.SetTexture("_MainTex", heatmapTexture);
        //------------

        var sourceMeshRenderer = sourceModel.GetComponentInChildren<MeshRenderer>();
        sourceMeshRenderer.material = FillHolesMaterial;
        sourceMeshRenderer.SetPropertyBlock(propertyBlock);

        //---Target Model---
        targetModel = await _loader.LoadFromUrl(dto.targetMesh);

        var targetMeshRenderer = targetModel.GetComponentInChildren<MeshRenderer>();
        targetMeshRenderer.material = TargetMaterial;
    }
}
