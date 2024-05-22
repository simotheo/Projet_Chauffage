# Utiliser une image de base Python
FROM python:3.9

# Définir des arguments de construction
ARG TEMPERATUREOCCUPEE
ARG TEMPERATURENONOCCUPEE
ARG TEMPSPRECHAUFFAGE
ARG TEMPSARRET
ARG HOST
ARG ORG
ARG TOKEN
ARG BUCKET
ARG BROKER
ARG PORT
ARG CLIENTID
ARG USERNAME
ARG PASSWORD

# Utiliser les arguments de construction pour définir des variables d'environnement
ENV TEMPERATUREOCCUPEE=${TEMPERATUREOCCUPEE}
ENV TEMPERATURENONOCCUPEE=${TEMPERATURENONOCCUPEE}
ENV TEMPSPRECHAUFFAGE=${TEMPSPRECHAUFFAGE}
ENV TEMPSARRET=${TEMPSARRET}
ENV HOST=${HOST}
ENV ORG=${ORG}
ENV TOKEN=${TOKEN}
ENV BUCKET=${BUCKET}
ENV BROKER=${BROKER}
ENV PORT=${PORT}
ENV CLIENTID=${CLIENTID}
ENV USERNAME=${USERNAME}
ENV PASSWORD=${PASSWORD}

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
