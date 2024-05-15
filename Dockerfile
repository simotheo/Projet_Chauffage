# Utilisez une image de base Python
FROM python:3.9

# Copiez les fichiers nécessaires dans le conteneur
COPY requirements.txt /app/requirements.txt

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Installez les dépendances Python spécifiées dans le fichier requirements.txt
RUN pip install -r requirements.txt

# Copiez le reste de votre application dans le conteneur
COPY . /app

# Commande par défaut pour l'exécution de votre application
CMD ["python", "main.py"]