"""
Political Intelligence Knowledge Base

Contains mappings used by the AI prompt to improve
classification consistency.
"""

# ==========================================================
# GOVERNMENT SCHEMES
# ==========================================================

GOVERNMENT_SCHEMES = {

    "प्रधानमंत्री आवास योजना": {
        "english": "PMAY",
        "sector": "Housing",
        "department": "Rural Development"
    },

    "पीएम आवास योजना": {
        "english": "PMAY",
        "sector": "Housing",
        "department": "Rural Development"
    },

    "आयुष्मान भारत": {
        "english": "Ayushman Bharat",
        "sector": "Health",
        "department": "Health"
    },

    "जल जीवन मिशन": {
        "english": "Jal Jeevan Mission",
        "sector": "Water Supply",
        "department": "Jal Nigam"
    },

    "प्रधानमंत्री किसान सम्मान निधि": {
        "english": "PM Kisan",
        "sector": "Agriculture",
        "department": "Agriculture"
    },

    "पीएम किसान": {
        "english": "PM Kisan",
        "sector": "Agriculture",
        "department": "Agriculture"
    },

    "स्वच्छ भारत मिशन": {
        "english": "Swachh Bharat Mission",
        "sector": "Sanitation",
        "department": "Urban Development"
    }

}

# ==========================================================
# DEVELOPMENT KEYWORDS
# ==========================================================

DEVELOPMENT_KEYWORDS = {

    "सड़क": "Road",
    "मार्ग": "Road",
    "हाईवे": "Road",

    "पुल": "Bridge",

    "बिजली": "Electricity",
    "विद्युत": "Electricity",
    "ट्रांसफार्मर": "Electricity",

    "पेयजल": "Water Supply",
    "जलापूर्ति": "Water Supply",

    "नलकूप": "Irrigation",
    "सिंचाई": "Irrigation",

    "विद्यालय": "Education",
    "स्कूल": "Education",
    "कॉलेज": "Education",

    "अस्पताल": "Health",
    "सीएचसी": "Health",
    "पीएचसी": "Health",
    "मेडिकल कॉलेज": "Health"
}

# ==========================================================
# GOVERNMENT DEPARTMENTS
# ==========================================================

DEPARTMENT_KEYWORDS = {

    "पीडब्ल्यूडी": "PWD",
    "लोक निर्माण विभाग": "PWD",

    "जल निगम": "Jal Nigam",

    "स्वास्थ्य विभाग": "Health",

    "शिक्षा विभाग": "Education",

    "कृषि विभाग": "Agriculture",

    "वन विभाग": "Forest",

    "पुलिस": "Police",

    "राजस्व": "Revenue"
}