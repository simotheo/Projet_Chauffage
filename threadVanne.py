# recup_mqtt.py
import paho.mqtt.client as mqtt
from threading import Thread
import variables as var
import gestionMqtt as gm

class VanneThread(Thread):
    """Thread pour la gestion des vannes.

    Args:
        Thread (Thread): Classe de base pour les threads.
    """
    def __init__(self,nom,salle, topic_up,topic_down):
        """Initialise le thread.

        Args:
            nom (str): Nom de la vanne.
            salle (str): Nom de la salle.
            topic_up (str): Topic pour envoyer un message.
            topic_down (str): Topic pour recevoir un message.
        """
        Thread.__init__(self)
        self.nom = nom
        self.salle = salle
        self.topic_up = topic_up
        self.topic_down = topic_down
        self.client = mqtt.Client()
        self.received_message = None
        
        
                
                
    def on_connect(self, client, userdata, flags, rc):
        """Fonction de rappel appelée lorsqu'un client se connecte au broker.

        Args:
            client (paho.mqtt.client.Client): Client MQTT.
            userdata (Any): Données utilisateur.
            flags (dict): Drapeaux de connexion.
            rc (int): Code de retour de connexion."""
        print(f"Vanne {self.nom} connecte avec le code {rc}")
        self.client.subscribe(self.topic_down)
        self.client.subscribe(self.topic_up)

    def on_message(self,client, userdata, msg):
        """Fonction de rappel appelée lorsqu'un message est reçu.

        Args:
            client (paho.mqtt.client.Client): Client MQTT.
            userdata (Any): Données utilisateur.
            msg (paho.mqtt.client.MQTTMessage): Message MQTT.
        """
        print(f"Vanne {self.nom} on message")
        self.process_message(msg.payload)

    def process_message(self, payload):
        """Traite un message reçu.

        Args:
            self (VanneThread): Instance de la classe.
            payload (bytes): Charge utile du message.
        """
        print(f"Vanne {self.nom} processing message")
        received_message = payload.decode()
        gm.envoie_mqtt(self.client,self.topic_down,gm.get_setpoint_from_message(received_message),self.salle, self.nom)

    def run(self):
        """Exécute le thread.
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(var.broker, var.port)
        self.client.username_pw_set(var.username,var.password)
        self.client.loop_forever()
        
        


    
