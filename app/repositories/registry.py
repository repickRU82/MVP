from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entities import RegistryRecord
from app.schemas.registry import RegistryFilters


class RegistryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, filters: RegistryFilters) -> list[RegistryRecord]:
        stmt = select(RegistryRecord)
        if filters.q:
            term = f"%{filters.q}%"
            stmt = stmt.where(
                or_(
                    RegistryRecord.registry_number.ilike(term),
                    RegistryRecord.subject.ilike(term),
                    RegistryRecord.from_email.ilike(term),
                    RegistryRecord.to_emails.ilike(term),
                )
            )
        if filters.record_type:
            stmt = stmt.where(RegistryRecord.record_type == filters.record_type)
        if filters.company_id:
            stmt = stmt.where(RegistryRecord.company_id == filters.company_id)
        if filters.mailbox_id:
            stmt = stmt.where(RegistryRecord.mailbox_id == filters.mailbox_id)
        if filters.status_id:
            stmt = stmt.where(RegistryRecord.status_id == filters.status_id)
        return list(self.db.scalars(stmt.order_by(RegistryRecord.registered_at.desc())).all())

    def get(self, record_id: int) -> RegistryRecord | None:
        return self.db.get(RegistryRecord, record_id)

    def create(self, record: RegistryRecord) -> RegistryRecord:
        self.db.add(record)
        self.db.flush()
        return record
