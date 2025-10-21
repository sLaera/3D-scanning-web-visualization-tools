using System.IO;
using UnityEngine;

public class FileLogger : MonoBehaviour
{
    private string _logFilePath;

    private void Awake()
    {
        _logFilePath = Path.Combine(Application.streamingAssetsPath, "log.txt");
        Application.logMessageReceived += HandleLog;
    }

    private void OnDestroy()
    {
        Application.logMessageReceived -= HandleLog;
    }

    private void HandleLog(string logString, string stackTrace, LogType type)
    {
        string logEntry = $"{System.DateTime.Now}: [{type}] {logString}\n";
        if (type == LogType.Exception)
        {
            logEntry += $"{stackTrace}\n";
        }

        File.AppendAllText(_logFilePath, logEntry);
    }
}
