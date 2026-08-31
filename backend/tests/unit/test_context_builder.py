from app.services.retrieval.context_builder import build_context
from app.services.retrieval.retrieval_service import RetrievalResult

def test_build_context_text_chunk():
    results = [
        RetrievalResult(
            chunk_id="chunk1",
            chunk_text="This is a    test chunk.",
            score=0.9,
            element_ids=["el1"],
            element_types=["NarrativeText"],
            page_numbers=[1],
            primary_page=1,
            chunk_type="text",
            image_path=None,
            image_description=None,
            coordinates=[]
        )
    ]
    
    context = build_context(results)
    
    assert "SOURCE 1" in context
    assert "Chunk ID: chunk1" in context
    assert "Page: 1" in context
    assert "Type: NarrativeText" in context
    assert "Content:" in context
    assert "This is a test chunk." in context # Whitespace should be cleaned

def test_build_context_image_chunk():
    results = [
        RetrievalResult(
            chunk_id="chunk2",
            chunk_text="",
            score=0.8,
            element_ids=["el2"],
            element_types=["Image"],
            page_numbers=[2],
            primary_page=2,
            chunk_type="image",
            image_path="/path/to/img.png",
            image_description="Image Analysis Details",
            coordinates=[]
        )
    ]
    
    context = build_context(results)
    
    assert "SOURCE 1" in context
    assert "Type: Image" in context
    assert "Image Analysis:" in context
    assert "Image Analysis Details" in context

def test_build_context_removes_duplicates_and_sorts_by_page():
    results = [
        RetrievalResult("chunk2", "Page 2 text", 0.7, ["el2"], ["Table"], [2], 2, "text", None, None, []),
        RetrievalResult("chunk1", "Page 1 text", 0.8, ["el1"], ["Text"], [1], 1, "text", None, None, []),
        RetrievalResult("chunk2", "Page 2 text duplicate", 0.6, ["el2"], ["Table"], [2], 2, "text", None, None, [])
    ]
    
    context = build_context(results)
    
    # Should only have SOURCE 1 and SOURCE 2
    assert "SOURCE 1" in context
    assert "SOURCE 2" in context
    assert "SOURCE 3" not in context
    
    # Page 1 should be first because it sorts by primary_page
    # The string parsing isn't perfectly straightforward to test ordering without regex, 
    # but we can check the order of substrings:
    idx_chunk1 = context.find("chunk1")
    idx_chunk2 = context.find("chunk2")
    assert idx_chunk1 < idx_chunk2
