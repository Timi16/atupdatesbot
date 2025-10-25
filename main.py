"""Main bot script for Twitter-Telegram monitoring."""
import asyncio
import logging
import os
import sys
from datetime import datetime
from collections import Counter

from config import Config
from twitter_client import TwitterClient
from telegram_client import TelegramClient
from keywords import get_search_queries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# File to store last processed tweet ID
LAST_TWEET_ID_FILE = 'last_tweet_id.txt'


def load_last_tweet_id():
    """Load the last processed tweet ID from file."""
    if os.path.exists(LAST_TWEET_ID_FILE):
        try:
            with open(LAST_TWEET_ID_FILE, 'r') as f:
                tweet_id = f.read().strip()
                if tweet_id:
                    logger.info(f"Loaded last tweet ID: {tweet_id}")
                    return tweet_id
        except Exception as e:
            logger.error(f"Error loading last tweet ID: {e}")
    return None


def save_last_tweet_id(tweet_id):
    """Save the last processed tweet ID to file."""
    try:
        with open(LAST_TWEET_ID_FILE, 'w') as f:
            f.write(str(tweet_id))
        logger.info(f"Saved last tweet ID: {tweet_id}")
    except Exception as e:
        logger.error(f"Error saving last tweet ID: {e}")


async def check_and_notify():
    """Check Twitter for new tweets and send to Telegram."""
    logger.info("Starting tweet check...")
    
    # Initialize clients
    twitter_client = TwitterClient()
    telegram_client = TelegramClient()
    
    # Load last processed tweet ID
    last_tweet_id = load_last_tweet_id()
    
    # Get search queries
    queries = get_search_queries()
    logger.info(f"Searching {len(queries)} categories")
    
    # Search for tweets
    tweets = twitter_client.search_multiple_queries(
        queries=queries,
        max_results_per_query=20,
        since_id=last_tweet_id
    )
    
    if not tweets:
        logger.info("No new tweets found")
        return
    
    logger.info(f"Found {len(tweets)} new tweets")
    
    # Count categories
    category_counter = Counter()
    for tweet in tweets:
        for category in tweet.get('categories', []):
            category_counter[category] += 1
    
    # Send tweets to Telegram
    sent_count = await telegram_client.send_tweets_batch(tweets)
    
    # Send summary
    await telegram_client.send_summary(len(tweets), dict(category_counter))
    
    # Save the ID of the newest tweet
    if tweets:
        newest_tweet_id = max(tweet['id'] for tweet in tweets)
        save_last_tweet_id(newest_tweet_id)
    
    logger.info(f"Check complete. Sent {sent_count}/{len(tweets)} tweets")


async def run_continuous():
    """Run the bot continuously with periodic checks."""
    logger.info("Starting continuous monitoring mode")
    logger.info(f"Check interval: {Config.CHECK_INTERVAL_MINUTES} minutes")
    
    # Send startup notification
    telegram_client = TelegramClient()
    await telegram_client.send_message(
        "🤖 <b>Twitter Monitor Bot Started!</b>\n\n"
        f"Monitoring for: blockchain, buildathons, grants, hackathons, and funding news\n"
        f"Check interval: {Config.CHECK_INTERVAL_MINUTES} minutes"
    )
    
    while True:
        try:
            await check_and_notify()
        except Exception as e:
            logger.error(f"Error in check cycle: {e}", exc_info=True)
        
        # Wait for next check
        logger.info(f"Waiting {Config.CHECK_INTERVAL_MINUTES} minutes until next check...")
        await asyncio.sleep(Config.CHECK_INTERVAL_MINUTES * 60)


async def run_once():
    """Run a single check and exit."""
    logger.info("Running single check mode")
    try:
        await check_and_notify()
        logger.info("Single check completed successfully")
    except Exception as e:
        logger.error(f"Error in single check: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == '--once':
            # Run once and exit
            asyncio.run(run_once())
        else:
            # Run continuously
            asyncio.run(run_continuous())
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
