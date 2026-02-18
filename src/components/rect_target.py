from dataclasses import dataclass

import cv2
from cv2.typing import MatLike
import random

import numpy as np

from components.atarget import ATarget


@dataclass
class RectTarget(ATarget):
    x: int
    y: int
    w: int
    h: int
    callback: callable = None

    def draw(self, img: MatLike):
        """Invisible"""
        pass

    def update(self, delta: float):
        """Static target, no update needed"""
        pass

    def on_shot(self):
        """Appelle le callback associé si le target est touché"""
        if self.callback:
            self.callback()

    def _is_hit(self, x: int, y: int) -> bool:
        """Détermine si les coordonnées (x, y) touchent le target"""
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h
