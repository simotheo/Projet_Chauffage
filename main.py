import connexion as connexion
import envoie_mqtt as em
import recuperation as recup
import recup_mqtt as mqtt
import genereJSon as gJ
import datetime
import time
import json
import plannificateur as pls
import variables as var
import sched
import threadVanne as tv
scheduler = sched.scheduler(time.time, time.sleep)

def calcul_heure(date,heure,decalage):
    """Calcul de l'heure de début et de fin d'occupation de la salle.

    Args:
        date (str): Date de l'occupation
        heure (str): Heure de l'occupation

    Returns:
        tuple: Heure de début et heure de fin
    """
    date = date.split("-")
    heure = heure.split(":")
    normal = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(heure[0]),int(heure[1]),0,0,datetime.timezone.utc)
    new_heure = normal - datetime.timedelta(hours=decalage)
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
    if debut is None or fin is None:
        return None, None
    new_debut=calcul_heure(str(debut.date()),str(debut.time()),var.temps_prechauffage)
    new_fin=calcul_heure(str(fin.date()),str(fin.time()),var.temps_arret)
    return new_debut, new_fin

def calcul_temperature(debut,fin):
    """Calcul de la température en fonction de l'occupation de la salle.

    Args:
        debut (datetime): Heure de début d'occupation de la salle
        fin (datetime): Heure de fin d'occupation de la salle

    Returns:
        int: Température à appliquer
    """
    if debut is None or fin is None:
        return var.temperature_non_occupee
    actu = datetime.datetime.now(datetime.timezone.utc)
    actu = calcul_heure(str(actu.date()),str(actu.time()),-var.temps_prechauffage)
    if (actu >= debut and actu <= fin):
        temperature = var.temperature_occupee
    else:
        temperature = var.temperature_non_occupee
    return temperature


def ecrire_consigne(temperature,nom_salle,debut,fin):
    """Ecriture de la consigne dans la base de données InfluxDB.

    Args:
        temperature (int): Température à appliquer
        nom_salle (str): Nom de la salle
        debut (datetime): Heure de début d'occupation de la salle
        fin (datetime): Heure de fin d'occupation de la salle
    """
    client = connexion.connexion(var.host,var.token,var.org)
    connexion.writeData(client, var.bucket,var.org,nom_salle,temperature,debut,fin)
    connexion.close(client)
    
    
def ecrire_setpoint(setpoint,salle,vanne):
    """Ecrit le setpoint dans la base de donnée InfluxDB

    Args:
        setpoint (float): setpoint
    """
    client = connexion.connexion(var.host,var.token,var.org)
    connexion.writeSetpoint(client, var.bucket,var.org,vanne,setpoint,salle)
    connexion.close(client)
    
def recup_consigne(nom_salle):
    """Récupération de la consigne dans la base de données InfluxDB.

    Args:
        nom_salle (str): Nom de la salle

    Returns:
        list: Résultat de la requête
    """
    client = connexion.connexion(var.host,var.token,var.org)
    result = connexion.readData(client,var.org,nom_salle)
    connexion.close(client)
    return result


def envoie_mqtt(client,topic_down,setpoint,salle,nom_vanne):
    """Envoie de la température en base64 à un appareil via MQTT.

    Args:
        temperature (int): Température à envoyer
        client (mqtt.Client): Objet client de connexion MQTT
        topic_down (str): Topic pour envoyer un message
        topic_up (str): Topic pour recevoir un message
    """
    ecrire_setpoint(setpoint,salle,nom_vanne)
    temperature_voulue = connexion.recup_info(recup_consigne(var.threads[topic_down]))[2][1]
    if verif_envoie_mqtt(setpoint, temperature_voulue):
        json = gJ.genereJSon(temperature_voulue)
        print(json)
        em.envoie_mqtt(client,topic_down,json)
        print("Envoi de la température à la vanne")
    else:
        print("La température est déjà la bonne")
    

def get_setpoint_from_message(message):
    """Extrait le setpoint d'un message MQTT.

    Args:
        message (str): Message MQTT

    Returns:
        int: Setpoint extrait du message
    """
    try:
        data = json.loads(message)
        setpoint = data['uplink_message']['decoded_payload']['setpoint']
        return setpoint
    except (KeyError, json.JSONDecodeError) as e:
        print("Erreur lors de l'extraction du setpoint :", e)
        return None
    
def calcul_consigne(url):
    """Calcul de la consigne de température pour une salle.

    Args:
        url (str): URL de l'emploi du temps ADE
    """
    chemin=recup.make_chemin(url)
    debut,fin=ade(url,chemin) #recupération des heures de début et de fin
    nom_salle=recup.nom_salle(url) #recupération du nom de la salle
    temperature=calcul_temperature(debut,fin) #calcul de la température
    ecrire_consigne(temperature,nom_salle,debut,fin) #écriture de la consigne dans la base de données
    
def verif_envoie_mqtt(setpoint, temperature_voulue):
    """Vérifie si la température doit être envoyée à la vanne via MQTT.

    Args:
        url (str): URL de l'emploi du temps ADE
        topic_down (str): Topic pour envoyer un message
        topic_up (str): Topic pour recevoir un message
    """
    doit_envoyer = False
    if temperature_voulue != setpoint:
        doit_envoyer = True
    return doit_envoyer
    
def edt_par_vanne():
    for salle in var.liste_salles:
        url=recup.create_url(salle)
        calcul_consigne(url)




def abonnement_general():
    for vanne in var.liste_vannes:
        salle=var.liste_vannes[vanne][0]
        topic_down,topic_up = mqtt.create_topic(vanne)
        vanne = tv.VanneThread(vanne,salle, topic_up,topic_down)
        var.threads.update({topic_down:vanne.salle})
        vanne.start()
    
    




    """
    for vanne in var.liste_vannes:
        salle=var.liste_vannes[vanne][1]
        topic_down,topic_up = mqtt.create_topic(vanne)
        mqtt.subscribe_mqtt(client, topic_down, topic_up)
        numero_salle=var.liste_vannes[vanne][0]
        var.liste_topics.update({topic_down: [numero_salle, topic_up]})
        print(var.liste_topics)
        print("Abonnement à la vanne ",vanne," de la salle ",salle) """    
def run():
    """Fonction principale pour exécuter les tâches planifiées.
    """
    edt_par_vanne()
    
    scheduler.enter(60, 1, run)
    
if __name__ == "__main__":
    
    abonnement_general()
    # Programmer la première exécution
    scheduler.enter(0, 1, run)

    # Démarrer le planificateur
    scheduler.run()
    pls.start_scheduler()  # Démarrer le scheduler dans un thread séparé

    


    
    


    

    
    

