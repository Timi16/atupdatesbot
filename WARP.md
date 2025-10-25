# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A Python bot that monitors Twitter for blockchain, hackathons, grants, and funding announcements, forwarding formatted notifications to Telegram. Built with Tweepy (Twitter API v2) and python-telegram-bot (async).

## Development Commands

### Setup
```powershell
# Install dependencies
pip install -r requirements.txt

# Configure environment (copy .env.example to .env and fill in credentials)
Copy-Item .env.example .env
```

### Running the Bot
```powershell
# Run continuously (checks every CHECK_INTERVAL_MINUTES)
python main.py

# Run once and exit (useful for testing)
python main.py --once

# Background execution
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

### Testing
There are no automated tests in this codebase. Test manually using `python main.py --once` after changes.

### Logs
- Application logs to `bot.log` (file) and stdout (console)
- Last processed tweet ID is stored in `last_tweet_id.txt` to prevent duplicates

## Architecture

### Core Design Pattern

**Orchestrator + Client Architecture**: `main.py` orchestrates the monitoring loop while delegating to specialized client classes:
- `TwitterClient`: Handles Twitter API searches
- `TelegramClient`: Handles Telegram message formatting and sending

### Key Components

**main.py** - Entry point and orchestration
- `check_and_notify()`: Core function that searches Twitter and sends to Telegram
- `run_continuous()`: Infinite loop with configurable interval (default: 15 minutes)
- `run_once()`: Single execution mode (for testing/cron)
- Tweet ID persistence: Stores last processed tweet ID to avoid duplicates

**twitter_client.py** - Twitter API integration
- Uses Bearer Token authentication (Twitter API v2)
- `search_tweets()`: Single query search with metadata (author, metrics, timestamps)
- `search_multiple_queries()`: Deduplicates tweets across multiple category queries
- Automatic rate limit handling via `wait_on_rate_limit=True`
- Returns enriched tweet objects with categorization

**telegram_client.py** - Telegram bot integration
- Async-only interface (all methods are `async`)
- `format_tweet_message()`: Converts tweets to HTML-formatted messages with metrics and category tags
- `send_tweets_batch()`: Sends multiple tweets sequentially
- `send_summary()`: Sends monitoring summary with category breakdown

**keywords.py** - Keyword management and categorization
- `KEYWORDS`: Dictionary mapping categories to search terms (blockchain, buildathons, grants, hackathons, funding)
- `get_search_queries()`: Generates Twitter OR queries per category
- `categorize_tweet()`: Matches tweet text against keywords to apply category tags

**config.py** - Configuration management
- Loads from `.env` using python-dotenv
- `Config.validate()`: Ensures required credentials are present
- Required: `TWITTER_BEARER_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

### Data Flow

1. `main.py` loads last processed tweet ID from disk
2. `get_search_queries()` generates category-based queries from `keywords.py`
3. `TwitterClient.search_multiple_queries()` executes searches (dedups by tweet ID)
4. Each tweet is categorized via `categorize_tweet()`
5. `TelegramClient.send_tweets_batch()` sends formatted messages
6. `TelegramClient.send_summary()` sends category breakdown
7. Highest tweet ID is persisted to `last_tweet_id.txt`

### Important Implementation Details

**Tweet Deduplication**: Uses dict with tweet ID as key in `search_multiple_queries()` to deduplicate across category queries.

**Async/Await**: Telegram operations are async; Twitter operations are sync. `main.py` uses `asyncio.run()` to bridge.

**Stateless Operation**: No database. State is a single file (`last_tweet_id.txt`) with the last processed tweet ID.

**Error Handling**: Try-except blocks in main loop prevent crashes; errors logged to `bot.log`.

## Configuration

### Required Environment Variables
- `TWITTER_BEARER_TOKEN`: Twitter API v2 Bearer Token (not API key/secret)
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Numeric chat ID (get from bot's getUpdates endpoint)

### Optional Environment Variables
- `CHECK_INTERVAL_MINUTES`: Minutes between checks (default: 15)
- `MAX_TWEETS_PER_CHECK`: Max tweets per query (default: 50, API max: 100)

## Adding New Features

### Adding Keywords
Edit `keywords.py` KEYWORDS dict. Add a new category or extend existing lists. No code changes needed elsewhere due to dynamic categorization.

### Changing Notification Format
Modify `TelegramClient.format_tweet_message()` in `telegram_client.py`. Uses HTML parse mode (supports `<b>`, `<i>`, `<a>`).

### Adding Filters
Add filtering logic in `TwitterClient.search_tweets()` after results are retrieved, or modify query construction in `keywords.py`.

## API Constraints

### Twitter API v2 (Free Tier)
- 500,000 tweets/month limit
- Recent tweets only (last 7 days)
- Rate limit: 450 requests per 15 minutes (handled automatically by Tweepy)

### Telegram Bot API
- 30 messages/second limit (not enforced in code; sequential sending is safe for typical volumes)
- No monthly limits

## Dependencies

- `tweepy==4.14.0`: Twitter API v2 client
- `python-telegram-bot==20.7`: Async Telegram bot framework
- `python-dotenv==1.0.0`: Environment variable loading
- `requests==2.31.0`: HTTP library (dependency of tweepy)
