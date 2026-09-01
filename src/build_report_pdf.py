"""Convert the Markdown report to PDF by rendering it in headless Chrome."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "report"
REPORT_MD = REPORT_DIR / "OpenCV_Matrix_Assignment_Report.md"
REPORT_PDF = REPORT_DIR / "OpenCV_Matrix_Assignment_Report.pdf"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]

CSS = """
@page { size: Letter; margin: 0.75in; }
body { font-family: -apple-system, Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.45; }
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 6px; }
h2 { font-size: 14pt; margin-top: 24px; border-bottom: 1px solid #bbb; padding-bottom: 3px; }
h3 { font-size: 11.5pt; margin-top: 18px; }
table { border-collapse: collapse; font-size: 7.5pt; margin: 8px 0; }
th, td { border: 1px solid #999; padding: 2px 5px; text-align: right; }
th { background: #eee; }
img { max-width: 2.4in; border: 1px solid #ccc; }
code { background: #f2f2f2; padding: 1px 3px; font-size: 9pt; }
"""


def find_browser() -> str:
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    for name in ("google-chrome", "chromium", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError(
        "No Chrome/Chromium/Edge installation found. Install one, or export the report "
        "with the VS Code 'Markdown PDF' extension instead."
    )


def render_html() -> str:
    if not REPORT_MD.exists():
        raise FileNotFoundError(f"{REPORT_MD} missing. Run generate_report.py first.")
    body = markdown.markdown(
        REPORT_MD.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code"],
    )
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


def main() -> None:
    browser = find_browser()
    # Chrome must load the HTML from the report folder so the ../ image paths resolve.
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=REPORT_DIR, encoding="utf-8", delete=False) as handle:
        handle.write(render_html())
        html_path = Path(handle.name)
    try:
        subprocess.run(
            [
                browser,
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=10000",
                f"--print-to-pdf={REPORT_PDF}",
                html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    finally:
        html_path.unlink(missing_ok=True)
    print(f"Wrote {REPORT_PDF}")


if __name__ == "__main__":
    main()
