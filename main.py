import connexion as connexion
import envoie_mqtt as em
import recuperation as recup
import recup_mqtt as mqtt
import genereJSon as gJ
import datetime
import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)

def ade(url,chemin):
    recup.recuperation(url, chemin)
    debut = recup.heure_debut(chemin)
    fin = recup.heure_fin(chemin)
    return debut, fin

def calcul_temperature(debut,fin):
    actu = datetime.datetime.now(datetime.timezone.utc)
    if actu >= debut and actu <= fin:
        temperature = 20
    else:
        temperature = 17
    return temperature
    

def consigne(temperature,nom_salle,heure):
    client = connexion.connexion(connexion.host,connexion.token,connexion.org)
    connexion.writeData(client, connexion.bucket,connexion.org,nom_salle,heure,temperature)
    connexion.close(client)
    
def recup_consigne(nom_salle):
    client = connexion.connexion(connexion.host,connexion.token,connexion.org)
    result = connexion.readData(client,connexion.org,nom_salle)
    connexion.close(client)
    return result

def envoie_mqtt(temperature):
    client=mqtt.connexion_mqtt()
    mqtt.subscribe_mqtt(client, mqtt.topic_down, mqtt.topic_up)
    json = gJ.genereJSon(temperature)
    em.envoie_mqtt(client, mqtt.topic_down,json) 
    mqtt.deconnexion_mqtt(client)
    
def recup_mqtt():
    client=mqtt.connexion_mqtt()
    mqtt.subscribe_mqtt(client, mqtt.topic_down, mqtt.topic_up)
    res = mqtt.on_message(client, mqtt.userdata, mqtt.message)
    mqtt.close_mqtt(client)
    return res
    
def run():
    debut,fin=ade(recup.url2,recup.chemin)
    temperature=calcul_temperature(debut,fin)
    nom_salle=recup.nom_salle(recup.url2)
    consigne(temperature,nom_salle,debut)   
    recup_consigne(nom_salle)
    envoie_mqtt(temperature)

    scheduler.enter(300, 1, run)

# Programmer la première exécution
scheduler.enter(0, 1, run)

# Démarrer le planificateur
scheduler.run()
    
    


    

    
    

