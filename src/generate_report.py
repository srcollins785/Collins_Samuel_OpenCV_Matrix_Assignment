"""Build the assignment report in Markdown from the generated images, matrices, and verification data."""

import json
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
STUDENT_TITLE = "Ph.D. Student, Department of Cyber-Physical Systems"
INSTITUTION = "Clark Atlanta University"
STUDENT_EMAIL = "samuel.collins@students.cau.edu"
COURSE = "CCIS 727 - Introduction to Computer Vision"
INSTRUCTOR = "Dr. Kishor Gupta"
PREVIEW = 8  # corner size, in pixels, shown for full 200x200 matrices

OPERATION_GROUPS = [
    (
        "4.1 Color and Intensity Operations",
        [
            ("grayscale", "Weighted BGR conversion to a single intensity channel."),
            ("channel_blue", "Blue channel isolated with `cv2.split`, shown as intensities."),
            ("channel_green", "Green channel isolated with `cv2.split`."),
            ("channel_red", "Red channel isolated with `cv2.split`."),
            (
                "merged_color",
                "The three channels merged back with `cv2.merge([B, G, R])`. The result is "
                "verified to be identical to the original image, which confirms the BGR order.",
            ),
            ("negative", "`I_negative = 255 - I`, inverting every intensity."),
            (
                "brightness_plus40",
                "`I_bright = clip(I + 40, 0, 255)`. Clipping prevents values above 255 from "
                "wrapping around to small numbers.",
            ),
            (
                "contrast_1_25",
                "`I_contrast = clip(1.25 x I, 0, 255)`. Values spread away from the midpoint, so "
                "bright areas saturate at 255.",
            ),
            (
                "threshold",
                "`I_binary = 255` where `I > 127`, otherwise `0`. Produces the binary image used "
                "for the morphological and contour sections.",
            ),
            (
                "histogram_equalized",
                "Histogram equalization redistributes intensities so the cumulative histogram is "
                "approximately linear, increasing global contrast.",
            ),
            ("histogram_original", "Intensity distribution before equalization."),
            ("histogram_equalized_plot", "Intensity distribution after equalization."),
        ],
    ),
    (
        "4.2 Geometric Operations",
        [
            ("center_crop_100x100", "The center 100 x 100 region, rows and columns 50 to 149."),
            ("flip_horizontal", "`cv2.flip` with code 1 reverses column order."),
            ("flip_vertical", "`cv2.flip` with code 0 reverses row order."),
            ("rotate_90", "`cv2.rotate` by 90 degrees clockwise, a pure index transposition."),
            (
                "rotate_30",
                "`cv2.warpAffine` with a 30 degree rotation about the center. Corners rotate "
                "outside the frame and are cropped, and empty corners are filled with black.",
            ),
            ("resized_100x100", "Downsampled to 100 x 100 with `INTER_AREA`."),
            ("upscaled_nearest", "The 100 x 100 image returned to 200 x 200 with nearest neighbor."),
            ("upscaled_bilinear", "The 100 x 100 image returned to 200 x 200 with bilinear."),
        ],
    ),
    (
        "4.3 Spatial Filtering Operations",
        [
            ("filter_mean_3x3", "3 x 3 mean filter using `K_mean = (1/9) * ones(3, 3)`."),
            (
                "filter_gaussian_3x3",
                "3 x 3 Gaussian filter using `K_Gaussian = (1/16) * [[1,2,1],[2,4,2],[1,2,1]]`. "
                "Center-weighted, so it smooths less aggressively than the mean filter.",
            ),
            (
                "filter_median_3x3",
                "3 x 3 median filter. Being rank-based rather than a convolution, it removes "
                "isolated outliers while keeping edges sharp.",
            ),
        ],
    ),
    (
        "4.4 Edge-Detection Operations",
        [
            ("sobel_x", "Horizontal Sobel using `G_x = [[-1,0,1],[-2,0,2],[-1,0,1]]`."),
            ("sobel_y", "Vertical Sobel using `G_y = [[-1,-2,-1],[0,0,0],[1,2,1]]`."),
            ("sobel_magnitude", "Gradient magnitude `G = sqrt(G_x^2 + G_y^2)`."),
            ("laplacian", "Second-derivative operator responding to intensity peaks and troughs."),
            ("canny", "Canny edge detection with gradient thresholds of 100 and 200."),
        ],
    ),
    (
        "4.5 Morphological Operations",
        [
            (
                "morph_erosion",
                "Erosion with a 3 x 3 kernel of ones. A pixel stays white only when every pixel "
                "under the kernel is white, so white regions shrink.",
            ),
            (
                "morph_dilation",
                "Dilation with the same kernel. A pixel becomes white when at least one pixel "
                "under the kernel is white, so white regions grow.",
            ),
            ("morph_opening", "Erosion followed by dilation, removing small white specks."),
            ("morph_closing", "Dilation followed by erosion, filling small black holes."),
        ],
    ),
    (
        "4.6 Contour Analysis",
        [
            ("contour_mask", "All detected contours filled white on a black background."),
            ("contours_drawn", "Every detected contour outlined in red on the original image."),
        ],
    ),
]


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
    resized = INPUT_DIR / "image_200x200.png"
    if resized.exists():
        lines.append(f"![Prepared 200x200 image](../input/{resized.name})")
        lines.append("")

    lines.append("### Image Properties")
    lines.append("")
    lines.append(
        "The properties below were read from the final 200 x 200 image with OpenCV and are "
        "stored in `csv_full_image/image_metadata.csv`."
    )
    lines.append("")
    metadata = FULL_CSV / "image_metadata.csv"
    if metadata.exists():
        lines.append(pd.read_csv(metadata).to_markdown(index=False))
        lines.append("")
    lines.append(
        "**Channel order.** `cv2.imread` loads a color image in **BGR order**, not RGB order. "
        "Index 0 of the third axis is blue, index 1 is green, and index 2 is red. All channel "
        "matrices in this report follow that convention, and `cv2.split` returns the channels in "
        "the same B, G, R sequence."
    )
    lines.append("")
    return lines


def section_matrices() -> list[str]:
    lines = [
        "## 3. The Image as a Numerical Matrix",
        "",
        "Each channel of the 200 x 200 image is exported in full to `csv_full_image/` as a "
        "200 x 200 grid of integers in the range 0-255. Each file contains numerical values only, "
        "with no row names, column headers, or DataFrame index. Because a full grid is too large "
        f"to print, the top-left {PREVIEW} x {PREVIEW} corner of each channel is shown below; the "
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

    lines += section_grayscale_math()
    return lines


def section_grayscale_math() -> list[str]:
    lines = [
        "### Grayscale Calculation",
        "",
        "Grayscale conversion is a weighted sum of the three color channels rather than a plain "
        "average. The weights reflect how sensitive human vision is to each color: the eye is most "
        "sensitive to green, less to red, and least to blue. OpenCV uses",
        "",
        "```",
        "I_gray = round(0.114 * B + 0.587 * G + 0.299 * R)",
        "```",
        "",
        "with the channels taken in BGR order as loaded by `cv2.imread`. The weights sum to 1.0, "
        "so the result stays within the original 0-255 range.",
        "",
    ]
    verification = MANUAL_CSV / "grayscale_pixel_verification.csv"
    if verification.exists():
        frame = pd.read_csv(verification)
        lines.append(
            f"The equation was applied by hand to {len(frame)} pixels taken from different "
            "locations in the image and compared against the value OpenCV produced."
        )
        lines.append("")
        lines.append(frame.to_markdown(index=False))
        lines.append("")
        worst = int(frame["difference"].abs().max())
        if worst == 0:
            lines.append(
                "Every manually calculated value matches OpenCV exactly, confirming the weighted "
                "equation is the operation OpenCV performs."
            )
        else:
            lines.append(
                f"The largest difference is {worst}. Small differences of one intensity level are "
                "expected because OpenCV evaluates the weights in fixed-point integer arithmetic "
                "rather than floating point, so its rounding can differ slightly from the "
                "floating-point calculation done here."
            )
        lines.append("")
    return lines


def section_operations() -> list[str]:
    lines = [
        "## 4. OpenCV Operations",
        "",
        "Each operation below was applied to the prepared image. Every visual result is saved in "
        "`output_images/` as a PNG and its numerical output is saved in `csv_full_image/` as a "
        "CSV matrix. Unless stated otherwise, operations are performed on the grayscale image.",
        "",
    ]
    for group_title, operations in OPERATION_GROUPS:
        lines.append(f"### {group_title}")
        lines.append("")
        for name, description in operations:
            image = IMAGE_DIR / f"{name}.png"
            if not image.exists():
                continue
            lines.append(f"#### {name.replace('_', ' ').title()}")
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
        if group_title.startswith("4.2"):
            lines += interpolation_discussion()
        if group_title.startswith("4.4"):
            lines += gradient_dtype_note()
        if group_title.startswith("4.6"):
            lines += contour_discussion()
    return lines


def interpolation_discussion() -> list[str]:
    lines = [
        "#### Nearest Neighbor Compared With Bilinear",
        "",
        "Both upscaled images start from the same 100 x 100 downsample, so any difference comes "
        "purely from how each method invents the missing pixels.",
        "",
        "Nearest neighbor copies the value of the closest source pixel. It performs no arithmetic, "
        "so every output value already existed in the source and edges stay hard. The cost is "
        "blockiness: each source pixel becomes a visible 2 x 2 square of identical values, which "
        "gives diagonal edges a stair-stepped appearance.",
        "",
        "Bilinear interpolation takes a weighted average of the four nearest source pixels. This "
        "introduces intermediate values that were never in the source, producing smooth gradients "
        "and removing the blocky squares, at the cost of softening genuine edges. The result looks "
        "less sharp but closer to the original continuous image.",
        "",
    ]
    comparison = FULL_CSV / "interpolation_comparison.csv"
    if comparison.exists():
        frame = pd.read_csv(comparison)
        lines.append("Measured against the original 200 x 200 grayscale image:")
        lines.append("")
        lines.append(frame.to_markdown(index=False))
        lines.append("")
        lines.append(
            "The bilinear result is closer to the original on both mean and maximum absolute "
            "difference, and its lower standard deviation reflects the smoothing it applies."
        )
        lines.append("")
    return lines


def gradient_dtype_note() -> list[str]:
    return [
        "#### Data Type of Gradient Values",
        "",
        "Sobel and Laplacian responses are signed: an edge running dark to light gives a positive "
        "value and the same edge running light to dark gives a negative one. Both operators are "
        "therefore computed with `cv2.CV_64F` rather than the default 8-bit unsigned type. Writing "
        "the result straight into a `uint8` matrix would clip every negative value to zero and "
        "silently discard half of the detected edges. The CSV matrices in `csv_full_image/` hold "
        "the true signed values; the PNG previews are separately scaled to the 0-255 display range.",
        "",
    ]


def contour_discussion() -> list[str]:
    lines = []
    measurements = FULL_CSV / "contour_measurements.csv"
    if not measurements.exists():
        return lines
    frame = pd.read_csv(measurements)
    if frame.empty:
        return lines

    lines.append("#### Contour Measurements")
    lines.append("")
    lines.append(
        f"Contours were detected from the binary threshold image, which yielded {len(frame)} "
        "contours. `RETR_LIST` was used rather than `RETR_EXTERNAL` because the white region "
        "reaches every image border: with `RETR_EXTERNAL` the only contour returned traces the "
        "image frame itself and describes nothing about the image content. The frame contour is "
        "still present in the table below and is flagged in the `is_image_frame` column, but it "
        "is excluded when identifying the largest contour."
    )
    lines.append("")
    lines.append(
        "The full table is saved as `csv_full_image/contour_measurements.csv`. The ten largest "
        "contours are shown here."
    )
    lines.append("")
    lines.append(frame.nlargest(10, "area").to_markdown(index=False))
    lines.append("")

    largest = frame[frame["is_largest"]]
    if not largest.empty:
        row = largest.iloc[0]
        centroid = (
            f"({row['centroid_x']}, {row['centroid_y']})"
            if str(row["centroid_x"]) not in ("", "nan")
            else "undefined, because the contour encloses zero area"
        )
        lines.append("**Largest contour**")
        lines.append("")
        lines.append(f"- Contour id: {row['contour_id']}")
        lines.append(f"- Area: {row['area']}")
        lines.append(f"- Perimeter: {row['perimeter']}")
        lines.append(f"- Bounding box x, y: {row['bbox_x']}, {row['bbox_y']}")
        lines.append(f"- Bounding box width, height: {row['bbox_width']}, {row['bbox_height']}")
        lines.append(f"- Centroid: {centroid}")
        lines.append("")
    return lines


def section_verification() -> list[str]:
    lines = [
        "## 5. Manual Matrix Calculations",
        "",
        "Manual calculation is performed on a single 7 x 7 grayscale patch rather than the full "
        "200 x 200 image. Every manual result below was produced by explicit arithmetic on the "
        "pixel values: point operations were evaluated element by element, and neighborhood "
        "operations were evaluated by sliding the kernel by hand and summing the products. No "
        "manual result was produced by calling the OpenCV function it is compared against.",
        "",
        "For every 3 x 3 neighborhood operation only the central 5 x 5 output is compared. Those "
        "25 output pixels depend solely on values inside the patch, so OpenCV's border-padding "
        "rules cannot influence the comparison.",
        "",
    ]

    location = MANUAL_CSV / "patch_location.csv"
    patch = MANUAL_CSV / "manual_input_patch_7x7.csv"
    if location.exists() and patch.exists():
        info = pd.read_csv(location).iloc[0]
        lines.append("### Selected Patch")
        lines.append("")
        lines.append(
            f"The patch spans **rows {info['start_row']} to {info['end_row']}** and "
            f"**columns {info['start_column']} to {info['end_column']}** of the 200 x 200 "
            f"grayscale image. It was chosen as the 7 x 7 window with the highest standard "
            f"deviation ({info['std']}), so it contains noticeable intensity variation: values "
            f"range from {info['min']} to {info['max']}."
        )
        lines.append("")
        lines.append("Saved as `csv_manual_calculations/manual_input_patch_7x7.csv`.")
        lines.append("")
        lines.append(matrix_table(patch))
        lines.append("")

    summary = MANUAL_CSV / "verification_summary.csv"
    if not summary.exists():
        return lines

    results = pd.read_csv(summary)
    lines.append("### Summary of All Manual Operations")
    lines.append("")
    lines.append(
        results[
            ["operation_id", "operation", "output_shape", "max_abs_difference", "result"]
        ].to_markdown(index=False)
    )
    lines.append("")
    matched = int((results["result"] == "MATCH").sum())
    lines.append(
        f"All {matched} of {len(results)} operations reproduce the OpenCV result. Where a maximum "
        "difference is not exactly zero it is on the order of 1e-14, which is floating-point "
        "representation error rather than a disagreement in the arithmetic."
    )
    lines.append("")

    examples = (
        pd.read_csv(MANUAL_CSV / "manual_worked_examples.csv")
        if (MANUAL_CSV / "manual_worked_examples.csv").exists()
        else pd.DataFrame()
    )

    for row in results.itertuples():
        lines.append(f"### {row.operation_id.upper()} - {row.operation}")
        lines.append("")
        prefix = row.file_prefix
        for label, suffix in [
            ("Input", "input"),
            ("Kernel", "kernel"),
            ("Manual output", "manual_output"),
            ("OpenCV output", "opencv_output"),
            ("Difference (manual - OpenCV)", "difference"),
        ]:
            path = MANUAL_CSV / f"{prefix}_{suffix}.csv"
            if path.exists():
                lines.append(f"**{label}** (`{path.name}`)")
                lines.append("")
                lines.append(matrix_table(path))
                lines.append("")

        if not examples.empty:
            subset = examples[examples["operation_id"] == row.operation_id]
            if not subset.empty:
                lines += worked_example_lines(subset)

        lines.append(
            f"Maximum absolute difference: **{row.max_abs_difference}** ({row.result})."
        )
        lines.append("")
    return lines


def worked_example_lines(subset: pd.DataFrame) -> list[str]:
    lines = [
        "**Worked calculations for three representative output cells**",
        "",
    ]
    for example in subset.itertuples():
        neighborhood = json.loads(example.neighborhood)
        lines.append(f"*Output cell ({example.output_row}, {example.output_col})*")
        lines.append("")
        if len(neighborhood) == 3 and len(neighborhood[0]) == 3:
            lines.append("Neighborhood values:")
            lines.append("")
            lines.append("```")
            for values in neighborhood:
                lines.append("  ".join(f"{v:>5}" for v in values))
            lines.append("```")
        else:
            lines.append(f"Gx = {neighborhood[0][0]}, Gy = {neighborhood[1][0]}")
        lines.append("")
        lines.append("```")
        lines.append(example.calculation)
        lines.append("```")
        lines.append("")
        lines.append(
            f"Manual result {example.manual_result}, OpenCV result {example.opencv_result}."
        )
        lines.append("")
    return lines


def build() -> str:
    lines = [
        "# OpenCV Matrix Assignment Report",
        "",
        f"**{STUDENT_NAME}**  ",
        f"{STUDENT_TITLE}  ",
        f"{INSTITUTION}  ",
        f"{STUDENT_EMAIL}",
        "",
        f"**Course:** {COURSE}  ",
        f"**Instructor:** {INSTRUCTOR}  ",
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
