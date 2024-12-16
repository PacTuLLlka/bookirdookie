from PIL import Image, ImageEnhance
import pytesseract
import logging

# Загружаем настройки из config.json
from utils import load_config

config = load_config()
pytesseract.pytesseract.tesseract_cmd = config["tesseract_path"]


def recognize_text(image_path: str, lang: str = "rus+eng") -> str:
    """Распознаёт текст с изображения."""
    try:
        image = Image.open(image_path).convert("L")
        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as e:
        logging.error(f"Ошибка OCR: {e}")
        return ""
