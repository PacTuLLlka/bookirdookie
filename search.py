import logging
import requests

def search_google_books(query):
    api_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": 1}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            book_data = data["items"][0]["volumeInfo"]
            title = book_data.get("title", "Неизвестно")
            authors = ", ".join(book_data.get("authors", ["Неизвестно"]))
            cover_image = book_data.get("imageLinks", {}).get("thumbnail", None)
            return {"title": title, "authors": authors, "cover_image": cover_image}
        else:
            return None
    except Exception as e:
        logging.error(f"Ошибка при запросе к Google Books API: {e}")
        return None