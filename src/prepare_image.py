"""Resize the cropped square photograph to the 200x200 working image used by the assignment."""

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
CSV_DIR = ROOT / "csv_full_image"

UNCROPPED = INPUT_DIR / "image_original_not_cropped.jpg"
ORIGINAL = INPUT_DIR / "image_original.jpg"
RESIZED = INPUT_DIR / "image_200x200.png"
SIZE = (200, 200)


def load_original() -> np.ndarray:
    image = cv2.imread(str(ORIGINAL), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read {ORIGINAL}. Place your source photo there.")
    return image


def validate_square(image: np.ndarray) -> None:
    height, width = image.shape[:2]
    if height != width:
        raise ValueError(
            f"{ORIGINAL.name} is {width}x{height}, not square. Resizing it to "
            f"{SIZE[0]}x{SIZE[1]} would distort the aspect ratio. Crop the photo to a square "
            "before running this script."
        )


def resize(image: np.ndarray) -> np.ndarray:
    return cv2.resize(image, SIZE, interpolation=cv2.INTER_AREA)


def validate_output(resized: np.ndarray) -> None:
    if resized.shape[:2] != (SIZE[1], SIZE[0]):
        raise ValueError(f"Resized image is {resized.shape[:2]}, expected {(SIZE[1], SIZE[0])}.")


def record_stages(resized: np.ndarray) -> None:
    """Document the acquisition chain from mobile-camera photo to final working image."""
    stages = [
        ("1. Original mobile-camera photograph", UNCROPPED),
        ("2. Cropped square image", ORIGINAL),
    ]
    rows = []
    for label, path in stages:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            continue
        rows.append(
            {
                "stage": label,
                "file": path.name,
                "width": image.shape[1],
                "height": image.shape[0],
                "channels": image.shape[2],
                "aspect_ratio": round(image.shape[1] / image.shape[0], 4),
            }
        )
    rows.append(
        {
            "stage": "3. Final working image",
            "file": RESIZED.name,
            "width": resized.shape[1],
            "height": resized.shape[0],
            "channels": resized.shape[2],
            "aspect_ratio": round(resized.shape[1] / resized.shape[0], 4),
        }
    )
    CSV_DIR.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(CSV_DIR / "source_image_stages.csv", index=False)


def main() -> None:
    INPUT_DIR.mkdir(exist_ok=True)
    original = load_original()
    validate_square(original)
    resized = resize(original)
    validate_output(resized)
    cv2.imwrite(str(RESIZED), resized)
    record_stages(resized)
    print(f"Wrote {RESIZED} ({resized.shape[1]}x{resized.shape[0]}), confirmed 200x200")


if __name__ == "__main__":
    main()
