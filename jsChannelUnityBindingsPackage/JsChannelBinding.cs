using System.Runtime.InteropServices;
using UnityEngine;

namespace Plugin.JsChannel
{
    public class JsChannelBinding
    {
        [DllImport("__Internal")]
        private static extern void PublishEventJson(string eventName, string jsonData, string channelName);
        [DllImport("__Internal")]
        private static extern void PublishEventString(string eventName, string data, string channelName);
        [DllImport("__Internal")]
        private static extern void PublishEventNumber(string eventName, float data, string channelName);
        [DllImport("__Internal")]
        private static extern void PublishEventArray(string eventName, float[] data, int size, string channelName);
        [DllImport("__Internal")]
        private static extern void PublishEventTexture(string eventName, int data, string channelName);

        private readonly string _channelName;
        /// <summary>
        /// Bind the js publish function to C#. Default channel name is _UNITY_CHANNEL
        /// </summary>
        /// <param name="channelName"></param>
        public JsChannelBinding(string channelName = "_UNITY_CHANNEL")
        {
            _channelName = channelName;
        }

        /// <summary>
        /// Publish an event with a json payload. The json string will be converted in js object
        /// </summary>
        /// <param name="eventName"></param>
        /// <param name="jsonData"></param>
        public void PublishJson(string eventName, string jsonData)
        {
            #if !UNITY_EDITOR && UNITY_WEBGL
            PublishEventJson(eventName, jsonData, _channelName);
            #endif
        }
        public void Publish(string eventName, int data)
        {
            #if !UNITY_EDITOR && UNITY_WEBGL
            PublishEventNumber(eventName, data, _channelName);
            #endif
        }
        public void Publish(string eventName, float data)
        {
            #if !UNITY_EDITOR && UNITY_WEBGL
            PublishEventNumber(eventName, data, _channelName);
            #endif
        }
        public void Publish(string eventName, string data)
        {
            #if !UNITY_EDITOR && UNITY_WEBGL
            PublishEventString(eventName, data, _channelName);
            #endif
        }
        public void Publish(string eventName, float[] data)
        {
            #if !UNITY_EDITOR && UNITY_WEBGL
            PublishEventArray(eventName, data, data.Length, _channelName);
            #endif
        }
        public void Publish(string eventName, Texture2D data)
        {
            #if !UNITY_EDITOR && UNITY_WEBGL
            PublishEventTexture(eventName, (int)data.GetNativeTexturePtr(), _channelName);
            #endif
        }

    }
}
