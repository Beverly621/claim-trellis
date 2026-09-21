from claim_trellis.deterministic import locate_quote, run_deterministic_checks


def test_quote_match_normalizes_spacing_and_curly_quotes() -> None:
    found, _ = locate_quote(
        "The paper says “risk fell” in the trial.", 'The paper says "risk fell"'
    )
    assert found


def test_numeric_mismatch_is_exposed_not_hidden() -> None:
    checks = run_deterministic_checks(
        "Events occurred in 6.5% of participants.",
        "Events occurred in 8.0% of participants.",
    )
    assert [token.normalized for token in checks.unmatched_claim_numbers] == [6.5]
    assert checks.warnings


def test_quote_is_checked_against_full_source() -> None:
    checks = run_deterministic_checks(
        "A claim.",
        "A selected passage.",
        "target quote",
        quote_source_text="Earlier text contains the target quote exactly.",
    )
    assert checks.quote_found is True
