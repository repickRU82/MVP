from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecordType(StrEnum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(64))
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    domain_name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Mailbox(Base):
    __tablename__ = "mailboxes"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255))
    imap_host: Mapped[str] = mapped_column(String(255), nullable=False)
    imap_port: Mapped[int] = mapped_column(Integer, default=993, nullable=False)
    imap_username: Mapped[str] = mapped_column(String(255), nullable=False)
    imap_password_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    imap_use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    inbox_folder: Mapped[str] = mapped_column(String(128), default="INBOX", nullable=False)
    sent_folder: Mapped[str] = mapped_column(String(128), default="Sent", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prefix_code: Mapped[str] = mapped_column(String(16), nullable=False)
    last_inbox_uid: Mapped[int | None] = mapped_column(Integer)
    last_sent_uid: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    record_type: Mapped[str | None] = mapped_column(String(16))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RegistryRecord(Base):
    __tablename__ = "registry_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    record_type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    registry_number: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"), nullable=False)
    mailbox_id: Mapped[int] = mapped_column(ForeignKey("mailboxes.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("statuses.id"), nullable=False)
    from_name: Mapped[str | None] = mapped_column(String(255))
    from_email: Mapped[str | None] = mapped_column(String(255))
    to_emails: Mapped[str | None] = mapped_column(Text)
    cc_emails: Mapped[str | None] = mapped_column(Text)
    bcc_emails: Mapped[str | None] = mapped_column(Text)
    reply_to: Mapped[str | None] = mapped_column(String(255))
    subject: Mapped[str | None] = mapped_column(String(1000))
    body_preview: Mapped[str | None] = mapped_column(Text)
    message_id: Mapped[str | None] = mapped_column(String(512))
    thread_key: Mapped[str | None] = mapped_column(String(512))
    mail_uid: Mapped[int | None] = mapped_column(Integer)
    mail_folder: Mapped[str | None] = mapped_column(String(128))
    message_hash: Mapped[str | None] = mapped_column(String(128))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    has_attachments: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attachments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(1024))
    storage_url: Mapped[str | None] = mapped_column(String(1024))
    linked_record_id: Mapped[int | None] = mapped_column(ForeignKey("registry_records.id"))
    responsible_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    attachments: Mapped[list["Attachment"]] = relationship(back_populates="record", cascade="all,delete")

    __table_args__ = (
        Index("ix_registry_records_registry_number", "registry_number"),
        Index("ix_registry_records_message_id", "message_id"),
        Index("ix_registry_records_record_type", "record_type"),
        Index("ix_registry_records_received_at", "received_at"),
        Index("ix_registry_records_sent_at", "sent_at"),
        Index("ix_registry_records_mailbox_id", "mailbox_id"),
        Index("ix_registry_records_status_id", "status_id"),
        Index("ix_registry_records_responsible_user_id", "responsible_user_id"),
        Index("ix_registry_records_from_email", "from_email"),
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("registry_records.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(Integer)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    storage_url: Mapped[str | None] = mapped_column(String(1024))
    checksum: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    record: Mapped[RegistryRecord] = relationship(back_populates="attachments")


class RegistryCounter(Base):
    __tablename__ = "registry_counters"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    record_type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    last_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("company_id", "year", "record_type", name="uq_counter_scope"),)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    details_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
