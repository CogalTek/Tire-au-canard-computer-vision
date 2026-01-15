import cv2
from game import game
from ultralytics import YOLO

def main():
    cap = cv2.VideoCapture(1)
    model = YOLO("model.pt")

if __name__ == "__main__":
    main()