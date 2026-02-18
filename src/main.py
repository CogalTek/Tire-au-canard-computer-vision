import cv2
from global_data import GlobalData
from model import Model
from game import Game
import numpy as np
import time

#

FPS = 30


def main():
    md = Model()
    gm = Game(md)
    window_name = "Hand Gesture Recognition"
    prev_time = time.time()
    GlobalData.dt = 0
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)

    while md.cap.isOpened() and GlobalData.running:
        current_time = time.time()
        GlobalData.dt = current_time - prev_time
        GlobalData.fps = 1 / GlobalData.dt if GlobalData.dt > 0 else float("inf")
        prev_time = current_time

        frame = md.get_current_frame()
        if frame is None:
            print("Ignoring empty camera frame.")
            continue

        md.process_active_players()
        md.process_frame(frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or gm.qt == 1:
            break
        # Change la capture video en appuyant sur tab
        if key == ord("\t"):
            md.switch_camera()

        gm.update(key)
        gm.draw()
        cv2.imshow(window_name, md.frame)

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
