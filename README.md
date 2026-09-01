# Collins_Samuel_OpenCV_Matrix_Assignment

Assignment 1 — CCIS 727, Introduction to Computer Vision
Clark Atlanta University · Instructor: Dr. Kishor Gupta
Samuel Collins, Ph.D. Student, Department of Cyber-Physical Systems

## Assignment Objective

The purpose of this assignment is to demonstrate that a digital image is a numerical matrix, not
only a visual object. An image is captured using a mobile phone, converted into a 200 × 200 image,
its pixel values are exported into CSV matrix files, important image-processing operations are
applied using OpenCV, and selected operations are verified through manual matrix calculations.

## Repository Structure

```
Collins_Samuel_OpenCV_Matrix_Assignment/
├── README.md
├── requirements.txt
├── report/                     Generated Markdown report and final PDF
├── src/                        Pipeline scripts
├── input/                      Original photo and prepared 200x200 image
├── output_images/              Rendered results of each OpenCV operation
├── csv_full_image/             Full 200x200 pixel matrices and measurements
└── csv_manual_calculations/    7x7 patch: manual vs. OpenCV comparisons
```

## Setup

```zsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Place the photo taken with your mobile phone at `input/image_original.jpg`, then run the full
pipeline:

```zsh
python src/run_all.py
```

This regenerates every image, CSV matrix, and the report. Individual stages can also be run on
their own:

| Script | Purpose |
| --- | --- |
| `src/prepare_image.py` | Resizes the original photo to 200 × 200 and records image metadata |
| `src/opencv_operations.py` | Applies the OpenCV operations and exports images and pixel matrices |
| `src/verify_matrices.py` | Compares manual calculations against OpenCV on a 7 × 7 patch |
| `src/generate_report.py` | Builds `report/OpenCV_Matrix_Assignment_Report.md` from the outputs |
| `src/build_report_pdf.py` | Converts the Markdown report to PDF using headless Chrome |

## Operations Performed

| Operation | Description |
| --- | --- |
| Grayscale | Converts the three BGR channels into a single intensity channel |
| Negative | Inverts every intensity value as `255 - pixel` |
| Threshold | Maps intensities to 0 or 255 using a fixed cutoff of 127 |
| Gaussian blur | Smooths the image by convolving with a 5 × 5 Gaussian kernel |
| Canny | Detects edges using gradient thresholds of 100 and 200 |

## Report

The final deliverable is `report/OpenCV_Matrix_Assignment_Report.pdf`, generated from
`report/OpenCV_Matrix_Assignment_Report.md`. The report is built from the actual pipeline outputs,
so rerunning the pipeline keeps it current.
