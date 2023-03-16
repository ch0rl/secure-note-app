# secure-note-app
![Code Check](https://github.com/ch0rl/secure-note-app/actions/workflows/lint.yml/badge.svg)
A "secure" note taking app that encrypts all data that isn't in use.

## app_files/
### manifest.json
```json
{
    "PASSWORD HASH": "hashlib.pbkdf2_hmac hash of the user's password.",
    "PASSWORD_SALT": "pseudo-random password hash used above.",
    "FILES": [
        "filename"
    ]
}
```
