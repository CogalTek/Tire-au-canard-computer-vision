from dataclasses import dataclass

import cv2
from cv2.typing import MatLike
import random

import numpy as np

from components.atarget import ATarget


@dataclass
class Target(ATarget):
    radius: int
    _velocity: tuple[float, float] = (0.0, 0.0)

    def __post_init__(self):
        # Initialiser une vélocité aléatoire pour le target
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(50, 150)  # pixels par seconde
        self._velocity = (speed * np.cos(angle), speed * np.sin(angle))
        self.sprite_right = cv2.imread("assets/duck_right.png", cv2.IMREAD_UNCHANGED)
        self.sprite_right = cv2.resize(
            self.sprite_right, (self.radius * 2, self.radius * 2)
        )
        self.sprite_up = cv2.imread("assets/duck_up.png", cv2.IMREAD_UNCHANGED)
        self.sprite_up = cv2.resize(self.sprite_up, (self.radius * 2, self.radius * 2))
        self.sprite_down = cv2.imread("assets/duck_down.png", cv2.IMREAD_UNCHANGED)
        self.sprite_down = cv2.resize(
            self.sprite_down, (self.radius * 2, self.radius * 2)
        )

    def draw(self, img: MatLike):
        """Dessine le target avec un style arrondi"""
        x1, y1 = self.x - self.radius, self.y - self.radius
        x2, y2 = self.x + self.radius, self.y + self.radius

        # Sprite du target
        sprite = self.sprite_up
        if abs(self._velocity[1]) > abs(self._velocity[0]):
            if self._velocity[1] > 0:
                sprite = self.sprite_down
        else:
            sprite = self.sprite_right
        # flip if moving left
        if self._velocity[0] < 0:
            sprite = cv2.flip(sprite, 1)
        for c in range(0, 3):
            img[y1:y2, x1:x2, c] = sprite[:, :, c] * (sprite[:, :, 3] / 255.0) + img[
                y1:y2, x1:x2, c
            ] * (1.0 - sprite[:, :, 3] / 255.0)

    def _to_radian(self, angle):
        return angle * np.pi / 180

    def update(self, delta: float):
        """Met à jour la position du target en fonction de sa vélocité"""
        self.x += int(self._velocity[0] * delta)
        self.y += int(self._velocity[1] * delta)

        # Rebondir sur les bords de l'écran
        if self.x - self.radius < 0 or self.x + self.radius > 640:
            self._velocity = (-self._velocity[0], self._velocity[1])
            self.x = max(self.radius, min(640 - self.radius, self.x))
        if self.y - self.radius < 0 or self.y + self.radius > 480:
            self._velocity = (self._velocity[0], -self._velocity[1])
            self.y = max(self.radius, min(480 - self.radius, self.y))

    def on_shot(self):
        """Réinitialise le target à une position aléatoire et une nouvelle vélocité"""
        self.x = random.randint(50, 590)
        self.y = random.randint(50, 430)
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(50, 150)  # pixels par seconde
        self._velocity = (speed * np.cos(angle), speed * np.sin(angle))

    def _is_hit(self, x: int, y: int) -> bool:
        """Détermine si les coordonnées (x, y) touchent le target"""
        return (x - self.x) ** 2 + (y - self.y) ** 2 <= self.radius**2
