#!/bin/sh

# Chemin du fichier JS qui sera utilisé par le frontend
ENV_FILE=/usr/share/nginx/html/env.js

echo "Génération de env.js à partir des variables d'environnement…"

# Commence le fichier
echo "window.__ENV__ = {" > $ENV_FILE

# Parcourt toutes les variables d'environnement et les écrit
env | while IFS='=' read -r name value; do
  # Filtrer si besoin les variables à exposer
  case "$name" in
    VITE_*)
      echo "  $name: \"$value\"," >> $ENV_FILE
      ;;
  esac
done

# Termine le fichier
echo "};" >> $ENV_FILE

# Lancer Nginx en foreground
exec nginx -g "daemon off;"
