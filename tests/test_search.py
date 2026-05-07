import time

import pytest

from app.services.keyword_search import search_keywords


def test_basic_keyword_found():
    result = search_keywords("the fox ran fast", ["fox"])
    assert "fox" in result["found"]
    assert result["match_count"] == 1


def test_keyword_not_found():
    result = search_keywords("the fox ran fast", ["cat"])
    assert "cat" in result["not_found"]
    assert result["match_count"] == 0


def test_case_insensitive_default():
    result = search_keywords("the fox ran fast", ["FOX"])
    assert "FOX" in result["found"]


def test_case_sensitive_no_match():
    result = search_keywords("the fox ran fast", ["FOX"], case_sensitive=True)
    assert "FOX" in result["not_found"]
    assert result["match_count"] == 0


def test_case_sensitive_match():
    result = search_keywords("the Fox ran fast", ["Fox"], case_sensitive=True)
    assert "Fox" in result["found"]


def test_multiple_keywords_mixed():
    result = search_keywords("the fox ran past the dog", ["fox", "dog", "cat"])
    assert "fox" in result["found"]
    assert "dog" in result["found"]
    assert "cat" in result["not_found"]
    assert result["match_count"] == 2
    assert result["keyword_count"] == 3


def test_duplicate_keyword_in_input():
    result = search_keywords("the fox ran fast", ["fox", "fox"])
    assert result["keyword_count"] == 2
    assert result["found"] == ["fox"]
    assert result["match_count"] == 1


def test_keyword_at_word_boundary():
    # FlashText matches on word boundaries; "fox" should not match inside "foxes"
    result = search_keywords("the foxes ran fast", ["fox"])
    assert "fox" in result["not_found"]


def test_results_are_sorted():
    result = search_keywords("the cat and the fox ran", ["fox", "cat", "zebra"])
    assert result["found"] == sorted(result["found"])
    assert result["not_found"] == sorted(result["not_found"])


def test_large_text_performance():
    large_text = "the fox ran fast " * 60_000  # ~1 MB
    keywords = [f"keyword{i}" for i in range(100)]
    keywords[0] = "fox"

    start = time.monotonic()
    result = search_keywords(large_text, keywords)
    elapsed = time.monotonic() - start

    assert elapsed < 2.0
    assert "fox" in result["found"]
