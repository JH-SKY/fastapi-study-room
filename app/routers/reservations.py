from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate
from app.services.reservation_service import reservation_service
from app.repositories.reservation_repo import reservation_repo
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/reservations", tags=["Reservations"])

@router.post("/", response_model=ReservationResponse)
async def create_reservation(res_in: ReservationCreate, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    return await reservation_service.create_res(db, user.id, res_in)

@router.get("/me", response_model=list[ReservationResponse])
async def get_my_reservations(db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    return await reservation_repo.get_my_list(db, user.id)

@router.patch("/{res_id}", response_model=ReservationResponse)
async def update_reservation(res_id: int, res_in: ReservationUpdate, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    return await reservation_service.update_res(db, user.id, res_id, res_in)

@router.delete("/{res_id}")
async def cancel_reservation(res_id: int, db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    return await reservation_service.cancel_res(db, user.id, res_id)