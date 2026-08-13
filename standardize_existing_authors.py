import re
from urllib.parse import urlparse, parse_qsl

import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

CREDENTIALS_PATH = "credentials/service_account.json"

TARGET_SPREADSHEET_ID = (
    "1grlbuXqu84eBwEEiKvKUuVjnET9zA76ESa1G5xcvMNI"
)

FACEBOOK_LINKS_SPREADSHEET_NAME = "Facebook links"
FACEBOOK_LINKS_WORKSHEET = "Sheet1"

TARGET_WORKSHEET = "AI Analysis"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ============================================================
# APPROVED FINAL MLA LIST
# ============================================================
#
# ONLY these names can be written into Author.
#
# ============================================================

APPROVED_AUTHORS = [
    "Vinay Verma",
    "Shyamdhani Rahi",
    "Jai Pratap Singh",
    "Mata Prasad Pandey",
    "Saiyada Khatoon",
    "Ajay Singh",
    "Kavindra Chaudhary - Atul",
    "Rajendra Prasad Chaudhary",
    "Mahendra Nath Yadav",
    "Dudhram",
    "Anil Kumar Tripathi",
    "Ankur Raj Tiwari",
    "Ganesh Chandra",
    "Virendra Chaudhary",
    "Rishi Tripathi",
    "Prem Sagar Patel",
    "Jai Mangal Kanojiya",
    "Gyanendra Singh",
    "Fateh Bahadur Singh",
    "Mahendra Pal Singh",
    "Yogi Adityanath",
    "Bipin Singh",
    "Pradeep Shukla",
    "Shriram Chauhan",
    "Sarvan Kumar Nishad",
    "Dr. Vimlesh Paswan",
    "Rajesh Tripathi",
    "Vivekanand Pandey",
    "Manish Kumar - Mantu",
    "Asim Kumar",
    "Surendra Kumar Kushwaha",
    "P. N. Pathak",
    "Mohan Verma",
    "Vinay Prakash Gond",
    "Jai Prakash Nishad",
    "Shalabh Mani Tripathi",
    "Surya Pratap Shahi",
    "Surendra Chaurasia",
    "Sabhakunwar Kushwaha",
    "Vijaylaxmi Gautam",
    "Deepak Kumar Mishra - Shaka",
    "Dr. Sangram Singh Yadav",
    "Nafees Ahmad",
    "Dr. Hriday Narayan Singh Patel",
    "Akhilesh Yadav",
    "Durga Prasad Yadav",
    "Ramakant Yadav",
    "Kamlakant Rajbhar - Pappu",
    "Bechai Saroj",
    "Puja Saroj",
    "Ram Bilas Chauhan",
    "Rajendra Kumar",
    "Abbas Ansari",
    "Hansu Ram",
    "Ziyauddin Rizvi",
    "Sangam Singh Yadav",
    "Daya Shankar Singh",
    "Ketakee Singh",
    "Jai Prakash Anchal",
    "Sujeet Singh",
]


# ============================================================
# SPECIAL ALIASES
# ============================================================
#
# Known variations -> FINAL approved name
#
# ============================================================

SPECIAL_AUTHOR_ALIASES = {

    # --------------------------------------------------------
    # RISHI TRIPATHI
    # --------------------------------------------------------

    "rishi tripathi": "Rishi Tripathi",
    "rishitripathi": "Rishi Tripathi",
    "rishi tripathi nautanwa": "Rishi Tripathi",
    "rishitripathinautanwa": "Rishi Tripathi",

    # --------------------------------------------------------
    # ANIL KUMAR TRIPATHI
    # --------------------------------------------------------

    "anil tripathi": "Anil Kumar Tripathi",
    "aniltripathi": "Anil Kumar Tripathi",
    "anil kumar tripathi": "Anil Kumar Tripathi",
    "anilkumartripathi": "Anil Kumar Tripathi",

    "अनिल त्रिपाठी": "Anil Kumar Tripathi",
    "अनिलत्रिपाठी": "Anil Kumar Tripathi",
    "अनिल कुमार त्रिपाठी": "Anil Kumar Tripathi",
    "अनिलकुमारत्रिपाठी": "Anil Kumar Tripathi",

    # --------------------------------------------------------
    # JAI MANGAL KANOJIYA
    # --------------------------------------------------------

    "jai mangal kanojiya": "Jai Mangal Kanojiya",
    "jaimangalkanojiya": "Jai Mangal Kanojiya",

    # Alternate English spelling
    "jai mangal kannaujiya": "Jai Mangal Kanojiya",
    "jaimangalkannaujiya": "Jai Mangal Kanojiya",

    # Hindi
    "जय मंगल कन्नौजिया": "Jai Mangal Kanojiya",
    "जयमंगलकन्नौजिया": "Jai Mangal Kanojiya",
    "जय मंगल कानौजिया": "Jai Mangal Kanojiya",
    "जयमंगलकानौजिया": "Jai Mangal Kanojiya",

    # --------------------------------------------------------
    # SABHAKUNWAR KUSHWAHA
    # --------------------------------------------------------

    "sabhakunwar kushwaha": "Sabhakunwar Kushwaha",
    "sabhakunwarkushwaha": "Sabhakunwar Kushwaha",

    "sabhakuwar kushwaha": "Sabhakunwar Kushwaha",
    "sabhakuwarkushwaha": "Sabhakunwar Kushwaha",

    # --------------------------------------------------------
    # RAM BILAS CHAUHAN
    # --------------------------------------------------------

    "ram bilas chauhan": "Ram Bilas Chauhan",
    "rambilaschauhan": "Ram Bilas Chauhan",

    "ram bilash chauhan": "Ram Bilas Chauhan",
    "rambilashchauhan": "Ram Bilas Chauhan",

    "राम बिलास चौहान": "Ram Bilas Chauhan",
    "रामबिलासचौहान": "Ram Bilas Chauhan",

    "राम बिलाश चौहान": "Ram Bilas Chauhan",
    "रामबिलाशचौहान": "Ram Bilas Chauhan",

    # --------------------------------------------------------
    # BECHAI SAROJ
    # --------------------------------------------------------

    "bechai saroj": "Bechai Saroj",
    "bechaisaroj": "Bechai Saroj",

    "mlabechaisarojlalganj351iswithdimpleyadav":
        "Bechai Saroj",
}


# ============================================================
# GOOGLE CONNECTION
# ============================================================

def get_client():

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):

    if value is None:
        return ""

    value = str(value).strip().lower()

    # Remove HTML
    value = re.sub(
        r"<br\s*/?>",
        " ",
        value,
        flags=re.I
    )

    value = re.sub(
        r"<[^>]+>",
        " ",
        value
    )

    # English titles
    value = re.sub(
        r"\bdr\.?\b",
        " ",
        value
    )

    value = re.sub(
        r"\bmla\b",
        " ",
        value
    )

    value = re.sub(
        r"\bex\s+mla\b",
        " ",
        value
    )

    value = re.sub(
        r"\bvidhayak\b",
        " ",
        value
    )

    # Hindi titles
    value = re.sub(
        r"विधायक",
        " ",
        value
    )

    value = re.sub(
        r"माननीय",
        " ",
        value
    )

    value = re.sub(
        r"डॉ\.?",
        " ",
        value
    )

    # Remove quotes
    value = re.sub(
        r"[\u2018\u2019\u201c\u201d'\"`]",
        " ",
        value
    )

    # Keep Hindi + English + numbers
    value = re.sub(
        r"[^a-z0-9\u0900-\u097f]+",
        " ",
        value
    )

    # Remove common Facebook phrases
    value = re.sub(
        r"\bis\s+with\b",
        " ",
        value
    )

    value = re.sub(
        r"\bis\s+at\b",
        " ",
        value
    )

    value = re.sub(
        r"\bupdated\s+their\s+status\b",
        " ",
        value
    )

    # Extra spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    ).strip()

    return value


def compact_text(value):

    return normalize_text(value).replace(" ", "")


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(value):

    if not value:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    value = value.replace(
        "\n",
        ""
    ).replace(
        "\r",
        ""
    )

    if not value.startswith(
        ("http://", "https://")
    ):
        value = "https://" + value

    try:

        parsed = urlparse(value)

        host = (
            parsed.hostname or ""
        ).lower()

        if host.startswith("www."):
            host = host[4:]

        if host in {
            "m.facebook.com",
            "mbasic.facebook.com",
            "web.facebook.com",
        }:
            host = "facebook.com"

        path = re.sub(
            r"/+",
            "/",
            parsed.path.strip("/").lower()
        )

        allowed_query = []

        for key, val in parse_qsl(
            parsed.query,
            keep_blank_values=True
        ):

            if key.lower() not in {
                "ref",
                "refsrc",
                "mibextid",
                "locale",
                "locale2",
                "notif_id",
                "notif_t",
            }:

                allowed_query.append(
                    (key, val)
                )

        if allowed_query:

            query = "&".join(
                f"{key}={val}"
                for key, val in allowed_query
            )

            return (
                f"https://{host}/{path}?{query}"
            ).rstrip("?")

        return (
            f"https://{host}/{path}"
        ).rstrip("/")

    except Exception:

        return value.lower().rstrip("/")


# ============================================================
# FACEBOOK IDENTIFIER
# ============================================================

def facebook_identifier(value):

    normalized = normalize_url(value)

    if not normalized:
        return ""

    try:

        parsed = urlparse(normalized)

        path = parsed.path.strip("/")

        if not path:
            return ""

        parts = [
            p for p in path.split("/")
            if p
        ]

        # profile.php?id=123
        if (
            parts
            and parts[0] == "profile.php"
        ):

            params = dict(
                parse_qsl(parsed.query)
            )

            if params.get("id"):

                return (
                    "id:"
                    + params["id"].lower()
                )

        # /pages/name/123456
        if (
            len(parts) >= 3
            and parts[0] == "pages"
        ):

            return parts[-1].lower()

        # /name
        return parts[0].lower()

    except Exception:

        return ""


# ============================================================
# APPROVED NAME MATCHER
# ============================================================

def get_approved_name(value):

    if not value:
        return None

    normalized = normalize_text(value)

    compact = compact_text(value)

    if not normalized:
        return None

    # --------------------------------------------------------
    # 1. SPECIAL ALIAS
    # --------------------------------------------------------

    if normalized in SPECIAL_AUTHOR_ALIASES:

        result = SPECIAL_AUTHOR_ALIASES[
            normalized
        ]

        if result in APPROVED_AUTHORS:
            return result

    if compact in SPECIAL_AUTHOR_ALIASES:

        result = SPECIAL_AUTHOR_ALIASES[
            compact
        ]

        if result in APPROVED_AUTHORS:
            return result

    # --------------------------------------------------------
    # 2. EXACT MATCH AGAINST APPROVED LIST
    # --------------------------------------------------------

    for approved in APPROVED_AUTHORS:

        if (
            normalized
            == normalize_text(approved)
        ):

            return approved

        if (
            compact
            == compact_text(approved)
        ):

            return approved

    # --------------------------------------------------------
    # 3. SAFE PHRASE MATCH
    #
    # Example:
    #
    # Rishi Tripathi Nautanwa
    # -> Rishi Tripathi
    #
    # Mahendra Nath Yadav MLA
    # -> Mahendra Nath Yadav
    #
    # --------------------------------------------------------

    for approved in sorted(
        APPROVED_AUTHORS,
        key=lambda x: len(
            compact_text(x)
        ),
        reverse=True,
    ):

        approved_normalized = normalize_text(
            approved
        )

        if not approved_normalized:
            continue

        if approved_normalized in normalized:

            return approved

    # --------------------------------------------------------
    # NO MATCH
    # --------------------------------------------------------

    return None


# ============================================================
# LOAD FACEBOOK MASTER
# ============================================================

def load_master(client):

    spreadsheet = client.open(
        FACEBOOK_LINKS_SPREADSHEET_NAME
    )

    worksheet = spreadsheet.worksheet(
        FACEBOOK_LINKS_WORKSHEET
    )

    rows = worksheet.get_all_records()

    by_url = {}
    by_identifier = {}

    count = 0

    for row in rows:

        status = str(
            row.get(
                "Status",
                ""
            )
        ).strip().lower()

        if (
            status
            and status != "active"
        ):
            continue

        name = str(
            row.get(
                "Name",
                ""
            )
        ).strip()

        url = str(
            row.get(
                "Facebook URL",
                ""
            )
        ).strip()

        if not name or not url:
            continue

        # Only use master names that belong
        # to our approved list.

        approved_name = get_approved_name(
            name
        )

        if not approved_name:
            continue

        record = {
            "name": approved_name,
            "url": url,
        }

        count += 1

        normalized_url = normalize_url(
            url
        )

        if normalized_url:

            by_url[
                normalized_url
            ] = record

        identifier = facebook_identifier(
            url
        )

        if identifier:

            by_identifier[
                identifier
            ] = record

    print(
        f"Approved Facebook master records loaded: {count}"
    )

    return (
        by_url,
        by_identifier,
    )


# ============================================================
# MATCH SOURCE
# ============================================================

def match_source(
    source_page,
    post_url,
    current_author,
    by_url,
    by_identifier,
):

    # --------------------------------------------------------
    # 1. AUTHOR MATCH
    # --------------------------------------------------------

    author_name = get_approved_name(
        current_author
    )

    if author_name:

        return (
            {
                "name": author_name,
                "url": "",
            },
            "Author Approved Match",
        )

    # --------------------------------------------------------
    # 2. SOURCE PAGE URL
    # --------------------------------------------------------

    source_normalized = normalize_url(
        source_page
    )

    if source_normalized in by_url:

        return (
            by_url[source_normalized],
            "Source URL Exact",
        )

    # --------------------------------------------------------
    # 3. SOURCE PAGE FACEBOOK ID
    # --------------------------------------------------------

    source_identifier = facebook_identifier(
        source_page
    )

    if (
        source_identifier
        and source_identifier in by_identifier
    ):

        return (
            by_identifier[
                source_identifier
            ],
            "Source Page ID",
        )

    # --------------------------------------------------------
    # 4. POST URL FACEBOOK ID
    # --------------------------------------------------------

    post_identifier = facebook_identifier(
        post_url
    )

    if (
        post_identifier
        and post_identifier in by_identifier
    ):

        return (
            by_identifier[
                post_identifier
            ],
            "Post URL ID",
        )

    # --------------------------------------------------------
    # 5. SOURCE PAGE NAME
    # --------------------------------------------------------

    source_name = get_approved_name(
        source_page
    )

    if source_name:

        return (
            {
                "name": source_name,
                "url": "",
            },
            "Source Name Approved Match",
        )

    return None, "Unmatched"


# ============================================================
# STANDARDIZE AI_ANALYSIS
# ============================================================

def standardize_ai_analysis(
    worksheet,
    by_url,
    by_identifier,
):

    values = worksheet.get_all_values()

    if not values:

        return {
            "rows": 0,
            "updated": 0,
            "already_correct": 0,
            "unmatched": 0,
            "empty": 0,
            "methods": {},
            "unmatched_examples": [],
        }

    headers = values[0]

    # --------------------------------------------------------
    # AUTHOR COLUMN
    # --------------------------------------------------------

    try:

        author_col = headers.index(
            "Author"
        )

    except ValueError:

        raise ValueError(
            "Author column not found in AI_Analysis."
        )

    # --------------------------------------------------------
    # SOURCE PAGE COLUMN
    # --------------------------------------------------------

    try:

        source_col = headers.index(
            "Source Page"
        )

    except ValueError:

        source_col = None

    # --------------------------------------------------------
    # POST URL COLUMN
    # --------------------------------------------------------

    try:

        post_url_col = headers.index(
            "Post URL"
        )

    except ValueError:

        post_url_col = None

    updates = []

    updated = 0
    already_correct = 0
    unmatched = 0
    empty = 0

    methods = {}

    unmatched_examples = []

    # ========================================================
    # PROCESS EVERY ROW
    # ========================================================

    for row_number, row in enumerate(
        values[1:],
        start=2,
    ):

        # ----------------------------------------------------
        # CURRENT AUTHOR
        # ----------------------------------------------------

        current_author = (
            row[author_col]
            if len(row) > author_col
            else ""
        )

        # ----------------------------------------------------
        # SOURCE PAGE
        # ----------------------------------------------------

        source_page = ""

        if (
            source_col is not None
            and len(row) > source_col
        ):

            source_page = row[
                source_col
            ]

        # ----------------------------------------------------
        # POST URL
        # ----------------------------------------------------

        post_url = ""

        if (
            post_url_col is not None
            and len(row) > post_url_col
        ):

            post_url = row[
                post_url_col
            ]

        # ----------------------------------------------------
        # COMPLETELY EMPTY AUTHOR / SOURCE / URL
        # ----------------------------------------------------

        if (
            not str(
                current_author
            ).strip()
            and not str(
                source_page
            ).strip()
            and not str(
                post_url
            ).strip()
        ):

            empty += 1
            continue

        # ----------------------------------------------------
        # MATCH
        # ----------------------------------------------------

        matched, method = match_source(
            source_page,
            post_url,
            current_author,
            by_url,
            by_identifier,
        )

        # ----------------------------------------------------
        # UNMATCHED
        # ----------------------------------------------------

        if not matched:

            unmatched += 1

            if len(
                unmatched_examples
            ) < 25:

                unmatched_examples.append(
                    {
                        "row": row_number,
                        "author": current_author,
                        "source": source_page,
                        "post_url": post_url,
                    }
                )

            continue

        # ----------------------------------------------------
        # FINAL APPROVED NAME
        # ----------------------------------------------------

        standardized_name = matched[
            "name"
        ]

        # Safety check
        if (
            standardized_name
            not in APPROVED_AUTHORS
        ):

            unmatched += 1
            continue

        # ----------------------------------------------------
        # ALREADY CORRECT
        # ----------------------------------------------------

        if (
            str(
                current_author
            ).strip()
            == standardized_name
        ):

            already_correct += 1

            methods[method] = (
                methods.get(
                    method,
                    0
                ) + 1
            )

            continue

        # ----------------------------------------------------
        # UPDATE ONLY AUTHOR CELL
        # ----------------------------------------------------

        cell = gspread.utils.rowcol_to_a1(
            row_number,
            author_col + 1,
        )

        updates.append(
            {
                "range": cell,
                "values": [
                    [standardized_name]
                ],
            }
        )

        updated += 1

        methods[method] = (
            methods.get(
                method,
                0
            ) + 1
        )

    # ========================================================
    # WRITE CHANGES
    # ========================================================

    if updates:

        worksheet.batch_update(
            updates,
            value_input_option="USER_ENTERED",
        )

    return {
        "rows": len(values) - 1,
        "updated": updated,
        "already_correct": already_correct,
        "unmatched": unmatched,
        "empty": empty,
        "methods": methods,
        "unmatched_examples": unmatched_examples,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print(
        "AI_ANALYSIS AUTHOR STANDARDIZATION"
    )
    print("=" * 80)

    print()

    print(
        f"Approved MLA names: "
        f"{len(APPROVED_AUTHORS)}"
    )

    print(
        f"Target worksheet: "
        f"{TARGET_WORKSHEET}"
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Only the Author column in AI_Analysis "
        "will be changed."
    )

    print(
        "No other worksheet will be modified."
    )

    print()

    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

    client = get_client()

    # --------------------------------------------------------
    # LOAD FACEBOOK MASTER
    # --------------------------------------------------------

    (
        by_url,
        by_identifier,
    ) = load_master(client)

    # --------------------------------------------------------
    # OPEN TARGET SPREADSHEET
    # --------------------------------------------------------

    target = client.open_by_key(
        TARGET_SPREADSHEET_ID
    )

    # --------------------------------------------------------
    # OPEN ONLY AI_ANALYSIS
    # --------------------------------------------------------

    worksheet = target.worksheet(
        TARGET_WORKSHEET
    )

    print(
        f"Processing: {worksheet.title}"
    )

    print()

    # --------------------------------------------------------
    # STANDARDIZE
    # --------------------------------------------------------

    result = standardize_ai_analysis(
        worksheet,
        by_url,
        by_identifier,
    )

    # ========================================================
    # RESULTS
    # ========================================================

    print()
    print("=" * 80)
    print(
        "AI_ANALYSIS STANDARDIZATION COMPLETE"
    )
    print("=" * 80)

    print(
        f"Total rows       : "
        f"{result['rows']}"
    )

    print(
        f"Updated          : "
        f"{result['updated']}"
    )

    print(
        f"Already correct  : "
        f"{result['already_correct']}"
    )

    print(
        f"Unmatched        : "
        f"{result['unmatched']}"
    )

    print(
        f"Empty rows       : "
        f"{result['empty']}"
    )

    # --------------------------------------------------------
    # MATCH METHODS
    # --------------------------------------------------------

    methods = result.get(
        "methods",
        {}
    )

    if methods:

        print()
        print(
            "MATCH METHODS:"
        )

        for method, count in sorted(
            methods.items()
        ):

            print(
                f"  {method:<35} {count}"
            )

    # --------------------------------------------------------
    # UNMATCHED EXAMPLES
    # --------------------------------------------------------

    examples = result.get(
        "unmatched_examples",
        []
    )

    if examples:

        print()
        print(
            "UNMATCHED EXAMPLES "
            "(maximum 25):"
        )

        for item in examples:

            print(
                f"  Row {item['row']} | "
                f"Author: {item['author']} | "
                f"Source: {item['source']}"
            )

    print()
    print(
        "Only Author values in AI_Analysis "
        "were changed."
    )

    print(
        "All other worksheets were left untouched."
    )

    print("=" * 80)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()