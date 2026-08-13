EXAMPLES = """
==========================
EXAMPLE 1

Caption:
आज बांसगांव में प्रधानमंत्री आवास योजना के अंतर्गत लाभार्थियों को आवास की चाबी वितरित की गई।

Output:

{
    "main_category": "Government Scheme",
    "sub_category": "Housing",
    "event_type": "Other",
    "place_of_visit": ["Bansgaon"],
    "location_type": "Town",
    "beneficiary_group": "General Public",
    "development_sector": "Housing",
    "government_scheme": "PMAY",
    "government_department": "Rural Development",
    "party_mentioned": "Not Mentioned",
    "leader_mentioned": "Not Mentioned",
    "mentioned_persons": [],
    "opposition_mention": "No",
    "opposition_target": "Not Mentioned",
    "keywords": [
        "PMAY",
        "Housing",
        "Beneficiaries"
    ],
    "summary": "House keys distributed under PMAY."
}

==========================
EXAMPLE 2

Caption:
आज गोरखपुर में भाजपा कार्यकर्ताओं के साथ बैठक की।

Output:

{
    "main_category": "Party Activity",
    "sub_category": "Organizational Meeting",
    "event_type": "Booth Meeting",
    "place_of_visit": ["Gorakhpur"],
    "location_type": "City",
    "beneficiary_group": "Party Workers",
    "development_sector": "Not Mentioned",
    "government_scheme": "Not Mentioned",
    "government_department": "Not Mentioned",
    "party_mentioned": "BJP",
    "leader_mentioned": "Not Mentioned",
    "mentioned_persons": [],
    "opposition_mention": "No",
    "opposition_target": "Not Mentioned",
    "keywords": [
        "BJP",
        "Meeting",
        "Workers"
    ],
    "summary": "Meeting held with BJP workers."
}

==========================
EXAMPLE 3

Caption:
आज जिला अस्पताल का निरीक्षण किया।

Output:

{
    "main_category": "Health",
    "sub_category": "Inspection",
    "event_type": "Inspection",
    "place_of_visit": [],
    "location_type": "Hospital",
    "beneficiary_group": "General Public",
    "development_sector": "Health",
    "government_scheme": "Not Mentioned",
    "government_department": "Health",
    "party_mentioned": "Not Mentioned",
    "leader_mentioned": "Not Mentioned",
    "mentioned_persons": [],
    "opposition_mention": "No",
    "opposition_target": "Not Mentioned",
    "keywords": [
        "Inspection",
        "Hospital"
    ],
    "summary": "Hospital inspection conducted."
}
"""