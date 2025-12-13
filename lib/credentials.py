"""
Encrypted credential management for SLS-AH
Uses AES encryption to securely store sensitive data
"""

import os
import json
import hashlib
import platform
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2


class CredentialManager:
    """Manages encrypted storage of Steam API credentials"""
    
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.config/slsah")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.creds_file = self.config_dir / "credentials.enc"
        self.salt_file = self.config_dir / "salt.bin"
        
        # Generate or load encryption key
        self._init_encryption()
    
    def _get_machine_id(self):
        """Get a unique machine identifier for encryption key derivation"""
        system = platform.system()
        
        if system == "Linux":
            try:
                with open("/etc/machine-id", "r") as f:
                    return f.read().strip()
            except:
                pass
        
        # Fallback: use hostname + username
        import getpass
        machine_id = f"{platform.node()}-{getpass.getuser()}"
        return hashlib.sha256(machine_id.encode()).hexdigest()
    
    def _init_encryption(self):
        """Initialize encryption with machine-specific key"""
        # Get or create salt
        if self.salt_file.exists():
            with open(self.salt_file, "rb") as f:
                self.salt = f.read()
        else:
            self.salt = get_random_bytes(32)
            with open(self.salt_file, "wb") as f:
                f.write(self.salt)
            # Secure the salt file
            os.chmod(self.salt_file, 0o600)
        
        # Derive encryption key from machine ID
        machine_id = self._get_machine_id()
        self.key = PBKDF2(machine_id, self.salt, dkLen=32, count=100000)
    
    def _encrypt(self, data):
        """Encrypt data using AES-256-GCM"""
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        
        return {
            'nonce': cipher.nonce,
            'ciphertext': ciphertext,
            'tag': tag
        }
    
    def _decrypt(self, encrypted_data):
        """Decrypt data using AES-256-GCM"""
        cipher = AES.new(
            self.key,
            AES.MODE_GCM,
            nonce=encrypted_data['nonce']
        )
        
        plaintext = cipher.decrypt_and_verify(
            encrypted_data['ciphertext'],
            encrypted_data['tag']
        )
        
        return plaintext.decode('utf-8')
    
    def save_credentials(self, api_key, steam_id):
        """Save encrypted credentials to disk"""
        credentials = {
            'api_key': api_key,
            'steam_id': steam_id
        }
        
        json_data = json.dumps(credentials)
        encrypted = self._encrypt(json_data)
        
        # Convert bytes to hex for storage
        storage_data = {
            'nonce': encrypted['nonce'].hex(),
            'ciphertext': encrypted['ciphertext'].hex(),
            'tag': encrypted['tag'].hex()
        }
        
        with open(self.creds_file, 'w') as f:
            json.dump(storage_data, f)
        
        # Secure the credentials file
        os.chmod(self.creds_file, 0o600)
    
    def load_credentials(self):
        """Load and decrypt credentials from disk"""
        if not self.creds_file.exists():
            return None
        
        try:
            with open(self.creds_file, 'r') as f:
                storage_data = json.load(f)
            
            # Convert hex back to bytes
            encrypted = {
                'nonce': bytes.fromhex(storage_data['nonce']),
                'ciphertext': bytes.fromhex(storage_data['ciphertext']),
                'tag': bytes.fromhex(storage_data['tag'])
            }
            
            json_data = self._decrypt(encrypted)
            credentials = json.loads(json_data)
            
            return credentials['api_key'], credentials['steam_id']
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return None
    
    def credentials_exist(self):
        """Check if encrypted credentials exist"""
        return self.creds_file.exists()
    
    def clear_credentials(self):
        """Delete stored credentials"""
        if self.creds_file.exists():
            self.creds_file.unlink()
        # Keep salt file for potential re-encryption
    
    def migrate_from_dotenv(self, dotenv_path):
        """Migrate credentials from old .env file to encrypted storage"""
        if not os.path.exists(dotenv_path):
            return False
        
        from dotenv import dotenv_values
        env_vars = dotenv_values(dotenv_path)
        
        api_key = env_vars.get('STEAM_API_KEY')
        steam_id = env_vars.get('STEAM_USER_ID')
        
        if api_key and steam_id:
            self.save_credentials(api_key, steam_id)
            # Optionally backup and remove .env
            import shutil
            shutil.move(dotenv_path, dotenv_path + '.bak')
            return True
        
        return False
