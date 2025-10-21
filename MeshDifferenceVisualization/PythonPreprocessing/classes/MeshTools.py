from typing import Tuple

import numpy as np
import open3d as o3d
import pymeshlab
import sys


class MeshTools:
    def __init__(self, mesh: o3d.geometry.TriangleMesh):
        self.mesh = mesh
        # The mesh geometry should not change, np arrays are precomputed in get functions and stored in private variables
        self.__vertex_array = None
        self.__triangles_array = None
        self.__normals_array = None

    #clear private values
    def clear_stored_data(self):
        self.__vertex_array = None
        self.__triangles_array = None
        self.__normals_array = None

    def scale_mesh_to_unit_cube(self):
        bbox = self.mesh.get_axis_aligned_bounding_box()
        bbox_extent = bbox.get_extent()  # [x, y, z] array with dimensions of bbox
        scale_factor = 1.0 / max(bbox_extent)
        center = bbox.get_center()

        translation_matrix = np.identity(4)
        translation_matrix[:3, 3] = -center  # Translate the center to the origin
        self.mesh.transform(translation_matrix)

        scale_matrix = np.identity(4)
        scale_matrix[:3, :3] = np.diag(
            [scale_factor, scale_factor, scale_factor])  # scale
        self.mesh.transform(scale_matrix)

        return self.mesh

    def simplify(self, num_vertices=100000):
        self.mesh.simplify_quadric_decimation(num_vertices)

    @staticmethod
    def load_mesh(path: str) -> "MeshTools":
        """
        Generate a new mesh tool from the mesh loaded from a file.
        Args:
            path: Path to the mesh file.

        Returns: MeshTools object.

        """
        mesh: o3d.geometry.TriangleMesh = o3d.io.read_triangle_mesh(path)
        mesh.compute_vertex_normals()
        return MeshTools(mesh)

    def calculate_triangle_areas(self) -> np.ndarray:
        """
        Compute the area of each triangle

        Returns:
            np.ndarray: Array of shape (T,) with the triangles' area.
        """
        vertices = self.get_vertices()
        triangles = self.get_triangles()

        v0 = vertices[triangles[:, 0]]
        v1 = vertices[triangles[:, 1]]
        v2 = vertices[triangles[:, 2]]
        cross_product = np.cross(v1 - v0, v2 - v0)
        areas = 0.5 * np.linalg.norm(cross_product, axis=1)
        return areas

    def get_vertices(self):
        if self.__vertex_array is None:
            self.__vertex_array = np.asarray(self.mesh.vertices)

        return self.__vertex_array

    def get_triangles(self):
        if self.__triangles_array is None:
            self.__triangles_array = np.asarray(self.mesh.triangles)
        return self.__triangles_array

    def get_vertex_normals(self):
        if self.__normals_array is None:
            self.__normals_array = np.asarray(self.mesh.vertex_normals)
        return self.__normals_array

    def get_uvs(self):
        return np.asarray(self.mesh.triangle_uvs)

    def get_triangle_vertices(self, triangle_index: int | np.ndarray) -> Tuple[np.array, np.array, np.array]:
        """
        Get vertices of triangle or multiple triangles by index
        Args:
            triangle_index (int): Index of triangle

        Returns:
            - First vertex coordinate
            - Second vertex coordinate
            - Third vertex coordinate
        """
        vertices = self.get_vertices()
        triangle = self.get_triangles()[triangle_index]
        if triangle.ndim == 1:
            return vertices[triangle[0]], vertices[triangle[1]], vertices[triangle[2]]
        else:
            return vertices[triangle[:, 0]], vertices[triangle[:, 1]], vertices[triangle[:, 2]]

    def get_triangle_normals(self, triangle_index: int | np.ndarray) -> Tuple[np.array, np.array, np.array]:
        """
        Get normals of triangle or multiple triangles by index
        Args:
            triangle_index (int): Index of triangle

        Returns:
            - First vertex normal
            - Second vertex normal
            - Third vertex normal
        """
        normals = self.get_vertex_normals()
        triangle = self.get_triangles()[triangle_index]
        return normals[triangle[0]], normals[triangle[1]], normals[triangle[2]]

    def pick_point_in_triangle_center(self, triangle_index: int) -> [np.ndarray]:
        """
            Generate a point in the center of a triangle.

            Args:
                triangle_index (int): index of the triangle to get center point from.

            Returns:
                np.ndarray: Sampled point, shape (1, 3).
            """
        v0, v1, v2 = self.get_triangle_vertices(triangle_index)
        return [(v0 + v1 + v2) / 3.0]

    def sample_points_on_triangle(self, triangle_index: int, num_samples: int) -> [np.ndarray]:
        """
        Generate points on a triangle in a uniform way.

        Args:
            triangle_index (int): index of the triangle to get center point from.
            num_samples (int): Number of points.

        Returns:
            [np.ndarray]: Sampled points, shape (num_samples, 3).
        """
        v0, v1, v2 = self.get_triangle_vertices(triangle_index)
        r1 = np.sqrt(np.random.rand(num_samples))
        r2 = np.random.rand(num_samples)
        u = 1 - r1
        v = r1 * (1 - r2)
        w = r1 * r2
        points = u[:, None] * v0 + v[:, None] * v1 + w[:, None] * v2
        return points

    def points_to_barycentric(
            self, points: np.ndarray, triangle_indexes: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate barycentric coordinates for multiple points with respect to multiple triangles.

        Args:
            points (np.ndarray): Array of shape (N, 3) containing the points.
            triangle_indexes (np.ndarray): Array of shape (N, 1) containing indexes of the triangles to get coordinates from.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]:
                - Array of shape (N, ) containing barycentric coordinates u for each point.
                - Array of shape (N, ) containing barycentric coordinates v for each point.
                - Array of shape (N, ) containing barycentric coordinates w for each point.
        """
        v0, v1, v2 = self.get_triangle_vertices(triangle_indexes)

        v0v1 = v1 - v0
        v0v2 = v2 - v0
        v0p = points - v0

        d00 = np.sum(v0v1 * v0v1, axis=1)
        d01 = np.sum(v0v1 * v0v2, axis=1)
        d11 = np.sum(v0v2 * v0v2, axis=1)
        d20 = np.sum(v0p * v0v1, axis=1)
        d21 = np.sum(v0p * v0v2, axis=1)

        denom = d00 * d11 - d01 * d01

        # --- prevent divide errors ---
        epsilon = 1e-10
        denom = np.nan_to_num(denom, nan=epsilon, posinf=1.0, neginf=-1.0)
        zero_indices = np.where(np.abs(denom) < epsilon)
        denom[zero_indices[0]] = epsilon
        # ---------------

        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w
        return u, v, w

    def generate_uv(self, textdim, border=0):
        """
        Generate an uv map using trivial per wedge
        :param textdim: Dimension of the texture
        :param border: border in pixel between faces in uv space
        :return: np.array: UV map
        """

        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(self.get_vertices(), self.get_triangles()))
        ms.compute_texcoord_parametrization_triangle_trivial_per_wedge(
            border=int(border), textdim=textdim)
        output_mesh = ms.current_mesh()
        v_uv = output_mesh.wedge_tex_coord_matrix()
        self.mesh.triangle_uvs = o3d.utility.Vector2dVector(v_uv)
        return v_uv
