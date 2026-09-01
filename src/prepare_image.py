"""Resize the original input image to the 200x200 working image used by the assignment."""

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "input"

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


def main() -> None:
    INPUT_DIR.mkdir(exist_ok=True)
    original = load_original()
    validate_square(original)
    resized = resize(original)
    validate_output(resized)
    cv2.imwrite(str(RESIZED), resized)
    print(f"Wrote {RESIZED} ({resized.shape[1]}x{resized.shape[0]}), confirmed 200x200")


if __name__ == "__main__":
    main()
