# Author : Ulrich COUDIN
# Date : 04/06/2023
# BUT Informatique - Groupe B2
# SAÉ 2.04 - Exploitation d'une base de données

# importation des modules nécessaires
import json
import time
from sql import *
from get_data import *

data_dynamique = extract_dynamic_data(url)  # données dynamiques
print(f'données dynamiques : {data_dynamique[0]}')

data_statique = get_data(url2)  # données statiques
print(f'données statiques : {data_statique[0]}')


# PAS OBLIGATOIRE (sauvegarde des données dynamiques dans un fichier json)
def save_to_json() -> None:
    """
    Sauvegarde les données dynamiques dans un fichier json
        :return:
    """
    now = time.localtime() # On récupère la date et l'heure
    filename = f"station_status_{time.strftime('%Y%m%d', now)}.json" # On crée le nom du fichier
    column_names, rows = get_station_status() # On récupère les données dynamiques
    data = []
    for row in rows: # On crée un dictionnaire avec les données dynamiques
        data.append(dict(zip(column_names, row)))
    with open(filename, 'a+') as file: # On écrit les données dans le fichier json
        file.seek(0, 2)
        if file.tell() == 0: # Cas où le fichier est vide
            file.write('[')
        else: # Cas où le fichier n'est pas vide
            file.seek(file.tell() - 2, 0)
            file.truncate()
            file.write(']')
            file.write(',')
        json.dump(data, file, default=str, indent=4)
        file.write(']')


# Mise à jour des données dynamiques dans la base de données toutes les 10 minutes (de 9h à 21h)
while True:
    try:
        # On affiche un message de mise à jour
        now = datetime.datetime.now()
        heure = now.hour # On récupère l'heure
        if heure >= 21 or heure < 9: # Si l'heure est entre 21h et 9h, on ne met pas à jour les données
            print('Pas de mise à jour des données dynamiques entre 21h et 9h')
            break
        else:
            # On récupère les données dynamiques
            data_dynamique = extract_dynamic_data(url)
            # On met à jour les données dynamiques dans la base de données
            update_data(data_dynamique)
            print("Mise à jour des données dynamiques effectuée à :", now.strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(600) # On attend 10 minutes avant de mettre à jour les données
    except Exception as e:
        print("Erreur :", e) # On affiche l'erreur
