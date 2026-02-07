from fastapi import APIRouter, Depends
from api.deps import get_agent
from core.agent import Agent

router = APIRouter(tags=["system"])

@router.get("/health")
async def health_check(agent: Agent = Depends(get_agent)):
    plugin_status = {}
    for category in agent.registry._services:
        plugin = agent.registry._services[category]
        plugin_status[category] = plugin.health_check()
    
    return {
        "status": "healthy" if all(plugin_status.values()) else "degraded",
        "plugins": plugin_status,
        "version": agent.config.get('agent.version', '0.1.0')
    }

@router.get("/plugins/{category}")
async def list_plugins(category: str, agent: Agent = Depends(get_agent)):
    plugins = agent.registry.list_category(category)
    return {
        "category": category,
        "active": agent.config.get(f'plugins.{category}.active'),
        "plugins": {
            name: {
                "version": p.version,
                "healthy": p.health_check()
            }
            for name, p in plugins.items()
        }
    }
