# Solana Memecoin Trading System

A comprehensive trading system for Solana memecoins with real-time monitoring, automated trading, and a user-friendly dashboard.

## Features

### Core Trading Features
- Real-time Twitter monitoring for memecoin mentions
- New token launch detection via GMGN and PumpFun APIs
- Advanced token analysis with machine learning
- Token safety verification via SolanaSniffer
- Automated trading on Solana
- Telegram bot integration for alerts and control

### Dashboard Interface
- Real-time token monitoring tables
- Advanced filtering and sorting
- Configuration management
- Live system monitoring
- Performance metrics
- Log viewer

### Operating Modes
1. Auto Mode
   - Fully automated trading
   - Real-time monitoring
   - Automatic safety checks
   - Configurable trading parameters

2. Monitor Mode
   - All monitoring features active
   - No automatic trading
   - Manual trade execution
   - Perfect for learning and strategy development

## System Architecture

### Backend Components
```
src/
  ├── grok/              # Core trading components
  │   ├── scanner.py     # Twitter monitoring
  │   ├── tracker.py     # Launch detection
  │   ├── analyzer.py    # Data analysis
  │   ├── safety.py      # Safety checks
  │   └── trader.py      # Trade execution
  │
  ├── telegram/          # Telegram integration
  │   ├── bot.py         # Bot interface
  │   ├── commands.py    # Command handlers
  │   └── alerts.py      # Alert system
  │
  └── main.py            # System runner
```

### Frontend Components
```
frontend/
  ├── src/
  │   ├── components/    # React components
  │   ├── pages/         # Page layouts
  │   ├── store/         # State management
  │   ├── api/           # API client
  │   └── utils/         # Utilities
  │
  └── public/            # Static assets
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Solana CLI
- SQLite

### Backend Setup
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

3. Start the backend:
```bash
python src/main.py
```

### Frontend Setup
1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Configuration

### Required API Keys
- Twitter API Keys
- GMGN API Key
- PumpFun API Key
- SolanaSniffer API Key
- Telegram Bot Token
- Solana Wallet

### Trading Parameters
- Maximum trade amount
- Default slippage
- Stop loss percentage
- Take profit percentage
- Risk management rules

### System Settings
- Operating mode (Auto/Monitor)
- Scan intervals
- Alert preferences
- Log level
- Data retention

## Usage

### Dashboard Navigation
1. Token Tables
   - Twitter Mentions
   - New Launches
   - Active Trades
   - Use filters and sorting for analysis

2. Configuration
   - API Keys Management
   - Trading Parameters
   - System Settings

3. Monitoring
   - Live Log Viewer
   - System Status
   - Performance Metrics

### Telegram Commands
- `/start` - Initialize bot
- `/status` - Check system status
- `/snipe <token>` - Snipe new token
- `/buy <token> <amount>` - Buy token
- `/sell <token> <amount>` - Sell token
- `/balance` - Check wallet balance
- `/positions` - View open positions

## Development Status

See [DevelopmentPlan.md](DevelopmentPlan.md) for:
- Detailed component specifications
- Implementation phases
- Current status
- Next steps
- Technical stack details

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational purposes only. Cryptocurrency trading carries significant risks. Always do your own research and never trade with money you cannot afford to lose.
