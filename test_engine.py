from ai_classifier.knowledge_engine import KnowledgeEngine

engine = KnowledgeEngine()

tests = [

    {
        "government_scheme": "Pradhan Mantri Awas Yojana",
        "government_department": "Not Mentioned",
        "development_sector": "Not Mentioned",
        "party_mentioned": "Bharatiya Janata Party"
    },

    {
        "government_scheme": "प्रधानमंत्री आवास योजना",
        "government_department": "Not Mentioned",
        "development_sector": "Not Mentioned",
        "party_mentioned": "भारतीय जनता पार्टी"
    },

    {
        "government_scheme": "PMAY Scheme",
        "government_department": "Not Mentioned",
        "development_sector": "Not Mentioned",
        "party_mentioned": "BJP Party"
    }

]

for i, sample in enumerate(tests, start=1):

    print("\n==============================")
    print(f"TEST {i}")
    print("==============================")

    result = engine.enrich(sample)

    print(result)