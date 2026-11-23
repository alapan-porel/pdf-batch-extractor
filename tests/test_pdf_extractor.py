from src.pdf_text_extractor import parse_page_range
from src.semantic_chunker import SemanticChunker

def test_page_range_parser():
    pages = parse_page_range("1-3,5", 10)
    assert pages == [0, 1, 2, 4]

def test_semantic_chunker():
    chunker = SemanticChunker(target_chunk_size=150, overlap=30)
    sample_text = (
        "Cognitive Behavioral Therapy is an evidence-based psychotherapy framework. "
        "It examines the dynamic relationship between beliefs, emotional feelings, and behaviors. "
        "Patients learn to identify cognitive distortions such as catastrophizing and black-and-white thinking. "
        "Behavioral experiments test the validity of automatic thoughts in real-life settings."
    )
    chunks = chunker.chunk_document(sample_text, source_doc="cbt_guide.pdf")
    assert len(chunks) >= 2
    assert all("text" in c for c in chunks)
    assert chunks[0]["source"] == "cbt_guide.pdf"
