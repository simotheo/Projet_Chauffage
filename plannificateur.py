import schedule
import time
from threading import Thread
import gestionADE as gad

def setup_scheduler():
    """Initialise le planificateur de tâches.
    """
    gad.edt_par_vanne()  # Exécute la fonction run une première fois pour initialiser les tâches
    schedule.every(5).minutes.do(gad.edt_par_vanne)  # Planifie la fonction run pour s'exécuter toutes les 10 minutes

def run_scheduler():
    """Exécute le planificateur de tâches.
    """
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    """Démarre le planificateur de tâches dans un thread séparé.
    """
    setup_scheduler()
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Assure que le thread s'arrête lorsque le programme principal s'arrête
    scheduler_thread.start()
