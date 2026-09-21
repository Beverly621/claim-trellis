from claim_trellis.citations import extract_citation_sentences, strip_citation_markers


def test_extracts_numeric_and_author_year_citations() -> None:
    text = "Earlier work disagreed. The intervention reduced risk [12, 14]. Smith et al. (2023) reported a similar result."
    rows = extract_citation_sentences(text)
    assert len(rows) == 2
    assert rows[0].markers == ["[12, 14]"]
    assert rows[1].markers == ["Smith et al. (2023)"]


def test_strips_markers_without_leaving_punctuation_gaps() -> None:
    assert strip_citation_markers("Risk decreased [12].") == "Risk decreased."
