from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")

@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def faz_checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
       
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()

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

        setattr(voo, poltrona_field, codigo_reserva)
        session.commit()

        return {"message": f"Seu check-in foi realizado com sucesso na poltrona {num_poltrona}."}
