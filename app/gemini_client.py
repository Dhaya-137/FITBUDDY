from .config import settings


class GeminiConfigurationError(RuntimeError):
    pass


def _create_gemini_client():
    try:
        from google import genai
    except ImportError as exc:
        raise GeminiConfigurationError(
            "The Google Gemini SDK is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    if not settings.gemini_api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not configured. "
            "Add it to .env and restart the server."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_text(
    model: str,
    prompt: str,
    *,
    max_output_tokens: int = 5000,
) -> str:

    client = _create_gemini_client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": max_output_tokens,
            },
        )

        text = (response.text or "").strip()

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text

    finally:
        client.close()