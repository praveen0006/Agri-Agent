import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import requests

# Define the growth stages in chronological order (for reference/logic)
GROWTH_STAGES = {
    0: "Stage 3: Squaring (Bud Formation)",
    1: "Stage 2: Germination & Seedling",
    2: "Stage 4: Flowering & Early Boll Development",
    3: "Stage 5: Boll Filling & Maturation",
    4: "Stage 6: Late Season (Boll Opening)",
    5: "Stage 1: Vegetative Canopy Development",
}

# Mapping for the model indices to logical display names
MODEL_LABELS = GROWTH_STAGES


class CottonStageModel:
    def __init__(self, model_path="models/cotton_stage_best.pth", num_classes=6):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path, num_classes)
        self.transform = transforms.Compose(
            [
                transforms.Resize((512, 512)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    def _load_model(self, path, num_classes):
        # Recreate the architecture from the user's notebook
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)

        if os.path.exists(path):
            try:
                checkpoint = torch.load(path, map_location=self.device)

                # Robust extraction: find any key that looks like a state dict or has 'model' in it
                state_dict = None
                if hasattr(checkpoint, "keys"):
                    # Check for common wrappers
                    for key in ["model_state", "model", "state_dict"]:
                        if key in checkpoint:
                            state_dict = checkpoint[key]
                            break

                    # If still not found, search keys for any that contain 'model' or 'state'
                    if state_dict is None:
                        for k in checkpoint.keys():
                            if isinstance(k, str) and ("model" in k.lower() or "state" in k.lower()):
                                state_dict = checkpoint[k]
                                break

                    # Fallback to the checkpoint itself
                    if state_dict is None:
                        state_dict = checkpoint
                else:
                    state_dict = checkpoint

                # Final check: if it's a dict and has 'features.0.0.weight', it's likely the right one
                model.load_state_dict(state_dict, strict=False)
                print(f"Successfully loaded model weights from {path}")

            except Exception as e:
                print(f"Error loading model weights: {e}. Running with random weights.")
        else:
            print(f"Warning: Model path {path} not found. Running with uninitialized weights.")

        model.to(self.device)
        model.eval()
        return model

    def predict(self, image_input):
        """
        Takes an image (PIL Image, bytes, or path) and returns the detected stage.
        """
        try:
            if isinstance(image_input, str):
                image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, bytes):
                image = Image.open(io.BytesIO(image_input)).convert("RGB")
            elif isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
            else:
                return "Unknown Image Format"

            img_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(img_tensor)
                _, predicted = torch.max(outputs, 1)
                class_idx = predicted.item()

            return MODEL_LABELS.get(class_idx, "Unknown Stage")

        except Exception as e:
            return f"Inference Error: {str(e)}"


# Singleton instance for the agent tools
_vision_model = None


def get_plant_growth_stage(image_bytes=None, camera_url=None):
    """
    Detects the cotton growth stage from an image.
    If no image is provided, it tries to fetch from the camera URL.
    """
    global _vision_model
    if _vision_model is None:
        # Initializing only on first call
        _vision_model = CottonStageModel()

    if image_bytes:
        return _vision_model.predict(image_bytes)

    if camera_url:
        try:
            response = requests.get(camera_url, timeout=5)
            if response.status_code == 200:
                return _vision_model.predict(response.content)
        except:
            pass

    return "Camera Unavailable"


if __name__ == "__main__":
    # Test with a mock image if needed
    print("Plant Stage Vision Tool initialized.")
    # result = get_plant_growth_stage(camera_url="http://192.168.0.124:8080/video")
    # print(f"Detected Stage: {result}")
