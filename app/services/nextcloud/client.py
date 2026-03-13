"""Nextcloud WebDAV client stub for MVP."""

from dataclasses import dataclass


@dataclass
class StoredMailFiles:
    storage_path: str
    storage_url: str


class NextcloudClient:
    def upload_mail_package(self, registry_number: str, files: dict[str, bytes]) -> StoredMailFiles:
        base_path = f"/Документооборот/Реестр писем/{registry_number}"
        return StoredMailFiles(storage_path=base_path, storage_url=base_path)
