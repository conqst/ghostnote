from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class EncryptionManager:

    def __init__(self, password: str, salt_base64: str):

        salt = base64.b64decode(salt_base64.encode('utf-8'))

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

        self.cipher = Fernet(key)

    def encrypt(self, data: bytes) -> bytes:

        return self.cipher.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:

        return self.cipher.decrypt(token)
