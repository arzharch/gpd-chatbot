REAL_ESTATE_KEYWORDS = {
    "apartment", "villa", "land", "plot", "property",
    "bed", "bhk", "budget", "price", "location", "buy", "sell", "rent"
}

def is_real_estate_topic(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in REAL_ESTATE_KEYWORDS)