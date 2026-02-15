from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from cv2.typing import MatLike


@dataclass
class ATarget(ABC):
    x: int
    y: int
    _draw_on_overlay: bool = field(
        default=False, init=False
    )  # Par défaut, les targets ne sont pas dessinés sur l'overlay

    @abstractmethod
    def _is_hit(self, x: int, y: int) -> bool:
        """Détermine si les coordonnées (x, y) touchent le target"""
        ...

    @abstractmethod
    def draw(self, img: MatLike):
        """Dessine le target sur l'image"""
        ...

    @abstractmethod
    def update(self, delta: float):
        """Met à jour la position du target en fonction du temps écoulé depuis la dernière mise à jour"""
        ...

    @abstractmethod
    def on_shot(self):
        """Gère la logique à appliquer lorsque le target est touché (ex: réinitialiser sa position)"""
        ...
