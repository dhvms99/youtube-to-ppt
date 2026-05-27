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
    
    # Resize the image to 2x for better punctuation (¿, ¡) recognition
    enlarged_img = cv2.resize(cropped_img, (w * 2, crop_h * 2), interpolation=cv2.INTER_CUBIC)
    
    # readtext can accept a numpy array
    results = reader.readtext(enlarged_img)
    
    # We join all extracted text lines into a single string with spaces instead of newlines
    extracted_text = " ".join([text for (bbox, text, prob) in results])
    return extracted_text
