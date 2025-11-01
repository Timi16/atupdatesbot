"""Optimized keywords and search queries for Twitter monitoring.

Focus: Grants, new blockchains, investment opportunities, and funding.
Uses semantic variations and common Twitter language patterns.
"""

# Define search keywords organized by category with semantic variations
KEYWORDS = {
    "blockchain_launches": [
        # Direct launches
        "new blockchain",
        "blockchain launch",
        "launching blockchain",
        "new L1",
        "new L2",
        "layer 1 launch",
        "layer 2 launch",
        # Testnet/Mainnet indicators
        "mainnet launch",
        "testnet live",
        "mainnet live",
        "chain goes live",
        "network launch",
        # Announcements
        "introducing new chain",
        "announcing blockchain",
        "built on new chain",
    ],
    
    "grants_programs": [
        # Developer grants
        "dev grants",
        "developer grants",
        "grants program",
        "grant applications open",
        "accepting grant applications",
        "apply for grant",
        "grant opportunity",
        # Specific amounts/types
        "grant funding available",
        "ecosystem grants",
        "research grants",
        "open source grants",
        "web3 grants",
        "blockchain grants",
        "DeFi grants",
        "dApp grants",
        # Grant rounds
        "grants round",
        "new grants program",
        "grants initiative",
        "developer funding",
        # Common patterns
        "building on? apply",
        "get funded",
        "funding for developers",
    ],
    
    "funding_rounds": [
        # Round types
        "raised funding",
        "raises $",
        "raised $",
        "seed round",
        "pre-seed",
        "series A",
        "series B",
        "funding round",
        # Announcements
        "funding announcement",
        "announced funding",
        "closed funding",
        "secured funding",
        "completed raise",
        # Amount indicators
        "million raise",
        "million funding",
        "valuation",
        # Investor signals
        "led by",
        "participated by",
        "invested in",
        "backed by",
    ],
    
    "investment_opportunities": [
        # Direct asks
        "seeking investment",
        "looking for investors",
        "raising capital",
        "fundraising",
        "investor deck",
        # Pitching
        "pitching to investors",
        "investor call",
        "demo day",
        "pitch deck",
        # Accelerator/VC signals
        "YC application",
        "accepted into accelerator",
        "incubator program",
        "VC interest",
        # Token/equity
        "token sale",
        "private sale",
        "equity round",
        "looking for angels",
    ],
    
    "hackathons_buildathons": [
        # Hackathons
        "hackathon announcement",
        "hackathon registration",
        "hackathon registration open",
        "new hackathon",
        "global hackathon",
        "virtual hackathon",
        "online hackathon",
        "hackathon winner",
        "hackathon prize",
        # Buildathons
        "buildathon",
        "build-a-thon",
        "online buildathon",
        # Bounties
        "bounty program",
        "bug bounty",
        "developer bounty",
        # Competitions
        "coding competition",
        "dev competition",
        "build and win",
    ],
    
    "ecosystem_growth": [
        # New projects/protocols
        "building on",
        "deployed on",
        "launching on",
        "new protocol",
        "new DeFi",
        "new dApp",
        # Integrations
        "integration with",
        "partners with",
        "partnership announcement",
        # Community
        "developer community",
        "ecosystem fund",
        "ecosystem growth",
        "TVL milestone",
        "user milestone",
    ],
    
    "founder_signals": [
        # Founder announcements
        "new founder",
        "founded by",
        "co-founder",
        "building in public",
        "launched my startup",
        "quit my job to build",
        # Fundraising signals
        "founder raised",
        "we raised",
        "excited to announce we raised",
        "closed our round",
        # Team building
        "hiring founding",
        "looking for co-founder",
        "join our team",
    ],
}


def get_all_keywords():
    """Get a flat list of all keywords."""
    all_keywords = []
    for category_keywords in KEYWORDS.values():
        all_keywords.extend(category_keywords)
    return all_keywords


def get_search_queries(combine_categories=False):
    """
    Generate Twitter search queries from keywords.
    
    Args:
        combine_categories: If True, creates fewer but broader queries.
                          If False, creates separate queries per category.
    
    Returns:
        List of query dictionaries with category and query string.
    """
    queries = []
    
    if combine_categories:
        # High-priority combined queries for better signal
        priority_queries = [
            {
                "category": "grants_and_funding",
                "query": '("grants program" OR "developer grants" OR "grant applications" OR "ecosystem grants") -job -hiring'
            },
            {
                "category": "blockchain_launches",
                "query": '("mainnet launch" OR "new L1" OR "new L2" OR "chain launch" OR "network launch") -testnet'
            },
            {
                "category": "fundraising",
                "query": '("raised $" OR "seed round" OR "series A" OR "closed funding" OR "secured funding") -job'
            },
            {
                "category": "investment_seeking",
                "query": '("seeking investment" OR "looking for investors" OR "raising capital" OR "investor deck")'
            }
        ]
        queries.extend(priority_queries)
    else:
        # Create individual queries for each category
        for category, keywords in KEYWORDS.items():
            # Optimize query structure for Twitter API
            # Use exact phrase matching for multi-word terms
            query_parts = [f'"{kw}"' if ' ' in kw else kw for kw in keywords]
            query = " OR ".join(query_parts)
            
            # Add filters to reduce noise
            filters = ""
            if category in ["grants_programs", "funding_rounds"]:
                filters = " -job -hiring"  # Exclude job postings
            elif category == "blockchain_launches":
                filters = " lang:en"  # English only for launches
            
            queries.append({
                "category": category,
                "query": query + filters,
                "priority": get_category_priority(category)
            })
    
    # Sort by priority
    queries.sort(key=lambda x: x.get("priority", 5), reverse=True)
    return queries


def get_category_priority(category):
    """Assign priority scores to categories (higher = more important)."""
    priority_map = {
        "grants_programs": 10,
        "funding_rounds": 9,
        "blockchain_launches": 8,
        "investment_opportunities": 7,
        "founder_signals": 6,
        "ecosystem_growth": 5,
        "hackathons_buildathons": 4,
    }
    return priority_map.get(category, 3)


def categorize_tweet(tweet_text):
    """
    Categorize a tweet based on its content using semantic matching.
    Returns list of matching categories sorted by relevance.
    """
    tweet_lower = tweet_text.lower()
    category_scores = {}
    
    for category, keywords in KEYWORDS.items():
        matches = 0
        for keyword in keywords:
            if keyword.lower() in tweet_lower:
                matches += 1
        
        if matches > 0:
            # Weight by priority and number of matches
            priority = get_category_priority(category)
            category_scores[category] = matches * priority
    
    # Sort categories by score
    sorted_categories = sorted(
        category_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [cat for cat, score in sorted_categories]


def get_advanced_filters():
    """
    Get advanced Twitter search filters to improve signal quality.
    These can be appended to queries.
    """
    return {
        "verified_only": " filter:verified",
        "min_engagement": " min_faves:10",
        "exclude_retweets": " -filter:retweets",
        "recent_only": " filter:recent",
        "links_only": " filter:links",  # Good for official announcements
        "exclude_noise": " -job -hiring -giveaway -airdrop",
    }


def build_optimized_query(categories, use_filters=True):
    """
    Build a single optimized query combining multiple categories.
    
    Args:
        categories: List of category names to include
        use_filters: Whether to add quality filters
    
    Returns:
        Optimized Twitter search query string
    """
    query_parts = []
    
    for category in categories:
        if category in KEYWORDS:
            keywords = KEYWORDS[category]
            # Take top 5 most specific keywords per category
            top_keywords = keywords[:5]
            category_query = " OR ".join(f'"{kw}"' for kw in top_keywords)
            query_parts.append(f"({category_query})")
    
    base_query = " OR ".join(query_parts)
    
    if use_filters:
        filters = get_advanced_filters()
        # Add most important filters
        base_query += filters["exclude_noise"]
        base_query += " filter:links"  # Prefer tweets with links (more official)
    
    return base_query


# Example usage patterns
def get_recommended_queries():
    """Get pre-configured recommended queries for different use cases."""
    return {
        "grants_hunter": build_optimized_query(
            ["grants_programs", "ecosystem_growth"],
            use_filters=True
        ),
        "blockchain_scout": build_optimized_query(
            ["blockchain_launches", "ecosystem_growth"],
            use_filters=True
        ),
        "funding_tracker": build_optimized_query(
            ["funding_rounds", "investment_opportunities", "founder_signals"],
            use_filters=True
        ),
        "all_opportunities": build_optimized_query(
            ["grants_programs", "blockchain_launches", "funding_rounds"],
            use_filters=True
        ),
    }
