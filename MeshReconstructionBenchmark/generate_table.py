import pandas as pd
import sys
import os
from dsrb.set_paths import set_paths

# fmt: off
# yapf: disable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classes.DefaultDataset import DefaultDataset
from classes.scan_settings import scan_settings
# fmt: on
# yapf: enable

set_paths(DATA_DIR=os.path.join(os.path.dirname(__file__), "dataset"),
              CPP_DIR=os.path.join(os.path.dirname(__file__), "externals"))


ds = DefaultDataset()
ds.get_models()

results_folder = os.path.join(ds.path, "results", '{}')
unoptimized_result_path = os.path.join(results_folder, "no_optimization.cvs")
optimized_result_path = os.path.join(results_folder, "optimized.csv")

merged = []

for config in scan_settings:
    for method in ["spsr", "resr", "bpivot", "advancing", "scale_space"]:
        unoptim_path = unoptimized_result_path.format(f"{method}_{config}")
        optim_path = optimized_result_path.format(f"{method}_{config}")
        
        unoptim = pd.read_csv(unoptim_path)
        optim = pd.read_csv(optim_path)
        
        for model in ds.model_dicts["default"]:
            model_name = model["model"]
            
            unoptim_iou = unoptim.loc[unoptim["model"] == model_name, 'iou'].values[0]
            unoptim_normal_consistency = unoptim.loc[unoptim["model"] == model_name, 'Normal Consistency'].values[0]
            unoptim_chamfer_distance = unoptim.loc[unoptim["model"] == model_name, 'Chamfer (x10^2)'].values[0]
            
            optim_iou = optim.loc[optim["model"] == model_name, 'iou'].values[0]
            optim_normal_consistency = optim.loc[optim["model"] == model_name, 'Normal Consistency'].values[0]
            optim_chamfer_distance = optim.loc[optim["model"] == model_name, 'Chamfer (x10^2)'].values[0]
            
            merged.append({
                "config": config,
                "method": method,
                "model": model_name,
                "iou unoptim": unoptim_iou,
                "iou optim": optim_iou,
                "distance unoptim": unoptim_chamfer_distance,
                "distance optim": optim_chamfer_distance,
                "normal consistency unoptim": unoptim_normal_consistency,
                "normal consistency optim": optim_normal_consistency,
                "optimization improvement": ""
            })
            
        unoptim_mean_iou = unoptim.loc[unoptim.iloc[:, 0] == "mean", 'iou'].values[0]
        unoptim_mean_normal_consistency = unoptim.loc[unoptim.iloc[:, 0] == "mean", 'Normal Consistency'].values[0]
        unoptim_mean_chamfer_distance = unoptim.loc[unoptim.iloc[:, 0] == "mean", 'Chamfer (x10^2)'].values[0]

        optim_mean_iou = optim.loc[optim.iloc[:, 0] == "mean", 'iou'].values[0]
        optim_mean_normal_consistency = optim.loc[optim.iloc[:, 0] == "mean", 'Normal Consistency'].values[0]
        optim_mean_chamfer_distance = optim.loc[optim.iloc[:, 0] == "mean", 'Chamfer (x10^2)'].values[0]
        
        merged.append({
            "config": config,
            "method": method,
            "model": "mean",
            "iou unoptim": unoptim_mean_iou,
            "iou optim": optim_mean_iou,
            "distance unoptim": unoptim_mean_chamfer_distance,
            "distance optim": optim_mean_chamfer_distance,
            "normal consistency unoptim": unoptim_mean_normal_consistency,
            "normal consistency optim": optim_mean_normal_consistency,
            # "optimization improvement": ((optim_mean_iou - unoptim_mean_iou) + ( optim_mean_normal_consistency - unoptim_mean_normal_consistency) - (optim_mean_chamfer_distance - unoptim_mean_chamfer_distance))/3
            "optimization improvement": optim_mean_iou - unoptim_mean_iou
        })
        
        #empty line
        merged.append({
            "config": "",
            "method": "",
            "model": "",
            "iou unoptim": "",
            "iou optim": "",
            "distance unoptim": "",
            "distance optim": "",
            "normal consistency unoptim": "",
            "normal consistency optim": "",
            "optimization improvement": ""
        })


pd.DataFrame(merged).to_csv(results_folder.format("merged_results.csv"))