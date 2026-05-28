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
                        "You are an expert Spanish-to-Korean textbook translator. "
                        "Translate the given Spanish text into natural and accurate Korean. "
                        "Since this is an educational material for language learners, pay close attention to:\n"
                        "1. Accurate translation of grammatical terms and parts of speech (e.g., verbs, adjectives, prepositions, etc.).\n"
                        "2. Keep the translation tone helpful and natural for students learning Spanish.\n"
                        "3. Preserve the original structural meaning as much as possible."
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

