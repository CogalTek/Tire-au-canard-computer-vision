from dataclasses import dataclass

import cv2

from components.atarget import ATarget


@dataclass
class Button(ATarget):
    width: int
    height: int
    text: str = "Button"

    def __post_init__(self):
        self._draw_on_overlay = True

    def draw(self, img: cv2.Mat):
        """Dessine le bouton sur l'image"""
        self._draw_background(img, color=(0, 255, 0))
        self._draw_border(img, color=(0, 255, 255))
        self._draw_text(img, color=(255, 255, 255))

    def _draw_background(self, img: cv2.Mat, color: tuple[int, int, int] = (0, 255, 0)):
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.width, self.y + self.height
        cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)

    def _draw_border(self, img: cv2.Mat, color: tuple[int, int, int] = (0, 255, 255)):
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.width, self.y + self.height
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

    def _draw_text(self, img: cv2.Mat, color: tuple[int, int, int] = (255, 255, 255)):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(self.text, font, 1, 2)[0]
        scale = min(self.width / (text_size[0] + 20), self.height / (text_size[1] + 20))
        text_size = (int(text_size[0] * scale), int(text_size[1] * scale))

        text_x = self.x
        text_y = self.y + (self.height + text_size[1]) // 2 - 5

        center_x = self.width // 2
        text_x = self.x + center_x - text_size[0] // 2
        center_y = self.height // 2
        text_y = self.y + center_y + text_size[1] // 2

        cv2.putText(img, self.text, (text_x, text_y), font, scale, color, 2)

    def update(self, delta: float):
        """Le bouton n'a pas de logique de mise à jour pour le moment"""

    def _is_hit(self, x, y):
        """Détermine si les coordonnées (x, y) touchent le bouton"""
        give_x, give_y = 5, 5  # Marge de tolérance pour les clics

        return (
            self.x - give_x <= x <= self.x + self.width + give_x
            and self.y - give_y <= y <= self.y + self.height + give_y
        )
