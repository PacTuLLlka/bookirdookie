import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import logging
from PIL import Image, ImageEnhance, ImageTk
import pytesseract
import requests
from io import BytesIO
from typing import List, Dict, Union

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

search_history: List[Dict] = []


def recognize_text(image_path: str, lang: str = "rus+eng") -> str:
    """Распознаёт текст с изображения."""
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
        logging.error(f"Ошибка при запросе к Google Books API: {e}")
    return None


def process_image_and_search_book(result_frame: tk.Frame, history_frame: tk.Frame):
    """Загружает изображение, распознаёт текст и ищет книгу по этому тексту."""
    image_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.*")])
    if not image_path:
        return

    recognized_text = recognize_text(image_path)
    if len(recognized_text) < 10:
        messagebox.showerror("Ошибка", "Недостаточно текста для поиска или вы использовали неверный формат.")
        return

    book_info = search_google_books(recognized_text[:200])
    for widget in result_frame.winfo_children():
        widget.destroy()

    if book_info:
        search_history.append(book_info)
        tk.Label(result_frame, text=f"Название: {book_info['title']}", font=("Arial", 14, "bold")).pack()
        tk.Label(result_frame, text=f"Автор: {book_info['authors']}", font=("Arial", 12)).pack()
        if book_info.get("cover_image"):
            try:
                cover_image = Image.open(BytesIO(requests.get(book_info["cover_image"]).content)).resize((150, 200))
                photo = ImageTk.PhotoImage(cover_image)
                label = tk.Label(result_frame, image=photo)
                label.image = photo
                label.pack()
            except Exception:
                pass
    else:
        tk.Label(result_frame, text="Книга не найдена.", font=("Arial", 14)).pack()

    update_search_history(history_frame)


def update_search_history(history_frame: tk.Frame):
    """Обновляет отображение истории поиска."""
    for widget in history_frame.winfo_children():
        widget.destroy()

    tk.Label(history_frame, text="История поиска:", font=("Arial", 12, "bold")).pack(anchor="w")
    for book in search_history:
        tk.Label(history_frame, text=f"{book['title']} — {book['authors']}", font=("Arial", 10)).pack(anchor="w")


def clear_search_history(history_frame: tk.Frame):
    """Очищает историю поиска."""
    global search_history
    search_history = []
    update_search_history(history_frame)


def show_about_program():
    """Отображает информацию о программе."""
    messagebox.showinfo(
        "О программе",
        "Big Balls\nВерсия 1.0\nNothing interesting here :)."
    )


def create_main_window():
    root = tk.Tk()
    root.title("ShazamForBooks")
    root.geometry("800x600")

    # Создание стилей
    style = ttk.Style(root)
    style.configure("TNotebook", background="#f0f0f0")
    style.configure("TNotebook.Tab", background="#e0e0e0", padding=[10, 5])
    style.map("TNotebook.Tab", background=[("selected", "#d0d0d0")])  # Цвет активной вкладки

    # Создание вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_search = ttk.Frame(notebook)
    tab_history = ttk.Frame(notebook)
    tab_about = ttk.Frame(notebook)

    notebook.add(tab_search, text="Поиск")
    notebook.add(tab_history, text="История")
    notebook.add(tab_about, text="О программе")

    tk.Label(tab_search, text="Загрузить изображение", font=("Arial", 14)).pack(pady=10)
    tk.Button(tab_search, text="Загрузить", font=("Arial", 12),
              command=lambda: process_image_and_search_book(tab_search, tab_history)).pack(pady=5)

    tk.Label(tab_history, text="История поиска", font=("Arial", 14)).pack(pady=10)
    tk.Button(tab_history, text="Очистить историю", font=("Arial", 12),
              command=lambda: clear_search_history(tab_history)).pack(pady=5)

    tk.Label(tab_about, text="О программе", font=("Arial", 14)).pack(pady=10)
    tk.Label(tab_about, text="Big Balls Version 1.0", font=("Arial", 12)).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_main_window()