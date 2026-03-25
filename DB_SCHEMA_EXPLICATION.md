# Schéma de la base de données et relations

Ce document décrit les tables, les champs et les relations dans le backend FastAPI (SQLAlchemy) du projet.

## 1) `roles` (table `Role`)
- id (PK)
- name (String, unique) : `admin`, `agent_forestier`, `superviseur` etc.

Relations :
- 1 role -> N users (relation `Role.users`)

## 2) `users` (table `User`)
- id (PK)
- username (unique)
- email (unique)
- hashed_password
- role_id (FK vers `roles.id`)
- direction_secondaire_id (FK vers `direction_secondaire.id`, nullable)
- telephone
- actif (bool)

Relations :
- `role` : Many-to-one vers `Role` (back_populates `users`)
- `direction_secondaire` : Many-to-one vers `DirectionSecondaire` (back_populates `superviseurs`)

## 3) `direction_regionale` (table `DirectionRegionale`)
- id (PK)
- nom (unique)
- gouvernorat

Relations :
- 1 direction_regionale -> N directions_secondaires (back_populates `direction_regionale`)

## 4) `direction_secondaire` (table `DirectionSecondaire`)
- id (PK)
- nom
- region_id (FK vers `direction_regionale.id`)

Relations :
- `direction_regionale` : Many-to-one vers `DirectionRegionale`
- `superviseurs` : 1 direction_secondaire -> N users (back_populates `direction_secondaire`)
- `forests` : 1 direction_secondaire -> N forests (back_populates `direction_secondaire`)

## 5) `forests` (table `Forest`)
- id (PK)
- name
- description
- geom (Geometry POLYGON SRID=4326)
- created_by_id (FK vers `users.id`)
- direction_secondaire_id (FK vers `direction_secondaire.id`)
- surface_ha
- type_foret

Relations :
- `direction_secondaire` : Many-to-one vers `DirectionSecondaire` (back_populates `forests`)
- `parcelles` : 1 forêt -> N parcelles (back_populates `forest`, cascade `all, delete-orphan`)
- `created_by` : Many-to-one vers `User` (simple relation, pas de back_populates)

## 6) `parcelles` (table `Parcelle`)
- id (PK)
- forest_id (FK vers `forests.id`)
- name
- description
- geom (Geometry POLYGON SRID=4326)
- surface_ha
- created_by_id (FK vers `users.id`)

Relations :
- `forest` : Many-to-one vers `Forest` (back_populates `parcelles`)

## Détails spécifiques géo-spatiaux
- `Forest.geom` et `Parcelle.geom` sont des POLYGONs PostGIS (GeoAlchemy2).
- Les conversions GeoJSON <-> ST_GeomFromText sont gérées dans `app/geo_utils.py`.

## Flux relationnels clé
1. rôles -> utilisateurs : un utilisateur a un rôle, un rôle a plusieurs utilisateurs.
2. direction_regionale -> direction_secondaire -> forest -> parcelle
   - Une région contient des directions secondaires.
   - Une direction secondaire contient des forêts et des superviseurs (utilisateurs).
   - Une forêt contient des parcelles.
   - Les parcelles et forêts possèdent une géométrie spatiale.
3. supervision : `User.direction_secondaire_id` identifie le secteur supervisé (optionnel) pour les agents.

## Routers API (correspondance)
- `app/routers/roles.py` -> CRUD rôle
- `app/routers/users.py` -> CRUD utilisateur
- `app/routers/directions_regionales.py` -> CRUD directions régionales
- `app/routers/directions_secondaires.py` -> CRUD directions secondaires
- `app/routers/forests.py` -> CRUD forêts
- `app/routers/parcelles.py` -> CRUD parcelles

## Usage recommandé
- Création d’un forest, puis ajout de parcelles à cette forêt.
- Création d’une direction régionale -> directions secondaires -> assignation de superviseurs.
- Assignation de rôle à utilisateur (`admin`, `agent_forestier`, `superviseur`) et lien possible sur `direction_secondaire`.

---

> Note : ce document synthétise la structure actuelle découverte dans `app/models.py`. Si tu veux un script SQL DDL complet, je peux l’ajouter sur demande.
