import pytest
from AiP.BoookieDookie import recognize_text, search_google_books


def test_recognize_text():
    assert recognize_text("tests/sample_image.png") != ""


def test_search_google_books():
    book = search_google_books("Python programming")
    assert book is not None
    assert "title" in book
    assert "authors" in book