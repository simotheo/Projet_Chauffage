import influxdb_client

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



def close(client):
    """Ferme la connexion à la base de donnée InfluxDB

    Args:
        client: client InfluxDB
    """
    client.close()
    







































