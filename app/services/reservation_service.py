from datetime import datetime, timedelta
from fastapi import HTTPException
from app.repositories.reservation_repo import reservation_repo
from app.models.reservation import Reservation

class ReservationService:
    async def create_res(self, db, user_id, res_in):
        # 1. 비즈니스 규칙 검증
        self._validate_reservation_rules(res_in.reservation_date, res_in.start_time, res_in.end_time)

        # 2. 중복 체크 (방/유저)
        if await reservation_repo.find_overlap(db, res_in.reservation_date, res_in.start_time, res_in.end_time, room_id=res_in.room_id):
            raise HTTPException(status_code=400, detail="해당 방의 해당 시간대는 이미 예약되었습니다.")
        
        if await reservation_repo.find_overlap(db, res_in.reservation_date, res_in.start_time, res_in.end_time, user_id=user_id):
            raise HTTPException(status_code=400, detail="해당 시간대에 이미 다른 예약이 존재합니다.")

        # 3. 객체 생성 및 저장
        new_res = Reservation(**res_in.model_dump(), user_id=user_id)
        saved_res = await reservation_repo.save(db, new_res)
        
        # 4. 명시적 저장 확정
        await db.commit()
        await db.refresh(saved_res)
        return saved_res

    async def cancel_res(self, db, user_id, res_id):
        # 1. 예약 존재 여부 및 본인 확인
        res = await reservation_repo.get_by_id(db, res_id)
        if not res or res.user_id != user_id:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")
        
        # 2. 취소 가능 시간 확인 (규칙 4)
        self._check_modification_limit(res.reservation_date, res.start_time)

        # 3. 상태 변경 및 취소 시간 기록
        res.status = "CANCELLED"
        res.canceled_at = datetime.now()
        
        await db.commit() # 변경 사항 반영
        return {"message": "정상적으로 취소되었습니다."}

    async def update_res(self, db, user_id, res_id, res_in):
        # 1. 조회 (레포지토리 이용)
        res = await reservation_repo.get_by_id(db, res_id)
        if not res or res.user_id != user_id:
            raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

        self._check_modification_limit(res.reservation_date, res.start_time)
        
        update_data = res_in.model_dump(exclude_unset=True)
        
        # 2. 비즈니스 로직 판단 (중복 체크 등)
        if any(k in update_data for k in ["start_time", "end_time", "reservation_date"]):
            new_date = update_data.get("reservation_date", res.reservation_date)
            new_start = update_data.get("start_time", res.start_time)
            new_end = update_data.get("end_time", res.end_time)
            
            self._validate_reservation_rules(new_date, new_start, new_end)

            overlap = await reservation_repo.find_overlap(
                db, new_date, new_start, new_end, 
                room_id=res.room_id, exclude_id=res_id
            )
            if overlap:
                raise HTTPException(status_code=400, detail="해당 시간대에 이미 예약이 있습니다.")

        # 3. [변경포인트] 실제 수정 행위는 레포지토리에 위임!
        updated_res = await reservation_repo.update(db, res, update_data)
        
        # 4. 트랜잭션 확정
        await db.commit()
        await db.refresh(updated_res)
        return updated_res

    def _validate_reservation_rules(self, res_date, start, end):
        now = datetime.now()
        if res_date < now.date():
            raise HTTPException(status_code=400, detail="과거 날짜는 예약할 수 없습니다.")
        if res_date == now.date() and start <= now.hour:
            raise HTTPException(status_code=400, detail="현재 시간 이후로만 예약이 가능합니다.")

    def _check_modification_limit(self, res_date, start_time):
        now = datetime.now()
        if res_date == now.date() and now.hour >= (start_time - 1):
            raise HTTPException(status_code=400, detail="이용 시작 1시간 전부터는 취소/변경이 불가능합니다.")

reservation_service = ReservationService()