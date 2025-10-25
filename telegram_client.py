"""Telegram bot client for sending notifications."""
import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from config import Config

logger = logging.getLogger(__name__)


class TelegramClient:
    """Client for sending messages via Telegram bot."""
    
    def __init__(self):
        """Initialize Telegram bot client."""
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.chat_id = Config.TELEGRAM_CHAT_ID
        logger.info("Telegram client initialized")
    
    async def send_message(self, message, parse_mode=ParseMode.HTML):
        """
        Send a message to the configured Telegram chat.
        
        Args:
            message: Message text to send
            parse_mode: Parse mode for message formatting (HTML or Markdown)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=False
            )
            logger.info("Message sent to Telegram")
            return True
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def format_tweet_message(self, tweet):
        """
        Format a tweet into a nice Telegram message.
        
        Args:
            tweet: Tweet dictionary with metadata
            
        Returns:
            Formatted HTML message string
        """
        # Build category tags
        categories = tweet.get('categories', [])
        category_tags = ' '.join([f"#{cat}" for cat in categories]) if categories else ""
        
        # Verified badge
        verified = "✅" if tweet['author'].get('verified') else ""
        
        # Format metrics
        metrics = tweet.get('metrics', {})
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        # Build message
        message = f"""🐦 <b>New Tweet Found!</b>

<b>{tweet['author']['name']}</b> {verified} @{tweet['author']['username']}

{tweet['text']}

📊 <i>{likes} likes • {retweets} retweets • {replies} replies</i>

🔗 <a href="{tweet['url']}">View Tweet</a>

{category_tags}
"""
        return message
    
    async def send_tweet(self, tweet):
        """
        Send a formatted tweet message to Telegram.
        
        Args:
            tweet: Tweet dictionary with metadata
            
        Returns:
            True if sent successfully, False otherwise
        """
        message = self.format_tweet_message(tweet)
        return await self.send_message(message)
    
    async def send_tweets_batch(self, tweets):
        """
        Send multiple tweets to Telegram.
        
        Args:
            tweets: List of tweet dictionaries
            
        Returns:
            Number of tweets successfully sent
        """
        success_count = 0
        
        for tweet in tweets:
            if await self.send_tweet(tweet):
                success_count += 1
        
        logger.info(f"Sent {success_count}/{len(tweets)} tweets to Telegram")
        return success_count
    
    async def send_summary(self, tweet_count, categories_found):
        """
        Send a summary message about the monitoring session.
        
        Args:
            tweet_count: Number of tweets found
            categories_found: Dictionary of category counts
        """
        if tweet_count == 0:
            message = "🔍 <b>Monitoring Update</b>\n\nNo new tweets found in this check."
        else:
            category_summary = "\n".join([
                f"  • {cat}: {count}" 
                for cat, count in categories_found.items()
            ])
            
            message = f"""📈 <b>Monitoring Summary</b>

Found <b>{tweet_count}</b> new tweet(s)

<b>Categories:</b>
{category_summary}
"""
        
        await self.send_message(message)
