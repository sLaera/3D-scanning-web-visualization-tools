import argparse
import os
import sys
from dsrb.set_paths import set_paths
import open3d as o3d
from tqdm import tqdm
import pymeshlab

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classes.AltecDataset import AltecDataset


def scan(args):
    set_paths(DATA_DIR=os.path.join(os.path.dirname(__file__), "dataset"),
              CPP_DIR=os.path.join(os.path.dirname(__file__), "externals"))
    ds = AltecDataset()
    models = ds.get_models()

    if args.mvs:
        print("------------------MVS------------------")
        print("Scan configuration 0 ...")
        ds.scan(scan_configuration="0")
        print("Scan configuration 1 ...")
        ds.scan(scan_configuration="1")
        print("Scan configuration 2 ...")
        ds.scan(scan_configuration="2")

    if args.lidar:
        print("------------------lidar------------------")
        ds.scan_lidar()

        print("Post processing ...")
        for s in ds.splits:
            models = models[s]
            for model in tqdm(models, ncols=50, file=sys.stdout):
                # --- scan configuration 2 ---
                out_file_path = str(model["scan_ply"]["2"])
                os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
                # The scans are saved in database/lidar-scan/model_name/[scan.off,scan_noisy.off]
                in_file_path = os.path.join(
                    ds.path, "lidar-scan", model["model"], "scan_noisy.off")
                ms = pymeshlab.MeshSet()
                ms.load_new_mesh(in_file_path)
                #ms.generate_simplified_point_cloud(samplenum=100000)
                ms.save_current_mesh(out_file_path, save_vertex_normal=True)

                # --- scan configuration 1 ---
                out_file_path = str(model["scan_ply"]["1"])
                ms.generate_simplified_point_cloud(samplenum=10000)
                ms.save_current_mesh(out_file_path, save_vertex_normal=True)

                # --- scan configuration 0 ---
                out_file_path = str(model["scan_ply"]["0"])
                os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
                # The scans are saved in database/lidar-scan/model_name/[scan.off,scan_noisy.off]
                in_file_path = os.path.join(
                    ds.path, "lidar-scan", model["model"], "scan.off")
                ms = pymeshlab.MeshSet()
                ms.load_new_mesh(in_file_path)
                #ms.generate_simplified_point_cloud(samplenum=100000)
                ms.save_current_mesh(out_file_path, save_vertex_normal=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--mvs", type=int, default=0,
                        help="Synthetic MVS scan")
    parser.add_argument("--lidar", type=int, default=1,
                        help="Synthetic LIDAR scan")
    args = parser.parse_args()
    scan(args)
