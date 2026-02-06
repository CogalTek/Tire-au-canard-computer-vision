import cv2
import numpy as np

from game_data import GameData


class Cursor:
    @property
    def pos(self):
        return self.smoothed_pos

    @property
    def just_clicked(self):
        return self.is_active and self._active_frames == 1

    def __init__(self, pos, color):
        self._pos = pos
        self._animation_length = 0.2
        self._animation_time = 0
        self.smoothed_pos = pos
        self.origin_pos = pos
        self.color = color
        self.is_active = False
        self.label = ""
        self._active_frames = 0

        self._reset_animation()

    def _reset_animation(self):
        self._animation_time = self._animation_length
        self._active_frames = 0

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
        self._active_frames = self._active_frames + 1 if is_active else 0

        # Appliquer un lissage de 5 frames pour éviter les mouvements brusques du curseur
        self.smoothed_pos = (
            (2 / 3) * np.array(self.smoothed_pos) + (1 / 3) * np.array(pos)
        ).astype(int)

    def draw(self, frame: cv2.Mat):
        """Dessine le curseur sur la frame avec un style différent selon son état"""
        pos = self.smoothed_pos

        cv2.line(frame, self.origin_pos, pos, (255, 255, 255), 1)

        if self.is_active:
            if self._animation_time > 0:
                progress = self._animation_time / self._animation_length * 2
                cv2.line(
                    frame,
                    (int(pos[0] - 12 * progress), int(pos[1] - 12 * progress)),
                    (int(pos[0] + 12 * progress), int(pos[1] + 12 * progress)),
                    (255, 255, 255),
                    6,
                )
                cv2.line(
                    frame,
                    (int(pos[0] - 12 * progress), int(pos[1] + 12 * progress)),
                    (int(pos[0] + 12 * progress), int(pos[1] - 12 * progress)),
                    (255, 255, 255),
                    6,
                )
                cv2.circle(frame, pos, 15, (255, 255, 255), 8)
                self._animation_time -= GameData.dt

            # Curseur actif (shooting) - Rouge avec effet de pulsation
            cv2.circle(frame, pos, 15, (0, 0, 255), 3)
            cv2.circle(frame, pos, 8, (255, 255, 255), -1)
            cv2.circle(frame, pos, 4, (0, 0, 255), -1)
        else:
            self._reset_animation()  # Réinitialiser l'animation pour la prochaine fois que le curseur devient actif
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
