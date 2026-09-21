import hashlib

from claim_trellis.chunking import chunk_text
from claim_trellis.models import EvidencePassage
from claim_trellis.retrieval import rank_passages


def test_chunking_preserves_offsets_and_overlap() -> None:
    text = "First sentence. Second sentence. Third sentence. Fourth sentence."
    passages = chunk_text(text, target_chars=25, max_chars=40, overlap_sentences=1)
    assert len(passages) >= 2
    for passage in passages:
        assert text[passage.start_char : passage.end_char] == passage.text


def test_retrieval_places_matching_passage_first() -> None:
    texts = [
        "The astronomy team measured distant stars and telescope noise.",
        "In the randomized trial, semaglutide reduced major cardiovascular events compared with placebo.",
        "A separate appendix describes software versions and data access.",
    ]
    passages = [
        EvidencePassage(
            passage_id=f"p-{index}",
            text=text,
            locator=f"test:{index}",
            start_char=index * 100,
            end_char=index * 100 + len(text),
            sha256=hashlib.sha256(text.encode()).hexdigest(),
        )
        for index, text in enumerate(texts)
    ]
    results = rank_passages("Semaglutide reduced cardiovascular events", passages, top_k=3)
    assert "semaglutide" in results[0].passage.text.lower()
    assert results[0].score > results[-1].score
