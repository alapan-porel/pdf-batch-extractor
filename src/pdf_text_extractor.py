"""
PDF Text Extractor - Robust PDF text extraction using PyMuPDF (fitz)

Usage:
    python pdf_text_extractor.py <pdf_file> [--output <output_file>] [--pages <page_range>]

Examples:
    python pdf_text_extractor.py document.pdf
    python pdf_text_extractor.py document.pdf --output extracted.txt
    python pdf_text_extractor.py document.pdf --pages 1-5
    python pdf_text_extractor.py document.pdf --pages 1,3,5,7-10
"""

import sys
from pathlib import Path
from typing import Optional, Union

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def parse_page_range(page_range: str, max_pages: int) -> list[int]:
    """
    Parse a page range string into a list of page numbers (0-indexed).
    
    Args:
        page_range: String like "1-5" or "1,3,5,7-10"
        max_pages: Maximum number of pages in the document
        
    Returns:
        List of 0-indexed page numbers
    """
    pages = set()
    parts = page_range.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            # Convert to 0-indexed and add range
            for p in range(max(1, start), min(end + 1, max_pages + 1)):
                pages.add(p - 1)  # Convert to 0-indexed
        else:
            page_num = int(part)
            if 1 <= page_num <= max_pages:
                pages.add(page_num - 1)  # Convert to 0-indexed
    
    return sorted(pages)


def extract_text_from_pdf(
    pdf_path: Union[str, Path],
    pages: Optional[list[int]] = None,
    preserve_layout: bool = False
) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        pages: Optional list of 0-indexed page numbers to extract.
               If None, extracts all pages.
        preserve_layout: If True, tries to preserve the visual layout
        
    Returns:
        Extracted text as a string
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        RuntimeError: If the PDF cannot be opened or processed
    """
    pdf_path_obj = Path(pdf_path)
    
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path_obj}")
    
    if pdf_path_obj.suffix.lower() != '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path_obj}")
    
    try:
        doc = fitz.open(pdf_path_obj)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")
    
    try:
        extracted_text = []
        total_pages = len(doc)
        
        # Determine which pages to process
        if pages is None:
            pages_to_process = range(total_pages)
        else:
            pages_to_process = [p for p in pages if 0 <= p < total_pages]
        
        for page_num in pages_to_process:
            page = doc.load_page(page_num)

            # Extract text with options
            if preserve_layout:
                # Use "text" with flags for better layout preservation
                text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            else:
                # Standard text extraction
                text = page.get_text("text")
            
            # Ensure text is a string
            if isinstance(text, str) and text.strip():
                extracted_text.append(f"--- Page {page_num + 1} ---\n{text}")
            else:
                # Try extracting as blocks if regular extraction fails
                blocks = page.get_text("blocks")
                block_text = "\n".join(
                    block[4] for block in blocks 
                    if block[-1] == 0  # Text blocks only (not images)
                )
                if block_text.strip():
                    extracted_text.append(f"--- Page {page_num + 1} ---\n{block_text}")
                else:
                    extracted_text.append(f"--- Page {page_num + 1} ---\n[No text found on this page]")
        
        return "\n\n".join(extracted_text)
    
    finally:
        doc.close()


def extract_text_to_file(
    pdf_path: Union[str, Path],
    output_path: Union[str, Path],
    pages: Optional[list[int]] = None,
    preserve_layout: bool = False,
    include_metadata: bool = False
) -> int:
    """
    Extract text from a PDF file and write directly to a file, page by page.
    
    This is memory-efficient as it doesn't hold all text in memory at once.
    Each page is extracted and immediately written to the output file.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to the output text file
        pages: Optional list of 0-indexed page numbers to extract.
               If None, extracts all pages.
        preserve_layout: If True, tries to preserve the visual layout
        include_metadata: If True, writes PDF metadata at the beginning
        
    Returns:
        Number of pages processed
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        RuntimeError: If the PDF cannot be opened or processed
    """
    pdf_path_obj = Path(pdf_path)
    output_path_obj = Path(output_path)
    
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path_obj}")
    
    if pdf_path_obj.suffix.lower() != '.pdf':
        raise ValueError(f"File is not a PDF: {pdf_path_obj}")
    
    try:
        doc = fitz.open(pdf_path_obj)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")
    
    try:
        total_pages = len(doc)
        
        # Determine which pages to process
        if pages is None:
            pages_to_process = list(range(total_pages))
        else:
            pages_to_process = [p for p in pages if 0 <= p < total_pages]
        
        # Open output file and write page by page
        with open(output_path_obj, 'w', encoding='utf-8') as outfile:
            # Write metadata if requested
            if include_metadata:
                metadata = doc.metadata or {}
                outfile.write("=== PDF Metadata ===\n")
                outfile.write(f"Title: {metadata.get('title', 'N/A')}\n")
                outfile.write(f"Author: {metadata.get('author', 'N/A')}\n")
                outfile.write(f"Subject: {metadata.get('subject', 'N/A')}\n")
                outfile.write(f"Creator: {metadata.get('creator', 'N/A')}\n")
                outfile.write(f"Producer: {metadata.get('producer', 'N/A')}\n")
                outfile.write(f"Page Count: {total_pages}\n")
                outfile.write("\n=== Extracted Text ===\n\n")
            
            pages_processed = 0
            
            for page_num in pages_to_process:
                page = doc.load_page(page_num)
                
                # Extract text with options
                if preserve_layout:
                    text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                else:
                    text = page.get_text("text")
                
                # Write page header
                if pages_processed > 0:
                    outfile.write("\n\n")  # Separator between pages
                
                outfile.write(f"--- Page {page_num + 1} ---\n")
                
                # Write text content
                if isinstance(text, str) and text.strip():
                    outfile.write(text)
                else:
                    # Try extracting as blocks if regular extraction fails
                    blocks = page.get_text("blocks")
                    block_text = "\n".join(
                        block[4] for block in blocks 
                        if block[-1] == 0  # Text blocks only (not images)
                    )
                    if block_text.strip():
                        outfile.write(block_text)
                    else:
                        outfile.write("[No text found on this page]")
                
                pages_processed += 1
                
                # Flush after each page to ensure data is written
                outfile.flush()
        
        return pages_processed
    
    finally:
        doc.close()


def extract_text_with_metadata(pdf_path: Union[str, Path]) -> dict:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing:
        - 'text': Extracted text
        - 'metadata': PDF metadata (title, author, etc.)
        - 'page_count': Number of pages
        - 'pages': List of page texts
    """
    pdf_path_obj = Path(pdf_path)
    
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path_obj}")
    
    try:
        doc = fitz.open(pdf_path_obj)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")
    
    try:
        result = {
            'metadata': doc.metadata,
            'page_count': len(doc),
            'pages': [],
            'text': ''
        }
        
        all_text = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            result['pages'].append({
                'page_number': page_num + 1,
                'text': text,
                'width': page.rect.width,
                'height': page.rect.height
            })
            
            all_text.append(text)
        
        result['text'] = "\n\n".join(all_text)
        return result
    
    finally:
        doc.close()


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


def main():
    """Main entry point - interactive keyboard input."""
    print("=" * 50)
    print("       PDF Text Extractor")
    print("=" * 50)
    print()
    
    try:
        # Get PDF file path
        while True:
            pdf_file = input("Enter the path to the PDF file: ").strip()
            # Remove quotes if user copied path with quotes
            pdf_file = pdf_file.strip('"').strip("'")
            
            if not pdf_file:
                print("Error: Please enter a file path.")
                continue
                
            pdf_path = Path(pdf_file)
            
            if not pdf_path.exists():
                print(f"Error: File not found: {pdf_path}")
                continue
                
            if not pdf_path.suffix.lower() == '.pdf':
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
        output_file = input("Enter output file path (press Enter to print to screen): ").strip()
        output_file = output_file.strip('"').strip("'")
        output_path = Path(output_file) if output_file else None
        
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
        print("-" * 50)
        print("Starting extraction...")
        print("-" * 50)
        
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
                
                output_lines = [
                    "=== PDF Metadata ===",
                    f"Title: {result['metadata'].get('title', 'N/A')}",
                    f"Author: {result['metadata'].get('author', 'N/A')}",
                    f"Subject: {result['metadata'].get('subject', 'N/A')}",
                    f"Creator: {result['metadata'].get('creator', 'N/A')}",
                    f"Producer: {result['metadata'].get('producer', 'N/A')}",
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
