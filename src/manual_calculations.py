"""Part C: manual matrix calculations on a 7x7 grayscale patch.

Every manual result is computed here with explicit arithmetic (NumPy indexing, loops, and
scalar math). No manual result is produced by calling the OpenCV function it will be checked
against. For 3x3 neighborhood operations only the central 5x5 output is produced, so that
OpenCV's border padding never influences the comparison.

This module only writes the input, kernel, manual-output, and OpenCV-output matrices.
Comparing them is the job of verify_matrices.py.
"""

import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLOR_IMAGE = ROOT / "input" / "image_200x200.png"
GRAY_CSV = ROOT / "csv_full_image" / "image_gray_200x200.csv"
CSV_DIR = ROOT / "csv_manual_calculations"

PATCH_SIZE = 7
VALID_SIZE = PATCH_SIZE - 2

# Pixels sampled from spread-out locations for the manual grayscale check.
SAMPLE_PIXELS = [(0, 0), (50, 150), (100, 100), (150, 50), (199, 199)]

MEAN_KERNEL = np.ones((3, 3)) / 9.0
GAUSSIAN_KERNEL = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], float) / 16.0
SOBEL_GX = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)
SOBEL_GY = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], float)
MORPH_KERNEL = np.ones((3, 3), np.uint8)

BRIGHTNESS_OFFSET = 40
CONTRAST_SCALE = 1.25
THRESHOLD_VALUE = 127

EXAMPLE_CELLS = [(0, 0), (2, 2), (4, 4)]

# Operations whose arithmetic is exact integer work must match OpenCV cell for cell.
# The rest involve floating-point weights or rounding, where one intensity level is allowed.
EXACT_OPERATIONS = {"op02", "op05", "op06", "op09", "op10", "op11", "op13", "op14"}

manifest: list[dict] = []
worked_examples: list[dict] = []


def save(matrix: np.ndarray, name: str) -> None:
    frame = pd.DataFrame(matrix)
    if np.issubdtype(np.asarray(matrix).dtype, np.floating):
        frame = frame.round(4)
    frame.to_csv(CSV_DIR / f"{name}.csv", index=False, header=False)


def load_gray() -> np.ndarray:
    if not GRAY_CSV.exists():
        raise FileNotFoundError(f"{GRAY_CSV} missing. Run opencv_operations.py first.")
    return pd.read_csv(GRAY_CSV, header=None).to_numpy(dtype=np.uint8)


def select_patch(gray: np.ndarray) -> tuple[int, int]:
    """Pick the 7x7 window with the most intensity variation."""
    best_score = -1.0
    best = (0, 0)
    for row in range(gray.shape[0] - PATCH_SIZE + 1):
        for col in range(gray.shape[1] - PATCH_SIZE + 1):
            score = float(gray[row : row + PATCH_SIZE, col : col + PATCH_SIZE].std())
            if score > best_score:
                best_score = score
                best = (row, col)
    return best


def correlate_valid(patch: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Slide the kernel by hand over every valid position and sum the products."""
    output = np.zeros((VALID_SIZE, VALID_SIZE))
    for i in range(VALID_SIZE):
        for j in range(VALID_SIZE):
            window = patch[i : i + 3, j : j + 3].astype(float)
            total = 0.0
            for m in range(3):
                for n in range(3):
                    total += float(window[m, n]) * float(kernel[m, n])
            output[i, j] = total
    return output


def rank_valid(patch: np.ndarray, statistic: str) -> np.ndarray:
    """Median, minimum (erosion), and maximum (dilation) are rank filters, not convolutions."""
    output = np.zeros((VALID_SIZE, VALID_SIZE))
    for i in range(VALID_SIZE):
        for j in range(VALID_SIZE):
            values = sorted(patch[i : i + 3, j : j + 3].astype(int).flatten().tolist())
            if statistic == "median":
                output[i, j] = values[4]
            elif statistic == "min":
                output[i, j] = values[0]
            else:
                output[i, j] = values[-1]
    return output


def record(
    op_id: str,
    label: str,
    title: str,
    source: np.ndarray,
    manual: np.ndarray,
    opencv: np.ndarray,
    kernel: np.ndarray | None = None,
) -> None:
    prefix = f"{op_id}_{label}"
    # Written under both naming patterns the assignment shows: the descriptive
    # "op07_mean_input.csv" form and the plain "op01_input.csv" form.
    for name in (prefix, op_id):
        save(source, f"{name}_input")
        save(manual, f"{name}_manual_output")
        save(opencv, f"{name}_opencv_output")
        if kernel is not None:
            save(kernel, f"{name}_kernel")

    manifest.append(
        {
            "operation_id": op_id,
            "operation": title,
            "file_prefix": prefix,
            "output_shape": f"{manual.shape[0]}x{manual.shape[1]}",
            "tolerance": 0 if op_id in EXACT_OPERATIONS else 1,
            "has_kernel": kernel is not None,
        }
    )
    print(f"{prefix}: wrote input, manual output, and OpenCV output")


def add_examples(op_id: str, title: str, patch: np.ndarray, kind: str, opencv: np.ndarray) -> None:
    """Record the substituted values and arithmetic for three representative output cells."""
    for row, col in EXAMPLE_CELLS:
        window = patch[row : row + 3, col : col + 3].astype(int)
        values = window.flatten().tolist()
        if kind == "mean":
            total = sum(values)
            calculation = (
                "O(i,j) = [I(i-1,j-1) + I(i-1,j) + I(i-1,j+1) + I(i,j-1) + I(i,j) + I(i,j+1)"
                " + I(i+1,j-1) + I(i+1,j) + I(i+1,j+1)] / 9\n"
                f"       = [{' + '.join(str(v) for v in values)}] / 9\n"
                f"       = {total} / 9 = {total / 9:.4f}"
            )
            result = total / 9
        elif kind in ("gaussian", "sobel_x", "sobel_y"):
            kernel = {
                "gaussian": GAUSSIAN_KERNEL * 16,
                "sobel_x": SOBEL_GX,
                "sobel_y": SOBEL_GY,
            }[kind]
            weights = kernel.flatten().astype(int).tolist()
            terms = " + ".join(f"({w})({v})" for w, v in zip(weights, values))
            total = sum(w * v for w, v in zip(weights, values))
            if kind == "gaussian":
                calculation = f"(1/16) x [{terms}]\n       = {total}/16 = {total / 16:.4f}"
                result = total / 16
            else:
                calculation = f"{terms}\n       = {total}"
                result = float(total)
        elif kind == "median":
            ordered = sorted(values)
            calculation = (
                f"sorted values: {', '.join(str(v) for v in ordered)}\n"
                f"       fifth of nine (the middle) = {ordered[4]}"
            )
            result = float(ordered[4])
        elif kind == "erosion":
            calculation = (
                f"min({', '.join(str(v) for v in values)}) = {min(values)}\n"
                "       (white only when every pixel under the kernel is white)"
            )
            result = float(min(values))
        else:
            calculation = (
                f"max({', '.join(str(v) for v in values)}) = {max(values)}\n"
                "       (white when at least one pixel under the kernel is white)"
            )
            result = float(max(values))

        worked_examples.append(
            {
                "operation_id": op_id,
                "operation": title,
                "output_row": row,
                "output_col": col,
                "neighborhood": json.dumps(window.tolist()),
                "calculation": calculation,
                "manual_result": round(result, 4),
                "opencv_result": round(float(opencv[row, col]), 4),
            }
        )


def add_magnitude_examples(gx: np.ndarray, gy: np.ndarray, opencv: np.ndarray) -> None:
    for row, col in EXAMPLE_CELLS:
        x, y = float(gx[row, col]), float(gy[row, col])
        result = (x**2 + y**2) ** 0.5
        worked_examples.append(
            {
                "operation_id": "op12",
                "operation": "Sobel gradient magnitude",
                "output_row": row,
                "output_col": col,
                "neighborhood": json.dumps([[x], [y]]),
                "calculation": (
                    f"G = sqrt(Gx^2 + Gy^2) = sqrt(({x:g})^2 + ({y:g})^2)\n"
                    f"       = sqrt({x**2 + y**2:g}) = {result:.4f}"
                ),
                "manual_result": round(result, 4),
                "opencv_result": round(float(opencv[row, col]), 4),
            }
        )


def grayscale_pixels(image: np.ndarray) -> None:
    """Apply I_gray = round(0.114B + 0.587G + 0.299R) by hand to five spread-out pixels."""
    opencv_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rows = []
    for row, col in SAMPLE_PIXELS:
        blue, green, red = (int(v) for v in image[row, col])
        manual = round(0.114 * blue + 0.587 * green + 0.299 * red)
        rows.append(
            {
                "row": row,
                "column": col,
                "B": blue,
                "G": green,
                "R": red,
                "manual_gray": manual,
                "opencv_gray": int(opencv_gray[row, col]),
            }
        )

    frame = pd.DataFrame(rows)
    frame["difference"] = frame["opencv_gray"] - frame["manual_gray"]
    frame.to_csv(CSV_DIR / "grayscale_pixel_verification.csv", index=False)
    for name in ("op01_grayscale", "op01"):
        frame[["row", "column", "B", "G", "R"]].to_csv(
            CSV_DIR / f"{name}_input.csv", index=False, header=False
        )
        save(frame[["manual_gray"]].to_numpy(), f"{name}_manual_output")
        save(frame[["opencv_gray"]].to_numpy(), f"{name}_opencv_output")

    manifest.append(
        {
            "operation_id": "op01",
            "operation": "Grayscale conversion (5 color pixels)",
            "file_prefix": "op01_grayscale",
            "output_shape": f"{len(frame)}x1",
            "tolerance": 1,
            "has_kernel": False,
        }
    )
    print(f"op01_grayscale: wrote {len(frame)} manually converted pixels")


def main() -> None:
    CSV_DIR.mkdir(exist_ok=True)
    image = cv2.imread(str(COLOR_IMAGE), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"{COLOR_IMAGE} missing. Run prepare_image.py first.")

    grayscale_pixels(image)

    gray = load_gray()
    row, col = select_patch(gray)
    patch = gray[row : row + PATCH_SIZE, col : col + PATCH_SIZE]
    save(patch, "manual_input_patch_7x7")
    pd.DataFrame(
        [
            {
                "start_row": row,
                "end_row": row + PATCH_SIZE - 1,
                "start_column": col,
                "end_column": col + PATCH_SIZE - 1,
                "min": int(patch.min()),
                "max": int(patch.max()),
                "std": round(float(patch.std()), 4),
            }
        ]
    ).to_csv(CSV_DIR / "patch_location.csv", index=False)
    print(f"patch: rows {row}-{row + 6}, columns {col}-{col + 6}, std {patch.std():.2f}")

    # Point operations, computed over the whole 7x7 patch.
    record(
        "op02", "negative", "Negative transformation", patch,
        (255 - patch.astype(int)).astype(np.uint8), cv2.bitwise_not(patch),
    )
    record(
        "op03", "brightness", f"Brightness adjustment (+{BRIGHTNESS_OFFSET})", patch,
        np.clip(patch.astype(int) + BRIGHTNESS_OFFSET, 0, 255).astype(np.uint8),
        cv2.add(patch, BRIGHTNESS_OFFSET),
    )
    record(
        "op04", "contrast", f"Contrast adjustment (x{CONTRAST_SCALE})", patch,
        np.clip(np.round(patch.astype(float) * CONTRAST_SCALE), 0, 255).astype(np.uint8),
        cv2.convertScaleAbs(patch, alpha=CONTRAST_SCALE, beta=0),
    )
    binary_manual = np.where(patch > THRESHOLD_VALUE, 255, 0).astype(np.uint8)
    _, binary_opencv = cv2.threshold(patch, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    record("op05", "threshold", f"Binary thresholding (>{THRESHOLD_VALUE})", patch,
           binary_manual, binary_opencv)
    record("op06", "flip_horizontal", "Horizontal flip", patch,
           patch[:, ::-1].copy(), cv2.flip(patch, 1))

    # Neighborhood operations, compared on the central 5x5 valid region only.
    mean_opencv = cv2.filter2D(patch, cv2.CV_64F, MEAN_KERNEL)[1:6, 1:6]
    record("op07", "mean", "Mean filter (3x3)", patch,
           correlate_valid(patch, MEAN_KERNEL), mean_opencv, MEAN_KERNEL)
    add_examples("op07", "Mean filter (3x3)", patch, "mean", mean_opencv)

    gaussian_opencv = cv2.filter2D(patch, cv2.CV_64F, GAUSSIAN_KERNEL)[1:6, 1:6]
    record("op08", "gaussian", "Gaussian filter (3x3)", patch,
           correlate_valid(patch, GAUSSIAN_KERNEL), gaussian_opencv, GAUSSIAN_KERNEL)
    add_examples("op08", "Gaussian filter (3x3)", patch, "gaussian", gaussian_opencv)

    median_opencv = cv2.medianBlur(patch, 3)[1:6, 1:6]
    record("op09", "median", "Median filter (3x3)", patch,
           rank_valid(patch, "median"), median_opencv)
    add_examples("op09", "Median filter (3x3)", patch, "median", median_opencv)

    gx_manual = correlate_valid(patch, SOBEL_GX)
    gy_manual = correlate_valid(patch, SOBEL_GY)
    gx_opencv = cv2.Sobel(patch, cv2.CV_64F, 1, 0, ksize=3)[1:6, 1:6]
    gy_opencv = cv2.Sobel(patch, cv2.CV_64F, 0, 1, ksize=3)[1:6, 1:6]
    record("op10", "sobel_gx", "Sobel Gx", patch, gx_manual, gx_opencv, SOBEL_GX)
    add_examples("op10", "Sobel Gx", patch, "sobel_x", gx_opencv)
    record("op11", "sobel_gy", "Sobel Gy", patch, gy_manual, gy_opencv, SOBEL_GY)
    add_examples("op11", "Sobel Gy", patch, "sobel_y", gy_opencv)

    magnitude_opencv = np.sqrt(gx_opencv**2 + gy_opencv**2)
    record("op12", "sobel_magnitude", "Sobel gradient magnitude", patch,
           np.sqrt(gx_manual**2 + gy_manual**2), magnitude_opencv)
    add_magnitude_examples(gx_manual, gy_manual, magnitude_opencv)

    erosion_opencv = cv2.erode(binary_opencv, MORPH_KERNEL)[1:6, 1:6]
    record("op13", "erosion", "Erosion (3x3 ones)", binary_manual,
           rank_valid(binary_manual, "min").astype(np.uint8), erosion_opencv, MORPH_KERNEL)
    add_examples("op13", "Erosion (3x3 ones)", binary_manual, "erosion", erosion_opencv)

    dilation_opencv = cv2.dilate(binary_opencv, MORPH_KERNEL)[1:6, 1:6]
    record("op14", "dilation", "Dilation (3x3 ones)", binary_manual,
           rank_valid(binary_manual, "max").astype(np.uint8), dilation_opencv, MORPH_KERNEL)
    add_examples("op14", "Dilation (3x3 ones)", binary_manual, "dilation", dilation_opencv)

    pd.DataFrame(manifest).to_csv(CSV_DIR / "manual_operations_manifest.csv", index=False)
    pd.DataFrame(worked_examples).to_csv(CSV_DIR / "manual_worked_examples.csv", index=False)
    print(f"\n{len(manifest)} manual operations written to {CSV_DIR}")


if __name__ == "__main__":
    main()
