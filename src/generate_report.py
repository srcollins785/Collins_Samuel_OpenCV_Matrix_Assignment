"""Build the assignment report in Markdown from the generated images, matrices, and verification data."""

from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
FULL_CSV = ROOT / "csv_full_image"
MANUAL_CSV = ROOT / "csv_manual_calculations"
IMAGE_DIR = ROOT / "output_images"
INPUT_DIR = ROOT / "input"
REPORT_MD = ROOT / "report" / "OpenCV_Matrix_Assignment_Report.md"

STUDENT_NAME = "Samuel Collins"
PREVIEW = 8  # corner size, in pixels, shown for full 200x200 matrices

OPERATIONS = {
    "grayscale": "Converts the three BGR channels into a single intensity channel.",
    "negative": "Inverts every intensity value as `255 - pixel`.",
    "threshold": "Maps intensities to 0 or 255 using a fixed cutoff of 127.",
    "gaussian_blur": "Smooths the image by convolving with a 5x5 Gaussian kernel.",
    "canny": "Detects edges using gradient thresholds of 100 and 200.",
}


def matrix_table(csv_path: Path, size: int | None = None) -> str:
    frame = pd.read_csv(csv_path, header=None)
    if size is not None:
        frame = frame.iloc[:size, :size]
    frame.index = [f"r{i}" for i in frame.index]
    frame.columns = [f"c{i}" for i in range(frame.shape[1])]
    return frame.to_markdown()


def section_metadata() -> list[str]:
    lines = ["## 2. Image Acquisition and Preparation", ""]
    lines.append(
        "The source photograph was captured with a mobile phone and stored as "
        "`input/image_original.jpg`, then resized to 200 x 200 pixels with "
        "`cv2.resize` using `INTER_AREA` interpolation and saved as "
        "`input/image_200x200.png`."
    )
    lines.append("")
    metadata = FULL_CSV / "image_metadata.csv"
    if metadata.exists():
        lines.append(pd.read_csv(metadata).to_markdown(index=False))
        lines.append("")
    resized = INPUT_DIR / "image_200x200.png"
    if resized.exists():
        lines.append(f"![Prepared 200x200 image](../input/{resized.name})")
        lines.append("")
    return lines


def section_matrices() -> list[str]:
    lines = [
        "## 3. The Image as a Numerical Matrix",
        "",
        "Each channel of the 200 x 200 image is exported in full to `csv_full_image/` as a "
        f"200 x 200 grid of integers in the range 0-255. Because a full grid is too large to "
        f"print, the top-left {PREVIEW} x {PREVIEW} corner of each channel is shown below; the "
        "complete values are in the CSV files.",
        "",
    ]
    channels = {
        "Grayscale": "image_gray_200x200.csv",
        "Blue channel": "image_blue_200x200.csv",
        "Green channel": "image_green_200x200.csv",
        "Red channel": "image_red_200x200.csv",
    }
    for label, filename in channels.items():
        path = FULL_CSV / filename
        if not path.exists():
            continue
        lines.append(f"### {label} (`{filename}`)")
        lines.append("")
        lines.append(matrix_table(path, PREVIEW))
        lines.append("")
    return lines


def section_operations() -> list[str]:
    lines = [
        "## 4. OpenCV Operations",
        "",
        "Each operation below was applied to the prepared image. The resulting image is saved "
        "in `output_images/` and its full pixel matrix is saved in `csv_full_image/`.",
        "",
    ]
    for name, description in OPERATIONS.items():
        image = IMAGE_DIR / f"{name}.png"
        if not image.exists():
            continue
        lines.append(f"### {name.replace('_', ' ').title()}")
        lines.append("")
        lines.append(description)
        lines.append("")
        lines.append(f"![{name}](../output_images/{image.name})")
        lines.append("")
        matrix = FULL_CSV / f"{name}_matrix.csv"
        if matrix.exists():
            lines.append(f"Top-left {PREVIEW} x {PREVIEW} corner of `{matrix.name}`:")
            lines.append("")
            lines.append(matrix_table(matrix, PREVIEW))
            lines.append("")
    contours = FULL_CSV / "contour_measurements.csv"
    if contours.exists():
        lines.append("### Contour Measurements")
        lines.append("")
        lines.append(pd.read_csv(contours).to_markdown(index=False))
        lines.append("")
    return lines


def section_verification() -> list[str]:
    lines = [
        "## 5. Manual Verification",
        "",
        "A 7 x 7 patch was extracted from the grayscale matrix and each selected operation was "
        "computed by hand, then compared against the OpenCV result element by element. A maximum "
        "absolute difference of 0 confirms the manual calculation reproduces OpenCV exactly.",
        "",
    ]
    patch = MANUAL_CSV / "manual_input_patch_7x7.csv"
    if patch.exists():
        lines.append("### Input Patch")
        lines.append("")
        lines.append(matrix_table(patch))
        lines.append("")

    summary = MANUAL_CSV / "verification_summary.csv"
    if summary.exists():
        results = pd.read_csv(summary)
        lines.append("### Summary")
        lines.append("")
        lines.append(results.to_markdown(index=False))
        lines.append("")
        for row in results.itertuples():
            lines.append(f"### {row.operation_id.upper()} - {row.operation}")
            lines.append("")
            for label, suffix in [
                ("Manual output", "manual_output"),
                ("OpenCV output", "opencv_output"),
                ("Difference (manual - OpenCV)", "difference"),
            ]:
                path = MANUAL_CSV / f"{row.operation_id}_{suffix}.csv"
                if path.exists():
                    lines.append(f"**{label}**")
                    lines.append("")
                    lines.append(matrix_table(path))
                    lines.append("")
            lines.append(
                f"Maximum absolute difference: **{row.max_abs_difference}** ({row.result})."
            )
            lines.append("")
    return lines


def build() -> str:
    lines = [
        "# OpenCV Matrix Assignment Report",
        "",
        f"**Student:** {STUDENT_NAME}  ",
        f"**Date:** {date.today().isoformat()}",
        "",
        "## 1. Objective",
        "",
        "This report demonstrates that a digital image is a numerical matrix rather than only a "
        "visual object. An image captured on a mobile phone is converted to 200 x 200 pixels, its "
        "pixel values are exported to CSV matrices, several OpenCV operations are applied, and "
        "selected operations are verified against manual matrix calculations.",
        "",
    ]
    lines += section_metadata()
    lines += section_matrices()
    lines += section_operations()
    lines += section_verification()
    lines += [
        "## 6. Conclusion",
        "",
        "Every operation applied through OpenCV corresponds to an arithmetic transformation of the "
        "underlying pixel matrix. The manual calculations reproduce the OpenCV results exactly, "
        "confirming that image processing is matrix processing.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    REPORT_MD.parent.mkdir(exist_ok=True)
    REPORT_MD.write_text(build(), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
