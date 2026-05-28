import easyocr
import os

# Initialize the EasyOCR reader once.
# gpu=True will use CUDA if available, falling back to CPU otherwise.
# We include 'en' (English) and 'es' (Spanish) as requested.
reader = easyocr.Reader(['en', 'es'], gpu=True)

import cv2

def extract_text_from_image(image_path: str, crop_bottom_percent: float = 8.0) -> str:
    """
    Extracts text from a given image using EasyOCR.
    Crops the bottom percentage of the image to remove watermarks.
    """
    if not os.path.exists(image_path):
        return ""
        
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        return ""
        
    # Crop the bottom part
    h, w = img.shape[:2]
    crop_h = int(h * (1.0 - (crop_bottom_percent / 100.0)))
    cropped_img = img[:crop_h, :]
    
    # Convert to grayscale to improve contrast for text recognition
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
    
    # Use EasyOCR's native readtext parameters instead of manual resizing
    # mag_ratio=2.0 helps with small punctuation like ¿
    # text_threshold=0.5 and low_text=0.3 help catch standalone letters like 'I'
    results = reader.readtext(
        gray, 
        mag_ratio=2.0,
        text_threshold=0.5,
        low_text=0.3,
        width_ths=0.7
    )
    
    texts = []
    for (bbox, text, prob) in results:
        # Quick post-processing for common OCR mistakes
        text = text.replace("g0", "go")
        
        # In Spanish, ¿ is often misread as i attached to a capital letter (e.g., iQué)
        if text.startswith('i') and len(text) > 1 and text[1].isupper():
            text = '¿' + text[1:]
            
        texts.append(text)
        
    extracted_text = " ".join(texts)
    return extracted_text

def correct_ocr_text_with_ai(text: str, api_key: str) -> str:
    """
    Uses OpenAI gpt-4o-mini to correct OCR typos and formatting issues.
    """
    if not text or not text.strip():
        return text
        
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return text # Fallback to original text if no key is provided
        
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert OCR corrector for English and Spanish educational slides. "
                        "Your task is to fix common OCR typos in the provided text. "
                        "CRITICAL RULES:\n"
                        "1. Output ONLY the corrected text. Do NOT add any conversational fillers or explanations.\n"
                        "2. Fix common errors: missing 'I', 'g0' to 'go', 'ies' or 'i' to '¿es' or '¿' when it is a Spanish question.\n"
                        "3. Fix spacing and capitalization issues caused by OCR.\n"
                        "4. Do NOT translate the text. Keep it in its original language."
                    )
                },
                {"role": "user", "content": text}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI OCR Correction error: {e}")
        return text
