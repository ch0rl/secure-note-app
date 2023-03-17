"""Classes for use in Note-App.py"""

from .crypto import encrypt, decrypt

class Note:
    def __init__(self, path: str):
        self.path = "app_files/" + path
        self.content = ""
        
    def read(self, key: bytes, salt: bytes):
        with open(self.path, "rb") as f:
            ciphertext = f.read()
        self.content = decrypt(ciphertext, key, salt).decode()

    def close(self, key: bytes, salt: bytes):
        ciphertext = encrypt(self.content.encode(), key, salt)
        with open(self.path, "wb") as f:
            f.write(ciphertext)
        self.content = ""
