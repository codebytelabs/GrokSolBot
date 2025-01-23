import os
import tweepy
import re
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TwitterScanner:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Twitter API credentials not found in .env file")
            
        self.auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        self.api = tweepy.API(self.auth)
        self.trends = {}  # Store trend data
        
    async def start_scanning(self, callback):
        """
        Start continuous Twitter scanning
        
        Args:
            callback: Function to call with new token data
        """
        while True:
            try:
                await self._scan_and_process(callback)
                await asyncio.sleep(10)  # Scan every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in Twitter scanning: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
                
    async def _scan_and_process(self, callback):
        """Scan tweets and process found tokens"""
        # Search for memecoin related tweets
        tweets = await self._search_tweets()
        
        for tweet in tweets:
            # Extract token symbols
            symbols = self._extract_symbols(tweet.text)
            
            # Update trend data
            timestamp = datetime.now()
            for symbol in symbols:
                if symbol not in self.trends:
                    self.trends[symbol] = []
                    
                self.trends[symbol].append({
                    'timestamp': timestamp,
                    'tweet_id': tweet.id,
                    'user': tweet.user.screen_name,
                    'followers': tweet.user.followers_count,
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count
                })
                
                # Calculate trend strength
                trend_strength = self._calculate_trend_strength(symbol)
                
                # Notify about strong trends
                if trend_strength > 0.7:  # Threshold for strong trends
                    await callback({
                        'symbol': symbol,
                        'trend_strength': trend_strength,
                        'mentions': len(self.trends[symbol]),
                        'latest_tweet': tweet.text,
                        'source': 'twitter'
                    })
                    
    async def _search_tweets(self):
        """Search for relevant tweets"""
        keywords = [
            'memecoin solana',
            'solana token',
            '$SOL memecoin',
            'new solana',
            'launch solana'
        ]
        
        all_tweets = []
        for query in keywords:
            try:
                tweets = self.api.search_tweets(
                    q=query,
                    count=100,
                    tweet_mode='extended',
                    lang='en'
                )
                all_tweets.extend(tweets)
            except tweepy.TweepError as e:
                logger.error(f"Twitter API error: {str(e)}")
                
        return all_tweets
        
    def _extract_symbols(self, text):
        """Extract potential token symbols from text"""
        # Match $SYMBOL pattern (3-10 uppercase letters)
        pattern = r'\$[A-Z]{3,10}\b'
        symbols = re.findall(pattern, text)
        
        # Remove $ prefix and filter out common words
        filtered = set()
        common_words = {'THE', 'AND', 'FOR', 'SOL'}  # Expand as needed
        
        for symbol in symbols:
            symbol = symbol[1:]  # Remove $
            if symbol not in common_words:
                filtered.add(symbol)
                
        return filtered
        
    def _calculate_trend_strength(self, symbol):
        """
        Calculate trend strength based on:
        - Number of mentions
        - User influence (followers)
        - Tweet engagement (likes, retweets)
        - Time decay
        """
        if symbol not in self.trends:
            return 0
            
        mentions = self.trends[symbol]
        now = datetime.now()
        
        # Only consider mentions in last 24 hours
        recent_mentions = [
            m for m in mentions 
            if (now - m['timestamp']).total_seconds() < 86400
        ]
        
        if not recent_mentions:
            return 0
            
        # Factors in trend strength
        num_mentions = len(recent_mentions)
        avg_followers = sum(m['followers'] for m in recent_mentions) / num_mentions
        avg_engagement = sum(
            m['retweets'] + m['likes'] 
            for m in recent_mentions
        ) / num_mentions
        
        # Normalize factors
        norm_mentions = min(num_mentions / 50, 1.0)  # Cap at 50 mentions
        norm_followers = min(avg_followers / 10000, 1.0)  # Cap at 10k followers
        norm_engagement = min(avg_engagement / 1000, 1.0)  # Cap at 1k engagement
        
        # Weighted average
        strength = (
            norm_mentions * 0.4 +
            norm_followers * 0.3 +
            norm_engagement * 0.3
        )
        
        return strength
        
    def get_trend_data(self, symbol=None):
        """Get trend data for analysis"""
        if symbol:
            return self.trends.get(symbol, [])
        return self.trends
