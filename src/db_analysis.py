# Author : Ulrich COUDIN
# Date : 04/06/2023
# BUT Informatique - Groupe B2
# SAÉ 2.04 - Exploitation d'une base de données

# importation des modules nécessaires
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geo import *
from sql import *
import os


def get_stations(period: str) -> list:
    """
    Récupère les informations des stations avec la période spécifiée.
        :param period: La période de temps ('realtime', 'hour', 'day', 'week').
        :type period: str
        :return: Les informations des stations.
        :rtype: list
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return []

    # Définition de l'intervalle de temps en fonction de la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    # Construction de la requête SQL avec la période spécifiée et les colonnes à extraire
    query = f"""
    SELECT station_information.station_id, name, lat, lon, capacity, available_docks, available_electric_bikes, 
    available_mechanical_bikes, available_bikes, status, MAX(last_update), district_name 
    FROM station_information, station_status 
    WHERE station_information.station_id = station_status.station_id 
    AND last_update >= NOW() - INTERVAL {interval}
    GROUP BY station_information.station_id
    """

    # Exécution de la requête SQL
    cursor = db.cursor()
    cursor.execute(query)
    return cursor.fetchall()  # Récupération des données


def view_global_stats(start_date: str, end_date: str) -> None:
    """
    Affiche les statistiques globales sur les données de la table station_status
        :param start_date: La date de début de la période de temps.
        :type start_date: str
        :param end_date: La date de fin de la période de temps.
        :type end_date: str
        :return: None
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT s.*, t.name 
    FROM station_status s 
    INNER JOIN station_information t ON s.station_id = t.station_id
    """
    data = pd.read_sql_query(query, db)

    # Conversion de la colonne de dates en format de date
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Récupération période de temps
    start_time = start_date
    end_time = end_date

    # Filtrage des données sur la période donnée
    start_date = pd.to_datetime(f'{start_date}')
    end_date = pd.to_datetime(f'{end_date}')
    filtered_data = data[(data['last_update'] >= start_date) & (data['last_update'] <= end_date)]

    # Calcul des statistiques globales par station
    global_stats = filtered_data.groupby(['station_id', 'name']).describe()

    # Affichage des statistiques globales
    print(global_stats)

    # Enregistrement des statistiques globales par station dans un fichier CSV
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/global_stats_by_station_{start_time}_{end_time}.csv'
    global_stats.to_csv(output_file, encoding='utf-8')

    print(f"Les statistiques globales par station ont été enregistrées dans le fichier : {output_file}")


def view_global_stats_by_district(start_date: str, end_date: str) -> None:
    """
    Affiche les statistiques globales par district (villes) sur les données de la table station_status
        :param start_date: La date de début de la période de temps.
        :type start_date: str
        :param end_date: La date de fin de la période de temps.
        :type end_date: str
        :return: None
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT *
    FROM station_status
    """
    data = pd.read_sql_query(query, db)

    # Récupération de la période de temps
    start_time = start_date
    end_time = end_date

    # Conversion de la colonne de dates en format de date
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Filtrage des données sur la période donnée
    start_date = pd.to_datetime(f'{start_date}')
    end_date = pd.to_datetime(f'{end_date}')
    filtered_data = data[(data['last_update'] >= start_date) & (data['last_update'] <= end_date)]

    # Calcul des statistiques globales par commune
    global_stats = filtered_data.groupby('district_name').apply(lambda x: x.describe())

    # Affichage des statistiques globales
    print(global_stats)

    # Enregistrement des statistiques globales par district dans un fichier CSV
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = f'{output_dir}/global_stats_by_district_{start_time}_{end_time}.csv'
    global_stats.to_csv(output_file, encoding='utf-8')

    print(f"Les statistiques globales par district ont été enregistrées dans le fichier : {output_file}")


def view_last_week_data(district_name: str) -> None:
    """
    Affiche les données de la dernière semaine pour une commune donné.
        :param district_name: Le nom de la commune.
        :type district_name: str
        :return: None
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT *
    FROM station_status
    WHERE district_name = '{}'
    """.format(district_name)
    data = pd.read_sql_query(query, db)

    # Si le DataFrame est vide, afficher la liste des district_name disponibles
    if data.empty:
        available_districts_query = """
        SELECT DISTINCT district_name
        FROM station_status
        """
        available_districts = pd.read_sql_query(available_districts_query, db)
        available_districts_list = available_districts['district_name'].tolist()
        print(f"La commune {district_name} n'est pas valide. Les communes disponibles sont :")
        for district in available_districts_list:
            print(district)
        return

    # Conversion de la colonne de dates en format de date
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Obtention de la date de début et de fin de la dernière semaine
    end_date = data['last_update'].max()
    start_date = end_date - pd.DateOffset(weeks=1)

    # Filtrage des données sur la dernière semaine
    filtered_data = data[(data['last_update'] >= start_date) & (data['last_update'] <= end_date)]

    # Enregistrement des données de la dernière semaine dans un fichier CSV
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'last_week_data_{district_name}.csv')
    filtered_data.to_csv(output_file, index=False)

    # Affichage des données de la dernière semaine
    print(filtered_data)


def pie_charts_per_district_period(district_name: str, period: str) -> None:
    """
    Création de graphiques en camembert pour afficher la répartition des vélos électriques et mécaniques dans une commune donnée sur une période donnée.
    :param district_name: Le nom de la commune.
    :type district_name: str
    :param period: La période de temps.
    :type period: str
    :return: None
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    # Requête SQL pour extraire les données selon la période et le regroupement par commune
    query = f"""
       SELECT district_name, SUM(available_mechanical_bikes) AS mechanical_bikes, SUM(available_electric_bikes) AS electric_bikes
       FROM station_status
       WHERE district_name = "{district_name}"
       AND last_update >= NOW() - INTERVAL {interval}
       GROUP BY district_name;
       """

    print(query)
    # Charger les données de la requête SQL dans un DataFrame
    data = pd.read_sql_query(query, db)
    print(data)

    # Si le DataFrame est vide, afficher la liste des district_name disponibles
    if data.empty:
        available_districts_query = """
        SELECT DISTINCT district_name
        FROM station_status
        """
        available_districts = pd.read_sql_query(available_districts_query, db)
        available_districts_list = available_districts['district_name'].tolist()
        print(f"La commune {district_name} n'est pas valide. Les communes disponibles sont :")
        for district in available_districts_list:
            print(district)
        return

    # Création du graphique en camembert
    mechanical_bikes = data['mechanical_bikes'].iloc[0]
    electric_bikes = data['electric_bikes'].iloc[0]
    labels = ['Mechanical bikes', 'Electric bikes']
    sizes = [mechanical_bikes, electric_bikes]
    colors = ['darkturquoise', 'yellowgreen']
    explode = (0.1, 0.1)
    autopct = '%1.1f%%'
    shadow = True

    # Création du graphique en camembert
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct=autopct, shadow=shadow, startangle=90)
    ax.axis('equal')  # Assurer un aspect circulaire du camembert
    ax.set_title(f"Vélos électriques et mécaniques à {district_name}")

    # Sauvegarde du graphique en camembert
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'pie_chart_{district_name}_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)

    # Affichage du graphique en camembert
    plt.show()


def pie_charts_per_station_period(station_code: str, period: str) -> None:
    """
    Création de graphiques en camembert pour afficher la répartition des vélos électriques et mécaniques dans une station donnée sur une période donnée.
    :param station_code: L'ID de la station.
    :type station_code: str
    :param period: La période de temps.
    :type period: str
    :return: None
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    # Requête SQL pour extraire les données selon la période et le regroupement par commune
    query = f"""
       SELECT station_information.name as name, SUM(available_mechanical_bikes) AS mechanical_bikes, SUM(available_electric_bikes) AS electric_bikes
       FROM station_status,station_information
       WHERE station_status.station_id = station_information.station_id
       AND station_information.station_id = {station_code}
       AND last_update >= NOW() - INTERVAL {interval}
       GROUP BY name;
       """

    print(query)
    # Charger les données de la requête SQL dans un DataFrame
    data = pd.read_sql_query(query, db)
    print(data)

    # Si le DataFrame est vide, afficher la liste des district_name disponibles
    if data.empty:
        available_stations_query = """
        SELECT DISTINCT station_id,name
        FROM station_information
        ORDER BY station_id ASC;
        """
        available_districts = pd.read_sql_query(available_stations_query, db)
        print(f"La station {station_code} n'existe pas. Les stations disponibles sont :")
        for index, row in available_districts.iterrows():
            print(f"{row['station_id']} - {row['name']}")
        return

    # Création du graphique en camembert
    mechanical_bikes = data['mechanical_bikes'].iloc[0]
    electric_bikes = data['electric_bikes'].iloc[0]
    name = data['name'].iloc[0]
    labels = ['Mechanical bikes', 'Electric bikes']
    sizes = [mechanical_bikes, electric_bikes]
    colors = ['darkturquoise', 'yellowgreen']
    explode = (0.1, 0.1)
    autopct = '%1.1f%%'
    shadow = True

    # Création du graphique en camembert
    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct=autopct, shadow=shadow, startangle=90)
    ax.axis('equal')  # Assurer un aspect circulaire du camembert
    ax.set_title(f"Vélos électriques et mécaniques à {name}")

    # Sauvegarde du graphique en camembert
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'pie_chart_{name}_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)

    # Affichage du graphique en camembert
    plt.show()


def create_bar_chart_districts_10(period: str) -> None:
    """
    Création d'un graphique en barres pour afficher la moyenne du nombre de vélos disponibles par station (les 10 stations avec la plus grande moyenne)
    :param period: La période de temps.
    :type period: str
    :return:
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    query = """
    SELECT SUM(available_bikes) AS average_bikes, district_name
    FROM station_status
    WHERE last_update >= NOW() - INTERVAL {}
    GROUP BY district_name
    ORDER BY average_bikes DESC
    LIMIT 10  
    """.format(interval)

    # Exécution de la requête
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Création d'un DataFrame à partir des résultats de la requête
    df = pd.DataFrame(results, columns=['average_bikes', 'district_name'])

    print(df)

    # Création du graphique en barres
    data = df['average_bikes'].tolist()
    labels = df['district_name'].tolist()
    colors = ['darkturquoise', 'yellowgreen']

    # Création d'un objet de figure et d'axes
    fig, ax = plt.subplots()

    # Ajout du graphique en barres
    ax.bar(labels, data, color=colors)
    ax.set_title(f"Les 10 communes avec le plus de vélos disponibles ({period})")

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel("Communes")
    plt.ylabel("Nombre de vélos")

    # Ajustement de la taille de la figure
    plt.figure(figsize=(16, 9))

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'10_highest_districts_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def create_bar_chart_districts_10_asc(period: str) -> None:
    """
    Création d'un graphique en barres pour afficher la moyenne du nombre de vélos disponibles par station (les 10
    stations avec le moins de vélos disponibles)
     :param period: La période de temps.
     :type period: str
     :return:
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    query = """
    SELECT SUM(available_bikes) AS average_bikes, district_name
    FROM station_status
    WHERE last_update >= NOW() - INTERVAL {}
    GROUP BY district_name
    ORDER BY average_bikes ASC
    LIMIT 10  
    """.format(interval)

    # Exécution de la requête
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Création d'un DataFrame à partir des résultats de la requête
    df = pd.DataFrame(results, columns=['average_bikes', 'district_name'])

    print(df)

    # Création du graphique en barres
    data = df['average_bikes'].tolist()
    labels = df['district_name'].tolist()
    colors = ['darkturquoise', 'yellowgreen']

    # Création d'un objet de figure et d'axes
    fig, ax = plt.subplots()

    # Ajout du graphique en barres
    ax.bar(labels, data, color=colors)
    ax.set_title(f"Les 10 communes avec le moins de vélos disponibles ({period})")

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel("Communes")
    plt.ylabel("Nombre de vélos")

    # Ajustement de la taille de la figure
    plt.figure(figsize=(16, 9))

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'10_lowest_districts_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def create_bar_chart_districts_10_separated(period: str) -> None:
    """
    Création d'un graphique en barres pour afficher la moyenne du nombre de vélos disponibles par station (les 10 stations avec la plus grande moyenne)
        :param period: La période de temps.
        :type period: str
        :return: None
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    query = """
    SELECT SUM(available_mechanical_bikes) AS avg_bikes_mechanical, SUM(available_electric_bikes) AS avg_bikes_electric, district_name
    FROM station_status
    WHERE last_update >= NOW() - INTERVAL {}
    GROUP BY district_name
    ORDER BY avg_bikes_mechanical DESC
    LIMIT 10  
    """.format(interval)

    # Exécution de la requête
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Création d'un DataFrame à partir des résultats de la requête
    df = pd.DataFrame(results, columns=['avg_bikes_mechanical', 'avg_bikes_electric', 'district_name'])

    print(df)

    # Création du graphique en barres
    data_mechanical = df['avg_bikes_mechanical'].tolist()
    data_electric = df['avg_bikes_electric'].tolist()
    labels = df['district_name'].tolist()
    colors = ['darkturquoise', 'yellowgreen']

    # Création d'un objet de figure et d'axes
    fig, ax = plt.subplots()

    # Ajout des barres pour les vélos mécaniques et les vélos électriques
    ax.bar(labels, data_mechanical, color=colors[0], label='Vélos mécaniques')
    ax.bar(labels, data_electric, color=colors[1], label='Vélos électriques', bottom=data_mechanical)

    ax.set_title(f"Les 10 communes avec le plus de vélos disponibles ({period})")

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel("Communes")
    plt.ylabel("Nombre de vélos")
    plt.legend()

    # Ajustement de la taille de la figure
    plt.figure(figsize=(16, 9))

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'10_highest_districts_separated_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def create_bar_chart_10_stations(period: str) -> None:
    """
    Création d'un graphique en barres pour afficher le nombre de vélos disponibles par station
    (les 10 stations avec le plus de vélos disponibles) (station_information)
        :param period: La période de temps.
        :type period: str
        :return:
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    query = """
    SELECT SUM(ss.available_bikes) AS available_bikes, si.name
    FROM station_status as ss 
    INNER JOIN station_information as si ON ss.station_id = si.station_id
    WHERE ss.last_update >= NOW() - INTERVAL {}
    GROUP BY si.name
    ORDER BY available_bikes DESC
    LIMIT 10
    """.format(interval)

    cursor = db.cursor()  # Création d'un curseur
    cursor.execute(query)  # Exécution de la requête
    results = cursor.fetchall()  # Récupération des résultats de la requête

    df = pd.DataFrame(results, columns=['available_bikes', 'name'])  # Création d'un DataFrame à partir des résultats
    print(df)
    data = df['available_bikes'].tolist()  # Création d'une liste à partir des données du DataFrame
    labels = df['name'].tolist()
    colors = ['darkturquoise', 'yellowgreen']

    fig, ax = plt.subplots(figsize=(12, 8))  # Ajuster la taille de la figure selon vos préférences
    ax.bar(labels, data, color=colors)
    ax.set_title(f"Les 10 stations avec le plus de vélos disponibles ({period})")

    ax.tick_params(axis='x', labelsize=8)  # Ajuster la taille de la police des labels x selon vos préférences
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel("Stations")
    plt.ylabel("Nombre de vélos")

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'10_highest_stations_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def create_bar_chart_10_stations_asc(period: str) -> None:
    """
    Création d'un graphique en barres pour afficher le nombre de vélos disponibles par station
    (les 10 stations avec le moins de vélos disponibles) (station_information)
        :param period: La période de temps.
        :type period: str
        :return:
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    query = """
    SELECT SUM(ss.available_bikes) AS available_bikes, si.name
    FROM station_status as ss 
    INNER JOIN station_information as si ON ss.station_id = si.station_id
    WHERE ss.last_update >= NOW() - INTERVAL {}
    AND ss.status = 1
    AND si.capacity > 0
    GROUP BY si.name
    ORDER BY available_bikes ASC
    LIMIT 10
    """.format(interval)

    cursor = db.cursor()  # Création d'un curseur
    cursor.execute(query)
    results = cursor.fetchall()  # Récupération des résultats de la requête

    df = pd.DataFrame(results, columns=['available_bikes', 'name'])
    print(df)
    data = df['available_bikes'].tolist()
    labels = df['name'].tolist()
    colors = ['darkturquoise', 'yellowgreen']

    fig, ax = plt.subplots(figsize=(12, 8))  # Ajuster la taille de la figure selon vos préférences
    ax.bar(labels, data, color=colors)
    ax.set_title(f"Les 10 stations avec le moins de vélos disponibles ({period})")

    ax.tick_params(axis='x', labelsize=8)  # Ajuster la taille de la police des labels x selon vos préférences
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel("Stations")
    plt.ylabel("Nombre de vélos")

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'10_lowest_stations_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def create_bar_chart_10_stations_separated(period: str) -> None:
    """
    Création d'un graphique en barres pour afficher le nombre de vélos disponibles par station (barres séparées)
    (les 10 stations avec le plus de vélos disponibles) (station_information)
        :param period: La période de temps.
        :type period: str
        :return:
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Requête SQL pour extraire les données selon la période
    if period == 'realtime':
        interval = '9 MINUTE'  # La période de temps en temps réel (-9 minutes)
    elif period == 'hour':
        interval = '1 HOUR'  # La période de temps d'une heure
    elif period == 'day':
        interval = '1 DAY'  # La période de temps d'une journée
    elif period == 'week':
        interval = '1 WEEK'  # La période de temps d'une semaine

    query = """
    SELECT SUM(ss.available_electric_bikes) AS available_electric_bikes, SUM(ss.available_mechanical_bikes) AS available_mechanical_bikes, si.name
    FROM station_status as ss 
    INNER JOIN station_information as si ON ss.station_id = si.station_id
    WHERE ss.last_update >= NOW() - INTERVAL {}
    GROUP BY si.name
    ORDER BY available_bikes DESC
    LIMIT 10
    """.format(interval)

    # Création d'un curseur
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Création d'un dataframe
    df = pd.DataFrame(results, columns=['available_electric_bikes', 'available_mechanical_bikes', 'name'])
    print(df)
    data_electric = df['available_electric_bikes'].tolist()
    data_mechanical = df['available_mechanical_bikes'].tolist()
    labels = df['name'].tolist()
    colors = ['darkturquoise', 'yellowgreen']

    fig, ax = plt.subplots(figsize=(12, 8))  # Ajuster la taille de la figure selon vos préférences

    ax.bar(labels, data_mechanical, color=colors[0], label='Vélos mécaniques')
    ax.bar(labels, data_electric, color=colors[1], label='Vélos électriques', bottom=data_mechanical)

    ax.set_title(f"Les 10 stations avec le plus de vélos disponibles ({period})")

    ax.tick_params(axis='x', labelsize=8)  # Ajuster la taille de la police des labels x selon vos préférences
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel("Stations")
    plt.ylabel("Nombre de vélos")
    plt.legend()

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'10_highest_stations_separated_{period}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def evolution_nbbikes_district(*district_names: str, start_date: str, end_date: str, start_time: str = '09:00:00',
                               end_time: str = '21:00:00') -> None:
    """
    Création d'un graphique linéaire pour afficher l'évolution du nombre de vélos disponibles par commune sur
    une période donnée.
        :param district_names: Noms des communes pour lesquelles afficher l'évolution.
        :type district_names: str
        :param start_date: Date de début de la période (au format 'YYYY-MM-DD').
        :type start_date: str
        :param end_date: Date de fin de la période (au format 'YYYY-MM-DD').
        :type end_date: str
        :param start_time: Heure de début de la période (au format 'HH:MM:SS').
        :type start_time: str
        :param end_time: Heure de fin de la période (au format 'HH:MM:SS').
        :type end_time: str
        :return:
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT s.district_name, s.available_bikes, s.last_update, t.name 
    FROM station_status s 
    INNER JOIN station_information t ON s.station_id = t.station_id
    """
    data = pd.read_sql_query(query, db)

    # Conversion de la colonne de dates en format de date et d'heure
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Filtrage des données sur les communes et la période donnée
    filtered_data = data[(data['district_name'].isin(district_names)) &
                         (data['last_update'] >= f"{start_date} {start_time}") &
                         (data['last_update'] <= f"{end_date} {end_time}")]

    # Calcul de la durée de la période
    duration = pd.to_datetime(end_date + ' ' + end_time) - pd.to_datetime(start_date + ' ' + start_time)

    if duration.days > 1:
        # Agrégation des données par date et calculer la moyenne du nombre de vélos disponibles par jour
        district_stats = filtered_data.groupby([filtered_data['last_update'].dt.date, 'district_name'])
        x_label = 'Date'
    else:
        # Agrégation des données par date et heure et calculer la moyenne du nombre de vélos disponibles par heure
        district_stats = filtered_data.groupby(
            [filtered_data['last_update'].dt.date, filtered_data['last_update'].dt.hour, 'district_name'])
        x_label = 'Date et Heure'

    # Création du graphique linéaire
    fig, ax = plt.subplots(figsize=(10, 6))

    for district_name, district_data in district_stats['available_bikes'].mean().groupby('district_name'):
        district_data.plot(ax=ax, label=district_name, marker='o')

    if duration.days > 1:
        ax.set_title(f'Evolution du nombre de vélos dans les communes ({start_date} - {end_date})')
    else:
        ax.set_title(
            f'Evolution du nombre de vélos dans les communes ({start_date} {start_time} à {end_date} {end_time})')

    ax.legend()

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légendes des axes
    plt.xlabel(x_label)
    plt.ylabel('Nombre de vélos disponibles')

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'nbbikes_evolution_5highestdistricts_week.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def evolution_nbbikes_electric_district(*district_names: str, start_date: str, end_date: str,
                                        start_time: str = '09:00:00',
                                        end_time: str = '21:00:00') -> None:
    """
    Création d'un graphique linéaire pour afficher l'évolution du nombre de vélos électriques disponibles par commune sur une période donnée.
        :param district_names: Noms des communes pour lesquelles afficher l'évolution.
        :type district_names: str
        :param start_date: Date de début de la période (au format 'YYYY-MM-DD').
        :type start_date: str
        :param end_date: Date de fin de la période (au format 'YYYY-MM-DD').
        :type end_date: str
        :param start_time: Heure de début de la période (au format 'HH:MM:SS').
        :type start_time: str
        :param end_time: Heure de fin de la période (au format 'HH:MM:SS').
        :type end_time: str
        :return:
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT s.district_name, s.available_electric_bikes, s.last_update, t.name 
    FROM station_status s 
    INNER JOIN station_information t ON s.station_id = t.station_id
    """
    data = pd.read_sql_query(query, db)

    # Conversion de la colonne de dates en format de date et d'heure
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Filtrage des données sur les communes et la période donnée
    filtered_data = data[(data['district_name'].isin(district_names)) &
                         (data['last_update'] >= f"{start_date} {start_time}") &
                         (data['last_update'] <= f"{end_date} {end_time}")]

    # Calcul de la durée de la période
    duration = pd.to_datetime(end_date + ' ' + end_time) - pd.to_datetime(start_date + ' ' + start_time)

    if duration.days > 1:
        # Agrégation des données par date et calculer la moyenne du nombre de vélos disponibles par jour
        district_stats = filtered_data.groupby([filtered_data['last_update'].dt.date, 'district_name'])
        x_label = 'Date'
    else:
        # Agrégation des données par date et heure et calculer la moyenne du nombre de vélos disponibles par heure
        district_stats = filtered_data.groupby(
            [filtered_data['last_update'].dt.date, filtered_data['last_update'].dt.hour, 'district_name'])
        x_label = 'Date et Heure'

    # Création du graphique linéaire
    fig, ax = plt.subplots(figsize=(10, 6))  # Ajuster la taille de la figure ici

    for district_name, district_data in district_stats['available_electric_bikes'].mean().groupby('district_name'):
        district_data.plot(ax=ax, label=district_name, marker='o')

    if duration.days > 1:
        ax.set_title(f'Evolution du nombre de vélos électriques dans les communes ({start_date} - {end_date})')
    else:
        ax.set_title(
            f'Evolution du nombre de vélos électriques dans les communes ({start_date} {start_time} à {end_date} {end_time})')

    ax.legend()

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légendes des axes
    plt.xlabel(x_label)
    plt.ylabel('Nombre de vélos électriques disponibles')

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'nbelectricbikes_evolution_5highestdistricts_week.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def evolution_nbbikes_mechanical_district(*district_names: str, start_date: str, end_date: str,
                                          start_time: str = '09:00:00',
                                          end_time: str = '21:00:00') -> None:
    """
    Crée un graphique linéaire pour afficher l'évolution du nombre de vélos électriques disponibles par commune sur une période donnée.
        :param district_names: Noms des communes pour lesquelles afficher l'évolution.
        :type district_names: str
        :param start_date: Date de début de la période (au format 'YYYY-MM-DD').
        :type start_date: str
        :param end_date: Date de fin de la période (au format 'YYYY-MM-DD').
        :type end_date: str
        :param start_time: Heure de début de la période (au format 'HH:MM:SS').
        :type start_time: str
        :param end_time: Heure de fin de la période (au format 'HH:MM:SS').
        :type end_time: str
        :return:
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT s.district_name, s.available_mechanical_bikes, s.last_update, t.name 
    FROM station_status s 
    INNER JOIN station_information t ON s.station_id = t.station_id
    """
    data = pd.read_sql_query(query, db)

    # Conversion de la colonne de dates en format de date et d'heure
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Filtrage des données sur les communes et la période donnée
    filtered_data = data[(data['district_name'].isin(district_names)) &
                         (data['last_update'] >= f"{start_date} {start_time}") &
                         (data['last_update'] <= f"{end_date} {end_time}")]

    # Calcul de la durée de la période
    duration = pd.to_datetime(end_date + ' ' + end_time) - pd.to_datetime(start_date + ' ' + start_time)

    if duration.days > 1:
        # Agrégation des données par date et calculer la moyenne du nombre de vélos disponibles par jour
        district_stats = filtered_data.groupby([filtered_data['last_update'].dt.date, 'district_name'])
        x_label = 'Date'
    else:
        # Agrégation des données par date et heure et calculer la moyenne du nombre de vélos disponibles par heure
        district_stats = filtered_data.groupby(
            [filtered_data['last_update'].dt.date, filtered_data['last_update'].dt.hour, 'district_name'])
        x_label = 'Date et Heure'

    # Création du graphique linéaire
    fig, ax = plt.subplots(figsize=(10, 6))  # Ajuster la taille de la figure ici

    for district_name, district_data in district_stats['available_mechanical_bikes'].mean().groupby('district_name'):
        district_data.plot(ax=ax, label=district_name, marker='o')

    if duration.days > 1:
        ax.set_title(f'Evolution du nombre de vélos mécaniques dans les communes ({start_date} - {end_date})')
    else:
        ax.set_title(
            f'Evolution du nombre de vélos mécaniques dans les communes ({start_date} {start_time} à {end_date} {end_time})')

    ax.legend()

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel(x_label)
    plt.ylabel('Nombre de vélos mécaniques disponibles')

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'nbmechanicalbikes_evolution_5highestdistricts_week.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def evolution_nbbikes_district_double(*district_name: str, start_date: str, end_date: str, start_time: str = '09:00:00',
                                      end_time: str = '21:00:00') -> None:
    """
    Crée un graphique linéaire pour afficher l'évolution du nombre de vélos disponibles par commune sur une période donnée.
        :param district_name: Noms des communes pour lesquelles afficher l'évolution.
        :type district_name: str
        :param start_date: Date de début de la période (au format 'YYYY-MM-DD').
        :type start_date: str
        :param end_date: Date de fin de la période (au format 'YYYY-MM-DD').
        :type end_date: str
        :param start_time: Heure de début de la période (au format 'HH:MM:SS').
        :type start_time: str
        :param end_time: Heure de fin de la période (au format 'HH:MM:SS').
        :type end_time: str
        :return:
    """
    # Chargement des données de la table station_status dans un DataFrame
    query = """
    SELECT s.district_name, s.available_electric_bikes,s.available_mechanical_bikes, s.last_update, t.name 
    FROM station_status s 
    INNER JOIN station_information t ON s.station_id = t.station_id
    """
    data = pd.read_sql_query(query, db)

    # Conversion de la colonne de dates en format de date et d'heure
    data['last_update'] = pd.to_datetime(data['last_update'])

    # Filtrage des données sur les communes et la période donnée
    filtered_data = data[(data['district_name'].isin(district_name)) &
                         (data['last_update'] >= f"{start_date} {start_time}") &
                         (data['last_update'] <= f"{end_date} {end_time}")]

    # Calcul de la durée de la période
    duration = pd.to_datetime(end_date + ' ' + end_time) - pd.to_datetime(start_date + ' ' + start_time)

    if duration.days > 1:
        # Agréger les données par date et calculer la moyenne du nombre de vélos disponibles par jour
        district_stats = filtered_data.groupby([filtered_data['last_update'].dt.date, 'district_name'])
        x_label = 'Date'
    else:
        # Agréger les données par date et heure et calculer la moyenne du nombre de vélos disponibles par heure
        district_stats = filtered_data.groupby(
            [filtered_data['last_update'].dt.date, filtered_data['last_update'].dt.hour, 'district_name'])
        x_label = 'Date & hour'

    # Création du graphique linéaire
    fig, ax = plt.subplots(figsize=(10, 6))  # Ajuster la taille de la figure ici

    for district_name, district_data in district_stats['available_electric_bikes'].mean().groupby('district_name'):
        district_data.plot(ax=ax, label=f"Electric bikes", marker='o', color="lightgreen")

    for district_name, district_data in district_stats['available_mechanical_bikes'].mean().groupby('district_name'):
        district_data.plot(ax=ax, label=f"Mechanical bikes", marker='o', color="lightblue")

    if duration.days > 1:
        ax.set_title(f'Evolution of the number of bikes in {district_name} ({start_date} - {end_date})')
    else:
        ax.set_title(
            f'Evolution of the number of bikes in {district_name} ({start_date} {start_time} to {end_date} {end_time})')

    ax.legend()

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")

    # Légende des axes
    plt.xlabel(x_label)
    plt.ylabel('Number of available bikes')

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir,
                               f'evolution_nbbikes_district_{",".join(district_name)}_{start_date}_{end_date}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def evolution_station_district(district: str) -> None:
    """
    Renvoie le graphique linéaire du nombre de vélos disponibles d'une station dans une ville précise
        :param district: Nom de la ville
        :type district: str
        :return:
    """
    # Requête SQL pour extraire la liste des stations disponibles pour le district passé en paramètre
    stations_query = f""" SELECT name FROM station_information INNER JOIN station_status on station_information.station_id = station_status.station_id WHERE district_name= '{district}' """
    cursor = db.cursor()
    cursor.execute(stations_query)
    stations = [station[0] for station in cursor.fetchall()]
    stationFound = False
    # Vérification si le district passé en paramètre est présent dans la liste des districts disponibles
    while not stationFound:
        print(f"Voici la liste des stations disponibles pour la ville de {district}: {', '.join(stations)}")
        station_rq = input(
            "Veuillez saisir le nom de la station dont vous souhaitez afficher l'évolution du nombre de vélos disponibles: ")
        if station_rq in stations:
            stationFound = True
        else:
            print("Veuillez saisir un nom de station valide")

    # On récupère les données des vélos disponibles pour la station sélectionnée
    query = f""" 
    SELECT si.name, ss.available_bikes, ss.last_update FROM station_information si
    INNER JOIN station_status ss ON si.station_id = ss.station_id
    WHERE si.name = '{station_rq}' AND ss.district_name = '{district}'
    """
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Création d'un DataFrame à partir des résultats de la requête
    df = pd.DataFrame(results, columns=['station_name', 'available_bikes', 'last_update'])
    # Création du graphique linéaire
    data = df['available_bikes'].tolist()
    labels = df['last_update'].tolist()
    print(labels)
    # Création d'un objet de figure et d'axes
    fig, ax = plt.subplots()

    # Ajout du graphique linéaire
    ax.plot(labels, data)
    ax.set_title(f'Evolution of the number of bikes available in {district}')

    # Ajustement de la taille et rotation de la police des x labels
    ax.tick_params(axis='x', labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", rotation_mode="anchor")
    # Légende des axes
    plt.xlabel('Date')
    plt.ylabel('Number of bikes')

    # Ajustement de la taille de la figure
    plt.figure(figsize=(16, 9))

    # Affichage du graphique
    plt.show()


def create_pie_charts(df: pd.DataFrame) -> None:
    """
    Création de graphiques camemberts pour les arrondissements avec le plus et le moins de vélos électriques et mécaniques
        :param df: DataFrame contenant les données des vélos disponibles
        :type df: pd.DataFrame
        :return: 
    """

    # Tri des arrondissements par nombre de vélos électriques et mécaniques
    arrondissements = df.groupby('arrondissement').sum().sort_values(by=['electric_bikes', 'mechanical_bikes'],
                                                                     ascending=False)

    # Sélection des 5 arrondissements avec le plus de vélos électriques et mécaniques
    top_arrondissements = arrondissements.head(5)

    # Sélection des 5 arrondissements avec le moins de vélos électriques et mécaniques
    bottom_arrondissements = arrondissements.tail(5)

    # Création des pie charts pour les arrondissements avec le plus de vélos électriques et mécaniques
    fig, axs = plt.subplots(nrows=2, ncols=5, figsize=(20, 10))
    for i, (arrondissement, row) in enumerate(top_arrondissements.iterrows()):
        ax = axs[0, i]
        ax.pie([row['electric_bikes'], row['mechanical_bikes']], labels=['Vélos électriques', 'Vélos mécaniques'],
               autopct='%1.1f%%')
        ax.set_title(f"Arrondissement {arrondissement}")

    # Création des pie chart pour les arrondissements avec le moins de vélos électriques et mécaniques
    for i, (arrondissement, row) in enumerate(bottom_arrondissements.iterrows()):
        ax = axs[1, i]
        ax.pie([row['electric_bikes'], row['mechanical_bikes']], labels=['Vélos électriques', 'Vélos mécaniques'],
               autopct='%1.1f%%')
        ax.set_title(f"Arrondissement {arrondissement}")

    # Ajout du titre global
    fig.suptitle("Répartition des vélos électriques et mécaniques par arrondissement")

    # Sauvegarde du graphique
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'pie_charts_arrondissements_{arrondissement}.png')
    fig.savefig(output_file)

    # Fermeture de la figure
    plt.close(fig)


def create_combined_bar_chart_arrondissements(period: str) -> None:
    """
    Création d'un graphique en barres combiné pour afficher le nombre de vélos électriques et mécaniques par arrondissement
    (les 10 arrondissements avec le plus de vélos électriques et mécaniques) 
        :param period: La période de temps.
        :type period: str
        :return:
    """
    # Vérification de la période de temps
    if period not in ['realtime', 'hour', 'day', 'week']:
        print(f"La période {period} n'est pas valide. Les périodes disponibles sont : realtime, hour, day, week")
        return

    # Création d'un DataFrame à partir des résultats de la requête
    stations = get_stations(period=period)  # Utilisation de la période spécifiée
    df = pd.DataFrame(stations, columns=['station_id', 'name', 'lat', 'lon', 'capacity', 'available_docks',
                                         'available_electric_bikes', 'available_mechanical_bikes',
                                         'available_bikes', 'status', 'last_update', 'district_name'])

    # Ajout d'une colonne avec le numéro de l'arrondissement si la station est dans Paris et appartient à un
    # arrondissement à l'aide de la géométrie
    arrondissements_paris["c_ar"] = arrondissements_paris["c_ar"].astype(str)
    for i in range(1, 21):
        arrondissement_num = arrondissements_paris[(arrondissements_paris["c_ar"]) == str(i)]
        in_arrondissement = df.apply(lambda row: arrondissement_num.contains(Point(row['lon'], row['lat'])).any(),
                                     axis=1)
        df.loc[in_arrondissement, 'arrondissement'] = str(i)

    # Ajout des colonnes pourcentage
    df['electric_bikes'] = df['available_electric_bikes']
    df['mechanical_bikes'] = df['available_mechanical_bikes']
    df['total_bikes'] = df['available_bikes']
    df['docks'] = df['available_docks']

    # Groupement par arrondissement pour compter le nombre de stations disponibles et indisponibles
    df['nb_stations_dispo'] = df.apply(lambda x: 1 if x['status'] == 1 else 0, axis=1)
    df['nb_stations_indispo'] = df.apply(lambda x: 1 if x['status'] == 0 else 0, axis=1)
    df_agg = df.groupby(['arrondissement']).agg({
        'electric_bikes': 'sum',
        'mechanical_bikes': 'sum',
        'total_bikes': 'sum',
        'docks': 'sum',
        'station_id': 'size',
        'nb_stations_dispo': 'sum',
        'nb_stations_indispo': 'sum'
    }).reset_index()

    # Renommage de la colonne "station_id" en "nb_stations"
    df_agg = df_agg.rename(columns={'station_id': 'nb_stations'})

    # Sélection des colonnes souhaitées
    df_agg = df_agg[['arrondissement', 'electric_bikes', 'mechanical_bikes']]

    # Sélection des 10 arrondissements avec le plus de vélos électriques et mécaniques
    top_10_highest = df_agg.nlargest(10, ['electric_bikes', 'mechanical_bikes'])

    # Création du graphique combiné en barres
    fig, ax = plt.subplots()
    x = np.arange(len(top_10_highest))
    width = 0.35

    # Barres pour les vélos électriques
    ax.bar(x - width / 2, top_10_highest['electric_bikes'], width, label='Vélos électriques', color='yellowgreen')
    # Barres pour les vélos mécaniques
    ax.bar(x + width / 2, top_10_highest['mechanical_bikes'], width, label='Vélos mécaniques', color='darkturquoise')

    ax.set_title(f"Les 10 arrondissements de Paris avec le plus de vélos électriques et mécaniques ({period})")
    ax.set_xlabel("Arrondissements")
    ax.set_ylabel("Nombre de vélos")
    ax.set_xticks(x)
    ax.set_xticklabels(top_10_highest['arrondissement'])
    ax.legend()

    # Ajustement de la taille et rotation de la police des x labels
    plt.xticks(rotation=20, ha='right')
    # Sauvegarde du graphique combiné
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file_combined = os.path.join(output_dir, f'10_highest_arrondissements_combined_{period}.png')
    fig.savefig(output_file_combined)
    plt.close(fig)

    # Sélection des 10 arrondissements avec le moins de vélos électriques et mécaniques
    top_10_lowest = df_agg.nsmallest(10, ['electric_bikes', 'mechanical_bikes'])

    # Création du graphique combiné en barres
    fig, ax = plt.subplots()
    x = np.arange(len(top_10_lowest))
    width = 0.35

    # Barres pour les vélos électriques
    ax.bar(x - width / 2, top_10_lowest['electric_bikes'], width, label='Vélos électriques', color='yellowgreen')
    # Barres pour les vélos mécaniques
    ax.bar(x + width / 2, top_10_lowest['mechanical_bikes'], width, label='Vélos mécaniques', color='darkturquoise')

    ax.set_title(f"Les 10 arrondissements de Paris avec le moins de vélos électriques et mécaniques ({period})")
    ax.set_xlabel("Arrondissements")
    ax.set_ylabel("Nombre de vélos")
    ax.set_xticks(x)
    ax.set_xticklabels(top_10_lowest['arrondissement'])
    ax.legend()

    # Ajustement de la taille et rotation de la police des x labels
    plt.xticks(rotation=20, ha='right')
    # Sauvegarde du graphique combiné
    output_dir = 'views'
    os.makedirs(output_dir, exist_ok=True)
    output_file_combined = os.path.join(output_dir, f'10_lowest_arrondissements_combined_{period}.png')
    fig.savefig(output_file_combined)
    plt.close(fig)
    print("Graphiques combinés créés avec succès.")


if __name__ == '__main__':  # Décommenter les fonctions à tester
    # view_global_stats('2023-05-28', '2023-06-04')
    # view_global_stats_by_district('2023-05-28', '2023-06-04')
    # view_last_week_data('Meudon')
    # pie_charts_per_district_period('Paris', 'realtime')
    # pie_charts_per_district_period('Paris', 'hour')
    # pie_charts_per_district_period('Paris', 'day')
    # pie_charts_per_district_period('Boulogne-Billancourt', 'week')
    # pie_charts_per_district_period('Issy-les-Moulineaux', 'week')
    # pie_charts_per_district_period('Ivry-sur-Seine', 'week')
    # pie_charts_per_district_period('Vitry-sur-Seine', 'week')
    #pie_charts_per_station_period('92004', 'realtime')
    #pie_charts_per_station_period('43005', 'hour')
    #pie_charts_per_station_period('2108', 'day')
    #pie_charts_per_station_period('13123', 'week')
    # create_bar_chart_districts_10('realtime')
    # create_bar_chart_10_stations('realtime')
    # create_bar_chart_10_stations('realtime')
    # evolution_nbbikes_district('Paris', 'Boulogne-Billancourt', 'Issy-les-Moulineaux', 'Ivry-sur-Seine',
    # 'Vitry-sur-Seine', start_date='2023-05-28', end_date='2023-06-04', start_time='09:00:00',
    # end_time='21:00:00')
    # evolution_nbbikes_electric_district('Paris', 'Boulogne-Billancourt', 'Issy-les-Moulineaux', 'Ivry-sur-Seine',
    # 'Vitry-sur-Seine', start_date='2023-05-28', end_date='2023-06-04',
    # start_time='09:00:00',
    # end_time='21:00:00')
    # evolution_nbbikes_mechanical_district('Paris', 'Boulogne-Billancourt', 'Issy-les-Moulineaux', 'Ivry-sur-Seine',
    # 'Vitry-sur-Seine', start_date='2023-05-28', end_date='2023-06-04',
    # start_time='09:00:00',
    # end_time='21:00:00')
    # create_bar_chart_districts_10('week')
    # create_bar_chart_10_stations('realtime')
    # create_bar_chart_10_stations('day')
    # create_bar_chart_10_stations('week')
    # create_bar_chart_10_stations_asc('day')
    # create_bar_chart_districts_10_asc('day')
    # create_bar_chart_districts_10_separated('day')
    # create_bar_chart_10_stations_separated('day')
    # create_combined_bar_chart_arrondissements('week')
    # evolution_nbbikes_district_double('Paris', start_date='2023-05-28', end_date='2023-06-04', start_time='09:00:00',
    # end_time='21:00:00')
