# Model

## How models are used

- The code expects a model implementing the AModel interface (see model/amodel.py). The game instantiates a model and calls its `process(frame_rgb)` method. The result must provide:
    - `multi_hand_landmarks` (2D image landmarks),
    - `multi_hand_world_landmarks` (3D/world landmarks used for angles/projection),
    - `multi_handedness` (hand labels/side).
- At runtime the chosen model is stored on `Model.hands` and is used by `Model.process_frame` → `Model.update_player_hand_metrics` to compute screen position, orientation, projected shooting point and shooting detection.

## Current behaviour and quality

- By default the project currently selects a model from `model.available_models` (the selection is done at instantiation time).
- Pros of a full-featured model (e.g. MediaPipe Hands):
    - Reliable 2D landmarks, world landmarks for approximate 3D, low inference latency on CPU/GPU.
    - Good handedness classification and multi-hand support.
- Cons / pitfalls to watch:
    - Not all model implementations expose `multi_hand_world_landmarks`. If missing, 3D-based features (angles, forward projection, robust shooting thresholds) degrade or must fallback to image-space heuristics.
    - Some models trade accuracy for speed or vice‑versa; finger tip jitter and false positives can affect shooting detection.
    - Lighting, camera resolution and finger occlusions will reduce robustness.

## How to change the model used in the game

### Add a new model implementation
- Implement the AModel interface (copy pattern from existing implementations in model/).
- Add your class to `available_models` in the model package (model/available_models.py) so it can be discovered/selected.
- Be aware that if more than one model is in the `available_models` list, the model will be chosen randomly

### Make your implementation the default one
- Remove all other implementation from `available_models` in model/available_models.py

## Validation checklist after switching
- Confirm `process_frame` returns `multi_hand_landmarks`, `multi_hand_world_landmarks`, and `multi_handedness`.
- Verify FPS on target hardware and measure detection jitter.
- Test shooting detection at typical hand distances and lighting; adjust thresholds (e.g. 3D distance threshold, bend-angle) if needed.

## Notes
- If the new model lacks world landmarks, either implement a mapping or update code to degrade gracefully (image-space projection / simpler shooting logic).
- For reproducible behavior in the game, avoid random selection in production — pick a specific, validated model.