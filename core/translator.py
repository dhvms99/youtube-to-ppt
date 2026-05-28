import os
from openai import OpenAI

def translate_text(text: str, api_key: str = None) -> str:
    """
    Translates Spanish text to Korean using OpenAI gpt-4o-mini.
    """
    if not text or not text.strip():
        return ""
        
    # Get API key (either passed or from environment variable)
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        return "[번역 실패: OpenAI API 키가 제공되지 않았습니다.]"
        
    try:
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Spanish-to-Korean literal translator (직독직해) for language learners. "
                        "Translate the given Spanish text into accurate Korean. "
                        "CRITICAL RULES:\n"
                        "1. Output ONLY the translated Korean text. Do NOT include any conversational fillers, prefixes, or explanations (e.g., never say 'Here is the translation...').\n"
                        "2. Translate literally (직독직해) keeping the original structure, rather than freely (의역).\n"
                        "3. Adjectives must be translated into their dictionary/modifier form (e.g., 'importante' -> '중요한', not '중요하다').\n"
                        "4. Accurately translate grammatical terms and parts of speech."
                    )
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return f"[번역 실패: {str(e)}]"

