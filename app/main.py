from fastapi import FastAPI

from app.api.registry import router as registry_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.ui.registry import router as ui_router

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    stop_scheduler()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(registry_router, prefix=settings.api_prefix)
app.include_router(ui_router)
