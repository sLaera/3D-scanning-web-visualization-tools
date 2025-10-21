using System;
using System.IO;
using System.Threading.Tasks;
using UnityEngine.Networking;

namespace SharedScripts
{
    public class Helpers
    {
        public static bool IsRemotePath(string path)
        {
            return Uri.TryCreate(path, UriKind.Absolute, out Uri uri) &&
                   (uri.Scheme == Uri.UriSchemeHttp || uri.Scheme == Uri.UriSchemeHttps || uri.Scheme == Uri.UriSchemeFtp);
        }
        
        public static string GetFileExtensionFromUrl(string url)
        {
            if (string.IsNullOrEmpty(url))
                throw new ArgumentException("URL cannot be null or empty.", nameof(url));

            Uri uri;
            if (!Uri.TryCreate(url, UriKind.Absolute, out uri))
                throw new UriFormatException("Invalid URL format.");

            string extension = Path.GetExtension(uri.AbsolutePath);
            return string.IsNullOrEmpty(extension) ? null : extension.ToLower();
        }
    }
    
    public static class RemoteFileUtils
    {
        // private static readonly HttpClient HttpClient = new HttpClient();
        //
        // public static async Task<Stream> GetRemoteFileStream(string url)
        // {
        //     HttpResponseMessage response = await HttpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead);
        //     response.EnsureSuccessStatusCode();
        //     return await response.Content.ReadAsStreamAsync();
        // }
        
        public static async Task<Stream> GetRemoteFileStream(string url)
        {
            using UnityWebRequest request = UnityWebRequest.Get(url);
            var asyncOp = request.SendWebRequest();

            while (!asyncOp.isDone)
            {
                await Task.Yield();
            }

            if (request.result != UnityWebRequest.Result.Success)
            {
                throw new Exception($"Error downloading file: {request.error}");
            }

            return new MemoryStream(request.downloadHandler.data);
        }
    }
}
