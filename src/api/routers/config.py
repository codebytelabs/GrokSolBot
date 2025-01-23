from fastapi import APIRouter, HTTPException, Security
from typing import Dict, Any, Optional
from ..schemas.base import ConfigBase
from pydantic import BaseModel

router = APIRouter()

# Temporary in-memory storage (will be replaced with database)
current_config = {
    "api_keys": {
        "twitter": "",
        "gmgn": "",
        "pumpfun": "",
        "solana_sniffer": "",
        "telegram": ""
    },
    "trading_params": {
        "max_trade_amount": 1.0,
        "default_slippage": 1.0,
        "stop_loss_percentage": 5.0,
        "take_profit_percentage": 10.0,
        "auto_snipe_enabled": False,
        "risk_management": {
            "max_concurrent_trades": 3,
            "max_daily_loss": 5.0,
            "max_position_size": 1.0
        }
    },
    "system_settings": {
        "operating_mode": "monitor",  # monitor/auto
        "scan_interval": 60,  # seconds
        "alert_preferences": {
            "telegram_enabled": True,
            "min_alert_severity": "warning"
        },
        "log_level": "info",
        "data_retention_days": 30
    }
}

class APIKeyUpdate(BaseModel):
    key_type: str
    value: str

class TradingParamUpdate(BaseModel):
    param_name: str
    value: Any

class SystemSettingUpdate(BaseModel):
    setting_name: str
    value: Any

@router.get("/", response_model=ConfigBase)
async def get_current_config():
    """
    Get current system configuration
    """
    try:
        return current_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api-keys")
async def update_api_key(key_update: APIKeyUpdate):
    """
    Update specific API key
    """
    try:
        if key_update.key_type not in current_config["api_keys"]:
            raise HTTPException(status_code=400, detail=f"Invalid API key type: {key_update.key_type}")
        
        # TODO: Implement proper encryption for API keys
        current_config["api_keys"][key_update.key_type] = key_update.value
        return {"status": "success", "message": f"Updated {key_update.key_type} API key"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/trading-params")
async def update_trading_param(param_update: TradingParamUpdate):
    """
    Update specific trading parameter
    """
    try:
        # Handle nested parameters
        if "." in param_update.param_name:
            category, param = param_update.param_name.split(".")
            if category not in current_config["trading_params"]:
                raise HTTPException(status_code=400, detail=f"Invalid parameter category: {category}")
            if not isinstance(current_config["trading_params"][category], dict):
                raise HTTPException(status_code=400, detail=f"Parameter category {category} is not a dictionary")
            current_config["trading_params"][category][param] = param_update.value
        else:
            if param_update.param_name not in current_config["trading_params"]:
                raise HTTPException(status_code=400, detail=f"Invalid parameter name: {param_update.param_name}")
            current_config["trading_params"][param_update.param_name] = param_update.value
        
        return {"status": "success", "message": f"Updated {param_update.param_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/system-settings")
async def update_system_setting(setting_update: SystemSettingUpdate):
    """
    Update specific system setting
    """
    try:
        # Handle nested settings
        if "." in setting_update.setting_name:
            category, setting = setting_update.setting_name.split(".")
            if category not in current_config["system_settings"]:
                raise HTTPException(status_code=400, detail=f"Invalid setting category: {category}")
            if not isinstance(current_config["system_settings"][category], dict):
                raise HTTPException(status_code=400, detail=f"Setting category {category} is not a dictionary")
            current_config["system_settings"][category][setting] = setting_update.value
        else:
            if setting_update.setting_name not in current_config["system_settings"]:
                raise HTTPException(status_code=400, detail=f"Invalid setting name: {setting_update.setting_name}")
            current_config["system_settings"][setting_update.setting_name] = setting_update.value
        
        return {"status": "success", "message": f"Updated {setting_update.setting_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-connection")
async def test_api_connection(api_type: str):
    """
    Test connection for specific API
    """
    try:
        if api_type not in current_config["api_keys"]:
            raise HTTPException(status_code=400, detail=f"Invalid API type: {api_type}")
        
        # TODO: Implement actual API connection testing
        return {
            "status": "success",
            "message": f"Successfully connected to {api_type} API",
            "timestamp": "2024-01-23T15:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
