import os
from dsrb.eval import MeshEvaluator
from dsrb.set_paths import set_paths

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classes.BergerTest import BergerTest


def test():
    set_paths(DATA_DIR= os.path.join(os.path.dirname(__file__), "..", "dataset"),CPP_DIR=os.path.join(os.path.dirname(__file__), "..", "externals"))
    dataset_path = os.path.join(os.path.dirname(
        __file__), "..", "dsr-benchmark", "test", "reconbench")
    ds = BergerTest(path=dataset_path)
    print('Reading models ...')
    models = ds.get_models(scan_configuration="mvs")
    ds.make_eval()
    ds.test_scan(scan_configuration="mvs")

    print('Remeshing ...')
    ds.makePoisson(outf=lambda m, self:
                   m["output"]["surface"].format("ScreenedPoisson"))

    print('Evaluating ...')
    ev = MeshEvaluator()
    results_full, results_class = ev.eval(
        models, outpath=ds.path, method="ScreenedPoisson")
    print(results_full)

