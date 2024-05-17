import schedule
import time
from threading import Thread
import main as m

def setup_scheduler():
    m.edt_par_vanne()  # Exécute la fonction run une première fois pour initialiser les tâches
    schedule.every(5).minutes.do(m.edt_par_vanne)  # Planifie la fonction run pour s'exécuter toutes les 10 minutes

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    setup_scheduler()
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Assure que le thread s'arrête lorsque le programme principal s'arrête
    scheduler_thread.start()
