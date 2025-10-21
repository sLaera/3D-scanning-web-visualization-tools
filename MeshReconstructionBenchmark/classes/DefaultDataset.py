import sys
import os
from dsrb.eval import MeshEvaluator

# fmt: off
# yapf: disable
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from BaseDataset import BaseDataset
# fmt: on
# yapf: enable


class AltecDataset(BaseDataset):
    def __init__(self, path=None, mesh_evaluator:MeshEvaluator = MeshEvaluator()):
        """Constructor of the Dataset Class

        Args:
            path (str, optional): Path of the dataset. Defaults to None.
            mesh_evaluator (MeshEvaluator, optional): Mesh evaluator object. Used for custom evaluation settings
        """
        super().__init__("Altec", path, mesh_evaluator)
        
