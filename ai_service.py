import os
import asyncio
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def ask_ai(prompt: str, timeout: float = 12.0) -> str:
    if not prompt or not prompt.strip():
        return "Ошибка: получен пустой запрос."
    loop = asyncio.get_running_loop()
    response = await asyncio.wait_for(
        loop.run_in_executor(
            None,
            lambda: groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — умный AI-ассистент платформы по поиску работы и подбору персонала. "
                            "Отвечай структурированно, профессионально и по существу."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
            )
        ),
        timeout=timeout
    )