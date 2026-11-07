import hashlib

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_noop as _

from apps.users.crypto import decrypt_password_hash, encrypt_password_hash, is_encrypted


class UnsaltedMD5PasswordHasher(BasePasswordHasher):
    """Store passwords as unsalted_md5$<Fernet(SECRET_KEY, md5_hex)>."""

    algorithm = "unsalted_md5"

    def salt(self):
        return ""

    def encode(self, password, salt):
        if password is None:
            raise TypeError("password must be provided.")
        md5_hex = hashlib.md5(force_bytes(password)).hexdigest()
        return f"{self.algorithm}${encrypt_password_hash(md5_hex)}"

    def decode(self, encoded):
        payload = encoded
        if encoded.startswith(f"{self.algorithm}$"):
            payload = encoded.split("$", 1)[1]
        if payload.startswith("md5$$"):
            payload = payload[5:]
        hash_value = decrypt_password_hash(payload) if is_encrypted(payload) else payload
        return {
            "algorithm": self.algorithm,
            "hash": hash_value,
            "salt": "",
        }

    def verify(self, password, encoded):
        decoded = self.decode(encoded)
        encoded_2 = hashlib.md5(force_bytes(password)).hexdigest()
        return constant_time_compare(decoded["hash"], encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        digest = decoded["hash"]
        visible = (digest[:6] + "*" * 26) if digest else "*" * 32
        return {
            _("algorithm"): decoded["algorithm"],
            _("hash"): visible,
        }

    def must_update(self, encoded):
        if not encoded.startswith(f"{self.algorithm}$"):
            return True
        payload = encoded.split("$", 1)[1]
        return not is_encrypted(payload)

    def harden_runtime(self, password, encoded):
        pass


def format_encrypted_md5_password(password_md5: str) -> str:
    """Store an already-computed MD5 hex under the project hasher format."""
    return f"unsalted_md5${encrypt_password_hash(password_md5)}"
