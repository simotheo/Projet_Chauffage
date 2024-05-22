import connexion as connexion
import datetime
import variables as var
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime





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
    
def writeSetpoint(client,bucket,org,vanne,setpoint,salle):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = influxdb_client.Point(vanne).tag(key="Admin",value="Maxime").field(field="temperature", value=setpoint).field(field="salle", value=salle).time(time=datetime.datetime.utcnow())
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




def ecrire_setpoint(setpoint,salle,vanne):
    """Ecrit le setpoint dans la base de donnée InfluxDB

    Args:
        setpoint (int): Setpoint à appliquer
        salle (str): Nom de la salle
        vanne (str): Nom de la vanne
    """
    client = connexion.connexion(var.host,var.token,var.org)
    writeSetpoint(client, var.bucket,var.org,vanne,setpoint,salle)
    connexion.close(client)
    
    
def ecrire_consigne(temperature,nom_salle,debut,fin):
    """Ecriture de la consigne dans la base de données InfluxDB.

    Args:
        temperature (int): Température à appliquer
        nom_salle (str): Nom de la salle
        debut (datetime): Heure de début d'occupation de la salle
        fin (datetime): Heure de fin d'occupation de la salle
    """
    client = connexion.connexion(var.host,var.token,var.org)
    writeData(client, var.bucket,var.org,nom_salle,temperature,debut,fin)
    connexion.close(client)
    
def recup_consigne(nom_salle):
    """Récupération de la consigne dans la base de données InfluxDB.

    Args:
        nom_salle (str): Nom de la salle

    Returns:
        list: Résultat de la requête
    """
    client = connexion.connexion(var.host,var.token,var.org)
    result = readData(client,var.org,nom_salle)
    connexion.close(client)
    return result