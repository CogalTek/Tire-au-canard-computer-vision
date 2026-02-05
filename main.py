import cv2
from _game import game
import numpy as np

# from ultralytics import YOLO


def main():
    window = cv2.namedWindow("Frame")
    # cap = cv2.VideoCapture(1)
    # model = YOLO("model.pt")

    while cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) >= 1:
        # ret, frame = cap.read()
        # frame = cv2.imread(
        #     "assets/empty.png"
        # )  # Placeholder for testing without a camera
        frame = np.array(
            [[(0, 0, 0) for _ in range(640)] for _ in range(480)], dtype=np.uint8
        )

        if frame is None:
            print("Failed to load image")
            break

        frame = game(frame)

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) < 1:
            break


if __name__ == "__main__":
    main()
