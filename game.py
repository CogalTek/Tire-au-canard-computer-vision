import cv2
import typing

from components.cursor import Cursor
from components.player_hand import PlayerHand

if typing.TYPE_CHECKING:
    from model import Model


class Game:
    def __init__(self, md: "Model"):
        self.md = md
        self.qt = 0
        self.cursors: dict[int, Cursor] = {}

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

    def view(self):
        """Affichage de l'interface"""
        # Bouton de sortie stylisé
        btn_x1, btn_y1 = 10, self.md.height - 60
        btn_x2, btn_y2 = 220, self.md.height - 20

        # Fond du bouton avec effet de transparence
        self.md.frame = cv2.flip(self.md.frame, 1)  # Flip horizontal pour effet miroir
        overlay = self.md.frame.copy()
        cv2.rectangle(overlay, (btn_x1, btn_y1), (btn_x2, btn_y2), (50, 180, 255), -1)
        cv2.addWeighted(overlay, 0.7, self.md.frame, 0.3, 0, self.md.frame)

        # Bordure du bouton
        cv2.rectangle(
            self.md.frame, (btn_x1, btn_y1), (btn_x2, btn_y2), (0, 255, 255), 2
        )

        # Texte du bouton
        cv2.putText(
            self.md.frame,
            "QUIT (Q)",
            (btn_x1 + 45, btn_y1 + 28),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

    def handle_click(self, x, y, clicked=False):
        btn_y1 = self.md.height - 60
        btn_y2 = self.md.height - 20
        if (10 <= x <= 220 and btn_y1 <= y <= btn_y2) and self.qt == 0 and clicked:
            print("Quitting game...")
            self.qt = 1

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

    def update(self):
        self.view()

        # Afficher le panneau d'info
        player_count = len(self.md.player)
        angles = self.md.player[0].angle if player_count > 0 else None
        self.draw_info_panel(player_count, angles)

        # Dessiner les curseurs pour chaque main
        for i, player in self.md.player.items():
            cursor = self.cursors.get(player.id)
            if not cursor:
                cursor = Cursor(player.projected_pos, (0, 255, 0))
                self.cursors[player.id] = cursor

            cursor.update(player.projected_pos, player.pos, player.is_shooting)

            self.handle_click(
                *cursor.pos,
                player.is_shooting,
            )
            cursor.draw(self.md.frame)
