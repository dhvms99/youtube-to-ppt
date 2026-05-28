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
