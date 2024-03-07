import requests
import json
import schedule
import time
import winsound
from datetime import datetime
from json.decoder import JSONDecodeError

def read_config():
    with open('config.txt', 'r') as file:
        content = file.read().split('---')
        url = content[0].strip()
        request_data = json.loads(content[1])
        return url, request_data

URL, REQUEST = read_config()

def request_new():
    try:
        result = requests.post(URL, json=REQUEST)
        if result.status_code == 200:
            return result.json()
        elif result.status_code == 500:
            print("Error 500")
        else:
            print(result.content)
    except Exception as e:
        print("Error when doing the request:", e)

def save_to_file(offre_info):
    try:
        with open('job_offers.txt', 'r+') as file:
            try:
                data = json.load(file)
            except JSONDecodeError:
                data = []
            id_offre = offre_info["ID Offre"]
            if id_offre not in [offre["ID Offre"] for offre in data]:
                data.append(offre_info)
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
                return True
            return False
    except Exception as e:
        print("Error when saving to file:", e)

def parse_result(data):
    new_offers = False
    for offre in data['d']:
        id_offre = offre['id_offre']
        titre = offre['titre']
        employeur_nom = offre['employeur_nom']
        date_debut = offre['date_debut']

        offre_info = {
            "ID Offre": id_offre,
            "Titre": titre,
            "Nom de l'employeur": employeur_nom,
            "Date de début": date_debut
        }
        if save_to_file(offre_info):
            new_offers = True
            print("ID Offre:", id_offre)
            print("Titre:", titre)
            print("Nom de l'employeur:", employeur_nom)
            print("Date de début:", date_debut)
            print("-" * 25)
            print()

    if new_offers:
        winsound.Beep(300, 300)  # Play a softer sound when new offers are found
    else:
        print("No new job offers found at", datetime.now())

def job():
    result = request_new()
    if result:
        parse_result(result)

schedule.every(15).minutes.do(job)

job()
while True:
    schedule.run_pending()
    time.sleep(1)
