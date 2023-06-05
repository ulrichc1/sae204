import folium
from sql import *
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

# Arrondissements de Paris

arrondissements_paris = gpd.read_file("../data/arrondissements.geojson")

# Conversion de c_ar en string
arrondissements_paris["c_ar"] = arrondissements_paris["c_ar"].astype(str)


# On récupère les dernières données de chaque station

def get_latest_stations() -> list:
    """
    On récupère les dernières données de chaque station
        :return: liste des données des stations
        :rtype: list
    """
    query = """SELECT station_information.station_id, name, lat, lon, capacity, available_docks, available_electric_bikes, 
    available_mechanical_bikes, available_bikes, status, last_update, district_name FROM station_information,station_status 
    WHERE station_information.station_id = station_status.station_id 
    AND station_status.last_update >= NOW() - INTERVAL 9 MINUTE 
    GROUP BY station_information.station_id"""
    cursor = db.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# Conversion en csv des données des stations

def convert_to_csv() -> None:
    """
    Conversion en csv des données des stations
        :return:
    """
    # Création d'un DataFrame à partir des résultats de la requête
    stations = get_latest_stations()
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

    # Enregistrement du DataFrame dans un fichier CSV
    df.to_csv('../data/stations_paris.csv', index=False)


def convert_to_csv_by_arrondissement() -> None:
    """
    Conversion en csv des données des stations regroupées par arrondissement
        :return:
    """
    # Création d'un DataFrame à partir des résultats de la requête
    stations = get_latest_stations()
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
    df['electric_bikes_percentage'] = df['available_electric_bikes'] / df['available_bikes'] * 100
    df['mechanical_bikes_percentage'] = df['available_mechanical_bikes'] / df['available_bikes'] * 100
    df['total_bikes_percentage'] = df['available_bikes'] / df['capacity'] * 100
    df['docks_percentage'] = df['available_docks'] / df['capacity'] * 100

    # Groupement par arrondissement pour compter le nombre de stations disponibles et indisponibles
    df['nb_stations_dispo'] = df.apply(lambda x: 1 if x['status'] == 1 else 0, axis=1)
    df['nb_stations_indispo'] = df.apply(lambda x: 1 if x['status'] == 0 else 0, axis=1)
    df_agg = df.groupby(['arrondissement']).agg({
        'electric_bikes_percentage': 'mean',
        'mechanical_bikes_percentage': 'mean',
        'total_bikes_percentage': 'mean',
        'docks_percentage': 'mean',
        'station_id': 'size',
        'nb_stations_dispo': 'sum',
        'nb_stations_indispo': 'sum'
    }).reset_index()

    # Renommage de la colonne "station_id" en "nb_stations"
    df_agg = df_agg.rename(columns={'station_id': 'nb_stations'})

    # Sélection des colonnes souhaitées
    df_agg = df_agg[['arrondissement', 'electric_bikes_percentage', 'mechanical_bikes_percentage',
                     'total_bikes_percentage', 'docks_percentage', 'nb_stations', 'nb_stations_dispo',
                     'nb_stations_indispo']]

    # Enregistrement du DataFrame agrégé dans un fichier CSV
    df_agg.to_csv('../data/stations_paris_by_arrondissement.csv', index=False)


def create_station_status_map() -> None:
    """
    Création d'une carte Folium (HTML) sur les informations des stations
    :return: None
    """

    # Focalisation de la carte sur Paris
    map = folium.Map(location=[48.8566, 2.3522], zoom_start=13)

    # Ajout des marqueurs sur la carte
    for station in get_latest_stations():
        # Création du label
        if station[9] == 1:  # La station est disponible
            icon_color = "lightblue"
        else:  # La station est indisponible
            icon_color = "gray"

        label = folium.Marker(
            location=[station[2], station[3]],
            icon=folium.Icon(color=icon_color, icon="bicycle", prefix="fa", icon_color="white")
        )

        # Ajout des infos comme tooltip
        # Conversion du statut en texte
        if station[9] == 1:
            status = "Disponible"
        else:
            status = "Indisponible"
        # Conversion de la date en texte
        date = station[10].strftime("%d/%m/%Y %H:%M:%S")
        # Ajout des infos comme tooltip avec un pop-up plus grand
        tooltip = f" ID : {station[0]} <br><br> Station : {station[1]} ({station[11]}) <br><br> Statut : {status}<br><br>   Capacité : {station[4]}  <br><br> Nombre de bornettes disponibles : {station[5]} <br><br> Nombre de vélos électriques disponibles : {station[6]} <br><br> Nombre de vélos mécaniques disponibles : {station[7]} <br><br> Date de mise à jour : {date}"
        label.add_child(folium.Popup(tooltip, max_width=300, min_width=200))

        # Ajout du marqueur sur la carte
        label.add_to(map)

    # Enregistrer la carte dans un fichier HTML
    map.save('../maps/carte_stations_status_velo.html')


# Carte Folium (HTML) sur les stations par arrondissement

def tracer_arrondissement() -> None:
    """
    Création d'une carte Folium (HTML) sur les stations par arrondissement
    :return: None
    """
    # Créer une carte Folium centrée sur Paris
    paris_map = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    # Parcourir chaque arrondissement et ajouter une couche GeoJson pour chaque arrondissement à la carte
    for i in range(1, 21):
        print(i)
        ebikes = 0
        mbikes = 0
        docks = 0
        nb_stations_dispo = 0
        last_update = " "
        arrondissement = arrondissements_paris[arrondissements_paris["c_ar"] == str(i)]
        geojson = folium.GeoJson(data=arrondissement, name="Arrondissement " + str(i),
                                 style_function=lambda x: {'color': 'red', 'weight': 2})

        # Ajouter une couche de texte pour chaque arrondissement
        folium.GeoJsonTooltip(fields=['c_ar'], aliases=['Arrondissement : '], labels=True, sticky=True,
                              toLocaleString=True).add_to(geojson)

        geojson.add_to(paris_map)

        # Ajouter des marqueurs pour chaque station contenue dans l'arrondissement
        for station in get_latest_stations():
            if arrondissement.contains(Point(station[3], station[2])).any():
                ebikes += station[6]
                mbikes += station[7]
                docks += station[5]
                last_update = station[10].strftime("%d/%m/%Y %H:%M:%S")
                if station[9] == 1:
                    nb_stations_dispo += 1

        # Création du label pour l'arrondissement
        label = folium.Marker(location=[arrondissement["geometry"].centroid.y.values[0],
                                         arrondissement["geometry"].centroid.x.values[0]],
                              icon=folium.Icon(color="lightblue", icon="info", prefix="fa", icon_color="white"))

        # Ajout des informations agrégées comme popup pour l'arrondissement
        popup_content = f"Arrondissement {i}<br><br> "
        popup_content += f"Nombre de vélos électriques : {ebikes}<br><br> "
        popup_content += f"Nombre de vélos mécaniques : {mbikes}<br><br> "
        popup_content += f"Nombre de bornettes disponibles : {docks}<br><br> "
        popup_content += f"Nombre de stations disponibles : {nb_stations_dispo}<br><br> "
        popup_content += f"Date de dernière mise à jour : {last_update}<br><br> "
        popup = folium.Popup(popup_content, max_width=300)
        label.add_child(popup)

        # Ajout du label à la carte
        label.add_to(paris_map)
        print(f"Arrondissement {i} : {ebikes} vélos électriques, {mbikes} vélos mécaniques, {docks} bornettes, {nb_stations_dispo} stations disponibles, Date de dernière mise à jour: {last_update}")

    paris_map.save('../maps/carte_arrondissement.html')


def choropleth(csv_parameter, legend):
    """
    Création d'une carte Folium (HTML) avec un choropleth à partir d'un fichier CSV préalablement créé
        :param csv_parameter:
        :param legend:
        :return:
    """

    # Chargement des données
    velos = "../data/stations_paris_by_arrondissement.csv"
    arr_data = pd.read_csv(velos, delimiter=",")
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    # Création du choropleth
    folium.Choropleth(
        geo_data=arrondissements_paris,
        name="choropleth",
        data=arr_data,
        columns=["arrondissement", f"{csv_parameter}"],
        key_on="feature.properties.c_ar",
        fill_color="YlGn",
        fill_opacity=0.2,  # Modification ici pour avoir un fill_opacity plus transparent
        line_opacity=1,  # Modification ici pour avoir un line_opacity de 1 pour un contour plus visible
        line_color="black",  # Ajout ici pour avoir des contours noirs
        legend_name=legend,
    ).add_to(m)

    # Parcours de chaque arrondissement et ajout d'une couche GeoJson pour chaque arrondissement à la carte
    for i in range(1, 21):
        arrondissement = arrondissements_paris[arrondissements_paris["c_ar"] == str(i)]
        geojson = folium.GeoJson(data=arrondissement, name="Arrondissement " + str(i),
                                 style_function=lambda x: {'fillColor': 'white', 'fillOpacity': 0, 'weight': 2,
                                                           'color': 'black'})  # Modification ici pour avoir un
        # fillOpacity de 0 et un weight plus épais pour un contour plus visible

        # Ajouter une couche de texte pour chaque arrondissement
        folium.GeoJsonTooltip(fields=['c_ar'], aliases=['Arrondissement : '], labels=True, sticky=True,
                              toLocaleString=True).add_to(geojson)

        geojson.add_to(m)

    folium.LayerControl().add_to(m)  # Ajout d'un LayerControl pour pouvoir afficher ou non le choropleth
    m.save(f"../choropleths/choropleth_{csv_parameter}.html")  # Sauvegarde de la carte dans un fichier HTML

# convert_to_csv_by_arrondissement() # A décommenter pour créer le fichier CSV (indépendamment des cartes)

#create_station_status_map()
#tracer_arrondissement()
#choropleth("nb_stations_dispo", "Nombre de stations disponibles")
#choropleth("nb_stations_indispo", "Nombre de stations indisponibles")
#choropleth("total_bikes_percentage", "Nombre de vélos (total)")
#choropleth("nb_stations", "Nombre de stations")
#choropleth("electric_bikes_percentage", "Number of electric bikes")
#choropleth("mechanical_bikes_percentage", "Number of mechanical bikes")
#choropleth("docks_percentage", "Nombre de bornettes")
