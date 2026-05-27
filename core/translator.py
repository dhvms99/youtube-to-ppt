from deep_translator import GoogleTranslator

# Initialize the translator once (Spanish to Korean)
translator = GoogleTranslator(source='es', target='ko')

def translate_text(text: str) -> str:
    """
    Translates English text to Korean.
    """
    if not text or not text.strip():
        return ""
        
    try:
        # deep-translator handles chunks up to 5000 characters automatically, 
        # but to be safe for very long paragraphs, it's good to just pass it in.
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return "[번역 실패: " + str(e) + "]"
