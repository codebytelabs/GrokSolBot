# GrokSolBot

A Solana Memecoin Trading System with automated trading capabilities and real-time monitoring.

## Features

- Real-time token monitoring and analysis
- Twitter mention tracking
- New token launch detection
- Automated trading with configurable parameters
- Safety checks and risk management
- Real-time WebSocket updates
- Telegram bot integration
- Web dashboard (coming soon)

## System Architecture

### Backend Components
- Twitter Scanner Module
- Launch Tracker Module
- Data Analyzer Module
- Safety Checker Module
- Trading Module
- Telegram Bot Integration
- FastAPI REST API
- WebSocket Server

### Frontend Components (Coming Soon)
- Dashboard Layout
- Token Tables
- Configuration Panel
- Monitoring Section

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/codebytelabs/GrokSolBot.git
cd GrokSolBot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Configure your environment variables in .env:
```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here  # Get this from @BotFather

# Twitter API Keys
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Solana API Keys
GMGN_API_KEY=your_gmgn_key
PUMPFUN_API_KEY=your_pumpfun_key
SOLANA_SNIFFER_API_KEY=your_sniffer_key

# Trading Configuration
MAX_TRADE_AMOUNT=1.0
DEFAULT_SLIPPAGE=1.0
STOP_LOSS_PERCENTAGE=5.0
TAKE_PROFIT_PERCENTAGE=10.0
```

6. Set up Telegram Bot:
   - Message @BotFather on Telegram
   - Create a new bot using `/newbot`
   - Copy the bot token to your .env file
   - Start your bot by sending `/start`

7. Run the application:
```bash
python src/main.py
```

## Telegram Bot Commands

The bot supports the following commands:

- `/start` - Initialize the bot and get welcome message
- `/help` - Show available commands and usage
- `/status` - Check system status and performance
- `/monitor [symbol]` - Monitor token or view monitored tokens
- `/trade [symbol] [amount]` - Execute trades or view active trades
- `/settings` - View and modify bot configuration

Example usage:
```
/monitor BONK
/trade BONK 100
/status
```

## Telegram Alerts

The bot provides real-time alerts for:

1. Token Mentions
   - New mentions on Twitter
   - Trend strength analysis
   - Latest tweets

2. Token Launches
   - New token launches
   - Initial price and liquidity
   - Safety score

3. Trade Updates
   - Trade execution status
   - Position updates
   - P/L notifications

4. System Alerts
   - Performance updates
   - Error notifications
   - Status changes

To subscribe to alerts:
1. Start the bot with `/start`
2. Use `/settings` to configure alert preferences
3. The bot will automatically send alerts based on your settings

## API Documentation

### Token Endpoints

#### GET /api/tokens/twitter-mentions
Get tokens mentioned on Twitter with filtering options.
- Query Parameters:
  - time_range: Time range in hours (default: 24)
  - min_mentions: Minimum mention count
  - min_trend_strength: Minimum trend strength

#### GET /api/tokens/new-launches
Get newly launched tokens with filtering options.
- Query Parameters:
  - time_range: Time range in hours (default: 24)
  - min_liquidity: Minimum liquidity
  - min_safety_score: Minimum safety score

### Trade Endpoints

#### GET /api/trades/active
Get list of active trades with filtering options.
- Query Parameters:
  - min_pl: Minimum P/L percentage
  - max_pl: Maximum P/L percentage
  - min_position: Minimum position size

#### POST /api/trades/execute
Execute a new trade.
- Parameters:
  - symbol: Token symbol
  - amount: Trade amount
  - slippage: Maximum slippage percentage (default: 1.0)

### Configuration Endpoints

#### GET /api/config
Get current system configuration.

#### PUT /api/config/api-keys
Update specific API key.
- Parameters:
  - key_type: Type of API key
  - value: New API key value

#### PUT /api/config/trading-params
Update specific trading parameter.
- Parameters:
  - param_name: Parameter name
  - value: New parameter value

### System Endpoints

#### GET /api/system/status
Get current system status and performance metrics.

#### GET /api/system/logs
Get system logs with filtering options.
- Query Parameters:
  - level: Log level filter
  - start_time: Start timestamp
  - end_time: End timestamp
  - limit: Maximum number of logs to return

### WebSocket API

Connect to `/ws` endpoint for real-time updates.

Available channels:
- tokens: Token-related updates (mentions, launches)
- trades: Trade execution and updates
- system: System status updates
- alerts: Error and warning alerts

Subscribe to channels:
```json
{
  "type": "subscribe",
  "channels": ["tokens", "trades"]
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
