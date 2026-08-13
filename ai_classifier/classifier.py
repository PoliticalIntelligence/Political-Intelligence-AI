import json
import re
import time

import google.generativeai as genai

from ai_classifier.prompt import build_prompt
from ai_classifier.schema import OUTPUT_SCHEMA


class AIClassifier:

    def __init__(self, api_key, model="gemini-3.5-flash-lite"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

        # Load default JSON structure
        self.default_output = json.loads(OUTPUT_SCHEMA)

    def classify(self, caption, retries=3):

        prompt = build_prompt(caption)

        for attempt in range(retries):

            try:
                response = self.model.generate_content(prompt)

                text = response.text.strip()

                data = self._extract_json(text)

                return self._validate_output(data)

            except Exception as e:

                print(f"[Gemini Attempt {attempt + 1}/{retries}] {e}")

                time.sleep(2)

        return self.default_output.copy()

    def _extract_json(self, text):

        text = re.sub(r"^```json", "", text)
        text = re.sub(r"^```", "", text)
        text = text.replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise ValueError("No JSON found.")

        return json.loads(match.group())

    def _validate_output(self, output):

        validated = self.default_output.copy()

        for key in validated:
            if key in output:
                validated[key] = output[key]

        return validated