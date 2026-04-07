from fastapi import APIRouter

from backend.runtime import model_manager, resource_monitor, sqlite_memory

router = APIRouter()


@router.get("/status")
def models_status():
    available = model_manager.available_models()
    return {
        "available_models": available,
        "routing_profiles": {
            "general_chat": model_manager.describe_routing("general_chat"),
            "code_generation": model_manager.describe_routing("code_generation"),
            "training": model_manager.describe_routing("training"),
        },
        "resources": resource_monitor.snapshot(),
        "recent_decisions": sqlite_memory.latest_model_decisions(limit=10),
    }
