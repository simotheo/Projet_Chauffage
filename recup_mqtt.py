import time
from paho.mqtt import client as mqtt


broker = 'eu1.cloud.thethings.network'
port = 1883
client_id = "mqtt-explorer-95791e2c"
username = 'usmb-project@ttn'
password = 'NNSXS.6TZ4WH2K4KWCG7WQHL6FYI6HPC3HMT6V6IOY6IQ.QS3SCCTRWJCFQYQLLSCBNQUHD23WHBF6IIWOW6EA445O7A5SR7ZA'
topic_down = "v3/usmb-project@ttn/devices/simu-vanne-01/down/replace"
topic_up = "v3/usmb-project@ttn/devices/simu-vanne-01/up"

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("Connecté avec le code ",rc)
    else:
        print("Echec de la connexion avec le code",rc)

def connexion_mqtt():
    """Connexion au broker MQTT

    Returns:
        client: Objet client de connexion
    """
    mqtt.Client.connected_flag=False#create flag in class
    client = mqtt.Client()             
    client.on_connect=on_connect  #bind call back function
    client.loop_start()
    print("Connexion au broker ",broker)
    client.connect(broker)      #connect to broker
    client.username_pw_set(username, password)
    while not client.connected_flag: #wait in loop
        print("En attente")
        time.sleep(1)
    print("Connecté au broker")
    client.loop_stop()    #Stop loop 
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


def on_message(client, userdata, message):
    print("Message reçu :", message.payload.decode("utf-8"))
    print("Topic du message ", message.topic)

def deconnexion_mqtt(client):
    client.disconnect() # disconnect
    print("Déconnecté du broker")










