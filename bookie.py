import argparse
import logging
from io import BytesIO
from typing import List, Dict, Union

import pytesseract
import requests
from PIL import Image, ImageEnhance, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Настройка путей для программы.")
    parser.add_argument(
        "--tesseract_path", type=str, help="Путь к tesseract"
    )
    return parser.parse_args()

args = parse_arguments()
if args.tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = args.tesseract_path
else:
    pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

search_history: List[Dict] = []

def recognize_text(image_path: str, lang: str = "rus+eng") -> str:
    """
    Распознаёт текст с изображения с помощью Tesseract OCR.

    :param image_path: Путь к изображению, с которого нужно извлечь текст.
    :param lang: Языковой пакет для Tesseract (например, "rus+eng").
    :return: Извлечённый текст в виде строки.
    """
    try:
        image = Image.open(image_path).convert("L")
        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = image.point(lambda p: p > 128 and 255)
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as e:
        logging.error(f"Ошибка OCR: {e}")
        return ""

def search_google_books(query: str) -> Union[Dict, None]:
    """
    Выполняет поиск книги по тексту через Google Books API.

    :param query: Текст для поиска (например, фрагмент текста из книги).
    :return: Словарь с данными о книге (название, авторы, обложка) или None, если ничего не найдено.
    """
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
                "cover_image": book_data.get("imageLinks", {}).get("thumbnail"),
            }
    except Exception as e:
        logging.error(f"Ошибка при запросе к Google Books API: {e}")
    return None

def process_image_and_search_book(
    notebook: ttk.Notebook, result_frame: tk.Frame, history_frame: tk.Frame
):
    """
    Загружает изображение, распознаёт текст, выполняет поиск книги и отображает результат.

    :param notebook: Виджет с вкладками (tkinter Notebook).
    :param result_frame: Фрейм для отображения результатов.
    :param history_frame: Фрейм для истории поиска.
    """
    image_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.*")])
    if not image_path:
        return

    recognized_text = recognize_text(image_path)
    if len(recognized_text) < 10:
        messagebox.showerror(
            "Ошибка",
            "Недостаточно текста для поиска или вы использовали неверный формат.",
        )
        return

    book_info = search_google_books(recognized_text[:200])
    for widget in result_frame.winfo_children():
        widget.destroy()

    if book_info:
        search_history.append(book_info)
        update_search_history(history_frame)

        tk.Label(
            result_frame,
            text=f"Название: {book_info['title']}",
            font=("Arial", 14, "bold"),
        ).pack()
        tk.Label(
            result_frame, text=f"Автор: {book_info['authors']}", font=("Arial", 12)
        ).pack()
        if book_info.get("cover_image"):
            try:
                cover_image = Image.open(
                    BytesIO(requests.get(book_info["cover_image"]).content)
                ).resize((150, 200))
                photo = ImageTk.PhotoImage(cover_image)
                label = tk.Label(result_frame, image=photo)
                label.image = photo  # Хранение ссылки на изображение, чтобы не очищалось
                label.pack()
            except Exception:
                pass
    else:
        tk.Label(result_frame, text="Книга не найдена.", font=("Arial", 14)).pack()

    tk.Button(
        result_frame,
        text="Назад",
        font=("Arial", 12),
        command=lambda: notebook.select(0),
    ).pack(pady=10)

    notebook.select(1)

def update_search_history(history_frame: tk.Frame):
    """
    Обновляет отображение истории поиска в интерфейсе.

    :param history_frame: Фрейм для отображения истории.
    """
    for widget in history_frame.winfo_children():
        widget.destroy()

    tk.Label(history_frame, text="История поиска:", font=("Arial", 12, "bold")).pack(
        anchor="w"
    )
    for book in search_history:
        tk.Label(
            history_frame,
            text=f"{book['title']} — {book['authors']}",
            font=("Arial", 10),
        ).pack(anchor="w")

def clear_search_history(history_frame: tk.Frame):
    """
    Очищает глобальную историю поиска и обновляет интерфейс.

    :param history_frame: Фрейм для отображения истории.
    """
    global search_history
    search_history = []
    update_search_history(history_frame)

def show_about_program():
    """
    Отображает окно с информацией о программе.
    """
    messagebox.showinfo(
        "О программе", "Big Balls\nVersion 1.0\nNothing interesting here :)"
    )

def create_main_window():
    """
    Создаёт главное окно приложения с интерфейсом.
    """
    root = tk.Tk()
    root.title("BookieDookie")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_search = ttk.Frame(notebook)
    notebook.add(tab_search, text="Поиск")

    tab_result = ttk.Frame(notebook)
    notebook.add(tab_result, text="Ваша книга")

    tab_history = ttk.Frame(notebook)
    notebook.add(tab_history, text="История")

    tab_about = ttk.Frame(notebook)
    notebook.add(tab_about, text="О программе")

    tk.Label(tab_search, text="Загрузите вашу страницу", font=("Arial", 14)).pack(
        pady=10
    )
    tk.Button(
        tab_search,
        text="Загрузить",
        font=("Arial", 12),
        command=lambda: process_image_and_search_book(
            notebook, tab_result, tab_history
        ),
    ).pack(pady=5)

    update_search_history(tab_history)
    tk.Button(
        tab_history,
        text="Очистить историю",
        font=("Arial", 12),
        command=lambda: clear_search_history(tab_history),
    ).pack(pady=5)

    tk.Label(tab_about, text="BookieDookie Version 1.0", font=("Arial", 12)).pack(pady=10)
    tk.Button(
        tab_about, text="О программе", font=("Arial", 12), command=show_about_program
    ).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_main_window()
