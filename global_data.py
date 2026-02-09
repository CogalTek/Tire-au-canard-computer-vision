from dataclasses import dataclass


@dataclass
class GlobalData:
    fps: float = 0.0
    dt: float = 0.0
    running: bool = True

    _signals: dict[str, list[callable]] = None

    @classmethod
    def emit(cls, signal_name: str, *args, **kwargs):
        """Émet un signal à tous les abonnés"""
        if cls._signals is None:
            cls._signals = {}
        for callback in cls._signals.get(signal_name, []):
            callback(*args, **kwargs)

    @classmethod
    def subscribe(cls, signal_name: str, callback: callable):
        """Abonne une fonction à un signal"""
        if cls._signals is None:
            cls._signals = {}
        if signal_name not in cls._signals:
            cls._signals[signal_name] = []
        cls._signals[signal_name].append(callback)
