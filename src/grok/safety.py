import os
import aiohttp
import logging
from datetime import datetime
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SafetyChecker:
    def __init__(self):
        self.api_key = os.getenv('SOLANASNIFFER_API_KEY')
        if not self.api_key:
            raise ValueError("SolanaSniffer API key not found in .env file")
            
        self.base_url = "https://api.solanasniffer.com"  # Example URL
        self.safety_cache = {}  # Cache safety results
        
    async def start_checking(self, callback):
        """
        Start continuous safety checking
        
        Args:
            callback: Function to call with safety check results
        """
        while True:
            try:
                # Clear old cache entries
                self._clear_expired_cache()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in safety checking: {str(e)}")
                await asyncio.sleep(300)  # Wait longer on error
                
    async def check_token(self, token_address):
        """
        Check token safety
        
        Args:
            token_address: Token contract address
            
        Returns:
            dict: Safety check results
        """
        # Check cache first
        if token_address in self.safety_cache:
            cached = self.safety_cache[token_address]
            if (datetime.now() - cached['timestamp']).seconds < 3600:  # Cache for 1 hour
                return cached['data']
                
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-Key': self.api_key,
                    'Content-Type': 'application/json'
                }
                
                # Get basic token info
                async with session.get(
                    f"{self.base_url}/token/{token_address}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API error: {response.status}")
                    token_info = await response.json()
                    
                # Get contract analysis
                async with session.get(
                    f"{self.base_url}/analyze/{token_address}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API error: {response.status}")
                    contract_analysis = await response.json()
                    
                # Process and combine results
                safety_result = await self._process_safety_data(
                    token_info,
                    contract_analysis
                )
                
                # Cache result
                self.safety_cache[token_address] = {
                    'timestamp': datetime.now(),
                    'data': safety_result
                }
                
                return safety_result
                
        except Exception as e:
            logger.error(f"Error checking token safety: {str(e)}")
            return None
            
    async def _process_safety_data(self, token_info, contract_analysis):
        """Process raw safety data into structured format"""
        try:
            # Basic token info
            result = {
                'timestamp': datetime.now().isoformat(),
                'token_info': {
                    'name': token_info.get('name'),
                    'symbol': token_info.get('symbol'),
                    'decimals': token_info.get('decimals'),
                    'total_supply': token_info.get('total_supply')
                },
                'contract_security': {
                    'is_verified': contract_analysis.get('is_verified', False),
                    'has_proxy': contract_analysis.get('has_proxy', False),
                    'is_mintable': contract_analysis.get('is_mintable', False),
                    'has_blacklist': contract_analysis.get('has_blacklist', False)
                }
            }
            
            # Ownership analysis
            result['ownership'] = {
                'owner_address': contract_analysis.get('owner'),
                'is_ownership_renounced': contract_analysis.get('is_renounced', False),
                'owner_balance_percentage': contract_analysis.get('owner_balance_pct', 0)
            }
            
            # Liquidity analysis
            result['liquidity'] = {
                'is_liquidity_locked': contract_analysis.get('liquidity_locked', False),
                'lock_duration_days': contract_analysis.get('lock_duration', 0),
                'total_liquidity': contract_analysis.get('total_liquidity', 0)
            }
            
            # Calculate risk scores
            result['risk_scores'] = self._calculate_risk_scores(result)
            
            # Overall safety assessment
            result['safety_status'] = self._assess_safety_status(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing safety data: {str(e)}")
            return None
            
    def _calculate_risk_scores(self, data):
        """Calculate various risk scores"""
        scores = {}
        
        # Contract risk (0-100, lower is better)
        contract_risk = 0
        if not data['contract_security']['is_verified']:
            contract_risk += 40
        if data['contract_security']['is_mintable']:
            contract_risk += 30
        if data['contract_security']['has_blacklist']:
            contract_risk += 20
        scores['contract_risk'] = contract_risk
        
        # Ownership risk
        ownership_risk = 0
        if not data['ownership']['is_ownership_renounced']:
            ownership_risk += 30
        if data['ownership']['owner_balance_percentage'] > 5:
            ownership_risk += data['ownership']['owner_balance_percentage'] * 2
        scores['ownership_risk'] = min(ownership_risk, 100)
        
        # Liquidity risk
        liquidity_risk = 0
        if not data['liquidity']['is_liquidity_locked']:
            liquidity_risk += 50
        elif data['liquidity']['lock_duration_days'] < 180:
            liquidity_risk += (180 - data['liquidity']['lock_duration_days']) / 3
        scores['liquidity_risk'] = min(liquidity_risk, 100)
        
        # Overall risk score (weighted average)
        scores['overall_risk'] = (
            contract_risk * 0.4 +
            ownership_risk * 0.3 +
            liquidity_risk * 0.3
        )
        
        return scores
        
    def _assess_safety_status(self, data):
        """Determine overall safety status"""
        risk_scores = data['risk_scores']
        
        if risk_scores['overall_risk'] < 20:
            status = 'safe'
        elif risk_scores['overall_risk'] < 50:
            status = 'medium_risk'
        else:
            status = 'high_risk'
            
        # Add warning flags
        warnings = []
        if not data['contract_security']['is_verified']:
            warnings.append('unverified_contract')
        if data['contract_security']['is_mintable']:
            warnings.append('mintable_token')
        if not data['liquidity']['is_liquidity_locked']:
            warnings.append('unlocked_liquidity')
        if data['ownership']['owner_balance_percentage'] > 10:
            warnings.append('high_owner_balance')
            
        return {
            'status': status,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
        
    def _clear_expired_cache(self):
        """Clear expired entries from cache"""
        now = datetime.now()
        expired = []
        
        for address, entry in self.safety_cache.items():
            if (now - entry['timestamp']).seconds >= 3600:  # 1 hour expiry
                expired.append(address)
                
        for address in expired:
            del self.safety_cache[address]
