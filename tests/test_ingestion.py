import pytest

from claim_trellis.ingestion import IngestionError, parse_document_bytes


def test_parses_utf8_text_and_citations() -> None:
    parsed = parse_document_bytes("source.txt", b"A result was reported [1].")
    assert parsed.character_count == 26
    assert parsed.citation_sentences[0].markers == ["[1]"]
    assert len(parsed.content_sha256) == 64


def test_rejects_unsupported_suffix() -> None:
    with pytest.raises(IngestionError, match="Unsupported"):
        parse_document_bytes("source.exe", b"not a document")


def test_rejects_oversized_upload() -> None:
    with pytest.raises(IngestionError, match="exceeds"):
        parse_document_bytes("source.txt", b"12345", max_bytes=4)
