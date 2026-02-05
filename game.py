import cv2

class Game:
    def __init__(self, md):
        self.md = md

    def update(self):
        for player in self.md.player:
            cv2.putText(self.md.frame, f"Pitch: {player['angle'][0]:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            if (player['is_shooting'] == False):
                cv2.circle(self.md.frame, (int(player['pos'][0]), int(player['pos'][1])), 10, (0, 255, 0), thickness=-1)
            else:
                cv2.circle(self.md.frame, (int(player['pos'][0]), int(player['pos'][1])), 10, (255, 0, 0), thickness=-1)