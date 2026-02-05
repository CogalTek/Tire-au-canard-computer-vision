import cv2
import numpy as np


class Cursor:
    @property
    def pos(self):
        return self.smoothed_pos

    def __init__(self, pos, color):
        self._pos = pos
        self.smoothed_pos = pos
        self.origin_pos = pos
        self.color = color
        self.is_active = False
        self.label = ""

    def update(self, pos: tuple[int, int], origin: tuple[int, int], is_active: bool):
        """Met à jour la position et l'état du curseur

        Args:
            pos (tuple[int, int]): Position actuelle du curseur (projetée à l'écran)
            origin (tuple[int, int]): Position d'origine du curseur (Sur la main)
            is_active (bool): Indique si le curseur est actif (en train de tirer)
        """
        self._pos = pos
        self.origin_pos = origin
        self.is_active = is_active

        # Appliquer un lissage de 5 frames pour éviter les mouvements brusques du curseur
        self.smoothed_pos = (
            0.8 * np.array(self.smoothed_pos) + 0.2 * np.array(pos)
        ).astype(int)

    def draw(self, frame: cv2.Mat):
        """Dessine le curseur sur la frame avec un style différent selon son état"""
        pos = self.smoothed_pos

        cv2.line(frame, self.origin_pos, pos, (255, 255, 255), 1)

        if self.is_active:
            # Curseur actif (shooting) - Rouge avec effet de pulsation
            cv2.circle(frame, pos, 15, (0, 0, 255), 3)
            cv2.circle(frame, pos, 8, (255, 255, 255), -1)
            cv2.circle(frame, pos, 4, (0, 0, 255), -1)
        else:
            # Curseur normal - Vert avec croix
            cv2.circle(frame, pos, 12, (0, 255, 0), 2)
            cv2.circle(frame, pos, 5, (0, 255, 0), -1)
            # Croix au centre
            cv2.line(
                frame,
                (pos[0] - 3, pos[1]),
                (pos[0] + 3, pos[1]),
                (255, 255, 255),
                1,
            )
            cv2.line(
                frame,
                (pos[0], pos[1] - 3),
                (pos[0], pos[1] + 3),
                (255, 255, 255),
                1,
            )

        # Afficher le label si défini
        if self.label:
            cv2.putText(
                frame,
                self.label,
                (pos[0] + 20, pos[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
