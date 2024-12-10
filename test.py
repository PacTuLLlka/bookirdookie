import unittest
from __main__ import recognize_text, search_google_books

class TestMain(unittest.TestCase):

    def test_recognize_text(self):
        result = recognize_text("example.png")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_search_google_books_valid_query(self):
        result = search_google_books("Harry Potter")
        self.assertIsNotNone(result)
        self.assertIn("title", result)
        self.assertIn("authors", result)

    def test_search_google_books_invalid_query(self):
        result = search_google_books("")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()