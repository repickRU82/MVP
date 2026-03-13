from __future__ import annotations

import json
from datetime import datetime
from email.utils import parsedate_to_datetime

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import Attachment, Mailbox, RecordType, Status
from app.schemas.registry import RegistryRecordCreate
from app.services.imap.collector import ImapCollector
from app.services.nextcloud.client import NextcloudClient
from app.services.registry.service import DuplicateMessageError, RegistryService


def _status_id_for_record(db, record_type: RecordType) -> int:
    code = "registered" if record_type == RecordType.INCOMING else "sent"
    status = db.scalar(select(Status).where(Status.code == code))
    if status:
        return status.id
    fallback = db.scalar(select(Status).limit(1))
    if fallback:
        return fallback.id
    status = Status(code=code, name="Зарегистрировано" if record_type == RecordType.INCOMING else "Отправлено")
    db.add(status)
    db.commit()
    db.refresh(status)
    return status.id


def _record_type_by_folder(folder: str, mailbox: Mailbox) -> RecordType:
    return RecordType.INCOMING if folder == mailbox.inbox_folder else RecordType.OUTGOING


def _storage_folder(record_type: RecordType, registry_number: str, now: datetime) -> str:
    kind = "Входящие" if record_type == RecordType.INCOMING else "Исходящие"
    return f"{settings.nextcloud_root}/{kind}/{now.year:04d}/{now.month:02d}/{registry_number}"


def run_poll_cycle() -> None:
    db = SessionLocal()
    try:
        mailboxes = list(db.scalars(select(Mailbox).where(Mailbox.is_enabled.is_(True))).all())
        nextcloud = NextcloudClient()

        for mailbox in mailboxes:
            collector = ImapCollector(
                host=mailbox.imap_host,
                username=mailbox.imap_username,
                password=mailbox.imap_password_encrypted,
                port=mailbox.imap_port,
                use_ssl=mailbox.imap_use_ssl,
            )
            for folder, last_uid in (
                (mailbox.inbox_folder, mailbox.last_inbox_uid or 0),
                (mailbox.sent_folder, mailbox.last_sent_uid or 0),
            ):
                record_type = _record_type_by_folder(folder, mailbox)
                status_id = _status_id_for_record(db, record_type)
                fetched = collector.fetch_since_uid(folder, last_uid)

                for uid, message in fetched:
                    parsed_date = parsedate_to_datetime(message.date_raw) if message.date_raw else None
                    payload = RegistryRecordCreate(
                        record_type=record_type,
                        company_id=mailbox.company_id,
                        domain_id=mailbox.domain_id,
                        mailbox_id=mailbox.id,
                        status_id=status_id,
                        subject=message.subject,
                        from_email=message.from_email,
                        to_emails=message.to_emails,
                        message_id=message.message_id,
                        mail_uid=uid,
                        mail_folder=folder,
                        message_hash=message.message_hash,
                        received_at=parsed_date if record_type == RecordType.INCOMING else None,
                        sent_at=parsed_date if record_type == RecordType.OUTGOING else None,
                        has_attachments=bool(message.attachments),
                        attachments_count=len(message.attachments),
                    )
                    service = RegistryService(db)
                    try:
                        record = service.create_record(payload)
                    except DuplicateMessageError:
                        continue

                    folder_path = _storage_folder(record_type, record.registry_number, datetime.utcnow())
                    metadata = {
                        "registry_number": record.registry_number,
                        "record_type": record.record_type.value,
                        "mailbox": mailbox.email,
                        "subject": record.subject,
                        "message_id": record.message_id,
                        "registered_at": record.registered_at.isoformat() if record.registered_at else None,
                    }
                    files = {
                        "original.eml": message.raw_eml,
                        "metadata.json": json.dumps(metadata, ensure_ascii=False, indent=2).encode("utf-8"),
                    }
                    for idx, att in enumerate(message.attachments, 1):
                        files[f"attachment_{idx:02d}_{att.stored_filename}"] = att.content

                    stored = nextcloud.upload_mail_package(folder_path, files)
                    record.storage_path = stored.storage_path
                    record.storage_url = stored.storage_url
                    for idx, att in enumerate(message.attachments, 1):
                        db.add(
                            Attachment(
                                record_id=record.id,
                                original_filename=att.original_filename,
                                stored_filename=f"attachment_{idx:02d}_{att.stored_filename}",
                                mime_type=att.mime_type,
                                file_size=len(att.content),
                                storage_path=f"{stored.storage_path}/attachment_{idx:02d}_{att.stored_filename}",
                                storage_url=f"{stored.storage_url}/attachment_{idx:02d}_{att.stored_filename}",
                            )
                        )
                    db.add(record)
                    db.commit()

                    if folder == mailbox.inbox_folder:
                        mailbox.last_inbox_uid = max(mailbox.last_inbox_uid or 0, uid)
                    else:
                        mailbox.last_sent_uid = max(mailbox.last_sent_uid or 0, uid)
                    db.add(mailbox)
                    db.commit()
    finally:
        db.close()
