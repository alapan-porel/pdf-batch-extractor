"""
PDF Scraper - Main driver for PDF text extraction.

Provides a unified interface for:
- Single file extraction (with page selection)
- Batch directory processing

Usage:
    python pdf_scraper.py
"""

import sys
from pathlib import Path

try:
    from pdf_text_extractor import (
        extract_text_to_file,
        extract_text_from_pdf,
        extract_text_with_metadata,
        parse_page_range
    )
except ImportError:
    print("Error: pdf_text_extractor.py not found in the same directory.")
    sys.exit(1)

try:
    from pdf_batch_processing import process_batch, get_pdf_files
except ImportError:
    print("Error: pdf_batch_processing.py not found in the same directory.")
    sys.exit(1)

try:
    import fitz  # PyMuPDF
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


def get_menu_choice() -> int:
    """Display main menu and get user choice."""
    print()
    print("What would you like to do?")
    print("  1. Extract text from a single PDF file")
    print("  2. Batch process all PDFs in a directory")
    print("  3. Exit")
    print()
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Invalid choice. Please enter 1, 2, or 3.")


def process_single_file():
    """Handle single file extraction with interactive input."""
    print()
    print("-" * 60)
    print("  Single File Extraction")
    print("-" * 60)
    print()
    
    # Get PDF file path
    while True:
        pdf_file = input("Enter the path to the PDF file: ").strip()
        pdf_file = pdf_file.strip('"').strip("'")
        
        if not pdf_file:
            print("Error: Please enter a file path.")
            continue
        
        pdf_path = Path(pdf_file)
        
        if not pdf_path.exists():
            print(f"Error: File not found: {pdf_path}")
            continue
        
        if pdf_path.suffix.lower() != '.pdf':
            print(f"Error: File is not a PDF: {pdf_path}")
            continue
        
        break
    
    # Open PDF to get page count
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    print(f"\nPDF loaded successfully!")
    print(f"Total pages: {total_pages}")
    print()
    
    # Get output file path
    output_file = input("Enter output file path or directory (press Enter to print to screen): ").strip()
    output_file = output_file.strip('"').strip("'")
    
    output_path = None
    if output_file:
        output_path = Path(output_file)
        # If output path is a directory, create txt file with same name as PDF
        if output_path.is_dir():
            output_path = output_path / (pdf_path.stem + ".txt")
            print(f"Output file: {output_path}")
        elif output_path.exists() and output_path.is_dir():
            output_path = output_path / (pdf_path.stem + ".txt")
            print(f"Output file: {output_path}")
    
    # Get page range
    print(f"\nPage range options:")
    print(f"  - Press Enter to extract all pages (1-{total_pages})")
    print(f"  - Enter specific pages like: 1-5 or 1,3,5,7-10")
    page_range = input("Enter page range: ").strip()
    
    pages = None
    if page_range:
        try:
            pages = parse_page_range(page_range, total_pages)
            print(f"Will extract {len(pages)} page(s)")
        except Exception:
            print("Invalid page range format. Extracting all pages.")
            pages = None
    
    # Get options
    print()
    preserve_layout = get_yes_no_input("Preserve layout/whitespace?", default=False)
    include_metadata = get_yes_no_input("Include PDF metadata?", default=False)
    
    print()
    print("-" * 60)
    print("Starting extraction...")
    print("-" * 60)
    
    # Perform extraction
    if output_path:
        # Memory-efficient streaming extraction to file
        pages_processed = extract_text_to_file(
            pdf_path,
            output_path,
            pages=pages,
            preserve_layout=preserve_layout,
            include_metadata=include_metadata
        )
        print(f"\nText extracted successfully to: {output_path}")
        print(f"Pages processed: {pages_processed}")
    else:
        # Output to stdout
        if include_metadata:
            result = extract_text_with_metadata(pdf_path)
            metadata = result['metadata'] or {}
            
            output_lines = [
                "=== PDF Metadata ===",
                f"Title: {metadata.get('title', 'N/A')}",
                f"Author: {metadata.get('author', 'N/A')}",
                f"Subject: {metadata.get('subject', 'N/A')}",
                f"Creator: {metadata.get('creator', 'N/A')}",
                f"Producer: {metadata.get('producer', 'N/A')}",
                f"Page Count: {result['page_count']}",
                "",
                "=== Extracted Text ===",
                result['text']
            ]
            text = "\n".join(output_lines)
        else:
            text = extract_text_from_pdf(
                pdf_path,
                pages=pages,
                preserve_layout=preserve_layout
            )
        print()
        print(text)


def process_directory():
    """Handle batch directory processing with interactive input."""
    print()
    print("-" * 60)
    print("  Batch Directory Processing")
    print("-" * 60)
    print()
    
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


def main():
    """Main entry point - driver for the PDF scraper project."""
    print("=" * 60)
    print("              PDF SCRAPER")
    print("       Extract text from PDF files")
    print("=" * 60)
    
    try:
        while True:
            choice = get_menu_choice()
            
            if choice == 1:
                process_single_file()
            elif choice == 2:
                process_directory()
            elif choice == 3:
                print("\nGoodbye!")
                break
            
            print()
            if not get_yes_no_input("Would you like to perform another operation?", default=True):
                print("\nGoodbye!")
                break
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
