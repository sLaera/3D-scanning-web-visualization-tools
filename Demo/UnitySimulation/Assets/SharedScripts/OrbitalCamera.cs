using UnityEngine;
using UnityEngine.Serialization;

namespace SharedScripts
{
    public class OrbitalCamera : MonoBehaviour
    {
        public Transform LookAt;
        public float Sensibility = 8f;
        public float InitialRadius = 10;

        public float OrbitRadius;
        private Vector3 _lookAtPositionCopy;
        
        // Start is called before the first frame update
        void Start()
        {
            OrbitRadius = InitialRadius;
            _lookAtPositionCopy = new Vector3(LookAt.position.x, LookAt.position.y, LookAt.position.z);
        }

        // Update is called once per frame
        void Update()
        {
            var mouseX = Input.GetAxis("Mouse X");
            var mouseY = Input.GetAxis("Mouse Y");
            
            if (Input.GetMouseButton(0))
            {
                transform.eulerAngles += new Vector3(0, mouseX * Sensibility, 0);
                transform.Rotate(new Vector3(-mouseY * Sensibility, 0, 0));
            }
            OrbitRadius -= Input.mouseScrollDelta.y * Sensibility * 0.1f;
            if (Input.GetMouseButton(1))
            {
                OrbitRadius -= mouseY * Sensibility * 0.5f;
            }
            if (Input.GetMouseButton(2))
            {
                _lookAtPositionCopy -= transform.right * mouseX / Sensibility;
                _lookAtPositionCopy -= transform.up * mouseY / Sensibility;
            }

            transform.position = _lookAtPositionCopy - transform.forward * OrbitRadius;
            
        }
    }
}
