import os
import aiohttp
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class LaunchTracker:
    def __init__(self):
        self.gmgn_api_key = os.getenv('GMGN_API_KEY')
        self.pumpfun_api_key = os.getenv('PUMPFUN_API_KEY')
        
        if not self.gmgn_api_key or not self.pumpfun_api_key:
            raise ValueError("API keys not found in .env file")
            
        self.gmgn_url = "https://api.gmgn.com"  # Example URL
        self.pumpfun_url = "https://api.pumpfun.com"  # Example URL
        self.tracked_launches = {}
        
    async def start_tracking(self, callback):
        """
        Start continuous launch tracking
        
        Args:
            callback: Function to call with new launch data
        """
        while True:
            try:
                # Track from multiple sources concurrently
                await asyncio.gather(
                    self._track_gmgn(callback),
                    self._track_pumpfun(callback)
                )
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in launch tracking: {str(e)}")
                await asyncio.sleep(30)  # Wait longer on error
                
    async def _track_gmgn(self, callback):
        """Track launches from GMGN"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.gmgn_api_key}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(
                    f"{self.gmgn_url}/new_launches",
                    headers=headers,
                    params={'chain': 'solana'}
                ) as response:
                    if response.status == 200:
                        launches = await response.json()
                        await self._process_launches(launches, 'gmgn', callback)
                    else:
                        logger.error(f"GMGN API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"GMGN tracking error: {str(e)}")
            
    async def _track_pumpfun(self, callback):
        """Track launches from PumpFun"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-Key': self.pumpfun_api_key,
                    'Content-Type': 'application/json'
                }
                
                async with session.get(
                    f"{self.pumpfun_url}/launches",
                    headers=headers,
                    params={'blockchain': 'solana'}
                ) as response:
                    if response.status == 200:
                        launches = await response.json()
                        await self._process_launches(launches, 'pumpfun', callback)
                    else:
                        logger.error(f"PumpFun API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"PumpFun tracking error: {str(e)}")
            
    async def _process_launches(self, launches, source, callback):
        """Process launch data and notify if new"""
        for launch in launches:
            token_address = launch.get('token_address')
            
            if not token_address:
                continue
                
            # Check if this is a new launch
            if token_address not in self.tracked_launches:
                processed_launch = {
                    'symbol': launch.get('symbol'),
                    'name': launch.get('name'),
                    'address': token_address,
                    'launch_time': launch.get('launch_time'),
                    'initial_price': launch.get('initial_price'),
                    'initial_liquidity': launch.get('initial_liquidity'),
                    'source': source,
                    'detected_at': datetime.now().isoformat()
                }
                
                # Add additional metrics if available
                if source == 'gmgn':
                    processed_launch.update({
                        'market_cap': launch.get('market_cap'),
                        'volume_24h': launch.get('volume_24h'),
                        'holders': launch.get('holders')
                    })
                elif source == 'pumpfun':
                    processed_launch.update({
                        'launch_type': launch.get('launch_type'),
                        'platform': launch.get('platform'),
                        'pair_address': launch.get('pair_address')
                    })
                    
                # Store and notify
                self.tracked_launches[token_address] = processed_launch
                await callback(processed_launch)
                
    def get_tracked_launches(self):
        """Get all tracked launches"""
        return self.tracked_launches
