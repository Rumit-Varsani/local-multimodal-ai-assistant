from fastapi import APIRouter

from backend.runtime import project_phase_service

router = APIRouter()


@router.get("/phases")
def project_phases():
    return project_phase_service.summary()
