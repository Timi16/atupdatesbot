# Twitter to Telegram Monitor Bot 🐦➡️📱

A Python bot that monitors Twitter for specific keywords related to blockchain, hackathons, grants, and funding announcements, then sends formatted notifications to Telegram.

## Features

- 🔍 **Smart Keyword Monitoring**: Tracks tweets about:
  - New blockchain launches (L1/L2)
  - Buildathons and hackathons
  - Developer and research grants
  - Startup funding announcements
  - New founders who raised money

- 📊 **Rich Telegram Notifications**: 
  - Formatted tweets with author info
  - Engagement metrics (likes, retweets, replies)
  - Category tags for easy filtering
  - Direct links to original tweets

- 🔄 **Continuous Monitoring**: Runs in the background and checks periodically
- 🚀 **No Duplicates**: Tracks last processed tweet to avoid sending duplicates
- ⚙️ **Configurable**: Easy environment-based configuration

## Project Structure

```
twitter-telegram-monitor/
├── main.py                  # Main bot orchestration
├── config.py                # Configuration management
├── keywords.py              # Keyword definitions and categorization
├── twitter_client.py        # Twitter API client
├── telegram_client.py       # Telegram bot client
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Twitter API access (Bearer Token required)
- Telegram Bot Token and Chat ID

### 2. Installation

Clone the repository and install dependencies:

```bash
cd twitter-telegram-monitor
pip install -r requirements.txt
```

### 3. Configuration

#### Twitter API Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Generate your API credentials
4. Copy your **Bearer Token** (this is the main credential needed)

#### Telegram Bot Setup

1. Create a bot:
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the **Bot Token** provided

2. Get your Chat ID:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your `chat_id` in the JSON response

#### Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here
   
   # Optional: Adjust check interval (default: 15 minutes)
   CHECK_INTERVAL_MINUTES=15
   MAX_TWEETS_PER_CHECK=50
   ```

## Usage

### Run Continuously (Recommended)

Start the bot to monitor Twitter continuously:

```bash
python main.py
```

The bot will:
- Check Twitter every 15 minutes (configurable)
- Send new tweets to your Telegram chat
- Run until you stop it (Ctrl+C)

### Run Once

To perform a single check and exit:

```bash
python main.py --once
```

This is useful for:
- Testing your setup
- Running as a cron job
- Manual checks

### Running in Background

#### Windows (PowerShell)
```powershell
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

#### Linux/Mac
```bash
nohup python main.py &
```

Or use a process manager like `systemd`, `pm2`, or `supervisor`.

## Monitored Keywords

The bot searches for tweets containing these keywords (organized by category):

### 🔗 Blockchain
- New blockchain
- Blockchain launch
- New L1/L2

### 🏗️ Buildathons
- Buildathon
- Build-a-thon
- Online buildathon

### 💰 Grants
- Dev grants
- Developer grants
- Research grants
- Open source grants
- Web3 grants
- Blockchain grants

### 🎯 Hackathons
- New hackathon
- Global hackathon
- Virtual hackathon
- Online hackathon
- Hackathon registration

### 💼 Funding
- Raised funding
- Seed round
- Series A
- Funding announcement
- New founder
- Founder raised
- Startup funding

## Customization

### Modify Keywords

Edit `keywords.py` to add or remove keywords:

```python
KEYWORDS = {
    "blockchain": [
        "new blockchain",
        "your custom keyword",
    ],
    "your_category": [
        "keyword1",
        "keyword2",
    ],
}
```

### Adjust Check Interval

Modify the `CHECK_INTERVAL_MINUTES` in your `.env` file:

```env
# Check every 30 minutes
CHECK_INTERVAL_MINUTES=30
```

### Change Notification Format

Edit `telegram_client.py` in the `format_tweet_message()` method to customize how tweets appear in Telegram.

## Logs

The bot creates a `bot.log` file with detailed information about:
- Tweets found and sent
- API errors
- Configuration issues

Check this file if something isn't working as expected.

## Troubleshooting

### No tweets being sent

1. **Check your Twitter API credentials**: Ensure your Bearer Token is valid
2. **Verify Telegram credentials**: Test by sending a message manually
3. **Check the keywords**: The keywords might be too specific
4. **Review logs**: Check `bot.log` for error messages

### "Missing required configuration" error

Make sure your `.env` file exists and contains all required values:
- `TWITTER_BEARER_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Rate limit errors

Twitter API has rate limits. The bot handles this automatically, but if you're hitting limits:
- Increase `CHECK_INTERVAL_MINUTES`
- Reduce `MAX_TWEETS_PER_CHECK`
- Use more specific keywords

## API Limits

### Twitter API v2 (Free Tier)
- 500,000 tweets/month
- Recent tweets only (last 7 days)
- Rate limit: 450 requests per 15 minutes

### Telegram Bot API
- 30 messages per second
- No monthly limits

## Security Notes

⚠️ **Important**: 
- Never commit your `.env` file to version control
- Keep your API tokens secure
- The `.gitignore` file is configured to exclude sensitive files

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Support

If you encounter issues:
1. Check the logs (`bot.log`)
2. Review this README
3. Verify your API credentials
4. Check that all dependencies are installed

## Acknowledgments

- Built with [Tweepy](https://www.tweepy.org/) for Twitter API
- Uses [python-telegram-bot](https://python-telegram-bot.org/) for Telegram integration
