import cv2
from model import Model

def main():
	md = Model()
	while md.cap.isOpened():
		success, image = md.cap.read()
		if not success:
			print("Ignoring empty camera frame.")
			continue

		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		results = md.hands.process(image)

		if results.multi_hand_landmarks:
			for hand_landmarks in results.multi_hand_landmarks:
				md.mp_draw.draw_landmarks(image, hand_landmarks, md.mp_hands.HAND_CONNECTIONS)

		prediction = md.predict(image)
		cv2.putText(image, prediction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

		cv2.imshow('Hand Gesture Recognition', image)
		if cv2.waitKey(5) & 0xFF == 27:
			break

if __name__ == "__main__":
    main()