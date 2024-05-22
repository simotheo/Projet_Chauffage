import connexion as connexion
import recuperation as recup
import datetime
import variables as var
import gestionADE as gad
import influxDB as influx
import pytz

def calcul_heure(heure,decalage):
    """Calcul de l'heure en fonction d'un décalage.

    Args:
        heure (datetime): Heure au format HH:MM
        decalage (int): Décalage en minutes

    Returns:
        datetime: Nouvelle heure calculée
    """
    new_heure = heure - datetime.timedelta(minutes=decalage)
    return new_heure


def ade(url,chemin):
    """Récupère les heures de début et de fin d'une salle depuis un fichier iCalendar.

    Args:
        url (str): URL du fichier iCalendar
        chemin (str): Chemin du fichier iCalendar

    Returns:
        tuple: Heure de début et heure de fin
    """
    recup.recuperation(url, chemin)
    debut = recup.heure_debut(chemin) 
    fin = recup.heure_fin(chemin)
    print("Debut : ",debut)
    print("Fin : ",fin)
    if debut is None and fin is None:
        return None, None
    elif debut is None and fin is not None:
        fin= calcul_heure(fin,var.temps_arret)
        return None, fin
    elif debut is not None and fin is None:
        debut= calcul_heure(debut,var.temps_prechauffage)
        return debut, None
    else:
        debut= calcul_heure(debut,var.temps_prechauffage)
        fin= calcul_heure(fin,var.temps_arret)
        return debut, fin

def calcul_temperature(debut,fin):
    """Calcul de la température en fonction de l'occupation de la salle.

    Args:
        debut (datetime): Heure de début d'occupation de la salle
        fin (datetime): Heure de fin d'occupation de la salle

    Returns:
        int: Température à appliquer
    """
    if debut is None and fin is None:
        return var.temperature_non_occupee
    
    actu  = datetime.datetime.now(pytz.timezone('Europe/Paris')).replace(second=0, microsecond=0)
    actu = actu + datetime.timedelta(hours=2)
    if debut is None and actu <= fin:
        temperature = var.temperature_occupee
    elif debut is None and actu >= fin:
        temperature = var.temperature_non_occupee
    elif (actu >= debut and actu <= fin):
        temperature = var.temperature_occupee
    elif debut >= fin and actu <= fin:
        temperature = var.temperature_occupee
    else:
        temperature = var.temperature_non_occupee
    return temperature

    
def calcul_consigne(url):
    """Calcul de la consigne de température pour une salle.

    Args:
        url (str): URL de l'emploi du temps ADE
    """
    chemin=recup.make_chemin(url)
    nom_salle=recup.nom_salle(url) #recupération du nom de la salle
    print("Nom salle : ",nom_salle)
    debut,fin=ade(url,chemin) #recupération des heures de début et de fin
    
    
    print("Debut : ",debut)
    print("Fin : ",fin)
    temperature=calcul_temperature(debut,fin) #calcul de la température
    influx.ecrire_consigne(temperature,nom_salle,debut,fin) #écriture de la consigne dans la base de données
    
    
def recup_liste_salle():
    """Récupération de la liste des salles.
    """
    for vannes in var.liste_vannes:
        salle = var.liste_vannes[vannes][0]
        if salle not in var.liste_salles:
            var.liste_salles.append(salle)
    
def edt_par_vanne():
    """Récupération des emplois du temps pour chaque salle et calcul des consignes.
    """
    recup_liste_salle()
    for salle in var.liste_salles:
        url=recup.create_url(salle)
        gad.calcul_consigne(url)