from paho.mqtt import client as paho
import variables as var
import influxDB as influx
import connexion as connexion
import genereJSon as gJ
import json
import threadVanne as tv

def envoie_mqtt(client,topic_down,setpoint,salle,nom_vanne):
    """Envoie de la température en base64 à un appareil via MQTT.

    Args:
        client (paho.mqtt.client.Client): Client MQTT
        topic_down (str): Topic pour envoyer un message
        setpoint (int): Température à envoyer
        salle (str): Nom de la salle
        nom_vanne (str): Nom de la vanne
    """
    influx.ecrire_setpoint(setpoint,salle,nom_vanne)
    temperature_voulue = influx.recup_info(influx.recup_consigne(var.threads[topic_down]))[2][1]
    if verif_envoie_mqtt(setpoint, temperature_voulue):
        json = gJ.genereJSon(temperature_voulue)
        print(json)
        transmet_mqtt(client,topic_down,json)
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
    

    
def verif_envoie_mqtt(setpoint, temperature_voulue):
    """Vérifie si la température doit être envoyée à la vanne via MQTT.

    Args:
        setpoint (int): Température à appliquer
        temperature_voulue (int): Température actuelle
    """
    doit_envoyer = False
    if temperature_voulue != setpoint:
        doit_envoyer = True
    return doit_envoyer


def transmet_mqtt(client, topic, payload):
    """Envoie un message MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        topic (str): Topic du message
        payload (str): Message à envoyer

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    result, _ = client.publish(topic, payload)
    # Vérification si l'envoi a réussi
    if result == paho.MQTT_ERR_SUCCESS:
        print("Message envoyé")
        return True
    else:
        print("Échec de l'envoi du message, code de retour : ", result)
        return False
    
def subscribe_mqtt(client, topic_down, topic_up):
    """Souscrit à des topics MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        topic_down (str): Topic auquel s'abonner pour recevoir des messages
        topic_up (str): Topic auquel s'abonner pour envoyer des messages

    Returns:
        bool: True si l'abonnement a réussi, False sinon
    """
    # Tentative d'abonnement aux topics MQTT
    result_down, _ = client.subscribe(topic_down)
    result_up, _ = client.subscribe(topic_up)

    # Vérification si l'abonnement a réussi
    if result_down == paho.MQTT_ERR_SUCCESS and result_up == paho.MQTT_ERR_SUCCESS:
        print("Abonnement aux topics réussi")
        return True
    else:
        print("Échec de l'abonnement aux topics")
        return False  

    
def create_topic(device_id):
    """Crée les topics MQTT pour un appareil donné

    Args:
        device_id (str): Identifiant de l'appareil

    Returns:
        tuple: Topic pour envoyer un message, topic pour recevoir un message
    """
    return f"v3/usmb-project@ttn/devices/{device_id}/down/replace", f"v3/usmb-project@ttn/devices/{device_id}/up"


def abonnement_general():
    """Abonnement général à tous les topics MQTT.
    """
    for vanne in var.liste_vannes:
        salle=var.liste_vannes[vanne][0]
        topic_down,topic_up = create_topic(vanne)
        vanne = tv.VanneThread(vanne,salle, topic_up,topic_down)
        var.threads.update({topic_down:vanne.salle})
        vanne.start()
 