# Unity Project Documentation – Simulation & Model Difference Visualization

This Unity project consists of **two independent scenes** designed to be used inside a **Vue.js** application through the communication library **`unity-webgl-vue`**.  
The project demonstrates how to run a WebGL simulation, communicate with a web frontend, load 3D models at runtime, compute visual differences between meshes, and visualize point clouds.

---

# 1. Project Structure

## Scenes

### **1. Simulation Scene**
Path: `Scenes/SimulationScene/SimulationScene`

- Implements a simplified simulation of a scanning operation, updated in real time through telemetry data sent from the Vue.js application.
- Demonstrates interpolation (lerp/slerp) of positions and rotations based on time-stamped telemetry.
- Generates point clouds through a `Sensor` component and returns data to the frontend.

### **2. Model Difference Scene**
Path: `Scenes/ModelDiffScene/ModelDiffScene`

- Loads preprocessed outputs (meshes and textures) coming from a Python backend.
- Computes a heatmap texture using a custom compute shader.
- Visualizes differences between two meshes (source and target).
- Designed to be modular and reusable for other mesh-difference evaluations.

---

# 2. WebGL Build Instructions

This project is meant to be embedded inside a Vue.js application.  
**The two scenes must be built separately**, each producing a standalone WebGL build.

### **Required build output structure**

```

/Builds/Simulation
/Builds/ModelDiff

```

### **How to build each scene**

1. Open Unity.
2. Go to **File → Build Settings**.
3. Select **WebGL** as target platform.
4. Add *only the desired scene*:

   - For the simulation build:  
     `Scenes/SimulationScene/SimulationScene`

   - For the model difference build:  
     `Scenes/ModelDiffScene/ModelDiffScene`

5. Build the scenes separately, placing the output folders into:

```

Builds/Simulation
Builds/ModelDiff

````

Do **not** include both scenes within the same WebGL build.

---

# 3. Shared Scripts (`Assets/SharedScripts`)

This folder contains reusable utilities that can be included in other Unity projects.

## 3.1 OBJImport/  
A customized version of the OBJ import library supporting **vertex color loading**.  
Used by the runtime model loader to load `.obj` files from remote or local paths.

---

## 3.2 `Classes/RuntimeLoader.cs`

A generic Runtime Loader used to load `.obj`, `.gltf`, and `.glb` files at runtime, from either local disk or remote URLs.

### **Features**

- Supports `.obj`, `.glb`, `.gltf`.
- Loads from remote HTTP URLs or local paths.
- Allows defining:
  - position  
  - rotation  
  - parent transform  

### **Usage Example**

```csharp
private RuntimeLoader _loader;

private async void Start() {
    _loader = new RuntimeLoader();

    // Load GLB/GLTF
    var model = await _loader.LoadFromUrl(
        "https://example.com/models/model.glb",
        position: new Vector3(0, 0, 0),
        rotation: Quaternion.identity
    );

    model.transform.localScale = Vector3.one * 2f;
}
````

### **How it works internally**

* Detects extension via `Helpers.GetFileExtensionFromUrl()`.
* For `.gltf`/`.glb`:
  Uses **GltfAsset** (from GLTFast) and loads asynchronously.
* For `.obj`:
  Loads either:

  * From remote via stream (`RemoteFileUtils`), or
  * From local path.
* Always applies transform arguments and optional parent assignment.

### **Texture Loading**

```csharp
var tex = await _loader.LoadTexture(url);
```

Supports downloading PNG/JPG textures at runtime.

---

# 3.3 Point Cloud Visualization

### Script: `PointCloudVisualizer.cs`

Used to render point clouds using the shader:
`Assets/Resources/Shaders/PointCloud.shader`

### **How to use**

1. Create an **Empty GameObject**.
2. Add the `PointCloudVisualizer` component.
3. Reference it from your script:

```csharp
public PointCloudVisualizer PcdVisualizer;
```

4. Assign points and normals:

```csharp
PcdVisualizer.Points = SensorObj.GetPoints();
PcdVisualizer.Normals = SensorObj.GetNormals();
PcdVisualizer.gameObject.SetActive(true);
```

### Points & Normals Format

```csharp
private readonly List<Vector3> _points = new List<Vector3>();
private readonly List<Vector3> _normals = new List<Vector3>();
```

The visualizer will automatically update the GPU buffer and render the cloud.

---

# 4. JavaScript Channel Integration (`Assets/Plugin/JsChannel`)

This folder contains a bridge for sending events from Unity WebGL → JavaScript.
It is designed to work with **unity-webgl-vue** and can be reused in other WebGL projects.

### **Main Class: `JsChannelBinding`**

Capable of publishing:

* JSON objects
* numbers
* strings
* float arrays
* textures (via native pointer)

### **Usage Example**

```csharp
private JsChannelBinding Js;

private void Start() {
    Js = new JsChannelBinding();
}

// Send JSON data
Js.PublishJson("telemetryUpdate", jsonString);

// Send numbers
Js.Publish("progress", 0.8f);

// Send string
Js.Publish("status", "Model Loaded");

// Send float array
Js.Publish("points", pointArray);
```

### **How it works**

On WebGL builds (not in the editor), it calls JS functions injected by `unity-webgl-vue`:

```csharp
[DllImport("__Internal")]
private static extern void PublishEventJson(string eventName, string jsonData, string channelName);
```

The event is delivered to the Vue.js application via the chosen channel (`_UNITY_CHANNEL` by default).

---

# 5. Simulation Scene – How It Works

The core logic is found in:

`Assets/Scenes/SimulationScene/Scripts/GameManager.cs`

### **Purpose**

* Receive telemetry data from Vue (`UpdateSimulation`)
* Interpolate servicer movement and joints smoothly
* Trigger scanning frames via `SensorObj`
* Send events back to Vue through `JsChannel`
* Show a point cloud at the end of the scan

### **Telemetry Flow**

1. Vue sends a JSON packet → `UpdateSimulation(string telemetryDataRaw)`
2. Converted to `TelemetryData`
3. Store previous & current packets
4. On each frame:

   * Compute interpolation factor:

```csharp
float t = (_simulationTime - _prevData.Timestamp) / (_currentData.Timestamp - _prevData.Timestamp);
```

5. Interpolate position & rotation:

```csharp
Servicer.position = Vector3.Lerp(_prevData.Position, _currentData.Position, t);
Servicer.rotation = Quaternion.Slerp(
    Quaternion.Euler(_prevData.Rotation),
    Quaternion.Euler(_currentData.Rotation),
    t
);
```

6. Interpolate robotic arm joints.

### **When a scan frame arrives**

```csharp
if (_prevData.ScanFrame)
    SensorObj.ScanFrame();
```

### **End of Simulation**

* Notify Vue to create an OFF file:

```csharp
JsChannel.Publish("createOffFile", SensorObj.GetPoints().Count);
```

* Display point cloud with `PointCloudVisualizer`
* Reset the scene

---

# 6. Model Difference Scene – How It Works

The main script handling model loading and difference visualization is:

`Assets/Scenes/ModelDiffScene/Scripts/ModelDiffVisualizer.cs`

## Overview

This component:

1. Receives a JSON payload from JavaScript containing:

   * source mesh path
   * target mesh path
   * UV-mapped points texture
   * positions texture
2. Loads both meshes via `RuntimeLoader`
3. Downloads textures from the backend
4. Executes a compute-like material pass (via GPU shader) to build a **heatmap texture**
5. Applies the heatmap texture to the source mesh
6. Displays the target mesh for comparison

---

## Steps in Detail

### **1. Load Models**

```csharp
SourceModel = await _loader.LoadFromUrl(dto.sourceMesh);
TargetModel = await _loader.LoadFromUrl(dto.targetMesh);
```

### **2. Load Textures**

```csharp
var pointsTexture = await _loader.LoadTexture(dto.pointsTexture);
var positionsTexture = await _loader.LoadTexture(dto.positionsTexture);
```

Textures are set to **FilterMode.Point** for precise sampling.

---

### **3. Create Heatmap Texture**

A RenderTexture is created:

```csharp
_heatmapTexture = new RenderTexture(width, height, 0, RenderTextureFormat.ARGBHalf);
```

Values passed to the compute material:

```csharp
HeatmapComputeMaterial.SetTexture("_PointsTex", pointsTexture);
HeatmapComputeMaterial.SetTexture("_Positions", positionsTexture);
HeatmapComputeMaterial.SetVector("_Resolution", new Vector2(pointsTexture.width, pointsTexture.height));
```

Then:

```csharp
Graphics.Blit(null, _heatmapTexture, HeatmapComputeMaterial);
```

This runs the GPU shader, producing the final heatmap.

---

### **4. Apply Texture to Source Model**

```csharp
var propertyBlock = new MaterialPropertyBlock();
propertyBlock.SetTexture("_MainTex", _heatmapTexture);
sourceRenderer.material = FillHolesMaterial;
sourceRenderer.SetPropertyBlock(propertyBlock);
```

### **5. Set Target Model Material**

```csharp
targetRenderer.material = TargetMaterial;
```

---

### **6. JS-Triggered Visibility Toggles**

```csharp
public void ToggleSource();
public void ToggleTarget();
```

These allow the Vue.js frontend to show/hide individual meshes.