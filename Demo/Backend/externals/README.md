# Mesh Reconstruction and Difference Utilities

This project integrates a mesh reconstruction script and a mesh difference preprocess script, providing a Dockerfile
for seamless implementation.

## Project Structure

- reconstruction: contains reconstruction scripts
- mesh-difference: contains scripts for create textures to visualize difference between two meshes
- Dockerfile: Docker file that installs and builds the scripts

## Dockerfile Documentation

### Build Stages

The Dockerfile uses a multi-stage build:

#### **Stage 1: Base Image (Node.js & Essential Tools)**

- Uses `node:22` as the base image.
- Installs system dependencies such as `build-essential`, `cmake`, and `libgl1`.
  This stage could be customized to pull any other image from docker hub (e.g. python, ubuntu, ...)

#### **Stage 2: Python Dependencies**

- Uses `python:3.11-slim` to install Python dependencies.
- Configures environment variables for Python optimization.
- Installs `pipenv` for dependency management.
- Installs dependencies from `Pipfile`.

#### **Stage 3: Move Python dependencies to base image**

- Extends the base image by copying the Python virtual environment from Stage 2.
- Ensures Python is properly linked within the container.
- Copies project files into `/app/externals`.

#### **Stage 4: Poisson Surface Reconstruction Setup**

- Installs additional system libraries needed for Poisson reconstruction.
- Changes the working directory to `PoissonRecon`.
- Builds the Poisson reconstruction binary.

### Integration with Docker Compose

This Dockerfile is designed to be used within a `docker-compose.yml` file. With the goal of building the necessary
scripts and placing them inside `/app/externals`.

Below is an example `docker-compose.yml` configuration to insert the scripts in a nestJS app:

```yaml
services:
  nestjs:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - externals-scripts
    volumes:
      - .:/app
      - /app/node_modules
      - externals-volume:/app/externals/reconstruction/PoissonRecon
    environment:
      - NODE_ENV=development
    command: [ "npm", "run", "start:dev" ]

  externals-scripts:
    # This service is used only to create an image used by the nestjs service
    # It won't be used as a running container
    image: build-externals
    build:
      context: ./externals
      dockerfile: Dockerfile
    volumes:
      - externals-volume:/app/externals

volumes:
  externals-volume:
```

#### Note

It is necessary to use `build-externals` as image for the Dockerfile in the nestjs service, as it has the necessary
configurations to run the scripts.
e.g.:

``` Dockerfile
FROM build-externals AS final
WORKDIR /app
#Externals are managed in previous steps
COPY . .
RUN npm install
EXPOSE 3000
```

### Scripts usage within the Docker Volume

Once the Docker container is built, the provided scripts for **Poisson Reconstruction** and **Mesh
Difference Calculation** can be executed from the `nestjs` service within the Docker Compose setup.

#### **Poisson Reconstruction**

The Poisson reconstruction script is located at:

```
/app/externals/reconstruct.py
```
and the Poisson Recon exe is in:
```
/app/externals/PoissonRecon/Bin/Linux/PoissonRecon
```

To execute it from Nest.js, the following approach could be used:

```typescript
const reconstructScript = '/app/externals/reconstruct.py';
const poissonReconExe = '/app/externals/reconstruction/PoissonRecon/Bin/Linux/PoissonRecon';
const inputMesh = '/app/resources/input_mesh.obj';
const outputMesh = '/app/resources/output_mesh.obj';
const depth = 10;
const boundary = 2;

const args = [
  reconstructScript,
  '--poisson_recon_exe', poissonReconExe,
  '--input', inputMesh,
  '--out', outputMesh,
  '--depth', depth.toString(),
  '--bType', boundary.toString(),
];

try {
  await spawnAsync('python', args);
  console.log('Poisson reconstruction completed');
} catch (error) {
  throw new Error(`Poisson reconstruction failed: ${error}`);
}
```

#### **Mesh Difference Calculation**

The mesh difference script is located at:

```
/app/externals/mesh-difference/calculate_difference.py
```

To execute it from Nest.js, the following approach could be used:

```typescript
const meshDiffScript = '/app/externals/mesh-difference/calculate_difference.py';
const sourceMesh = '/app/resources/ground_truth.obj';
const targetMesh = '/app/resources/output_mesh.obj';
const outputDir = '/app/resources/diff_results';

const args = [
  meshDiffScript,
  '--source_path', sourceMesh,
  '--target_path', targetMesh,
  '--output_path_dir', outputDir,
  '--texture_dim', '2048',
  '--samples', '100000',
  '--icp',
  '--simplify',
];

try {
  await spawnAsync('python', args);
  console.log('Mesh difference calculation completed');
} catch (error) {
  throw new Error(`Mesh difference calculation failed: ${error}`);
}
```

## Note
More details on the script parameters and execution are available in the READMEs inside the `reconstruction` and `mesh-difference` folders

