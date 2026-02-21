from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.repositories.review_repo import review_repo
from app.repositories.reservation_repo import reservation_repo
from app.models.review import Review

class ReviewService:
    async def create_review(self, db, user_id, review_in):
        # 1. 예약 존재 및 본인 확인
        res = await reservation_repo.get_by_id(db, review_in.reservation_id)
        if not res or res.user_id != user_id:
            raise HTTPException(status_code=403, detail="본인의 이용 완료된 예약에 대해서만 리뷰를 남길 수 있습니다.")

        # 2. 상태 확인 (취소된 예약 불가)
        if res.status == "CANCELLED":
            raise HTTPException(status_code=400, detail="취소된 예약에는 리뷰를 작성할 수 없습니다.")

        # 3. 중복 작성 방지
        existing_review = await review_repo.get_by_reservation_id(db, review_in.reservation_id)
        if existing_review:
            raise HTTPException(status_code=400, detail="이미 이 예약에 대한 리뷰를 작성하셨습니다.")

        # 4. 이용 완료 확인 및 7일 기간 제한
        now = datetime.now()
        # 예약 종료 시간 계산 (reservation_date + end_time)
        res_end_time = datetime.combine(res.reservation_date, datetime.min.time()) + timedelta(hours=res.end_time)
        
        if now < res_end_time:
            raise HTTPException(status_code=400, detail="이용이 완료된 후에 리뷰를 작성할 수 있습니다.")
        
        if now > res_end_time + timedelta(days=7):
            raise HTTPException(status_code=400, detail="이용 완료 후 7일 이내에만 리뷰 작성이 가능합니다.")

        # 리뷰 생성
        new_review = Review(
            user_id=user_id,
            room_id=res.room_id,
            reservation_id=res.id,
            rating=review_in.rating,
            content=review_in.content
        )
        
        saved_review = await review_repo.save(db, new_review)
        await db.commit()
        await db.refresh(saved_review)
        return saved_review

    async def delete_review(self, db, user_id, review_id):
        review = await review_repo.get_by_id(db, review_id)
        if not review or review.user_id != user_id:
            raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없거나 삭제 권한이 없습니다.")
        
        await review_repo.delete(db, review)
        await db.commit()
        return {"message": "리뷰가 삭제되었습니다."}

review_service = ReviewService()