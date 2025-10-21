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

public class ModelDiffVisualizer : MonoBehaviour
{
    public OrbitalCamera Camera;
    public Image Spinner;
    public Material FillHolesMaterial;
    public Material TargetMaterial;
    public Material HeatmapComputeMaterial;

    public GameObject SourceModel { get; set; }
    public GameObject TargetModel { get; set; }

    private RuntimeLoader _loader;
    private RenderTexture _heatmapTexture;

    private void Start()
    {
        _loader = new RuntimeLoader();
        
        // var dummyLoad = @"{
        //     ""sourceMesh"": ""http://localhost:3000/difference/outputTarget/source.obj"",
        //     ""targetMesh"": ""http://localhost:3000/difference/outputTarget/target.obj"",
        //     ""pointsTexture"": ""http://localhost:3000/difference/outputTarget/points.png"",
        //     ""positionsTexture"": ""http://localhost:3000/difference/outputTarget/positions.png""
        // }";
        //
        // LoadModelsAndTextures(dummyLoad);
    }

    private void OnDestroy()
    {
        DestroyLoadedModels();
    }

    public void DestroyLoadedModels()
    {
        if (SourceModel)
        {
            Destroy(SourceModel);
        }

        if (TargetModel)
        {
            Destroy(TargetModel);
        }

        if (_heatmapTexture)
        {
            _heatmapTexture.Release();
        }
    }

    /**
     * Function called from js
     */
    public async Task LoadModelsAndTextures(string rawModelDiffDto)
    {
        Spinner.gameObject.SetActive(true);
        DestroyLoadedModels();
        try
        {
            var dto = JsonUtility.FromJson<ModelDiffDto>(rawModelDiffDto);
            //--Source Model---
            SourceModel = await _loader.LoadFromUrl(dto.sourceMesh);
            var pointsTexture = await _loader.LoadTexture(dto.pointsTexture);
            pointsTexture.filterMode = FilterMode.Point;
            var positionsTexture = await _loader.LoadTexture(dto.positionsTexture);
            positionsTexture.filterMode = FilterMode.Point;

            //----Compute Heatmap Texture------
            //Create result texture
            _heatmapTexture = new RenderTexture(pointsTexture.width / 4, pointsTexture.height / 4, 0, RenderTextureFormat.ARGBHalf);
            _heatmapTexture.Create();

            //set shader parameters
            HeatmapComputeMaterial.SetTexture("_PointsTex", pointsTexture);
            HeatmapComputeMaterial.SetTexture("_Positions", positionsTexture);
            HeatmapComputeMaterial.SetVector("_Resolution", new Vector2(pointsTexture.width, pointsTexture.height));
            HeatmapComputeMaterial.SetInt("_RadiusSearch", 25);

            //---convert uvs in texture---
            var mesh = SourceModel.GetComponentInChildren<MeshFilter>().mesh;
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

            HeatmapComputeMaterial.SetTexture("_UVTex", uvTex);
            HeatmapComputeMaterial.SetInt("_UV_length", uvCount);
            HeatmapComputeMaterial.SetVector("_UVTexSize", new Vector2(texWidth, texHeight));
            //------
            //create texture
            Graphics.Blit(null, _heatmapTexture, HeatmapComputeMaterial);
            //--------------------------------

            //---set property block for fill holes material---
            var propertyBlock = new MaterialPropertyBlock();
            propertyBlock.SetTexture("_MainTex", _heatmapTexture);
            //------------

            var sourceMeshRenderer = SourceModel.GetComponentInChildren<MeshRenderer>();
            sourceMeshRenderer.material = FillHolesMaterial;
            sourceMeshRenderer.SetPropertyBlock(propertyBlock);

            //---Target Model---
            TargetModel = await _loader.LoadFromUrl(dto.targetMesh);
            Camera.LookAt = SourceModel.transform;

            var targetMeshRenderer = TargetModel.GetComponentInChildren<MeshRenderer>();
            targetMeshRenderer.material = TargetMaterial;
        }
        catch (Exception e)
        {
            Debug.LogError(e.Message + "\n" + e.StackTrace);
        }
        finally
        {
            Spinner.gameObject.SetActive(false);
        }
    }

    private void MakeTargetSolid()
    {
        if (!SourceModel.gameObject.activeSelf)
        {
            //if there is no source, make target solid
            var newMaterial = new Material(Shader.Find("Standard (Specular setup)"));
            TargetModel.GetComponentInChildren<MeshRenderer>().material = newMaterial;
        }
        else
        {
            TargetModel.GetComponentInChildren<MeshRenderer>().material = TargetMaterial;
        }
    }
    
    //called from js
    public void ToggleSource()
    {
        SourceModel.gameObject.SetActive(!SourceModel.gameObject.activeSelf);
        MakeTargetSolid();
    }
    
    //called from js
    public void ToggleTarget()
    {
        TargetModel.gameObject.SetActive(!TargetModel.gameObject.activeSelf);
        MakeTargetSolid();
    }
}
