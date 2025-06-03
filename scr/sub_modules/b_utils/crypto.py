from __future__ import annotations
import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 256-bit key read from env var to avoid hard-coding secrets
_KEY_ENV = "BUCKET_UTILS_AES_KEY"  # must be 32 random bytes (base64url)


def _get_key() -> bytes:
    raw = os.getenv(_KEY_ENV)
    if not raw:
        raise RuntimeError(f"Set {_KEY_ENV} env var to a base64url-encoded 32-byte key")
    return urlsafe_b64decode(raw)


def encrypt(data: bytes) -> bytes:
    key = _get_key()
    aes = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit random nonce
    return nonce + aes.encrypt(nonce, data, None)


def decrypt(blob: bytes) -> bytes:
    key = _get_key()
    aes = AESGCM(key)
    nonce, ct = blob[:12], blob[12:]
    return aes.decrypt(nonce, ct, None)
