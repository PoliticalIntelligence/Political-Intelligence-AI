from ai_classifier.classifier import PoliticalClassifier

classifier = PoliticalClassifier()

caption = """
आज प्रधानमंत्री आवास योजना के अंतर्गत लाभार्थियों को आवास की चाबी वितरित की गई।
कार्यक्रम में भारतीय जनता पार्टी के कार्यकर्ता उपस्थित रहे।
"""

result = classifier.classify(caption)

print("\n========== FINAL RESULT ==========\n")
print(result)