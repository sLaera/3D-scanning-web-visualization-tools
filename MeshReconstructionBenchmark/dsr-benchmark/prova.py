import open3d as o3d #0.18.0
import numpy as np

# Carica la mesh da un file
file_path = "/home/slaera/lidar-mesh-reconstruction/benchmark/dsr-benchmark/test/reconbench/mesh/teapot.obj"  # Sostituisci con il percorso del tuo file
mesh = o3d.io.read_triangle_mesh(file_path)

w, h = 10, 10
corners = np.array([
    [0, 0, 0],
    [w, 0, 0],
    [w, h, 0],
])

triangles = np.array([[2, 1, 0]])
mesh = o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(corners), o3d.utility.Vector3iVector(triangles))

# Verifica che la mesh sia stata caricata correttamente
if mesh.is_empty():
    raise ValueError("Mesh non caricata correttamente, controlla il percorso del file.")

# Applica uno scalamento del 10%
scaling_factor = 1.1
mesh.scale(scaling_factor, center=mesh.get_center())

# Visualizza la mesh scalata
o3d.visualization.draw_geometries([mesh])
