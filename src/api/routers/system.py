from fastapi import APIRouter, HTTPException, WebSocket, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ..schemas.base import SystemStatus
import psutil
import time

router = APIRouter()

# System start time for uptime calculation
START_TIME = time.time()

# Temporary in-memory storage for logs
system_logs = []
connected_clients = set()

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    Get current system status and performance metrics
    """
    try:
        return {
            "uptime": time.time() - START_TIME,
            "active_connections": len(connected_clients),
            "api_status": {
                "twitter": True,
                "gmgn": True,
                "pumpfun": True,
                "solana_sniffer": True
            },
            "memory_usage": psutil.Process().memory_percent(),
            "error_rate": 0.0,  # TODO: Implement error rate tracking
            "trading_performance": {
                "daily_pnl": 0.0,
                "win_rate": 0.0,
                "average_trade_duration": 0.0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query("info", description="Log level filter"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, description="Maximum number of logs to return")
):
    """
    Get system logs with filtering options
    """
    try:
        filtered_logs = system_logs
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        if start_time:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_time]
        if end_time:
            filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_time]
        return filtered_logs[-limit:]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mode/{mode}")
async def set_operating_mode(mode: str):
    """
    Set system operating mode (monitor/auto)
    """
    try:
        if mode not in ["monitor", "auto"]:
            raise HTTPException(status_code=400, detail="Invalid mode. Must be 'monitor' or 'auto'")
        # TODO: Implement mode switching logic
        return {"status": "success", "message": f"System mode set to {mode}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restart")
async def restart_system():
    """
    Restart the system
    """
    try:
        # TODO: Implement proper system restart logic
        return {"status": "success", "message": "System restart initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    """
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Handle incoming messages
            data = await websocket.receive_text()
            # TODO: Implement message handling logic
            
            # Send updates to client
            await websocket.send_json({
                "type": "update",
                "data": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "system_status": await get_system_status()
                }
            })
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        connected_clients.remove(websocket)

@router.get("/metrics")
async def get_system_metrics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """
    Get detailed system performance metrics
    """
    try:
        # TODO: Implement metrics collection
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_stats": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            },
            "process_stats": {
                "threads": psutil.Process().num_threads(),
                "open_files": len(psutil.Process().open_files()),
                "connections": len(psutil.Process().connections())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-logs")
async def clear_system_logs():
    """
    Clear system logs
    """
    try:
        system_logs.clear()
        return {"status": "success", "message": "System logs cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
