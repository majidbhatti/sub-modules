"""
Public façade – import this, not the backend modules.
"""
from __future__ import annotations
from pathlib import Path
from typing import Protocol, runtime_checkable

from .exceptions import FileNotFoundError


# ---------- protocol for any cloud backend ---------- #
@runtime_checkable
class BucketClient(Protocol):
    bucket_name: str

    # core operations every backend must support
    def upload_file(self, local: Path, remote_path: str, *, encrypt: bool = False) -> str: ...

    def download_file(self, remote_path: str, local: Path, *, decrypt: bool = False) -> Path: ...

    def exists(self, remote_path: str) -> bool: ...

    def remote_uri(self, remote_path: str) -> str: ...


# ---------- factory helpers ---------- #
def gcp(bucket: str, *, project: str | None = None, credentials_path: str | None = None) -> BucketClient:
    from .gcp import GCPBucketClient
    return GCPBucketClient(bucket, project=project, credentials_path=credentials_path)


def azure(bucket: str, *, conn_str: str | None = None, container: str | None = None) -> BucketClient:
    from .azure import AzureBucketClient
    return AzureBucketClient(bucket, conn_str=conn_str, container=container)
