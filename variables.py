liste_salles = [] # liste des salles à gérer, se remplira automatiquement
threads={} # dictionnaire des threads, se remplira automatiquement


# Variables pour la gestion des vannes

liste_vannes={"simu-vanne-01": [9563,"8D-010"]} # liste des vannes à gérer avec le numéro et le nom de la salle , "simu-vanne-02": [5009,"8C-38"], "simu-vanne-03": [5037,"4A-65"]
temperature_occupee=20 # température de consigne pour une salle occupée
temperature_non_occupee=17 # température de consigne pour une salle non occupée
temps_prechauffage=60 # temps de préchauffage en minutes
temps_arret=20 # temps d'arrêt en minutes


# Variables pour la connexion à la base de données InfluxDB

host = "http://projetl3info.univ-lorawan.fr:81" # adresse du serveur InfluxDB
org = "training-usmb" # nom de l'organisation
token = "U3lsdmFpbk1vbnRhZ255RXN0VW5DaGFtcGlvbl9Gb3JtYXRpb25Mb1JhV0FOX1VuaXZfU2F2b2llXzIwMjMhCg==" # token d'accès
bucket="iot-platform" # nom du bucket


# Variables pour la connexion au broker MQTT

broker = 'eu1.cloud.thethings.network' # adresse du broker MQTT
port = 1883 # port du broker MQTT
client_id = "mqtt-explorer-95791e2c" # identifiant du client
username = 'usmb-project@ttn' # nom d'utilisateur
password = 'NNSXS.6TZ4WH2K4KWCG7WQHL6FYI6HPC3HMT6V6IOY6IQ.QS3SCCTRWJCFQYQLLSCBNQUHD23WHBF6IIWOW6EA445O7A5SR7ZA' # mot de passe
