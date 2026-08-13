import json

OUTPUT_SCHEMA = json.dumps(
    {
        "main_category": "",
        "sub_category": "",
        "event_type": "",

        # Location
        "place_of_visit": [],
        "location_type": "",

        # Beneficiary
        "beneficiary_group": "",

        # Governance
        "development_sector": "",
        "government_scheme": "",
        "government_department": "",

        # Politics
        "party_mentioned": "",
        "leader_mentioned": "",
        "mentioned_persons": [],

        # Opposition
        "opposition_mention": False,
        "opposition_target": "",

        # Metadata
        "keywords": [],
        "summary": ""

    },
    indent=4,
    ensure_ascii=False
)