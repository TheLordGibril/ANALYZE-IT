import os
import re
from config import config

class SecurityValidator:
    def __init__(self):
        self.allowed_extensions = {'.csv'}
        
        # Patterns de validation
        self.country_pattern = re.compile(r'^[a-zA-Z\s\-\.\']{1,100}$')
        self.virus_pattern = re.compile(r'^[a-zA-Z0-9\s\-]{1,50}$')
        self.date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    def valider_fichier_csv(self, chemin_fichier):
        config.log_info(f"Validation du fichier: {chemin_fichier}")
        
        if not os.path.exists(chemin_fichier):
            raise FileNotFoundError(f"Fichier CSV introuvable: {chemin_fichier}")
        
        _, extension = os.path.splitext(chemin_fichier)
        if extension.lower() not in self.allowed_extensions:
            config.log_security_event(f"Extension de fichier non autorisée: {extension}")
            raise ValueError(f"Extension de fichier non autorisée: {extension}")
        
        return True

# Instance globale du validateur
validator = SecurityValidator()