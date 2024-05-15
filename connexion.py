import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime


host = "http://projetl3info.univ-lorawan.fr:81"
org = "training-usmb"
token = "U3lsdmFpbk1vbnRhZ255RXN0VW5DaGFtcGlvbl9Gb3JtYXRpb25Mb1JhV0FOX1VuaXZfU2F2b2llXzIwMjMhCg=="
bucket="iot-platform"


def connexion(url,token,org):
    """Se connecte à la base de donnée InfluxDB

    Args:
        url (str): url de la base de donnée
        token (str): token d'authentification
        org (str): organisation

    Returns:
        client: client InfluxDB
    """
    client = influxdb_client.InfluxDBClient(url,token,org)
    return client

def writeData(client, bucket,org,salle,temperature,debut,fin):
    """Ecrit les données dans la base de donnée InfluxDB

    Args:
        client (client): client InfluxDB
        bucket (str): nom du bucket
        org (str): organisation
        salle (str): nom de la salle
        temperature (float): température
        debut (datetime): heure de début
        fin (datetime): heure de fin
    """
    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = influxdb_client.Point(salle).tag(key="Admin",value="Maxime").field(field="temperature", value=temperature).field(field="heure de debut", value=str(debut)).field(field="heure de fin", value=str(fin)).time(time=datetime.datetime.utcnow())
    write_api.write(bucket=bucket, org=org, record=data)
    
def readData(client,org,salle):
    """Lit les données de la base de donnée InfluxDB

    Args:
        client (client): client InfluxDB
        org (str): organisation
        salle (str): nom de la salle

    Returns:
        result: résultat de la requête
    """
    query_api = client.query_api()
    query = f'from(bucket: "iot-platform")|> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "{salle}")|> last()'
    result = query_api.query(org=org, query=query)
    return result

def recup_info(result):
    """Récupère les informations de la requête

    Args:
        result: résultat de la requête

    Returns:
        list: liste des informations
    """
    res = []
    for table in result:
        for record in table.records:
            res.append((record.get_field(), record.get_value()))
    return res

def affiche_res(result):
    """Affiche les résultats de la requête

    Args:
        result: résultat de la requête
    """
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_field(), record.get_value()))
    print(results)

def close(client):
    """Ferme la connexion à la base de donnée InfluxDB

    Args:
        client: client InfluxDB
    """
    client.close()
    







































