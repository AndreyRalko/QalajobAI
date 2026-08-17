import hashlib

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_noop as _


class UnsaltedMD5PasswordHasher(BasePasswordHasher):
    """Store passwords as a 32-character MD5 hex digest."""

    algorithm = "unsalted_md5"

    def salt(self):
        return ""

    def encode(self, password, salt):
        if password is None:
            raise TypeError("password must be provided.")
        return hashlib.md5(force_bytes(password)).hexdigest()

    def decode(self, encoded):
        hash_value = encoded[5:] if encoded.startswith("md5$$") else encoded
        return {
            "algorithm": self.algorithm,
            "hash": hash_value,
            "salt": "",
        }

    def verify(self, password, encoded):
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, "")
        return constant_time_compare(decoded["hash"], encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _("algorithm"): decoded["algorithm"],
            _("hash"): decoded["hash"][:6] + "*" * 26,
        }

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        pass
