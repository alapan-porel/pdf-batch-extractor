"""
Unified CLI Entry Point for PyMuPDF Batch Extractor
"""

import argparse
import sys
from pathlib import Path
from src.pdf_text_extractor import extract_text_from_pdf
from src.pdf_batch_processing import process_batch
from src.semantic_chunker import SemanticChunker

def main():
    parser = argparse.ArgumentParser(description="PyMuPDF High-Throughput PDF Text Extractor & Semantic Chunker")
    parser.add_argument("path", help="PDF file or directory to process")
    parser.add_argument("--output", "-o", default="output", help="Output directory")
    parser.add_argument("--workers", "-w", type=int, default=4, help="Worker pool size")
    parser.add_argument("--chunk", action="store_true", help="Apply semantic chunking to extracted text")

    args = parser.parse_args()
    target = Path(args.path)

    if not target.exists():
        print(f"Error: Path {target} does not exist.")
        sys.exit(1)

    if target.is_file():
        text = extract_text_from_pdf(target)
        out_file = Path(args.output) / (target.stem + ".txt")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(text, encoding="utf-8")
        print(f"Successfully extracted {target.name} -> {out_file}")
    else:
        process_batch(target, Path(args.output), max_workers=args.workers)

if __name__ == "__main__":
    main()
