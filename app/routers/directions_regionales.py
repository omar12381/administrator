from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.DirectionRegionaleRead, status_code=status.HTTP_201_CREATED)
def create_direction_regionale(
    direction_in: schemas.DirectionRegionaleCreate,
    db: Session = Depends(get_db)
):
    try:
        db_direction = models.DirectionRegionale(
            nom=direction_in.nom,
            gouvernorat=direction_in.gouvernorat,
        )
        db.add(db_direction)
        db.commit()
        db.refresh(db_direction)
        return db_direction
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}"
        ) from e


@router.get("/", response_model=List[schemas.DirectionRegionaleRead])
def list_directions_regionales(db: Session = Depends(get_db)):
    directions = db.query(models.DirectionRegionale).all()
    return directions


@router.get("/{region_id}", response_model=schemas.DirectionRegionaleRead)
def get_direction_regionale(region_id: int, db: Session = Depends(get_db)):
    direction = db.query(models.DirectionRegionale).filter(models.DirectionRegionale.id == region_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction régionale non trouvée")
    return direction


@router.put("/{region_id}", response_model=schemas.DirectionRegionaleRead)
def update_direction_regionale(
    region_id: int,
    direction_in: schemas.DirectionRegionaleCreate,
    db: Session = Depends(get_db)
):
    direction = db.query(models.DirectionRegionale).filter(models.DirectionRegionale.id == region_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction régionale non trouvée")
    
    try:
        direction.nom = direction_in.nom
        direction.gouvernorat = direction_in.gouvernorat
        db.commit()
        db.refresh(direction)
        return direction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}") from e


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_direction_regionale(region_id: int, db: Session = Depends(get_db)):
    direction = db.query(models.DirectionRegionale).filter(models.DirectionRegionale.id == region_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction régionale non trouvée")
    
    try:
        db.delete(direction)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}") from e
