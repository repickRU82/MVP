from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.registry import RegistryFilters, RegistryRecordCreate, RegistryRecordRead, RegistryRecordUpdate
from app.services.export.xlsx_exporter import export_records_to_xlsx
from app.services.registry.service import DuplicateMessageError, RegistryService

router = APIRouter(prefix="/registry", tags=["registry"])


@router.get("", response_model=list[RegistryRecordRead])
def list_registry(
    q: str | None = None,
    record_type: str | None = None,
    company_id: int | None = None,
    mailbox_id: int | None = None,
    status_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = RegistryService(db)
    filters = RegistryFilters(
        q=q,
        record_type=record_type,
        company_id=company_id,
        mailbox_id=mailbox_id,
        status_id=status_id,
    )
    return service.list_records(filters)


@router.post("", response_model=RegistryRecordRead, status_code=201)
def create_registry(payload: RegistryRecordCreate, db: Session = Depends(get_db)):
    service = RegistryService(db)
    try:
        return service.create_record(payload)
    except DuplicateMessageError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.patch("/{record_id}", response_model=RegistryRecordRead)
def update_registry(record_id: int, payload: RegistryRecordUpdate, db: Session = Depends(get_db)):
    service = RegistryService(db)
    record = service.update_record(record_id, payload)
    if record is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return record


@router.get("/export/xlsx")
def export_registry(db: Session = Depends(get_db)):
    service = RegistryService(db)
    rows = service.list_records(RegistryFilters())
    content = export_records_to_xlsx(rows)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="registry_export.xlsx"'},
    )
