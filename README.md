## User & Forest Management

Backend FastAPI + PostgreSQL/PostGIS pour la gestion des utilisateurs (avec rôles) et des forêts (polygones géographiques en GeoJSON).

### 1. Installation backend

```bash
cd d:\user_management
pip install -r requirements.txt
```

Créer la base et activer PostGIS dans PostgreSQL (adapter l'URL dans `app/db.py`) :

```sql
CREATE DATABASE forest_db;
\c forest_db;
CREATE EXTENSION postgis;
```

### 2. Lancer l'API

```bash
uvicorn app.main:app --reload
```

Endpoints principaux :

- `POST /users/`, `GET /users/`, `PUT /users/{id}`, `DELETE /users/{id}`
- `POST /forests/`, `GET /forests/`, `PUT /forests/{id}`, `DELETE /forests/{id}`

Les géométries de forêts sont échangées en **GeoJSON Polygon** entre le frontend Flutter et FastAPI.

