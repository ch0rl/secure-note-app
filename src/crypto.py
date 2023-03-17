"""Simple AES wrappers."""

import hashlib
from Crypto.Cipher import AES

from .config import *


def encrypt(plaintext: bytes, key: bytes, salt: bytes) -> bytes:
    cipher = AES.new(hashlib.pbkdf2_hmac(
        "sha256", key, salt, PBKD_ITERATIONS
    ), AES.MODE_CBC, IV)
    return cipher.encrypt(plaintext + (" "*(16 - (len(plaintext) % 16))).encode())


def decrypt(ciphertext: bytes, key: bytes, salt: bytes) -> bytes:
    cipher = AES.new(hashlib.pbkdf2_hmac(
        "sha256", key, salt, PBKD_ITERATIONS
    ), AES.MODE_CBC, IV)
    return cipher.decrypt(ciphertext)
