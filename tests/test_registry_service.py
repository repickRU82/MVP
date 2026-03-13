from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.entities import Company, Domain, Mailbox, RecordType, Status
from app.schemas.registry import RegistryRecordCreate
from app.services.registry.service import DuplicateMessageError, RegistryService


def setup_db() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def seed(session: Session) -> None:
    session.add(Company(id=1, name="Agro Fregat", code="AGF"))
    session.add(Domain(id=1, company_id=1, domain_name="agf.local", code="AGF"))
    session.add(
        Mailbox(
            id=1,
            company_id=1,
            domain_id=1,
            email="info@agf.local",
            imap_host="imap.local",
            imap_username="info",
            imap_password_encrypted="enc",
            prefix_code="AGF",
        )
    )
    session.add(Status(id=1, code="registered", name="Зарегистрировано"))
    session.commit()


def test_create_record_and_duplicate_detection() -> None:
    db = setup_db()
    seed(db)
    service = RegistryService(db)

    created = service.create_record(
        RegistryRecordCreate(
            record_type=RecordType.INCOMING,
            company_id=1,
            domain_id=1,
            mailbox_id=1,
            status_id=1,
            message_id="<a@a>",
            message_hash="hash-1",
            subject="Hello",
        )
    )

    assert created.registry_number.startswith("AGF-ВХ-")

    try:
        service.create_record(
            RegistryRecordCreate(
                record_type=RecordType.INCOMING,
                company_id=1,
                domain_id=1,
                mailbox_id=1,
                status_id=1,
                message_id="<a@a>",
            )
        )
        raise AssertionError("Expected DuplicateMessageError")
    except DuplicateMessageError:
        pass
