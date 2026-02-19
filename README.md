# 🏫 스터디룸 예약 시스템 (Study-Room-Reservation)

> **청년취업사관학교 도봉캠퍼스 AI 서비스 개발자 과정** > 실무 관점의 데이터 설계와 검증 로직 구현을 위한 미니 프로젝트입니다.

---

## 1. 📂 프로젝트 구조 (Repository Structure)

* **study-room-reservation/** (최상위 루트)
    * `.gitignore`
    * `README.md`
    * `uv.lock`
    * `.env` : **[v1.1 추가] PostgreSQL 접속 정보 관리**
    * **app/**
        * **models/** : [DB 설계도] 테이블 정의 (SQLAlchemy 2.0)
            * `__init__.py` : **[v1.1 추가] 모든 모델 통합 관리**
            * `user.py`, `room.py`, `reservation.py`
            * `review.py` : **[v1.1 추가] 이용 후기 테이블**
        * **schemas/** : [데이터 규격] Pydantic 모델 (Request/Response)
        * **services/** : [핵심 로직] 비즈니스 규칙 및 검증
        * **repositories/** : [창고 관리] DB CRUD 직접 수행
        * **routers/** : [안내 데스크] API 엔드포인트
        * **docs/** : [프로젝트 문서화] 설계 및 자료 관리
            * **images/** : **ERD v1.1 (Review 추가본)**
            * **api/** : Postman API 컬렉션 등
        * `database.py` : **[v1.1 수정] PostgreSQL 엔진 설정 예정**
        * `main.py` : **[v1.1 수정] 테이블 자동 생성 로직 예정**

---

## 2. 🎯 기획 의도 (Why)

### 2.1 개발 배경
* 학생들이 스터디룸을 예약할 때 발생하는 **중복 예약 문제**와 **무분별한 독점**을 막기 위해 체계적인 예약 시스템이 필요했습니다.

### 2.2 해결하고자 하는 문제
* **중복 예약 방지**: 동일 시간대, 동일 강의실에 대한 중복 예약을 원천 차단합니다.
* **공정한 이용**: 하루 최대 이용 시간을 제한하여 특정 사용자의 독점을 방지합니다.
* **데이터 무결성**: 과거 날짜 예약 금지, 운영 시간 외 예약 금지 등 실무적인 검증 로직을 구현합니다.
* **[v1.1 추가] 서비스 신뢰도 확보**: 실제 이용자만 작성 가능한 리뷰 시스템을 통해 공간 관리를 최적화합니다.

---

## 3. 🏗️ 설계 및 구조 (Architecture)

### 3.1 Layered Architecture
* **Router → Service → Repository → Model**로 이어지는 4계층 구조를 채택했습니다.
* **이유**: API 경로(Router)와 실제 비즈니스 규칙(Service)을 분리하여 유지보수성을 높였습니다.

### 3.2 ERD 설계 (v1.1 최신화)
* **주요 엔티티**: User, StudyRoom, Reservation, Review
* **특이사항**: `Review` 테이블이 `Reservation`의 ID를 참조하도록 설계하여 "예약 완료자만 리뷰 가능"한 로직의 근거를 마련했습니다.

---

## 4. 🛠️ 핵심 로직 및 기술 선택 이유 (Core Logic)

* **PostgreSQL [v1.1 확정]**: 실무 환경과 유사한 관계형 데이터베이스 운영을 위해 채택했습니다.
* **SQLAlchemy 2.0**: `Mapped`와 `mapped_column` 방식을 사용하여 타입 안정성을 높였습니다.
* **TYPE_CHECKING**: 모델 간 순환 참조(Circular Import) 문제를 방지하기 위해 도입했습니다.
* **Pydantic**: 입출력 데이터의 규격을 엄격하게 제한합니다.
* **bcrypt & PyJWT**: 사용자 인증 및 보안을 구현할 예정입니다.

---

## 5. 🚀 성장 포인트 (Retrospective)

* **[v1.1] 순환 참조 해결**: `TYPE_CHECKING`을 통해 클래스 간 상호 참조 에러를 해결하는 실무적인 방법을 익혔습니다.
* **[v1.1] DB 모델링**: 정규화와 조회 성능 사이의 균형을 맞추기 위해 Review 테이블에 관계 설정을 최적화했습니다.

---

## 6. 📝 업데이트 기록 (Changelog)

* **v1.0**: 프로젝트 초기 아키텍처 설계 및 환경 세팅 완료 (2026-02-19)
* **v1.1**: **4개 핵심 모델(User, Room, Reservation, Review) 구축 및 PostgreSQL 환경 설정** (2026-02-19)