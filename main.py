import cv2
from model import Model
from game import Game
import numpy as np

#


def main():
    md = Model()
    gm = Game(md)
    window_name = "Hand Gesture Recognition"
    cv2.namedWindow(window_name)

    while md.cap.isOpened():
        success, frame = md.cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Utiliser les dimensions de la frame capturée
        height, width = frame.shape[:2]
        md.width, md.height = width, height

        md.update()
        md.predict(frame)
        gm.update()

        cv2.imshow(window_name, md.frame)
        if cv2.waitKey(1) & 0xFF == ord("q") or gm.qt == 1:
            break

    md.cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
