import pytest
from AiP.bookie import recognize_text, search_google_books, clear_search_history, search_history
from PIL import Image, ImageDraw
from unittest.mock import MagicMock
import requests_mock


@pytest.fixture
def mock_image(tmp_path):
    """Создает временное тестовое изображение с текстом и проверяет его создание."""
    image = Image.new("RGB", (200, 100), "white")
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "Test OCR", fill="black")

    image_path = tmp_path / "test_image.png"
    image.save(image_path)

    assert image_path.exists(), f"Файл {image_path} не был создан"

    return str(image_path)


def test_recognize_text(mock_image):
    """Тестирует распознавание текста с изображения."""
    result = recognize_text(mock_image, lang="eng")
    assert "Test" in result, f"Функция recognize_text не распознала текст корректно. Получено: {result}"


def test_search_google_books():
    """Тестирует поиск книги через Google Books API."""
    mocked_response = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Mocked Book Title",
                    "authors": ["Mocked Author"],
                    "imageLinks": {"thumbnail": "http://example.com/mock.jpg"},
                }
            }
        ]
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            "https://www.googleapis.com/books/v1/volumes", json=mocked_response
        )

        query = "Mocked Query"
        result = search_google_books(query)

        assert result is not None, "search_google_books вернула None, но ожидался результат."
        assert result["title"] == "Mocked Book Title", "Название книги не совпадает."
        assert result["authors"] == "Mocked Author", "Автор книги не совпадает."
        assert result["cover_image"] == "http://example.com/mock.jpg", "Ссылка на обложку не совпадает."


def test_clear_search_history():
    """Тестирует очистку истории поиска."""
    search_history.append({"title": "Test Book", "authors": "Test Author"})

    assert len(search_history) > 0, "История поиска не должна быть пустой перед очисткой."

    mock_frame = MagicMock()
    clear_search_history(mock_frame)

    search_history.clear()

    assert len(search_history) == 0, "История поиска не была очищена."
    assert search_history == [], "История поиска должна быть пустой после очистки."
