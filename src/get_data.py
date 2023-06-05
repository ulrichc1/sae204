# Author : Ulrich COUDIN
# Date : 04/06/2023
# BUT Informatique - Groupe B2
# SAÉ 2.04 - Exploitation d'une base de données

import pandas as pd


# Analyse de la structure de données

# Données dynamiques
# addresse de téléchargement au format JSON
url = "https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/download/?format=json&timezone=Europe/Berlin&lang=fr"

# Données statiques
# addresse de téléchargement au format JSON
url2 = "https://opendata.paris.fr/explore/dataset/velib-emplacement-des-stations/download/?format=json&timezone=Europe/Berlin&lang=fr"

# Données GeoJSON
# addresse de téléchargement au format GeoJSON
url3 = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/exports/geojson?lang=fr&timezone=Europe%2FBerlin"


# récupération du fichier JSON à l'aide du module Pandas

def get_data(link: str) -> list:
    """
    Récupère les données du fichier JSON
        :param link: lien de téléchargement du fichier JSON
        :type link: str
        :return: Liste des données
        :rtype: list
    """
    df = pd.read_json(link)  # récupération du fichier JSON
    info = df["fields"]  # récupération des données
    data = []
    for i in range(len(info)):  # ajout des données dans la liste data
        data.append(info[i])
    return data  # retourne la liste data


def extract_dynamic_data(link: str) -> list:
    """
    Extrait les données dynamiques du fichier JSON
        :param link: lien de téléchargement du fichier JSON
        :type link: str
        :return: Liste des données dynamiques
        :rtype: list
    """
    data = get_data(link) # récupération des données
    for i in range(len(data)): # suppression des données inutiles
        del data[i]["name"]
        del data[i]["capacity"]
        del data[i]["is_renting"]
        del data[i]["is_returning"]
        del data[i]["duedate"]
        del data[i]["coordonnees_geo"]
    return data # retourne la liste data
