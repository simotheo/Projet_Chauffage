import connexion as connexion
import time
import plannificateur as pls
import sched
import gestionADE as gad
import gestionMqtt as gm

scheduler = sched.scheduler(time.time, time.sleep)

def run():
    """Fonction principale pour exécuter les tâches planifiées.
    """
    gad.edt_par_vanne()
    
    scheduler.enter(300, 1, run)
    
if __name__ == "__main__":
    """Exécution du programme principal.
    """
    
    gm.abonnement_general()
    # Programmer la première exécution
    scheduler.enter(0, 1, run)

    # Démarrer le planificateur
    scheduler.run()
    pls.start_scheduler()  # Démarrer le scheduler dans un thread séparé

    


    
    


    

    
    

