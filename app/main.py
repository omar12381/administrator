from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .db import engine, Base
from . import models  # noqa: F401
from .routers import users, forests, parcelles, roles
from .routers import directions_regionales, directions_secondaires


app = FastAPI(title="User & Forest Management API")

app.add_middleware(
    CORSMiddleware,
    # En dev, on autorise toutes les origines pour simplifier
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Crée les tables si elles n'existent pas encore
    Base.metadata.create_all(bind=engine)
    # Initialise quelques rôles par défaut
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO roles (name) "
                "SELECT unnest(:names) "
                "WHERE NOT EXISTS (SELECT 1 FROM roles)"
            ),
            {"names": ["admin", "agent_forestier", "superviseur"]},
        )

        # Évolutions de schéma ponctuelles si la base est plus ancienne
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS direction_secondaire_id INTEGER REFERENCES direction_secondaire(id),"
                " ADD COLUMN IF NOT EXISTS telephone VARCHAR(50),"
                " ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT TRUE"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE forests ADD COLUMN IF NOT EXISTS direction_secondaire_id INTEGER REFERENCES direction_secondaire(id)"
            )
        )

        # Spatial indexes (PostGIS geometry).
        # These improve performance for ST_Intersects/ST_Contains/ST_Disjoint queries.
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_forests_geom ON forests USING GIST (geom)"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_parcelles_geom ON parcelles USING GIST (geom)"
            )
        )


app.include_router(roles.router, prefix="/roles", tags=["roles"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(forests.router, prefix="/forests", tags=["forests"])
app.include_router(parcelles.router, prefix="/parcelles", tags=["parcelles"])
app.include_router(directions_regionales.router, prefix="/directions-regionales", tags=["directions"])
app.include_router(directions_secondaires.router, prefix="/directions-secondaires", tags=["directions"])

