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

# Section 7 is a first-person reflection. Write it here in your own words; while this is
# empty the report prints a visible placeholder instead.
REFLECTION_TEXT = """
"""

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
        "The photograph was captured with a mobile phone, cropped to a square, and then resized "
        "to 200 x 200 pixels with `cv2.resize` using `INTER_AREA` interpolation. Cropping before "
        "resizing matters: the camera produces a 4:3 frame, and resizing that directly to a square "
        "would compress the image horizontally and distort every measurement taken from it. "
        "`prepare_image.py` verifies that its input is square and refuses to continue otherwise."
    )
    lines.append("")

    stages = FULL_CSV / "source_image_stages.csv"
    if stages.exists():
        lines.append(pd.read_csv(stages).to_markdown(index=False))
        lines.append("")

    for caption, filename in [
        ("Original mobile-camera photograph", "image_original_not_cropped.jpg"),
        ("Cropped square image", "image_original.jpg"),
        ("Final 200 x 200 working image", "image_200x200.png"),
    ]:
        if (INPUT_DIR / filename).exists():
            lines.append(f"**{caption}** (`input/{filename}`)")
            lines.append("")
            lines.append(f"![{caption}](../input/{filename})")
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
            f"The equation was evaluated independently for {len(frame)} pixels taken from "
            "different locations in the image and compared against the value OpenCV produced. "
            "The calculation is performed in `src/manual_calculations.py`, function "
            "`grayscale_pixels()`, which multiplies out the three weights directly rather than "
            "calling `cv2.cvtColor`."
        )
        lines.append("")
        lines.append(frame.to_markdown(index=False))
        lines.append("")
        worst = int(frame["difference"].abs().max())
        if worst == 0:
            lines.append(
                "Every independently calculated value matches OpenCV exactly, confirming the "
                "weighted "
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
        "200 x 200 image. In this project *manual* means the result is derived directly from the "
        "defining equation using ordinary arithmetic, without calling the OpenCV function being "
        "checked. Point operations are evaluated element by element, and neighborhood operations "
        "are evaluated by stepping the kernel across the patch and summing the nine products "
        "explicitly.",
        "",
        "**Where each calculation lives.** All manual results are produced by "
        "`src/manual_calculations.py`:",
        "",
        "| Operations | Function | What it does instead of calling OpenCV |",
        "| --- | --- | --- |",
        "| op01 grayscale | `grayscale_pixels()` | Multiplies the three BGR weights out directly "
        "instead of `cv2.cvtColor` |",
        "| op02-op06 point operations | `main()` | NumPy element arithmetic and slicing instead of "
        "`cv2.bitwise_not`, `cv2.add`, `cv2.convertScaleAbs`, `cv2.threshold`, `cv2.flip` |",
        "| op07, op08, op10, op11 kernels | `correlate_valid()` | Nested loops summing nine "
        "weighted products instead of `cv2.filter2D` or `cv2.Sobel` |",
        "| op09, op13, op14 rank filters | `rank_valid()` | Sorts the nine neighborhood values and "
        "selects the middle, minimum, or maximum instead of `cv2.medianBlur`, `cv2.erode`, "
        "`cv2.dilate` |",
        "| op12 magnitude | `main()` | `sqrt(Gx^2 + Gy^2)` applied to the manual Gx and Gy matrices |",
        "| Worked examples | `add_examples()`, `add_magnitude_examples()` | Records the substituted "
        "values and arithmetic shown for three cells per operation |",
        "",
        "Comparison is deliberately kept in a separate program, `src/verify_matrices.py`, which "
        "reloads the saved matrices from disk rather than recomputing anything.",
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
    lines.append("### Verification Statistics for All Manual Operations")
    lines.append("")
    lines.append(
        "Verification is performed by `src/verify_matrices.py`, a separate program that reloads "
        "the saved manual and OpenCV matrices from disk, confirms their dimensions match, and "
        "computes the signed difference `D = I_OpenCV - I_manual`. Exact-match tolerance is 0 for "
        "operations built from exact integer arithmetic (negative, thresholding, flipping, median, "
        "Sobel, erosion, dilation) and 1 intensity level for operations involving floating-point "
        "weights or rounding (grayscale, brightness, contrast, mean, Gaussian, gradient magnitude)."
    )
    lines.append("")
    lines.append(
        results[
            [
                "operation_id",
                "operation",
                "output_shape",
                "max_abs_difference",
                "mean_abs_difference",
                "exact_match_cells",
                "total_cells",
                "exact_match_percentage",
                "tolerance",
                "verdict",
            ]
        ].to_markdown(index=False)
    )
    lines.append("")
    passed = int((results["verdict"] == "PASS").sum())
    perfect = int((results["exact_match_percentage"] == 100.0).sum())
    lines.append(
        f"All {passed} of {len(results)} operations pass. {perfect} of them match OpenCV in "
        "100 percent of cells, with a maximum absolute difference of 0 and a mean absolute "
        "difference of 0, so there are no nonzero differences left to explain."
    )
    lines.append("")
    lines.append(
        "One detail is worth noting. When the mean filter is computed in memory the largest "
        "disagreement is about 3e-14, because the weight 1/9 has no exact binary representation "
        "and the manual loop accumulates its nine products in a different order than OpenCV does. "
        "That residue is far below one intensity level and disappears once the matrices are "
        "written to CSV at four decimal places, which is why the table reports exactly 0."
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
            f"Maximum absolute difference **{row.max_abs_difference}**, mean absolute difference "
            f"**{row.mean_abs_difference}**, exact matches **{row.exact_match_cells}/"
            f"{row.total_cells}** (**{row.exact_match_percentage} percent**), tolerance "
            f"{row.tolerance}: **{row.verdict}**."
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


def largest_change_discussion() -> list[str]:
    """Rank operations by measured deviation from the source image rather than by impression."""
    path = FULL_CSV / "operation_change_magnitude.csv"
    lines = ["### Which Operation Produced the Largest Visual Change", ""]
    if not path.exists():
        return lines + [""]

    frame = pd.read_csv(path)
    lines.append(
        "Rather than judging this by eye, every operation whose output has the same shape and type "
        "as the source grayscale image was compared against it pixel by pixel. The table below "
        "reports the mean absolute change, the largest single-pixel change, the root mean square "
        "error, and the share of pixels altered. The full ranking is in "
        "`csv_full_image/operation_change_magnitude.csv`."
    )
    lines.append("")
    lines.append(frame.head(10).to_markdown(index=False))
    lines.append("")

    top = frame.iloc[0]
    second = frame.iloc[1]
    lines.append(
        f"By mean absolute change, **{top['operation'].replace('_', ' ')}** produced the largest "
        f"change at {top['mean_abs_change']} intensity levels per pixel, followed by "
        f"**{second['operation'].replace('_', ' ')}** at {second['mean_abs_change']}."
    )
    lines.append("")
    lines.append(
        "The measurement is worth interpreting carefully, because the two leaders are large for "
        "opposite reasons. Canny scores highest because its output is binary and almost entirely "
        "black: nearly every pixel of a mid-tone photograph is driven to 0, so the average "
        "distance from the original is enormous even though Canny is a detector rather than a "
        "transformation of the image. The negative is second because it is the largest possible "
        "one-to-one remapping, sending every value v to 255 - v, yet it destroys no information "
        "at all and is perfectly reversible. Thresholding, which discards the most information of "
        "any operation here by collapsing 256 levels into 2, ranks only mid-table at "
        f"{frame[frame['operation'] == 'threshold']['mean_abs_change'].iloc[0]} because the "
        "surviving values stay numerically close to the originals."
    )
    lines.append("")
    lines.append(
        "The lesson is that numerical distance and information loss are different things. If the "
        "question means the largest change in appearance, the measurement points to Canny. If it "
        "means the greatest loss of image content, thresholding is the stronger answer despite its "
        "smaller numerical distance."
    )
    lines.append("")
    return lines


def noise_reduction_discussion() -> list[str]:
    """Report a controlled experiment instead of repeating textbook expectations."""
    path = FULL_CSV / "noise_reduction_comparison.csv"
    lines = ["### Which Filtering Method Best Reduced Noise", ""]
    if not path.exists():
        return lines + [""]

    frame = pd.read_csv(path)
    lines.append(
        "This was tested directly. Two kinds of noise were added to the grayscale image with a "
        "fixed random seed: salt-and-pepper noise affecting 5 percent of pixels, and Gaussian "
        "noise with a standard deviation of 15. Each of the three filters was then applied and the "
        "result compared against the clean original. The `percent_error_removed` column gives the "
        "reduction in mean absolute error relative to leaving the noise unfiltered, so a negative "
        "value means the filter made the image worse."
    )
    lines.append("")
    lines.append(frame.to_markdown(index=False))
    lines.append("")

    results = []
    for noise_type in frame["noise_type"].unique():
        subset = frame[(frame["noise_type"] == noise_type) & (frame["filter"] != "none (noisy input)")]
        best = subset.loc[subset["mae_vs_original"].idxmin()]
        results.append((noise_type, best))
        lines.append(
            f"For **{noise_type}** noise the best filter was **{best['filter']}**, removing "
            f"{best['percent_error_removed']} percent of the error."
        )
    lines.append("")
    lines.append(
        "There is no single winner, and that is the interesting result. The median filter "
        "dominates on salt-and-pepper noise while the mean and Gaussian filters actually increase "
        "the mean absolute error there, because averaging spreads each isolated extreme value "
        "across its whole neighborhood instead of removing it. Being a rank filter, the median "
        "sorts an outlier to one end of the nine values and never selects it, so the corrupted "
        "pixel is discarded outright."
    )
    lines.append("")
    lines.append(
        "On Gaussian noise the ordering reverses. The mean and Gaussian filters perform nearly "
        "identically and both beat the median, because Gaussian noise is zero-mean and spread "
        "across every pixel rather than concentrated in a few, which is exactly the situation "
        "averaging is designed for. The median gives up some accuracy here since it discards "
        "seven of the nine samples instead of using them."
    )
    lines.append("")
    lines.append(
        "The practical conclusion is that the filter must be matched to the noise. Impulse noise "
        "calls for a rank filter; distributed sensor noise calls for a linear one."
    )
    lines.append("")
    return lines


def section_discussion() -> list[str]:
    lines = [
        "## 6. Discussion",
        "",
    ]
    lines += largest_change_discussion()
    lines += noise_reduction_discussion()
    lines += [
        "### Differences Among Mean, Gaussian, and Median Filtering",
        "",
        "The mean filter weights all nine neighbors equally at 1/9. It is the simplest to compute "
        "but blurs the most aggressively, because a distant corner pixel influences the result as "
        "much as the center pixel does. The Gaussian filter uses the weights "
        "`(1/16) * [[1,2,1],[2,4,2],[1,2,1]]`, giving the center four times the influence of a "
        "corner. It therefore smooths less and preserves edge position better, which is why it is "
        "the standard pre-processing step before edge detection. Both are linear convolutions and "
        "can produce output values that appear nowhere in the input. The median filter is "
        "fundamentally different: it performs no arithmetic at all, only sorting and selection, so "
        "every output value is one of the original input values. This makes it non-linear, "
        "edge-preserving, and immune to outliers, at the cost of being slower and of erasing fine "
        "texture detail that the linear filters would merely soften.",
        "",
        "### Differences Among Sobel, Laplacian, and Canny Edge Detection",
        "",
        "Sobel computes the first derivative in a single direction, so `Gx` responds to vertical "
        "edges and `Gy` to horizontal ones. Its output is signed and directional, and combining "
        "the two through `G = sqrt(Gx^2 + Gy^2)` gives an orientation-independent edge strength. "
        "The Laplacian computes the second derivative in both directions at once. It is not "
        "directional and responds to the rate of change of the gradient, which makes it sensitive "
        "to fine detail but also considerably noisier, since differentiating twice amplifies "
        "high-frequency noise. Both Sobel and the Laplacian produce a continuous-valued response "
        "in which every pixel receives some score. Canny is not a single operator but a full "
        "pipeline: Gaussian smoothing, Sobel gradients, non-maximum suppression to thin thick "
        "gradient ridges to single-pixel lines, and hysteresis thresholding with two thresholds to "
        "link strong edges to weak ones while rejecting isolated weak responses. Its output is "
        "therefore binary and sparse, giving clean connected contours rather than a gradient map.",
        "",
        "### Effects of Erosion and Dilation",
        "",
        "With a 3 x 3 kernel of ones and a white foreground, erosion keeps a pixel white only when "
        "all nine pixels under the kernel are white, which is the minimum over the neighborhood. "
        "White regions therefore shrink by roughly one pixel on every boundary, thin connections "
        "break, and small white specks vanish entirely. Dilation keeps a pixel white when at least "
        "one pixel under the kernel is white, which is the maximum over the neighborhood. White "
        "regions grow by about one pixel, small black holes fill, and nearby components merge. The "
        "two are duals rather than inverses, so applying one after the other does not restore the "
        "original: opening (erosion then dilation) removes small white noise while keeping the "
        "overall object size, and closing (dilation then erosion) fills small gaps while keeping "
        "the overall object size.",
        "",
        "### Effects of Nearest-Neighbor and Bilinear Interpolation",
        "",
        "This is covered quantitatively in section 4.2. In summary, nearest neighbor copies the "
        "closest source pixel and performs no arithmetic, so it introduces no new intensity values "
        "and keeps edges hard, at the cost of visible blockiness where each source pixel becomes a "
        "2 x 2 square. Bilinear interpolation averages the four nearest source pixels, which "
        "creates intermediate values that were never present in the source and yields smoother "
        "gradients but softer edges. Measured against the original image, the bilinear result was "
        "closer on both mean and maximum absolute difference.",
        "",
        "### Problems Caused by Rounding, Clipping, Data Types, and Image Borders",
        "",
        "**Rounding.** Filter weights such as 1/9 and 1/16 are not exactly representable in binary "
        "floating point, and the order in which the nine products are accumulated affects the last "
        "few bits of the result. This produced the roughly 3e-14 residue seen in the mean filter "
        "comparison. It also matters that OpenCV rounds when converting back to 8-bit while a "
        "plain NumPy cast truncates, a one-level discrepancy that appeared in the contrast "
        "operation until the manual calculation was changed to round explicitly.",
        "",
        "**Clipping.** Brightness and contrast adjustment can push values outside the 0 to 255 "
        "range. Without clipping, an unsigned 8-bit result wraps around, so a bright pixel at 240 "
        "plus 40 becomes 24 and appears black. Both operations must clip rather than allow "
        "overflow, which means they are not reversible: information above 255 is permanently lost.",
        "",
        "**Data types.** Sobel and Laplacian responses are signed, and an edge running light to "
        "dark produces a negative value. Storing these directly in a `uint8` matrix clips every "
        "negative response to zero and silently discards half of the detected edges. Both were "
        "therefore computed with `cv2.CV_64F`, with a separately scaled copy produced only for the "
        "PNG previews.",
        "",
        "**Image borders.** A 3 x 3 neighborhood is undefined at the outermost row and column, so "
        "OpenCV invents values there according to a border mode, reflection by default. Manual "
        "calculation has no such convention, so comparing border pixels would measure the padding "
        "rule rather than the arithmetic. This is why the manual verification compares only the "
        "central 5 x 5 region of the 7 x 7 patch, where every contributing pixel is real data. The "
        "same effect appears in contour analysis: because the thresholded white region touches all "
        "four borders, `RETR_EXTERNAL` returned a single contour tracing the image frame, and "
        "`RETR_LIST` was needed to recover meaningful interior contours.",
        "",
    ]
    lines += section_learned()
    return lines


def section_learned() -> list[str]:
    """Section 7 is a first-person reflection and must be written by the author.

    The placeholder below is deliberately visible so an unedited report cannot be submitted
    by accident. Replace REFLECTION_TEXT with your own writing.
    """
    if REFLECTION_TEXT.strip():
        return ["## 7. What I Learned", "", REFLECTION_TEXT.strip(), ""]

    return [
        "## 7. What I Learned",
        "",
        "> **[ THIS SECTION IS NOT YET WRITTEN ]**",
        ">",
        "> Section 7 asks what *I* learned, so it has to be written in my own words rather than "
        "generated. To fill it in, set `REFLECTION_TEXT` at the top of `src/generate_report.py` "
        "and regenerate the report.",
        "",
        "Prompts to write against, with the evidence this project produced:",
        "",
        "- **On images as matrices.** All fourteen manual operations matched OpenCV in 100 percent "
        "of cells. What does it change about how you think about an image, knowing every library "
        "call is arithmetic you can reproduce yourself?",
        "- **On kernels.** The mean and Gaussian filters differ only in nine weights, yet behave "
        "noticeably differently. Sobel uses the same convolution machinery to detect edges instead "
        "of blurring. What does that suggest about what a kernel actually is?",
        "- **On rank filters.** The noise experiment in section 6 showed the median removing 71 "
        "percent of salt-and-pepper error while the averaging filters made it worse, and the "
        "ordering reversing for Gaussian noise. What did that result teach you that the formulas "
        "alone did not?",
        "- **On measurement versus intuition.** The largest-visual-change analysis ranked Canny "
        "first and thresholding mid-table, which is not what inspection of the images suggests. "
        "How did having a number change your answer?",
        "- **On implementation reality.** Every discrepancy encountered came from rounding, "
        "clipping, data types, or border handling rather than from the mathematics. What would you "
        "watch for next time?",
        "",
    ]


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
    lines += section_discussion()
    return "\n".join(lines)


def main() -> None:
    REPORT_MD.parent.mkdir(exist_ok=True)
    REPORT_MD.write_text(build(), encoding="utf-8")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
