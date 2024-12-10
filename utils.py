import os

def truncate_text(text, max_length=200):
    """Обрезает текст до заданной длины."""
    return text[:max_length] + "..." if len(text) > max_length else text