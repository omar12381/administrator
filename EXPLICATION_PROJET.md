# Explication du projet User & Forest Management — Ligne par ligne

Ce document décrit les **technologies** utilisées et le **rôle de chaque partie du code** dans le backend FastAPI + PostgreSQL/PostGIS.

---

## 1. Technologies utilisées (résumé)

| Technologie | Rôle |
|-------------|------|
| **Python 3.10** | Langage du backend |
| **FastAPI** | Framework web pour créer l’API REST (routes, validation, docs auto) |
| **SQLAlchemy** | ORM pour parler à PostgreSQL (modèles, sessions, requêtes) |
| **PostgreSQL** | Base de données relationnelle |
| **PostGIS** | Extension PostgreSQL pour stocker des géométries (points, polygones, etc.) |
| **GeoAlchemy2** | Pont entre SQLAlchemy et PostGIS (type `Geometry`) |
| **Shapely** | Manipulation de géométries en Python (GeoJSON ↔ objets géométriques) |
| **Pydantic** | Validation des données entrantes/sortantes (schémas JSON) |
| **Uvicorn** | Serveur ASGI qui exécute l’application FastAPI |
| **passlib** | Hash des mots de passe (ex. pbkdf2_sha256) |
| **psycopg2** | Pilote Python pour se connecter à PostgreSQL |

---

## 2. Fichier `requirements.txt`

```
fastapi              # Framework API REST
uvicorn[standard]     # Serveur pour lancer l’app
SQLAlchemy           # ORM base de données
psycopg2-binary      # Connexion à PostgreSQL
geoalchemy2          # Types géographiques pour SQLAlchemy (PostGIS)
shapely              # Géométries en Python (conversion GeoJSON)
pydantic-settings    # Configuration via variables d’environnement (optionnel)
python-multipart     # Pour recevoir des formulaires / fichiers
passlib              # Hash de mots de passe
```

`email-validator` est requis par Pydantic quand on utilise `EmailStr` (installé via `pip install email-validator` si besoin).

---

## 3. `app/db.py` — Connexion à la base de données

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
```
- **SQLAlchemy** : bibliothèque qui permet de faire des requêtes SQL via des objets Python.
- `create_engine` : crée un « moteur » qui sait comment se connecter à PostgreSQL.
- `sessionmaker` : fabrique des **sessions** (une session = une connexion logique pour faire des requêtes).
- `declarative_base()` : base pour définir les modèles (chaque classe = une table).

```python
DATABASE_URL = "postgresql+psycopg2://forest_user:1234@localhost:5432/forest_db"
```
- **URL de connexion** au format : `pilote://utilisateur:mot_de_passe@hôte:port/nom_base`.
- `psycopg2` : pilote utilisé par SQLAlchemy pour PostgreSQL.

```python
engine = create_engine(DATABASE_URL, echo=True, future=True)
```
- `engine` : objet qui gère le pool de connexions à la base.
- `echo=True` : affiche les requêtes SQL dans la console (utile en dev).
- `future=True` : active le style « 2.0 » de SQLAlchemy.

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```
- Une **session** regroupe plusieurs opérations (ajout, lecture, commit).
- `autocommit=False` : on fait nous-mêmes `commit()`.
- `bind=engine` : toutes les sessions utilisent ce moteur.

```python
Base = declarative_base()
```
- Toutes les tables (modèles) héritent de `Base` (ex. `class User(Base)`).

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
- **Générateur** utilisé par FastAPI avec `Depends(get_db)`.
- À chaque requête, on crée une session, on la passe à la route, puis on la ferme dans `finally` pour éviter les fuites de connexions.

---

## 4. `app/models.py` — Modèles SQLAlchemy (tables)

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .db import Base
```
- **Column, Integer, String, etc.** : types de colonnes en base.
- **relationship** : lien entre tables (ex. User → Role).
- **Geometry** (GeoAlchemy2) : colonne qui stocke une géométrie PostGIS (polygone, point, etc.).
- **Base** : classe de base pour tous les modèles.

### Table `roles`

```python
class Role(Base):
    __tablename__ = "roles"
```
- Nom de la table en base : `roles`.

```python
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
```
- `id` : clé primaire, entier auto-incrémenté.
- `name` : nom du rôle (admin, agent_forestier, superviseur), unique et obligatoire.

```python
    users = relationship("User", back_populates="role")
```
- Côté Role : « un rôle a plusieurs users ». `back_populates="role"` fait le lien avec le champ `role` du modèle `User`.

### Table `users`

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    role = relationship("Role", back_populates="users")
```
- **ForeignKey("roles.id")** : clé étrangère vers la table `roles`.
- **hashed_password** : on ne stocke jamais le mot de passe en clair, seulement son hash (fait dans le routeur avec passlib).
- **relationship("Role", back_populates="users")** : chaque user a un rôle ; côté Role, la liste des users est dans `users`.

### Table `forests`

```python
class Forest(Base):
    __tablename__ = "forests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    geom = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = relationship("User")
```
- **Geometry(geometry_type="POLYGON", srid=4326)** : colonne PostGIS pour un polygone en WGS84 (coordonnées GPS).
- **created_by_id** : optionnel, référence l’utilisateur qui a créé la forêt.
- **created_by** : relation pour accéder à l’objet `User` à partir de `created_by_id`.

---

## 5. `app/schemas.py` — Schémas Pydantic (validation et sérialisation)

Pydantic sert à :
- **Valider** les données entrantes (body JSON).
- **Sérialiser** les réponses (objets Python → JSON), avec contrôle des champs (pas de mot de passe en sortie, etc.).

```python
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, EmailStr, Field
```
- **BaseModel** : base des schémas Pydantic.
- **EmailStr** : chaîne validée comme adresse e-mail (nécessite `email-validator`).
- **Field** : pour décrire un champ (obligatoire, description, etc.).

### Rôles

```python
class RoleBase(BaseModel):
    name: str = Field(..., description="admin, agent_forestier, superviseur")

class RoleCreate(RoleBase):
    pass

class RoleRead(RoleBase):
    id: int
    class Config:
        from_attributes = True
```
- **RoleBase** : champs communs (name).
- **RoleCreate** : pour la création (même chose que Base ici).
- **RoleRead** : pour la lecture ; inclut `id` ; `from_attributes = True` permet de construire le schéma à partir d’un objet SQLAlchemy (ex. `role` venant de la base).

### Utilisateurs

```python
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role_id: int

class UserCreate(UserBase):
    password: str
```
- **UserCreate** : ce que le client envoie en POST (username, email, role_id, password). Le mot de passe ne doit jamais apparaître en sortie.

```python
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    password: Optional[str] = None
```
- **UserUpdate** : pour PATCH/PUT ; tous les champs optionnels, on ne met à jour que ceux envoyés.

```python
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleRead
    class Config:
        from_attributes = True
```
- **UserRead** : réponse API ; inclut l’objet `role` (RoleRead), pas le mot de passe.

### Forêts

```python
class ForestBase(BaseModel):
    name: str
    description: Optional[str] = None
    geometry: Dict[str, Any] = Field(
        ..., description="GeoJSON Polygon ou Feature avec geometry=Polygon"
    )
```
- **geometry** : dictionnaire GeoJSON (type Polygon ou Feature). C’est ce que le front envoie et ce qu’on renvoie ; la conversion vers la colonne PostGIS se fait dans `geo_utils`.

```python
class ForestCreate(ForestBase):
    created_by_id: Optional[int] = None

class ForestRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    geometry: Dict[str, Any]
    class Config:
        from_attributes = True
```
- **ForestRead** : en sortie on veut `geometry` en GeoJSON ; comme la base stocke `geom` (Geometry), on construit à la main un `ForestRead` dans les routeurs en appelant `geometry_to_geojson(forest.geom)`.

---

## 6. `app/geo_utils.py` — Conversion GeoJSON ↔ PostGIS

```python
from typing import Dict, Any
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping
```
- **Shapely** : `shape()` construit un objet géométrique à partir d’un dict GeoJSON ; `mapping()` fait l’inverse (géométrie → dict).
- **GeoAlchemy2** : `from_shape()` convertit une géométrie Shapely en type stockable en base ; `to_shape()` lit la colonne PostGIS et renvoie une géométrie Shapely.

```python
def geojson_to_geometry(geojson: Dict[str, Any], srid: int = 4326):
    if geojson.get("type") == "Feature":
        geom_geojson = geojson["geometry"]
    else:
        geom_geojson = geojson
    shp = shape(geom_geojson)
    return from_shape(shp, srid=srid)
```
- Si le client envoie un **Feature** GeoJSON, on prend sa propriété `geometry`.
- Sinon on suppose que c’est déjà un objet **Geometry** (ex. Polygon).
- **shape(geom_geojson)** : dict → objet Shapely.
- **from_shape(shp, srid=4326)** : Shapely → type GeoAlchemy2 pour PostGIS (WGS84).

```python
def geometry_to_geojson(geom) -> Dict[str, Any]:
    shp = to_shape(geom)
    return mapping(shp)
```
- **to_shape(geom)** : colonne PostGIS → Shapely.
- **mapping(shp)** : Shapely → dict GeoJSON (pour la réponse API).



[Flutter App] 
     |
     | POST GeoJSON + nom + description (JSON)
     v
[FastAPI] 
     |
     | 1️⃣ Désérialisation JSON → Pydantic ForestCreate
     | 2️⃣ Validation des champs (nom, description, geometry)
     | 3️⃣ Conversion GeoJSON → Geometry PostGIS
     v
[PostGIS / PostgreSQL] 
     |
     | Stockage de la forêt avec Polygon
     v
[FastAPI]
     |
     | Récupère la forêt depuis PostGIS
     | Convertit Geometry → GeoJSON
     | Sérialisation → JSON
     v
[Flutter App]
     |
     | Affiche le polygone sur la map



---

## 7. `app/routers/users.py` — CRUD utilisateurs

```python
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
```
- **APIRouter** : groupe de routes monté dans `main.py` sous le préfixe `/users`.
- **Depends(get_db)** : injection de la session base de données à chaque requête.
- **CryptContext** : algorithme de hash (pbkdf2_sha256) pour les mots de passe.

```python
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
```
- Transforme le mot de passe en clair en hash stockable en base.

```python
@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
```
- **POST /** = `POST /users/` (le préfixe est ajouté dans `main.py`).
- **user_in** : body JSON validé par Pydantic selon `UserCreate`.
- **response_model=schemas.UserRead** : la réponse est convertie en JSON selon UserRead (avec `role`, sans mot de passe).

```python
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username déjà utilisé")
```
- Vérification d’unicité : si l’email ou le username existe déjà, on renvoie 400.

```python
    db_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role_id=user_in.role_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```
- Création de l’instance **User** avec le mot de passe hashé.
- **add** → **commit** : écriture en base.
- **refresh** : recharge l’objet (pour avoir l’`id` et les relations, ex. `role`) avant de le sérialiser en UserRead.

Les routes **GET /** (liste), **GET /{user_id}** (détail), **PUT /{user_id}** (mise à jour), **DELETE /{user_id}** suivent la même logique : utilisation de `db` injecté, requêtes SQLAlchemy, et pour le PUT mise à jour partielle avec `user_in.dict(exclude_unset=True)` et hash du mot de passe si fourni.

---

## 8. `app/routers/forests.py` — CRUD forêts (avec géométrie)

```python
from ..geo_utils import geojson_to_geometry, geometry_to_geojson
```
- On utilise les deux fonctions pour : entrée JSON → Geometry (écriture) et Geometry → JSON (lecture).

```python
@router.post("/", response_model=schemas.ForestRead, status_code=status.HTTP_201_CREATED)
def create_forest(forest_in: schemas.ForestCreate, db: Session = Depends(get_db)):
    geom = geojson_to_geometry(forest_in.geometry)
```
- **forest_in.geometry** : dict GeoJSON (Polygon) envoyé par le client.
- **geojson_to_geometry** : conversion pour la colonne `geom` en base.

```python
    db_forest = models.Forest(
        name=forest_in.name,
        description=forest_in.description,
        geom=geom,
        created_by_id=forest_in.created_by_id,
    )
    db.add(db_forest)
    db.commit()
    db.refresh(db_forest)

    return schemas.ForestRead(
        id=db_forest.id,
        name=db_forest.name,
        description=db_forest.description,
        geometry=geometry_to_geojson(db_forest.geom),
    )
```
- On crée la forêt avec `geom` (type PostGIS).
- En réponse, on construit **ForestRead** à la main car le champ en base s’appelle `geom` et on veut l’exposer en JSON sous le nom `geometry` via **geometry_to_geojson**.

Pour **GET /** et **GET /{forest_id}**, on fait pareil : lecture des `Forest` en base puis construction de `ForestRead` avec `geometry=geometry_to_geojson(f.geom)`.

Pour **PUT /{forest_id}** : si `geometry` est dans les données envoyées, on fait `forest.geom = geojson_to_geometry(data["geometry"])`, puis on met à jour les autres champs et on renvoie un `ForestRead` avec `geometry_to_geojson`.

---

## 9. `app/main.py` — Point d’entrée de l’API

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .db import engine, Base
from . import models  # noqa: F401
from .routers import users, forests

app = FastAPI(title="User & Forest Management API")
```
- **FastAPI()** : application principale.
- **import models** : enregistre les modèles SQLAlchemy avec `Base` pour que `create_all` connaisse les tables.
- **text** : pour exécuter du SQL brut (insert des rôles).

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- **CORS** : autorise les requêtes depuis un autre domaine (ex. Flutter Web sur un autre port). En dev `allow_origins=["*"]` est pratique ; en prod on restreint aux origines autorisées.

```python
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
```
- Au démarrage du serveur : création des tables **roles**, **users**, **forests** si elles n’existent pas (PostGIS doit être activé sur la base).

```python
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO roles (name) "
                "SELECT unnest(:names) "
                "WHERE NOT EXISTS (SELECT 1 FROM roles)"
            ),
            {"names": ["admin", "agent_forestier", "superviseur"]},
        )
```
- Insertion des trois rôles par défaut **uniquement si** la table `roles` est vide (`WHERE NOT EXISTS`).

```python
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(forests.router, prefix="/forests", tags=["forests"])
```
- Montage des routeurs : toutes les routes de `users` sont sous **/users**, celles de `forests` sous **/forests**. Les **tags** servent à grouper les routes dans la doc Swagger (**/docs**).

---

## 10. Résumé du flux

1. **Requête HTTP** (ex. `POST /users/` avec JSON) → FastAPI.
2. **Pydantic** valide le body selon le schéma (ex. `UserCreate`) et injecte **db** via `get_db()`.
3. Le **routeur** fait la logique (vérifications, création en base avec SQLAlchemy, hash du mot de passe avec passlib).
4. La **réponse** est sérialisée selon le `response_model` (ex. `UserRead`) : pas de mot de passe, objet `role` inclus.
5. Pour les **forêts**, le GeoJSON est converti en Geometry pour la base (geo_utils + GeoAlchemy2 + Shapely) et reconverti en GeoJSON en sortie.

Tu peux tester toutes les routes depuis **http://127.0.0.1:8000/docs** une fois le serveur lancé avec `python -m uvicorn app.main:app --reload`.
