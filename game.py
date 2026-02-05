import cv2
import random
import time


class Enemy:
    def __init__(self, position, color=(0, 0, 255)):
        self.position = position
        self.color = color
        self.score = 0

    @staticmethod
    def initial_radius():
        return 100

    def draw(self, frame: cv2.Mat):
        x, y = self.position
        radius = self.get_radius()
        if self.has_expired():
            return frame
        frame = cv2.circle(frame, (x, y), radius, self.color, -1)
        return frame

    def update(self, dt):
        self.score += dt * 25

    def is_colliding(self, position, radius):
        ex, ey = self.position
        distance = ((position[0] - ex) ** 2 + (position[1] - ey) ** 2) ** 0.5
        return distance < (self.get_radius() + radius)

    def get_radius(self):
        return int(100 - int(self.score))

    def has_expired(self):
        return self.get_radius() < 2


class GameState:
    FRAMERATE = 30

    def __init__(self, num_players=2):
        self.score = 0
        self.lives = 3

        self.colors = [
            (255 * i, 128 * (num_players - i), 64 * i) for i in range(num_players)
        ]
        self.enemies = {
            player_id: [
                Enemy(
                    (random.randint(0, 640), random.randint(0, 480)),
                    self.colors[player_id],
                )
            ]
            for player_id in range(num_players)
        }
        self.dt = 0
        self.last_time = time.time()

    def update(self, frame: cv2.Mat):
        self.dt = time.time() - self.last_time

        frame = self._draw_update(frame)

        if self.dt >= 1 / self.FRAMERATE:
            frame = self._game_update(frame)
            self.last_time = time.time()

        return frame

    def _draw_update(self, frame: cv2.Mat):
        # Draw enemies
        for player_id, enemies in self.enemies.items():
            for enemy in enemies:
                frame = enemy.draw(frame)
        return frame

    def _game_update(self, frame: cv2.Mat):
        for player_id in self.enemies.keys():
            num_enemies = len(self.enemies[player_id])
            # Spawn new enemies randomly 5% chance per frame, min 1 max 3 enemies
            if (random.random() < 0.01 or num_enemies == 0) and num_enemies < 3:
                pos = self.find_spawn_position(frame, self.enemies[player_id])
                if pos is not None:
                    self.enemies[player_id].append(Enemy(pos, self.colors[player_id]))

            for enemy in self.enemies[player_id]:
                enemy.update(self.dt)
                if enemy.has_expired():
                    self.lives -= 1
                    self.enemies[player_id].remove(enemy)
        return frame

    def find_spawn_position(self, frame: cv2.Mat, enemies: list[Enemy]):
        h, w, _ = frame.shape
        initial_radius = Enemy.initial_radius()
        for _ in range(100):  # Try 100 times to find a valid position
            x = random.randint(initial_radius, w - initial_radius)
            y = random.randint(initial_radius, h - initial_radius)

            if self._goes_outside(frame, x, y):
                continue
            will_collide = False
            for enemy in enemies:
                if enemy.is_colliding((x, y), initial_radius):
                    will_collide = True
                    break
            if will_collide:
                continue
            return x, y
        return None

    def _goes_outside(self, frame: cv2.Mat, x: int, y: int):
        h, w, _ = frame.shape
        size = Enemy.initial_radius()
        if x - size < 0 or x + size > w or y - size < 0 or y + size > h:
            return True
        return False

    # def _will_collide(self, x: int, y: int, enemies: list[Enemy]):
    #     for enemy in enemies:
    #         ex, ey = enemy.position
    #         distance = ((x - ex) ** 2 + (y - ey) ** 2) ** 0.5
    #         if distance < enemy.get_radius() + 30:  # 30 is a buffer
    #             return True
    #     return False

    def draw_enemy(self, frame: cv2.Mat, enemy: Enemy):
        x, y = enemy.position
        w, h = enemy.size
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        return frame


game_state = GameState()


def game(frame):

    # x, y, w, h = cv2.getWindowImageRect(win_name)
    # cv2.rectangle(frame, (50, 50), (200, 200), (0, 0, 0), -1)

    frame = game_state.update(frame)
    print(f"0 Enemies: {len(game_state.enemies[0])}, Lives: {game_state.lives}")
    print(f"1 Enemies: {len(game_state.enemies[1])}, Lives: {game_state.lives}")
    return frame
