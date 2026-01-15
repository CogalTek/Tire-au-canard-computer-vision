import cv2
from game import game
from ultralytics import YOLO

def main():
    # 0 est généralement la caméra par défaut, 1 pour une caméra externe
    cap = cv2.VideoCapture(1)
    model = YOLO("model.pt")
    
    win_name = 'Video Feed'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL) # Rend la fenêtre redimensionnable

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 1. Inférence YOLO
        results = model(frame)
        annotated_frame = results[0].plot()
        
        # 2. Récupérer la taille actuelle de la fenêtre
        # Si l'utilisateur l'étire, w et h changeront
        x, y, w, h = cv2.getWindowImageRect(win_name)
        
        # Optionnel : Afficher la taille sur la console ou l'image
        # print(f"Fenêtre : {w}x{h}")

        # 3. Logique de votre jeu
        # Note : assurez-vous que game() peut gérer les dimensions dynamiques si besoin
        game(annotated_frame)

        # 4. Affichage unique
        cv2.imshow(win_name, annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()