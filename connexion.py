import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime


host = "http://192.168.170.61:81"
org = "training-usmb"
token = "U3lsdmFpbk1vbnRhZ255RXN0VW5DaGFtcGlvbl9Gb3JtYXRpb25Mb1JhV0FOX1VuaXZfU2F2b2llXzIwMjMhCg=="
bucket="iot-platform"


def connexion(url,token,org):
    client = influxdb_client.InfluxDBClient(url,token,org)
    return client

def writeData(client, bucket,org):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = influxdb_client.Point("Salles").tag(key="Admin",value="Maxime").field(field="Salle-001", value="12:00:12").field("Salle-001", 15).time(time=datetime.datetime.utcnow())
    write_api.write(bucket=bucket, org=org, record=data)
    
def readData(client,org):
    query_api = client.query_api()
    query = 'from(bucket: "iot-platform")|> range(start: -1h)|> filter(fn:(r) => r._field == "Salle-001")'
    result = query_api.query(org=org, query=query)
    return result

def affiche_res(result):
    results = []
    for table in result:
        for record in table.records:
            results.append((record.get_field(), record.get_value()))
    print(results)

def close(client):
    client.close()
    
client = connexion(host,token,org)
affiche_res(readData(client,org))
close(client)







































