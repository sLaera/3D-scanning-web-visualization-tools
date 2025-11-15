
# Demo Application – WebGL Simulation

![alt text](https://github.com/sLaera/3D-scanning-web-visualization-tools/blob/master/image.png?raw=1)

## 1. Introduction

This application is a demo showcasing how to integrate a **Unity WebGL simulation** inside a **Vue.js** web application using the `unity-webgl-vue` library.

The user interface is composed of two main sections:

- **Upper section** – the actual Unity simulation (e.g., model loading, animation, telemetry-driven updates).
- **Lower section** – an interface used to visualize the differences between the scanned model and the reference model.

This demo features:

- A page with 2 unity instances. 
  - The first one will load a 3d model of a satellite and run a simulation that uses telemetry data (mimic a realtime stream) given by the server.
    - The simulation provides also a simulation of a lidar scanner.
    - This simulation produces also a point cloud of the scanned 3d model
  - The second one will
    - load (after the pcd is reconstructed and preprocessed by the server) the reconstructed mesh 
    - create the heatmap texture, load the ground truth mesh and apply the texture


## 2. External modules

The project includes several Git submodules:

- `externals/ios-webgl-simulator` → contains Unity builds (Simulation and ModelDiff)
- `externals/unity-webgl-vue` → Vue.js library used to embed and communicate with Unity WebGL


## 3. Installation and Setup

### 3.1 Clone the repository (including submodules)

Clone the repository and

1. Copy the content of the folder `Demo\UnitySimulation` in the folder `Demo\Frontend\externals\webgl-simulator`
2. Copy the content of the folder `UnityWebGLVueLibrary` in the folder `Demo\Frontend\externals\unity-webgl-vue`

## 3.2 Required builds before starting

Before running the project, two builds are mandatory.

### 1. Build the `unity-webgl-vue` library

Inside:

```
externals/unity-webgl-vue
```

Run:

```bash
npm install
npm run build
```

### 2. Build the Unity projects

Unity must export the following directories:

* `externals/ios-webgl-simulator/Builds/Simulation`
* `externals/ios-webgl-simulator/Builds/ModelDiff`

Each build must contain:

* `.data.gz`
* `.framework.js.gz`
* `.wasm.gz`
* `.loader.js`


## 3.3 Copy Unity builds into the public folder

After the builds are ready, you can automatically copy them with:

```bash
npm run update-submodules
```

This script will:

1. Rebuild the `unity-webgl-vue` library
2. Update the local dependency
3. Copy Unity builds into:

```
public/UnityBuilds/Simulation
public/UnityBuilds/ModelDiff
```


## 3.4 Start the application

```bash
npm install
npm run dev
```

---

## 4. Unity WebGL + Vue.js Communication

Communication between the Vue application and Unity WebGL relies on:

### Sending messages to Unity:

```ts
channel.call(objectName, methodName, payload)
```

### Receiving messages from Unity:

```ts
channel.subscribe(eventName, callback)
```

Two example components included in the project:

* `LoadAndScanModelUnity.vue`
* `ModelDiffUnity.vue`

These components demonstrate:

* loading 3D assets
* subscribing to Unity events
* triggering simulation actions
* sending telemetry-driven updates

---

## 5. Generic Unity WebGL Integration Example

### Unity configuration:

```ts
const unityConfigs: UnityConfigs = {
  dataUrl: '/UnityBuilds/Simulation/Simulation.data.gz',
  frameworkUrl: '/UnityBuilds/Simulation/Simulation.framework.js.gz',
  codeUrl: '/UnityBuilds/Simulation/Simulation.wasm.gz',
  loaderUrl: '/UnityBuilds/Simulation/Simulation.loader.js'
}
```

### Example: sending a command to load a mesh

```ts
channel.value?.call(
  'ModelLoader',
  'Load',
  JSON.stringify({
    Url: meshInfo.url,
    Position: { x: 0, y: 0, z: 0 }
  })
)
```

### Example: subscribing to Unity events

```ts
c.subscribe('modelLoaded', (modelUrl) => {
  emit('modelLoaded', modelUrl)
})
```

---

## 6. Telemetry Handling via WebSocket

Telemetry management is implemented in:

```
composables/useTelemetry.ts
```

This composable:

* connects to a WebSocket server
* receives telemetry at high frequency
* updates UI state in optimized batches
* sends OFF file fragments to Unity
* notifies when the stream ends

### 6.1 Buffered and throttled state updates

To avoid performance issues, telemetry is stored in a buffer and committed periodically:

```ts
let historyBuffer: TelemetryData[] = []
const handleNewData = Utils.throttle(() => {
  telemetryHistory.value.push(...historyBuffer)
  historyBuffer = []
}, 300)
```

### 6.2 Updating Unity on each telemetry packet

```ts
const updateSimulation = (data: TelemetryData) => {
  channel.value?.call('GameManager', 'UpdateSimulation', JSON.stringify(data))
}
```

When the telemetry stream ends:

```ts
channel.value?.call('GameManager', 'CompleteSimulation')
```

## 7. Relevant Scripts (from package.json)

### Update submodules and copy Unity builds

```json
"update-submodules": "cd externals/unity-webgl-vue && npm run build && cd ../../ && npm upgrade unity-webgl-vue && npm run cpy-unity-build"
```

### Copy Unity builds

```json
"cpy-unity-build": "npm run cpy-unity-build:model-diff && npm run cpy-unity-build:simulation"
```