from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
import uuid

from app.dependencies import get_db, get_current_user, require_admin
from app.layer5_domain.entities.user import User
from app.layer6_data.models.client_model import ClientModel

router = APIRouter(prefix="/clients", tags=["Clients"])


class ClientCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    status: Optional[str] = None


class ClientRead(BaseModel):
    id: str
    name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    status: str
    job_count: Optional[int] = 0

    class Config:
        from_attributes = True


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User must belong to a company")

    client = ClientModel(
        id=str(uuid.uuid4()),
        company_id=current_user.company_id,
        name=payload.name,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
    )
    db.add(client)
    await db.flush()
    return {"id": client.id, "name": client.name, "status": client.status, "contact_name": client.contact_name, "contact_email": client.contact_email, "contact_phone": client.contact_phone}


@router.get("", response_model=List[ClientRead])
async def list_clients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.company_id:
        return []
    result = await db.execute(
        select(ClientModel)
        .where(ClientModel.company_id == current_user.company_id)
        .where(ClientModel.status == "active")
        .order_by(ClientModel.created_at.desc())
    )
    clients = result.scalars().all()
    return [
        ClientRead(id=c.id, name=c.name, contact_name=c.contact_name,
                   contact_email=c.contact_email, contact_phone=c.contact_phone,
                   status=c.status)
        for c in clients
    ]


@router.get("/{client_id}")
async def get_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalar_one_or_none()
    if not client or client.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"id": client.id, "name": client.name, "contact_name": client.contact_name,
            "contact_email": client.contact_email, "contact_phone": client.contact_phone,
            "status": client.status}


@router.patch("/{client_id}")
async def update_client(
    client_id: str,
    payload: ClientUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalar_one_or_none()
    if not client or client.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Client not found")

    if payload.name is not None:
        client.name = payload.name
    if payload.contact_name is not None:
        client.contact_name = payload.contact_name
    if payload.contact_email is not None:
        client.contact_email = payload.contact_email
    if payload.contact_phone is not None:
        client.contact_phone = payload.contact_phone
    if payload.status is not None:
        client.status = payload.status

    await db.flush()
    return {"id": client.id, "name": client.name, "status": client.status}
