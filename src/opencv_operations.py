"""Run the required OpenCV operations on the 200x200 image and export images plus matrices."""

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_IMAGE = ROOT / "input" / "image_200x200.png"
IMAGE_DIR = ROOT / "output_images"
CSV_DIR = ROOT / "csv_full_image"


def load_image() -> np.ndarray:
    image = cv2.imread(str(INPUT_IMAGE), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read {INPUT_IMAGE}. Run prepare_image.py first.")
    return image


def save_matrix(matrix: np.ndarray, name: str) -> None:
    pd.DataFrame(matrix).to_csv(CSV_DIR / f"{name}.csv", index=False, header=False)


def write_metadata(image: np.ndarray, gray: np.ndarray) -> None:
    height, width, channels = image.shape
    rows = [
        ("width", width),
        ("height", height),
        ("channels", channels),
        ("shape", f"{image.shape}"),
        ("dtype", str(image.dtype)),
        # OpenCV's imread returns channels in BGR order, not RGB.
        ("channel_order", "BGR"),
        ("min_pixel_value", int(image.min())),
        ("max_pixel_value", int(image.max())),
        ("mean_pixel_value", round(float(image.mean()), 4)),
        ("std_pixel_value", round(float(image.std()), 4)),
        ("gray_min_pixel_value", int(gray.min())),
        ("gray_max_pixel_value", int(gray.max())),
        ("gray_mean_pixel_value", round(float(gray.mean()), 4)),
        ("gray_std_pixel_value", round(float(gray.std()), 4)),
    ]
    pd.DataFrame(rows, columns=["property", "value"]).to_csv(
        CSV_DIR / "image_metadata.csv", index=False
    )


def save_result(image: np.ndarray, name: str) -> None:
    cv2.imwrite(str(IMAGE_DIR / f"{name}.png"), image)
    save_matrix(image, f"{name}_matrix")


def export_channels(image: np.ndarray, gray: np.ndarray) -> None:
    blue, green, red = cv2.split(image)
    save_matrix(gray, "image_gray_200x200")
    save_matrix(blue, "image_blue_200x200")
    save_matrix(green, "image_green_200x200")
    save_matrix(red, "image_red_200x200")


def export_contours(binary: np.ndarray) -> None:
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rows = [
        {
            "contour_id": i,
            "area": cv2.contourArea(c),
            "perimeter": cv2.arcLength(c, True),
            "points": len(c),
        }
        for i, c in enumerate(contours)
    ]
    pd.DataFrame(rows).to_csv(CSV_DIR / "contour_measurements.csv", index=False)


def main() -> None:
    IMAGE_DIR.mkdir(exist_ok=True)
    CSV_DIR.mkdir(exist_ok=True)

    image = load_image()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    write_metadata(image, gray)
    export_channels(image, gray)

    save_result(gray, "grayscale")
    save_result(cv2.bitwise_not(gray), "negative")

    _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    save_result(threshold, "threshold")

    save_result(cv2.GaussianBlur(gray, (5, 5), 0), "gaussian_blur")
    save_result(cv2.Canny(gray, 100, 200), "canny")

    export_contours(threshold)
    print(f"Wrote outputs to {IMAGE_DIR} and matrices to {CSV_DIR}")


if __name__ == "__main__":
    main()
