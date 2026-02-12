# Gameplay

## Setup
Create and activate a virtual environment, then install dependencies:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
Start the game with:

```sh
python main.py
```

## Gameplay

### Start the game
- Each player should have one hand visible to the camera/screen.
- Players should use different hands (one left, one right).

### How to aim
Form a "fingergun": curl all fingers except the index and thumb, then point your hand toward the screen.

### How to shoot / click
You can use either method below:

- **Realistic (may be unreliable):** form a ~90° angle with your thumb (like pulling a firing pin). This can be less reliable when aiming straight at the camera.
- **Easy (recommended):** bring your thumb tip underneath the index finger — simpler and more consistently recognized.

### Tips & Troubleshooting
- Good lighting and a clear background improve detection accuracy.
- Make sure your hand(s) do not blend into the background
- Press Tab to switch cameras (cycle available cameras) if the default camera isn't the one you want.
- If recognition feels inconsistent, try the "Easy" shooting method and ensure both players use opposite hands.