from rapidfuzz import fuzz
import re


class Matcher:

    @staticmethod
    def normalize(text):

        if text is None:
            return ""

        text = str(text).strip().lower()

        # remove multiple spaces
        text = re.sub(r"\s+", " ", text)

        # remove hyphens
        text = text.replace("-", " ")

        return text

    @staticmethod
    def exact(query, values):

        query = Matcher.normalize(query)

        for value in values:

            if Matcher.normalize(value) == query:
                return value, 100

        return None, 0

    @staticmethod
    def fuzzy(query, values, threshold=85):

        query = Matcher.normalize(query)

        best_match = None
        best_score = 0

        for value in values:

            score = fuzz.token_sort_ratio(
                query,
                Matcher.normalize(value)
            )

            if score > best_score:

                best_score = score
                best_match = value

        if best_score >= threshold:
            return best_match, best_score

        return None, best_score