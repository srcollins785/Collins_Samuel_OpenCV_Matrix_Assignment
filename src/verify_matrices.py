"""Compare hand-calculated results against OpenCV output on a 7x7 patch."""

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
GRAY_CSV = ROOT / "csv_full_image" / "image_gray_200x200.csv"
CSV_DIR = ROOT / "csv_manual_calculations"

PATCH_SIZE = 7
PATCH_ORIGIN = (0, 0)  # top-left (row, col) of the patch inside the 200x200 image


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


def compare(op_id: str, patch: np.ndarray, manual: np.ndarray, opencv: np.ndarray) -> None:
    difference = manual.astype(np.int32) - opencv.astype(np.int32)
    save(patch, f"{op_id}_input")
    save(manual, f"{op_id}_manual_output")
    save(opencv, f"{op_id}_opencv_output")
    save(difference, f"{op_id}_difference")
    max_diff = int(np.abs(difference).max())
    print(f"{op_id}: max absolute difference = {max_diff} ({'match' if max_diff == 0 else 'MISMATCH'})")


def main() -> None:
    CSV_DIR.mkdir(exist_ok=True)
    patch = load_patch()
    save(patch, "manual_input_patch_7x7")
    compare("op01", patch, manual_negative(patch), opencv_negative(patch))


if __name__ == "__main__":
    main()
