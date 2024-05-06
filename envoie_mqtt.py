import genereJSon as recup
import recup_mqtt as mqtt
from paho.mqtt import client as paho

def envoie_mqtt(client, topic, payload):
    """Envoie un message MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        topic (str): Topic du message
        payload (str): Message à envoyer

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Tentative d'envoi du message MQTT
    result, _ = client.publish(topic, payload)

    # Vérification si l'envoi a réussi
    if result == paho.MQTT_ERR_SUCCESS:
        print("Message envoyé")
        return True
    else:
        print("Échec de l'envoi du message, code de retour : ", result)
        return False
    

    



