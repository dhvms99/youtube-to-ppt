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
                        "You are an expert Latin American (Colombian) Spanish-to-Korean literal translator (직독직해) for language learners. "
                        "The user input is extracted from a Spanish textbook PDF and may contain incomplete sentence fragments, typos, or isolated vocabulary words due to text extraction formatting. "
                        "CRITICAL RULES:\n"
                        "1. Output ONLY the translated Korean text. Do NOT include any conversational fillers, prefixes, or explanations.\n"
                        "2. Standardize translation to Latin American (Colombian) Spanish nuances.\n"
                        "   - Contextual meaning matters: 'para mi' should be translated as '나에게', not '나를 위해'.\n"
                        "   - e.g. 'es importante para mi' -> '나에게 중요하다', 'es normal para mi' -> '나에게 정상적인 일이다'.\n"
                        "3. If the input contains isolated vocabulary words or short fragments, act like a dictionary:\n"
                        "   - For common or basic expressions that can have multiple translations (like 'así'), provide 3-4 diverse translations separated by spaces (e.g., 'así' -> '이렇게 이대로 그대로 그렇게').\n"
                        "   - Base verbs MUST be translated to base Korean verbs (e.g., 'hacer' -> '하다 만들다', NOT '...에 대한').\n"
                        "   - Adverbs/Pronouns must be precise (e.g., 'aquí' -> '여기', 'hoy' -> '오늘').\n"
                        "   - Adjectives should use the modifier/adjective form (e.g., 'normal' -> '정상적인 보통의', 'importante' -> '중요한').\n"
                        "   - Verbs like 'es' or 'ser' -> '...이다' or '그것은 ...이다'.\n"
                        "4. For full sentences, provide a chunk-by-chunk literal translation (청킹/구간 단위 직독직해) to help beginners understand the exact structure. Use spaces to separate the chunks instead of slashes.\n"
                        "   - For example: 'quiero saber si puede llamarme más tarde' MUST be translated as '난 알고싶다 만약 그가 내게 전화할 수 있는지 나중에'.\n"
                        "   - Break the sentence into logical phrases (chunks) such as verbs, clauses, and adverbs.\n"
                        "5. When translating 'porque' clauses, make sure the final phrase naturally ends with '~때문이다'.\n"
                        "   - For example: 'porque es muy importante' -> '왜냐하면 매우 중요하기 때문이다'.\n"
                        "6. CRITICAL FORMATTING RULE: The final Korean translation MUST NOT contain ANY slashes (/) or periods (.). Use spaces to separate meanings or chunks. The string should just be Korean words and spaces.\n"
                        "7. Maintain the exact line breaks and structure of the original input. Your output MUST have exactly the same number of lines as the input, mapped line-by-line."
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

