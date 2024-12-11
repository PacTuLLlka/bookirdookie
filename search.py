import requests
import logging
from typing import Union, Dict


def search_google_books(query: str) -> Union[Dict, None]:
    """Выполняет поиск книги в Google Books API."""
    api_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": 1}

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        if "items" in data:
            book_data = data["items"][0]["volumeInfo"]
            return {
                "title": book_data.get("title", "Неизвестно"),
                "authors": ", ".join(book_data.get("authors", ["Неизвестно"])),
                "cover_image": book_data.get("imageLinks", {}).get("thumbnail")
            }
    except Exception as e:
        logging.error(f"Ошибка Google Books API: {e}")
    return None