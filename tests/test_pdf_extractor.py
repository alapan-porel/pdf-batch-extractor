import unittest
import sys
import os

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pdf_text_extractor import parse_page_range
from src.semantic_chunker import SemanticChunker

class TestPyMuPDFExtractor(unittest.TestCase):
    def test_page_range_parser(self):
        pages = parse_page_range("1-3,5", 10)
        self.assertEqual(pages, [0, 1, 2, 4])

    def test_page_range_parser_bounds(self):
        pages = parse_page_range("8-15", 10)
        self.assertEqual(pages, [7, 8, 9])

    def test_semantic_chunker(self):
        chunker = SemanticChunker(target_chunk_size=150, overlap=30)
        sample_text = (
            "Cognitive Behavioral Therapy is an evidence-based psychotherapy framework. "
            "It examines the dynamic relationship between beliefs, emotional feelings, and behaviors. "
            "Patients learn to identify cognitive distortions such as catastrophizing and black-and-white thinking. "
            "Behavioral experiments test the validity of automatic thoughts in real-life settings."
        )
        chunks = chunker.chunk_document(sample_text, source_doc="cbt_guide.pdf")
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(all("text" in c for c in chunks))
        self.assertEqual(chunks[0]["source"], "cbt_guide.pdf")

if __name__ == "__main__":
    unittest.main()
