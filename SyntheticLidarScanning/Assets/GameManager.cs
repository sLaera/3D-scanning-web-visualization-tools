using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    public static GameManager I;
    public List<string> ModelNames;
    public (int, string) CurrentModel;
    public Sensor Sensor;
    
    private void Awake()
    {
        // If there is an instance, and it's not me, delete myself.

        if (I != null && I != this)
        {
            Destroy(this);
        }
        else
        {
            I = this;
        }
    }
    
    void Start()
    {
        //Load the models
        ModelNames = Utils.ReadMeshNames(ArgsManager.InPath);
        CurrentModel = (-1, null);
        StartNewScan();
        Debug.Log("===========================================================================================");
        Debug.Log("New Scan started.\n Scanning lst file: " + ArgsManager.InPath);
        Debug.Log("===========================================================================================");
    }

    public void StartNewScan()
    {
        if (CurrentModel.Item1 + 1 == ModelNames.Count )
        {
            //Scan completed
            Application.Quit();
            Sensor.gameObject.SetActive(false);
            return;
        }
        Debug.Log("------------------------------");
        Debug.Log(CurrentModel.Item1);
        Debug.Log("------------------------------");
        
        CurrentModel.Item1 ++;
        CurrentModel.Item2 = ModelNames[CurrentModel.Item1];
        //load model
        var model = ModelLoader.I.LoadModel(Path.Combine(ArgsManager.InDir, CurrentModel.Item2 + ".obj"));
        model.transform.GetChild(0).gameObject.AddComponent<MeshCollider>();
        //Start scan
        Sensor.StartNewScan();
    }
}
