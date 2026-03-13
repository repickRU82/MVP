from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import RecordType


class RegistryRecordCreate(BaseModel):
    record_type: RecordType
    company_id: int
    domain_id: int
    mailbox_id: int
    status_id: int
    subject: str | None = None
    from_email: str | None = None
    to_emails: str | None = None
    message_id: str | None = None
    mail_uid: int | None = None
    mail_folder: str | None = None
    message_hash: str | None = None
    received_at: datetime | None = None
    sent_at: datetime | None = None
    has_attachments: bool = False
    attachments_count: int = 0


class RegistryRecordUpdate(BaseModel):
    status_id: int | None = None
    responsible_user_id: int | None = None
    note: str | None = None


class RegistryRecordRead(BaseModel):
    id: int
    record_type: RecordType
    registry_number: str
    company_id: int
    domain_id: int
    mailbox_id: int
    status_id: int
    subject: str | None
    from_email: str | None
    to_emails: str | None
    message_id: str | None
    responsible_user_id: int | None
    registered_at: datetime
    storage_url: str | None

    model_config = ConfigDict(from_attributes=True)


class RegistryFilters(BaseModel):
    q: str | None = Field(default=None, description="Номер/тема/email")
    record_type: RecordType | None = None
    company_id: int | None = None
    mailbox_id: int | None = None
    status_id: int | None = None
    responsible_user_id: int | None = None
