import asyncio
from google import genai
from src.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

_GENERATE_CONFIG = {
    "system_instruction": None,  # filled per-call
    "max_output_tokens": 300,
    "temperature": 0.7,
}


async def get_ai_response(system_prompt: str, conversation_history: list[dict]) -> str:
    config = {**_GENERATE_CONFIG, "system_instruction": system_prompt}
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=conversation_history,
            config=config,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error LLM: {e}")
        return "En este momento no puedo procesar tu mensaje. Por favor intenta en unos minutos. 🙏"
