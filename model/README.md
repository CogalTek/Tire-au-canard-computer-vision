# Models

To create a custom hand detection model, follow these steps:

1. **Extend AModel**: Create a new class that inherits from `AModel` and implement the `process()` method to handle frame processing.

    ```python
    from .amodel import AModel
    
    class MyCustomModel(AModel):
         def process(self, frame):
              # Your hand detection logic here
              return AModel.Results(
                    multi_hand_landmarks=[...],
                    multi_hand_world_landmarks=[...],
                    multi_handedness=[...]
              )
    ```

2. **Register in available_models.py**: Add your model to the `available_models` list in `available_models.py`.

    ```python
    from .my_custom_model import MyCustomModel
    
    available_models = [MyCustomModel]
    ```

Your model should return an `AModel.Results` object containing hand landmarks, world landmarks, and handedness information.