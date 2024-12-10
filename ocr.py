import logging
from PIL import Image, ImageEnhance
import pytesseract

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

def recognize_text(image_path):
    try:
        image = Image.open(image_path)
        image = image.convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        threshold = 128
        image = image.point(lambda p: p > threshold and 255)
        text = pytesseract.image_to_string(image, lang="rus+eng")
        logging.info(f"Распознанный текст (длина {len(text)} символов): {text[:200]}...")
        return text.strip()
    except Exception as e:
        logging.error(f"Ошибка OCR: {e}")
        return ""