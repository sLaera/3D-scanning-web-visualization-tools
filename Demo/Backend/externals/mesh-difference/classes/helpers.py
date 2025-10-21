import os

import numpy as np


def get_file_name(path):
    file_name = os.path.basename(path)
    file = os.path.splitext(file_name)
    return file[0]


def save_arrays(filename, **arrays):
    """Saves arrays in file .npz"""
    np.savez(filename, **arrays)

def save_to_file(filename, value):
    """Saves values in file .npz"""
    np.savez(filename, value)

def load_arrays(filename):
    """Load .npz and return a dict"""
    loaded_data = np.load(filename)
    return {key: loaded_data[key] for key in loaded_data.files}

def load_from_file(filename):
    """Load .npz and return the values"""
    return np.load(filename)

def normalize(arr):
    # absolute median
    mad = np.median(np.abs(arr - np.median(arr)))
    max_val = np.max(np.abs(arr))

    normalized = ((arr - mad) / (max_val - mad)) * 2 - 1
    return normalized