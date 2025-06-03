from __future__ import annotations
from pathlib import Path

from google.cloud import storage  # requires optional extra "gcp"
from .crypto import encrypt, decrypt
from .exceptions import FileNotFoundError


class GCPBucketClient:
    def __init__(self, bucket_name: str, *, project: str | None = None, credentials_path: str | None = None):
        self.bucket_name = bucket_name
        client_args = {}
        if credentials_path:
            client_args["credentials_path"] = credentials_path
        if project:
            client_args["project"] = project
        self._client = storage.Client(**client_args)
        self._bucket = self._client.bucket(bucket_name)

    # --------- API --------- #
    def upload_file(self, local: Path, remote_path: str, *, encrypt: bool = False) -> str:
        blob = self._bucket.blob(remote_path)
        data = local.read_bytes()
        if encrypt:
            data = encrypt(data)
        blob.upload_from_string(data)
        return f"gs://{self.bucket_name}/{remote_path}"

    def download_file(self, remote_path: str, local: Path, *, decrypt: bool = False) -> Path:
        blob = self._bucket.blob(remote_path)
        if not blob.exists():
            raise FileNotFoundError(remote_path)
        data = blob.download_as_bytes()
        if decrypt:
            data = decrypt(data)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(data)
        return local

    def exists(self, remote_path: str) -> bool:
        return self._bucket.blob(remote_path).exists()

    def remote_uri(self, remote_path: str) -> str:
        return f"gs://{self.bucket_name}/{remote_path}"
