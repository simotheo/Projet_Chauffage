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

scheduler = sched.scheduler(time.time, time.sleep)
liste_vanne={"8C-032": [5003,["simu-vanne-01"]]}
temperature_occupee=20
temperature_non_occupee=17

def ade(url,chemin):
    recup.recuperation(url, chemin)
    debut = recup.heure_debut(chemin)
    fin = recup.heure_fin(chemin)
    return debut, fin

def calcul_temperature(debut,fin):
    actu = datetime.datetime.now(datetime.timezone.utc)
    if actu >= debut and actu <= fin:
        temperature = temperature_occupee
    else:
        temperature = temperature_non_occupee
    return temperature


def ecrire_consigne(temperature,nom_salle,debut,fin):
    client = connexion.connexion(connexion.host,connexion.token,connexion.org)
    connexion.writeData(client, connexion.bucket,connexion.org,nom_salle,temperature,debut,fin)
    connexion.close(client)
    
def recup_consigne(nom_salle):
    client = connexion.connexion(connexion.host,connexion.token,connexion.org)
    result = connexion.readData(client,connexion.org,nom_salle)
    connexion.close(client)
    return result


def envoie_mqtt(temperature,client,topic_down,topic_up):
    client=mqtt.connexion_mqtt(topic_up)
    mqtt.subscribe_mqtt(client, topic_down, topic_up)
    json = gJ.genereJSon(temperature)
    print(json)
    em.envoie_mqtt(client,topic_down,json) 
    


def table_to_dataframe(table):
    """
    Convertir une table InfluxDB en DataFrame.
    """
    
    columns = [column.label for column in table.columns]
    
    
    records = [record.values for record in table.records]
    
    
    return pd.DataFrame(records, columns=columns)

def afficher_table_list(table_list):
    """
    Affiche les tables d'un TableList en DataFrames individuels.
    """
    for i, table in enumerate(table_list):
        df = table_to_dataframe(table)
        print(f"\nTable {i} (Measurement: {table.records[0].get_measurement()}):")
        print(df)

def get_setpoint_from_message(message):
    try:
        data = json.loads(message)
        setpoint = data['uplink_message']['decoded_payload']['setpoint']
        return setpoint
    except (KeyError, json.JSONDecodeError) as e:
        print("Erreur lors de l'extraction du setpoint :", e)
        return None
    
def calcul_consigne(url):
    chemin=recup.make_chemin(url)
    debut,fin=ade(url,chemin) #recupération des heures de début et de fin
    nom_salle=recup.nom_salle(url) #recupération du nom de la salle
    temperature=calcul_temperature(debut,fin) #calcul de la température
    ecrire_consigne(temperature,nom_salle,debut,fin) #écriture de la consigne dans la base de données
    
def verif_envoie_mqtt(url, topic_down, topic_up):
    client=mqtt.connexion_mqtt(topic_up)
    client_bdd=connexion.connexion(connexion.host,connexion.token,connexion.org)
    nom_salle=recup.nom_salle(url)
    data=recup_consigne(nom_salle)
    données=connexion.recup_info(data)
    temperature= int(données[2][1])
    message = mqtt.wait_for_message(client,mqtt.broker, mqtt.username, mqtt.password)
    setpoint=int(get_setpoint_from_message(message))
    if setpoint!=temperature:
        envoie_mqtt(temperature,client,topic_down,topic_up)
        print("Message envoyé")
    else:
        print("Erreur lors de la réception du message")
    connexion.close(client_bdd)
    mqtt.deconnexion_mqtt(client)
    
    
def run():
    for salle in liste_vanne:
        id_salle = liste_vanne[salle][0]
        liste_vanne_salle = liste_vanne[salle][1]
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
    
    


    

    
    

