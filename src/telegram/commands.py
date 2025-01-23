import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, grok_bot, alert_system):
        self.grok = grok_bot  # Reference to main Grok bot
        self.alerts = alert_system
        
    async def handle_snipe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle snipe command
        Format: /snipe <token_address>
        """
        try:
            if not context.args:
                await update.message.reply_text(
                    "Please provide a token address.\n"
                    "Usage: /snipe <token_address>"
                )
                return
                
            token_address = context.args[0]
            
            # Check token safety first
            safety_result = await self.grok.safety.check_token(token_address)
            if safety_result['status'] == 'high_risk':
                await self.alerts.send_safety_alert(update.message.chat_id, safety_result)
                await update.message.reply_text(
                    "❌ Snipe cancelled: Token failed safety checks"
                )
                return
                
            # Execute snipe
            trade_result = await self.grok.trader.execute_trade(
                token_address,
                'buy',
                amount=1.0,  # Example amount
                params={'slippage': 2.0}  # Higher slippage for sniping
            )
            
            if trade_result['status'] == 'success':
                await self.alerts.send_trade_alert(
                    update.message.chat_id,
                    trade_result['details']
                )
            else:
                await update.message.reply_text(
                    f"❌ Snipe failed: {trade_result['message']}"
                )
                
        except Exception as e:
            logger.error(f"Snipe command error: {str(e)}")
            await update.message.reply_text("❌ Error executing snipe command")
            
    async def handle_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle buy command
        Format: /buy <token_address> <amount>
        """
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "Please provide token address and amount.\n"
                    "Usage: /buy <token_address> <amount>"
                )
                return
                
            token_address = context.args[0]
            amount = float(context.args[1])
            
            # Check token safety
            safety_result = await self.grok.safety.check_token(token_address)
            await self.alerts.send_safety_alert(update.message.chat_id, safety_result)
            
            if safety_result['status'] == 'high_risk':
                await update.message.reply_text(
                    "⚠️ Warning: This token has high risk. Proceed with caution."
                )
                
            # Execute buy
            trade_result = await self.grok.trader.execute_trade(
                token_address,
                'buy',
                amount=amount
            )
            
            if trade_result['status'] == 'success':
                await self.alerts.send_trade_alert(
                    update.message.chat_id,
                    trade_result['details']
                )
            else:
                await update.message.reply_text(
                    f"❌ Buy failed: {trade_result['message']}"
                )
                
        except ValueError:
            await update.message.reply_text("Invalid amount format")
        except Exception as e:
            logger.error(f"Buy command error: {str(e)}")
            await update.message.reply_text("❌ Error executing buy command")
            
    async def handle_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle sell command
        Format: /sell <token_address> <amount>
        """
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "Please provide token address and amount.\n"
                    "Usage: /sell <token_address> <amount>"
                )
                return
                
            token_address = context.args[0]
            amount = float(context.args[1])
            
            # Execute sell
            trade_result = await self.grok.trader.execute_trade(
                token_address,
                'sell',
                amount=amount
            )
            
            if trade_result['status'] == 'success':
                await self.alerts.send_trade_alert(
                    update.message.chat_id,
                    trade_result['details']
                )
            else:
                await update.message.reply_text(
                    f"❌ Sell failed: {trade_result['message']}"
                )
                
        except ValueError:
            await update.message.reply_text("Invalid amount format")
        except Exception as e:
            logger.error(f"Sell command error: {str(e)}")
            await update.message.reply_text("❌ Error executing sell command")
            
    async def handle_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle balance command"""
        try:
            positions = self.grok.trader.get_positions()
            
            if not positions:
                await update.message.reply_text("No open positions")
                return
                
            balance_text = "Current Positions:\n\n"
            
            for token_address, position in positions.items():
                balance_text += (
                    f"Token: {token_address}\n"
                    f"Amount: {position['amount']}\n"
                    f"Avg Price: {position['avg_price']} SOL\n\n"
                )
                
            await update.message.reply_text(balance_text)
            
        except Exception as e:
            logger.error(f"Balance command error: {str(e)}")
            await update.message.reply_text("❌ Error fetching balance")
            
    async def handle_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle history command"""
        try:
            history = self.grok.trader.get_trade_history()
            
            if not history:
                await update.message.reply_text("No trade history")
                return
                
            history_text = "Recent Trades:\n\n"
            
            for trade in history[-5:]:  # Show last 5 trades
                history_text += (
                    f"{trade['action'].upper()}: {trade['token_address']}\n"
                    f"Amount: {trade['amount']}\n"
                    f"Price: {trade['price']} SOL\n"
                    f"Time: {trade['timestamp']}\n\n"
                )
                
            await update.message.reply_text(history_text)
            
        except Exception as e:
            logger.error(f"History command error: {str(e)}")
            await update.message.reply_text("❌ Error fetching trade history")
            
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle settings command
        Format: /settings [parameter] [value]
        """
        try:
            # Show current settings if no parameters
            if not context.args:
                settings_text = (
                    "Current Settings:\n\n"
                    "- auto_snipe: enabled\n"
                    "- max_slippage: 1%\n"
                    "- stop_loss: 20%\n"
                    "- take_profit: 50%\n\n"
                    "To change a setting:\n"
                    "/settings <parameter> <value>"
                )
                await update.message.reply_text(settings_text)
                return
                
            # Update setting
            param = context.args[0]
            value = context.args[1]
            
            # Implement settings update logic here
            await update.message.reply_text(
                f"✅ Updated {param} to {value}"
            )
            
        except Exception as e:
            logger.error(f"Settings command error: {str(e)}")
            await update.message.reply_text("❌ Error updating settings")
