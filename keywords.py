"""Keywords and search queries for Twitter monitoring."""

# Define search keywords organized by category
KEYWORDS = {
    "blockchain": [
        "new blockchain",
        "blockchain launch",
        "new L1",
        "new L2",
    ],
    "buildathons": [
        "buildathon",
        "build-a-thon",
        "online buildathon",
    ],
    "grants": [
        "dev grants",
        "developer grants",
        "research grants",
        "open source grants",
        "web3 grants",
        "blockchain grants",
    ],
    "hackathons": [
        "new hackathon",
        "global hackathon",
        "virtual hackathon",
        "online hackathon",
        "hackathon registration",
    ],
    "funding": [
        "raised funding",
        "seed round",
        "series A",
        "funding announcement",
        "new founder",
        "founder raised",
        "startup funding",
    ],
}


def get_all_keywords():
    """Get a flat list of all keywords."""
    all_keywords = []
    for category_keywords in KEYWORDS.values():
        all_keywords.extend(category_keywords)
    return all_keywords


def get_search_queries():
    """
    Generate Twitter search queries from keywords.
    Combines multiple keywords using OR operator.
    """
    queries = []
    
    # Create individual queries for each category
    for category, keywords in KEYWORDS.items():
        # Join keywords with OR for Twitter search
        query = " OR ".join(f'"{keyword}"' for keyword in keywords)
        queries.append({
            "category": category,
            "query": query
        })
    
    return queries


def categorize_tweet(tweet_text):
    """
    Categorize a tweet based on its content.
    Returns list of matching categories.
    """
    tweet_lower = tweet_text.lower()
    matching_categories = []
    
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in tweet_lower:
                if category not in matching_categories:
                    matching_categories.append(category)
                break
    
    return matching_categories
