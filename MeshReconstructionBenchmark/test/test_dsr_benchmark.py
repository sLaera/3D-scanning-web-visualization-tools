import os
import open3d as o3d

from dsrb.eval import MeshEvaluator
from dsrb.set_paths import set_paths

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "classes"))
from BergerTest import BergerTest

def test():
    print('-------------------------------------------------------------------------------------')
    print('This script tests that the metric evaluation works fine.\n This will load models from a small sample, already included, of Berger dataset and compute the evaluation of Poisson reconstruction')
    print('-------------------------------------------------------------------------------------')
    # note that, here we do not actually use the data in data_dir, but the small sample set included in the repo
    set_paths(DATA_DIR= os.path.join(os.path.dirname(__file__), "..", "dataset"),CPP_DIR=os.path.join(os.path.dirname(__file__), "..", "externals"))

    # note necessary to provide if set_paths is called. here we override the path from set_paths
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "dsr-benchmark", "test", "reconbench")
    ds = BergerTest(path=dataset_path)
    print('Reading models ...')
    models = ds.get_models(scan_configuration="mvs")
    ds.make_eval()
    ds.scan(scan_configuration="mvs")

    print('Remeshing ...')
    for model in models:
        # make a Poisson reconstruction with open3d
        pcd = o3d.io.read_point_cloud(model["scan_ply"])
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=6)
        os.makedirs(os.path.dirname(model["output"]["surface"].format("poisson")),exist_ok=True)
        o3d.io.write_triangle_mesh(model["output"]["surface"].format("poisson"),mesh)
    print('Evaluating ...')
    ev = MeshEvaluator()
    results_full, results_class = ev.eval(models,outpath=ds.path,method="poisson")
    print(results_full)
