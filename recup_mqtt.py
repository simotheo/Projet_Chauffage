import time
from paho.mqtt import client as mqtt
import variables as var
import gestionMqtt as gm
  
def connexion_mqtt():
    """Connexion à un broker MQTT

    Returns:
        mqtt.Client: Objet client de connexion
    """
    mqtt.Client.connected_flag=False
    client = mqtt.Client()             
    client.on_connect=on_connect  
    client.loop_start()
    print("Connexion au broker ",var.broker)
    client.connect(var.broker)      
    client.username_pw_set(var.username, var.password)
    while not client.connected_flag: 
        print("En attente")
        time.sleep(1)
    print("Connecté au broker")
    client.loop_stop()    
    return client


def on_connect(client, userdata, flags, rc):
    """Fonction de rappel appelée lors de la connexion au broker MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        userdata (dict): Données utilisateur
        flags (dict): Drapeaux de connexion
        rc (int): Code de retour de connexion
    """
    if rc == 0:
        client.connected_flag = True
        print("Connecté avec le code ", rc)
    else:
        print("Echec de la connexion avec le code", rc)



def on_message(client, userdata, msg):
    """Fonction de rappel appelée lors de la réception d'un message MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        userdata (dict): Données utilisateur
        msg (mqtt.MQTTMessage): Message reçu
    """
    global received_message
    print("Message reçu sur le topic " + msg.topic + " avec le payload " + str(msg.payload))
    received_message = msg.payload.decode()
    gm.envoie_mqtt(client,userdata['topic_down'],gm.get_setpoint_from_message(received_message))
    

def deconnexion_mqtt(client):
    """Déconnecte un client MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
    """
    client.disconnect() # disconnect
    print("Déconnecté du broker")








