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
                detail="localizada uma reserva para o mesmo documento."
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
    
@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
       
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()

        if not reserva:
            raise HTTPException(
                status_code=404,
                detail="Reserva não localizada"
            )

        voo = session.get(Voo, reserva.voo_id)

        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo {reserva.voo_id} não localizado."
            )
            
        poltrona_field = f"poltrona_{num_poltrona}"
        if getattr(voo, poltrona_field) is not None:
            raise HTTPException(
                status_code=403,
                detail="Esta poltrona está ocupada"
            )

        setattr(voo, poltrona_field, codigo_reserva)
        session.commit()

        return {"message": f"Seu check-in foi realizado com sucesso na poltrona {num_poltrona}."}

@reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(id_reserva: int, num_poltrona: int):
    with get_session() as session:
        reserva = session.get(Reserva, id_reserva)

        if not reserva:
            raise HTTPException(
                status_code=404,
                detail="Sua reserva não foi encontrada"
            )

        voo = session.get(Voo, reserva.voo_id)

        if not voo:
            raise HTTPException(
                status_code=404,
                detail=f"Voo {reserva.voo_id} não localizado."
            )

        poltrona_field = f"poltrona_{num_poltrona}"
        if getattr(voo, poltrona_field) is not None:
            raise HTTPException(
                status_code=403,
                detail="Esta poltrona está ocupada"
            )

        setattr(voo, poltrona_field, reserva.codigo_reserva)
        session.commit()

        return {"message": f"Seu check-in foi realizado com sucesso na poltrona {num_poltrona}."}
