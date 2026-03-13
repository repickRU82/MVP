from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, UserRole, get_current_user
from app.db.session import get_db
from app.schemas.registry import RegistryFilters
from app.services.registry.service import RegistryService

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/registry", response_class=HTMLResponse)
def registry_page(
    request: Request,
    q: str | None = None,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    if user.role not in {UserRole.ADMIN, UserRole.OPERATOR, UserRole.MANAGER, UserRole.EXECUTOR}:
        return HTMLResponse("Недостаточно прав", status_code=403)

    service = RegistryService(db)
    filters = RegistryFilters(q=q, responsible_user_id=user.user_id if user.role == UserRole.EXECUTOR else None)
    records = service.list_records(filters)
    return templates.TemplateResponse(
        request,
        "registry.html",
        {"records": records, "q": q or "", "user": user},
    )
