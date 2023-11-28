from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select
from src.config.database import get_session
from src.models.voos_model import Voo
from src.models.reservas_model import Reserva

voos_router = APIRouter(prefix="/voos")

@voos_router.post("")
def cria_voo(voo: Voo):
    with get_session() as session:
        LIMITE_HORAS = 5
        hora_atual = datetime.now()
        hora_limite = hora_atual + timedelta(hours=LIMITE_HORAS)
        no_horario_limite = voo.data_saida <= hora_limite

        if no_horario_limite:
            raise HTTPException(
                status_code=403,
                detail=f"Nao permitida a inclusao de voos {LIMITE_HORAS} horas antes de este sair"
            )

        session.add(voo)
        session.commit()
        session.refresh(voo)
        return voo

@voos_router.get("/vendas")
def lista_voos_venda():
    LIMITE_HORAS = 2
    with get_session() as session:
        hora_limite = datetime.now() + timedelta(hours=LIMITE_HORAS)
        statement = select(Voo).where(Voo.data_saida >= hora_limite)
        voo = session.exec(statement).all()
        return voo

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



