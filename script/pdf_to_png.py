#!/usr/bin/env python3
"""Export PDF pages to PNG images."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_page_range(value: str, page_count: int) -> list[int]:
    """Parse a 1-based page range like '1,3-5' into 0-based page indexes."""
    pages: set[int] = set()

    for part in value.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            if start > end:
                raise ValueError(f"invalid page range: {part}")
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))

    if not pages:
        raise ValueError("page range is empty")

    invalid_pages = [page for page in pages if page < 1 or page > page_count]
    if invalid_pages:
        raise ValueError(
            f"page out of range: {invalid_pages[0]} (PDF has {page_count} pages)"
        )

    return [page - 1 for page in sorted(pages)]


def export_pdf_to_png(
    pdf_path: Path,
    output_dir: Path,
    dpi: int,
    pages_text: str | None,
    prefix: str | None,
) -> int:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency: PyMuPDF. Install it with: pip install pymupdf"
        ) from exc

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        raise ValueError(f"PDF path is not a file: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    name_prefix = prefix or pdf_path.stem

    with fitz.open(pdf_path) as document:
        if document.page_count == 0:
            raise ValueError("PDF has no pages")

        page_indexes = (
            parse_page_range(pages_text, document.page_count)
            if pages_text
            else list(range(document.page_count))
        )

        page_number_width = max(3, len(str(document.page_count)))
        for page_index in page_indexes:
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            output_path = output_dir / (
                f"{name_prefix}_p{page_index + 1:0{page_number_width}d}.png"
            )
            pixmap.save(output_path)
            print(output_path)

    return len(page_indexes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export PDF pages to PNG images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("pdf", type=Path, help="Input PDF file path")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to '<pdf_stem>_png' next to the PDF.",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI")
    parser.add_argument(
        "-p",
        "--pages",
        help="1-based pages to export, for example: '1', '1,3,5', or '2-4'",
    )
    parser.add_argument(
        "--prefix",
        help="Output filename prefix. Defaults to the input PDF filename stem.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.dpi <= 0:
        parser.error("--dpi must be greater than 0")

    pdf_path = args.pdf.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else pdf_path.with_name(f"{pdf_path.stem}_png")
    )

    try:
        count = export_pdf_to_png(
            pdf_path=pdf_path,
            output_dir=output_dir,
            dpi=args.dpi,
            pages_text=args.pages,
            prefix=args.prefix,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Exported {count} page(s) to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
