"""Classes for use in Note-App.py"""

import os

from PyQt5.QtWidgets import QDialog, QMainWindow, QTreeWidgetItem, QErrorMessage

from .NoteAppUI import *
from .crypto import encrypt, decrypt, new_IV


class Note:
    def __init__(self, path: str, iv: bytes):
        self.path = "app_files/" + path
        self.content = ""
        self.iv = iv
        
    def read(self, key: bytes, salt: bytes):
        """Read and decrypt file contents into memory."""
        with open(self.path, "rb") as f:
            ciphertext = f.read()
        self.content = decrypt(ciphertext, key, salt, self.iv).decode()

    def close(self, key: bytes, salt: bytes):
        """Encrypt and write file contents."""
        ciphertext = encrypt(self.content.encode(), key, salt, self.iv)
        with open(self.path, "wb") as f:
            f.write(ciphertext)
            
        del self.content


class New_Note_Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        # Setup UI
        super().__init__(parent)
        self.setupUi(self)
        
        # Setup hooks
        self.cancel_button.clicked.connect(lambda: self.__exit(False))
        self.create_button.clicked.connect(lambda: self.__exit(True))
        
        self.new_note_name = ""
    
    def __exit(self, save: bool):
        if not save:
            self.close()
        else:
            self.new_note_name = self.lineEdit.text()
            self.close()


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, key: bytes, manifest, parent=None):
        # Setup UI
        super().__init__(parent)
        self.setupUi(self)
        
        # Setup hooks
        self.tree_widget.itemClicked.connect(self.change_file_hook)
        self.new_button.clicked.connect(self.new_file_hook)
        self.delete_button.clicked.connect(self.delete_file_hook)
        
        # Variables
        self.current_note: Note = None
        self.current_widget: QTreeWidgetItem = None
        self.key = key
        self.manifest = manifest
        
        # Files
        self.tree_widget.setColumnCount(1)
        self.tree_widget.insertTopLevelItems(
            0, map(lambda x: QTreeWidgetItem(None, [x]), self.manifest["IVs"].keys())
        )
        
    def change_file_hook(self, current: QTreeWidgetItem, previous: QTreeWidgetItem, note_is_new=False):
        # Need to create entry for new note
        if note_is_new:
            self.manifest["IVs"][current.text(0)] = new_IV()
            with open(f"app_files/{current.text(0)}", "w") as f: pass
            
        # If previous note exists, save it
        if self.current_note is not None:
            self.current_note.content = self.main_text_area.toPlainText()
            self.current_note.close(self.key, self.key)
        
        # Get new note
        self.current_note = Note(current.text(0), self.manifest["IVs"][current.text(0)].encode())
        self.current_note.read(self.key, self.key)
        self.current_widget = current
        
        # Display note contents
        self.main_text_area.setPlainText(self.current_note.content)

    def new_file_hook(self):
        dialog = New_Note_Dialog(self)
        dialog.exec()  # Blocks until closed
        
        # If not empty, user pressed "create"
        if dialog.new_note_name != "":
            # Check if note already exists
            for i in self.manifest["IVs"].keys():
                if i == dialog.new_note_name:
                    err = QErrorMessage(self)
                    err.showMessage(f"A file with name {i} already exists.")
                    break
            else:
                # Create new note
                new_note_widget = QTreeWidgetItem(None, [dialog.new_note_name])
                self.tree_widget.insertTopLevelItem(0, new_note_widget)
                self.change_file_hook(new_note_widget, None, note_is_new=True)
                
    def delete_file_hook(self):
        # Remove file
        os.remove(self.current_note.path)
        
        # Remove info from memory
        del self.current_note
        del self.manifest["IVs"][self.current_widget.text(0)]
        
        # Remove entry from LHS
        self.tree_widget.removeItemWidget(self.current_widget, 0)
        
        # Reset vars
        self.current_note = None
        self.current_widget = None
        self.main_text_area.setPlainText("")
