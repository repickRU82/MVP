from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, UserRole, get_current_user
from app.db.session import get_db
from app.models.entities import RecordType
from app.schemas.registry import RegistryFilters, RegistryRecordCreate, RegistryRecordRead, RegistryRecordUpdate
from app.services.export.xlsx_exporter import export_records_to_xlsx
from app.services.registry.service import DuplicateMessageError, RegistryService

router = APIRouter(prefix="/registry", tags=["registry"])


def _assert_roles(user: CurrentUser, roles: set[UserRole]) -> None:
    if user.role not in roles:
        raise HTTPException(status_code=403, detail="Недостаточно прав")


@router.get("", response_model=list[RegistryRecordRead])
def list_registry(
    q: str | None = None,
    record_type: RecordType | None = None,
    company_id: int | None = None,
    mailbox_id: int | None = None,
    status_id: int | None = None,
    responsible_user_id: int | None = None,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    _assert_roles(user, {UserRole.ADMIN, UserRole.OPERATOR, UserRole.MANAGER, UserRole.EXECUTOR})
    service = RegistryService(db)
    if user.role == UserRole.EXECUTOR:
        responsible_user_id = user.user_id
    filters = RegistryFilters(
        q=q,
        record_type=record_type,
        company_id=company_id,
        mailbox_id=mailbox_id,
        status_id=status_id,
        responsible_user_id=responsible_user_id,
    )
    return service.list_records(filters)


@router.post("", response_model=RegistryRecordRead, status_code=201)
def create_registry(
    payload: RegistryRecordCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    _assert_roles(user, {UserRole.ADMIN, UserRole.OPERATOR})
    service = RegistryService(db)
    try:
        return service.create_record(payload, created_by=user.user_id)
    except DuplicateMessageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{record_id}", response_model=RegistryRecordRead)
def update_registry(
    record_id: int,
    payload: RegistryRecordUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    _assert_roles(user, {UserRole.ADMIN, UserRole.OPERATOR, UserRole.EXECUTOR})
    if user.role == UserRole.EXECUTOR and payload.responsible_user_id not in (None, user.user_id):
        raise HTTPException(status_code=403, detail="Исполнитель не может переназначать ответственного")
    service = RegistryService(db)
    record = service.update_record(record_id, payload, user_id=user.user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return record


@router.get("/export/xlsx")
def export_registry(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    _assert_roles(user, {UserRole.ADMIN, UserRole.OPERATOR, UserRole.MANAGER})
    service = RegistryService(db)
    rows = service.list_records(RegistryFilters())
    content = export_records_to_xlsx(rows)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="registry_export.xlsx"'},
    )
