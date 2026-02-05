import mediapipe as mp
import numpy as np
import cv2

class Model:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)

    def predict(self, image):
        # Dummy prediction logic
        return "duck"