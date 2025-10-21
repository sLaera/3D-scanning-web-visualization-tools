import time
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

import numpy as np
import open3d as o3d
import concurrent

from igl import signed_distance

from classes.HeatmapColor import HeatmapColors
from classes.helpers import save_arrays, load_arrays
from classes.MeshTools import MeshTools


class SampledMesh:
    def __init__(self, pcd: o3d.geometry.PointCloud, triangle_indexes: np.ndarray):
        self.pcd: o3d.geometry.PointCloud = pcd
        self.triangle_indexes = triangle_indexes
        # The points in pcd should not change, np arrays are precomputed in get functions and stored in private variables
        self.__points = None
        self.__normals = None
        self.__colors = None

    # clear private values
    def clear_stored_data(self):
        self.__vertex_array = None
        self.__triangles_array = None
        self.__normals_array = None

    def save_to_file(self, filename: str):
        """
            Saves sampled point cloud data (points, normals, and triangle indices) to a compressed .npz file.

            Parameters:
            - save_file (str): The path to the file where the data will be saved.
            - points (numpy.ndarray): A NumPy array containing the sampled points.
            - normals (numpy.ndarray): A NumPy array containing the normal vectors for each point.
            - triangle_idxes (numpy.ndarray): A NumPy array containing the triangle indices.

            The data is saved using the `save_arrays` function in a compressed .npz format.
            """
        save_arrays(filename, points=np.asarray(self.pcd.points), normals=np.asarray(self.pcd.normals),
                    triangle_idxes=self.triangle_indexes)

    @staticmethod
    def load_from_file(filename: str) -> "SampledMesh":
        """
        Loads sampled point cloud from a .npz file.

        Parameters:
        - filename (str): The path to the .npz file containing the saved point cloud data.

        Returns:
            the SampledMesh object.
        """
        arrays = load_arrays(filename)
        points = arrays["points"]
        normals = arrays["normals"]
        tri_idxs = arrays["triangle_idxes"]

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.normals = o3d.utility.Vector3dVector(normals)

        return SampledMesh(pcd, tri_idxs)

    def get_points(self):
        if self.__points is None:
            self.__points = np.asarray(self.pcd.points)
        return self.__points

    def get_normals(self):
        if self.__normals is None:
            self.__normals = np.asarray(self.pcd.normals)
        return self.__normals

    def get_colors(self):
        if self.__colors is None:
            self.__colors = np.asarray(self.pcd.colors)
        return self.__colors

    def compute_centroid(self):
        """Computes the centroid of a point cloud."""
        return np.mean(self.get_points(), axis=0)

    def align_centroids(self, target: "SampledMesh"):
        """Generate the translation matrix to translate the source point cloud to align its centroid with the target's centroid."""
        source_centroid = self.compute_centroid()
        target_centroid = target.compute_centroid()

        translation = target_centroid - source_centroid
        transformation = np.eye(4)
        transformation[:3, 3] = translation  # Apply translation

        return transformation

    @staticmethod
    def __compute_signed_distance(point: np.ndarray, normal: np.ndarray, target_points: np.ndarray,
                                  target_normals: np.ndarray, target_tree: o3d.geometry.KDTreeFlann):
        """Compute the signed distance of one point"""
        [_, idx, dist] = target_tree.search_knn_vector_3d(point, 1)
        idx = idx[0]
        dist = np.asarray(dist)[0]
        nearest_point = target_points[idx]
        nearest_point_normal = target_normals[idx]

        dist_vector = nearest_point - point
        dot_product = np.dot(dist_vector, normal)
        # If angle is small the surfaces are perpendicular to each other, as fallback use the normal of the target point
        # If angle of vector is less than ~10° consider the normal vector of the target point
        if abs(dot_product) <= 0.15:
            dot_product = np.dot(dist_vector, nearest_point_normal)
        signed_distance = dist if dot_product >= 0 else -dist
        return signed_distance, idx

    @staticmethod
    def __compute_signed_distances_multiple_points(point: np.ndarray, normal: np.ndarray, target_points: np.ndarray,
                                   target_normals: np.ndarray, target_tree: o3d.geometry.KDTreeFlann):
        """Compute the signed distances from one point to its 5 nearest neighbors"""
        [_, idxs, dists_squared] = target_tree.search_knn_vector_3d(point, 5)

        nearest_points = target_points[idxs]  # shape: (5, 3)
        nearest_normals = target_normals[idxs]  # shape: (5, 3)
        dist_vectors = nearest_points - point  # shape: (5, 3)

        dot_products = np.einsum('ij,j->i', dist_vectors, normal)  # shape: (5,)

        # If angle is small the surfaces are perpendicular to each other, as fallback use the normal of the target point
        # If angle of vector is less than ~10° consider the normal vector of the target point
        use_fallback = np.abs(dot_products) <= 0.15
        fallback_dots = np.einsum('ij,ij->i', dist_vectors, nearest_normals)
        dot_products = np.where(use_fallback, fallback_dots, dot_products)

        dists = np.sqrt(dists_squared)
        signed_dists = np.where(dot_products >= 0, dists, -dists)

        return list(zip(signed_dists, idxs))

    def compute_chamfer_distances(self, target: "SampledMesh"):
        source_pcd_tree = o3d.geometry.KDTreeFlann(self.pcd)
        target_pcd_tree = o3d.geometry.KDTreeFlann(target.pcd)
        num_points = len(self.pcd.points)
        target_points = target.get_points()
        target_normals = target.get_normals()

        distances = np.zeros(num_points) # array of distances. Each point have a distance correlated to
        # --------- Calculate distances from source point cloud to target
        for i, (point, normal) in enumerate(zip(self.pcd.points, self.pcd.normals)):
            signed_distance, _ = self.__compute_signed_distance(point, normal, target_points, target_normals, target_pcd_tree)
            distances[i] = signed_distance

        # --------- Calculate distances from target to source
        source_points = self.get_points()
        source_normals = self.get_points()
        for point, normal in zip(target.pcd.points, target.pcd.normals):
            signed_distances = self.__compute_signed_distances_multiple_points(point, normal, source_points, source_normals,
                                                               source_pcd_tree)
            for signed_distance, idx in signed_distances:
                distances[idx] = float(distances[idx] - signed_distance) / 2.0  # mean distance

        return distances

    @staticmethod
    def from_mesh(mesh: MeshTools, num_samples: int):
        pcd, triangle_indexes = SampledMesh.__sample_points_uniformly(mesh, num_samples)
        return SampledMesh(pcd, triangle_indexes)

    @staticmethod
    def __sample_points_uniformly(mesh: MeshTools, num_samples: int) -> Tuple[o3d.geometry.PointCloud, np.array]:
        """
        Sample points uniformly on the triangles retaining normals.

        Args:
            mesh (o3d.geometry.TriangleMesh): Mesh of Open3D.
            num_samples (int): Total number of points.

        Returns:
            Tuple[o3d.geometry.PointCloud, np.array]:
                - Sampled point cloud
                - Indices of the triangle array of each point.
        """

        areas = mesh.calculate_triangle_areas()
        total_area = np.sum(areas)
        num_points_per_triangle = (areas / total_area * num_samples).astype(int)

        def process_triangle(i):
            """
            Process a triangle.
            Args:
                i:

            Returns:
                - array of points
                - array of normals of each point
                - indexes of triangle for each point
            """
            n_points = max(num_points_per_triangle[i], 1)  # At least 1 point per triangle

            n0, n1, n2 = mesh.get_triangle_normals(i)

            if n_points == 1:
                face_points = mesh.pick_point_in_triangle_center(i)
            else:
                face_points = mesh.sample_points_on_triangle(i, n_points)

            u, v, w = mesh.points_to_barycentric(face_points, np.tile(i, n_points))

            face_normals = u[:, None] * n0 + v[:, None] * n1 + w[:, None] * n2

            # --- prevent divide errors ---
            epsilon = 1e-10
            face_normals = np.nan_to_num(face_normals, nan=epsilon, posinf=1.0, neginf=-1.0)
            zero_indices = np.where(np.abs(face_normals) < epsilon)
            face_normals[zero_indices[0]] = epsilon
            # ---------------

            face_normals /= np.linalg.norm(face_normals, axis=1, keepdims=True)

            return face_points, face_normals, np.full(n_points, i)

        sampled_points = []
        sampled_normals = []
        triangle_idxes = []

        for idx in range(len(mesh.get_triangles())):
            points, normals, indices = process_triangle(idx)
            sampled_points.append(points)
            sampled_normals.append(normals)
            triangle_idxes.append(indices)

        triangle_idxes = np.hstack(triangle_idxes)
        points = np.vstack(sampled_points)
        normals = np.vstack(sampled_normals)

        # Create o3d point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.normals = o3d.utility.Vector3dVector(normals)

        return pcd, np.hstack(triangle_idxes)

    def colorize_by_distance(self, distances: np.ndarray, positive_breakpoints = None, negative_breakpoints = None):
        """
        Colorize points of poit cloud by the give distances. Distances are mapped using breakpoints

        Args:
            distances: distances in range [-1, 1]
            positive_breakpoints (np.ndarray): Array of breakpoints to use for positive values.
            negative_breakpoints (np.ndarray): Array of breakpoints to use for negative values.
        """

        points_color = HeatmapColors.get_color_from_value(distances, positive_breakpoints, negative_breakpoints)
        self.pcd.colors = o3d.utility.Vector3dVector(points_color[:, :3])

    def map_colors_to_texture(
            self,
            mesh: MeshTools,
            texture_dim: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Map point colors to a texture. The resulting texture will be almost completely black with colored pixels only in corresponding points

        Args:
            mesh (MeshTools): mesh object to generate texture.
            texture_dim (int): Dimension of the square texture (texture_dim x texture_dim).

        Returns:
            - np.ndarray: A texture image of shape (texture_dim, texture_dim, 3) with RGB values in [0, 255].
            - np.ndarray: A texture image of shape (texture_dim, texture_dim, 3) with 255 value only where the point is situated.
        """
        # ---- create uvs -----
        uv_map = mesh.get_uvs()
        texture = np.zeros((texture_dim, texture_dim, 3), dtype=np.uint8)
        positions = np.zeros((texture_dim, texture_dim, 4), dtype=np.uint8)
        vertices = mesh.get_vertices()
        triangles = mesh.get_triangles()
        points = self.get_points()
        # opencv handle colors as values in range 0, 255
        colors = (self.get_colors() * 255).astype(np.uint8)

        triangle_vertices = vertices[triangles[self.triangle_indexes]]

        a, b, c = mesh.points_to_barycentric(points, self.triangle_indexes)

        # get uv coordinates
        uv_idx = self.triangle_indexes * 3
        uv0 = uv_map[uv_idx]
        uv1 = uv_map[uv_idx + 1]
        uv2 = uv_map[uv_idx + 2]
        uv = a[:, None] * uv0 + b[:, None] * uv1 + c[:, None] * uv2
        # uv = np.clip(uv, 0, 1)

        u, v = uv[:, 0], uv[:, 1]
        # calculate x,y positions from uv coordinates
        xs = (u * (texture_dim - 1)).astype(int)
        ys = (v * (texture_dim - 1)).astype(int)
        texture[ys, xs] = colors
        positions[ys, xs] = [255, 255, 255, 255]

        return texture, positions

    def colorize_vertex_from_points(self, mesh: MeshTools):
        """
        Color vertex as the color of the first point inside face that vertex represent
        Args:
            mesh: Mesh to colorize.

        """
        vertices = mesh.get_vertices()
        triangles = mesh.get_triangles()
        colors = self.get_colors()

        # get color face as the color of the fist point inside the face. Set vertex colors accordingly
        face_colors = np.full((len(triangles), 3), np.nan)
        # Find first element that correspond to a face
        face_indexes, first_point_indexes = np.unique(self.triangle_indexes, return_index=True)
        # Each triangle have as color the color of the fist point inside
        face_colors[face_indexes] = colors[first_point_indexes]

        vertex_colors = np.zeros((len(vertices), 3))
        # get indexes of each vertex of the face
        face_vertex_indices = triangles[face_indexes].reshape(-1)
        # Each vertex of the face is colored as the color of the face (repeat 3 times)
        face_vertex_colors = np.repeat(face_colors[face_indexes], 3, axis=0)
        vertex_colors[face_vertex_indices] = face_vertex_colors

        mesh.mesh.vertex_colors = o3d.utility.Vector3dVector(vertex_colors[:, :3])
