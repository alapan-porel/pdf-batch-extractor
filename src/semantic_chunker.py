"""
Semantic Text Chunker
Splits raw extracted PDF document streams into bounded, sentence-aware chunks suitable for RAG embedding.
"""

import re
from typing import List, Dict, Any

class SemanticChunker:
    def __init__(self, target_chunk_size: int = 1000, overlap: int = 150):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def clean_text(self, text: str) -> str:
        # Strip header/footer noise and multiple newlines
        text = re.sub(r'\f', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()

    def split_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries while preserving abbreviations
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_document(self, text: str, source_doc: str = "") -> List[Dict[str, Any]]:
        cleaned = self.clean_text(text)
        sentences = self.split_sentences(cleaned)
        chunks = []
        current_chunk: List[str] = []
        current_len = 0
        chunk_idx = 0

        for sent in sentences:
            sent_len = len(sent)
            if current_len + sent_len > self.target_chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "chunk_id": f"{source_doc}_chunk_{chunk_idx}",
                    "source": source_doc,
                    "index": chunk_idx,
                    "text": chunk_text,
                    "char_count": len(chunk_text)
                })
                chunk_idx += 1
                # Overlap logic
                current_chunk = current_chunk[-2:] if len(current_chunk) >= 2 else []
                current_len = sum(len(s) for s in current_chunk)

            current_chunk.append(sent)
            current_len += sent_len

        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "chunk_id": f"{source_doc}_chunk_{chunk_idx}",
                "source": source_doc,
                "index": chunk_idx,
                "text": chunk_text,
                "char_count": len(chunk_text)
            })

        return chunks
