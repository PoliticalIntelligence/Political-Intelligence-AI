import json
import re
import time

import google.generativeai as genai

from ai_classifier.prompt import build_prompt
from ai_classifier.schema import OUTPUT_SCHEMA


class AIClassifier:

    # Keep safely below the Gemini 15 requests/minute limit.
    # 6 seconds = approximately 10 requests/minute.
    REQUEST_INTERVAL_SECONDS = 6

    # Maximum number of retries after a temporary API error.
    MAX_RETRIES = 4

    def __init__(self, api_key, model="gemini-3.5-flash-lite"):
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model)

        # Load default JSON structure
        self.default_output = json.loads(OUTPUT_SCHEMA)

        # Track the last Gemini request time
        self.last_request_time = 0

    def _wait_for_rate_limit(self):
        """
        Ensure there is at least 6 seconds between Gemini API requests.
        """

        elapsed = time.time() - self.last_request_time

        if elapsed < self.REQUEST_INTERVAL_SECONDS:
            wait_time = self.REQUEST_INTERVAL_SECONDS - elapsed

            print(
                f"[Gemini Rate Limit] Waiting "
                f"{wait_time:.1f} seconds..."
            )

            time.sleep(wait_time)

    def _is_rate_limit_error(self, error):
        """
        Detect Gemini rate-limit / quota errors.
        """

        error_text = str(error).lower()

        rate_limit_indicators = [
            "429",
            "resource exhausted",
            "rate limit",
            "quota",
            "too many requests",
        ]

        return any(
            indicator in error_text
            for indicator in rate_limit_indicators
        )

    def _is_temporary_error(self, error):
        """
        Detect errors that are reasonable to retry.
        """

        error_text = str(error).lower()

        temporary_indicators = [
            "429",
            "503",
            "504",
            "408",
            "resource exhausted",
            "rate limit",
            "too many requests",
            "temporarily unavailable",
            "unavailable",
            "timeout",
        ]

        return any(
            indicator in error_text
            for indicator in temporary_indicators
        )

    def classify(self, caption, retries=None):

        if retries is None:
            retries = self.MAX_RETRIES

        prompt = build_prompt(caption)

        for attempt in range(retries):

            try:

                # -------------------------------------------------
                # RATE LIMIT PROTECTION
                # -------------------------------------------------

                self._wait_for_rate_limit()

                print(
                    f"[Gemini] Sending request "
                    f"(attempt {attempt + 1}/{retries})..."
                )

                # Record the time immediately before the API call.
                self.last_request_time = time.time()

                response = self.model.generate_content(prompt)

                # -------------------------------------------------
                # RESPONSE VALIDATION
                # -------------------------------------------------

                if not response:
                    raise ValueError("Empty Gemini response.")

                text = response.text.strip()

                if not text:
                    raise ValueError("Gemini returned empty text.")

                # -------------------------------------------------
                # JSON EXTRACTION
                # -------------------------------------------------

                data = self._extract_json(text)

                # -------------------------------------------------
                # VALIDATE OUTPUT
                # -------------------------------------------------

                return self._validate_output(data)

            except Exception as e:

                print(
                    f"[Gemini Attempt "
                    f"{attempt + 1}/{retries}] "
                    f"{type(e).__name__}: {e}"
                )

                # -------------------------------------------------
                # RATE LIMIT / TEMPORARY ERROR
                # -------------------------------------------------

                if self._is_temporary_error(e):

                    if attempt < retries - 1:

                        if self._is_rate_limit_error(e):

                            # Longer backoff for rate-limit errors.
                            # 20 → 40 → 60 seconds
                            wait_time = min(
                                20 * (2 ** attempt),
                                60
                            )

                            print(
                                f"[Gemini Rate Limit] "
                                f"Waiting {wait_time} seconds "
                                f"before retry..."
                            )

                        else:

                            # Shorter backoff for other temporary errors.
                            wait_time = min(
                                5 * (2 ** attempt),
                                30
                            )

                            print(
                                f"[Gemini Temporary Error] "
                                f"Waiting {wait_time} seconds "
                                f"before retry..."
                            )

                        time.sleep(wait_time)

                        continue

                # -------------------------------------------------
                # NON-RETRYABLE ERROR
                # -------------------------------------------------

                print(
                    "[Gemini] Non-retryable error. "
                    "Skipping this request."
                )

                break

        print(
            "[Gemini] All attempts failed. "
            "Using default output."
        )

        return self.default_output.copy()

    def _extract_json(self, text):

        text = re.sub(
            r"^```json",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"^```",
            "",
            text
        )

        text = text.replace("```", "").strip()

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if not match:
            raise ValueError("No JSON found.")

        return json.loads(match.group())

    def _validate_output(self, output):

        validated = self.default_output.copy()

        for key in validated:

            if key in output:
                validated[key] = output[key]

        return validated