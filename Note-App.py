"""A simple, "secure", note taking app.

(c) chorl [github.com/ch0rl]
Licensed under GPLv3
"""

import sys
import json
import hashlib
import getpass
from typing import Dict, Tuple

from PyQt5.QtWidgets import QApplication

from src.classes import *
from src.config import *
from src.crypto import _hash, new_IV


def setup() -> Tuple[bytes, Dict]:
    """Loads and returns the password (pbkdf2 thereof) and manifest."""
    with open("app_files/manifest.json") as f:
        manifest = json.load(f)

    if manifest["PASSWORD HASH"] == "":
        # Get new password with no echo
        password = getpass.getpass(
            "[!] No password has been set, set one now:\n> ")

        # Generate salt
        manifest["PASSWORD SALT"] = new_IV()
        print(f"[+] Salt: " + manifest["PASSWORD SALT"])

        # Hash password
        manifest["PASSWORD HASH"] = _hash(password.encode()).hex()

        # Store manifest
        with open("app_files/manifest.json", "w") as f:
            json.dump(manifest, f)

        print("[+] Password & Salt saved.")
    else:
        # Get password attempt with no echo
        password = getpass.getpass("[!] Enter your password:\n> ")

        if _hash(password.encode()).hex() != manifest["PASSWORD HASH"]:
            print("[!] Incorrect password.")
            exit(1)

    # Get PBKDF2 of password
    pbkdf2 = hashlib.pbkdf2_hmac("sha256", password.encode(), 
        manifest["PASSWORD SALT"].encode(), PBKD_ITERATIONS
    )

    del password

    return pbkdf2, manifest


if __name__ == "__main__":
    # Setup manifest
    key, manifest = setup()

    # Start window
    app = QApplication(sys.argv)
    win = Window(key, manifest)
    win.show()

    exit_code = app.exec()

    # Clean shutdown
    if win.current_note is not None:
        win.current_note.close(key)
    
    with open("app_files/manifest.json", "w") as f:
        json.dump(manifest, f)
