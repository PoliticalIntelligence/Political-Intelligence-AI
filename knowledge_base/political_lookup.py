import os
import re
import pandas as pd
from rapidfuzz import fuzz


class PoliticalLookup:

    # ============================================================
    # Constructor
    # ============================================================

    def __init__(self):

        self.datasets = []

        self.search_index = {}

        self.alias_cache = {}

        # Column Priority
        self.column_weights = {

            "वार्ड": 100,
            "जिला पंचायत वार्ड": 100,

            "नगर निगम": 95,
            "नगर पालिका": 95,
            "नगर पंचायत": 95,

            "विकास खंड": 90,

            "जिला": 60,
            "विधानसभा": 50

        }

        self.load_datasets()

        self.build_index()

    # ============================================================
    # Load CSVs
    # ============================================================

    def load_datasets(self):

        dataset_folder = os.path.join(

            os.path.dirname(__file__),

            "datasets"

        )

        if not os.path.exists(dataset_folder):

            raise FileNotFoundError(
                f"Dataset folder not found : {dataset_folder}"
            )

        csv_files = [

            file

            for file in os.listdir(dataset_folder)

            if file.lower().endswith(".csv")

        ]

        print("=" * 70)
        print("Loading Political Knowledge Base")
        print("=" * 70)

        for file in sorted(csv_files):

            path = os.path.join(

                dataset_folder,

                file

            )

            try:

                df = pd.read_csv(path)

                # -------------------------
                # Clean Column Names
                # -------------------------

                df.columns = (

                    df.columns

                    .astype(str)

                    .str.strip()

                    .str.replace("\n", "", regex=False)

                    .str.replace("\r", "", regex=False)

                )

                # -------------------------
                # Clean Cell Values
                # -------------------------

                df = df.fillna("")

                df = df.apply(

                    lambda col:

                    col.astype(str).str.strip()

                )

                self.datasets.append({

                    "name": file,

                    "data": df

                })

                print(

                    f"Loaded : {file} ({len(df)} rows)"

                )

            except Exception as e:

                print(f"Failed : {file}")

                print(e)

        print("=" * 70)

        print(

            f"Datasets Loaded : {len(self.datasets)}"

        )

        print("=" * 70)

    # ============================================================
    # Normalize Text
    # ============================================================

    def normalize(self, text):

        if text is None:

            return ""

        text = str(text)

        text = text.lower()

        text = text.strip()

        # Remove prefixes

        remove_words = [

            "नगर पालिका परिषद",

            "नगर पालिका",

            "नगर पंचायत",

            "नगर निगम",

            "विकास खंड",

            "जिला पंचायत वार्ड",

            "वार्ड",

            "ward"

        ]

        for word in remove_words:

            text = text.replace(

                word.lower(),

                ""

            )

        # Remove leading numbers

        text = re.sub(

            r"^\d+\s*[-]?\s*",

            "",

            text

        )

        # Replace separators

        text = re.sub(

            r"[-_/]",

            " ",

            text

        )

        # Multiple spaces

        text = re.sub(

            r"\s+",

            " ",

            text

        )

        return text.strip()

    # ============================================================
    # Build Search Index
    # ============================================================

    def build_index(self):

        print("Building Search Index...")

        for dataset in self.datasets:

            df = dataset["data"]

            dataset_name = dataset["name"]

            for column in df.columns:

                if column not in self.column_weights:

                    continue

                for idx, value in enumerate(df[column]):

                    normalized = self.normalize(value)

                    if normalized == "":

                        continue

                    if normalized not in self.search_index:

                        self.search_index[normalized] = []

                    self.search_index[normalized].append({

                        "dataset": dataset_name,

                        "row": idx,

                        "column": column,

                        "weight": self.column_weights[column]

                    })

        print(

            f"Indexed {len(self.search_index)} unique locations."

        )
    # ============================================================
    # Exact Index Lookup
    # ============================================================

    def exact_lookup(self, query):

        query = self.normalize(query)

        return self.search_index.get(query, [])

    # ============================================================
    # Fuzzy Search
    # ============================================================

    def fuzzy_lookup(self, query, threshold=85):

        query = self.normalize(query)

        matches = []

        for key, candidates in self.search_index.items():

            score = fuzz.token_sort_ratio(query, key)

            if score >= threshold:

                for candidate in candidates:

                    candidate_copy = candidate.copy()

                    candidate_copy["similarity"] = score

                    matches.append(candidate_copy)

        return matches

    # ============================================================
    # Search
    # ============================================================

    def search(

        self,

        query,

        district_hint=None,

        assembly_hint=None

    ):

        query = self.normalize(query)

        candidates = []

        # ----------------------------------------
        # Exact Match
        # ----------------------------------------

        exact = self.exact_lookup(query)

        for item in exact:

            item = item.copy()

            item["method"] = "Exact"

            item["similarity"] = 100

            candidates.append(item)

        # ----------------------------------------
        # Fuzzy Match
        # ----------------------------------------

        if len(candidates) == 0:

            fuzzy = self.fuzzy_lookup(query)

            for item in fuzzy:

                item["method"] = "Fuzzy"

                candidates.append(item)

        if len(candidates) == 0:

            return []

        # ----------------------------------------
        # Build Rich Results
        # ----------------------------------------

        results = []

        for item in candidates:

            dataset = next(

                d

                for d in self.datasets

                if d["name"] == item["dataset"]

            )

            row = dataset["data"].iloc[item["row"]]

            result = {

                "matched": True,

                "dataset": item["dataset"],

                "matched_column": item["column"],

                "matched_value": row[item["column"]],

                "match_method": item["method"],

                "confidence": round(item["similarity"], 2),

                "score": item["similarity"] + item["weight"],

                "district": "",

                "assembly": "",

                "entity_type": "",

                "row": row

            }

            # -----------------------------
            # District
            # -----------------------------

            if "जिला" in row.index:

                result["district"] = row["जिला"]

            # -----------------------------
            # Assembly
            # -----------------------------

            if "विधानसभा" in row.index:

                result["assembly"] = row["विधानसभा"]

            # -----------------------------
            # Entity Type
            # -----------------------------

            filename = item["dataset"].lower()

            if "nagar nigam ward" in filename:

                result["entity_type"] = "Nagar Nigam Ward"

            elif "nagar palika" in filename:

                result["entity_type"] = "Nagar Palika"

            elif "nagar panchayat" in filename:

                result["entity_type"] = "Nagar Panchayat"

            elif "kshetra panchayat" in filename:

                result["entity_type"] = "Kshetra Panchayat"

            elif "jila panchayat" in filename:

                result["entity_type"] = "Jila Panchayat Ward"

            else:

                result["entity_type"] = "Unknown"

            # -----------------------------
            # Context Boost
            # -----------------------------

            if district_hint:

                if result["district"] == district_hint:

                    result["score"] += 20

            if assembly_hint:

                if assembly_hint == result["assembly"]:

                    result["score"] += 20

            results.append(result)

        # ----------------------------------------
        # Remove Duplicate Matches
        # ----------------------------------------

        unique = {}

        for result in results:

            key = (

                result["entity_type"],

                result["matched_value"],

                result["district"]

            )

            if key not in unique:

                unique[key] = result

            elif result["score"] > unique[key]["score"]:

                unique[key] = result

        results = list(unique.values())

        # ----------------------------------------
        # Sort by Score
        # ----------------------------------------

        results.sort(

            key=lambda x: x["score"],

            reverse=True

        )

        return results
    # ============================================================
    # Lookup (Return Best Match)
    # ============================================================

    def lookup(
        self,
        place,
        district_hint=None,
        assembly_hint=None,
        page_hint=None,
        top_n=5
    ):

        results = self.search(
            query=place,
            district_hint=district_hint,
            assembly_hint=assembly_hint
        )

        if len(results) == 0:
            return self.empty_result()

        best = results[0].copy()

        best["alternatives"] = results[:top_n]

        return best

    # ============================================================
    # Lookup Multiple Places
    # ============================================================

    def lookup_multiple(
        self,
        places,
        district_hint=None,
        assembly_hint=None
    ):

        if not places:
            return []

        output = []

        for place in places:

            result = self.lookup(
                place,
                district_hint=district_hint,
                assembly_hint=assembly_hint
            )

            if result["matched"]:
                output.append(result)

        return output

    # ============================================================
    # Empty Result
    # ============================================================

    def empty_result(self):

        return {

            "matched": False,

            "matched_value": "",

            "matched_column": "",

            "match_method": "",

            "confidence": 0,

            "score": 0,

            "district": "",

            "assembly": "",

            "entity_type": "",

            "dataset": "",

            "alternatives": []

        }

    # ============================================================
    # Pretty Print
    # ============================================================

    def print_result(self, result):

        print("=" * 80)

        if not result["matched"]:

            print("NO MATCH FOUND")

            print("=" * 80)

            return

        print(f"Matched        : {result['matched_value']}")
        print(f"Method         : {result['match_method']}")
        print(f"Confidence     : {result['confidence']}")
        print(f"Score          : {result['score']}")
        print(f"Dataset        : {result['dataset']}")
        print(f"Entity Type    : {result['entity_type']}")
        print(f"District       : {result['district']}")
        print(f"Assembly       : {result['assembly']}")

        print("-" * 80)
        print("Top Alternatives")
        print("-" * 80)

        for i, alt in enumerate(result["alternatives"], start=1):

            print(
                f"{i}. "
                f"{alt['matched_value']} | "
                f"{alt['entity_type']} | "
                f"{alt['confidence']} | "
                f"{alt['dataset']}"
            )

        print("=" * 80)

