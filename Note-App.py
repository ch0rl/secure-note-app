"""A simple, "secure", note taking app.

(c) chorl [github.com/ch0rl]
Licensed under GPLv3
"""

import sys
import json
import hashlib
import getpass
from collections import defaultdict
from typing import Dict, Tuple, DefaultDict

from PyQt5.QtWidgets import QApplication

from src.classes import *
from src.config import *
from src.crypto import _hash, new_IV


def setup() -> Tuple[bytes, DefaultDict]:
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

    # Make IVs a defaultdict
    manifest["IVs"] = defaultdict(new_IV, manifest["IVs"])
    
    return pbkdf2, manifest


def load_files(head: Note, IVs: DefaultDict):
    """Load files/directories into the tree."""
    
    def __recurse_dir(dir: str, current_dir_node: Note):
        # Go through directories
        for d in filter(
            lambda x: os.path.isdir(os.path.join(dir, x)), os.listdir(dir)
        ):
            d = os.path.join(dir, d)
            dir_node = Note(d, IVs[d].encode(), True)
            current_dir_node.addChild(dir_node)
            
            __recurse_dir(d, dir_node)
        
        # Go through files
        for f in filter(
            lambda x: os.path.isfile(os.path.join(dir, x)), os.listdir(dir)
        ):
            f = os.path.join(dir, f)
            # Ignore manifest
            if f == "./app_files/manifest.json": continue
            
            current_dir_node.addChild(Note(f, IVs[f].encode()))        
        
    __recurse_dir("./app_files/", head)


if __name__ == "__main__":
    # Setup manifest
    key, manifest = setup()

    # Start window
    app = QApplication(sys.argv)
    win = Window(key, manifest["IVs"])
    
    # Load tree
    head = Note("./app_files", bytes(0), True)
    load_files(head, manifest["IVs"])
    win.tree_widget.addTopLevelItem(head)
    
    win.show()

    exit_code = app.exec()

    # Clean shutdown
    if win.current_note is not None:
        win.current_note.close(key)
    
    with open("app_files/manifest.json", "w") as f:
        json.dump(manifest, f)
