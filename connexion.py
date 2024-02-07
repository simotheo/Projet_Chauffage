import influxdb_client as influxdb
from sshtunnel import SSHTunnelForwarder

# Informations de connexion au serveur
url = "192.168.141.107"
ssh_port = 22
login="root"
mdp="password"
#token = "U3lsdmFpbk1vbnRhZ255RXN0VW5DaGFtcGlvbl9Gb3JtYXRpb25Mb1JhV0FOX1VuaXZfU2F2b2llXzIwMjMhCg=="
#org = "training-usmb"
#bucket = "iot-platform"

influxdb_address = 'localhost'
influxdb_port = 8086
influxdb_username = 'admin'
influxdb_password = 'univ-lorawan'
influxdb_bucket = 'iot-platform'

def connexion_bdd(url, ssh_port, login, mdp, influxdb_address, influxdb_port, influxdb_username, influxdb_password, influxdb_bucket):
    

    try:
        # Création d'un tunnel SSH vers le serveur
        with SSHTunnelForwarder(
            (url, ssh_port),
            ssh_username=login,
            ssh_password=mdp,
            remote_bind_address=(influxdb_address, influxdb_port),
        ) as tunnel:
            print("Tunnel SSH établi avec succès.")

            # Connexion à la base de données InfluxDB à travers le tunnel SSH
            client = influxdb.InfluxDBClient(
                url=' http://localhost:8086',
                token='U3lsdmFpbk1vbnRhZ255RXN0VW5DaGFtcGlvbl9Gb3JtYXRpb25Mb1JhV0FOX1VuaXZfU2F2b2llXzIwMjMhCg==',
                port=tunnel.local_bind_port,
                username=influxdb_username,
                password=influxdb_password,
                database=influxdb_bucket,
            )

        if client:
            print("Connexion à la base de données InfluxDB réussie.")
            return client
        else:
            print("Échec de la connexion à la base de données InfluxDB.")
            return False

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return e

def fermer_connexion(client):
    if client:    
        client.close()
        print("Connexion à la base de données InfluxDB fermée avec succès.")
        return True
    else:
        print("Aucune connexion à fermer.")
        return False

client = connexion_bdd(url, ssh_port, login, mdp, influxdb_address, influxdb_port, influxdb_username, influxdb_password, influxdb_bucket)
fermer_connexion(client)



