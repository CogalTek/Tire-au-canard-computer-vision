from dataclasses import dataclass


@dataclass
class PlayerHand:
    @dataclass
    class Angle:
        pitch: float
        roll: float
        yaw: float

    @property
    def is_active(self) -> bool:
        """Le joueur est considéré comme actif s'il a été détecté récemment (moins de 5 frames) et qu'il a un ID valide"""
        return self.id is not None and self._time_since_last_claimed < 5

    id: int = None

    is_shooting: bool = False

    angle: Angle = None
    pos: tuple[int, int] = (0, 0)
    projected_pos: tuple[int, int] = (0, 0)
    average_dist_3D: float = 0.5
    wrist_pos_3d: tuple[float, float, float] = None

    # Number of frames since the hand was last detected, used to determine when to remove a player from the game
    _time_since_last_claimed: int = 0

    def claim(self):
        """Marque ce joueur comme actif et réinitialise le compteur de temps depuis la dernière détection"""
        self._time_since_last_claimed = 0

    def update(self):
        if not self.is_active:
            return  # Ne rien faire si le joueur n'est pas actif
        self._time_since_last_claimed += 1
