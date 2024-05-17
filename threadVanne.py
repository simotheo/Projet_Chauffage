# recup_mqtt.py
import paho.mqtt.client as mqtt
from threading import Thread
import variables as var
import main as m

class VanneThread(Thread):
    def __init__(self,nom,salle, topic_up,topic_down):
        Thread.__init__(self)
        self.nom = nom
        self.salle = salle
        self.topic_up = topic_up
        self.topic_down = topic_down
        self.client = mqtt.Client()
        self.received_message = None
        
        
                
                
    def on_connect(self, client, userdata, flags, rc):
        print(f"Vanne {self.nom} connecte avec le code {rc}")
        self.client.subscribe(self.topic_down)
        self.client.subscribe(self.topic_up)

    def on_message(self, client, userdata, msg):
        print(f"Vanne {self.nom} on message")
        self.process_message(msg.topic, msg.payload)

    def process_message(self, topic, payload):
        print(f"Vanne {self.nom} processing message")
        received_message = payload.decode()
        m.envoie_mqtt(self.client,self.topic_down,m.get_setpoint_from_message(received_message),self.salle, self.nom)

    def run(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(var.broker, var.port)
        self.client.username_pw_set(var.username,var.password)
        self.client.loop_forever()
        
        


    
