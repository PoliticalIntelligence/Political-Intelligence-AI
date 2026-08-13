import json
from pathlib import Path


class KnowledgeLoader:
    """
    Loads all knowledge base JSON files from the knowledge_base folder.
    """

    ROOT_DIR = Path(__file__).resolve().parent.parent
    KB_DIR = ROOT_DIR / "knowledge_base"

    @classmethod
    def load(cls, filename):
        path = cls.KB_DIR / filename

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


# -------------------------
# Load all Knowledge Bases
# -------------------------

SCHEMES = KnowledgeLoader.load("schemes.json")
DEPARTMENTS = KnowledgeLoader.load("departments.json")
SECTORS = KnowledgeLoader.load("sectors.json")
PARTIES = KnowledgeLoader.load("parties.json")

# Future Files

# LEADERS = KnowledgeLoader.load("leaders.json")
# ORGANIZATIONS = KnowledgeLoader.load("organizations.json")
# DISTRICTS = KnowledgeLoader.load("districts.json")
# CONSTITUENCIES = KnowledgeLoader.load("assembly_constituencies.json")
# EVENT_TYPES = KnowledgeLoader.load("event_types.json")
# BENEFICIARY_GROUPS = KnowledgeLoader.load("beneficiary_groups.json")