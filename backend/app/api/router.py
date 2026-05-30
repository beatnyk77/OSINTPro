from fastapi import APIRouter
from app.api.endpoints import ingest

api_router = APIRouter()
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])