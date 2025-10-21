using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using Scenes.ModelDiffScene.Scripts.Classes;
using SharedScripts;
using SharedScripts.Classes;
using UnityEngine;
using UnityEngine.Serialization;
using UnityEngine.UI;

namespace Scenes.ModelDiffScene.Scripts
{
    public class ModelLoader : MonoBehaviour
    {
        public OrbitalCamera Camera;
        public Image Spinner;

        public GameObject LoadedModel { get; set; }

        private RuntimeLoader _loader;

        private void Start()
        {
            _loader = new RuntimeLoader();
            // Load("{\"Url\": \"http://localhost:3000/models/Target.glb\", \"Position\":{\"x\":0,\"y\":0,\"z\":0}}");
        }

        public void DestroyLoadedModel()
        {
            if (LoadedModel)
            {
                Destroy(LoadedModel);
            }
        }

        /**
         * Function called from js
         */
        public async Task Load(string modelInfo)
        {
            Spinner.gameObject.SetActive(true);
            if (LoadedModel)
            {
                Destroy(LoadedModel);
            }

            try
            {
                var info = JsonUtility.FromJson<ModelInfo>(modelInfo);
                LoadedModel = await _loader.LoadFromUrl(info.Url, info.Position);
                AddCollidersToChildren(LoadedModel.transform);
                LoadedModel.transform.localScale = new Vector3(5, 5, 5);
                Camera.LookAt = LoadedModel.transform;
                GameManager.I.JsChannel.Publish("modelLoaded", info.Url);
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

        private void AddCollidersToChildren(Transform obj)
        {
            foreach (Transform child in obj)
            {
                //skip current object
                if (child == obj)
                    continue;

                AddCollidersToChildren(child);

                MeshFilter meshFilter = child.GetComponent<MeshFilter>();
                if (meshFilter != null && meshFilter.sharedMesh != null)
                {
                    // check for existing colliders
                    MeshCollider existingCollider = child.GetComponent<MeshCollider>();
                    if (existingCollider == null)
                    {
                        child.gameObject.AddComponent<MeshCollider>();
                    }
                }
            }
        }
    }
}
