from knowledge_base.political_lookup import PoliticalLookup

lookup = PoliticalLookup()

tests = [

    "अभिरामदास",

    "अमरोहा",

    "गजरौला",

    "हसनपुर"

]

for place in tests:

    print("="*80)

    result = lookup.lookup(place)

    print(result)