import itertools
import time
from typing import cast
from dsrb.eval import MeshEvaluator
import shutil
import os
import sys
import subprocess
from tqdm import tqdm
import numpy as np
import open3d as o3d
import trimesh
from pathlib import Path
import traceback
import glob
import pandas as pd

from libmesh import check_mesh_contains
from dsrb import DefaultDataset

# fmt: off
# yapf: disable
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from scan_settings import scan_settings
# fmt: on
# yapf: enable


class BaseDataset(DefaultDataset):
    def __init__(self, dataset_folder_name, path=None, mesh_evaluator:MeshEvaluator = MeshEvaluator(), ext = ".off"):
        """Constructor of the Dataset Class

        Args:
            base_path (str): Name of the folder of the dataset
            path (str, optional): Path of the dataset. Defaults to None.
            mesh_evaluator (MeshEvaluator, optional): Mesh evaluator object. Used for custom evaluation settings
        """
        super().__init__()

        if path is not None:
            self.path = path
        else:
            self.path = os.path.join(self.path, dataset_folder_name)

        # read classes from file
        self.classes = []
        with open(os.path.join(self.path, "classes.lst"), 'r') as f:
            categories = f.read().split('\n')
        if '' in categories:
            categories.remove('')
        self.classes = categories
        self.all_classes = categories

        # Saves the paths of the models of the dataset. Used in get_models()
        self.model_dicts = {}
        
        self.me = mesh_evaluator
        
        self.ext = ext

    def get_classes(self):
        """Get the current used classes list

        Returns:
            list<str>: classes list
        """
        return self.classes

    def get_all_classes(self):
        """Get all the classes defined in the classes.lst file

        Returns:
            list<str>: classes list
        """
        return self.classes

    def set_classes(self, classes):
        """Set the list of current used classes

        Args:
            classes (list<str>): classes list
        """
        self.classes = [
            element for element in self.all_classes if element in classes]

    def get_models(self, disable_scaling=False):
        """Get a dict with all of the dataset's models information. By default it will scale the models to unit cube

        Args:
            disable_scaling (bool, optional): Do not scale the models

        Returns:
            {
                "default": {
                    [
                        {
                            ["path"]: Path of the root folder of the dataset
                            ["class"]: In this case the name of the class is the same as the name of the model
                            ["model"]: Name of the model
                            ["scan"][scan_configuration]: path to the scan npz (for each scan configuration)
                            ["scan_ply"][scan_configuration]: path to the scan ply (for each scan configuration)
                            ["eval"]["occ"]: path to the sampled point for the evaluation step
                            ["eval"]["pointcloud"]: path to the point cloud for the evaluation step
                            ["scaled"]: path to scaled model generated after the scale() function
                            ["mesh"]: Path to the mesh file. If `disable_scaling` is false this will be the path to the scaled mesh (["scaled"])
                            ["_mesh"]: Path to the original mesh file regardless of `disable_scaling` 
                            ["output"]["surface"]: Path to the reconstructed surface
                        }
                    ]
                }    
            }: a collection of object that contain the information of each model
        """
        # todo: implement test and train dataset split
        self.splits = ["default"]
        for s in self.splits:
            class_list = []
            for c in self.classes:
                # In this case a class represent a model in the dataset.
                d = {}
                d["path"] = self.path
                d["class"] = c
                d["model"] = c
                d["scan"] = {}
                d["scan_ply"] = {}
                for conf in scan_settings.keys():
                    d["scan"][conf] = os.path.join(
                        self.path, "scan", conf, c+".npz")
                    d["scan_ply"][conf] = os.path.join(
                        self.path, "scan_ply", conf, c+".ply")
                d["eval"] = {}
                d["eval"]["occ"] = os.path.join(
                    self.path, "eval", c, "points.npz")
                d["eval"]["pointcloud"] = os.path.join(
                    self.path, "eval", c, "pointcloud.npz")
                d["mesh"] = os.path.join(
                    self.path, c + self.ext)
                d["_mesh"] = d["mesh"]
                d["scaled"] = os.path.join(
                    self.path, "scaled", os.path.split(d["mesh"])[1])  # os.path.split(d["mesh"])[1] get the name of the mesh file
                d["output"] = {}
                d["output"]["surface"] = os.path.join(
                    self.path, '{}', c, s, "surface.obj")
                d["output"]["surface_simplified"] = os.path.join(
                    self.path, '{}', c, s, "surface_simplified.obj")  # unused
                class_list.append(d)

            self.model_dicts[s] = class_list

        print("Scaling ...")
        if not disable_scaling:
            self._scale()
            for s in self.splits:
                for m in self.model_dicts[s]:
                    m["mesh"] = m["scaled"]

        return self.model_dicts

    def _scale(self, force_rescan=False):
        """
        Scale mesh so that bounding box has a diagonal length of 1.
        Meshes are saved on the model_dicts["scaled"] path

        Args:
            force_rescan (bool, optional): Default false. If set to `false`, the function skips scanning files already present in the `scan` directory. If set to `true`, the function performs a full rescan and overwrites any existing files in the `scan` directory.
        """
        if (len(self.model_dicts) < 1):
            self.logger.error("run get_models() before scale().")
            return 1

        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        for s in self.splits:
            for m in tqdm(self.model_dicts[s], disable=self.tqdm_disabled, file=sys.stdout):
                file_path = str(m["scaled"])
                # skips files if already scanned
                if not force_rescan and os.path.exists(file_path):
                    tqdm.write("Already processed. Skipping " + m["model"])
                    continue

                mesh = o3d.io.read_triangle_mesh(m["mesh"])

                bb = mesh.get_axis_aligned_bounding_box()
                mesh = mesh.translate(-bb.get_center(), relative=True)

                minb = mesh.get_min_bound()
                maxb = mesh.get_max_bound()
                diag = np.linalg.norm(minb-maxb)

                mesh = mesh.scale(1/diag, center=(0, 0, 0))

                outfile = str(m["scaled"])
                os.makedirs(os.path.dirname(outfile), exist_ok=True)
                o3d.io.write_triangle_mesh(outfile, mesh)

    def make_eval(self, n_points=100000, unit=False, surface=True, occ=True, force_rescan=False):
        """Sample points from mesh surface. Need on the evaluation phase

        Args:
            n_points (int, optional): number of points. Defaults to 100000.
            unit (bool, optional): If the mesh is scaled in the unit cube. Defaults to False.
            surface (bool, optional): Sample the surface points. Defaults to True.
            occ (bool, optional): Sample points for IOU. Defaults to True.
            force_rescan (bool, optional): Default false. If set to `false`, the function skips scanning files already present in the `scan` directory. If set to `true`, the function performs a full rescan and overwrites any existing files in the `scan` directory.
        """
        from libmesh import check_mesh_contains

        self.logger.info(
            "Sample points on ground truth surface and in bounding box for evaluation...")

        if (len(self.model_dicts) < 1):
            self.logger.error("run get_models() before make_eval().")
            return 1

        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        for s in self.splits:
            for m in tqdm(self.model_dicts[s], file=sys.stdout):

                file_path_point_cloud = str(m["eval"]["pointcloud"])
                file_pat_occ = str(m["eval"]["occ"])

                try:

                    # if not unit:
                    #     m["mesh"] = m["ori_mesh"]
                    mesh = trimesh.load(m["mesh"])
                    mesh = cast(trimesh.Trimesh, mesh)
                    fpath = os.path.dirname(m["eval"]["pointcloud"])
                    os.makedirs(fpath, exist_ok=True)

                    if surface:
                        # skips files if already make eval
                        if not force_rescan and os.path.exists(file_path_point_cloud):
                            tqdm.write(
                                "Surface already processed. Skipping " + m["model"])
                            continue

                        # surface points
                        points_surface, fid = mesh.sample(
                            n_points, return_index=True)
                        normals = mesh.face_normals[fid]

                        np.savez_compressed(
                            m["eval"]["pointcloud"], points=points_surface, normals=normals)

                        if self.debug_export:
                            print('Writing points: %s' %
                                  m["eval"]["pointcloud"])
                            pcd = o3d.geometry.PointCloud()
                            pcd.points = o3d.utility.Vector3dVector(
                                points_surface)
                            pcd.normals = o3d.utility.Vector3dVector(normals)
                            o3d.io.write_point_cloud(
                                str(Path(m["eval"]["pointcloud"]).with_suffix(".ply")), pcd)

                    # IoU points
                    if occ:
                        # skips files if already make eval
                        if not force_rescan and os.path.exists(file_pat_occ):
                            tqdm.write(
                                "OCC already processed. Skipping " + m["model"])
                            continue

                        n_points_uniform = int(n_points * 0.5)
                        n_points_surface = n_points - n_points_uniform

                        if not unit:
                            o3dmesh = o3d.io.read_triangle_mesh(m["mesh"])
                            o3dmesh = o3dmesh.scale(1.1, o3dmesh.get_center())
                            min = o3dmesh.get_min_bound()
                            max = o3dmesh.get_max_bound()
                            points_uniform = np.random.uniform(
                                low=min, high=max, size=(n_points_uniform, 3))
                            points_surface = mesh.sample(n_points_surface)
                            points_surface += 0.05 * \
                                np.random.randn(n_points_surface, 3) * \
                                np.linalg.norm(min-max)
                        else:
                            points_uniform = np.random.rand(
                                n_points_uniform, 3)
                            points_uniform = points_uniform - 0.5
                            points_surface = mesh.sample(n_points_surface)
                            points_surface += 0.05 * \
                                np.random.randn(n_points_surface, 3)

                        points = np.concatenate(
                            [points_uniform, points_surface], axis=0)

                        occupancies = check_mesh_contains(mesh, points)

                        colors = np.zeros(shape=(n_points, 3)) + [0, 0, 1]
                        colors[occupancies] = [1, 0, 0]

                        dtype = np.float16
                        points = points.astype(dtype)
                        occupancies = np.packbits(occupancies)

                        np.savez_compressed(
                            m["eval"]["occ"], points=points, occupancies=occupancies)

                        if self.debug_export:
                            print('Writing points: %s' % m["eval"]["occ"])
                            pcd = o3d.geometry.PointCloud()
                            pcd.points = o3d.utility.Vector3dVector(points)
                            pcd.colors = o3d.utility.Vector3dVector(colors)
                            o3d.io.write_point_cloud(
                                str(Path(m["eval"]["occ"]).with_suffix(".ply")), pcd)

                except Exception:
                    # raise e
                    print("Problem with {}".format(m["model"]))
                    traceback.print_exc()
                    return 1

    def scan(self, scan_configuration="0", force_rescan=False, use_scaled=True):
        """Generate a synthetic MVS scan of the models of the datasets. The meshes must be manifold

        Args:
            scan_configuration (str, optional): string value with this possible alternatives:
                "0": 100000 points with no noise or outliers
                "1": 10000 points with dev 0.005 gaussian noise,  0.01 outliers
                "2": 100000 points with dev 0.005 gaussian noise,  0.01 outliers
            force_rescan (bool, optional): Default false. If set to `false`, the function skips scanning files already present in the `scan` directory. If set to `true`, the function performs a full rescan and overwrites any existing files in the `scan` directory.
            use_scaled (bool, optional): If `True` will load models from the "scaled" folder otherwise from "mesh" folder
        """
        self.logger.info("Scan ground truth surface...")

        # the scan is performed by the mesh-tool scan tool
        scan_exe = os.path.join(self.mesh_tools_dir, "scan")
        if not os.path.isfile(scan_exe):
            self.logger.error(
                "Could not find {}. Please install mesh-tools from here: https://github.com/raphaelsulzer/mesh-tools.git".format(scan_exe))
            return 1

        if (len(self.model_dicts) < 1):
            self.logger.error("run get_models() before scan().")
            return 1

        scan = scan_settings[scan_configuration]

        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        for s in self.splits:
            models = self.model_dicts[s]
            for model in tqdm(models, ncols=50, file=sys.stdout):
                file_path = str(model["scan"][scan_configuration])
                # skips files if already scanned
                if not force_rescan and os.path.exists(file_path):
                    tqdm.write("Already scanned. Skipping " + model["model"])
                    continue
                try:
                    os.makedirs(os.path.dirname(
                        model["scan"][scan_configuration]), exist_ok=True)
                    # execute the mesh-tool scan command
                    input_path = model["scaled"] if use_scaled else model["mesh"]
                    command = [str(scan_exe),
                               "-i", str(input_path),
                               "-o", str(model["scan"]
                                         [scan_configuration][:-4]),
                               "--points", scan["points"],
                               "--noise", scan["noise"],
                               "--outliers", scan["outliers"],
                               "--cameras", scan["cameras"],
                               "--normal_neighborhood", "30",
                               "--normal_method", "jet",
                               "--normal_orientation", "1",
                               "--export", "all",
                               "-e", "n"]
                    if self.logger.level < 20:
                        print(*command)
                        p = subprocess.Popen(command)
                    else:
                        p = subprocess.Popen(
                            command, stdout=subprocess.DEVNULL)
                    p.wait()
                    # the scan command generates .npz files. The files are converted to ply and put in the scn_ply folder
                    os.makedirs(os.path.dirname(
                        model["scan_ply"][scan_configuration]), exist_ok=True)
                    os.rename(model["scan"][scan_configuration].replace(
                        ".npz", ".ply"), model["scan_ply"][scan_configuration])
                except Exception as e:
                    # raise e
                    print(e)
                    print(
                        "Skipping {}/{}".format(model["class"], model["model"]))

    def scan_lidar(self, force_rescan=False):
        # ---mesh preprocessing---
        # convert the meshes to obj format
        obj_folder = os.path.join(self.path, "objs")
        os.makedirs(obj_folder, exist_ok=True)
        for s in self.splits:
            models = self.model_dicts[s]
            print("Preprocessing ...")

            for model in tqdm(models, ncols=50, file=sys.stdout):

                if not force_rescan and os.path.exists(os.path.join(
                    obj_folder, model["model"] + ".obj")):
                    tqdm.write("skipping prep " + model["model"])
                    continue

                mesh = o3d.io.read_triangle_mesh(model["mesh"])
                o3d.io.write_triangle_mesh(os.path.join(
                    obj_folder, model["model"] + ".obj"), mesh)

        shutil.copyfile(os.path.join(self.path, "classes.lst"), os.path.join(
            obj_folder, "classes.lst"))  # the lst file must be in the obj folder

        # --- lidar simulation ---
        # input path to the lst file
        input_path = os.path.join(obj_folder, "classes.lst")
        output_folder = os.path.join(self.path, "lidar-scan")
        os.makedirs(output_folder, exist_ok=True)

        # chmod
        p = subprocess.Popen(["chmod 755 " + str(self.lidar_exe)], shell=True)
        p.wait()

        # Models are scaled by 10 to match Unity dimensions
        # 1 unit = 2 m if the satellite is 2m large
        command = [str(self.lidar_exe),
                   "-in_path", str(input_path),
                   "-out_dir", output_folder,
                   "-gaussian_noise", "0.003",  # <1cm -> 2m * 0.0003unit = 0.6 cm
                   "-distance_noise_amplitude", "0.001",  # <0.1% of distance
                   "-outlier_probability", "0.0",
                   "-random_rotation", "true",
                   "-save_frames", "false",
                   "-rescans", "4",
                   "-rotation_for_rescan", "5",
                   "-fov", "20",
                   "-ray_rows", "128",
                   "-ray_col", "128",
                   "-sensor_speed", "0.1", # it's the percentage of the path traveled from one frame to the other
                   "-path_scale", "50"  # 50m distance -> 100m diameter path -> 50 unit * 2 = 100m
                   ]
        if self.logger.level < 20:
            print(*command)
            p = subprocess.Popen(command)
        else:
            p = subprocess.Popen(
                command, stdout=subprocess.DEVNULL)
        p.wait()
        print("Scan completed")
        print("Logs are written in `externals/virtual_lidar/Build/Build_Data/StreamingAssets/log.txt`")

    def makePoisson(self, depth=8, boundary=2, scan_configuration="0"):

        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        times = {}
        
        for s in self.splits:
            models = self.model_dicts[s]
            for m in tqdm(models, ncols=50):
                out_path = m["output"]["surface"].format("spsr")

                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                command = [self.poisson_exe,
                           "--in", m["scan_ply"][scan_configuration],
                           "--out", out_path,
                           "--depth", str(depth),
                           "--bType", str(boundary)]

                start_time = time.time()
                p = subprocess.Popen(command)
                p.wait()

                mesh = o3d.io.read_triangle_mesh(out_path + ".ply")
                o3d.io.write_triangle_mesh(out_path, mesh)
                times[m["model"]] = time.time() - start_time
        
        return times
                
    def eval_poisson(self):
        results = {}
        for s in self.splits:
            results[s] = self.me.eval(self.model_dicts[s], outpath=self.path,
                                 method="spsr")
        return results

    def makeLabatut(self, sigma=0.001, lam=5, alpha=32, scan_configuration="0", ignore_out = False):
        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        times = {}

        for s in self.splits:
            models = self.model_dicts[s]
            for m in tqdm(models, ncols=50):
                out_path = m["output"]["surface"].format("resr")

                s = sigma
                l = lam
                a = alpha
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                command = [self.labatut_exe,
                           "-i", m["scan_ply"][scan_configuration],
                           "-o", out_path,
                           "-s", "ply",
                           "--sigma", str(s),
                           "--alpha", str(a),
                           "--gco", "angle-"+str(l),
                           "--closed", "1"]
                start_time = time.time()
                if ignore_out:
                    p = subprocess.Popen(command, stdout=subprocess.DEVNULL)
                else:
                    p = subprocess.Popen(command)
                p.wait()

                # find the output file
                # the output file has a ending part like "_rt_5.0"
                file_paths = glob.glob(out_path + "*.ply")

                mesh = o3d.io.read_triangle_mesh(file_paths[0])
                o3d.io.write_triangle_mesh(out_path, mesh)
                os.remove(file_paths[0]) # clean up
                times[m["model"]] = time.time() - start_time
        return times
                
    def eval_labatut(self):
        results = {}
        for s in self.splits:
            results[s] = self.me.eval(self.model_dicts[s], outpath=self.path,
                                 method="resr")
        return results

    def grid_search_poisson(self, grid, scan_configuration, metric_f=(lambda iou, normal_consistency, chamfer_distance: iou)):
        """Perform a grid search over the depth and boundary parameters of the screed poisson surface reconstruction

        Args:
            grid (dict): A dictionary of the depth and boundary values. <br/> es: 
                {
                    'depth': [6, 8, 10, 12],
                    'boundary': [0, 1, 2],
                }
            metric_f ((iou, normal_consistency,chamfer_distance) -> float, optional): function that calculate the metric to be maximized.

        Returns:
            ({['depth', float] ['boundary', float]}, float): return the best params and the best metric
        """
        def remesh_f(params, scan_configuration): return self.makePoisson(
            scan_configuration=scan_configuration, depth=params["depth"], boundary=params["boundary"])

        def eval_f(): return self.eval_poisson()["default"]

        return self._grid_search(grid, scan_configuration, metric_f, remesh_f, eval_f)

    def grid_search_labatut(self, grid, scan_configuration, metric_f=lambda iou, normal_consistency, chamfer_distance: iou):
        """Perform a grid search over alpha sigma and lambda parameters of the labatut reconstruction

        Args:
            grid (dict): A dictionary of alpha sigma and lambda values. <br/> es: 
                {
                    'alpha': [16, 32, 48],
                    'sigma': [0.001, 0.01, 0.1, 1],
                    'lam': [1.5, 2.5, 5, 10]
                }
            metric_f ((iou, normal_consistency,chamfer_distance) -> float, optional): function that calculate the metric to be maximized.

        Returns:
            ({['alpha', float], ['sigma', float], ['lambda', float]}, float): return the best params and the best metric
        """
        def remesh_f(params, scan_configuration): return self.makeLabatut(
            scan_configuration=scan_configuration, alpha=params["alpha"], sigma=params["sigma"], lam=params["lam"], ignore_out=True)

        def eval_f(): return self.eval_labatut()["default"]

        return self._grid_search(grid, scan_configuration, metric_f, remesh_f, eval_f)

    def _grid_search(self, grid, scan_configuration, metric_f=lambda iou, normal_consistency, chamfer_distance: iou, remesh_f=lambda params, scan_configuration: print("To implement"), eval_f=lambda: print("To implement")):
        best_metric = 0
        best_params = None

        for params in tqdm(itertools.product(*grid.values()), ncols=50):
            try:
                remesh_f(dict(zip(grid.keys(), params)), scan_configuration)
                result, _ = eval_f()

                # extract mean results
                iou = result.loc['mean', 'iou']
                normal_consistency = result.loc['mean', 'Normal Consistency']
                chamfer_distance = result.loc['mean', 'Chamfer (x10^2)']

                metric = metric_f(iou, normal_consistency, chamfer_distance)

                if metric > best_metric:
                    best_metric = metric
                    best_params = dict(zip(grid.keys(), params))

                tqdm.write(f"Current: {params} => Metric: {metric}")
                tqdm.write(f"Best: {best_params} => Metric: {best_metric}")
            except Exception:
                print("GRID search. Problem with {}".format(scan_configuration))
                traceback.print_exc()

        return best_params, best_metric

    def make_ball_pivoting(self, scan_configuration="0", mean_distance_weight=3, radius_w1=0.01, radius_w2=0.5, radius_w3=1, radius_w4=2):

        # radii = [0.005, 0.01, 0.02, 0.04]
        # rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
        #     pcd, o3d.utility.DoubleVector(radii))
        # o3d.visualization.draw_geometries([pcd, rec_mesh])

        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        times = {}

        for s in self.splits:
            models = self.model_dicts[s]
            for m in tqdm(models, ncols=50):
                out_path = m["output"]["surface"].format("bpivot")

                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                start_time = time.time()
                
                point_cloud = o3d.io.read_point_cloud(
                    m["scan_ply"][scan_configuration])
                # --- calculating mean point distance ---
                distances = point_cloud.compute_nearest_neighbor_distance()
                mean_distance = np.mean(distances)
                radius = mean_distance * mean_distance_weight

                radii = [radius * radius_w1, radius * radius_w2,
                         radius * radius_w3, radius * radius_w4]
                mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(
                    point_cloud, o3d.utility.DoubleVector(radii))
                mesh.triangle_normals = o3d.utility.Vector3dVector([])
                
                o3d.io.write_triangle_mesh(out_path, mesh)
                
                times[m["model"]] = time.time() - start_time
        return times

    def eval_ball_pivot(self):
        results = {}
        for s in self.splits:
            results[s] = self.me.eval(self.model_dicts[s],
                                 outpath=self.path, method="bpivot")
        return results

    def grid_search_ball_pivot(self, grid, scan_configuration, metric_f=lambda iou, normal_consistency, chamfer_distance: iou):
        """Perform a grid search over various radius sizes by changing mean distance weight and various radius weight parameters fro ball pivoting reconstruction

        Args:
            grid (dict): A dictionary of mean distance weight and radios weights. <br/> es: 
                {
                    'mean_distance_weight': [1, 2, 3],
                    'radius_w1': [0.01, 0.1],
                    'radius_w2': [0.2, 0.5],
                    'radius_w3': [1, 2],
                    'radius_w4': [2, 5],
                }
            metric_f ((iou, normal_consistency,chamfer_distance) -> float, optional): function that calculate the metric to be maximized.

        Returns:
            ({['alpha', float], ['sigma', float], ['lambda', float]}, float): return the best params and the best metric
        """
        def remesh_f(params, scan_configuration): return self.make_ball_pivoting(
            scan_configuration=scan_configuration, mean_distance_weight=params["mean_distance_weight"], radius_w1=params["radius_w1"], radius_w2=params["radius_w2"], radius_w3=params["radius_w3"], radius_w4=params["radius_w4"])

        def eval_f(): return self.eval_ball_pivot()["default"]

        return self._grid_search(grid, scan_configuration, metric_f, remesh_f, eval_f)
    
    
    def make_advancing_front(self, radius_ratio_bound=2, beta=0.125, scan_configuration="0", ignore_out = False):
        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        times = {}

        for s in self.splits:
            models = self.model_dicts[s]
            for m in tqdm(models, ncols=50):
                out_path = m["output"]["surface"].format("advancing")

                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                exe_path = os.path.join(self.mesh_tools_dir, "..", "..", "..", "cgal-reconstruction", "build", "Reconstruct")
                command = [exe_path,
                           "-in", str(m["scan_ply"][scan_configuration]),
                           "-out", str(out_path),
                           "-method", str(0),
                           "radius_ratio_bound", str(radius_ratio_bound),
                           "-beta", str(beta)]
                
                start_time = time.time()
                if ignore_out:
                    p = subprocess.Popen(command, stdout=subprocess.DEVNULL)
                else:
                    p = subprocess.Popen(command)
                p.wait()

                mesh = cast(trimesh.Trimesh, trimesh.load(out_path + ".off"))
                mesh.fix_normals()
                mesh.export(out_path)
                times[m["model"]] = time.time() - start_time
        return times
                
    def eval_advancing_front(self):
        results = {}
        for s in self.splits:
            results[s] = self.me.eval(self.model_dicts[s],
                                 outpath=self.path, method="advancing")
        return results

    def grid_search_advancing_front(self, grid, scan_configuration, metric_f=lambda iou, normal_consistency, chamfer_distance: iou):
        
        def remesh_f(params, scan_configuration): return self.make_advancing_front(
            scan_configuration=scan_configuration, radius_ratio_bound=params["radius_ratio_bound"], beta=params["beta"])

        def eval_f(): return self.eval_advancing_front()["default"]

        return self._grid_search(grid, scan_configuration, metric_f, remesh_f, eval_f)
    
    
    def make_scale_space(self, maximum_facet_length=0.5, iterations=4, scan_configuration="0", ignore_out = False):
        if self.splits is None:
            self.splits = ["default"]
            md = {}
            md["default"] = self.model_dicts
            self.model_dicts = md

        times = {}

        for s in self.splits:
            models = self.model_dicts[s]
            for m in tqdm(models, ncols=50):
                out_path = m["output"]["surface"].format("scale_space")

                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                exe_path = os.path.join(self.mesh_tools_dir, "..", "..", "..", "cgal-reconstruction", "build", "Reconstruct")
                command = [exe_path,
                           "-in", m["scan_ply"][scan_configuration],
                           "-out", out_path,
                           "-method", "1",
                           "-iterations", str(iterations),
                           "-maximum_facet_length", str(maximum_facet_length)]
                start_time = time.time()
                if ignore_out:
                    p = subprocess.Popen(command, stdout=subprocess.DEVNULL)
                else:
                    p = subprocess.Popen(command)
                p.wait()

                mesh = cast(trimesh.Trimesh, trimesh.load(out_path + ".off"))
                mesh.fix_normals()
                mesh.export(out_path)
                times[m["model"]] = time.time() - start_time
        return times
                
    def eval_scale_space(self):
        results = {}
        for s in self.splits:
            results[s] = self.me.eval(self.model_dicts[s],
                                 outpath=self.path, method="scale_space")
        return results

    def grid_search_scale_space(self, grid, scan_configuration, metric_f=lambda iou, normal_consistency, chamfer_distance: iou):
        
        def remesh_f(params, scan_configuration): return self.make_scale_space(
            scan_configuration=scan_configuration, iterations=params["iterations"], maximum_facet_length=params["maximum_facet_length"])

        def eval_f(): return self.eval_scale_space()["default"]

        return self._grid_search(grid, scan_configuration, metric_f, remesh_f, eval_f)