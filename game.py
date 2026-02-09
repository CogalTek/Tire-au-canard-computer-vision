import cv2
import typing
import numpy as np

from components import PlayerHand, Cursor, Target, QuitButton
from global_data import GlobalData

if typing.TYPE_CHECKING:
    from model import Model


class Game:
    def __init__(self, md: "Model"):
        self.md = md
        self.qt = 0
        self.cursors: dict[int, Cursor] = {}
        self.targets = []  # List of targets to shoot at
        self.targets.extend(
            [
                QuitButton(
                    x=20,
                    y=md.height - md.height // 20 - 10,
                    width=md.width // 5,
                    height=md.height // 20,
                ),
                Target(x=md.width // 2, y=md.height // 2, radius=30),
            ]
        )

    def draw_rounded_rect(self, img, pt1, pt2, color, thickness, radius):
        """Dessine un rectangle avec des coins arrondis"""
        x1, y1 = pt1
        x2, y2 = pt2

        # Créer un overlay pour la transparence
        overlay = img.copy()

        # Rectangle principal
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)

        # Coins arrondis
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1)

        # Appliquer la transparence
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)

    def draw_info_panel(self, player_count: int, angles: PlayerHand.Angle | None):
        """Affiche un panneau d'informations stylisé"""
        panel_height = 120
        panel_width = 280
        panel_x = 10
        panel_y = 10

        # Fond du panneau avec transparence
        overlay = self.md.frame.copy()
        cv2.rectangle(
            overlay,
            (panel_x, panel_y),
            (panel_x + panel_width, panel_y + panel_height),
            (40, 40, 40),
            -1,
        )
        cv2.addWeighted(overlay, 0.8, self.md.frame, 0.2, 0, self.md.frame)

        # Bordure du panneau
        cv2.rectangle(
            self.md.frame,
            (panel_x, panel_y),
            (panel_x + panel_width, panel_y + panel_height),
            (0, 200, 255),
            2,
        )

        # Titre
        cv2.putText(
            self.md.frame,
            "HAND TRACKING",
            (panel_x + 15, panel_y + 30),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        # Nombre de mains détectées
        cv2.putText(
            self.md.frame,
            f"Hands: {player_count}",
            (panel_x + 15, panel_y + 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        # Afficher les angles si disponibles
        if angles:
            cv2.putText(
                self.md.frame,
                f"Pitch: {angles.pitch:.1f}°",
                (panel_x + 15, panel_y + 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (100, 200, 255),
                1,
            )
            cv2.putText(
                self.md.frame,
                f"Roll: {angles.roll:.1f}°  Yaw: {angles.yaw:.1f}°",
                (panel_x + 15, panel_y + 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (100, 200, 255),
                1,
            )

    def handle_click(self, x, y, cursor: Cursor):
        btn_y1 = self.md.height - 60
        btn_y2 = self.md.height - 20
        # if (
        #     (10 <= x <= 220 and btn_y1 <= y <= btn_y2)
        #     and self.qt == 0
        #     and cursor.just_clicked
        # ):
        #     print("Quitting game...")
        #     self.qt = 1

        if not cursor.just_clicked:
            return
        for target in self.targets:
            if target._is_hit(x, y):
                print("Target hit!")
                target.on_shot()

    def draw_cursor(
        self, origin: tuple[int, int], pos: tuple[int, int], is_active: bool
    ):
        """Dessine un curseur stylisé"""

        # Draw line between origin and pos
        cv2.line(self.md.frame, origin, pos, (255, 255, 255), 1)

        if is_active:
            # Curseur actif (shooting) - Rouge avec effet de pulsation
            cv2.circle(self.md.frame, pos, 15, (0, 0, 255), 3)
            cv2.circle(self.md.frame, pos, 8, (255, 255, 255), -1)
            cv2.circle(self.md.frame, pos, 4, (0, 0, 255), -1)
        else:
            # Curseur normal - Vert avec croix
            cv2.circle(self.md.frame, pos, 12, (0, 255, 0), 2)
            cv2.circle(self.md.frame, pos, 5, (0, 255, 0), -1)
            # Croix au centre
            cv2.line(
                self.md.frame,
                (pos[0] - 3, pos[1]),
                (pos[0] + 3, pos[1]),
                (255, 255, 255),
                1,
            )
            cv2.line(
                self.md.frame,
                (pos[0], pos[1] - 3),
                (pos[0], pos[1] + 3),
                (255, 255, 255),
                1,
            )

    def draw(self):
        overlay = np.zeros_like(self.md.frame)
        overlay = cv2.cvtColor(
            overlay, cv2.COLOR_BGR2RGB
        )  # Convertir en BGRA pour la transparence
        self.md.frame = cv2.flip(self.md.frame, 1)  # Flip horizontal pour effet miroir

        # Afficher le panneau d'info
        player_count = len(self.md.player)
        angles = list(self.md.player.values())[0].angle if player_count > 0 else None
        self.draw_info_panel(player_count, angles)

        for target in self.targets:
            target.draw(overlay if target._draw_on_overlay else self.md.frame)

        # Dessiner les curseurs pour chaque main
        for i, player in self.md.player.items():
            cursor = self.cursors.get(player.id)
            if not cursor:
                cursor = Cursor(player.projected_pos, (0, 255, 0))
                self.cursors[player.id] = cursor

            cursor.label = f"Player {player.id}"
            cursor.draw(self.md.frame)

        self.md.frame = cv2.add(overlay, self.md.frame)

    def update(self):
        # Dessiner les curseurs pour chaque main
        for i, player in self.md.player.items():
            cursor = self.cursors.get(player.id)
            if not cursor:
                cursor = Cursor(player.projected_pos, (0, 255, 0))
                self.cursors[player.id] = cursor

            cursor.update(player.projected_pos, player.pos, player.is_shooting)

            self.handle_click(
                *cursor.pos,
                self.cursors[player.id],
            )

        # Mettre à jour les targets
        for target in self.targets:
            target.update(GlobalData.dt)
