"""Nextcloud WebDAV client for MVP."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import requests

from app.core.config import settings


@dataclass
class StoredMailFiles:
    storage_path: str
    storage_url: str


class NextcloudClient:
    def __init__(self, base_url: str | None = None, username: str | None = None, password: str | None = None):
        self.base_url = (base_url or settings.nextcloud_webdav_url).rstrip("/")
        self.username = username or settings.nextcloud_username
        self.password = password or settings.nextcloud_password

    def _mkdir(self, path: str) -> None:
        url = f"{self.base_url}/{quote(path.strip('/'))}"
        response = requests.request("MKCOL", url, auth=(self.username, self.password), timeout=30)
        if response.status_code not in {201, 405}:
            response.raise_for_status()

    def _put(self, path: str, content: bytes) -> None:
        url = f"{self.base_url}/{quote(path.strip('/'))}"
        response = requests.put(url, data=content, auth=(self.username, self.password), timeout=60)
        response.raise_for_status()

    def upload_mail_package(self, storage_folder: str, files: dict[str, bytes]) -> StoredMailFiles:
        parts = storage_folder.strip("/").split("/")
        for i in range(1, len(parts) + 1):
            self._mkdir("/".join(parts[:i]))

        for filename, content in files.items():
            self._put(f"{storage_folder.strip('/')}/{filename}", content)

        return StoredMailFiles(storage_path=storage_folder, storage_url=f"{self.base_url}/{quote(storage_folder.strip('/'))}")
