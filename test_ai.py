import os
import json
from dotenv import load_dotenv

load_dotenv()
from ai_classifier.classifier import AIClassifier
from ai_classifier.knowledge_engine import KnowledgeEngine

# -------------------------
# Gemini API Key
# -------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

classifier = AIClassifier(API_KEY)
knowledge = KnowledgeEngine()

# -------------------------
# Test Caption
# -------------------------
caption = """
आज बांसगांव में प्रधानमंत्री आवास योजना के लाभार्थियों को आवास की चाबी वितरित की तथा भाजपा कार्यकर्ताओं के साथ बैठक की।
"""

# -------------------------
# AI Classification
# -------------------------
result = classifier.classify(caption)

# -------------------------
# Knowledge Enrichment
# -------------------------
result = knowledge.enrich(result)

# -------------------------
# Print Result
# -------------------------
print(json.dumps(result, indent=4, ensure_ascii=False))