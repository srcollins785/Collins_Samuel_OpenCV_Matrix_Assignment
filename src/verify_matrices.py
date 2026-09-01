"""Part D: verify manual matrices against OpenCV matrices.

This program reads the CSV files produced by manual_calculations.py rather than recomputing
anything. For each operation it loads the manual-output and OpenCV-output matrices, confirms
their dimensions match, computes the signed difference D = I_OpenCV - I_manual, saves that
difference as a CSV, and reports verification statistics.
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "csv_manual_calculations"
MANIFEST = CSV_DIR / "manual_operations_manifest.csv"

# Cells this close are treated as exactly matching despite binary floating-point storage.
FLOAT_EPSILON = 1e-9


def load_matrix(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(f"{path} missing. Run manual_calculations.py first.")
    return pd.read_csv(path, header=None).to_numpy(dtype=float)


def save_difference(difference: np.ndarray, name: str) -> None:
    pd.DataFrame(difference).round(4).to_csv(
        CSV_DIR / f"{name}.csv", index=False, header=False
    )


def compare(prefix: str, tolerance: int) -> dict:
    manual = load_matrix(CSV_DIR / f"{prefix}_manual_output.csv")
    opencv = load_matrix(CSV_DIR / f"{prefix}_opencv_output.csv")
    if manual.shape != opencv.shape:
        raise ValueError(
            f"{prefix}: dimension mismatch, manual is {manual.shape} but OpenCV is {opencv.shape}"
        )

    difference = opencv - manual
    magnitude = np.abs(difference)
    exact = int((magnitude <= FLOAT_EPSILON).sum())
    total = int(magnitude.size)
    max_error = float(magnitude.max())

    return {
        "rows": manual.shape[0],
        "columns": manual.shape[1],
        "dimensions_match": True,
        "max_abs_difference": round(max_error, 6),
        "mean_abs_difference": round(float(magnitude.mean()), 6),
        "exact_match_cells": exact,
        "total_cells": total,
        "exact_match_percentage": round(100.0 * exact / total, 4),
        "tolerance": tolerance,
        "within_tolerance": bool(max_error <= tolerance + FLOAT_EPSILON),
        "difference": difference,
    }


def main() -> None:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"{MANIFEST} missing. Run manual_calculations.py first.")
    operations = pd.read_csv(MANIFEST)

    results = []
    print(f"{'operation':<38}{'max':>8}{'mean':>9}{'exact':>10}{'match %':>10}  verdict")
    print("-" * 88)
    for operation in operations.itertuples():
        stats = compare(operation.file_prefix, int(operation.tolerance))
        difference = stats.pop("difference")
        for name in (operation.file_prefix, operation.operation_id):
            save_difference(difference, f"{name}_difference")

        verdict = "PASS" if stats["within_tolerance"] else "FAIL"
        results.append(
            {
                "operation_id": operation.operation_id,
                "operation": operation.operation,
                "file_prefix": operation.file_prefix,
                "output_shape": f"{stats['rows']}x{stats['columns']}",
                **{k: v for k, v in stats.items() if k not in ("rows", "columns")},
                "verdict": verdict,
            }
        )
        print(
            f"{operation.operation_id + ' ' + operation.operation:<38}"
            f"{stats['max_abs_difference']:>8.4g}{stats['mean_abs_difference']:>9.4g}"
            f"{stats['exact_match_cells']:>6}/{stats['total_cells']:<3}"
            f"{stats['exact_match_percentage']:>9.2f}%  {verdict}"
        )

    frame = pd.DataFrame(results)
    frame.to_csv(CSV_DIR / "verification_summary.csv", index=False)

    failures = frame[frame["verdict"] == "FAIL"]
    print("-" * 88)
    print(f"{len(frame)} operations verified, {len(failures)} outside tolerance")
    if not failures.empty:
        for row in failures.itertuples():
            print(f"  {row.operation_id}: max difference {row.max_abs_difference}")


if __name__ == "__main__":
    main()
