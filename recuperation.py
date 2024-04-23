import requests
import re
from datetime import datetime
from pathlib import Path
from icalendar import Calendar, Event
from datetime import datetime
import pytz


def nom_salle(url):
    """
    Extrait l'identifiant de la ressource depuis l'URL fournie.
    
    Cette fonction recherche une séquence spécifique dans l'URL qui correspond
    à l'identifiant de la ressource indiqué après '1&resources='. L'identifiant est 
    supposé être un nombre, et est extrait à l'aide d'une expression régulière.
    
    :param url: L'URL à partir de laquelle extraire l'identifiant de la ressource.
    :return: L'identifiant de la ressource sous forme de chaîne de caractères.
             Si aucun identifiant n'est trouvé, 'None' est retourné par défaut.
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
    """
    Supprime le fichier au chemin spécifié si celui-ci existe.
    
    :param chemin: Le chemin du fichier à supprimer.
    :return: True si le fichier a été supprimé, False sinon.
    """
    chemin_fichier = Path(chemin)
    if chemin_fichier.exists():  # Vérifie si le fichier existe
        chemin_fichier.unlink()  # Supprime le fichier
        return True
    else:
        return False

def recuperation(url, chemin):
    """
    Télécharge un fichier depuis une URL et le sauvegarde à un chemin spécifié.
    Supprime d'abord le fichier existant au même chemin, si présent.
    
    :param url: L'URL du fichier à télécharger.
    :param chemin: Le chemin où enregistrer le fichier téléchargé.
    :return: True si le fichier a été téléchargé et enregistré avec succès, False sinon.
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
    """
    Récupère l'heure de début de l'événement dans le fichier ICS.
    
    :param chemin: Le chemin du fichier ICS à analyser.
    :return: L'heure de début du premier événement sous forme de chaîne de caractères.
             Si l'heure de début n'est pas trouvée, 'None' est retourné par défaut.
    """
    with open(chemin, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    # Parcourir les composants du calendrier
    for composant in cal.walk():
        if composant.name == "VEVENT":
            # Récupérer l'heure de début de l'événement
            debut = composant.get('dtstart').dt
            # Si l'heure de début est une date avec fuseau horaire, convertir en heure locale
            if isinstance(debut, datetime):
                # Remplacer 'Europe/Paris' par votre fuseau horaire si nécessaire
                debut = debut.astimezone(pytz.timezone('Europe/Paris'))
            break
    return debut

def heure_fin(chemin):
    """
    Récupère l'heure de fin de l'événement dans le fichier ICS.
    
    :param chemin: Le chemin du fichier ICS à analyser.
    :return: L'heure de fin du premier événement sous forme de chaîne de caractères.
             Si l'heure de fin n'est pas trouvée, 'None' est retourné par défaut.
    """
    with open(chemin, 'rb') as f:
        cal = Calendar.from_ical(f.read())

    # Parcourir les composants du calendrier
    for composant in cal.walk():
        if composant.name == "VEVENT":
            # Récupérer l'heure de fin de l'événement
            fin = composant.get('dtend').dt
            # Si l'heure de fin est une date avec fuseau horaire, convertir en heure locale
            if isinstance(fin, datetime):
                # Remplacer 'Europe/Paris' par votre fuseau horaire si nécessaire
                fin = fin.astimezone(pytz.timezone('Europe/Paris'))
    return fin

# Obtenir la date actuelle
date_actuelle = datetime.now()


# Formater la date actuelle pour l'incorporer dans l'URL
date_formatee = date_actuelle.strftime("%Y-%m-%d")


# Construit l'URL avec la date formatée
url = "https://ade-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=b5cfb898a9c27be94975c12c6eb30e9233bdfae22c1b52e2cd88eb944acf5364c69e3e5921f4a6ebe36e93ea9658a08f,1&resources=2999&projectId=1&calType=ical&lastDate="+date_formatee
url2 = "https://ade-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=b5cfb898a9c27be94975c12c6eb30e9233bdfae22c1b52e2cd88eb944acf5364c69e3e5921f4a6ebe36e93ea9658a08f,1&resources=2042&projectId=1&calType=ical&lastDate="+date_formatee

# Chemin où le fichier doit être téléchargé et sauvegardé
chemin = nom_salle(url)+".ics"
chemin2 = nom_salle(url2)+".ics"

# Appel de la fonction de récupération pour télécharger et sauvegarder le fichier
recuperation(url, chemin)
recuperation(url2, chemin2)
print(heure_debut(chemin))
print(heure_fin(chemin))

