"""
Component Testing Script

This script performs tests for specified components.

Usage:
    Run this script with the component name as a parameter to execute its corresponding test file
    located in the './test' directory. Tests should be run through this script, not directly from
    the './test' folder, to ensure proper setup and configuration.

Arguments:
    component_name (str): The name of the component to test.

Example:
    python test.py component_name

Notes:
    - Test results will be displayed in the console.
"""
import argparse
from enum import Enum

class Component(Enum):
    bechmark = "benchmark"
    spsr = "spsr"
    resr = "resr"

def run_test(component_name):
    #It is important that the scripts starts from the root folder in order to get the correct CPP_DIR DATA_DIR files
    #Each component is enumerated and mathced here. So the component is imported and the test function is executed
    match component_name:
        case Component.bechmark.value:
            from test.test_dsr_benchmark import test
        case Component.spsr.value:
            from test.test_spsr import test
        case Component.resr.value:
            from test.test_resr import test
        case _:
            print("Component to test not found")
            return
    print("======================================================")
    print("------------------"+component_name+"------------------")
    print("======================================================")
    test()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("component_name", type=str, help="Name of the component to test")
    args = parser.parse_args()

    if (args.component_name != "all"):
        run_test(args.component_name)
    else:
        for component in list(Component):
            run_test(component.value)