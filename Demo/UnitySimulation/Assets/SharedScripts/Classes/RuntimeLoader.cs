using System;
using System.IO;
using System.Threading.Tasks;
using GLTFast;
using SharedScripts.OBJImport;
using UnityEngine;
using UnityEngine.Networking;

namespace SharedScripts.Classes
{
    public class RuntimeLoader
    {
        /// <summary>
        /// Load the Model base on the url given by the Vue application.
        /// Supports obj, glb, gltf file formats.
        /// Supports local or remote files.
        /// </summary>
        public async Task<GameObject> LoadFromUrl(string url, Vector3? position = null, Quaternion? rotation = null, Transform parent = null)
        {
            var format = Helpers.GetFileExtensionFromUrl(url);
            switch (format)
            {
                case ".gltf":
                case ".glb":
                    var loader = new GameObject();
                    if (parent)
                    {
                        loader.transform.SetParent(parent);
                    }

                    position ??= new Vector3(0, 0, 0);
                    loader.transform.position = (Vector3)position;
                    rotation ??= Quaternion.identity;
                    loader.transform.rotation = (Quaternion)rotation;

                    var gltf = loader.AddComponent<GltfAsset>();
                    gltf.Url = url;
                    gltf.LoadOnStartup = false;
                    gltf.ImportSettings = new ImportSettings {
                        GenerateMipMaps = true
                    };
                    //remote file paths handled inside Load
                    var result = await gltf.Load(gltf.FullUrl);
                    if (!result)
                        throw new InvalidOperationException("Error while loading gltf file");
                    return loader;
                case ".obj":
                    //File url could be a local path or remote path
                    GameObject model;
                    if (Helpers.IsRemotePath(url))
                    {
                        var stream = await RemoteFileUtils.GetRemoteFileStream(url);
                        model = new ObjLoader().Load(stream, Path.GetFileNameWithoutExtension(url));
                    }
                    else
                    {
                        model = new ObjLoader().Load(url);
                    }

                    if (parent)
                    {
                        model.transform.SetParent(parent);
                    }

                    position ??= new Vector3(0, 0, 0);
                    model.transform.position = (Vector3)position;
                    rotation ??= Quaternion.identity;
                    model.transform.rotation = (Quaternion)rotation;
                    return model;
            }
            throw new NotSupportedException("Given model format is not supported");
        }

        /// <summary>
        /// Download a texture form uri (with a remote http call if the url is remote)
        /// </summary>
        /// <param name="uri"></param>
        /// <returns>2D texture</returns>
        public async Task<Texture2D> LoadTexture(string uri)
        {
            using (UnityWebRequest www = UnityWebRequestTexture.GetTexture(uri))
            {
                //SendWebRequest return yield instruction
                var asyncOperation = www.SendWebRequest();
                while (!asyncOperation.isDone) //await for competition
                {
                    await Task.Yield();
                }

                if (www.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError(www.error);
                    return null;
                }

                return DownloadHandlerTexture.GetContent(www);
            }
        }
    }
}
