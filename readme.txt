
================================================================================
                    USER & FOREST MANAGEMENT - README COMPLET
================================================================================
Date de génération : 23 Mars 2026
================================================================================


================================================================================
1. DESCRIPTION GENERALE DU PROJET
================================================================================

Ce projet est une application FULLSTACK de gestion des utilisateurs, des
forêts et des parcelles forestières. Il est composé de deux parties distinctes :

  a) Un BACKEND RESTful développé en Python avec FastAPI
  b) Un FRONTEND mobile/desktop développé en Flutter (Dart)

L'objectif principal est de permettre à des agents forestiers, superviseurs et
administrateurs de :
  - Gérer des comptes utilisateurs avec leurs rôles
  - Créer, visualiser, modifier et supprimer des zones forestières (polygones
    géographiques) sur une carte interactive
  - Découper chaque forêt en PARCELLES (sous-polygones) avec calcul automatique
    de surface en hectares
  - Stocker toutes les géométries en GeoJSON/WGS84 dans une base de données
    PostgreSQL avec l'extension PostGIS


================================================================================
2. ARCHITECTURE GLOBALE DU PROJET
================================================================================

d:\user_management\
│
├── app\                        --> Backend Python/FastAPI
│   ├── main.py                 --> Point d'entrée de l'API FastAPI
│   ├── db.py                   --> Connexion à la base de données PostgreSQL
│   ├── models.py               --> Modèles SQLAlchemy (tables BDD)
│   ├── schemas.py              --> Schémas Pydantic (validation des données)
│   ├── geo_utils.py            --> Utilitaires de conversion GeoJSON <-> PostGIS
│   └── routers\
│       ├── users.py            --> Endpoints CRUD pour les utilisateurs
│       ├── forests.py          --> Endpoints CRUD pour les forêts
│       └── parcelles.py        --> Endpoints CRUD pour les parcelles (NOUVEAU)
│
├── user_forest_app\            --> Frontend Flutter (Dart)
│   └── lib\
│       ├── main.dart           --> Point d'entrée Flutter, thème, routes
│       ├── config\
│       │   └── api_config.dart --> URL de base de l'API (http://localhost:8000)
│       ├── models\
│       │   ├── user.dart       --> Modèle de données User + Role (Flutter)
│       │   ├── forest.dart     --> Modèle de données Forest (Flutter)
│       │   └── parcelle.dart   --> Modèle de données Parcelle (Flutter) (NOUVEAU)
│       ├── services\
│       │   ├── user_service.dart     --> Appels HTTP vers l'API (users)
│       │   ├── forest_service.dart   --> Appels HTTP vers l'API (forests)
│       │   └── parcelle_service.dart --> Appels HTTP vers l'API (parcelles) (NOUVEAU)
│       └── screens\
│           ├── home_screen.dart            --> Écran d'accueil principal
│           ├── user_management_screen.dart --> Gestion CRUD des utilisateurs
│           ├── add_forest_screen.dart      --> Formulaire + carte pour ajouter une forêt
│           ├── forest_list_screen.dart     --> Liste des forêts enregistrées
│           ├── edit_forest_screen.dart     --> Modifier une forêt existante
│           └── parcelle_screen.dart        --> Gestion CRUD des parcelles (NOUVEAU)
│
├── requirements.txt            --> Dépendances Python du backend
├── README.md                   --> Readme sommaire du projet
├── test_cascade.py             --> Script de test suppression en cascade
├── test_parcelle.py            --> Script de test du module parcelles
└── readme.txt                  --> CE FICHIER (README complet)


================================================================================
3. BACKEND - Python / FastAPI
================================================================================

--- TECHNOLOGIE ET LIBRAIRIES ---

  - FastAPI          : Framework web Python pour créer des APIs REST rapides
  - Uvicorn          : Serveur ASGI pour exécuter l'application FastAPI
  - SQLAlchemy       : ORM (Object Relational Mapper) pour interagir avec la BDD
  - Psycopg2-binary  : Driver Python pour PostgreSQL
  - GeoAlchemy2      : Extension SQLAlchemy pour les types géographiques PostGIS
  - Shapely          : Bibliothèque pour manipuler des géométries (formes Python)
  - Pydantic         : Validation et sérialisation des données (schemas)
  - Passlib          : Hachage sécurisé des mots de passe (algorithme pbkdf2_sha256)
  - Python-multipart : Support des formulaires multipart

--- BASE DE DONNÉES ---

  - SGBD     : PostgreSQL
  - Extension: PostGIS (pour stocker et interroger des données géographiques)
  - Nom BDD  : forest_db
  - Utilisateur BDD : forest_user (mot de passe: 1234)
  - URL de connexion : postgresql+psycopg2://forest_user:1234@localhost:5432/forest_db

  Les tables créées automatiquement au démarrage sont :
    * roles     : Contient les rôles disponibles (admin, agent_forestier, superviseur)
    * users     : Contient les comptes utilisateurs
    * forests   : Contient les zones forestières avec géométrie POLYGON WGS84 (SRID 4326)
    * parcelles : Contient les parcelles associées à chaque forêt (NOUVEAU)

--- MODÈLES DE DONNÉES (models.py) ---

  [Role]
    - id   : Clé primaire entière
    - name : Nom du rôle (unique) => "admin", "agent_forestier", "superviseur"

  [User]
    - id              : Clé primaire entière
    - username        : Nom d'utilisateur (unique)
    - email           : Adresse email (unique)
    - hashed_password : Mot de passe haché (pbkdf2_sha256)
    - role_id         : Clé étrangère vers la table roles

  [Forest]
    - id             : Clé primaire entière
    - name           : Nom de la forêt
    - description    : Description optionnelle
    - geom           : Géométrie POLYGON en WGS84 (latitude/longitude, SRID=4326)
    - created_by_id  : Clé étrangère vers la table users (créateur)
    - parcelles      : Relation 1->N vers Parcelle (cascade delete)

  [Parcelle] (NOUVEAU)
    - id             : Clé primaire entière
    - forest_id      : Clé étrangère vers Forest (FK, index)
    - name           : Nom de la parcelle (ex: "P-01", "Zone Nord")
    - description    : Description optionnelle
    - geom           : Géométrie POLYGON WGS84 (SRID=4326)
    - surface_ha     : Surface approximative en hectares (calcul automatique)
    - created_by_id  : Clé étrangère vers users (optionnel)

  IMPORTANT : La suppression d'une forêt entraîne la suppression en cascade
  de toutes ses parcelles (cascade="all, delete-orphan").

--- SCHEMAS PYDANTIC (schemas.py) ---

  Ces schemas définissent le format des données échangées via l'API :

  Pour les Roles :
    - RoleCreate  : Données pour créer un rôle (name)
    - RoleRead    : Réponse de l'API (id, name)

  Pour les Users :
    - UserCreate  : Données pour créer un utilisateur (username, email, password, role_id)
    - UserUpdate  : Mise à jour partielle (tous les champs sont optionnels)
    - UserRead    : Réponse de l'API (id, username, email, role complet)

  Pour les Forests :
    - ForestCreate : Données pour créer une forêt (name, description, geometry GeoJSON)
    - ForestUpdate : Mise à jour partielle
    - ForestRead   : Réponse de l'API (id, name, description, geometry GeoJSON)

  Pour les Parcelles (NOUVEAU) :
    - ParcelleCreate : Données pour créer une parcelle
                       (forest_id, name, description?, geometry GeoJSON, created_by_id?)
    - ParcelleUpdate : Mise à jour partielle (name?, description?, geometry?)
    - ParcelleRead   : Réponse de l'API
                       (id, forest_id, name, description?, geometry GeoJSON, surface_ha?, created_by_id?)

--- UTILITAIRES GÉOGRAPHIQUES (geo_utils.py) ---

  Ce fichier contient deux fonctions de conversion :

  geojson_to_geometry(geojson, srid=4326)
    - ENTRÉE  : Un objet GeoJSON (envoyé depuis Flutter)
    - SORTIE  : Un objet Geometry compatible PostGIS (pour la BDD)
    - Accepte un GeoJSON de type "Feature" ou directement une géométrie

  geometry_to_geojson(geom)
    - ENTRÉE  : Un objet Geometry PostGIS (venant de la BDD)
    - SORTIE  : Un dictionnaire GeoJSON (renvoyé à Flutter)

  Flux de données géographiques :
    Flutter (GeoJSON) --> geojson_to_geometry --> PostGIS (BDD)
    PostGIS (BDD) --> geometry_to_geojson --> Flutter (GeoJSON)

--- CALCUL DE SURFACE DES PARCELLES ---

  Le calcul de la surface en hectares est effectué côté backend dans parcelles.py
  à l'aide de la librairie Shapely.

  Formule approximative (valide pour de petites surfaces en WGS84) :
    surface_ha = aire_en_degrés * (111320 * 111320) / 10000

  Cette valeur est stockée dans la colonne surface_ha (Float) de la table parcelles
  et renvoyée au frontend pour affichage.

  NOTE : Lors de la mise à jour d'une parcelle, le backend vérifie également que
  la nouvelle géométrie de la parcelle est bien contenue dans le polygone de la
  forêt parente (validation spatiale avec Shapely).

--- ROUTES API (Endpoints) ---

  /users/ (router: app/routers/users.py)
  ----------------------------------------
  POST   /users/          -> Créer un utilisateur
                             Corps JSON : { username, email, password, role_id }
                             Réponse : UserRead (201 Created)
                             Erreur 400 si email ou username déjà utilisé

  GET    /users/          -> Lister tous les utilisateurs
                             Réponse : Liste de UserRead (200 OK)

  GET    /users/{id}      -> Obtenir un utilisateur par ID
                             Réponse : UserRead (200 OK)
                             Erreur 404 si non trouvé

  PUT    /users/{id}      -> Mettre à jour un utilisateur (partiel)
                             Corps JSON : { username?, email?, password?, role_id? }
                             Réponse : UserRead mise à jour (200 OK)

  DELETE /users/{id}      -> Supprimer un utilisateur
                             Réponse : 204 No Content

  /forests/ (router: app/routers/forests.py)
  -------------------------------------------
  POST   /forests/        -> Créer une forêt
                             Corps JSON : { name, description?, geometry(GeoJSON), created_by_id? }
                             Réponse : ForestRead (201 Created)

  GET    /forests/        -> Lister toutes les forêts
                             Réponse : Liste de ForestRead (200 OK)

  GET    /forests/{id}    -> Obtenir une forêt par ID
                             Réponse : ForestRead (200 OK)
                             Erreur 404 si non trouvée

  PUT    /forests/{id}    -> Mettre à jour une forêt (partiel)
                             Corps JSON : { name?, description?, geometry? }
                             Réponse : ForestRead mise à jour (200 OK)

  DELETE /forests/{id}    -> Supprimer une forêt (et toutes ses parcelles)
                             Réponse : 204 No Content

  /parcelles/ (router: app/routers/parcelles.py) (NOUVEAU)
  ----------------------------------------------------------
  POST   /parcelles/               -> Créer une parcelle
                                      Corps JSON : { forest_id, name, description?,
                                                     geometry(GeoJSON), created_by_id? }
                                      Réponse : ParcelleRead (201 Created)
                                      Erreur 404 si forêt parente non trouvée
                                      Erreur 500 en cas d'erreur serveur

  GET    /parcelles/               -> Lister toutes les parcelles
                                      Réponse : Liste de ParcelleRead (200 OK)

  GET    /parcelles/{id}           -> Obtenir une parcelle par ID
                                      Réponse : ParcelleRead (200 OK)
                                      Erreur 404 si non trouvée

  GET    /parcelles/by_forest/{forest_id} -> Lister les parcelles d'une forêt
                                      Réponse : Liste de ParcelleRead (200 OK)

  PUT    /parcelles/{id}           -> Mettre à jour une parcelle (partiel)
                                      Corps JSON : { name?, description?, geometry? }
                                      Validation : la géométrie doit être contenue
                                      dans le polygone de la forêt parente
                                      Réponse : ParcelleRead mise à jour (200 OK)
                                      Erreur 400 si géométrie hors forêt parente
                                      Erreur 404 si non trouvée

  DELETE /parcelles/{id}           -> Supprimer une parcelle
                                      Réponse : 204 No Content
                                      Erreur 404 si non trouvée

--- CONFIGURATION CORS ---

  Le backend autorise TOUTES les origines ("*") en mode développement,
  ce qui permet à l'application Flutter de faire des requêtes HTTP
  depuis n'importe quel hôte sans restriction de sécurité cross-origin.


================================================================================
4. FRONTEND - Flutter / Dart
================================================================================

--- TECHNOLOGIE ET LIBRAIRIES ---

  - Flutter SDK  : Framework multiplateforme Google (mobile, web, desktop)
  - Dart SDK     : ^3.10.7
  - http ^1.2.2  : Client HTTP pour appeler l'API REST FastAPI
  - flutter_map ^7.0.2 : Widget de carte interactif (compatible Web + Mobile)
  - latlong2 ^0.9.1   : Classes de coordonnées LatLng pour flutter_map
  - cupertino_icons   : Icônes style iOS

--- CONFIGURATION API (config/api_config.dart) ---

  La base URL de l'API est définie dans une constante :
    const String apiBaseUrl = 'http://localhost:8000';

  IMPORTANT : Si le backend tourne sur une autre machine ou un autre port,
  il faut modifier cette valeur avant de builder l'application Flutter.

--- MODÈLES DE DONNÉES FLUTTER ---

  [models/user.dart]
    Classe Role  : { id, name }
    Classe User  : { id, username, email, role(Role) }
    Les deux classes disposent d'un constructeur factory fromJson()
    pour parser les réponses JSON de l'API.

  [models/forest.dart]
    Classe Forest : { id, name, description?, geometry(Map GeoJSON) }
    Dispose aussi d'un constructeur factory fromJson().

  [models/parcelle.dart] (NOUVEAU)
    Classe Parcelle : { id, forestId, name, description?, geometry(Map GeoJSON),
                        surfaceHa?, createdById? }
    Dispose d'un constructeur factory fromJson() avec conversion numérique
    sécurisée pour surfaceHa (num -> double).

--- SERVICES (Couche d'accès API) ---

  [services/user_service.dart] => Classe UserService
    - fetchUsers()        : GET /users/ -> Liste<User>
    - createUser(...)     : POST /users/ -> User
    - updateUser(...)     : PUT /users/{id} -> User
    - deleteUser(id)      : DELETE /users/{id} -> void

  [services/forest_service.dart] => Classe ForestService
    - fetchForests()      : GET /forests/ -> Liste<Forest>
    - createForest(...)   : POST /forests/ -> Forest
    - updateForest(...)   : PUT /forests/{id} -> Forest
    - deleteForest(id)    : DELETE /forests/{id} -> void

  [services/parcelle_service.dart] => Classe ParcelleService (NOUVEAU)
    - fetchParcellesByForest(forestId) : GET /parcelles/by_forest/{forestId}
                                         -> Liste<Parcelle>
    - createParcelle(...)              : POST /parcelles/ -> Parcelle
    - updateParcelle(...)              : PUT /parcelles/{id} -> Parcelle
    - deleteParcelle(id)               : DELETE /parcelles/{id} -> void

  Chaque méthode lève une Exception si le code HTTP de la réponse
  n'est pas le code attendu (200, 201, 204).

--- THÈME ET DESIGN (main.dart) ---

  L'application utilise Material Design 3 avec :
  - Couleur principale : Vert (Colors.green)
  - Fond d'écran       : #F4F5F7 (gris clair)
  - AppBar             : Surface claire, titre en gras (FontWeight.w600)
  - Cards              : Élévation 2, coins arrondis (BorderRadius 12)
  - Mode debug désactivé (debugShowCheckedModeBanner: false)

--- ROUTES FLUTTER (Navigation) ---

  '/'              -> HomeScreen           (Écran d'accueil)
  '/users'         -> UserManagementScreen (Gestion des utilisateurs)
  '/forests/add'   -> AddForestScreen      (Ajouter une forêt)
  '/forests/list'  -> ForestListScreen     (Liste des forêts)

  NOTE : ParcelleScreen est accessible via navigation directe (MaterialPageRoute)
  depuis ForestListScreen, en passant l'objet Forest en paramètre. Il n'est pas
  dans les routes nommées car il nécessite un paramètre d'objet.

--- ÉCRANS DE L'APPLICATION ---

  [home_screen.dart] - Écran d'accueil
    Affiche un titre de bienvenue et trois boutons de navigation :
    - "Gestion des utilisateurs" -> /users
    - "Ajouter une forêt"        -> /forests/add
    - "Liste des forêts"         -> /forests/list
    Le layout est responsive : en mode large (>800px), affichage en Row ;
    en mode étroit, affichage en Column.

  [user_management_screen.dart] - Gestion CRUD des utilisateurs
    - Affiche la liste de tous les utilisateurs avec leur rôle
    - Permet de créer un nouvel utilisateur via un formulaire
    - Permet de modifier un utilisateur existant
    - Permet de supprimer un utilisateur
    - Taille : 17 802 octets

  [add_forest_screen.dart] - Ajout d'une forêt
    - Formulaire pour le nom et la description
    - Carte interactive (flutter_map) pour dessiner le polygone de la forêt
    - Envoi de la géométrie au format GeoJSON vers l'API
    - Taille : 7 392 octets

  [forest_list_screen.dart] - Liste des forêts (MIS À JOUR)
    - Récupère et affiche toutes les forêts enregistrées
    - Affiche le nom et la description de chaque forêt
    - Bouton "Parcelles" (teal) => navigue vers ParcelleScreen pour cette forêt
    - Bouton "Modifier" => navigue vers EditForestScreen
    - Bouton "Supprimer" => confirmation puis suppression (avec cascade sur parcelles)
    - Pull-to-refresh et bouton rafraîchir dans l'AppBar
    - Taille : 9 502 octets

  [edit_forest_screen.dart] - Modification d'une forêt
    - Permet de modifier le nom, la description et/ou la géométrie d'une forêt
    - Affiche la carte avec le polygone actuel pré-chargé
    - Taille : 9 102 octets

  [parcelle_screen.dart] - Gestion des parcelles (NOUVEAU)
    - Reçoit en paramètre l'objet Forest parent
    - Charge et affiche les parcelles existantes de la forêt (GET /parcelles/by_forest/{id})
    - Carte interactive (flutter_map) affichant :
        * Le polygone de la forêt parente (vert, semi-transparent)
        * Les parcelles existantes (couleurs variées: bleu, orange, rouge, violet...)
        * Le polygone en cours de dessin (jaune)
        * Les points cliqués (marqueurs rouges)
    - Permet de dessiner plusieurs polygones de parcelles en cliquant sur la carte
    - Bouton "Terminer le polygone" pour valider un polygone (min. 3 points)
    - Bouton "Annuler" pour effacer le tracé en cours
    - Bouton "Effacer tout" pour réinitialiser tous les polygones dessinés
    - Formulaire de saisie du nom et description pour chaque polygone dessiné
    - Bouton "Enregistrer toutes les parcelles" pour sauvegarder en masse
    - Liste des parcelles existantes avec surface en hectares et bouton de suppression
    - Suppression avec dialog de confirmation
    - Taille : 17 493 octets


================================================================================
5. INSTALLATION ET DÉMARRAGE
================================================================================

--- PRÉREQUIS ---

  * Python 3.9+ (avec pip)
  * PostgreSQL 14+ avec l'extension PostGIS installée
  * Flutter SDK (version compatible avec Dart ^3.10.7)
  * Git (optionnel)

--- ÉTAPE 1 : Préparer la base de données PostgreSQL ---

  1. Se connecter à PostgreSQL avec un superutilisateur (ex: psql -U postgres)
  2. Exécuter les commandes SQL suivantes :

     CREATE USER forest_user WITH PASSWORD '1234';
     CREATE DATABASE forest_db OWNER forest_user;
     \c forest_db
     CREATE EXTENSION postgis;
     GRANT ALL PRIVILEGES ON DATABASE forest_db TO forest_user;

--- ÉTAPE 2 : Installer les dépendances Python ---

  Ouvrir un terminal dans le dossier du projet :

     cd d:\user_management
     pip install -r requirements.txt

--- ÉTAPE 3 : Lancer le Backend FastAPI ---

     uvicorn app.main:app --reload

  L'API sera disponible sur : http://localhost:8000
  Documentation interactive (Swagger UI) : http://localhost:8000/docs
  Documentation alternative (ReDoc)      : http://localhost:8000/redoc

  Au premier démarrage, le backend créera automatiquement les tables
  (roles, users, forests, parcelles) et insérera les 3 rôles par défaut
  (admin, agent_forestier, superviseur).

--- ÉTAPE 4 : Lancer le Frontend Flutter ---

  Ouvrir un AUTRE terminal dans le dossier Flutter :

     cd d:\user_management\user_forest_app
     flutter pub get
     flutter run

  Choisir la plateforme cible (Windows, Chrome/Web, Android, etc.)
  L'application se connectera automatiquement à http://localhost:8000

--- CONFIGURATION (si besoin) ---

  Si l'API n'est pas sur localhost:8000, modifier ce fichier :
    user_forest_app\lib\config\api_config.dart
    -> Changer la valeur de apiBaseUrl


================================================================================
6. FLUX DE DONNÉES COMPLET
================================================================================

--- Exemple : Créer une forêt ---

  1. L'utilisateur dessine un polygone sur la carte Flutter (flutter_map)
  2. Les coordonnées sont converties en GeoJSON Polygon dans le code Flutter
  3. Flutter appelle ForestService.createForest() qui envoie une requête
     HTTP POST vers http://localhost:8000/forests/ avec le corps JSON :
     {
       "name": "Forêt du Nord",
       "description": "Zone protégée",
       "geometry": {
         "type": "Polygon",
         "coordinates": [[[lng1, lat1], [lng2, lat2], ...]]
       }
     }
  4. FastAPI reçoit la requête, valide les données avec le schéma ForestCreate
  5. geo_utils.geojson_to_geometry() convertit le GeoJSON en objet PostGIS
  6. L'objet Forest est sauvegardé dans PostgreSQL/PostGIS
  7. La forêt est relue, geometry_to_geojson() reconvertit en GeoJSON
  8. FastAPI renvoie un ForestRead en JSON (201 Created) à Flutter
  9. Flutter met à jour l'interface avec la nouvelle forêt ajoutée

--- Exemple : Créer des parcelles dans une forêt (NOUVEAU) ---

  1. Depuis ForestListScreen, l'utilisateur clique sur "Parcelles" d'une forêt
  2. ParcelleScreen s'ouvre avec la forêt passée en paramètre
  3. La carte affiche le polygone de la forêt parente en vert
  4. L'utilisateur clique sur la carte pour tracer le polygon d'une parcelle
  5. Bouton "Terminer le polygone" => le polygone est ajouté à la liste
  6. L'utilisateur saisit le nom (et optionnellement la description)
  7. Il peut dessiner plusieurs parcelles supplémentaires de la même façon
  8. Bouton "Enregistrer toutes les parcelles" => pour chaque polygone nommé :
     a. Flutter appelle POST /parcelles/ avec geometry GeoJSON
     b. Le backend calcule surface_ha avec Shapely
     c. La parcelle est sauvegardée en BDD (lien forest_id)
     d. ParcelleRead est retourné à Flutter
  9. La liste des parcelles est rechargée et affichée sur la carte

--- Exemple : Suppression en cascade ---

  1. L'utilisateur supprime une forêt depuis ForestListScreen
  2. Une confirmation est demandée via AlertDialog
  3. ForestService.deleteForest(id) envoie DELETE /forests/{id}
  4. PostgreSQL supprime automatiquement toutes les parcelles associées
     (grâce au cascade="all, delete-orphan" de SQLAlchemy + contrainte FK)
  5. La liste des forêts est rechargée


================================================================================
7. SÉCURITÉ
================================================================================

  - Les mots de passe ne sont JAMAIS stockés en clair
  - Algorithme de hachage : pbkdf2_sha256 (via la librairie passlib)
  - Les emails et usernames sont uniques en base de données
  - NOTE : Il n'y a pas encore d'authentification JWT/Token implémentée.
    L'API est actuellement ouverte à tous les clients (mode développement).
    En production, il faudrait ajouter une couche d'authentification.


================================================================================
8. RÔLES ET PERMISSIONS
================================================================================

  L'application supporte 3 rôles utilisateurs :

  admin          (ID: 1) : Administrateur système
  agent_forestier (ID: 2) : Agent sur le terrain chargé des forêts
  superviseur    (ID: 3) : Superviseur qui contrôle les agents

  Ces rôles sont créés automatiquement au démarrage du backend.
  Chaque utilisateur est assigné à exactement un rôle.
  NOTE : La gestion des permissions par rôle (contrôle d'accès) n'est pas
  encore implémentée dans l'API actuelle.


================================================================================
9. DÉPENDANCES DÉTAILLÉES
================================================================================

  Backend (requirements.txt) :
  --------------------------------
  fastapi           : Framework API REST Python
  uvicorn[standard] : Serveur ASGI (avec WebSockets et performances améliorées)
  SQLAlchemy        : ORM Python pour PostgreSQL
  psycopg2-binary   : Adaptateur PostgreSQL pour Python
  geoalchemy2       : Types géographiques PostGIS pour SQLAlchemy
  shapely           : Manipulation de géométries (conversion de formes, calcul surface)
  pydantic-settings : Gestion de la configuration via variables d'environnement
  python-multipart  : Support des formulaires multipart/form-data
  passlib           : Hachage sécurisé des mots de passe

  Frontend (pubspec.yaml) :
  -------------------------
  http: ^1.2.2         : Client HTTP pour les appels REST API
  flutter_map: ^7.0.2  : Widget de carte interactive basé sur OpenStreetMap
  latlong2: ^0.9.1     : Classes LatLng pour les coordonnées géographiques
  cupertino_icons      : Pack d'icônes style Apple/iOS


================================================================================
10. STRUCTURE DES FICHIERS COMPLETS
================================================================================

  BACKEND (app/)
  --------------
  app/
  ├── __pycache__/          Fichiers Python compilés (ignorés par git)
  ├── db.py                 Connexion SQLAlchemy + session factory + Base ORM
  ├── geo_utils.py          Conversion GeoJSON <-> GeoAlchemy2 <-> Shapely
  ├── main.py               Application FastAPI + CORS + startup + routers
  ├── models.py             Entités SQLAlchemy : Role, User, Forest, Parcelle
  ├── schemas.py            Schémas Pydantic : validation et sérialisation
  └── routers/
      ├── users.py          Endpoints CRUD /users/*
      ├── forests.py        Endpoints CRUD /forests/*
      └── parcelles.py      Endpoints CRUD /parcelles/*  (NOUVEAU)

  FRONTEND (user_forest_app/lib/)
  --------------------------------
  lib/
  ├── main.dart             Entrée Flutter, thème Material3, routes de navigation
  ├── config/
  │   └── api_config.dart   Constante apiBaseUrl (URL du backend)
  ├── models/
  │   ├── user.dart         Classe Role + Classe User avec fromJson()
  │   ├── forest.dart       Classe Forest avec fromJson()
  │   └── parcelle.dart     Classe Parcelle avec fromJson()  (NOUVEAU)
  ├── services/
  │   ├── user_service.dart      CRUD HTTP utilisateurs
  │   ├── forest_service.dart    CRUD HTTP forêts
  │   └── parcelle_service.dart  CRUD HTTP parcelles  (NOUVEAU)
  └── screens/
      ├── home_screen.dart              Tableau de bord / accueil
      ├── user_management_screen.dart   Liste + CRUD complet des utilisateurs
      ├── add_forest_screen.dart        Carte + formulaire pour créer une forêt
      ├── forest_list_screen.dart       Affichage + actions sur toutes les forêts
      ├── edit_forest_screen.dart       Modification d'une forêt existante
      └── parcelle_screen.dart          Dessin + gestion des parcelles  (NOUVEAU)


================================================================================
11. POINTS IMPORTANTS À RETENIR
================================================================================

  1.  Le projet est FULLSTACK : Python (FastAPI) + Dart (Flutter)
  2.  PostgreSQL avec PostGIS est OBLIGATOIRE pour la partie géographique
  3.  Les forêts ET les parcelles sont des POLYGONES en GeoJSON / WGS84 (SRID 4326)
  4.  La conversion GeoJSON <-> PostGIS est gérée par geo_utils.py
  5.  Le CORS est ouvert (*) en développement - à sécuriser en production
  6.  Les mots de passe sont hachés avec pbkdf2_sha256
  7.  L'authentification JWT n'est pas encore implémentée
  8.  L'application Flutter est compatible Web, Android, iOS, Windows, Linux, macOS
  9.  La carte utilise OpenStreetMap via le package flutter_map
  10. L'URL de l'API est centralisée dans api_config.dart
  11. Les parcelles sont liées à une forêt (forest_id) et supprimées en cascade
  12. Le calcul de surface des parcelles est automatique (Shapely, formule approx.)
  13. La mise à jour d'une parcelle valide que sa géométrie est incluse dans la forêt
  14. ParcelleScreen permet de dessiner plusieurs parcelles avant sauvegarde en masse
  15. ForestListScreen intègre maintenant un bouton "Parcelles" par forêt (teal)


================================================================================
                              FIN DU README
================================================================================
