"""IMAP collector stub for MVP.

Интеграция с iRedMail реализуется отдельным фоновым воркером.
"""

from dataclasses import dataclass


@dataclass
class MailEnvelope:
    message_id: str | None
    uid: int
    folder: str


class ImapCollector:
    def poll(self) -> list[MailEnvelope]:
        return []
