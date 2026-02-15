from typing import List

from .default import DefaultModel
from .amodel import AModel

# List of available models. Add your model class to this list when you create it.
available_models: List[AModel] = [DefaultModel]
