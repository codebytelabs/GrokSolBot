from .bot import TelegramBot
from .alerts import AlertManager
from .client import TelegramClient

__version__ = "0.1.0"

__all__ = [
    "TelegramBot",
    "AlertManager",
    "TelegramClient"
]

# Example usage:
"""
from telegram import TelegramBot, AlertManager

# Initialize bot
bot = TelegramBot(token="YOUR_BOT_TOKEN")

# Initialize alert manager
alert_manager = AlertManager(bot)

# Subscribe chat to alerts
alert_manager.subscribe_to_alerts(
    chat_id=123456789,
    alert_types=["mentions", "launches", "trades"]
)

# Start bot
await bot.start()

# Send alerts
await alert_manager.send_token_mention_alert(
    symbol="BONK",
    mentions=10,
    trend_strength=0.8,
    latest_tweet="BONK is mooning! 🚀"
)
"""
