from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from src.config.database import get_session
from src.models.voos_model import Voo

voos_router = APIRouter(prefix="/voos")

@voos_router.get("/vendas")
def lista_voos_venda():
    LIMITE_HORAS = 2
    with get_session() as session:
        hora_limite = datetime.now() + timedelta(hours=LIMITE_HORAS)
        statement = select(Voo).where(Voo.data_saida >= hora_limite)
        voos = session.exec(statement).all()
        return voos
