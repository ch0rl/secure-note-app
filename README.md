# secure-note-app
A "secure" note taking app that encrypts all data that isn't in use.

## app_files/
### manifest.json
```json
{
    "PASSWORD HASH": "hashlib.pbkdf2_hmac hash of the user's password.",
    "PASSWORD_SALT": "pseudo-random password hash used above.",
    "INDEX": [
        {
            "file name": "actual file name",
            "display name": "name to display in the GUI"
        }, ...
    ]
}
```
