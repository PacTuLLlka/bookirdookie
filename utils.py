import json
from tkinter import Frame, Label
from typing import List, Dict


def load_config(config_path="config.json") -> Dict:
    """Загружает конфигурационный файл."""
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def update_search_history(history_frame: Frame, search_history: List[Dict]):
    """Обновляет виджет истории поиска."""
    for widget in history_frame.winfo_children():
        widget.destroy()

    Label(history_frame, text="История поиска:", font=("Arial", 12, "bold")).pack(
        anchor="w"
    )
    for book in search_history:
        Label(
            history_frame,
            text=f"{book['title']} — {book['authors']}",
            font=("Arial", 10),
        ).pack(anchor="w")


def clear_search_history(history_frame: Frame, search_history: List[Dict]):
    """Очищает историю поиска."""
    search_history.clear()
    update_search_history(history_frame, search_history)
