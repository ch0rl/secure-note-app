"""General config for Note-App.py"""

from string import digits, ascii_letters, punctuation

CHAR_INDEX = list(digits + ascii_letters + punctuation)
INT_CHAR_INDEX = list(map(ord, CHAR_INDEX))

PBKD_ITERATIONS = 500_000
