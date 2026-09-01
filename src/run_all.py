"""Run the full assignment pipeline: prepare, process, verify, and build the report."""

import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
STEPS = [
    "prepare_image.py",
    "opencv_operations.py",
    "manual_calculations.py",
    "verify_matrices.py",
    "generate_report.py",
    "build_report_pdf.py",
]


def main() -> None:
    for step in STEPS:
        print(f"\n=== {step} ===")
        result = subprocess.run([sys.executable, str(SRC / step)])
        if result.returncode != 0:
            sys.exit(f"{step} failed with exit code {result.returncode}")
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
