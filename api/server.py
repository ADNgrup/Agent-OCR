from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.agent import Agent
from api.routes import ocr, system
import logging

logger = logging.getLogger(__name__)

def create_app(config_path: str = None) -> FastAPI:
    if not config_path:
        config_path = "config/config.yaml"
        
    agent = Agent(config_path)
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.agent = agent
        logger.info("Agent initialized and plugins loaded")
        
        yield
        
        logger.info("Shutting down agent...")
        for plugin in agent.registry._services.values():
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
    
    app = FastAPI(
        title="Agent API",
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(system.router, prefix="/api/v1")
    app.include_router(ocr.router, prefix="/api/v1")
    
    return app
