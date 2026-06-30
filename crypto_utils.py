import os
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

class CryptoUtils:
    SALT_SIZE = 16
    NONCE_SIZE = 12

    @staticmethod
    def generate_salt() -> bytes:
        """Generates a cryptographically secure random salt."""
        return os.urandom(CryptoUtils.SALT_SIZE)

    @staticmethod
    def derive_key(master_password: str, salt: bytes) -> bytes:
        """
        Derives an encryption key from the Master Password using Scrypt.
        Key length is 32 bytes (256 bits) for AES-256.
        """
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,      # 16384 (CPU/Memory cost)
            r=8,          # Block size
            p=1,          # Parallelization factor
        )
        key = kdf.derive(master_password.encode('utf-8'))
        return key

    @staticmethod
    def encrypt_data(key: bytes, plaintext: bytes) -> bytes:
        """
        Encrypts plaintext using AES-256-GCM.
        Returns a single bytes object: NONCE + CIPHERTEXT
        """
        aesgcm = AESGCM(key)
        nonce = os.urandom(CryptoUtils.NONCE_SIZE)
        # AESGCM.encrypt creates ciphertext + authentication tag automatically
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    @staticmethod
    def decrypt_data(key: bytes, encrypted_payload: bytes) -> bytes:
        """
        Decrypts data using AES-256-GCM.
        Expects payload structure: NONCE (12 bytes) + CIPHERTEXT
        Returns plaintext or raises ValueError if decryption fails.
        """
        if len(encrypted_payload) < CryptoUtils.NONCE_SIZE + 16:
            raise ValueError("Payload too short.")
        
        nonce = encrypted_payload[:CryptoUtils.NONCE_SIZE]
        ciphertext = encrypted_payload[CryptoUtils.NONCE_SIZE:]
        
        aesgcm = AESGCM(key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext
        except InvalidTag:
            raise ValueError("Decryption failed. Incorrect master password or corrupted data.")
