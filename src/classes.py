"""Classes for use in Note-App.py"""

import os

from typing import List, DefaultDict
from PyQt5.QtWidgets import QDialog, QMainWindow, QTreeWidgetItem, QErrorMessage

from .NoteAppUI import *
from .crypto import encrypt, decrypt


class Note(QTreeWidgetItem):
    def __init__(self, path: str, iv: bytes, is_dir: bool = False):
        super().__init__()
        
        # Set variables
        self.path = path
        self.content = ""        
        self.iv = iv
        self.is_dir = is_dir
        
        # Get filename
        self.name = os.path.basename(path)
        self.setText(0, self.name)
        
        # Save children as Notes
        self.children: List[Note] = []

    def read(self, key: bytes):
        """Read and decrypt file contents into memory."""
        with open(self.path, "rb") as f:
            ciphertext = f.read()
        self.content = decrypt(ciphertext, key, self.iv).decode()

    def close(self, key: bytes):
        """Encrypt and write file contents."""
        self.save(key)
        del self.content
        
    def save(self, key: bytes):
        """Save the note to its file."""
        ciphertext = encrypt(self.content.encode(), key, self.iv)
        with open(self.path, "wb") as f:
            f.write(ciphertext)
            
    def addChild(self, child: 'Note'):
        """Wrapper for addChild."""
        self.children.append(child)
        return super().addChild(child)


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
    def __init__(self, key: bytes, IVs: DefaultDict[str, str], parent=None):
        # Setup UI
        super().__init__(parent)
        self.setupUi(self)

        # Setup hooks
        self.tree_widget.itemClicked.connect(self.change_file_hook)
        self.new_button.clicked.connect(self.new_file_hook)
        self.delete_button.clicked.connect(self.delete_file_hook)
        self.save_button.clicked.connect(self.save_file_hook)

        # Variables
        self.current_note: Note = None
        self.key = key
        self.IVs = IVs

        # Files
        self.tree_widget.setColumnCount(1)
        
    def change_file_hook(self, current: Note, previous: Note, note_is_new=False):
        # Check if note is a directory
        if current.is_dir:
            return
        
        # Need to create entry for new note
        if note_is_new:
            os.makedirs(os.path.split(current.path)[0], exist_ok=True)
            with open(current.path, "w"): pass

        # If previous note exists, save it
        if self.current_note is not None:
            self.current_note.content = self.main_text_area.toPlainText()
            self.current_note.close(self.key)

        # Get new note
        self.current_note = current
        current.read(self.key)

        # Display note contents
        self.main_text_area.setPlainText(current.content)

    def new_file_hook(self):
        dialog = New_Note_Dialog(self)
        dialog.exec()  # Blocks until closed

        new_note_name = dialog.new_note_name

        # If not empty, user pressed "create"
        if new_note_name != "":
            # Check if note already exists
            if new_note_name in self.IVs.keys():
                err = QErrorMessage(self)
                err.showMessage(f"A file with path {new_note_name} already exists.")
            else:
                # Create new note
                dir_node: Note = self.tree_widget.topLevelItem(0)
                expanded_path = new_note_name.split("/")
                prev_path = "./app_files"
                
                # Iterate over path
                while len(expanded_path) > 1:
                    d = expanded_path.pop(0)
                    prev_path += f"/{d}"
                    
                    for i in dir_node.children:
                        if i.name == d:
                            dir_node = i
                            break
                    else:
                        # Create dir node if it doesn't exist
                        node = Note(prev_path, self.IVs[prev_path].encode(), True)
                        dir_node.addChild(node)
                        dir_node = node
                      
                # Save new note
                new_note_name = "./app_files/" + new_note_name
                new_note = Note(new_note_name, self.IVs[new_note_name].encode())
                dir_node.addChild(new_note)
                self.change_file_hook(new_note, self.current_note, True)

    def delete_file_hook(self, /, note: Note | None = None):
        if not note:
            note = self.current_note
        
        # Remove file/dir
        if note.is_dir:
            for i in note.children:
                self.delete_file_hook(note=i)
            os.removedirs(note.path)
        else:
            os.remove(note.path)

        # Remove IV
        del self.IVs[note.path]

        # Remove entry from LHS
        note.parent().removeChild(note)
        del note

        # Reset vars
        self.current_note = None
        self.main_text_area.setPlainText("")
        
    def save_file_hook(self):
        self.current_note.content = self.main_text_area.toPlainText()
        self.current_note.save(self.key)
