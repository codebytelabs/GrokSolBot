import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TelegramClient:
    """
    Custom Telegram client using aiohttp to avoid httpx version conflicts
    """
    def __init__(self, token: str, base_url: str = "https://api.telegram.org"):
        self.token = token
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _build_url(self, method: str) -> str:
        return f"{self.base_url}/bot{self.token}/{method}"

    async def _make_request(
        self,
        method: str,
        http_method: str = "get",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make request to Telegram API
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use async with context.")

        url = self._build_url(method)
        try:
            async with getattr(self.session, http_method.lower())(
                url, params=params, json=json_data
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Telegram API request failed: {str(e)}")
            raise

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
    ) -> Dict[str, Any]:
        """
        Send message to a chat
        """
        return await self._make_request(
            "sendMessage",
            "post",
            json_data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification,
            },
        )

    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        timeout: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get updates from Telegram
        """
        params = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if timeout is not None:
            params["timeout"] = timeout
        if allowed_updates is not None:
            params["allowed_updates"] = json.dumps(allowed_updates)

        return await self._make_request("getUpdates", params=params)

    async def set_webhook(
        self,
        url: str,
        certificate: Optional[str] = None,
        max_connections: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Set webhook for receiving updates
        """
        json_data = {"url": url}
        if certificate is not None:
            json_data["certificate"] = certificate
        if max_connections is not None:
            json_data["max_connections"] = max_connections
        if allowed_updates is not None:
            json_data["allowed_updates"] = allowed_updates

        return await self._make_request("setWebhook", "post", json_data=json_data)

    async def delete_webhook(self) -> Dict[str, Any]:
        """
        Delete webhook
        """
        return await self._make_request("deleteWebhook", "post")

    async def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get webhook info
        """
        return await self._make_request("getWebhookInfo")
