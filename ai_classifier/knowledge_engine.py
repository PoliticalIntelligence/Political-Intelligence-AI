from ai_classifier.knowledge_loader import (
    SCHEMES,
    DEPARTMENTS,
    PARTIES,
    SECTORS
)


class KnowledgeEngine:
    """
    Generic Knowledge Engine

    Responsibilities:
    1. Normalize values using aliases.
    2. Enrich missing fields.
    3. Keep all business logic in one place.
    """

    def __init__(self):

        self.kbs = {
            "schemes": SCHEMES,
            "departments": DEPARTMENTS,
            "parties": PARTIES,
            "sectors": SECTORS
        }

    # ==========================================================
    # Generic Lookup
    # ==========================================================

    def lookup(self, value, knowledge_base, primary_key):

        if value is None:
            return None

        value = str(value).strip().lower()

        if value in ["", "not mentioned"]:
            return None

        for item in knowledge_base:

            # Primary Value
            primary = str(item[primary_key]).strip().lower()

            if value == primary:
                return item

            # Aliases
            aliases = item.get("aliases", [])

            for alias in aliases:

                alias = str(alias).strip().lower()

                # Exact Match
                if value == alias:
                    return item

                # Partial Match
                if alias in value:
                    return item

                if value in alias:
                    return item

        return None

    # ==========================================================
    # Government Scheme
    # ==========================================================

    def enrich_scheme(self, data):

        result = self.lookup(
            data.get("government_scheme"),
            self.kbs["schemes"],
            "scheme"
        )

        if result is None:
            return data

        # Normalize
        data["government_scheme"] = result["scheme"]

        # Fill Department
        if data.get("government_department") in ["", "Not Mentioned", None]:
            data["government_department"] = result["department"]

        # Fill Sector
        if data.get("development_sector") in ["", "Not Mentioned", None]:
            data["development_sector"] = result["sector"]

        return data

    # ==========================================================
    # Political Party
    # ==========================================================

    def enrich_party(self, data):

        result = self.lookup(
            data.get("party_mentioned"),
            self.kbs["parties"],
            "party"
        )

        if result:
            data["party_mentioned"] = result["party"]

        return data

    # ==========================================================
    # Department
    # ==========================================================

    def enrich_department(self, data):

        result = self.lookup(
            data.get("government_department"),
            self.kbs["departments"],
            "department"
        )

        if result:
            data["government_department"] = result["department"]

        return data

    # ==========================================================
    # Master Enrichment
    # ==========================================================

    def enrich(self, data):

        data = self.enrich_scheme(data)
        data = self.enrich_department(data)
        data = self.enrich_party(data)

        return data