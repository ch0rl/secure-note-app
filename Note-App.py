"""A simple, "secure", note taking app.

(c) chorl [github.com/ch0rl]
Licensed under GPLv3
"""

import sys
import json
import hashlib
import getpass
from Crypto.Random import random

from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal

from src.NoteAppUI import Ui_MainWindow
from src.classes import *
from src.config import *


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, key: bytes, manifest, parent=None):
        # Setup UI
        super().__init__(parent)
        self.setupUi(self)
        
        # Setup hooks
        self.tree_widget.itemClicked.connect(self.change_file_hook)
        
        # Variables
        self.current_note: Note = None
        self.key = key
        self.manifest = manifest
        
        # Files
        self.tree_widget.setColumnCount(1)
        self.tree_widget.insertTopLevelItems(
            0, map(lambda x: QTreeWidgetItem(None, [x]), self.manifest["FILES"])
        )
        
    def change_file_hook(self, current: QTreeWidgetItem, previous: QTreeWidgetItem):
        if self.current_note is not None:
            self.current_note.content = self.main_text_area.toPlainText()
            self.current_note.close(self.key, bytes.fromhex(self.manifest["PASSWORD HASH"]))
        
        self.current_note = Note(current.text(0))
        self.current_note.read(self.key, bytes.fromhex(self.manifest["PASSWORD HASH"]))
        
        self.main_text_area.setPlainText(self.current_note.content)


if __name__ == "__main__":
    with open("app_files/manifest.json") as f:
        manifest = json.load(f)
        
    if manifest["PASSWORD HASH"] == "":
        password = getpass.getpass("[!] No password has been set, set one now:\n> ")
        
        manifest["PASSWORD SALT"] = "".join(
            chr(random.choice(INT_CHAR_INDEX)) for _ in range(20)
        )
        print(f"[+] Salt: " + manifest["PASSWORD SALT"])
        
        manifest["PASSWORD HASH"] = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), manifest["PASSWORD SALT"].encode(), PBKD_ITERATIONS
        ).hex()
        
        with open("app_files/manifest.json", "w") as f:
            json.dump(manifest, f)
        
        print("[+] Password saved.")
    else:
        password = getpass.getpass("[!] Enter your password:\n> ")
        
        if hashlib.pbkdf2_hmac(
            "sha256", password.encode(), manifest["PASSWORD SALT"].encode(), PBKD_ITERATIONS
        ).hex() != manifest["PASSWORD HASH"]:
            print("[!] Incorrect password.")
            exit(1)
    
    app = QApplication(sys.argv)
    win = Window(password.encode(), manifest)
    win.show()
    
    exit_code = app.exec()
    
    win.current_note.close(password.encode(), manifest["PASSWORD SALT"].encode())    
    with open("app_files/manifest.json", "w") as f:
        json.dump(manifest, f)
