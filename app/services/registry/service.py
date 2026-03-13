from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.entities import AuditLog, RegistryRecord
from app.repositories.registry import RegistryRepository
from app.schemas.registry import RegistryFilters, RegistryRecordCreate, RegistryRecordUpdate
from app.services.numbering.service import next_registry_number


class DuplicateMessageError(Exception):
    pass


class RegistryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RegistryRepository(db)

    def list_records(self, filters: RegistryFilters) -> list[RegistryRecord]:
        return self.repo.list(filters)

    def create_record(self, payload: RegistryRecordCreate, created_by: int | None = None) -> RegistryRecord:
        duplicate_conditions = []
        if payload.message_id:
            duplicate_conditions.append(RegistryRecord.message_id == payload.message_id)
        if payload.message_hash:
            duplicate_conditions.append(RegistryRecord.message_hash == payload.message_hash)
        if duplicate_conditions:
            duplicate = self.db.scalar(
                select(RegistryRecord.id).where(
                    and_(RegistryRecord.mailbox_id == payload.mailbox_id, or_(*duplicate_conditions))
                )
            )
            if duplicate:
                raise DuplicateMessageError("Письмо уже зарегистрировано")

        registry_number = next_registry_number(self.db, payload.company_id, payload.record_type)
        record = RegistryRecord(**payload.model_dump(), registry_number=registry_number, created_by=created_by)
        self.repo.create(record)
        self.db.add(AuditLog(entity_type="registry_records", entity_id=record.id, action="created", user_id=created_by))
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_record(self, record_id: int, payload: RegistryRecordUpdate, user_id: int | None = None) -> RegistryRecord | None:
        record = self.repo.get(record_id)
        if not record:
            return None

        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(record, field, value)

        self.db.add(AuditLog(entity_type="registry_records", entity_id=record.id, action="updated", user_id=user_id))
        self.db.commit()
        self.db.refresh(record)
        return record
