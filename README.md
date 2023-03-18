# secure-note-app
A "secure" note taking app that encrypts all data that isn't in use.

## Install
1. `git clone https://github.com/ch0rl/secure-note-app.git`
2. `cd secure-note-app`
3. `pip install -r requirements`
4. `python Note-App.py`

## Details
### Files
Every file is encrypted with AES-256, with a random - per file - IV. 
The key for these files is the PBKDF2 hash of the user's password, salted with the manifest salt.

### Password
The user's password is stored as its sha256 hash.

### Salt
The password salt is generated by "random" choices from `CHAR_INDEX` in [config.py](./src/config.py), using `Crypto.Random.random`.

### Memory
Any sensitive information is removed from memory once it is no longer needed.

### Algorithms
Encryption, hashing, and IV-generation algorithms can easily be changed by changing their respective functions in [crypto.py](./src/crypto.py).

## Known Issues
- 'Delete'ing a note does not remove it from the list.
## TODO
- [x] Prototype
- [ ] Speed up processing
- [x] 'Add'/'Delete' options
- [x] Better IV per file
- [ ] Standalone? (ie., don't rely on Crypto/hashlib)
- [ ] Look nicer?
- [ ] 2fa?
- [ ] Directories
- [ ] Error handling
- [ ] Proper padding (not just spaces)
- [ ] Path handling
