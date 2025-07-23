import json
import os
from pathlib import Path
from .helper import setup_logging

logger = setup_logging()

class ConfigManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.credential_file = self.config_dir / "credentials.json"
        self.template_file = self.config_dir / "credentials.json.template"

    def setup_config(self):
        """Membuat file konfigurasi jika belum ada"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            if not self.credential_file.exists():
                logger.warning("File credentials.json tidak ditemukan, membuat dari template...")
                
                if not self.template_file.exists():
                    self._create_template()
                
                self.credential_file.write_text(self.template_file.read_text())
                logger.info("File credentials.json berhasil dibuat dari template")
            
            return self._load_config()
            
        except Exception as e:
            logger.error(f"Gagal menyiapkan konfigurasi: {e}", exc_info=True)
            raise

    def _create_template(self):
        template = {
            "api_id": "ISI_DENGAN_API_ID_ANDA",
            "api_hash": "ISI_DENGAN_API_HASH_ANDA",
            "bot_token": "ISI_DENGAN_BOT_TOKEN_ANDA"
        }
        self.template_file.write_text(json.dumps(template, indent=4))
        logger.info("File template credentials.json berhasil dibuat")

    def _load_config(self):
        try:
            with open(self.credential_file) as f:
                config = json.load(f)
            
            # Validasi config
            required_keys = ["api_id", "api_hash", "bot_token"]
            if not all(key in config for key in required_keys):
                raise ValueError("Konfigurasi tidak lengkap")
                
            return config
            
        except Exception as e:
            logger.error(f"Gagal memuat konfigurasi: {e}", exc_info=True)
            raise
