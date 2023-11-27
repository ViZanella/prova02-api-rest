from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import random 
from sqlmodel import select
from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")

@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        existing_reservation = session.exec(
            select(Reserva).where(Reserva.documento == reserva.documento)
        ).first()

        if existing_reservation:
            raise HTTPException(
                status_code=400,
                detail="O docuemnto informado já possui reserva vinculada ao mesmo."
            )


        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo {reserva.voo_id} não localizado."},
                status_code=404,
            )

        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        

        return JSONResponse(content=reserva.dict(), status_code=201) 
