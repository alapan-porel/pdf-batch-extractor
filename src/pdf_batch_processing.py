"""
PDF Batch Processing - Convert all PDFs in a directory to text files.

Uses the pdf_text_extractor module for extraction.

Usage:
    python pdf_batch_processing.py
"""

import sys
from pathlib import Path

try:
    from pdf_text_extractor import extract_text_to_file, parse_page_range
except ImportError:
    print("Error: pdf_text_extractor.py not found in the same directory.")
    sys.exit(1)

try:
    import fitz  # PyMuPDF - needed to get page count
except ImportError:
    print("Error: PyMuPDF is not installed. Install it with: pip install pymupdf")
    sys.exit(1)


def get_yes_no_input(prompt: str, default: bool = False) -> bool:
    """Get a yes/no input from the user."""
    default_str = "Y/n" if default else "y/N"
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if response == "":
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'")


def get_pdf_files(directory: Path) -> list[Path]:
    """Get all PDF files in a directory."""
    return sorted(directory.glob("*.pdf"))


def process_batch(
    input_dir: Path,
    output_dir: Path,
    preserve_layout: bool = False,
    include_metadata: bool = False
) -> tuple[int, int, list[tuple[str, str]]]:
    """
    Process all PDF files in a directory.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save text files
        preserve_layout: Whether to preserve layout in extracted text
        include_metadata: Whether to include PDF metadata
        
    Returns:
        Tuple of (successful_count, failed_count, list of (filename, error) for failures)
    """
    pdf_files = get_pdf_files(input_dir)
    
    if not pdf_files:
        print(f"No PDF files found in: {input_dir}")
        return 0, 0, []
    
    successful = 0
    failed = 0
    errors: list[tuple[str, str]] = []
    
    total = len(pdf_files)
    print(f"\nFound {total} PDF file(s) to process.\n")
    
    for i, pdf_path in enumerate(pdf_files, 1):
        # Create output filename (same name but .txt extension)
        output_filename = pdf_path.stem + ".txt"
        output_path = output_dir / output_filename
        
        print(f"[{i}/{total}] Processing: {pdf_path.name}")
        
        try:
            pages_processed = extract_text_to_file(
                pdf_path,
                output_path,
                pages=None,  # Extract all pages
                preserve_layout=preserve_layout,
                include_metadata=include_metadata
            )
            print(f"         -> {output_filename} ({pages_processed} pages)")
            successful += 1
            
        except Exception as e:
            error_msg = str(e)
            print(f"         -> FAILED: {error_msg}")
            errors.append((pdf_path.name, error_msg))
            failed += 1
    
    return successful, failed, errors


def main():
    """Main entry point - interactive batch processing."""
    print("=" * 60)
    print("       PDF Batch Processor")
    print("       Convert all PDFs in a directory to text files")
    print("=" * 60)
    print()
    
    try:
        # Get input directory
        while True:
            input_dir_str = input("Enter the input directory containing PDF files: ").strip()
            input_dir_str = input_dir_str.strip('"').strip("'")
            
            if not input_dir_str:
                print("Error: Please enter a directory path.")
                continue
            
            input_dir = Path(input_dir_str)
            
            if not input_dir.exists():
                print(f"Error: Directory not found: {input_dir}")
                continue
            
            if not input_dir.is_dir():
                print(f"Error: Path is not a directory: {input_dir}")
                continue
            
            # Check if there are any PDF files
            pdf_count = len(get_pdf_files(input_dir))
            if pdf_count == 0:
                print(f"Warning: No PDF files found in: {input_dir}")
                if not get_yes_no_input("Continue anyway?", default=False):
                    continue
            else:
                print(f"Found {pdf_count} PDF file(s)")
            
            break
        
        print()
        
        # Get output directory
        while True:
            output_dir_str = input("Enter the output directory for text files: ").strip()
            output_dir_str = output_dir_str.strip('"').strip("'")
            
            if not output_dir_str:
                print("Error: Please enter a directory path.")
                continue
            
            output_dir = Path(output_dir_str)
            
            # Create directory if it doesn't exist
            if not output_dir.exists():
                print(f"Directory does not exist: {output_dir}")
                if get_yes_no_input("Create it?", default=True):
                    try:
                        output_dir.mkdir(parents=True, exist_ok=True)
                        print(f"Created directory: {output_dir}")
                    except Exception as e:
                        print(f"Error creating directory: {e}")
                        continue
                else:
                    continue
            elif not output_dir.is_dir():
                print(f"Error: Path is not a directory: {output_dir}")
                continue
            
            break
        
        print()
        
        # Get options
        preserve_layout = get_yes_no_input("Preserve layout/whitespace?", default=False)
        include_metadata = get_yes_no_input("Include PDF metadata in each file?", default=False)
        
        print()
        print("-" * 60)
        print("Starting batch processing...")
        print("-" * 60)
        
        # Process all PDFs
        successful, failed, errors = process_batch(
            input_dir,
            output_dir,
            preserve_layout=preserve_layout,
            include_metadata=include_metadata
        )
        
        # Print summary
        print()
        print("=" * 60)
        print("                    SUMMARY")
        print("=" * 60)
        print(f"  Input directory:  {input_dir}")
        print(f"  Output directory: {output_dir}")
        print(f"  Successful:       {successful}")
        print(f"  Failed:           {failed}")
        print("=" * 60)
        
        if errors:
            print("\nFailed files:")
            for filename, error in errors:
                print(f"  - {filename}: {error}")
        
        if successful > 0:
            print(f"\nText files saved to: {output_dir}")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
