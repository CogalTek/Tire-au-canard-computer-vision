import cv2
from model import Model
from game import Game
import numpy as np

#


def main():
    md = Model()
    gm = Game(md)
    window_name = "Hand Gesture Recognition"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)

    while md.cap.isOpened():
        frame = md.get_current_frame()
        if frame is None:
            print("Ignoring empty camera frame.")
            continue

        md.process_active_players()
        md.process_frame(frame)

        gm.update()
        gm.draw()

        cv2.imshow(window_name, md.frame)
        if cv2.waitKey(1) & 0xFF == ord("q") or gm.qt == 1:
            break

        # Window closed manually
        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            # Handle the case where the window property cannot be retrieved (e.g., on Wayland)
            break

    md.cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
