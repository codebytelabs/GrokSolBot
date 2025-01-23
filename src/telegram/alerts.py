import logging
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("Telegram bot token not found in .env file")
            
        self.bot = Bot(token=self.token)
        self.chat_ids = set()  # Store subscribed chat IDs
        
    async def send_launch_alert(self, chat_id, token_data):
        """
        Send alert for new token launch
        
        Args:
            chat_id: Telegram chat ID
            token_data: Token launch information
        """
        try:
            message = (
                "🚀 New Token Launch Detected!\n\n"
                f"Symbol: {token_data['symbol']}\n"
                f"Name: {token_data['name']}\n"
                f"Address: {token_data['address']}\n"
                f"Initial Price: {token_data['initial_price']} SOL\n"
                f"Initial Liquidity: {token_data['initial_liquidity']} SOL\n\n"
                "Use /snipe to trade this token!"
            )
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Error sending launch alert: {str(e)}")
            
    async def send_trend_alert(self, chat_id, trend_data):
        """
        Send alert for trending token
        
        Args:
            chat_id: Telegram chat ID
            trend_data: Token trend information
        """
        try:
            message = (
                "📈 Trending Token Alert!\n\n"
                f"Symbol: {trend_data['symbol']}\n"
                f"Trend Strength: {trend_data['trend_strength']*100:.1f}%\n"
                f"Recent Mentions: {trend_data['mentions']}\n"
                f"Latest Tweet: {trend_data['latest_tweet']}\n\n"
                "Use /buy to trade this token!"
            )
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            
        except Exception as e:
            logger.error(f"Error sending trend alert: {str(e)}")
            
    async def send_safety_alert(self, chat_id, safety_data):
        """
        Send alert for token safety check
        
        Args:
            chat_id: Telegram chat ID
            safety_data: Token safety information
        """
        try:
            status_emoji = {
                'safe': '✅',
                'medium_risk': '⚠️',
                'high_risk': '🚨'
            }
            
            warning_text = "\n".join([
                f"- {w.replace('_', ' ').title()}"
                for w in safety_data['warnings']
            ]) if safety_data['warnings'] else "None"
            
            message = (
                f"{status_emoji[safety_data['status']]} Safety Check Results\n\n"
                f"Token: {safety_data['token_info']['symbol']}\n"
                f"Status: {safety_data['status'].replace('_', ' ').title()}\n\n"
                "Risk Scores:\n"
                f"- Contract Risk: {safety_data['risk_scores']['contract_risk']}%\n"
                f"- Ownership Risk: {safety_data['risk_scores']['ownership_risk']}%\n"
                f"- Liquidity Risk: {safety_data['risk_scores']['liquidity_risk']}%\n"
                f"- Overall Risk: {safety_data['risk_scores']['overall_risk']}%\n\n"
                "Warnings:\n"
                f"{warning_text}"
            )
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            
        except Exception as e:
            logger.error(f"Error sending safety alert: {str(e)}")
            
    async def send_trade_alert(self, chat_id, trade_data):
        """
        Send alert for executed trade
        
        Args:
            chat_id: Telegram chat ID
            trade_data: Trade execution information
        """
        try:
            action_emoji = '🟢' if trade_data['action'] == 'buy' else '🔴'
            
            message = (
                f"{action_emoji} Trade Executed\n\n"
                f"Action: {trade_data['action'].upper()}\n"
                f"Token: {trade_data['symbol']}\n"
                f"Amount: {trade_data['amount']}\n"
                f"Price: {trade_data['price']} SOL\n"
                f"Total: {trade_data['total']} SOL\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            
        except Exception as e:
            logger.error(f"Error sending trade alert: {str(e)}")
            
    async def send_error_alert(self, chat_id, error_data):
        """
        Send alert for system errors
        
        Args:
            chat_id: Telegram chat ID
            error_data: Error information
        """
        try:
            message = (
                "❌ System Error\n\n"
                f"Component: {error_data['component']}\n"
                f"Error: {error_data['message']}\n"
                f"Time: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            await self.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            
        except Exception as e:
            logger.error(f"Error sending error alert: {str(e)}")
            
    def subscribe(self, chat_id):
        """Add chat ID to subscribers"""
        self.chat_ids.add(chat_id)
        
    def unsubscribe(self, chat_id):
        """Remove chat ID from subscribers"""
        self.chat_ids.discard(chat_id)
        
    async def broadcast(self, message):
        """Send message to all subscribers"""
        for chat_id in self.chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Error broadcasting to {chat_id}: {str(e)}")
