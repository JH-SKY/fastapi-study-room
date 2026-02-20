# 🚀 학습 기록 및 트러블슈팅 로그 (Learning Log)

이 파일은 프로젝트 개발 과정에서 겪은 시행착오, 에러 해결 과정, 그리고 새롭게 배운 개념들을 기록하는 공간입니다.

---

## 📅 2026-02-20: 모델 초기 설정 및 DB 연결

### 1. ⚠️ [Error] 모델 임포트 시 서버 실행 실패
- **에러 메시지**: `ImportError` 또는 `NameError: name 'Base' is not defined`
- **상황**: `app/models/__init__.py`에서 모든 모델을 한꺼번에 임포트하려 했으나 서버가 켜지지 않음.
- **원인 분석**:
    - 모든 SQLAlchemy 모델은 `Base`를 상속받아야 함.
    - 하지만 모델 파일에서 `Base`를 불러오지 않았거나, `__init__.py`에서 모델을 모으는 과정에서 의존성 주입이 누락됨.
- **해결 방법**: 
    1. `app/database.py`에 정의된 `Base`를 각 모델 파일 상단에서 정확히 임포트함.
    2. `app/models/__init__.py`에서 각 모델을 다시 호출하여 `main.py`가 모든 테이블 구조를 한 번에 인식하도록 수정.
- **성장 포인트**: 
    - `__init__.py`의 역할(패키지화)과 모델 간의 의존성 연결 구조를 확실히 이해함.
    - 에러가 났을 때 가장 아랫줄의 메시지부터 읽는 '사고 훈련'을 시작함.

### 2. ⚠️ [Error] datetime 타입 인식 불가로 인한 서버 실행 실패
- **에러 메시지**: `MappedAnnotationError: ... is not a Python type, it's the object <module 'datetime' ...>`
- **상황**: `created_at` 등 날짜 관련 필드를 모델에 추가한 후 서버를 실행했으나, SQLAlchemy가 타입을 인식하지 못함.
- **원인 분석**:
    - `Mapped[...]` 안에는 데이터를 담는 그릇의 종류(클래스/타입)를 적어야 함.
    - 하지만 `import datetime`만 작성할 경우, `datetime`은 클래스가 아닌 **모듈(파일 묶음)** 전체를 가리키게 됨.
    - SQLAlchemy는 "데이터 타입이 들어올 자리에 왜 폴더(모듈)를 통째로 넣었니?"라며 에러를 발생시킨 것임.
- **해결 방법**:
    1. 각 모델 파일 상단의 임포트 문을 `import datetime`에서 `from datetime import datetime`으로 수정함.
    2. 이를 통해 모듈 내부의 'datetime 클래스'를 직접 참조하게 하여 SQLAlchemy가 정확한 데이터 타입을 인지하도록 교정함.
- **성장 포인트**:
    - 파이썬에서 **모듈(Module)**과 **클래스(Class)**의 계층적 차이를 명확히 구분하는 법을 익힘.
    - 라이브러리 에러 발생 시, 단순히 코드를 고치는 게 아니라 "이 도구가 왜 이 데이터를 거부하는가"라는 관점에서 명칭과 타입을 대조하는 습관을 기름.

## 📅 2026-02-20: 회원가입 로직 추가 

### 3. ⚠️ [Error] SQLAlchemy 모델 간 순환 참조 발생
- **에러 메시지**: `sqlalchemy.exc.InvalidRequestError: ... failed to locate a name ('Reservation')`
- **상황**: `User` 모델과 `Reservation` 모델이 서로를 참조하고 있어 SQLAlchemy가 전체 구조를 파악하지 못함.
- **원인 분석**:
    - 파이썬은 위에서 아래로 읽는데, `User`가 정의될 때 아직 존재하지 않는 `Reservation` 클래스를 호출해서 발생함.
- **해결 방법**: 
    - `relationship`의 첫 번째 인자를 클래스 객체가 아닌 문자열(`"Reservation"`)로 수정하여 지연 로딩을 유도함.
- **성장 포인트**: 
    - ORM에서 모델 간의 관계(Relationship)를 설정할 때 순환 참조를 피하는 표준적인 방법을 익힘.

---

### 4. ⚠️ [Error] bcrypt 비밀번호 길이 제한 초과
- **에러 메시지**: `ValueError: password cannot be longer than 72 bytes`
- **상황**: 테스트 중 긴 비밀번호를 입력했을 때 서버가 즉시 종료됨.
- **원인 분석**:
    - `bcrypt` 알고리즘 설계상 최대 입력값이 72바이트로 고정되어 있음.
- **해결 방법**: 
    - `Pydantic` 스키마(`UserCreate`)에서 `password` 필드에 `max_length=50`을 설정하여 서버 로직에 도달하기 전 입구에서 차단함.
- **성장 포인트**: 
    - 보안 라이브러리의 물리적 한계를 인지하고, 유효성 검사(Validation)의 중요성을 체감함.

---

### 5. ⚠️ [Error] DB 무한 대기 (Deadlock) 및 응답 없음
- **에러 메시지**: 에러 메시지 없이 Swagger/Postman이 무한 로딩됨.
- **상황**: `with db.begin()` 트랜잭션 블록 안에서 `db.refresh()`를 실행함.
- **원인 분석**:
    - 아직 Commit(확정)되지 않은 데이터를 읽으려 시도(Refresh)하면서 DB 세션이 스스로를 기다리는 교착 상태에 빠짐.
- **해결 방법**: 
    - `db.refresh()`를 `commit()`이후에 하게끔 레포에는 `db.flush()` 으로 수정하고 `refresh`는 서비스단계에서 실행
- **성장 포인트**: 
    - DB 트랜잭션의 생명주기(Life-cycle)와 `flush`, `commit`, `refresh`의 각기 다른 역할을 명확히 구분함.

---

### 6. ⚠️ [Error] 라이브러리 속성 참조 오류 (bcrypt)
- **에러 메시지**: `AttributeError: type object 'bcrypt' has no attribute 'gensalt'`
- **상황**: 비밀번호 해싱 과정에서 `gensalt()` 함수를 찾지 못함.
- **원인 분석**:
    - `from passlib.hash import bcrypt`를 사용함. 이는 래핑된 도구라 원본 `bcrypt`의 세부 함수(`gensalt`)가 포함되어 있지 않음.
- **해결 방법**: 
    - `import bcrypt`를 통해 순수 라이브러리를 직접 임포트하여 해결.
- **성장 포인트**: 
    - 동일한 이름의 라이브러리라도 임포트 경로에 따라 제공하는 기능이 다를 수 있음을 배움.

---

### 7. ⚠️ [Error] 모델-레포지토리 인자 불일치
- **에러 메시지**: `TypeError: 'hashed_password' is an invalid keyword argument for User`
- **상황**: 레포지토리에서 `User` 객체를 생성하여 DB에 넣으려 할 때 발생.
- **원인 분석**:
    - `models/user.py`에는 `password`라는 이름으로 컬럼이 정의되어 있는데, 레포지토리에서는 `hashed_password`라는 이름으로 값을 전달함.
- **해결 방법**: 
    - 모델의 정의서와 일치하도록 레포지토리의 인자명을 `password=hashed_password`로 수정함.
- **성장 포인트**: 
    - DB 모델(Schema)과 실제 코드 상의 변수 매핑 과정에서 꼼꼼한 이름 확인이 필수적임을 깨달음.

