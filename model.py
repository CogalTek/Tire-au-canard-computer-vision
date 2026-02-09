from typing import Literal
import mediapipe as mp
import numpy as np
import cv2
from mediapipe.python.solutions import hands

from components.player_hand import PlayerHand


class Model:
    def __init__(self):
        self.hands = hands.Hands(
            max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.player: dict[int, PlayerHand] = {}
        self.height = 480
        self.width = 640

    def get_current_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None

        # Utiliser les dimensions de la frame capturée
        height, width = frame.shape[:2]
        self.width, self.height = width, height
        return frame

    def process_active_players(self):
        # Remove players that haven't been detected for a while
        for player in list(self.player.values()):
            player.update()
            if not player.is_active:
                self.player.pop(player.id, None)

    def process_frame(self, frame: cv2.typing.MatLike):
        self.frame = frame
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        # On vérifie la présence des deux types de landmarks
        if results.multi_hand_landmarks and results.multi_hand_world_landmarks:
            # zip permet de parcourir les deux listes en même temps
            self.update_player_hand_metrics(
                results.multi_hand_landmarks,
                results.multi_hand_world_landmarks,
                results.multi_handedness,
                self.width,
                self.height,
            )

    def update_player_hand_metrics(
        self,
        multi_landmarks: list,
        multi_world_landmarks: list,
        multi_handedness,
        width: int,
        height: int,
    ):
        for i, (hand_lms, hand_world_lms, handedness) in enumerate(
            zip(multi_landmarks, multi_world_landmarks, multi_handedness)
        ):
            # player = self._find_or_create_player(hand_world_lms)
            if i >= 2:
                print(
                    f"Warning: Detected more hands than player slots ({i}/{2}). Ignoring extra hands."
                )
                continue
            player = self.player.get(
                handedness.classification[0].label, PlayerHand(id=i)
            )
            player.id = handedness.classification[0].label

            # --- 1. POSITION ÉCRAN (Utilise hand_landmarks) ---
            # On prend l'index (point 8) ou le poignet (point 0)
            index_tip = hand_lms.landmark[8]
            screen_x = int((1 - index_tip.x) * width)
            screen_y = int(index_tip.y * height)

            # --- 2. ANGLES & GIZMO (Utilise hand_world_landmarks) ---
            wrist_w = hand_world_lms.landmark[0]
            index_mcp_w = hand_world_lms.landmark[5]
            pinky_mcp_w = hand_world_lms.landmark[17]

            wrist_pos = np.array([wrist_w.x, wrist_w.y, wrist_w.z])
            index_mcp_pos = np.array([index_mcp_w.x, index_mcp_w.y, index_mcp_w.z])
            pinky_mcp_pos = np.array([pinky_mcp_w.x, pinky_mcp_w.y, pinky_mcp_w.z])

            # Calcul des vecteurs
            milieu_mcp = (index_mcp_pos + pinky_mcp_pos) / 2
            axe_y = milieu_mcp - wrist_pos
            axe_y /= np.linalg.norm(axe_y)

            axe_x = pinky_mcp_pos - index_mcp_pos
            axe_x /= np.linalg.norm(axe_x)

            axe_z = np.cross(axe_x, axe_y)
            axe_z /= np.linalg.norm(axe_z)

            # Angles d'Euler
            pitch = np.degrees(np.atan2(-axe_y[2], axe_y[1]))
            roll = np.degrees(np.atan2(axe_x[1], axe_x[0]))
            yaw = np.degrees(np.atan2(axe_z[0], axe_z[2]))

            # Gestion du shoot
            # on verifie si le bout du pouce (landmark 4) est proche de la base de l'index (landmark 5)
            thumb_2d = hand_lms.landmark[4]
            index_base_2d = hand_lms.landmark[5]
            dist_2d = np.sqrt(
                (thumb_2d.x - index_base_2d.x) ** 2
                + (thumb_2d.y - index_base_2d.y) ** 2
            )

            # 3D distance using world landmarks (real-world coordinates)
            thumb_w = hand_world_lms.landmark[4]
            index_base_w = hand_world_lms.landmark[5]
            thumb_pos = np.array([thumb_w.x, thumb_w.y, thumb_w.z])
            index_pos = np.array([index_base_w.x, index_base_w.y, index_base_w.z])
            dist_3d = float(np.linalg.norm(thumb_pos - index_pos))

            index_tip = hand_lms.landmark[8]

            # Use a 3D threshold (meters) for shooting detection; adjust as needed
            is_shooting = (
                # dist_3d < 0.035
                1
                and self._is_thumb_bent(hand_lms)
                # and abs(player.average_dist_3D - dist_3d)
                # > 0.01  # ensure it's a new "shoot" action, not just noise
            )

            projected_pos = self._calculate_projected_pos(
                hand_lms, hand_world_lms, width, height
            )

            player.angle = PlayerHand.Angle(pitch, roll, yaw)
            player.pos = (screen_x, screen_y)
            player.projected_pos = projected_pos
            player.is_shooting = is_shooting
            player.average_dist_3D = (
                dist_3d * 0.5 + player.average_dist_3D * 0.5
            )  # simple moving average to smooth distance
            self.player[player.id] = player

    def _calculate_projected_pos(
        self, hand_lms, hand_world_lms, width, height, forward_m=0.5
    ):
        """Compute projected image pixel position by moving forward `forward_m` meters
        along the axis defined by world landmarks 5->8, then map that world offset
        to image pixels using the observed image displacement between 5 and 8.

        Falls back to a 10-pixel forward projection if world->image mapping is unstable.
        """
        # image-space points
        idx_mcp_2d = hand_lms.landmark[5]
        idx_tip_2d = hand_lms.landmark[8]
        px_mcp = np.array(
            [int(idx_mcp_2d.x * width), int(idx_mcp_2d.y * height)], dtype=float
        )
        px_tip = np.array(
            [int(idx_tip_2d.x * width), int(idx_tip_2d.y * height)], dtype=float
        )

        # Derive pixels-per-meter from image MCP->TIP displacement assuming
        # the finger length is always 0.4 meters (no world landmarks used).
        v_img = px_tip - px_mcp
        img_norm = np.linalg.norm(v_img)
        finger_length_m = 0.4

        if img_norm > 1e-6:
            pixels_per_meter = img_norm / finger_length_m
            dir_unit = v_img / img_norm
            delta_pixels = dir_unit * (pixels_per_meter * forward_m)
            proj_point = px_tip + delta_pixels
        else:
            print("Fallback projection used due to unstable world->image mapping")
            # fallback: simple image-space 10-pixel forward
            dir_px = px_tip - px_mcp
            norm_dir = np.linalg.norm(dir_px)
            if norm_dir == 0:
                return (int(px_tip[0]), int(px_tip[1]))
            dir_unit = dir_px / norm_dir
            proj_point = px_tip + dir_unit * 10  # 10 pixels forward

        # Flip x coordinate for mirror effect
        proj_point[0] = width - proj_point[0]
        return (int(proj_point[0]), int(proj_point[1]))

    def _is_thumb_bent(self, hand_lms):
        """Estimate thumb bend using image-space landmarks (`hand_lms`).

        Reconstruct a simple 3D chain for the thumb using the landmark directions
        and assuming each segment length = 0.2 meters. Then compute the angle at
        the middle joint and return True if bend > 25°.
        """
        # Use landmarks 4,5,8 which are the thumb tip, index base, and index tip respectively
        thumb_base = hand_lms.landmark[2]
        thumb_mid = hand_lms.landmark[3]
        thumb_tip = hand_lms.landmark[4]
        index_pip = hand_lms.landmark[6]

        # If thumb tip is below index base in image space, consider it bent
        if thumb_tip.y > index_pip.y:
            return True

        # Build direction vectors from normalized landmarks (x,y,z provided by hand_lms)
        v23 = np.array(
            [
                thumb_mid.x - thumb_base.x,
                thumb_mid.y - thumb_base.y,
                thumb_mid.z - thumb_base.z,
            ],
            dtype=float,
        )
        v34 = np.array(
            [
                thumb_tip.x - thumb_mid.x,
                thumb_tip.y - thumb_mid.y,
                thumb_tip.z - thumb_mid.z,
            ],
            dtype=float,
        )

        na = np.linalg.norm(v23)
        nb = np.linalg.norm(v34)
        if na == 0 or nb == 0:
            return False

        # Unit directions in image-normalized space
        d23 = v23 / na
        d34 = v34 / nb

        # Reconstruct 3D positions assuming each thumb segment length = 0.2 m
        L = 0.2
        p2 = np.array([0.0, 0.0, 0.0], dtype=float)
        p3 = p2 + d23 * L
        p4 = p3 + d34 * L

        # Angle at p3 between p2->p3 and p4->p3
        va = p2 - p3
        vb = p4 - p3
        na2 = np.linalg.norm(va)
        nb2 = np.linalg.norm(vb)
        if na2 == 0 or nb2 == 0:
            return False
        cosang = np.clip(np.dot(va, vb) / (na2 * nb2), -1.0, 1.0)
        angle_deg = float(np.degrees(np.arccos(cosang)))
        bend_deg = abs(180.0 - angle_deg)

        # # Debug visualization (optional): draw the thumb chain and angle on the frame
        # ## First segment (constant, length = 0.2, along y axis, start in center of screen)
        # cv2.line(
        #     self.frame,
        #     (self.width // 2, self.height // 2),
        #     (self.width // 2, self.height // 2 + int(L * self.height)),
        #     (255, 255, 0),
        #     2,
        # )
        # # rotated second segment
        # end_x = int(self.width // 2 + L * self.height * np.sin(np.radians(bend_deg)))
        # end_y = int(self.height // 2 + L * self.height * np.cos(np.radians(bend_deg)))
        # cv2.line(
        #     self.frame,
        #     (self.width // 2, self.height // 2),
        #     (end_x, end_y),
        #     (255, 0, 0),
        #     2,
        # )

        return bend_deg > 40
