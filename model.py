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
            # on verifie si index:12 est proche de index:16
            index_a = hand_lms.landmark[12]
            index_b = hand_lms.landmark[4]
            dist = np.sqrt((index_a.x - index_b.x) ** 2 + (index_a.y - index_b.y) ** 2)

            # debug tracé de la distance
            cv2.line(
                self.frame,
                (int(index_a.x * width), int(index_a.y * height)),
                (int(index_b.x * width), int(index_b.y * height)),
                (255, 0, 0),
                2,
            )
            cv2.putText(
                self.frame,
                f"Dist: {dist:.4f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),
                2,
            )

            if dist < 0.05:  # Seuil à ajuster selon les besoins
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
