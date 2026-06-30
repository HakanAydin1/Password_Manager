import json
import os
from crypto_utils import CryptoUtils

class DataAccess:
    @staticmethod
    def vault_exists(filepath: str) -> bool:
        return os.path.exists(filepath)
        
    @staticmethod
    def initialize_vault(filepath: str, master_password: str) -> bool:
        """
        Creates a new, empty vault file.
        Format: [16 bytes SALT] + [12 bytes NONCE + AES-256-GCM Encrypted JSON]
        """
        try:
            salt = CryptoUtils.generate_salt()
            key = CryptoUtils.derive_key(master_password, salt)
            
            empty_vault_data = {"entries": []}
            json_data = json.dumps(empty_vault_data).encode('utf-8')
            
            encrypted_payload = CryptoUtils.encrypt_data(key, json_data)
            
            with open(filepath, 'wb') as f:
                f.write(salt)
                f.write(encrypted_payload)
            return True
        except Exception as e:
            print(f"Failed to initialize vault: {e}")
            return False

    @staticmethod
    def load_vault(filepath: str, master_password: str) -> dict:
        """
        Loads and decrypts the vault.
        Returns the parsed JSON dictionary if successful.
        Raises ValueError on wrong password or corruption.
        Raises FileNotFoundError if vault doesn't exist.
        """
        if not DataAccess.vault_exists(filepath):
            raise FileNotFoundError("Vault file not found.")
            
        with open(filepath, 'rb') as f:
            salt = f.read(CryptoUtils.SALT_SIZE)
            encrypted_payload = f.read()
            
        if len(salt) != CryptoUtils.SALT_SIZE:
            raise ValueError("Vault file is corrupted.")
            
        key = CryptoUtils.derive_key(master_password, salt)
        
        # CryptoUtils.decrypt_data raises ValueError on invalid password / authentication tag fail
        plaintext = CryptoUtils.decrypt_data(key, encrypted_payload)
        
        return json.loads(plaintext.decode('utf-8'))

    @staticmethod
    def save_vault(filepath: str, master_password: str, vault_data: dict) -> bool:
        """
        Re-encrypts the vault_data and saves it. 
        Note: It reuses the old salt from the file to avoid generating a new one every save,
        but it generates a new nonce via CryptoUtils.encrypt_data inside.
        """
        if not DataAccess.vault_exists(filepath):
            raise FileNotFoundError("Vault file not found. Cannot save.")
            
        try:
            # Read the existing salt
            with open(filepath, 'rb') as f:
                salt = f.read(CryptoUtils.SALT_SIZE)
                
            key = CryptoUtils.derive_key(master_password, salt)
            
            json_data = json.dumps(vault_data).encode('utf-8')
            encrypted_payload = CryptoUtils.encrypt_data(key, json_data)
            
            with open(filepath, 'wb') as f:
                f.write(salt)
                f.write(encrypted_payload)
            return True
        except Exception as e:
            print(f"Failed to save vault: {e}")
            return False
