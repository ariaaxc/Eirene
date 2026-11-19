import os
from google.cloud import vision

# Указываем путь к ключу (он лежит в корне папки backend)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_credentials.json"

def extract_text_from_image(image_bytes: bytes) -> str:
    """Отправляет картинку в Google и возвращает распознанный текст."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    
    # Вызываем распознавание текста (OCR)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if response.error.message:
        raise Exception(f"Ошибка Google API: {response.error.message}")
        
    if texts:
        return texts[0].description # Возвращаем весь текст с картинки
    return ""