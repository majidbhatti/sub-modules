from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from azure.storage.blob import BlobServiceClient  # optional extra "azure"
from .crypto import encrypt, decrypt
from .exceptions import FileNotFoundError


class AzureBucketClient:
    def __init__(self, bucket_name: str, *, conn_str: Optional[str] = None, container: Optional[str] = None):
        conn_str = conn_str or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            raise RuntimeError("Provide Azure connection string via arg or AZURE_STORAGE_CONNECTION_STRING env")
        self.bucket_name = bucket_name
        self._svc = BlobServiceClient.from_connection_string(conn_str)
        self._container = self._svc.get_container_client(container or bucket_name)

    # ----- API ----- #
    def upload_file(self, local: Path, remote_path: str, *, encrypt: bool = False) -> str:
        data = local.read_bytes()
        if encrypt:
            data = encrypt(data)
        self._container.upload_blob(name=remote_path, data=data, overwrite=True)
        return f"https://{self._container.account_name}.blob.core.windows.net/{self._container.container_name}/{remote_path}"

    def download_file(self, remote_path: str, local: Path, *, decrypt: bool = False) -> Path:
        try:
            stream = self._container.download_blob(remote_path)
        except Exception:  # azure raises specific HTTP errors, keep simple here
            raise FileNotFoundError(remote_path)
        data = stream.readall()
        if decrypt:
            data = decrypt(data)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(data)
        return local

    def exists(self, remote_path: str) -> bool:
        return self._container.get_blob_client(remote_path).exists()

    def remote_uri(self, remote_path: str) -> str:
        return f"https://{self._container.account_name}.blob.core.windows.net/{self._container.container_name}/{remote_path}"
