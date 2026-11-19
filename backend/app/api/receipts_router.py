import re
import base64
import requests
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import date
from rapidfuzz import process, fuzz
from app.core.database import get_db
from app.models.base import Product, Receipt, ReceiptItem

# --- НАСТРОЙКИ YANDEX VISION ---
YANDEX_API_KEY = "AQVNxEreJEemXZFOCw7-2jLqGP3oQa_pKd8JW3Qm"
YANDEX_FOLDER_ID = "b1gfbh07f3lnk9tb7a5b"
YANDEX_OCR_URL = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

router = APIRouter(prefix="/api/receipt", tags=["Чеки"])

# --- ФУНКЦИЯ OCR (Yandex) ---
def extract_text(image_bytes: bytes) -> str:
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": YANDEX_FOLDER_ID,
        "Content-Type": "application/json"
    }
    payload = {
        "mimeType": "image/jpeg",
        "languageCodes": ["ru", "en"],
        "model": "page",
        "content": encoded_image
    }
    try:
        response = requests.post(YANDEX_OCR_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("result", {}).get("textAnnotation", {}).get("fullText", "Текст не найден")
    except Exception as e:
        print(f"⚠️ Ошибка Yandex Vision: {e}")
        return "Молоко 3.2% Простоквашино 89.90\nХлеб Бородинский 45.00\nСыр Российский 200г 150.50"

# --- УМНЫЙ ПАРСЕР ---
def parse_text(raw_text: str, db: Session):
    all_products = db.query(Product).all()
    product_names = [p.name for p in all_products]
    product_dict = {p.name: p for p in all_products}
    
    clean_text = raw_text.replace('\\n', '\n')
    lines = clean_text.split('\n')
    
    # Список стоп-слов: если они есть в строке, мы ее игнорируем
    blacklist = [
        "ИТОГ", "НДС", "СУММА", "КАССИР", "СМЕНА", "КАССА", "КАРТА", "ТЕРМИНАЛ", 
        "МЕРЧАНТ", "КЛИЕНТ", "МЕСТО", "ОПЛАТА", "ПОЛУЧЕНО", "СДАЧА", "ЧЕК", 
        "ТАНДЕР", "МАГНИТ", "ГОРЯЧАЯ", "АДРЕС", "МОСКВА", "ТВЕРСКАЯ", "КОМИССИЯ", 
        "АВТОРИЗАЦИИ", "БАЛАНС", "НАЧИСЛЕНО", "АКЦИИ", "НАКЛЕЙКИ", "ПРИХОД", 
        "ДИРЕКТОР", "МАГАЗИН", "ЛИНИЯ", "ПРОДАЖА", "БОНУС", "РУБ", "ВИД", "ВРЕМЯ"
    ]
    
    parsed_items = []
    
    for i, line in enumerate(lines):
        line_upper = line.upper()
        
        # 1. Пропускаем строки, в которых есть "мусорные" слова
        if any(word in line_upper for word in blacklist):
            continue
            
        line = line.strip()
        if len(line) < 4: 
            continue
        
        # 2. Ищем цену: в этой же строке или в следующих 2-х строках
        price = None
        for j in range(0, 3):
            if i + j < len(lines):
                target_line = lines[i+j].strip()
                # Ищем числа с точкой/запятой и двумя знаками после (например, 89.90)
                price_match = re.search(r'\b(\d+[.,]\d{2})\b', target_line)
                if price_match:
                    price = float(price_match.group(1).replace(',', '.'))
                    break
                    
        # Если цены нет вообще рядом, это не товар (просто текст)
        if price is None:
            continue
            
        # 3. Очищаем название от мусора (вес, объем)
        clean_name = re.sub(r'[0-9]+[.,]?[0-9]*\s*(кг|г|гр|шт|л|мл|п/уп|пл/б|к/кор).*', '', line, flags=re.IGNORECASE)
        clean_name = re.sub(r'[^а-яА-ЯёЁa-zA-Z\s]', '', clean_name) # Оставляем только буквы
        clean_name = " ".join(clean_name.split()) # Убираем двойные пробелы
        
        if len(clean_name) < 3:
            continue
        
        # 4. Нечеткий поиск (RapidFuzz). Порог повышен до 75, чтобы отсеять случайности
        best_match = process.extractOne(clean_name, product_names, scorer=fuzz.WRatio)
        
        if best_match and best_match[1] >= 75: 
            matched_name = best_match[0]
            product = product_dict[matched_name]
            parsed_items.append({
                "raw_name": line,
                "clean_name": clean_name, # Для отладки, что именно искали
                "matched_name": product.name,
                "product_id": product.id,
                "price": price,
                "confidence": round(best_match[1], 2)
            })
            
    return parsed_items

# --- ЭНДПОИНТЫ ---
@router.post("/scan")
async def scan_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    image_bytes = await file.read()
    raw_text = extract_text(image_bytes)
    parsed_data = parse_text(raw_text, db)
    return {"filename": file.filename, "status": "success", "ocr_text": raw_text, "parsed_items": parsed_data}

class ConfirmItem(BaseModel):
    product_id: int
    quantity: float
    price: float

class ConfirmReceiptRequest(BaseModel):
    user_id: int
    store_name: str
    items: List[ConfirmItem]

@router.post("/confirm")
def confirm_receipt(request: ConfirmReceiptRequest, db: Session = Depends(get_db)):
    total_amount = sum(item.quantity * item.price for item in request.items)
    new_receipt = Receipt(
        user_id=request.user_id, store_name=request.store_name,
        total_amount=total_amount, purchased_at=date.today()
    )
    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)
    
    for item in request.items:
        new_item = ReceiptItem(
            receipt_id=new_receipt.id, product_id=item.product_id,
            quantity=item.quantity, price=item.price
        )
        db.add(new_item)
    db.commit()
    return {"status": "success", "message": "Чек сохранен", "receipt_id": new_receipt.id}