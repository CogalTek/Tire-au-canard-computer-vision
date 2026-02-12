
# Tire-au-canard — Computer Vision Duck Shooting

Simple local multiplayer game that uses hand gestures as input to "shoot" targets on screen.

## Quickstart

Prerequisites: Python 3.10+ and a camera.

1. Create and activate a virtual environment, then install dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the game:

```sh
python main.py
```

## Controls
- Form a "fingergun" to aim; use either shooting method in docs.
- Press Tab to cycle available cameras if the default camera isn't the one you want.

Detailed gameplay notes: [docs/HOW_TO_PLAY.md](docs/HOW_TO_PLAY.md)

## Project layout (selected)
- `main.py` — game entrypoint
- `game.py`, `model.py`, `global_data.py` — core game and model glue
- `components/` — UI/game components
- `assets/` — game assets (images, sounds, exported model files, etc.)
- `docs/` — documentation (how to play, model notes)

## Contributing
PRs welcome. If you retrain the model, please document the steps in `docs/MODEL.md` and include any exported model files in `assets/` or provide download instructions.

