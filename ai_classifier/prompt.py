from ai_classifier.schema import OUTPUT_SCHEMA
from ai_classifier.examples import EXAMPLES


def build_prompt(caption):
    return f"""
You are an expert Political Intelligence Analyst specializing in Indian politics.

Your task is to analyze a Facebook post caption of an MLA, MP, Minister, Political Party, or Political Leader.

Return ONLY valid JSON.

Do NOT return markdown.
Do NOT explain your answer.
Do NOT add extra text.
Do NOT invent information.
Only extract information explicitly mentioned in the caption.

--------------------------------------------------
CLASSIFICATION RULES
--------------------------------------------------

1. main_category

Choose ONLY ONE:

Development
Government Scheme
Welfare
Law & Order
Health
Education
Agriculture
Employment
Women Empowerment
Youth
Religious
Cultural
Public Outreach
Party Activity
Booth/Karyakarta
Political Attack
Election Campaign
Administrative Meeting
Inspection
Disaster Relief
Environment
Achievement
Personal
Other

--------------------------------------------------

2. sub_category

Return a short descriptive sub-category.

Examples:

Housing
Road Construction
Farmer Welfare
Temple Visit
Organizational Meeting
Health Camp
Review Meeting

If not applicable return "".

--------------------------------------------------

3. event_type

Choose ONLY ONE:

Inauguration
Foundation Stone
Inspection
Public Meeting
Jan Chaupal
Village Visit
Press Conference
Review Meeting
Courtesy Meeting
Temple Visit
Festival Celebration
Medical Camp
Tree Plantation
Relief Distribution
Booth Meeting
Mandal Meeting
Training Programme
Campaign Rally
Road Show
Social Media Appeal
Birthday Greeting
Condolence
Protest
Memorandum Submission
Award Ceremony
Other

--------------------------------------------------

4. place_of_visit

Extract ALL places explicitly mentioned.

Rules:

- Return a JSON array.
- Include only explicitly mentioned places.
- Do NOT infer districts.
- Do NOT infer assembly constituencies.
- Do NOT infer states.
- If no place is mentioned return [].

Examples:

["Gorakhpur"]

["Bansgaon", "Kaudiram"]

[]

--------------------------------------------------

5. location_type

Choose ONLY ONE:

Village
Gram Panchayat
Block
Tehsil
Town
City
Temple
Mosque
Church
Gurudwara
School
College
University
Hospital
Medical College
Government Office
Party Office
Police Station
Market
Railway Station
Bus Stand
Industrial Area
Other

If unknown return "".

--------------------------------------------------

6. beneficiary_group

Choose ONLY ONE:

General Public
Farmers
Women
Youth
Students
Senior Citizens
Children
SC
ST
OBC
EWS
Minorities
Divyang
Labourers
Government Employees
Teachers
Healthcare Workers
Entrepreneurs
Traders
Industrialists
Self Help Groups
Party Workers
Booth Workers
Religious Community
Flood Victims
Disaster Victims
Villagers
Urban Residents
Multiple Groups

If unknown return "".

--------------------------------------------------

7. development_sector

Choose ONLY ONE:

Road
Bridge
Electricity
Water Supply
Irrigation
Housing
Health
Education
Transport
Railway
Airport
Drainage
Sanitation
Digital Infrastructure
Agriculture
Tourism
Industry
Sports
Environment
Other

If not applicable return "".

--------------------------------------------------

8. government_scheme

Return the official scheme name.

If no scheme is mentioned return "".

--------------------------------------------------

9. government_department

Return the official department.

If unknown return "".

--------------------------------------------------

10. party_mentioned

Return ONLY ONE:

BJP
SP
BSP
Congress
JD(U)
RJD
NISHAD Party
Apna Dal (S)
SBSP
AAP
AIMIM
Jan Suraaj
Other

If no political party is mentioned return "".

--------------------------------------------------

11. leader_mentioned

Return the primary political leader mentioned.

If none return "".

--------------------------------------------------

12. mentioned_persons

Return every other person's name.

Return a JSON array.

If none:

[]

--------------------------------------------------

13. opposition_mention

Return:

true

or

false

--------------------------------------------------

14. opposition_target

If opposition_mention is true, return the targeted party or leader.

Otherwise return "".

--------------------------------------------------

15. keywords

Return 5-10 important keywords.

Return a JSON array.

--------------------------------------------------

16. summary

Write one concise sentence (maximum 30 words).

--------------------------------------------------

OUTPUT SCHEMA

{OUTPUT_SCHEMA}

--------------------------------------------------

REFERENCE EXAMPLES

{EXAMPLES}

--------------------------------------------------

CAPTION

{caption}

--------------------------------------------------

Return ONLY valid JSON.
"""