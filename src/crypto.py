"""Simple crypto wrappers."""

import hashlib
from Crypto.Cipher import AES
from Crypto.Random import random

from .config import *


def encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(plaintext + (" " * (16 - (len(plaintext) % 16))).encode())


def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.decrypt(ciphertext)


def _hash(x: bytes) -> bytes:
    return hashlib.sha256(x).digest()


def new_IV() -> str:
    return "".join(chr(random.choice(INT_CHAR_INDEX)) for _ in range(16))
