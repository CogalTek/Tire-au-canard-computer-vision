import cv2
from components.button import Button
from global_data import GlobalData


class QuitButton(Button):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height, text="Quit")
        self._draw_on_overlay = (
            True  # Dessiner le bouton sur l'overlay pour qu'il soit au-dessus de tout
        )

    def draw(self, img):
        """Dessine le bouton Quit avec un style arrondi"""
        self._draw_background(img, color=(0, 0, 255, 127))
        self._draw_border(img, color=(255, 255, 0))
        self._draw_text(img, color=(255, 255, 255))

    def on_shot(self):
        GlobalData.running = False
