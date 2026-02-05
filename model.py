import mediapipe as mp
import numpy as np
import cv2


class Model:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.player = []
        self.height = 480
        self.width = 640
        self.index_info = {}

    def predict(self, frame):
        self.frame = frame
        self.player = []
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        # On vérifie la présence des deux types de landmarks
        if results.multi_hand_landmarks and results.multi_hand_world_landmarks:
            # zip permet de parcourir les deux listes en même temps
            self.createGuizmo(
                results.multi_hand_landmarks,
                results.multi_hand_world_landmarks,
                self.width,
                self.height,
            )

    def createGuizmo(self, multi_landmarks, multi_world_landmarks, width, height):
        for hand_lms, hand_world_lms in zip(multi_landmarks, multi_world_landmarks):
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
            self.index_info = {
                "x": int(index_tip.x * width),
                "y": int(index_tip.y * height),
                "z": index_tip.z,
                "dist_2d": float(dist_2d),
                "dist_3d": dist_3d,
            }

            # debug tracé de la distance (2D projection)
            cv2.line(
                self.frame,
                (int(thumb_2d.x * width), int(thumb_2d.y * height)),
                (int(index_base_2d.x * width), int(index_base_2d.y * height)),
                (255, 0, 0),
                2,
            )
            cv2.putText(
                self.frame,
                f"Dist2D: {dist_2d:.4f} 3D: {dist_3d:.4f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),
                2,
            )

            # Use a 3D threshold (meters) for shooting detection; adjust as needed
            if dist_3d < 0.035 and self._is_thumb_bent(hand_world_lms):
                is_shooting = True
            else:
                is_shooting = False

            self.player.append(
                {
                    "angle": (pitch, roll, yaw),
                    "pos": (screen_x, screen_y),
                    "is_shooting": is_shooting,
                }
            )

    def _is_thumb_bent(self, hand_world_lms):
        th2_w = hand_world_lms.landmark[2]
        th3_w = hand_world_lms.landmark[3]
        th4_w = hand_world_lms.landmark[4]
        p2 = np.array([th2_w.x, th2_w.y, th2_w.z])
        p3 = np.array([th3_w.x, th3_w.y, th3_w.z])
        p4 = np.array([th4_w.x, th4_w.y, th4_w.z])

        v_a = p2 - p3
        v_b = p4 - p3
        na = np.linalg.norm(v_a)
        nb = np.linalg.norm(v_b)
        if na == 0 or nb == 0:
            return False
        cosang = np.clip(np.dot(v_a, v_b) / (na * nb), -1.0, 1.0)
        angle_deg = float(np.degrees(np.arccos(cosang)))
        bend_deg = abs(180.0 - angle_deg)
        return bend_deg > 25.0
