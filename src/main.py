import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the application
    """
    try:
        logger.info("Starting GrokSolBot application")
        
        # Import the FastAPI app
        from api import app
        
        # Get configuration from environment variables
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        reload = os.getenv("API_RELOAD", "true").lower() == "true"
        
        # Run the FastAPI application
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
