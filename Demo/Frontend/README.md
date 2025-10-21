# web-gui

this project is a demo designed to illustrate the usage of the tools developed for aereo spatial simulations.
This demo features:
- A page with 2 unity instances. 
  - The first one will load a 3d model of a satellite and run a simulation that uses telemetry data (mimic a realtime stream) given by the server.
    - The simulation provides also a simulation of a lidar scanner.
    - This simulation produces also a point cloud of the scanned 3d model
  - The second one will
    - load (after the pcd is reconstructed and preprocessed by the server) the reconstructed mesh 
    - create the heatmap texture, load the ground truth mesh and apply the texture

1. Copy the content of the folder `Demo\UnitySimulation` in the folder `Demo\Frontend\externals\webgl-simulator`
2. Copy the content of the folder `UnityWebGLVueLibrary` in the folder `Demo\Frontend\externals\unity-webgl-vue`