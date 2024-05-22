import connexion as connexion
import time
import plannificateur as pls
import sched
import gestionADE as gad
import gestionMqtt as gm
import variables as var
import os

"""
# Variables d'environnement
TEMPERATUREOCCUPEE = os.getenv("TEMPERATUREOCCUPEE", "var.temperature_occupee")
TEMPERATURENONOCCUPEE = os.getenv("TEMPERATURENONOCCUPEE", "var.temperature_non_occupee")
TEMPSPRECHAUFFAGE = os.getenv("TEMPSPRECHAUFFAGE", "var.temps_prechauffage")
TEMPSARRET = os.getenv("TEMPSARRET", "var.temps_arret")
HOST = os.getenv("HOST", "var.host")
ORG = os.getenv("ORG", "var.org")
TOKEN = os.getenv("TOKEN", "var.token")
BUCKET = os.getenv("BUCKET", "var.bucket")
BROKER = os.getenv("BROKER", "var.broker")
PORT = os.getenv("PORT", "var.port")
CLIENTID = os.getenv("CLIENTID", "var.client_id")
USERNAME = os.getenv("USERNAME", "var.username")
PASSWORD = os.getenv("PASSWORD", "var.password")

if TEMPERATUREOCCUPEE != '':
    var.temperature_occupee = int(TEMPERATUREOCCUPEE)
if TEMPERATURENONOCCUPEE != '':
    var.temperature_non_occupee = int(TEMPERATURENONOCCUPEE)
if TEMPSPRECHAUFFAGE != '':
    var.temps_prechauffage = int(TEMPSPRECHAUFFAGE)
if TEMPSARRET != '':
    var.temps_arret = int(TEMPSARRET)
if HOST != '':
    var.host = HOST
if ORG != '':
    var.org = ORG
if TOKEN != '':
    var.token = TOKEN
if BUCKET != '':
    var.bucket = BUCKET
if BROKER != '':
    var.broker = BROKER
if PORT != '':
    var.port = int(PORT)
if CLIENTID != '':
    var.client_id = CLIENTID
if USERNAME != '':
    var.username = USERNAME
if PASSWORD != '':
    var.password = PASSWORD"""

scheduler = sched.scheduler(time.time, time.sleep) # Créer un planificateur

def run():
    """Fonction principale pour exécuter les tâches planifiées.
    """
    gad.edt_par_vanne()
    
    scheduler.enter(var.refresh, 1, run)
    
if __name__ == "__main__":
    """Exécution du programme principal.
    """
    
    gm.abonnement_general() # Abonnement à tous les topics
    # Programmer la première exécution
    scheduler.enter(0, 1, run)

    # Démarrer le planificateur
    scheduler.run()
    pls.start_scheduler()  # Démarrer le scheduler dans un thread séparé

    


    
    


    

    
    

