"""IMAP collector and email parser for MVP."""

from __future__ import annotations

import email
import hashlib
import imaplib
from dataclasses import dataclass
from email.header import decode_header, make_header
from email.message import Message


@dataclass
class ParsedAttachment:
    original_filename: str
    stored_filename: str
    mime_type: str
    content: bytes


@dataclass
class ParsedEmail:
    message_id: str | None
    subject: str | None
    from_email: str | None
    to_emails: str | None
    cc_emails: str | None
    date_raw: str | None
    body_preview: str | None
    message_hash: str
    raw_eml: bytes
    attachments: list[ParsedAttachment]


class EmailParser:
    @staticmethod
    def _decode(value: str | None) -> str | None:
        if not value:
            return None
        return str(make_header(decode_header(value)))

    def parse(self, raw_eml: bytes) -> ParsedEmail:
        msg: Message = email.message_from_bytes(raw_eml)

        attachments: list[ParsedAttachment] = []
        body_preview = ""
        for part in msg.walk():
            content_disposition = part.get_content_disposition()
            if content_disposition == "attachment":
                filename = self._decode(part.get_filename()) or "attachment.bin"
                safe_name = filename.replace(" ", "_")
                payload = part.get_payload(decode=True) or b""
                attachments.append(
                    ParsedAttachment(
                        original_filename=filename,
                        stored_filename=safe_name,
                        mime_type=part.get_content_type(),
                        content=payload,
                    )
                )
            elif part.get_content_type() in {"text/plain", "text/html"} and not body_preview:
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                body_preview = payload.decode(charset, errors="ignore")[:500]

        message_hash = hashlib.sha256(raw_eml).hexdigest()
        return ParsedEmail(
            message_id=msg.get("Message-ID"),
            subject=self._decode(msg.get("Subject")),
            from_email=self._decode(msg.get("From")),
            to_emails=self._decode(msg.get("To")),
            cc_emails=self._decode(msg.get("Cc")),
            date_raw=msg.get("Date"),
            body_preview=body_preview or None,
            message_hash=message_hash,
            raw_eml=raw_eml,
            attachments=attachments,
        )


class ImapCollector:
    def __init__(self, host: str, username: str, password: str, port: int = 993, use_ssl: bool = True):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.parser = EmailParser()

    def _client(self) -> imaplib.IMAP4:
        if self.use_ssl:
            return imaplib.IMAP4_SSL(self.host, self.port)
        return imaplib.IMAP4(self.host, self.port)

    def fetch_since_uid(self, folder: str, since_uid: int = 0) -> list[tuple[int, ParsedEmail]]:
        client = self._client()
        client.login(self.username, self.password)
        client.select(folder)
        criteria = f"UID {since_uid + 1}:*" if since_uid > 0 else "ALL"
        typ, data = client.uid("search", None, criteria)
        if typ != "OK":
            client.logout()
            return []

        parsed: list[tuple[int, ParsedEmail]] = []
        for uid in data[0].split():
            ftyp, fdata = client.uid("fetch", uid, "(RFC822)")
            if ftyp != "OK" or not fdata or not fdata[0]:
                continue
            raw_eml = fdata[0][1]
            parsed.append((int(uid), self.parser.parse(raw_eml)))

        client.logout()
        return parsed
