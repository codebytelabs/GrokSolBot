import logging
from typing import List, Dict, Any, Optional
from .bot import TelegramBot

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, bot: TelegramBot):
        self.bot = bot
        self.alert_channels: Dict[str, List[int]] = {
            "mentions": [],    # Chat IDs for token mention alerts
            "launches": [],    # Chat IDs for new token launch alerts
            "trades": [],      # Chat IDs for trade execution alerts
            "system": [],      # Chat IDs for system status alerts
        }

    async def send_token_mention_alert(
        self,
        symbol: str,
        mentions: int,
        trend_strength: float,
        latest_tweet: str
    ):
        """
        Send alert for token mentions on Twitter
        """
        message = (
            f"🔔 Token Mention Alert\n\n"
            f"Symbol: {symbol}\n"
            f"Mentions: {mentions}\n"
            f"Trend Strength: {trend_strength:.2f}\n"
            f"Latest Tweet: {latest_tweet}"
        )
        
        await self._broadcast_alert(message, "mentions")

    async def send_token_launch_alert(
        self,
        symbol: str,
        initial_price: float,
        initial_liquidity: float,
        source: str,
        safety_score: float
    ):
        """
        Send alert for new token launches
        """
        message = (
            f"🚀 New Token Launch\n\n"
            f"Symbol: {symbol}\n"
            f"Initial Price: ${initial_price:.6f}\n"
            f"Initial Liquidity: ${initial_liquidity:,.2f}\n"
            f"Source: {source}\n"
            f"Safety Score: {safety_score:.1f}/10"
        )
        
        await self._broadcast_alert(message, "launches")

    async def send_trade_alert(
        self,
        symbol: str,
        action: str,
        amount: float,
        price: float,
        pl_percentage: Optional[float] = None
    ):
        """
        Send alert for trade execution
        """
        message = (
            f"💰 Trade Alert\n\n"
            f"Symbol: {symbol}\n"
            f"Action: {action}\n"
            f"Amount: ${amount:,.2f}\n"
            f"Price: ${price:.6f}"
        )
        
        if pl_percentage is not None:
            emoji = "📈" if pl_percentage >= 0 else "📉"
            message += f"\nP/L: {emoji} {pl_percentage:+.2f}%"
        
        await self._broadcast_alert(message, "trades")

    async def send_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info"
    ):
        """
        Send system status alert
        """
        severity_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "🚨",
            "success": "✅"
        }
        
        formatted_message = (
            f"{severity_emoji.get(severity, 'ℹ️')} System Alert\n\n"
            f"Type: {alert_type}\n"
            f"Message: {message}"
        )
        
        await self._broadcast_alert(formatted_message, "system")

    async def send_performance_alert(
        self,
        total_trades: int,
        successful_trades: int,
        total_profit_loss: float,
        time_period: str = "24h"
    ):
        """
        Send trading performance alert
        """
        success_rate = (successful_trades / total_trades * 100) if total_trades > 0 else 0
        
        message = (
            f"📊 Performance Update ({time_period})\n\n"
            f"Total Trades: {total_trades}\n"
            f"Success Rate: {success_rate:.1f}%\n"
            f"Total P/L: {total_profit_loss:+.2f}%"
        )
        
        await self._broadcast_alert(message, "system")

    def subscribe_to_alerts(self, chat_id: int, alert_types: List[str]):
        """
        Subscribe a chat to specific types of alerts
        """
        for alert_type in alert_types:
            if alert_type in self.alert_channels:
                if chat_id not in self.alert_channels[alert_type]:
                    self.alert_channels[alert_type].append(chat_id)
                    logger.info(f"Chat {chat_id} subscribed to {alert_type} alerts")

    def unsubscribe_from_alerts(self, chat_id: int, alert_types: Optional[List[str]] = None):
        """
        Unsubscribe a chat from alerts
        """
        if alert_types is None:
            # Unsubscribe from all alert types
            for channel in self.alert_channels.values():
                if chat_id in channel:
                    channel.remove(chat_id)
            logger.info(f"Chat {chat_id} unsubscribed from all alerts")
        else:
            # Unsubscribe from specific alert types
            for alert_type in alert_types:
                if alert_type in self.alert_channels and chat_id in self.alert_channels[alert_type]:
                    self.alert_channels[alert_type].remove(chat_id)
                    logger.info(f"Chat {chat_id} unsubscribed from {alert_type} alerts")

    async def _broadcast_alert(self, message: str, alert_type: str):
        """
        Broadcast alert to all subscribed chats
        """
        if alert_type not in self.alert_channels:
            logger.error(f"Invalid alert type: {alert_type}")
            return

        chat_ids = self.alert_channels[alert_type]
        if not chat_ids:
            logger.debug(f"No subscribers for {alert_type} alerts")
            return

        try:
            await self.bot.broadcast_message(
                chat_ids=chat_ids,
                text=message,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error broadcasting {alert_type} alert: {str(e)}")
