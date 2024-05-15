import time
from paho.mqtt import client as mqtt


def create_topic(device_id):
    """Crée les topics MQTT pour un appareil donné

    Args:
        device_id (str): Identifiant de l'appareil

    Returns:
        tuple: Topic pour envoyer un message, topic pour recevoir un message
    """
    return f"v3/usmb-project@ttn/devices/{device_id}/down/replace", f"v3/usmb-project@ttn/devices/{device_id}/up"

def on_connect(client, userdata, flags, rc):
    """Fonction de rappel appelée lors de la connexion au broker MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        userdata (dict): Données utilisateur
        flags (dict): Drapeaux de connexion
        rc (int): Code de retour de connexion
    """
    client.subscribe(userdata['topic'])
    if rc == 0:
        client.connected_flag = True
        print("Connecté avec le code ", rc)
    else:
        print("Echec de la connexion avec le code", rc)

def connexion_mqtt(topic):
    """Connexion à un broker MQTT

    Args:
        topic (str): Topic auquel s'abonner

    Returns:
        mqtt.Client: Objet client de connexion
    """
    mqtt.Client.connected_flag=False
    client = mqtt.Client()      
    client = mqtt.Client(userdata={'topic': topic})       
    client.on_connect=on_connect  
    client.loop_start()
    print("Connexion au broker ",broker)
    client.connect(broker)      
    client.username_pw_set(username, password)
    while not client.connected_flag: 
        print("En attente")
        time.sleep(1)
    print("Connecté au broker")
    client.loop_stop()    
    return client



    
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
    if result_down == mqtt.MQTT_ERR_SUCCESS and result_up == mqtt.MQTT_ERR_SUCCESS:
        print("Abonnement aux topics réussi")
        return True
    else:
        print("Échec de l'abonnement aux topics")
        return False



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
    client.disconnect()
    
    
    
def wait_for_message(client,broker_address, username, password):
    """Attend la réception d'un message MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
        broker_address (str): Adresse du broker MQTT
        username (str): Nom d'utilisateur pour la connexion
        password (str): Mot de passe pour la connexion

    Returns:
        str: Message reçu
    """
    global received_message
    received_message = None
    
    
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.username_pw_set(username, password)
    client.connect(broker_address, port, 60)

    client.loop_start()

    while received_message is None:
        pass

    client.loop_stop()
    return received_message

def deconnexion_mqtt(client):
    """Déconnecte un client MQTT

    Args:
        client (mqtt.Client): Objet client de connexion
    """
    client.disconnect() # disconnect
    print("Déconnecté du broker")

broker = 'eu1.cloud.thethings.network'
port = 1883
client_id = "mqtt-explorer-95791e2c"
username = 'usmb-project@ttn'
password = 'NNSXS.6TZ4WH2K4KWCG7WQHL6FYI6HPC3HMT6V6IOY6IQ.QS3SCCTRWJCFQYQLLSCBNQUHD23WHBF6IIWOW6EA445O7A5SR7ZA'
received_message = None








