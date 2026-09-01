"""Run the required OpenCV operations on the 200x200 image and export images plus matrices."""

from pathlib import Path

import cv2
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (backend must be set before pyplot import)

ROOT = Path(__file__).resolve().parent.parent
INPUT_IMAGE = ROOT / "input" / "image_200x200.png"
IMAGE_DIR = ROOT / "output_images"
CSV_DIR = ROOT / "csv_full_image"

MEAN_KERNEL = np.ones((3, 3), np.float32) / 9.0
GAUSSIAN_KERNEL = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], np.float32) / 16.0
MORPH_KERNEL = np.ones((3, 3), np.uint8)


def load_image() -> np.ndarray:
    image = cv2.imread(str(INPUT_IMAGE), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read {INPUT_IMAGE}. Run prepare_image.py first.")
    if image.shape[:2] != (200, 200):
        raise ValueError(f"Working image is {image.shape[:2]}, expected (200, 200).")
    return image


def save_matrix(matrix: np.ndarray, name: str) -> None:
    frame = pd.DataFrame(matrix)
    if np.issubdtype(matrix.dtype, np.floating):
        frame = frame.round(4)
    frame.to_csv(CSV_DIR / f"{name}.csv", index=False, header=False)


def save_image(image: np.ndarray, name: str) -> None:
    cv2.imwrite(str(IMAGE_DIR / f"{name}.png"), image)


def save_result(image: np.ndarray, name: str) -> None:
    save_image(image, name)
    save_matrix(image, f"{name}_matrix")


def save_signed_result(matrix: np.ndarray, name: str) -> None:
    """Keep signed gradient values in the CSV, but scale to 0-255 for the PNG preview."""
    save_matrix(matrix, f"{name}_matrix")
    preview = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    save_image(preview, name)


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


def save_histogram(gray: np.ndarray, name: str, title: str) -> None:
    counts = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten().astype(int)
    pd.DataFrame({"intensity": np.arange(256), "count": counts}).to_csv(
        CSV_DIR / f"{name}.csv", index=False
    )
    plt.figure(figsize=(4.5, 2.8))
    plt.bar(np.arange(256), counts, width=1.0, color="#444444")
    plt.title(title, fontsize=9)
    plt.xlabel("Intensity", fontsize=8)
    plt.ylabel("Pixel count", fontsize=8)
    plt.tick_params(labelsize=7)
    plt.tight_layout()
    plt.savefig(IMAGE_DIR / f"{name}.png", dpi=150)
    plt.close()


def color_and_intensity(image: np.ndarray, gray: np.ndarray) -> np.ndarray:
    blue, green, red = cv2.split(image)
    save_matrix(gray, "image_gray_200x200")
    save_matrix(blue, "image_blue_200x200")
    save_matrix(green, "image_green_200x200")
    save_matrix(red, "image_red_200x200")
    save_image(gray, "grayscale")
    save_image(blue, "channel_blue")
    save_image(green, "channel_green")
    save_image(red, "channel_red")

    merged = cv2.merge([blue, green, red])
    save_image(merged, "merged_color")
    if not np.array_equal(merged, image):
        raise ValueError("Merged image does not match the original; channel order may be wrong.")

    save_result(cv2.bitwise_not(gray), "negative")
    save_result(np.clip(gray.astype(np.int16) + 40, 0, 255).astype(np.uint8), "brightness_plus40")
    save_result(cv2.convertScaleAbs(gray, alpha=1.25, beta=0), "contrast_1_25")

    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    save_result(binary, "threshold")

    equalized = cv2.equalizeHist(gray)
    save_result(equalized, "histogram_equalized")
    save_histogram(gray, "histogram_original", "Original grayscale histogram")
    save_histogram(equalized, "histogram_equalized_plot", "Equalized grayscale histogram")
    return binary


def geometric(gray: np.ndarray) -> None:
    save_result(gray[50:150, 50:150], "center_crop_100x100")
    save_result(cv2.flip(gray, 1), "flip_horizontal")
    save_result(cv2.flip(gray, 0), "flip_vertical")
    save_result(cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE), "rotate_90")

    center = (gray.shape[1] / 2, gray.shape[0] / 2)
    matrix = cv2.getRotationMatrix2D(center, 30, 1.0)
    save_result(cv2.warpAffine(gray, matrix, (gray.shape[1], gray.shape[0])), "rotate_30")

    small = cv2.resize(gray, (100, 100), interpolation=cv2.INTER_AREA)
    save_result(small, "resized_100x100")

    nearest = cv2.resize(small, (200, 200), interpolation=cv2.INTER_NEAREST)
    bilinear = cv2.resize(small, (200, 200), interpolation=cv2.INTER_LINEAR)
    save_result(nearest, "upscaled_nearest")
    save_result(bilinear, "upscaled_bilinear")

    rows = []
    for label, result in [("nearest_neighbor", nearest), ("bilinear", bilinear)]:
        difference = result.astype(np.int16) - gray.astype(np.int16)
        rows.append(
            {
                "method": label,
                "mean_abs_difference": round(float(np.abs(difference).mean()), 4),
                "max_abs_difference": int(np.abs(difference).max()),
                "std_of_result": round(float(result.std()), 4),
                "unique_values": int(np.unique(result).size),
            }
        )
    pd.DataFrame(rows).to_csv(CSV_DIR / "interpolation_comparison.csv", index=False)


def spatial_filtering(gray: np.ndarray) -> None:
    save_result(cv2.filter2D(gray, -1, MEAN_KERNEL), "filter_mean_3x3")
    gaussian = cv2.filter2D(gray, -1, GAUSSIAN_KERNEL)
    save_result(gaussian, "filter_gaussian_3x3")
    # Also emitted under the name used in the assignment's required repository structure.
    save_result(gaussian, "gaussian_blur")
    save_result(cv2.medianBlur(gray, 3), "filter_median_3x3")


def edge_detection(gray: np.ndarray) -> None:
    # CV_64F keeps the negative gradient values that an unsigned 8-bit matrix would clip to zero.
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    save_signed_result(sobel_x, "sobel_x")
    save_signed_result(sobel_y, "sobel_y")
    save_signed_result(np.sqrt(sobel_x**2 + sobel_y**2), "sobel_magnitude")
    save_signed_result(cv2.Laplacian(gray, cv2.CV_64F), "laplacian")
    save_result(cv2.Canny(gray, 100, 200), "canny")


def morphology(binary: np.ndarray) -> None:
    save_result(cv2.erode(binary, MORPH_KERNEL), "morph_erosion")
    save_result(cv2.dilate(binary, MORPH_KERNEL), "morph_dilation")
    save_result(cv2.morphologyEx(binary, cv2.MORPH_OPEN, MORPH_KERNEL), "morph_opening")
    save_result(cv2.morphologyEx(binary, cv2.MORPH_CLOSE, MORPH_KERNEL), "morph_closing")


def contour_analysis(image: np.ndarray, binary: np.ndarray) -> None:
    # RETR_LIST keeps interior boundaries: the white region touches every border, so
    # RETR_EXTERNAL alone would return only a contour tracing the image frame.
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        pd.DataFrame().to_csv(CSV_DIR / "contour_measurements.csv", index=False)
        return

    mask = np.zeros(binary.shape, np.uint8)
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)
    save_result(mask, "contour_mask")

    outlined = image.copy()
    cv2.drawContours(outlined, contours, -1, (0, 0, 255), 1)
    save_image(outlined, "contours_drawn")

    frame_area = (binary.shape[0] - 1) * (binary.shape[1] - 1)
    candidates = [
        i for i, c in enumerate(contours) if cv2.contourArea(c) < frame_area
    ]
    largest = max(candidates or range(len(contours)), key=lambda i: cv2.contourArea(contours[i]))

    rows = []
    for index, contour in enumerate(contours):
        x, y, width, height = cv2.boundingRect(contour)
        moments = cv2.moments(contour)
        has_centroid = moments["m00"] != 0
        rows.append(
            {
                "contour_id": index,
                "area": round(cv2.contourArea(contour), 4),
                "perimeter": round(cv2.arcLength(contour, True), 4),
                "bbox_x": x,
                "bbox_y": y,
                "bbox_width": width,
                "bbox_height": height,
                "centroid_x": round(moments["m10"] / moments["m00"], 4) if has_centroid else "",
                "centroid_y": round(moments["m01"] / moments["m00"], 4) if has_centroid else "",
                "points": len(contour),
                "is_image_frame": cv2.contourArea(contour) >= frame_area,
                "is_largest": index == largest,
            }
        )
    pd.DataFrame(rows).to_csv(CSV_DIR / "contour_measurements.csv", index=False)
    print(f"contours: {len(contours)} found, largest (excluding frame) is id {largest}")


def main() -> None:
    IMAGE_DIR.mkdir(exist_ok=True)
    CSV_DIR.mkdir(exist_ok=True)

    image = load_image()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    write_metadata(image, gray)

    binary = color_and_intensity(image, gray)
    geometric(gray)
    spatial_filtering(gray)
    edge_detection(gray)
    morphology(binary)
    contour_analysis(image, binary)
    print(f"Wrote outputs to {IMAGE_DIR} and matrices to {CSV_DIR}")


if __name__ == "__main__":
    main()
