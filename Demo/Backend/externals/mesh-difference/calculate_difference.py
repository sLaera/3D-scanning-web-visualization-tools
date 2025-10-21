import argparse
import json
import os
from typing import Union

import cv2
import numpy as np
import open3d as o3d

from classes.MeshTools import MeshTools
from classes.SampledMesh import SampledMesh
from classes.helpers import get_file_name, save_to_file, load_from_file, normalize, save_arrays, load_arrays
import sys


def print_uv_debug(uv_map: np.ndarray,
                   texture_img: Union[str, np.ndarray] = 'points.png',
                   alpha: float = 1.0,
                   show_texture_only: bool = False,
                   resize=600,
                   save=False) -> None:
    """
    Visualize UV mapping on a texture for debugging purposes.

    Args:
        uv_map (np.ndarray): Array of shape (N, 2) containing UV coordinates, where each UV coordinate is in [0, 1].
        texture_img (Union[str, np.ndarray]): Path to the texture image or a preloaded texture (shape: H x W x 3).
        alpha (float): Transparency factor for blending the original texture with the UV overlay (range: 0.0 to 1.0).

    Returns:
        None: The function displays the UV plot in a window and does not return anything.
    """
    # Load texture image if a file path is provided
    if isinstance(texture_img, str):
        texture = cv2.imread(texture_img)
        if texture is None:
            raise FileNotFoundError(
                f"Texture image not found at path: {texture_img}")
    else:
        texture = texture_img

    # Resize the texture for visualization purposes
    texture = cv2.resize(texture, (resize, resize), interpolation=cv2.INTER_CUBIC)
    final_texture = texture
    if not show_texture_only:
        original = texture.copy()

        triangle_points = []
        height, width, _ = texture.shape

        for i, uv in enumerate(uv_map):
            u, v = uv
            x = int(u * (width - 1))
            y = int(v * (height - 1))
            triangle_points.append([x, y])

            # Draw triangles once three points are collected
            if (i + 1) % 3 == 0:
                # Draw triangle outline
                cv2.polylines(texture, [np.array(triangle_points, dtype=np.int32)], isClosed=True, color=(0, 255, 0),
                              thickness=1)
                triangle_points = []

        # Apply the overlay with a transparency factor
        final_texture = cv2.addWeighted(texture, alpha, original, 1 - alpha, 0)

    if save:
        cv2.imwrite("UV_Plot.png", final_texture)
    else:
        # Display the resulting texture
        cv2.imshow("UV Plot", final_texture)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main(args):
    # ----------------- args ---------------------
    samples = args.samples
    texture_dim = args.texture_dim
    perform_icp = args.icp
    simplify = args.simplify
    source_model_path = args.source_path
    if not os.path.exists(source_model_path):
        raise Exception(f"Path:{os.path.abspath(source_model_path)} doesn't exist")
    target_model_path = args.target_path
    if not os.path.exists(target_model_path):
        raise Exception(f"Path:{os.path.abspath(target_model_path)} doesn't exist")

    if args.use_brk:
        positive_breakpoints = [args.p_brk1, args.p_brk2, args.p_brk3]
        negative_breakpoints = [args.n_brk1, args.n_brk2, args.n_brk3]
    else:
        positive_breakpoints = None
        negative_breakpoints = None

    output_path = args.output_path_dir
    # ------------------------------------------

    os.makedirs(output_path, exist_ok=True)
    output_source_mesh_path = f"{output_path}/source.obj"
    output_target_mesh_path = f"{output_path}/target.obj"
    output_info_path = f"{output_path}/info.json"

    # -------loading source
    source_pcd_output_path = f"{output_path}/sampled_source.npz"
    if not os.path.exists(source_pcd_output_path):
        print("loading source mesh")
        sys.stdout.flush()
        source = MeshTools.load_mesh(source_model_path)

        print("source faces:", len(source.mesh.vertices))
        sys.stdout.flush()
        if simplify:
            print("Simplifying source")
            sys.stdout.flush()
            source.simplify(100000)

        # calculate uvs
        source.generate_uv(texture_dim, border=3)
        # save to file intermediate processed mesh. Will be resaved at the end with vertex colors
        o3d.io.write_triangle_mesh(output_source_mesh_path, source.mesh, write_triangle_uvs=True, write_vertex_normals=True)

        # Reload to avoid difference between cache mesh and current loaded mesh
        source = MeshTools.load_mesh(output_source_mesh_path)

        print("Sampling source")
        sys.stdout.flush()
        sampled_source = SampledMesh.from_mesh(source, samples)
        sampled_source.save_to_file(source_pcd_output_path)
    else:
        print("Sampled source in cache. Loading from cache")
        sys.stdout.flush()
        source = MeshTools.load_mesh(output_source_mesh_path)
        sampled_source = SampledMesh.load_from_file(source_pcd_output_path)

    #  ---- loading target
    target_pcd_output_path = f"{output_path}/sampled_target.npz"
    if not os.path.exists(target_pcd_output_path):
        print("loading target mesh")
        sys.stdout.flush()
        target = MeshTools.load_mesh(target_model_path)
        print("target faces:", len(target.mesh.vertices))
        sys.stdout.flush()
        if simplify:
            print("Simplifying target")
            sys.stdout.flush()
            target.simplify(100000)

        # calculate uvs
        # target.generate_uv(texture_dim, border=3)
        # save to file intermediate processed mesh. Will be resaved at the end with vertex colors
        o3d.io.write_triangle_mesh(output_target_mesh_path, target.mesh, write_triangle_uvs=True, write_vertex_normals=True)

        # Reload to avoid difference between cache mesh and current loaded mesh
        target = MeshTools.load_mesh(output_target_mesh_path)

        print("Sampling target")
        sys.stdout.flush()
        sampled_target = SampledMesh.from_mesh(target, samples)
        sampled_target.save_to_file(target_pcd_output_path)
    else:
        print("Sampled target in cache. Loading from cache")
        sys.stdout.flush()
        target = MeshTools.load_mesh(output_target_mesh_path)
        sampled_target = SampledMesh.load_from_file(target_pcd_output_path)

    # ------------------------- ICP -------------------------------
    distances_output_path = f"{output_path}/distances.npz"
    if perform_icp and not os.path.exists(distances_output_path):
        print("Performing ICP")
        sys.stdout.flush()

        align_transform = sampled_source.align_centroids(sampled_target)
        source.mesh.transform(align_transform)
        source.clear_stored_data()
        sampled_source.pcd.transform(align_transform)
        sampled_source.clear_stored_data()

        threshold = 0.02
        trans_init = np.eye(4)
        reg_icp = o3d.pipelines.registration.registration_icp(
            sampled_source.pcd, sampled_target.pcd, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=100)
        )
        # apply icp transformation
        source.mesh.transform(reg_icp.transformation)
        source.clear_stored_data()
        # apply icp transformation
        sampled_source.pcd.transform(reg_icp.transformation)
        sampled_source.clear_stored_data()

        # Save in cache
        o3d.io.write_triangle_mesh(output_source_mesh_path, source.mesh, write_triangle_uvs=True, write_vertex_normals=True)
        sampled_source.save_to_file(source_pcd_output_path)
    # o3d.visualization.draw_geometries([source.mesh, target.mesh])
    # -------------------------  -------------------------------
    # ------------------------- calculate difference -------------------------------
    if not os.path.exists(distances_output_path):
        print("calculating distances")
        sys.stdout.flush()
        distances = sampled_source.compute_chamfer_distances(sampled_target)
        save_arrays(distances_output_path, distances = distances)
    else:
        print("Distances in cache. Loading from cache")
        sys.stdout.flush()
        distances = load_arrays(distances_output_path)["distances"]

    # ------------------------ normalizations -------------------------------
    # bbox = source.mesh.get_axis_aligned_bounding_box()
    # dimensions = np.array(bbox.get_max_bound()) - \
    #              np.array(bbox.get_min_bound())
    # normalized_distances= normalize(distances)
    # ------------------------ colorization ---------------------------------
    sampled_source.colorize_by_distance(distances, positive_breakpoints, negative_breakpoints)

    # o3d.visualization.draw_geometries([sampled_source.pcd])
    # ------------------------- generate texture ---------------------------------
    print("generate texture")
    sys.stdout.flush()
    texture, positions = sampled_source.map_colors_to_texture(source, texture_dim)

    sampled_source.colorize_vertex_from_points(source)

    # print_uv_debug(source.get_uvs(), texture, show_texture_only=False)

    # source.mesh.textures = [o3d.geometry.Image(texture), o3d.geometry.Image(positions)]

    o3d.io.write_triangle_mesh(output_source_mesh_path, source.mesh, write_triangle_uvs=True, write_vertex_colors=True, write_vertex_normals=True)
    o3d.io.write_triangle_mesh(output_target_mesh_path, target.mesh, write_vertex_normals=True)

    cv2.imwrite(f"{output_path}/points.png", cv2.cvtColor(cv2.flip(texture,0), cv2.COLOR_RGB2BGR))
    cv2.imwrite(f"{output_path}/positions.png",  cv2.cvtColor(cv2.flip(positions,0), cv2.COLOR_RGB2BGR))

    # --- save additional information
    with open(output_info_path, 'w', encoding='utf-8') as f:
        json.dump({
            "min_positive_distance": "{:10.4f}".format(distances[distances >= 0].min()),
            "max_positive_distance": "{:10.4f}".format(distances[distances >= 0].max()),
            "min_negative_distance": "{:10.4f}".format(distances[distances < 0].min()),
            "max_negative_distance": "{:10.4f}".format(distances[distances < 0].max()),
        }, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_path", type=str,
                        help="Path of the source mesh")
    parser.add_argument("--target_path", type=str,
                        help="Path of the target mesh")
    parser.add_argument("--texture_dim", type=int,
                        help="Dimension of the texture")
    parser.add_argument("--samples", type=int,
                        help="Number of samples")
    parser.add_argument("--icp", action='store_true',
                        help="Flag to perform ICP")
    parser.add_argument("--simplify", action='store_true',
                        help="Flag to simplify mesh")

    parser.add_argument("--use_brk", action='store_true',
                        help="Use breakpoints")

    parser.add_argument("--p_brk1", type=float, help="First positive breakpoint")
    parser.add_argument("--p_brk2", type=float, help="Second positive breakpoint")
    parser.add_argument("--p_brk3", type=float, help="Third positive breakpoint")


    parser.add_argument("--n_brk1", type=float, help="First negative breakpoint")
    parser.add_argument("--n_brk2", type=float, help="Second negative breakpoint")
    parser.add_argument("--n_brk3", type=float, help="Third negative breakpoint")

    parser.add_argument("--output_path_dir", type=str, help="Output files folder path")

    args = parser.parse_args()

    main(args)
