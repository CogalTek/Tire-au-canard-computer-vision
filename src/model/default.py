from .amodel import AModel
from mediapipe.python.solutions import hands


class DefaultModel(AModel):
    def __init__(self):
        super().__init__()
        self.hands: AModel = hands.Hands(max_num_hands=2, min_detection_confidence=0.8)

    def process(self, frame):
        return self.hands.process(frame)
