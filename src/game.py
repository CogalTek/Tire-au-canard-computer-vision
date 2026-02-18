import cv2
import typing
import numpy as np

from components import PlayerHand, Cursor, Target, QuitButton, RectTarget
from global_data import GlobalData

if typing.TYPE_CHECKING:
    from model import Model


class Game:
    def __init__(self, md: "Model"):
        self.md = md
        self.qt = 0
        self.cursors: dict[int, Cursor] = {}
        self.targets = []  # List of targets to shoot at
        self.scores = {}
        self.game_over = False
        self.winCondition = 5
        self.show_panel = False
        self.targets.extend(
            [
                QuitButton(
                    x=20,
                    y=md.height - md.height // 20 - 10,
                    width=md.width // 5,
                    height=md.height // 20,
                ),
                Target(x=md.width // 2, y=md.height // 2, radius=30),
                RectTarget(
                    x=md.width // 4,
                    y=md.height // 4,
                    w=80,
                    h=80,
                    callback=self.toggle_help_panel,
                ),
            ]
        )
        GlobalData.subscribe("target_hit", self.on_target_hit)

    def on_target_hit(self, player_id, target):
        if not isinstance(target, Target):
            return
        # Initialiser le score du joueur s'il n'existe pas
        if player_id not in self.scores:
            self.scores[player_id] = 0

        # Incrémenter le score
        self.scores[player_id] += 1
        print(f"Player {player_id} hit a {target}! Score: {self.scores[player_id]}")
        if self.scores[player_id] >= self.winCondition:
            self.game_over = True

    def toggle_help_panel(self):
        self.show_panel = not self.show_panel

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

    def draw_scores(self):
        left_score = self.scores.get("Left", 0)
        right_score = self.scores.get("Right", 0)
        cv2.putText(
            self.md.frame,
            f"Right Score: {left_score}",
            (400, 464),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            self.md.frame,
            f"Left Score: {right_score}",
            (170, 464),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )

    def draw_info_panel(self, player_count: int, angles: PlayerHand.Angle | None):
        """Affiche un panneau d'informations stylisé"""
        title = "Help" if self.show_panel else "Press 'H' for help"
        content = (
            (
                "Aim by fingergun'ing at the cam\n"
                "Shoot by either:\n"
                "- Bending your thumb\n"
                "- Bringing your thumb lower\n"
                "  than the index finger\n"
                "Keybindings:\n"
                "'Tab' switch camera\n"
                "'Q' to quit\n"
                "'H' toggle help"
            )
            if self.show_panel
            else ""
        )
        panel_height = content.count("\n") * 28 + 50
        panel_width = (
            max(len(title) * 13, len(max(content.split("\n"), key=len)) * 10) + 20
        )
        panel_x = 10
        panel_y = 10
        panel_target: RectTarget = self.targets[
            2
        ]  # Assuming the RectTarget is the third target in the list

        if panel_target.w != panel_width or panel_target.h != panel_height:
            panel_target.w = panel_width
            panel_target.h = panel_height
            panel_target.x = panel_x
            panel_target.y = panel_y

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
            title,
            (panel_x + 14, panel_y + 30),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        for i, line in enumerate(content.split("\n")):
            cv2.putText(
                self.md.frame,
                line,
                (panel_x + 15, panel_y + 60 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )

    def handle_click(self, player_id, x, y, cursor: Cursor):
        if not cursor.just_clicked:
            return
        if self.game_over:
            self.game_over = False
            self.scores = {}
        for target in self.targets:
            if target._is_hit(x, y):
                GlobalData.emit("target_hit", player_id=player_id, target=target)
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

        if self.game_over:
            left_score = self.scores.get("Right", 0)
            right_score = self.scores.get("Left", 0)
            text = "Left Won" if left_score > right_score else "Right Won"
            cv2.putText(
                self.md.frame,
                text,
                (100, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                (30, 255, 30),
                6,
            )
            cv2.putText(
                self.md.frame,
                "Shoot to restart",
                (180, 300),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (30, 255, 30),
                2,
            )
        else:
            # Afficher le panneau d'info
            player_count = len(self.md.player)
            angles = (
                list(self.md.player.values())[0].angle if player_count > 0 else None
            )
            self.draw_info_panel(player_count, angles)
            self.draw_scores()

            for target in self.targets:
                target.draw(overlay if target._draw_on_overlay else self.md.frame)

            # Dessiner les curseurs pour chaque main
            for i, player in self.md.player.items():
                cursor = self.cursors.get(player.id)
                if not cursor:
                    cursor = Cursor(player.projected_pos, (0, 255, 0))
                    self.cursors[player.id] = cursor

                # On inverse les labels des mains car on est sur une caméra frontale
                if player.id == "Left":
                    cursor.label = f"Player Right"
                else:
                    cursor.label = f"Player Left"
                cursor.draw(self.md.frame)

        self.md.frame = cv2.add(overlay, self.md.frame)

    def update(self, key: int = None):
        if key == ord("h"):
            self.toggle_help_panel()
        for player_id, player in self.md.player.items():
            cursor = self.cursors.get(player_id)
            if not cursor:
                cursor = Cursor(player.projected_pos, (0, 255, 0))
                self.cursors[player_id] = cursor

            cursor.update(player.projected_pos, player.pos, player.is_shooting)

            self.handle_click(
                player_id,
                *cursor.pos,
                self.cursors[player_id],
            )

        # Mettre à jour les targets
        for target in self.targets:
            target.update(GlobalData.dt)
