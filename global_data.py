from dataclasses import dataclass


@dataclass
class GlobalData:
    fps: float = 0.0
    dt: float = 0.0
    running: bool = True
