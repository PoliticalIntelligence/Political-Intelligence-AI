from ai_classifier.knowledge_loader import (
    SCHEMES,
    DEPARTMENTS,
    PARTIES
)


class Normalizer:

    @staticmethod
    def normalize_scheme(value):

        if not value or value == "Not Mentioned":
            return value

        value = value.strip()

        for scheme in SCHEMES:

            if value.lower() == scheme["scheme"].lower():
                return scheme["scheme"]

            for alias in scheme["aliases"]:
                if value.lower() == alias.lower():
                    return scheme["scheme"]

        return value

    @staticmethod
    def normalize_department(value):

        if not value or value == "Not Mentioned":
            return value

        value = value.strip()

        for dept in DEPARTMENTS:

            if value.lower() == dept["department"].lower():
                return dept["department"]

            for alias in dept["aliases"]:
                if value.lower() == alias.lower():
                    return dept["department"]

        return value

    @staticmethod
    def normalize_party(value):

        if not value or value == "Not Mentioned":
            return value

        value = value.strip()

        for party in PARTIES:

            if value.lower() == party["party"].lower():
                return party["party"]

            for alias in party["aliases"]:
                if value.lower() == alias.lower():
                    return party["party"]

        return value