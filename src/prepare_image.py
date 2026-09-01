"""Resize the original input image to the 200x200 working image used by the assignment."""

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"
CSV_DIR = ROOT / "csv_full_image"

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


def write_metadata(original: np.ndarray, resized: np.ndarray) -> None:
    rows = [
        {"property": "original_height", "value": original.shape[0]},
        {"property": "original_width", "value": original.shape[1]},
        {"property": "original_channels", "value": original.shape[2]},
        {"property": "resized_height", "value": resized.shape[0]},
        {"property": "resized_width", "value": resized.shape[1]},
        {"property": "resized_channels", "value": resized.shape[2]},
        {"property": "dtype", "value": str(resized.dtype)},
    ]
    pd.DataFrame(rows).to_csv(CSV_DIR / "image_metadata.csv", index=False)


def main() -> None:
    CSV_DIR.mkdir(exist_ok=True)
    original = load_original()
    validate_square(original)
    resized = resize(original)
    cv2.imwrite(str(RESIZED), resized)
    write_metadata(original, resized)
    print(f"Wrote {RESIZED} ({resized.shape[1]}x{resized.shape[0]})")


if __name__ == "__main__":
    main()
