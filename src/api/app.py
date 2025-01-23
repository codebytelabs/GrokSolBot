from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import time
from datetime import datetime
import logging
from typing import Callable
from .websocket.handler import manager as websocket_manager, handle_websocket_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="GrokSolBot API",
    description="API for Solana Memecoin Trading System",
    version="1.0.0"
)

# Middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Process Time: {process_time:.4f}s"
    )
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "API is running",
            "timestamp": datetime.utcnow().isoformat()
        },
        status_code=200
    )

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await handle_websocket_message(websocket, message)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        websocket_manager.disconnect(websocket)

# Import and include routers
from .routers import tokens, config, system, trades

app.include_router(tokens.router, prefix="/api/tokens", tags=["tokens"])
app.include_router(config.router, prefix="/api/config", tags=["configuration"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up GrokSolBot API")
    # TODO: Initialize database connection
    # TODO: Load configuration
    # TODO: Start background tasks

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down GrokSolBot API")
    # TODO: Close database connection
    # TODO: Clean up resources

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
