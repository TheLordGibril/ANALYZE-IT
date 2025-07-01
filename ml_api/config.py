import os
from dotenv import load_dotenv
from urllib.parse import quote_plus


class Config:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self._valider_config()

    def _valider_config(self):
        params_obligatoires = {
            'DB_NAME': self.db_name,
            'DB_USER': self.db_user,
            'DB_PASSWORD': self.db_password
        }
        params_manquants = [param for param,
                            valeur in params_obligatoires.items() if not valeur]
        if params_manquants:
            raise ValueError(
                f"Paramètres de configuration manquants: {', '.join(params_manquants)}"
            )

    def get_database_url(self):
        password = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?client_encoding=utf8"


config = Config()
