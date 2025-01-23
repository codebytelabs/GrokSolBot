import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class DataAnalyzer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.token_data = {}  # Store historical data
        self.analysis_results = {}  # Store analysis results
        
    async def start_analysis(self, callback):
        """
        Start continuous data analysis
        
        Args:
            callback: Function to call with analysis results
        """
        while True:
            try:
                await self._analyze_all_tokens(callback)
                await asyncio.sleep(30)  # Analyze every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in data analysis: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
                
    async def _analyze_all_tokens(self, callback):
        """Analyze all tracked tokens"""
        for token_address in self.token_data:
            try:
                analysis = await self._analyze_token(token_address)
                if analysis:
                    self.analysis_results[token_address] = analysis
                    await callback(analysis)
            except Exception as e:
                logger.error(f"Error analyzing token {token_address}: {str(e)}")
                
    async def _analyze_token(self, token_address):
        """Analyze single token data"""
        data = self.token_data.get(token_address)
        if not data or len(data) < 10:  # Need minimum data points
            return None
            
        df = pd.DataFrame(data)
        
        # Basic indicators
        current_price = df['price'].iloc[-1]
        price_change = self._calculate_price_change(df)
        volume = self._calculate_volume(df)
        volatility = self._calculate_volatility(df)
        trend = self._detect_trend(df)
        
        # Advanced analysis
        support, resistance = self._calculate_support_resistance(df)
        momentum = self._calculate_momentum(df)
        liquidity = self._analyze_liquidity(df)
        prediction = await self._predict_price(df)
        
        # Social metrics if available
        social_score = self._calculate_social_score(df)
        
        return {
            'token_address': token_address,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'current_price': current_price,
                'price_change_1h': price_change['1h'],
                'price_change_24h': price_change['24h'],
                'volume_24h': volume,
                'volatility': volatility,
                'trend': trend,
                'support_level': support,
                'resistance_level': resistance,
                'momentum': momentum,
                'liquidity_score': liquidity,
                'social_score': social_score,
                'predicted_price': prediction
            },
            'signals': self._generate_signals(locals())
        }
        
    def _calculate_price_change(self, df):
        """Calculate price changes over different periods"""
        current = df['price'].iloc[-1]
        changes = {}
        
        for period, hours in [('1h', 1), ('24h', 24)]:
            if len(df) >= hours:
                previous = df['price'].iloc[-hours]
                changes[period] = ((current - previous) / previous) * 100
            else:
                changes[period] = 0
                
        return changes
        
    def _calculate_volume(self, df, hours=24):
        """Calculate trading volume"""
        if len(df) < hours:
            return df['volume'].sum()
        return df['volume'].tail(hours).sum()
        
    def _calculate_volatility(self, df, hours=24):
        """Calculate price volatility"""
        if len(df) < hours:
            return df['price'].std()
        return df['price'].tail(hours).std()
        
    def _detect_trend(self, df, hours=24):
        """Detect price trend using linear regression"""
        if len(df) < hours:
            return 'insufficient_data'
            
        prices = df['price'].tail(hours)
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]
        
        if slope > 0.01:
            return 'uptrend'
        elif slope < -0.01:
            return 'downtrend'
        else:
            return 'sideways'
            
    def _calculate_support_resistance(self, df):
        """Calculate support and resistance levels"""
        prices = df['price'].values
        
        # Simple method using percentiles
        support = np.percentile(prices, 25)
        resistance = np.percentile(prices, 75)
        
        return support, resistance
        
    def _calculate_momentum(self, df):
        """Calculate price momentum"""
        roc = df['price'].pct_change(periods=12)  # Rate of change
        return roc.mean() * 100
        
    def _analyze_liquidity(self, df):
        """Analyze token liquidity"""
        if 'liquidity' not in df.columns:
            return None
            
        recent = df.tail(24)  # Last 24 hours
        
        # Calculate liquidity score based on:
        # - Average liquidity
        # - Liquidity stability
        # - Volume/Liquidity ratio
        avg_liquidity = recent['liquidity'].mean()
        liquidity_stability = 1 - recent['liquidity'].std() / avg_liquidity
        volume_liquidity_ratio = recent['volume'].sum() / avg_liquidity
        
        # Combine metrics into score (0-1)
        score = (
            0.4 * min(avg_liquidity / 1000000, 1) +  # Cap at 1M
            0.3 * liquidity_stability +
            0.3 * min(volume_liquidity_ratio / 0.5, 1)  # Cap at 50% turnover
        )
        
        return score
        
    def _calculate_social_score(self, df):
        """Calculate social sentiment score"""
        if 'social_mentions' not in df.columns:
            return None
            
        recent = df.tail(24)
        
        # Combine different social metrics
        mentions = recent['social_mentions'].sum()
        sentiment = recent.get('sentiment', pd.Series([0])).mean()
        
        # Normalize and combine
        norm_mentions = min(mentions / 1000, 1)  # Cap at 1000 mentions
        norm_sentiment = (sentiment + 1) / 2  # Convert -1,1 to 0,1
        
        return (norm_mentions * 0.7 + norm_sentiment * 0.3)
        
    async def _predict_price(self, df):
        """Predict future price using ML"""
        if len(df) < 48:  # Need enough historical data
            return None
            
        try:
            # Create features
            X = self._create_features(df)
            y = df['price'].shift(-1).dropna()
            
            if len(X) != len(y):
                return None
                
            # Train on recent data
            train_size = int(len(X) * 0.8)
            X_train = X[:train_size]
            y_train = y[:train_size]
            
            # Fit model
            self.model.fit(X_train, y_train)
            
            # Predict next price
            next_price = self.model.predict(X[-1:])
            return float(next_price[0])
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return None
            
    def _create_features(self, df):
        """Create feature set for ML prediction"""
        features = pd.DataFrame()
        
        # Price changes over different periods
        for period in [1, 3, 6, 12, 24]:
            features[f'price_change_{period}h'] = df['price'].pct_change(period)
            
        # Volume features
        features['volume_ma24'] = df['volume'].rolling(24).mean()
        features['volume_std24'] = df['volume'].rolling(24).std()
        
        # Price features
        features['price_ma24'] = df['price'].rolling(24).mean()
        features['price_std24'] = df['price'].rolling(24).std()
        
        # Add social metrics if available
        if 'social_mentions' in df.columns:
            features['social_ma24'] = df['social_mentions'].rolling(24).mean()
            
        return features.dropna()
        
    def _generate_signals(self, data):
        """Generate trading signals based on analysis"""
        signals = []
        metrics = data['metrics']
        
        # Trend following signals
        if metrics['trend'] == 'uptrend' and metrics['momentum'] > 0:
            signals.append({
                'type': 'buy',
                'strength': 0.7,
                'reason': 'Strong uptrend with positive momentum'
            })
            
        # Reversal signals
        if metrics['price'] <= metrics['support_level']:
            signals.append({
                'type': 'buy',
                'strength': 0.6,
                'reason': 'Price at support level'
            })
            
        # Volume-based signals
        if metrics['volume_24h'] > metrics.get('volume_ma24', 0) * 2:
            signals.append({
                'type': 'buy',
                'strength': 0.5,
                'reason': 'High volume spike'
            })
            
        return signals
        
    def update_token_data(self, token_address, new_data):
        """Update historical data for a token"""
        if token_address not in self.token_data:
            self.token_data[token_address] = []
            
        self.token_data[token_address].append(new_data)
        
        # Keep only last 7 days of data
        cutoff = datetime.now() - timedelta(days=7)
        self.token_data[token_address] = [
            d for d in self.token_data[token_address]
            if datetime.fromisoformat(d['timestamp']) > cutoff
        ]
