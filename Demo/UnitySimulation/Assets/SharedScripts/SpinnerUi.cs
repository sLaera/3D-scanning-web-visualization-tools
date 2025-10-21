using UnityEngine;

namespace SharedScripts
{
    public class SpinnerUi : MonoBehaviour
    {
        public float Speed = 100;
        // Start is called before the first frame update
        void Start()
        {
        
        }

        // Update is called once per frame
        void Update()
        {
            transform.Rotate(0,0,Time.deltaTime * Speed);
        }
    }
}
