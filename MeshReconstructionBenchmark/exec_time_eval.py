import os
import sys
from dsrb.set_paths import set_paths
import ast

# fmt: off
# yapf: disable
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from classes.DefaultDataset import DefaultDataset
from classes.scan_settings import scan_settings
# fmt: on
# yapf: enable


set_paths(DATA_DIR=os.path.join(os.path.dirname(__file__), "dataset"),
          CPP_DIR=os.path.join(os.path.dirname(__file__), "externals"))


def get_best_params_file_path(method, config, ds: DefaultDataset):
    file_name = f"best_params_{method}_{config}.txt"
    return os.path.join(ds.path, "results", file_name)


def read_params_and_run(file_path, config, remesh_f):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            try:
                readed_values = ast.literal_eval(content)
                if isinstance(readed_values, dict):
                    return remesh_f(**readed_values, scan_configuration=config)
                else:
                    print(f"{file_path} Not valid file format")
            except (SyntaxError, ValueError) as e:
                print(f"Error while reading file {file_path}: {e}")
    else:
        print(f"Cannot find file: {file_path}")

def eval():
    def save_times(times):
        file_path = os.path.join(ds.path, "results", f"Time_results.txt")
        with open(file_path, "w") as file:
            file.write(str(times))
        print(f"File saved in: {file_path}")

    set_paths(DATA_DIR=os.path.join(os.path.dirname(__file__), "dataset"),
              CPP_DIR=os.path.join(os.path.dirname(__file__), "externals"))

    ds = DefaultDataset()
    ds.get_models()

    times = {}
    
    for config in scan_settings:
        times[config] = {}
        times[config]["unoptim"] = {}
        times[config]["optim"] = {}
        
        method = "spsr"
        print(f"------------- eval {method} ------------")
        times[config]["unoptim"][method] = ds.makePoisson(
            scan_configuration=config)
        file_path = get_best_params_file_path(method, config, ds)
        times[config]["optim"][method] = read_params_and_run(file_path, config, ds.makePoisson)
        
        method = "resr"
        print(f"------------- eval {method} ------------")
        times[config]["unoptim"][method] = ds.makeLabatut(
            scan_configuration=config)
        file_path = get_best_params_file_path(method, config, ds)
        times[config]["optim"][method] = read_params_and_run(file_path, config, ds.makeLabatut)
        
        method = "bpivot"
        print(f"------------- eval {method} ------------")
        times[config]["unoptim"][method] = ds.make_ball_pivoting(
            scan_configuration=config)
        file_path = get_best_params_file_path(method, config, ds)
        times[config]["optim"][method] = read_params_and_run(file_path, config, ds.make_ball_pivoting)
        
        method = "advancing"
        print(f"------------- eval {method} ------------")
        times[config]["unoptim"][method] = ds.make_advancing_front(
            scan_configuration=config)
        file_path = get_best_params_file_path(method, config, ds)
        times[config]["optim"][method] = read_params_and_run(file_path, config, ds.make_advancing_front)
        
        method = "scale_space"
        print(f"------------- eval {method} ------------")
        times[config]["unoptim"][method] = ds.make_scale_space(
            scan_configuration=config)
        file_path = get_best_params_file_path(method, config, ds)
        times[config]["optim"][method] = read_params_and_run(file_path, config, ds.make_scale_space)

    save_times(times)


if __name__ == "__main__":

    eval()
