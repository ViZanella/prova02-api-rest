from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select
from src.config.database import get_session
from src.models.voos_model import Voo

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
    LIMITE_HORAS = 3
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
                detail=f"Voo {voo_id} não localizado."
            )

        poltronas = {
            "poltrona_1": voo.poltrona_1,
            "poltrona_2": voo.poltrona_2,
        }

        return poltronas

@voos_router.get("")
def lista_voos():
    with get_session() as session:
        statement = select(Voo)
        voos = session.exec(statement).all()
        return voos
