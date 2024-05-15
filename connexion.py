import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime


host = "http://projetl3info.univ-lorawan.fr:81"
org = "training-usmb"
token = "U3lsdmFpbk1vbnRhZ255RXN0VW5DaGFtcGlvbl9Gb3JtYXRpb25Mb1JhV0FOX1VuaXZfU2F2b2llXzIwMjMhCg=="
bucket="iot-platform"


def connexion(url,token,org):
    client = influxdb_client.InfluxDBClient(url,token,org)
    return client

def writeData(client, bucket,org,salle,temperature,debut,fin):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = influxdb_client.Point(salle).tag(key="Admin",value="Maxime").field(field="temperature", value=temperature).field(field="heure de debut", value=str(debut)).field(field="heure de fin", value=str(fin)).time(time=datetime.datetime.utcnow())
    write_api.write(bucket=bucket, org=org, record=data)
    
def readData(client,org,salle):
    query_api = client.query_api()
    query = 'from(bucket: "iot-platform")|> range(start: -1h) |> last()'
    result = query_api.query(org=org, query=query)
    return result

def recup_info(result):
    res = []
    for table in result:
        for record in table.records:
            res.append((record.get_field(), record.get_value()))
    return res

def affiche_res(result):
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_field(), record.get_value()))
    print(results)

def close(client):
    client.close()
    







































