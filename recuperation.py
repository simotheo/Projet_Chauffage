import requests
import re
from datetime import datetime
from pathlib import Path
from icalendar import Calendar, Event
import datetime 
import pytz

#Création url
def create_url(num):
    """Crée une URL pour l'emploi du temps ADE d'une salle spécifique.

    Args:
        num (int): Numéro de la salle.

    Returns:
        str: URL de l'emploi du temps ADE de la salle spécifiée.
    """
    # Obtenir la date actuelle
    date_actuelle = datetime.datetime.now()

    # Formater la date actuelle pour l'incorporer dans l'URL
    date_formatee = date_actuelle.strftime("%Y-%m-%d")
    return "https://ade-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=b5cfb898a9c27be94975c12c6eb30e9233bdfae22c1b52e2cd88eb944acf5364c69e3e5921f4a6ebe36e93ea9658a08f,1&resources="+str(num)+"&projectId=1&calType=ical&lastDate="+date_formatee

def nom_salle(url):
    """Récupère le nom de la salle à partir de l'URL de l'emploi du temps ADE.

    Args:
        url (str): URL de l'emploi du temps ADE.

    Returns:
        str: Nom de la salle extrait de l'URL.
    """
    # Initialisation de la variable de retour à None pour gérer le cas où aucun match n'est trouvé
    res = None
    
    # Utiliser une expression régulière pour trouver la partie souhaitée de l'URL
    match = re.search("1&resources=(\d+)", url)

    # Vérifier si une correspondance a été trouvée
    if match:
        # Si un match est trouvé, extraire la valeur correspondante (le premier groupe capturé par l'expression régulière)
        res = match.group(1)  # Le groupe 1 contient la valeur correspondante

    # Retourner l'identifiant extrait, ou None si aucun match n'a été trouvé
    return res



def supprime_fichier(chemin):
    """Supprime un fichier à un chemin spécifié.

    Args:
        chemin (str): Le chemin du fichier à supprimer.

    Returns:
        bool: True si le fichier a été supprimé avec succès, False sinon.
    """
    chemin_fichier = Path(chemin)
    if chemin_fichier.exists():  # Vérifie si le fichier existe
        chemin_fichier.unlink()  # Supprime le fichier
        return True
    else:
        return False

def recuperation(url, chemin):
    """Télécharge un fichier à partir d'une URL et l'enregistre localement.

    Args:
        url (str): L'URL du fichier à télécharger.
        chemin (str): Le chemin où enregistrer le fichier téléchargé.

    Returns:
        bool: True si le téléchargement a réussi, False sinon.
    """
    supprime_fichier(chemin)  # Supprime le fichier existant si nécessaire
    reponse = requests.get(url)  # Effectue une requête GET pour télécharger le fichier
    if reponse.status_code == 200:  # Vérifie si la requête a réussi
        with open(chemin, 'wb') as fichier:  # Ouvre le fichier en écriture binaire
            fichier.write(reponse.content)  # Écrit le contenu téléchargé dans le fichier
        return True
    else:
        return False
    
def heure_debut(chemin):
    """Récupère l'heure de début du premier événement futur dans le fichier ICS.

    Args:
        chemin (str): Le chemin du fichier ICS à analyser.

    Returns:
        datetime: L'heure de début du premier événement futur.
    """
    with open(chemin, 'rb') as f:
        cal = Calendar.from_ical(f.read())
        
    debut=None
    trouver=False
    # Obtenir l'heure actuelle
    maintenant  = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
    maintenant = maintenant + datetime.timedelta(hours=2)
    # Parcourir les composants du calendrier
    for composant in cal.walk():
        if composant.name == "VEVENT" and trouver==False:
            
            # Récupérer l'heure de début de l'événement
            debut = composant.get('dtstart').dt
            
            # Si l'heure de début est une date avec fuseau horaire, convertir en heure locale
            if isinstance(debut, datetime.datetime):
                debut = debut.astimezone(pytz.timezone('Europe/Paris'))
                # Vérifier si l'événement n'est pas déjà passé
                if debut > maintenant:
                    trouver=True

    if trouver==False:
        debut=None
    return debut

def heure_fin(chemin):
    """Récupère l'heure de fin du premier événement futur dans le fichier ICS.

    Args:
        chemin (str): Le chemin du fichier ICS à analyser.

    Returns:
        datetime: L'heure de fin du premier événement futur.
    """
    with open(chemin, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    fin=None
    trouver=False
    # Obtenir l'heure actuelle
    maintenant  = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
    maintenant = maintenant + datetime.timedelta(hours=2)

    # Parcourir les composants du calendrier
    for composant in cal.walk():
        if composant.name == "VEVENT" and trouver==False:
            # Récupérer l'heure de fin de l'événement
            fin = composant.get('dtend').dt
            # Si l'heure de fin est une date avec fuseau horaire, convertir en heure locale
            if isinstance(fin, datetime.datetime):
                fin = fin.astimezone(pytz.timezone('Europe/Paris'))
                # Vérifier si l'événement n'est pas déjà terminé
                if fin > maintenant:
                    trouver=True
    if trouver==False:
        fin=None
    return fin

def make_chemin(url):
    """Crée le chemin du fichier ICS à partir de l'URL de l'emploi du temps ADE.

    Args:
        url (str): URL de l'emploi du temps ADE.

    Returns:
        str: Chemin du fichier ICS.
    """
    return nom_salle(url)+".ics"




