import argparse
import os
import pymeshlab
import subprocess
import sys


def change_extension_to_ply(file_path):
    base, _ = os.path.splitext(file_path)
    return base + ".ply"


def main(args):
    if not os.path.exists(args.input):
        raise Exception(f"Path:{os.path.abspath(args.input)} doesn't exist")
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    if not args.poisson_recon_exe:
        args.poisson_recon_exe = './PoissonRecon/Bin/Linux'
    if not os.path.exists(args.poisson_recon_exe):
        raise Exception(f"Path:{os.path.abspath(args.poisson_recon_exe)} doesn't exist")

    ms = pymeshlab.MeshSet()
    input_ply_path = change_extension_to_ply(args.input)
    output_ply_path = change_extension_to_ply(args.out)

    print("Reading input mesh")
    sys.stdout.flush()
    ms.load_new_mesh(args.input)
    ms.save_current_mesh(input_ply_path, save_vertex_normal=True)
    # ---Execute reconstruction----
    print("Reconstruction")
    sys.stdout.flush()
    command = [args.poisson_recon_exe,
               "--in", input_ply_path,
               "--out", output_ply_path,
               "--depth", str(args.depth),
               "--bType", str(args.bType)]

    p = subprocess.Popen(command)
    p.wait()
    # -----------------------------
    # clean temp files
    os.remove(input_ply_path)

    print("Save results")
    sys.stdout.flush()
    ms.clear()
    # ---convert ply in obj---
    ms.load_new_mesh(output_ply_path)
    ms.save_current_mesh(args.out, save_vertex_normal=True)
    # clean temp files
    os.remove(output_ply_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poisson_recon_exe", type=str,
                        help="Path of the poisson reconstruct algorithm exe file",
                        required=False
                        )
    parser.add_argument("--input", type=str,
                        help="Path of the source mesh")
    parser.add_argument("--out", type=str,
                        help="Path of the output mesh")
    parser.add_argument("--depth", type=int,
                        help="Depth of the solver")
    parser.add_argument("--bType", type=int,
                        help="Type of boundary")

    args = parser.parse_args()
    main(args)
