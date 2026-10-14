import re
import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "tomato_efficientnet_b0.pth"

IMAGE_SIZE = 224

# The three classes this project reports.
REQUIRED_CLASSES = ["Healthy", "Early Blight", "Late Blight"]


if torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
elif torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


# --------------------------------------------------
# Label normalisation
# --------------------------------------------------

def normalize_label(raw_name):
    """
    Map any common dataset class name to one of the three project labels.

    Examples:
        "Tomato___Early_blight" -> "Early Blight"
        "late_blight"           -> "Late Blight"
        "Tomato___healthy"      -> "Healthy"
    """
    key = re.sub(r"[^a-z]", "", str(raw_name).lower())

    if "healthy" in key:
        return "Healthy"
    if "early" in key:
        return "Early Blight"
    if "late" in key:
        return "Late Blight"

    # Unknown class: keep it readable rather than guessing.
    return str(raw_name).replace("_", " ").strip()


# --------------------------------------------------
# Load checkpoint
# --------------------------------------------------

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
)

class_to_idx = checkpoint["class_to_idx"]

idx_to_raw_class = {
    index: class_name
    for class_name, index in class_to_idx.items()
}

idx_to_class = {
    index: normalize_label(raw_name)
    for index, raw_name in idx_to_raw_class.items()
}


# --------------------------------------------------
# Validate classes (printed once at startup)
# --------------------------------------------------

print("")
print("[predict.py] Classes found in model checkpoint:")
for index in sorted(idx_to_raw_class):
    print(
        f"   index {index}: {idx_to_raw_class[index]!r}"
        f"  ->  {idx_to_class[index]}"
    )

_found = set(idx_to_class.values())
_missing = [name for name in REQUIRED_CLASSES if name not in _found]

if _missing:
    print(
        "[predict.py] WARNING: model has no class for: "
        + ", ".join(_missing)
    )
    print(
        "[predict.py] A model without all 3 classes cannot predict them. "
        "It must be retrained with all 3 classes."
    )

if len(_found) != len(idx_to_class):
    print(
        "[predict.py] WARNING: two checkpoint classes map to the same "
        "label. Check the class names above."
    )

print("")


# --------------------------------------------------
# Build model
# --------------------------------------------------

model = efficientnet_b0(weights=None)

input_features = model.classifier[1].in_features

model.classifier[1] = torch.nn.Linear(
    input_features,
    len(class_to_idx),
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.to(DEVICE)
model.eval()


# NOTE: this must match the preprocessing used during validation/training.
image_transform = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


# --------------------------------------------------
# Prediction
# --------------------------------------------------

def predict_disease_detailed(image_path):
    """
    Returns (label, confidence_percent, probabilities)

    probabilities: {"Healthy": %, "Early Blight": %, "Late Blight": %, ...}
    """
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = Image.open(image_path).convert("RGB")

    image_tensor = image_transform(image)
    image_tensor = image_tensor.unsqueeze(0)
    image_tensor = image_tensor.to(DEVICE)

    with torch.no_grad():
        output = model(image_tensor)

        probabilities = torch.softmax(
            output,
            dim=1,
        )[0]

    confidence_tensor, predicted_index_tensor = torch.max(
        probabilities,
        dim=0,
    )

    predicted_index = predicted_index_tensor.item()
    confidence = confidence_tensor.item() * 100

    label = idx_to_class[predicted_index]

    # Per-class probabilities, using the project's label names.
    probability_by_class = {name: 0.0 for name in REQUIRED_CLASSES}

    for index, probability in enumerate(probabilities.tolist()):
        name = idx_to_class[index]
        probability_by_class[name] = (
            probability_by_class.get(name, 0.0) + probability * 100
        )

    return label, confidence, probability_by_class


def predict_disease(image_path):
    """Controller-compatible API: returns (label, confidence_percent)."""
    label, confidence, _ = predict_disease_detailed(image_path)
    return label, confidence


# --------------------------------------------------
# Standalone test:
#   python predict.py path/to/image_or_folder [more paths...]
# --------------------------------------------------

if __name__ == "__main__":

    targets = [Path(p) for p in sys.argv[1:]]

    if not targets:
        print("Usage: python predict.py <image_or_folder> [...]")
        sys.exit(0)

    image_files = []

    for target in targets:
        if target.is_dir():
            image_files += sorted(
                p for p in target.rglob("*")
                if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
            )
        else:
            image_files.append(target)

    counts = {}

    header = f"{'File':<32}{'Prediction':<15}" + "".join(
        f"{name:<15}" for name in REQUIRED_CLASSES
    )
    print(header)
    print("-" * len(header))

    for path in image_files:
        label, confidence, probs = predict_disease_detailed(path)
        counts[label] = counts.get(label, 0) + 1

        print(
            f"{path.name[:30]:<32}{label:<15}"
            + "".join(
                f"{probs.get(name, 0.0):<15.2f}"
                for name in REQUIRED_CLASSES
            )
        )

    print("")
    print("Prediction counts:", counts)