from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Company, RecordType, RegistryCounter


TYPE_PREFIX = {
    RecordType.INCOMING: "ВХ",
    RecordType.OUTGOING: "ИСХ",
}


def next_registry_number(db: Session, company_id: int, record_type: RecordType) -> str:
    year = datetime.now(UTC).year
    counter = db.scalar(
        select(RegistryCounter).where(
            RegistryCounter.company_id == company_id,
            RegistryCounter.year == year,
            RegistryCounter.record_type == record_type,
        )
    )
    if counter is None:
        counter = RegistryCounter(company_id=company_id, year=year, record_type=record_type, last_number=0)
        db.add(counter)
        db.flush()

    counter.last_number += 1
    company = db.get(Company, company_id)
    company_code = company.code if company else "ORG"
    return f"{company_code}-{TYPE_PREFIX[record_type]}-{year}-{counter.last_number:06d}"
