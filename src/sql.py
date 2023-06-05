# Author : Ulrich COUDIN
# Date : 04/06/2023
# BUT Informatique - Groupe B2
# SAÉ 2.04 - Exploitation d'une base de données

# Importation pour utiliser mysql et manipuler les données
from get_data import *
import mysql.connector
import datetime

# Debug (False pour désactiver / True pour activer)
debug = True

# Connexion à la base de données
# Paramètres de connexion
connection_params = {
    'host': "localhost",
    'user': "root",
    'password': "",
    'database': "velibs",
}

# Création des tables dans la base de données
db = mysql.connector.connect(**connection_params)


def create_tables() -> None:
    """
    Création des tables dans la base de données
        :return: None
    """
    try:
        # création de la table station_information (statique)
        if debug:
            print("Suppression de la table station_information si elle existe")
            print("Création de la table station_information")

        cursor = db.cursor()  # création du curseur
        cursor.execute("DROP TABLE IF EXISTS station_information")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS station_information (station_id VARCHAR(32) NOT NULL PRIMARY KEY, name VARCHAR(255), "
            "lat FLOAT, lon FLOAT, capacity INT)")  # création de la table station_information

        if debug:  # affichage des messages de debug
            print("Création de la table station_information terminée")

        # création de la table station_status (dynamique)
        if debug:
            print("Suppression de la table station_status si elle existe")
            print("Création de la table station_status")

        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS station_status")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS station_status (station_id VARCHAR(32) NOT NULL, district_name VARCHAR(255), "
            "available_electric_bikes INT,"
            "available_mechanical_bikes INT, available_bikes INT,"
            "available_docks INT, status BOOLEAN, last_update TIMESTAMP DEFAULT NOW() ON "
            "UPDATE NOW(), PRIMARY KEY(station_id, last_update), FOREIGN KEY (station_id) REFERENCES "
            "station_information(station_id))"  # création de la table station_status
        )

        if debug:  # affichage des messages de debug
            print("Création de la table station_status terminée")

        # création de la table history_change (logs)
        if debug:
            print("Suppression de la table history_change si elle existe")
            print("Création de la table history_change")

        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS history_change")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS history_change (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, table_name VARCHAR(255), "
            "row_id VARCHAR(32), action VARCHAR(255), date TIMESTAMP DEFAULT NOW() ON UPDATE NOW(), user VARCHAR(255))")
        # création de la table history_change (logs)

        if debug:  # affichage des messages de debug
            print("Création de la table history_change terminée")

    except Exception as e:  # affichage des erreurs
        print("Erreur lors de la création des tables :", e)

    finally:  # fermeture du curseur et de la connexion
        cursor.close()
        db.close()


# Insertion des données dans la base de données
def insert_data(table_name: str, data: list) -> None:
    """
    Insertion des données dans la base de données
        :param table_name: nom de la table dans laquelle insérer les données
        :type table_name: str
        :param data: données à insérer
        :type data: list
        :return:
    """
    db = mysql.connector.connect(**connection_params)  # connexion à la base de données
    nb_rows = 0  # initialisation du nombre de lignes insérées
    try:  # insertion des données dans la base de données
        cursor = db.cursor()
        for i in range(len(data)):
            if table_name == "station_information":
                sql = "INSERT INTO station_information (station_id, name, lat, lon, capacity) VALUES (%s, %s, %s, %s, " \
                      "%s)"
                val = (
                    data[i]["stationcode"], data[i]["name"], data[i]["coordonnees_geo"][0],
                    data[i]["coordonnees_geo"][1],
                    data[i]["capacity"])
            elif table_name == "station_status":
                status = 1 if data[i]["is_installed"] == 'OUI' else 0
                sql = "INSERT INTO station_status (station_id, available_electric_bikes, " \
                      "available_mechanical_bikes, available_bikes, available_docks, status, district_name) VALUES (" \
                      "%s, %s, %s, %s, %s, %s, %s)"
                val = (data[i]["stationcode"], data[i]["ebike"], data[i]["mechanical"], data[i]["numbikesavailable"],
                       data[i]["numdocksavailable"], status, data[i]["nom_arrondissement_communes"])
            cursor.execute(sql, val)
            db.commit()
            # On incrémente une variable pour compter le nombre de lignes insérées
            nb_rows += cursor.rowcount
    except Exception as e:  # affichage des erreurs
        print("Erreur lors de l'insertion des données :", e)
    finally:  # fermeture du curseur et de la connexion
        cursor.close()
        db.close()
        # On affiche le nombre de lignes insérées
        print(f"{nb_rows} lignes insérées.")


# Mis à jour des données dynamiques dans la base de données
def update_data(data: list) -> None:
    """
    Mis à jour des données dynamiques dans la base de données
        :param data:
        :type data: list
        :return:
    """

    db = mysql.connector.connect(**connection_params)  # connexion à la base de données
    nb_rows = 0  # initialisation du nombre de lignes modifiées
    try:
        cursor = db.cursor()
        for i in range(len(data)):
            status = 1 if data[i]["is_installed"] == 'OUI' else 0
            sql = "INSERT INTO station_status (station_id, available_electric_bikes, " \
                  "available_mechanical_bikes, available_bikes, available_docks, status, district_name) VALUES (" \
                  "%s, %s, %s, %s, %s, %s, %s)"
            val = (data[i]["stationcode"], data[i]["ebike"], data[i]["mechanical"], data[i]["numbikesavailable"],
                   data[i]["numdocksavailable"], status, data[i]["nom_arrondissement_communes"])
            cursor.execute(sql, val)
            db.commit()
            # On incrémente une variable pour compter le nombre de lignes modifiées
            nb_rows += cursor.rowcount
    except Exception as e:  # affichage des erreurs
        print("Erreur lors de la mise à jour des données :", e)
    finally: # fermeture du curseur et de la connexion
        cursor.close()
        db.close()
        # On affiche le nombre de lignes insérées
        print(f"{nb_rows} lignes insérées.")


# Triggers pour les logs
def create_triggers() -> None:
    """
    Création des triggers pour les logs (history_change)
        :return:
    """
    db = mysql.connector.connect(**connection_params) # connexion à la base de données
    try:
        cursor = db.cursor() # création du curseur
        # Triggers pour la table station_status (gestion du booléen en tinyint)
        cursor.execute("DROP TRIGGER IF EXISTS station_status_trigger_bool")
        cursor.execute("CREATE TRIGGER station_status_trigger_bool BEFORE INSERT ON station_status FOR EACH ROW "
                       "SET NEW.status = IF(NEW.status = 1, TRUE, FALSE)")
        cursor.execute("DROP TRIGGER IF EXISTS station_status_trigger_bool2")
        cursor.execute("CREATE TRIGGER station_status_trigger_bool2 BEFORE UPDATE ON station_status FOR EACH ROW "
                       "SET NEW.status = IF(NEW.status = 1, TRUE, FALSE)")
        # Trigger pour la table station_information (gestion des logs)
        cursor.execute("DROP TRIGGER IF EXISTS station_information_trigger")
        cursor.execute("CREATE TRIGGER station_information_trigger AFTER INSERT ON station_information FOR EACH ROW "
                       "INSERT INTO history_change (table_name, row_id, action, user) VALUES ('station_information', "
                       "NEW.station_id, 'INSERT', system_user())")
        cursor.execute("DROP TRIGGER IF EXISTS station_information_trigger2")
        cursor.execute("CREATE TRIGGER station_information_trigger2 AFTER UPDATE ON station_information FOR EACH ROW "
                       "INSERT INTO history_change (table_name, row_id, action, user) VALUES ('station_information', "
                       "NEW.station_id, 'UPDATE', system_user())")
        cursor.execute("DROP TRIGGER IF EXISTS station_information_trigger3")
        cursor.execute("CREATE TRIGGER station_information_trigger3 AFTER DELETE ON station_information FOR EACH ROW "
                       "INSERT INTO history_change (table_name, row_id, action,user ) VALUES ('station_information', "
                       "OLD.station_id, 'DELETE', system_user())")
        # Trigger pour la table station_status (gestion des logs)
        cursor.execute("DROP TRIGGER IF EXISTS station_status_trigger")
        cursor.execute("CREATE TRIGGER station_status_trigger AFTER INSERT ON station_status FOR EACH ROW INSERT INTO "
                       "history_change (table_name, row_id, action,user) VALUES ('station_status', NEW.station_id, "
                       "'INSERT', system_user())")
        cursor.execute("DROP TRIGGER IF EXISTS station_status_trigger2")
        cursor.execute("CREATE TRIGGER station_status_trigger2 AFTER UPDATE ON station_status FOR EACH ROW INSERT "
                       "INTO history_change (table_name, row_id, action,user) VALUES ('station_status', NEW.station_id, "
                       "'UPDATE', system_user())")
        cursor.execute("DROP TRIGGER IF EXISTS station_status_trigger3")
        cursor.execute("CREATE TRIGGER station_status_trigger3 AFTER DELETE ON station_status FOR EACH ROW INSERT "
                       "INTO history_change (table_name, row_id, action,user) VALUES ('station_status', OLD.station_id, "
                       "'DELETE', system_user())")
    except Exception as e: # affichage des erreurs
        print("Erreur lors de la création des triggers :", e)
    finally:
        cursor.close()
        db.close()
        # On affiche un message de création des triggers
        print("Triggers créés.")


# On récupère les données dynamiques
def get_station_status() -> tuple:
    """
    Récuparation des données dynamiques
        :return: nom des colonnes et données
        :rtype: tuple
    """
    db = mysql.connector.connect(**connection_params) # connexion à la base de données
    cursor = db.cursor()    # création du curseur
    cursor.execute("SELECT * FROM station_status WHERE last_update >= NOW() - INTERVAL 9 MINUTE")  # Requête SQL
    # (données dynamiques en temps réel)
    rows = cursor.fetchall()   # récupération des données
    column_names = [desc[0] for desc in cursor.description]  # récupération des noms des colonnes
    cursor.close()
    db.close() # fermeture du curseur et de la connexion
    return column_names, rows # on retourne les noms des colonnes et les données correspondantes

# Création des tables dans la base de données
# create_tables()

# Création des triggers pour les logs
# create_triggers()

# Insertion des données statiques dans la base de données
# insert_data("station_information", data_statique)

# Insertion des données dynamiques dans la base de données
# insert_data("station_status", data_dynamique)
