import argparse
import itertools
import os
import shutil
import sys
from dsrb.set_paths import set_paths
import pandas as pd
from tqdm import tqdm
from dsrb.eval import MeshEvaluator

# fmt: off
# yapf: disable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classes.AltecDataset import AltecDataset
from classes.scan_settings import scan_settings
# fmt: on
# yapf: enable


def calculate_composite_metric(iou, normal_consistency, ch_distance, w_iou=0.4,  w_normal=0.2, w_ch=0.4, k=1):
    # """
    # calculate a composite metric base on the iou, normal consistency and Chamfer distance.

    # Args:
    #     iou (float): IOU value between 0 and 1
    #     normal_consistency (float): normal consistency value between 0 and 1.
    #     ch_distance (float): Chamfer distance.
    #     w_iou (float): weight for iou value
    #     w_normal (float): weight for normal consistency value
    #     w_ch (float): weight for Chamfer distance value
    #     k (float): value to not make the nearness metric infinite.

    # Return:
    #     composite value.
    # """

    # composite_value = (w_iou * iou) + (w_normal * normal_consistency) + (w_ch*(1 / (ch_distance + k)))
    composite_value = iou
    return composite_value


grid_spsr = {
    'depth': [6, 8, 10, 12],
    'boundary': [1, 2, 3],
}

grid_resr = {
    'alpha': [16, 32, 48],
    'sigma': [0.001, 0.01, 0.1, 1],
    'lam': [1.5, 2.5, 5, 10]
}

grid_ball_pivot = {
    'mean_distance_weight': [1, 2, 3],
    'radius_w1': [0.01, 0.1],
    'radius_w2': [0.2, 0.5],
    'radius_w3': [1, 2],
    'radius_w4': [2, 5],
}

grid_advancing_front = {
    'radius_ratio_bound': [0.5, 1, 2, 4],
    'beta': [0.01, 0.1, 0.5],
}

grid_scale_space = {
    'iterations': [1,2,3,4],
    'maximum_facet_length': [0.5,1,2,5,10],
}

NUMBER_POINTS_FOR_EVALUATION = 100000

def eval(args):
    set_paths(DATA_DIR=os.path.join(os.path.dirname(__file__), "dataset"),
              CPP_DIR=os.path.join(os.path.dirname(__file__), "externals"))

    ds = AltecDataset(mesh_evaluator=MeshEvaluator(n_points=NUMBER_POINTS_FOR_EVALUATION))
    models = ds.get_models()
    print("Sample points for eval ...")
    if (ds.make_eval(n_points=NUMBER_POINTS_FOR_EVALUATION) == 1):
        raise Exception("Evaluation step not completed correctly")

    results_folder = os.path.join(ds.path, "results", '{}')
    unoptimized_result_path = os.path.join(
        results_folder, "no_optimization.csv")
    unoptimized_models_folder = os.path.join(
        results_folder, "models", "no_optimization")
    optimized_result_path = os.path.join(results_folder, "optimized.csv")
    optimized_models_folder = os.path.join(
        results_folder, "models", "optimized")
    
    if not args.search_only:
        for config in scan_settings:
            if args.all or args.spsr:
                print(
                    f"---------------------Evaluating SPSR without optimization. config: {config}---------------------------")
                ds.makePoisson(scan_configuration=config)
                results = ds.eval_poisson()
                # --- save in a predefine folder for easy access ---
                save_results(ds, "spsr", unoptimized_result_path,
                            unoptimized_models_folder, config, results)

            if args.all or args.resr:
                print(
                    f"---------------------Evaluating RESR without optimization. config: {config}---------------------------")
                ds.makeLabatut(scan_configuration=config, ignore_out=True)
                results = ds.eval_labatut()
                # --- save in a predefine folder for easy access ---
                save_results(ds, "resr", unoptimized_result_path,
                            unoptimized_models_folder, config, results)
            
            if args.all or args.bpivot:
                print(
                    f"---------------------Evaluating bpivot without optimization. config: {config}---------------------------")
                ds.make_ball_pivoting(scan_configuration=config)
                results = ds.eval_ball_pivot()
                # --- save in a predefine folder for easy access ---
                save_results(ds, "bpivot", unoptimized_result_path,
                            unoptimized_models_folder, config, results)
            
            if args.all or args.advancing:
                print(
                    f"---------------------Evaluating advancing front without optimization. config: {config}---------------------------")
                ds.make_advancing_front(scan_configuration=config)
                results = ds.eval_advancing_front()
                # --- save in a predefine folder for easy access ---
                save_results(ds, "advancing", unoptimized_result_path,
                            unoptimized_models_folder, config, results)
            
            if args.all or args.scale_space:
                print(
                    f"---------------------Evaluating scale space without optimization. config: {config}---------------------------")
                ds.make_scale_space(scan_configuration=config)
                results = ds.eval_scale_space()
                # --- save in a predefine folder for easy access ---
                save_results(ds, "scale_space", unoptimized_result_path,
                            unoptimized_models_folder, config, results)

    if args.all or args.spsr:
        for config in scan_settings:
            print(
                f"---------------------Optimizing SPSR. config: {config}---------------------------")
            best_params, best_metric = ds.grid_search_poisson(
                grid_spsr, config, calculate_composite_metric)
            print(f"Best params: {best_params} | Best metric: {best_metric}")
            ds.makePoisson(scan_configuration=config,
                        depth=best_params["depth"], boundary=best_params["boundary"])
            results = ds.eval_poisson()
            # --- save in a predefine folder for easy access ---
            save_results(ds, "spsr", optimized_result_path,
                        optimized_models_folder, config, results)
            with open(os.path.join(ds.path, "results", f"best_params_spsr_{config}.txt"), "w") as file:
                file.write(str(best_params))

    if args.all or args.resr:
        for config in scan_settings:
            print(
                f"---------------------Optimizing RESR. config: {config}---------------------------")
            best_params, best_metric = ds.grid_search_labatut(
                grid_resr, config, calculate_composite_metric)
            print(f"Best params: {best_params} | Best metric: {best_metric}")
            ds.makeLabatut(scan_configuration=config,
                        alpha=best_params["alpha"], sigma=best_params["sigma"], lam=best_params["lam"], ignore_out=True)
            results = ds.eval_labatut()
            # --- save in a predefine folder for easy access ---
            save_results(ds, "resr", optimized_result_path,
                        optimized_models_folder, config, results)
            with open(os.path.join(ds.path, "results", f"best_params_resr_{config}.txt"), "w") as file:
                file.write(str(best_params))
        
    if args.all or args.bpivot:
        for config in scan_settings:
            print(
                f"---------------------Optimizing bpivot. config: {config}---------------------------")
            best_params, best_metric = ds.grid_search_ball_pivot(
                grid_ball_pivot, config, calculate_composite_metric)
            print(f"Best params: {best_params} | Best metric: {best_metric}")
            ds.make_ball_pivoting(scan_configuration=config,
                        mean_distance_weight=best_params["mean_distance_weight"], radius_w1=best_params["radius_w1"], radius_w2=best_params["radius_w2"], radius_w3=best_params["radius_w3"], radius_w4=best_params["radius_w4"])
            results = ds.eval_ball_pivot()
            # --- save in a predefine folder for easy access ---
            save_results(ds, "bpivot", optimized_result_path,
                        optimized_models_folder, config, results)
            with open(os.path.join(ds.path, "results", f"best_params_bpivot_{config}.txt"), "w") as file:
                file.write(str(best_params))
    
    if args.all or args.advancing:
        for config in scan_settings:
            print(
                f"---------------------Optimizing advancing front. config: {config}---------------------------")
            best_params, best_metric = ds.grid_search_advancing_front(
                grid_advancing_front, config, calculate_composite_metric)
            print(f"Best params: {best_params} | Best metric: {best_metric}")
            ds.make_advancing_front(scan_configuration=config, radius_ratio_bound=best_params["radius_ratio_bound"], beta=best_params["beta"], ignore_out=True)
            results = ds.eval_advancing_front()
            # --- save in a predefine folder for easy access ---
            save_results(ds, "advancing", optimized_result_path,
                        optimized_models_folder, config, results)
            with open(os.path.join(ds.path, "results", f"best_params_advancing_{config}.txt"), "w") as file:
                file.write(str(best_params))
    
    if args.all or args.scale_space:
        for config in scan_settings:
            print(
                f"---------------------Optimizing scale space. config: {config}---------------------------")
            best_params, best_metric = ds.grid_search_scale_space(
                grid_scale_space, config, calculate_composite_metric)
            print(f"Best params: {best_params} | Best metric: {best_metric}")
            ds.make_scale_space(scan_configuration=config, iterations=best_params["iterations"], maximum_facet_length=best_params["maximum_facet_length"], ignore_out=True)
            results = ds.eval_scale_space()
            # --- save in a predefine folder for easy access ---
            save_results(ds, "scale_space", optimized_result_path,
                        optimized_models_folder, config, results)
            with open(os.path.join(ds.path, "results", f"best_params_scale_space_{config}.txt"), "w") as file:
                file.write(str(best_params))


def save_results(ds: AltecDataset, method, unoptimized_result_path, unoptimized_models_folder, config, results):
    model_path = unoptimized_models_folder.format(f"{method}_{config}")
    shutil.copytree(os.path.join(
        ds.path, f"{method}"), model_path, dirs_exist_ok=True)
    for _, (res, _) in results.items():
        os.makedirs(os.path.dirname(unoptimized_result_path.format(
            f"{method}_{config}")), exist_ok=True)
        res.to_csv(unoptimized_result_path.format(
            f"{method}_{config}"), float_format='%.3g')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--search_only", type=bool, default=False,
                        help="If true will skip the unoptimized reconstruction and will do the grid search")
    parser.add_argument("--spsr", type=bool, default=False,
                        help="If true will perform actions for SPSR")
    parser.add_argument("--resr", type=bool, default=False,
                        help="If true will perform actions for RESR")
    parser.add_argument("--bpivot", type=bool, default=False,
                        help="If true will perform actions for ball pivoting")
    parser.add_argument("--advancing", type=bool, default=False,
                        help="If true will perform actions for advancing front")
    parser.add_argument("--scale_space", type=bool, default=False,
                        help="If true will perform actions for scale space")
    parser.add_argument("--all", type=bool, default=False,
                        help="If true will perform actions for all the remeshing algorithms")
    args = parser.parse_args()
    eval(args)
