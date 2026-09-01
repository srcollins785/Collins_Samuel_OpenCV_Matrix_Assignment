# Collins_Samuel_OpenCV_Matrix_Assignment

Assignment 1 — CCIS 727, Introduction to Computer Vision
Clark Atlanta University · Instructor: Dr. Kishor Gupta
Samuel Collins, Ph.D. Student, Department of Cyber-Physical Systems
`samuel.collins@students.cau.edu`

## Full Technical Report

> **The complete technical report is [report/OpenCV_Matrix_Assignment_Report.md](report/OpenCV_Matrix_Assignment_Report.md)**
> — readable directly in the browser, no download required.
> A PDF export is also provided at [report/OpenCV_Matrix_Assignment_Report.pdf](report/OpenCV_Matrix_Assignment_Report.pdf).

The report contains, for **every** operation, the input and output images, the OpenCV function and
its parameters, the output matrix dimensions, and an interpretation of the result. For every manual
operation it contains the input patch, the kernel or formula, three fully substituted numerical
calculations, and the manual, OpenCV, and difference matrices. This README summarizes that material;
the report is the authoritative source.

| Report section | Contents |
| --- | --- |
| [1. Objective](report/OpenCV_Matrix_Assignment_Report.md#1-objective) | Purpose of the assignment |
| [2. Image Acquisition and Preparation](report/OpenCV_Matrix_Assignment_Report.md#2-image-acquisition-and-preparation) | The three source images, properties, BGR ordering |
| [3. The Image as a Numerical Matrix](report/OpenCV_Matrix_Assignment_Report.md#3-the-image-as-a-numerical-matrix) | Channel matrices and grayscale derivation |
| [4. OpenCV Operations](report/OpenCV_Matrix_Assignment_Report.md#4-opencv-operations) | All Part B operations, 4.1 through 4.6 |
| [5. Manual Matrix Calculations](report/OpenCV_Matrix_Assignment_Report.md#5-manual-matrix-calculations) | All 14 manual operations with worked arithmetic |
| [6. Discussion](report/OpenCV_Matrix_Assignment_Report.md#6-discussion) | Required comparison and analysis topics |
| [7. What I Learned](report/OpenCV_Matrix_Assignment_Report.md#7-what-i-learned) | Summary of findings |

## Project Purpose

This project demonstrates that a digital image is a numerical matrix, not only a visual object.
A photograph captured with a mobile phone is converted into a 200 × 200 image, its pixel values are
exported into CSV matrix files, a set of image-processing operations is applied with OpenCV, and
fourteen of those operations are then reproduced independently and verified against the OpenCV
results cell by cell.

### The Image at Three Stages

| Original mobile-camera photograph | Cropped square image | Final 200 × 200 image |
| :---: | :---: | :---: |
| ![Original photograph](input/image_original_not_cropped.jpg) | ![Cropped square](input/image_original.jpg) | ![Final working image](input/image_200x200.png) |
| 2316 × 3088 | 2316 × 2316 | 200 × 200 |

### Representative Results

| Grayscale | Negative | Threshold | Histogram equalized |
| :---: | :---: | :---: | :---: |
| ![Grayscale](output_images/grayscale.png) | ![Negative](output_images/negative.png) | ![Threshold](output_images/threshold.png) | ![Equalized](output_images/histogram_equalized.png) |

| Mean 3×3 | Gaussian 3×3 | Median 3×3 | Canny |
| :---: | :---: | :---: | :---: |
| ![Mean](output_images/filter_mean_3x3.png) | ![Gaussian](output_images/filter_gaussian_3x3.png) | ![Median](output_images/filter_median_3x3.png) | ![Canny](output_images/canny.png) |

| Sobel Gx | Sobel Gy | Gradient magnitude | Laplacian |
| :---: | :---: | :---: | :---: |
| ![Sobel Gx](output_images/sobel_x.png) | ![Sobel Gy](output_images/sobel_y.png) | ![Magnitude](output_images/sobel_magnitude.png) | ![Laplacian](output_images/laplacian.png) |

| Erosion | Dilation | Contour mask | Contours drawn |
| :---: | :---: | :---: | :---: |
| ![Erosion](output_images/morph_erosion.png) | ![Dilation](output_images/morph_dilation.png) | ![Contour mask](output_images/contour_mask.png) | ![Contours](output_images/contours_drawn.png) |

Every operation's image, matrix, and interpretation appears in
[section 4 of the report](report/OpenCV_Matrix_Assignment_Report.md#4-opencv-operations).

## Requirements

- **Python 3.10 or newer** (developed and tested on Python 3.14.3)
- Packages, listed in [requirements.txt](requirements.txt):

| Package | Purpose |
| --- | --- |
| `opencv-python` | All image-processing operations |
| `numpy` | Matrix arithmetic for the manual calculations |
| `pandas` | Reading and writing CSV matrices |
| `matplotlib` | Histogram plots |
| `markdown` | Markdown to HTML conversion for the report |
| `tabulate` | Markdown table rendering |

A Chromium-based browser (Google Chrome, Microsoft Edge, or Chromium) is required only for the
final PDF export step.

## Installation

```zsh
git clone https://github.com/srcollins785/Collins_Samuel_OpenCV_Matrix_Assignment.git
cd Collins_Samuel_OpenCV_Matrix_Assignment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execution Sequence

Place a square photograph at `input/image_original.jpg`, then run the whole pipeline:

```zsh
python src/run_all.py
```

`run_all.py` executes the six stages below in order. Each can also be run on its own, provided the
stages before it have run at least once.

| Order | Script | Purpose |
| --- | --- | --- |
| 1 | `src/prepare_image.py` | Validates the photo is square and resizes it to 200 × 200 |
| 2 | `src/opencv_operations.py` | Applies every Part B operation, exporting PNGs and CSV matrices |
| 3 | `src/manual_calculations.py` | Computes the fourteen manual operations on a 7 × 7 patch |
| 4 | `src/verify_matrices.py` | Compares manual against OpenCV matrices and reports statistics |
| 5 | `src/generate_report.py` | Builds the Markdown report from the outputs on disk |
| 6 | `src/build_report_pdf.py` | Converts the Markdown report to PDF |

All scripts resolve paths relative to the repository root, create their output folders when
missing, and fail with a clear message if an expected input is absent.

## Repository Structure

```
Collins_Samuel_OpenCV_Matrix_Assignment/
├── README.md
├── requirements.txt
├── report/
│   ├── OpenCV_Matrix_Assignment_Report.md
│   └── OpenCV_Matrix_Assignment_Report.pdf
├── src/
│   ├── prepare_image.py
│   ├── opencv_operations.py
│   ├── manual_calculations.py
│   ├── verify_matrices.py
│   ├── generate_report.py
│   ├── build_report_pdf.py
│   └── run_all.py
├── input/
│   ├── image_original_not_cropped.jpg
│   ├── image_original.jpg
│   └── image_200x200.png
├── output_images/
├── csv_full_image/
└── csv_manual_calculations/
```

### Output Folder Descriptions

| Folder | Contents |
| --- | --- |
| `report/` | The generated technical report in Markdown and its PDF export |
| `src/` | All Python source. Each stage is a separate module built from functions |
| `input/` | The original mobile-camera photograph, the square crop, and the prepared 200 × 200 working image |
| `output_images/` | One PNG per operation, plus the two histogram plots and the contour overlay |
| `csv_full_image/` | Full 200 × 200 pixel matrices for every channel and every operation, image metadata, histogram counts, interpolation comparison, and contour measurements |
| `csv_manual_calculations/` | The selected 7 × 7 patch and, for each manual operation, the input, kernel, manual output, OpenCV output, and difference matrices, plus worked examples and verification statistics |

## Source Image

| Stage | File | Size |
| --- | --- | --- |
| Original mobile-camera photograph | `input/image_original_not_cropped.jpg` | 2316 × 3088 (3:4) |
| Cropped square image | `input/image_original.jpg` | 2316 × 2316 (1:1) |
| Final working image | `input/image_200x200.png` | 200 × 200 (1:1) |

Cropping before resizing matters. The camera produces a 3:4 frame, and resizing that directly to a
square would compress the image vertically and distort every measurement taken from it.
`prepare_image.py` verifies its input is square and refuses to continue otherwise. The stage
dimensions are also recorded in `csv_full_image/source_image_stages.csv`.

Shape `(200, 200, 3)`, data type `uint8`, values 0–255.

### BGR and RGB Channel Ordering

`cv2.imread` returns a color image with channels in **BGR** order, not RGB. Index 0 of the third
axis is blue, index 1 is green, and index 2 is red, and `cv2.split` returns the channels in that
same B, G, R sequence. Most other libraries, including Matplotlib and PIL, assume RGB, so displaying
an OpenCV array directly without conversion swaps the red and blue channels. Every channel matrix
and every grayscale calculation in this project follows the BGR convention, and
`opencv_operations.py` verifies that `cv2.merge([B, G, R])` reproduces the original array exactly.

## CSV Matrix Representation

The four required channel matrices are written to `csv_full_image/` as 200 × 200 grids of integers
in the range 0–255, containing numerical values only with no row names, column headers, or
DataFrame index:

- `image_gray_200x200.csv`
- `image_blue_200x200.csv`
- `image_green_200x200.csv`
- `image_red_200x200.csv`

`image_metadata.csv` records the width, height, channel count, shape, data type, channel order, and
the minimum, maximum, mean, and standard deviation of both the color and grayscale images.

### Grayscale Conversion

```
I_gray = round(0.114 B + 0.587 G + 0.299 R)
```

The weights reflect human visual sensitivity — the eye is most sensitive to green, less to red, and
least to blue — and sum to 1.0 so the result stays within 0–255. Five pixels from different image
locations were converted by hand and matched OpenCV exactly; see
`csv_manual_calculations/grayscale_pixel_verification.csv`.

## OpenCV Operations

All operations run on the grayscale image unless noted. Every result is saved as a PNG in
`output_images/` and as a CSV matrix in `csv_full_image/`.

### Color and Intensity

| Operation | OpenCV function | Parameters | Output | Interpretation |
| --- | --- | --- | --- | --- |
| Grayscale | `cv2.cvtColor` | `COLOR_BGR2GRAY` | 200×200 | Collapses three channels into one intensity channel |
| Channel split | `cv2.split` | — | 3 × 200×200 | Isolates B, G, R; each is a full-range intensity map |
| Channel merge | `cv2.merge` | `[B, G, R]` | 200×200×3 | Reconstructs the original exactly, confirming BGR order |
| Negative | `cv2.bitwise_not` | — | 200×200 | `255 - I`; reversible, preserves all structure |
| Brightness | `cv2.add` | `+40` | 200×200 | Shifts values up; clipping at 255 loses highlight detail |
| Contrast | `cv2.convertScaleAbs` | `alpha=1.25` | 200×200 | Spreads values from the midpoint; bright areas saturate |
| Threshold | `cv2.threshold` | `127`, `THRESH_BINARY` | 200×200 | Reduces 256 levels to 2; the largest visual change |
| Equalization | `cv2.equalizeHist` | — | 200×200 | Linearizes the cumulative histogram, raising global contrast |
| Histograms | `cv2.calcHist` | 256 bins, range 0–256 | 256×1 | Show the redistribution equalization performs |

### Geometric

| Operation | OpenCV function | Parameters | Output | Interpretation |
| --- | --- | --- | --- | --- |
| Center crop | NumPy slice | rows/cols 50–149 | 100×100 | Pure indexing, no resampling |
| Flip horizontal | `cv2.flip` | `flipCode=1` | 200×200 | Reverses column order |
| Flip vertical | `cv2.flip` | `flipCode=0` | 200×200 | Reverses row order |
| Rotate 90° | `cv2.rotate` | `ROTATE_90_CLOCKWISE` | 200×200 | Index transposition, lossless |
| Rotate 30° | `cv2.warpAffine` | `getRotationMatrix2D(center, 30, 1.0)` | 200×200 | Requires interpolation; corners crop, empty areas fill black |
| Downsample | `cv2.resize` | `INTER_AREA` | 100×100 | Area averaging, appropriate for shrinking |
| Upscale nearest | `cv2.resize` | `INTER_NEAREST` | 200×200 | No new values; hard edges but blocky |
| Upscale bilinear | `cv2.resize` | `INTER_LINEAR` | 200×200 | Averages 4 neighbors; smooth but softer |

### Spatial Filtering

| Operation | OpenCV function | Kernel | Output | Interpretation |
| --- | --- | --- | --- | --- |
| Mean 3×3 | `cv2.filter2D` | `(1/9) × ones(3,3)` | 200×200 | Equal weights; blurs most aggressively |
| Gaussian 3×3 | `cv2.filter2D` | `(1/16) × [[1,2,1],[2,4,2],[1,2,1]]` | 200×200 | Center-weighted; smooths less, preserves edges better |
| Median 3×3 | `cv2.medianBlur` | 3×3 window | 200×200 | Rank filter, not a convolution; removes outliers, keeps edges |

### Edge Detection

All gradient operations use `cv2.CV_64F` so signed values survive.

| Operation | OpenCV function | Parameters | Output | Interpretation |
| --- | --- | --- | --- | --- |
| Sobel Gx | `cv2.Sobel` | `dx=1, dy=0, ksize=3` | 200×200 float | Responds to vertical edges; range −679 to 611 |
| Sobel Gy | `cv2.Sobel` | `dx=0, dy=1, ksize=3` | 200×200 float | Responds to horizontal edges; range −595 to 733 |
| Gradient magnitude | `np.sqrt` | `sqrt(Gx² + Gy²)` | 200×200 float | Orientation-independent edge strength |
| Laplacian | `cv2.Laplacian` | `CV_64F` | 200×200 float | Second derivative; sensitive but noisier |
| Canny | `cv2.Canny` | `100`, `200` | 200×200 binary | Full pipeline; thin, connected, binary edges |

### Morphological

Applied to the binary threshold image with a 3 × 3 kernel of ones.

| Operation | OpenCV function | Output | Interpretation |
| --- | --- | --- | --- |
| Erosion | `cv2.erode` | 200×200 | White only when all covered pixels are white; regions shrink |
| Dilation | `cv2.dilate` | 200×200 | White when any covered pixel is white; regions grow |
| Opening | `cv2.morphologyEx` `MORPH_OPEN` | 200×200 | Erode then dilate; removes small white specks |
| Closing | `cv2.morphologyEx` `MORPH_CLOSE` | 200×200 | Dilate then erode; fills small black holes |

### Contour Analysis

Detected from the binary image with `cv2.findContours` using `RETR_LIST` and `CHAIN_APPROX_SIMPLE`.
`RETR_EXTERNAL` was unusable here: the white region reaches all four image borders, so it returned a
single contour tracing the image frame. `RETR_LIST` recovers 30 contours including the subject.

The largest contour excluding the frame has area 15435.5, perimeter 505.0, bounding box (46, 9)
119 × 176, and centroid (103.6, 95.8). Full measurements are in
`csv_full_image/contour_measurements.csv`, and the filled mask is exported as a CSV matrix.

## Manual Calculations and Verification

Manual calculation uses one 7 × 7 grayscale patch spanning **rows 121–127, columns 53–59**, selected
automatically as the window with the highest standard deviation (83.87, values 18–213) so it
contains strong intensity variation. It is saved as
`csv_manual_calculations/manual_input_patch_7x7.csv`.

For 3 × 3 neighborhood operations only the central 5 × 5 output is compared, so OpenCV's
border-padding rules cannot influence the result.

### What "Manual" Means Here

*Manual* means each result is derived directly from the defining equation using ordinary
arithmetic — indexing, multiplication, addition, sorting, square roots — without calling the OpenCV
function being checked. Using the same library call for both sides would make the verification
circular. The report additionally shows three fully substituted numerical calculations per
neighborhood operation, which can be checked with a calculator.

All manual results are produced by [src/manual_calculations.py](src/manual_calculations.py):

| Operations | Function | What it does instead of calling OpenCV |
| --- | --- | --- |
| op01 grayscale | `grayscale_pixels()` | Multiplies the three BGR weights out directly instead of `cv2.cvtColor` |
| op02–op06 point operations | `main()` | NumPy element arithmetic and slicing instead of `cv2.bitwise_not`, `cv2.add`, `cv2.convertScaleAbs`, `cv2.threshold`, `cv2.flip` |
| op07, op08, op10, op11 kernel operations | `correlate_valid()` | Nested loops summing nine weighted products instead of `cv2.filter2D` or `cv2.Sobel` |
| op09, op13, op14 rank filters | `rank_valid()` | Sorts the nine neighborhood values and selects the middle, minimum, or maximum instead of `cv2.medianBlur`, `cv2.erode`, `cv2.dilate` |
| op12 gradient magnitude | `main()` | `sqrt(Gx² + Gy²)` applied to the manual Gx and Gy matrices |
| Worked examples | `add_examples()`, `add_magnitude_examples()` | Records the substituted values and arithmetic for three cells per operation |

Comparison is deliberately kept in a separate program,
[src/verify_matrices.py](src/verify_matrices.py), which reloads the saved matrices from disk rather
than recomputing anything.

The mean filter follows the required structure, with actual patch values substituted:

```
O(i,j) = [ I(i-1,j-1) + I(i-1,j) + I(i-1,j+1)
         + I(i,j-1)   + I(i,j)   + I(i,j+1)
         + I(i+1,j-1) + I(i+1,j) + I(i+1,j+1) ] / 9
```

Three fully substituted calculations are shown for every neighborhood operation in
[section 5 of the report](report/OpenCV_Matrix_Assignment_Report.md#5-manual-matrix-calculations),
which also prints the input patch, the kernel, and the manual, OpenCV, and difference matrices for
each of the fourteen operations. The same data is in
`csv_manual_calculations/manual_worked_examples.csv`.

### Verification Statistics

`src/verify_matrices.py` reloads the saved matrices, confirms dimensions match, computes
`D = I_OpenCV - I_manual`, saves each difference matrix, and reports statistics.

| Op | Operation | Shape | Max error | Mean error | Exact cells | Match % | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| op01 | Grayscale (5 pixels) | 5×1 | 0 | 0 | 5/5 | 100% | PASS |
| op02 | Negative | 7×7 | 0 | 0 | 49/49 | 100% | PASS |
| op03 | Brightness +40 | 7×7 | 0 | 0 | 49/49 | 100% | PASS |
| op04 | Contrast ×1.25 | 7×7 | 0 | 0 | 49/49 | 100% | PASS |
| op05 | Threshold >127 | 7×7 | 0 | 0 | 49/49 | 100% | PASS |
| op06 | Horizontal flip | 7×7 | 0 | 0 | 49/49 | 100% | PASS |
| op07 | Mean filter | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op08 | Gaussian filter | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op09 | Median filter | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op10 | Sobel Gx | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op11 | Sobel Gy | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op12 | Gradient magnitude | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op13 | Erosion | 5×5 | 0 | 0 | 25/25 | 100% | PASS |
| op14 | Dilation | 5×5 | 0 | 0 | 25/25 | 100% | PASS |

Tolerance is 0 for operations built from exact integer arithmetic and 1 intensity level for those
involving floating-point weights or rounding. **There are no nonzero differences to explain**: all
fourteen operations match OpenCV in 100 percent of cells.

The one subtlety worth recording is that when the mean filter is computed in memory, the largest
disagreement is roughly 3 × 10⁻¹⁴, because the weight 1/9 has no exact binary representation and the
manual loop accumulates its nine products in a different order than OpenCV. That residue is far
below one intensity level and disappears once matrices are written to CSV at four decimal places.

## Discussion

The [full discussion is in section 6 of the report](report/OpenCV_Matrix_Assignment_Report.md#6-discussion).
In brief:

- **Largest visual change:** binary thresholding, which discards 254 of 256 intensity levels.
- **Best noise reduction:** the median filter, because a rank filter discards outliers outright
  rather than averaging them into their neighbors.
- **Mean vs. Gaussian vs. median:** the first two are linear convolutions that can invent new
  values, differing only in weighting; the median is non-linear and edge-preserving.
- **Sobel vs. Laplacian vs. Canny:** first derivative and directional; second derivative and
  omnidirectional but noisier; and a complete pipeline yielding thin binary edges.
- **Erosion and dilation:** minimum and maximum over the neighborhood; duals rather than inverses,
  which is why opening and closing behave as they do.
- **Nearest vs. bilinear:** no new values and hard blocky edges, versus interpolated values and
  smooth but softer edges.
- **Rounding, clipping, data types, borders:** the four places where implementation reality departs
  from the mathematics, and the source of every discrepancy encountered during development.

## Notes on Reproducibility

Running `python src/run_all.py` regenerates every image, CSV, and the report from
`input/image_original.jpg` alone. No OpenCV-generated CSV is edited by hand at any point.
