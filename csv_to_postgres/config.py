import os
import logging
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlparse

class Config:
    def __init__(self):
        load_dotenv()

        database_url = os.getenv('DATABASE_URL')

        if database_url:
            # Utiliser DATABASE_URL de Docker Compose
            self._parse_database_url(database_url)
        else:
            # Configuration base de données
            self.db_host = os.getenv('DB_HOST', 'localhost')
            self.db_port = os.getenv('DB_PORT', '5432')
            self.db_name = os.getenv('DB_NAME')
            self.db_user = os.getenv('DB_USER')
            self.db_password = os.getenv('DB_PASSWORD')
        
        # Configuration des fichiers
        self.csv_file_path = os.getenv('CSV_FILE_PATH')
        
        # Validation des paramètres obligatoires
        self._valider_config()
        
        # Configuration du logging sécurisé
        self._configurer_logging()

    def _parse_database_url(self, database_url):
        parsed = urlparse(database_url)

        self.db_host = parsed.hostname
        self.db_port = str(parsed.port) if parsed.port else '5432'
        self.db_name = parsed.path.lstrip('/')
        self.db_user = parsed.username
        self.db_password = parsed.password

    def _valider_config(self):
        params_obligatoires = {
            'DB_NAME': self.db_name,
            'DB_USER': self.db_user,
            'DB_PASSWORD': self.db_password,
            'CSV_FILE_PATH': self.csv_file_path
        }
        
        params_manquants = [param for param, valeur in params_obligatoires.items() if not valeur]
        
        if params_manquants:
            raise ValueError(f"Paramètres de configuration manquants: {', '.join(params_manquants)}")
    
    def _configurer_logging(self):
        logging.basicConfig(
            level=getattr(logging, 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('migration.log'),
                logging.StreamHandler()
            ]
        )
        
        # Créer un logger spécifique pour la migration
        self.logger = logging.getLogger('migration')
        
        # Masquer les informations sensibles dans les logs
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    def get_database_url(self):
        # Garde les caractères spéciaux dans le mot de passe
        password = quote_plus(self.db_password)
        
        return f"postgresql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?client_encoding=utf8"
    
    def log_info(self, message):
        self.logger.info(message)
    
    def log_error(self, message, exception=None):
        if exception:
            self.logger.error(f"{message}: {type(exception).__name__}")
        else:
            self.logger.error(message)
    
    def log_event(self, event):
        self.logger.warning(f"SECURITY EVENT: {event}")

# Instance globale de configuration
config = Config()