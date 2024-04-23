import requests
from datetime import datetime

def liens_reussi():
    date_actuelle = datetime.now()
    date_formatee = date_actuelle.strftime("%Y-%m-%d")
    url="https://ade-usmb-ro.grenet.fr/jsp/custom/modules/plannings/direct_cal.jsp?data=b5cfb898a9c27be94975c12c6eb30e9233bdfae22c1b52e2cd88eb944acf5364c69e3e5921f4a6ebe36e93ea9658a08f,1&resources=2999&projectId=1&calType=ical&lastDate="+date_formatee
    reponse = requests.get(url)  
    if reponse.status_code == 200: 
        return "True"
    else:
        return "False"


result =  liens_reussi()
with open('outpoot.txt', 'w') as f:
    f.write(result)
