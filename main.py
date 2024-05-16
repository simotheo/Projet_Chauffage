import connexion as connexion
import envoie_mqtt as em
import recuperation as recup
import recup_mqtt as mqtt
import genereJSon as gJ
import datetime
import sched
import time
import json
import pandas as pd
import variables as var

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


def envoie_mqtt(temperature,client,topic_down,topic_up):
    """Envoie de la température en base64 à un appareil via MQTT.

    Args:
        temperature (int): Température à envoyer
        client (mqtt.Client): Objet client de connexion MQTT
        topic_down (str): Topic pour envoyer un message
        topic_up (str): Topic pour recevoir un message
    """
    client=mqtt.connexion_mqtt(topic_up)
    mqtt.subscribe_mqtt(client, topic_down, topic_up)
    json = gJ.genereJSon(temperature)
    print(json)
    em.envoie_mqtt(client,topic_down,json) 
    


def table_to_dataframe(table):
    """Convertit une table InfluxDB en DataFrame Pandas.

    Args:
        table (influxdb_client.client.InfluxDBClient.query): Table InfluxDB

    Returns:
        pd.DataFrame: DataFrame Pandas
    """
    
    columns = [column.label for column in table.columns]
    
    
    records = [record.values for record in table.records]
    
    
    return pd.DataFrame(records, columns=columns)

def afficher_table_list(table_list):
    """Affiche les tables InfluxDB sous forme de DataFrames Pandas.

    Args:
        table_list (list): Liste de tables InfluxDB
    """
    for i, table in enumerate(table_list):
        df = table_to_dataframe(table)
        print(f"\nTable {i} (Measurement: {table.records[0].get_measurement()}):")
        print(df)

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
    
def verif_envoie_mqtt(url, topic_down, topic_up):
    """Vérifie si la température doit être envoyée à la vanne via MQTT.

    Args:
        url (str): URL de l'emploi du temps ADE
        topic_down (str): Topic pour envoyer un message
        topic_up (str): Topic pour recevoir un message
    """
    client=mqtt.connexion_mqtt(topic_up)
    client_bdd=connexion.connexion(var.host,var.token,var.org)
    nom_salle=recup.nom_salle(url)
    data=recup_consigne(nom_salle)
    connexion.affiche_res(data)
    données=connexion.recup_info(data)
    temperature= int(données[2][1])
    message = mqtt.wait_for_message(client,var.broker, var.username, var.password)
    setpoint=int(get_setpoint_from_message(message))
    if setpoint!=temperature:
        envoie_mqtt(temperature,client,topic_down,topic_up)
        print("Message envoyé")
    else:
        print("Message non envoyé car la consigne est déjà la bonne")
    connexion.close(client_bdd)
    mqtt.deconnexion_mqtt(client)
    
    
def run():
    """Fonction principale pour exécuter les tâches planifiées.
    """
    for salle in var.liste_vannes:
        id_salle = var.liste_vannes[salle][0]
        liste_vanne_salle = var.liste_vannes[salle][1]
        for vanne in liste_vanne_salle:
            url=recup.create_url(id_salle)
            topic_down,topic_up = mqtt.create_topic(vanne)
            calcul_consigne(url)
            verif_envoie_mqtt(url,topic_down,topic_up)
            print("Message envoyé à la vanne ",vanne," de la salle ",salle)
    
    scheduler.enter(300, 1, run)

# Programmer la première exécution
scheduler.enter(0, 1, run)

# Démarrer le planificateur
scheduler.run()
    
    


    

    
    

