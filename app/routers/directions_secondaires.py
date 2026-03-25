from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.DirectionSecondaireRead, status_code=status.HTTP_201_CREATED)
def create_direction_secondaire(
    direction_in: schemas.DirectionSecondaireCreate,
    db: Session = Depends(get_db)
):
    try:
        # Verify parent direction régionale exists
        parent = db.query(models.DirectionRegionale).filter(
            models.DirectionRegionale.id == direction_in.region_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Direction régionale parente non trouvée")
        
        db_direction = models.DirectionSecondaire(
            nom=direction_in.nom,
            region_id=direction_in.region_id,
        )
        db.add(db_direction)
        db.commit()
        db.refresh(db_direction)
        return db_direction
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}"
        ) from e


@router.get("/", response_model=List[schemas.DirectionSecondaireRead])
def list_directions_secondaires(db: Session = Depends(get_db)):
    directions = db.query(models.DirectionSecondaire).all()
    return directions


@router.get("/by_region/{region_id}", response_model=List[schemas.DirectionSecondaireRead])
def get_directions_by_region(region_id: int, db: Session = Depends(get_db)):
    directions = db.query(models.DirectionSecondaire).filter(
        models.DirectionSecondaire.region_id == region_id
    ).all()
    return directions


@router.get("/{secondaire_id}", response_model=schemas.DirectionSecondaireRead)
def get_direction_secondaire(secondaire_id: int, db: Session = Depends(get_db)):
    direction = db.query(models.DirectionSecondaire).filter(models.DirectionSecondaire.id == secondaire_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction secondaire non trouvée")
    return direction


@router.put("/{secondaire_id}", response_model=schemas.DirectionSecondaireRead)
def update_direction_secondaire(
    secondaire_id: int,
    direction_in: schemas.DirectionSecondaireCreate,
    db: Session = Depends(get_db)
):
    direction = db.query(models.DirectionSecondaire).filter(models.DirectionSecondaire.id == secondaire_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction secondaire non trouvée")
    
    try:
        # Verify parent direction régionale exists
        parent = db.query(models.DirectionRegionale).filter(
            models.DirectionRegionale.id == direction_in.region_id
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Direction régionale parente non trouvée")
        
        direction.nom = direction_in.nom
        direction.region_id = direction_in.region_id
        db.commit()
        db.refresh(direction)
        return direction
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}") from e


@router.delete("/{secondaire_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_direction_secondaire(secondaire_id: int, db: Session = Depends(get_db)):
    direction = db.query(models.DirectionSecondaire).filter(models.DirectionSecondaire.id == secondaire_id).first()
    if not direction:
        raise HTTPException(status_code=404, detail="Direction secondaire non trouvée")
    
    try:
        db.delete(direction)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}") from e
