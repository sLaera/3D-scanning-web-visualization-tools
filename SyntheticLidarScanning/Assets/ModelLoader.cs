using System.Collections;
using System.Collections.Generic;
using Dummiesman;
using UnityEngine;

public class ModelLoader : MonoBehaviour
{
    public static ModelLoader I { get; private set; }
    public GameObject CurrentModel { get; private set; }

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

    public GameObject LoadModel(string modelPath)
    {
        Destroy(CurrentModel);
        CurrentModel = new OBJLoader().Load(modelPath);
        CurrentModel.transform.localScale = Vector3.one * 10;//scale the object to match Unity scale
        return CurrentModel;
    }
}
