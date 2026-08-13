import json
import os

from dotenv import load_dotenv
from google import genai

from ai_classifier.prompt import build_prompt

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def classify_caption(caption: str) -> dict:

    prompt = build_prompt(caption)

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
    )

    text = response.text.strip()

    # Remove markdown if Gemini returns ```json
    text = (
        text.replace("```json", "")
            .replace("```", "")
            .strip()
    )

    print("\n===== RAW GEMINI RESPONSE =====\n")
    print(text)

    return json.loads(text)