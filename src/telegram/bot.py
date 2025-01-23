import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable, Awaitable
from .client import TelegramClient
from .commands import handle_command

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.client: Optional[TelegramClient] = None
        self.command_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[str]]] = {}
        self.running = False
        self.last_update_id = 0

    async def start(self):
        """
        Start the bot
        """
        self.running = True
        self.client = TelegramClient(self.token)
        
        try:
            async with self.client:
                # Delete any existing webhook to use getUpdates
                await self.client.delete_webhook()
                logger.info("Bot started successfully")
                await self._poll_updates()
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            raise

    async def stop(self):
        """
        Stop the bot
        """
        self.running = False
        logger.info("Bot stopped")

    def register_command(self, command: str, handler: Callable[[Dict[str, Any]], Awaitable[str]]):
        """
        Register a command handler
        """
        self.command_handlers[command] = handler
        logger.info(f"Registered handler for command: {command}")

    async def _poll_updates(self):
        """
        Poll for updates using long polling
        """
        while self.running:
            try:
                updates = await self.client.get_updates(
                    offset=self.last_update_id + 1,
                    timeout=30
                )
                
                for update in updates.get("result", []):
                    await self._process_update(update)
                    self.last_update_id = update["update_id"]
                    
            except Exception as e:
                logger.error(f"Error polling updates: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _process_update(self, update: Dict[str, Any]):
        """
        Process a single update
        """
        try:
            message = update.get("message", {})
            if not message:
                return

            text = message.get("text", "")
            chat_id = message.get("chat", {}).get("id")
            
            if not text or not chat_id:
                return

            if text.startswith("/"):
                # Handle command
                command_parts = text[1:].split()
                command = command_parts[0].lower()
                args = command_parts[1:]

                response = await handle_command(command, args, message)
                if response:
                    await self.client.send_message(
                        chat_id=chat_id,
                        text=response,
                        parse_mode="HTML"
                    )
            else:
                # Handle regular message if needed
                pass

        except Exception as e:
            logger.error(f"Error processing update: {str(e)}")

    async def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None):
        """
        Send a message to a chat
        """
        if not self.client:
            raise RuntimeError("Bot not started")
            
        try:
            await self.client.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

    async def broadcast_message(self, chat_ids: List[int], text: str, parse_mode: Optional[str] = None):
        """
        Broadcast a message to multiple chats
        """
        if not self.client:
            raise RuntimeError("Bot not started")
            
        for chat_id in chat_ids:
            try:
                await self.send_message(chat_id, text, parse_mode)
                await asyncio.sleep(0.1)  # Small delay between messages
            except Exception as e:
                logger.error(f"Error broadcasting to {chat_id}: {str(e)}")
