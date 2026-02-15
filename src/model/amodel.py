from dataclasses import dataclass
from typing import List, Literal, Union

import cv2


class AModel:
    """Abstract base class for models that process video frames."""

    @dataclass
    class Landmark:
        x: float
        y: float
        z: float

    @dataclass
    class HandLandmarks:
        landmark: List["AModel.Landmark"]

    @dataclass
    class Classification:
        index: int
        score: float
        label: Union[Literal["Left", "Right"]]

    @dataclass
    class Handedness:
        classification: List["AModel.Classification"]

    @dataclass
    class Results:
        """Class to hold the results of hand tracking

        1) a "multi_hand_landmarks" field that contains the hand landmarks on
           each detected hand.
        2) a "multi_hand_world_landmarks" field that contains the hand landmarks
           on each detected hand in real-world 3D coordinates that are in meters
           with the origin at the hand's approximate geometric center.
        3) a "multi_handedness" field that contains the handedness (left v.s.
           right hand) of the detected hand.
        """

        multi_hand_landmarks: List["AModel.HandLandmarks"]
        multi_hand_world_landmarks: List["AModel.HandLandmarks"]
        multi_handedness: List["AModel.Handedness"]

    def process(self, frame: cv2.typing.MatLike) -> Results:
        """Process a frame and return the processed frame."""
        raise NotImplementedError("Subclasses must implement this method.")
