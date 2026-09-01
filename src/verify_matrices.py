"""Compare hand-calculated results against OpenCV output.

Two checks are performed: per-pixel grayscale conversion on selected pixels, and full
operation matrices on a 7x7 patch.
"""

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLOR_IMAGE = ROOT / "input" / "image_200x200.png"
GRAY_CSV = ROOT / "csv_full_image" / "image_gray_200x200.csv"
CSV_DIR = ROOT / "csv_manual_calculations"

PATCH_SIZE = 7
PATCH_ORIGIN = (0, 0)  # top-left (row, col) of the patch inside the 200x200 image

# Pixels sampled from spread-out locations for the manual grayscale check.
SAMPLE_PIXELS = [(0, 0), (50, 150), (100, 100), (150, 50), (199, 199)]


def load_patch() -> np.ndarray:
    if not GRAY_CSV.exists():
        raise FileNotFoundError(f"{GRAY_CSV} missing. Run opencv_operations.py first.")
    gray = pd.read_csv(GRAY_CSV, header=None).to_numpy(dtype=np.uint8)
    row, col = PATCH_ORIGIN
    return gray[row : row + PATCH_SIZE, col : col + PATCH_SIZE]


def manual_negative(patch: np.ndarray) -> np.ndarray:
    return (255 - patch.astype(np.int32)).astype(np.uint8)


def opencv_negative(patch: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(patch)


def save(matrix: np.ndarray, name: str) -> None:
    pd.DataFrame(matrix).to_csv(CSV_DIR / f"{name}.csv", index=False, header=False)


def verify_grayscale_pixels() -> None:
    """Check I_gray = round(0.114B + 0.587G + 0.299R) against cv2.cvtColor pixel by pixel."""
    image = cv2.imread(str(COLOR_IMAGE), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"{COLOR_IMAGE} missing. Run prepare_image.py first.")
    opencv_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rows = []
    for row, col in SAMPLE_PIXELS:
        blue, green, red = (int(v) for v in image[row, col])
        manual = round(0.114 * blue + 0.587 * green + 0.299 * red)
        actual = int(opencv_gray[row, col])
        rows.append(
            {
                "row": row,
                "column": col,
                "B": blue,
                "G": green,
                "R": red,
                "manual_gray": manual,
                "opencv_gray": actual,
                "difference": manual - actual,
            }
        )

    frame = pd.DataFrame(rows)
    frame.to_csv(CSV_DIR / "grayscale_pixel_verification.csv", index=False)
    worst = int(frame["difference"].abs().max())
    print(f"grayscale pixels: {len(frame)} checked, max absolute difference = {worst}")


def compare(op_id: str, label: str, patch: np.ndarray, manual: np.ndarray, opencv: np.ndarray) -> dict:
    difference = manual.astype(np.int32) - opencv.astype(np.int32)
    save(patch, f"{op_id}_input")
    save(manual, f"{op_id}_manual_output")
    save(opencv, f"{op_id}_opencv_output")
    save(difference, f"{op_id}_difference")
    max_diff = int(np.abs(difference).max())
    print(f"{op_id}: max absolute difference = {max_diff} ({'match' if max_diff == 0 else 'MISMATCH'})")
    return {
        "operation_id": op_id,
        "operation": label,
        "max_abs_difference": max_diff,
        "mean_abs_difference": float(np.abs(difference).mean()),
        "result": "MATCH" if max_diff == 0 else "MISMATCH",
    }


def main() -> None:
    CSV_DIR.mkdir(exist_ok=True)
    verify_grayscale_pixels()
    patch = load_patch()
    save(patch, "manual_input_patch_7x7")

    results = [
        compare("op01", "Negative (255 - pixel)", patch, manual_negative(patch), opencv_negative(patch)),
    ]
    pd.DataFrame(results).to_csv(CSV_DIR / "verification_summary.csv", index=False)


if __name__ == "__main__":
    main()
