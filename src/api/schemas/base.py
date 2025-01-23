from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class TokenBase(BaseModel):
    symbol: str
    first_mention_time: Optional[datetime] = None
    mention_count: Optional[int] = 0
    trend_strength: Optional[float] = 0.0
    latest_tweet: Optional[str] = None
    safety_score: Optional[float] = 0.0

class TradeBase(BaseModel):
    symbol: str
    entry_price: float
    current_price: Optional[float] = None
    position_size: float
    time_entered: datetime
    status: str
    pl_percentage: Optional[float] = None

class ConfigBase(BaseModel):
    api_keys: Dict[str, str]
    trading_params: Dict[str, Any]
    system_settings: Dict[str, Any]

class SystemStatus(BaseModel):
    uptime: float
    active_connections: int
    api_status: Dict[str, bool]
    memory_usage: float
    error_rate: float
    trading_performance: Dict[str, float]

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
