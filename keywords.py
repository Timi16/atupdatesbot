"""
Hackathon-focused Twitter keyword & query builder

Purpose:
- Provide optimized keywords and Twitter/X search queries focused solely on hackathons,
  buildathons, bounties and related developer competitions.
- Includes utilities for generating queries, filtering noise, and simple tweet categorization.
"""

# -----------------------
# Keywords (hackathon-only)
# -----------------------
KEYWORDS = {
    "hackathons_buildathons": [
        # Core terms
        "hackathon",
        "buildathon",
        "build-a-thon",
        "codefest",
        "coding competition",
        "developer challenge",
        "dev competition",
        "programming contest",

        # Announcements & registration
        "hackathon announcement",
        "hackathon alert",
        "hackathon is live",
        "hackathon is here",
        "hackathon registration open",
        "register for hackathon",
        "hackathon kickoff",
        "hackathon starts",
        "new hackathon",
        "upcoming hackathon",
        "global hackathon",
        "virtual hackathon",
        "online hackathon",
        "college hackathon",
        "university hackathon",

        # Prizes / winners / bounties
        "hackathon prize",
        "hackathon winners",
        "bounty program",
        "bug bounty",
        "developer bounty",
        "win prizes",
        "build and win",
        "hackathon prize pool",

        # Participation signals
        "join the hackathon",
        "building for hackathon",
        "submitting my hackathon project",
        "hackathon submission",
        "hackathon project",
        "hackathon demo",
        "hackathon demo day",
        "hackathon team",
        "hackathon devs",
        "hackathon builders",

        # Domain-specific variants
        "web3 hackathon",
        "blockchain hackathon",
        "crypto hackathon",
        "AI hackathon",
        "ML hackathon",
        "DeFi hackathon",
        "startup hackathon",
        "open source hackathon",
        "student hackathon",
        "college hackathon",

        # Alternate spellings / hyphenations
        "build-a-thon",
        "build a thon",
        "hack-a-thon",
    ]
}

# -----------------------
# Utilities
# -----------------------
def get_all_keywords():
    """Return a flat list of all hackathon keywords."""
    all_keywords = []
    for category_keywords in KEYWORDS.values():
        all_keywords.extend(category_keywords)
    return all_keywords


def get_category_priority(category):
    """
    Assign priority scores to categories (higher = more important).
    There's only one category here but keep structure for compatibility.
    """
    priority_map = {
        "hackathons_buildathons": 10,
    }
    return priority_map.get(category, 3)


def get_advanced_filters():
    """
    Advanced Twitter search filters that can be appended to queries to reduce noise.
    Tweak these depending on whether you're using the Twitter API v2 query language,
    the web UI, or a third-party stream tool.
    """
    return {
        "verified_only": " filter:verified",
        "min_engagement": " min_faves:10",     # requires v2-like syntax
        "exclude_retweets": " -filter:retweets",
        "recent_only": " filter:recent",
        "links_only": " filter:links",
        "exclude_noise": " -job -hiring -airdrop -giveaway -NFTdrop",
    }


def build_optimized_query(categories, use_filters=True, top_n_per_category=6):
    """
    Build a single optimized query combining specified categories.

    Args:
        categories: list of category names (must exist in KEYWORDS)
        use_filters: whether to append advanced filters
        top_n_per_category: how many top keywords from each category to include

    Returns:
        query string suitable for Twitter/X search (tweak filters to your API/version)
    """
    query_parts = []

    for category in categories:
        if category in KEYWORDS:
            keywords = KEYWORDS[category]
            # pick the most specific keywords (first N)
            top_keywords = keywords[:top_n_per_category]
            # quote multi-word keywords
            category_query = " OR ".join(f'"{kw}"' if " " in kw else kw for kw in top_keywords)
            query_parts.append(f"({category_query})")

    base_query = " OR ".join(query_parts)

    if use_filters:
        filters = get_advanced_filters()
        # conservative default: remove common noise and prefer linked announcements
        base_query += filters["exclude_noise"]
        base_query += " " + filters["exclude_retweets"]
        base_query += " " + filters["links_only"]

    return base_query.strip()


def get_search_queries(combine_categories=False):
    """
    Generate search queries from the hackathon keywords.

    Args:
        combine_categories: If True, returns a single combined query.
                            If False, returns per-category queries (still only one category here).

    Returns:
        List of dicts: { "category": str, "query": str, "priority": int }
    """
    queries = []

    if combine_categories:
        query = build_optimized_query(list(KEYWORDS.keys()), use_filters=True)
        queries.append({
            "category": "hackathons_combined",
            "query": query,
            "priority": max(get_category_priority(c) for c in KEYWORDS.keys())
        })
    else:
        for category, keywords in KEYWORDS.items():
            # exact-phrase for multi-word terms
            query_parts = [f'"{kw}"' if ' ' in kw else kw for kw in keywords]
            query = " OR ".join(query_parts)
            # append a basic noise exclusion filter
            query += " -job -hiring -airdrop -giveaway -retweet"
            queries.append({
                "category": category,
                "query": query,
                "priority": get_category_priority(category)
            })

    # sort by priority descending
    queries.sort(key=lambda x: x.get("priority", 0), reverse=True)
    return queries


def categorize_tweet(tweet_text):
    """
    Categorize a tweet by matching hackathon keywords.
    Returns list of matching categories sorted by match-relevance.

    Simple substring matching is used for speed; for better accuracy consider
    tokenization, stemming, or fuzzy/regex matching.
    """
    tweet_lower = tweet_text.lower()
    category_scores = {}

    for category, keywords in KEYWORDS.items():
        matches = 0
        for keyword in keywords:
            if keyword.lower() in tweet_lower:
                matches += 1

        if matches > 0:
            priority = get_category_priority(category)
            category_scores[category] = matches * priority

    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return [cat for cat, score in sorted_categories]


def get_recommended_queries():
    """
    Pre-configured queries for typical hackathon monitoring use-cases.
    """
    return {
        "hackathon_monitor": build_optimized_query(
            ["hackathons_buildathons"],
            use_filters=True,
            top_n_per_category=10
        ),
        "hackathon_quick": build_optimized_query(
            ["hackathons_buildathons"],
            use_filters=False,
            top_n_per_category=6
        ),
    }
