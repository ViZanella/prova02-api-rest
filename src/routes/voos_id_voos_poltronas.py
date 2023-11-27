from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.config.database import get_session
from src.models.voos_model import Voo
from src.models.reservas_model import Reserva

voos_router = APIRouter(prefix="/voos")

@voos_router.get("/{voo_id}/poltronas")
def lista_poltronas(voo_id: int):
    with get_session() as session:
        voo = session.get(Voo, voo_id)
        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo{voo_id} não localizado."
            )

        statement = select(Reserva).where(Reserva.voo_id == voo_id)
        reservas = session.exec(statement).all()

        poltronas_status = {}

        for i in range(1, 10):  
            poltrona_field = f"poltrona_{i}"
            poltrona_value = getattr(voo, poltrona_field)

            if poltrona_value is None:
    
                poltronas_status[poltrona_field] = {"status": "livre"}
            else:
            
                poltronas_status[poltrona_field] = {"status": "ocupada", "numero_reserva": poltrona_value}

        return poltronas_status


