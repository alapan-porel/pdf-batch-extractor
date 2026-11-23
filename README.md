# PyMuPDF High-Throughput Batch Corpus Extractor

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyMuPDF](https://img.shields.io/badge/Engine-PyMuPDF%20%28fitz%29-orange.svg)](https://github.com/pymupdf/PyMuPDF)

A high-performance multiprocessing document extraction and semantic chunking suite built on PyMuPDF (`fitz`). Engineered to rapidly convert complex multi-page academic textbooks, clinical treatises, and PDF monographs into clean, header-stripped, token-budgeted corpora for RAG vector databases and LLM instruction tuning.

---

## Architectural Highlights

* **Multi-Process Concurrency**: Exploits Python's `multiprocessing` worker pools to saturate multi-core CPUs during large directory text conversions.
* **Header / Footer Stripping**: Positionally eliminates repetitive running heads, page numbering, and copyright notices.
* **Ligature & Hyphenation Normalization**: Resolves broken hyphenated words at line wraps (`psycho-\nlogy` $\rightarrow$ `psychology`) and fixes font encoding anomalies.
* **Sentence-Aware Semantic Chunking**: Respects sentence boundaries and embeds customizable character overlap for dense retrieval applications.
* **Zero Copyrighted Dumps**: Ships purely as clean engine source code without bundled third-party PDF or text dumps.

---

## Installation & Quickstart

```bash
pip install -r requirements.txt
pytest tests/
```

### CLI Batch Extraction

```bash
# Convert a single PDF
python -m src.cli document.pdf --output out/

# Convert entire directory using 8 parallel worker processes
python -m src.cli /path/to/pdf/library --output /path/to/extracted/ --workers 8 --chunk
```

### Python API Integration

```python
from src.pdf_text_extractor import extract_text_from_pdf
from src.semantic_chunker import SemanticChunker

# 1. Extract raw text
raw_text = extract_text_from_pdf("clinical_treatise.pdf", page_range="1-20")

# 2. Semantic chunking
chunker = SemanticChunker(target_chunk_size=1000, overlap=150)
chunks = chunker.chunk_document(raw_text, source_doc="clinical_treatise.pdf")

print(f"Generated {len(chunks)} bounded chunks for embedding index.")
```

---

## License

Apache-2.0. Cleanroom extraction and packaging release.
