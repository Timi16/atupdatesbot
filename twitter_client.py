"""Twitter API client for searching and filtering tweets."""
import tweepy
import logging
from datetime import datetime
from config import Config
from keywords import categorize_tweet

logger = logging.getLogger(__name__)


class TwitterClient:
    """Client for interacting with Twitter API."""
    
    def __init__(self):
        """Initialize Twitter API client with Bearer Token authentication."""
        self.client = tweepy.Client(
            bearer_token=Config.TWITTER_BEARER_TOKEN,
            wait_on_rate_limit=True
        )
        logger.info("Twitter client initialized")
    
    def search_tweets(self, query, max_results=50, since_id=None):
        """
        Search for tweets matching the given query.
        
        Args:
            query: Search query string
            max_results: Maximum number of tweets to return (10-100)
            since_id: Returns results with Tweet ID greater than this
            
        Returns:
            List of tweets with metadata
        """
        try:
            # Tweet fields to include in response
            tweet_fields = ['created_at', 'author_id', 'public_metrics', 'entities']
            user_fields = ['name', 'username', 'verified']
            expansions = ['author_id']
            
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                expansions=expansions,
                since_id=since_id
            )
            
            if not response.data:
                logger.info(f"No tweets found for query: {query}")
                return []
            
            # Create user lookup dict
            users = {}
            if response.includes and 'users' in response.includes:
                users = {user.id: user for user in response.includes['users']}
            
            # Format tweets with user information
            tweets = []
            for tweet in response.data:
                author = users.get(tweet.author_id)
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author': {
                        'name': author.name if author else 'Unknown',
                        'username': author.username if author else 'unknown',
                        'verified': author.verified if author else False
                    },
                    'metrics': tweet.public_metrics,
                    'url': f"https://twitter.com/{author.username}/status/{tweet.id}" if author else None,
                    'categories': categorize_tweet(tweet.text)
                })
            
            logger.info(f"Found {len(tweets)} tweets for query: {query}")
            return tweets
            
        except tweepy.TweepyException as e:
            logger.error(f"Error searching tweets: {e}")
            return []
    
    async def search_multiple_queries_async(self, queries, max_results_per_query=20, since_id=None, callback=None):
        """
        Search multiple queries and combine results (async version with callback support).
        
        Args:
            queries: List of query dictionaries with 'category' and 'query' keys
            max_results_per_query: Max results per individual query
            since_id: Returns results with Tweet ID greater than this
            callback: Optional async callback function to call with tweets after each query
            
        Returns:
            List of tweets from all queries (deduplicated)
        """
        all_tweets = {}  # Use dict to deduplicate by tweet ID
        
        for query_info in queries:
            category = query_info['category']
            query = query_info['query']
            
            logger.info(f"Searching {category}: {query}")
            tweets = self.search_tweets(query, max_results_per_query, since_id)
            
            # Collect new tweets
            new_tweets = []
            for tweet in tweets:
                if tweet['id'] not in all_tweets:
                    all_tweets[tweet['id']] = tweet
                    new_tweets.append(tweet)
            
            # Call callback with new tweets from this category if provided
            if callback and new_tweets:
                await callback(new_tweets, category)
        
        # Sort by creation time (newest first)
        sorted_tweets = sorted(
            all_tweets.values(),
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        logger.info(f"Total unique tweets found: {len(sorted_tweets)}")
        return sorted_tweets
    
    def search_multiple_queries(self, queries, max_results_per_query=20, since_id=None):
        """
        Search multiple queries and combine results.
        
        Args:
            queries: List of query dictionaries with 'category' and 'query' keys
            max_results_per_query: Max results per individual query
            since_id: Returns results with Tweet ID greater than this
            
        Returns:
            List of tweets from all queries (deduplicated)
        """
        all_tweets = {}  # Use dict to deduplicate by tweet ID
        
        for query_info in queries:
            category = query_info['category']
            query = query_info['query']
            
            logger.info(f"Searching {category}: {query}")
            tweets = self.search_tweets(query, max_results_per_query, since_id)
            
            for tweet in tweets:
                if tweet['id'] not in all_tweets:
                    all_tweets[tweet['id']] = tweet
        
        # Sort by creation time (newest first)
        sorted_tweets = sorted(
            all_tweets.values(),
            key=lambda x: x['created_at'],
            reverse=True
        )
        
        logger.info(f"Total unique tweets found: {len(sorted_tweets)}")
        return sorted_tweets
