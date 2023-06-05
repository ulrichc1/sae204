SAE 2.04 - Exploitation d'une base de données
BUT INFORMATIQUE
GROUPE B2:
COUDIN Ulrich 

/**** INSTALLER IMPÉRATIVEMENT CES MODULES AVANT D'UTILISER LE LOGICIEL *****/

  - attrs==23.1.0
  - branca==0.6.0
  - certifi==2023.5.7
  - charset-normalizer==3.1.0
  - click==8.1.3
  - click-plugins==1.1.1
  - cligj==0.7.2
  - colorama==0.4.6
  - contourpy==1.0.7
  - cycler==0.11.0
  - Fiona==1.9.4.post1
  - folium==0.14.0
  - fonttools==4.39.4
  - geopandas==0.13.0
  - idna==3.4
  - Jinja2==3.1.2
  - kiwisolver==1.4.4
  - MarkupSafe==2.1.3
  - matplotlib==3.7.1
  - mysql-connector-python==8.0.33
  - numpy==1.24.3
  - packaging==23.1
  - pandas==2.0.2
  - Pillow==9.5.0
  - protobuf==3.20.3
  - pyparsing==3.0.9
  - pyproj==3.5.0
  - python-dateutil==2.8.2
  - pytz==2023.3
  - requests==2.31.0
  - shapely==2.0.1
  - six==1.16.0
  - tzdata==2023.3
  - urllib3==2.0.2


Les modules sont à installer via la commande 'pip install <nom_du_module>' dans le terminal de votre IDE (PyCharm, VSCode, etc...).
Les modules à installer sont également présents dans le fichier 'requirements.txt' situé à la racine du projet.

! PENSEZ À CRÉER UN ENVIRONNEMENT VIRTUEL (venv) !

/*****************************************************************************/

PARTIE GITHUB :

Afin d'installer l'application Web (React + Node.js) :

Installer Node.js et npm sur votre machine si ce n'est pas déjà fait :
    - https://nodejs.org/en
    - https://www.npmjs.com/package/npm

Rendez-vous sur le lien github suivant (afin de télécharger le projet (attention fichier très lourd ~ 1.5 GB)) :
    - https://github.com/ulrichc1/sae204

Une fois le projet téléchargé, ouvrez un nouveau terminal dans votre IDE (PyCharm, VSCode, etc...) ou PowerShell / Git Bash et exécutez la commande suivante :
    - Dans la racine du projet, exécutez la commande suivante : 'npm install --package-lock-only' puis 'npm ci ou npm install'
    - Dans le répertoire '/client', exécutez la commande suivante : 'npm install --package-lock-only' puis 'npm ci ou npm install'
    - Dans le répertoire '/server', exécutez la commande suivante : 'npm install --package-lock-only' puis 'npm ci ou npm install'

Vous devriez normalement posséder un fichier 'package-lock.json' dans la racine du projet, dans le répertoire '/client' et dans le répertoire '/server'.

Il vous suffira ensuite d'exécuter la commande suivante dans la racine du projet :
    - 'npm start'

/*****************************************************************************

Afin de pouvoir exécuter l'insertion des données dans la base de données, il vous faut créer une base de données nommée 'velibs' dans votre SGBD (MySQL) puis :
    - Vous rendre dans le répertoire './src' et ouvrir le fichier 'sql.py' (pensez à bien lire les commentaires et décommenter les lignes de code nécessaires).
    - Exécuter le programme 'sql.py' (en console) afin de créer les tables de la base de données 'velibs'.
    - Vous rendre dans le fichier 'main.py' et exécuter le programme afin d'insérer les données dans la base de données 'velibs'.

Pour faciliter la création de la base de données et la création des tables, un script .sql nommé 'velibs.sql' est également présent dans le fichier .zip.

/*****************************************************************************/

Afin de pouvoir analyser les données de la base de données velibs, il vous faut : 
    - Vous rendre dans le répertoire './src' et ouvrir le fichier 'geo.py' ou 'db_analysis.py' (pensez à bien lire les commentaires et décommenter les lignes de code nécessaires).
    - Exécuter le programme 'geo.py' ou 'db_analysis.py' (en console) afin de générer les graphiques et les cartes de la base de données 'velibs' en fonction de vos besoins.

En fonction du programme exécuté, il vous suffira juste de vous rendre dans le dossier './src/views' pour visualiser les graphiques générés, ou bien dans le dossier './choropleths' ou './maps' pour visualiser les cartes Folium générées.

/*****************************************************************************/

PARTIE GITHUB :

Afin de pouvoir utiliser le logiciel avec interface web (React + Node.js) :
    - Ouvrez un nouveau terminal dans votre IDE (PyCharm, VSCode, etc...) ou PowerShell / Git Bash et exécutez la commande suivante : 'npm start'

Normalement, vous devriez voir apparaître dans la console les liens vers le site web (en React) et le serveur back-end (en Node.js) :

    - Le serveur Node.js (back-end API) est accessible à l'adresse suivante : http://localhost:8800/
    - Le site web est accessible à l'adresse suivante : http://localhost:3000/

/*****************************************************************************/

Le répertoire '/server' contient le serveur back-end du projet (en Node.js / Nodemon / Express). (Github)
Le répertoire '/client' contient le site web front-end du projet (en React).  (Github)
Le répertoire '/choropleths' contient les cartes générées par le programme 'geo.py'.
Le répertoire '/src' contient les fichiers sources (codes, modules...) du logiciel.
Le répertoire '/src/views' contient les graphiques générés par le programme 'db_analysis.py'.
Le répertoire '/data' contient les données brutes (arrondissements, stations) du projet (fichiers .csv, .json, .geojson...).
Le répertoire '/maps' contient l'historique récent des données concernant le stock de vélos en libre-service enregistré dans toutes les stations de Vélib' Métropole ainsi que par arrondissement.

/*****************************************************************************/

Application principale : 

    Répertoire './src' :
                - main.py : programme principal permettant d'insérer les données depuis l'API open data de Vélib'Métropole dans la base de données 'velibs' (MySQL).
                - db_analysis.py : programme permettant d'analyser les données de la base de données 'velibs' (MySQL) et de générer les graphiques.
                - geo.py : programme permettant de générer les cartes (Folium) de la base de données 'velibs' (MySQL).
                - get_data.py : programme permettant de récupérer et d'extraire les données utiles depuis l'API open data de Vélib'Métropole.
                - sql.py : programme permettant de créer les tables de la base de données 'velibs' (MySQL).

/*****************************************************************************/
