# Installation

## 요구 환경

- Python 3.11 이상
- Poetry
- Node.js 및 npm
- FastAPI 백엔드 실행 포트: `http://localhost:8000`
- Vite React 프론트엔드 실행 포트: `http://localhost:3000`
- Supabase 프로젝트
- 외부 API 키
  - OpenAI API key
  - 응급의료포털/ERMCT service key
  - Tmap app key
  - Kakao REST API key
  - Kakao JavaScript map key

## 백엔드 설치 및 실행

레포 루트에서 실행합니다.

```powershell
poetry install
Copy-Item .env.example .env
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

이 프로젝트에서는 Python 명령을 직접 실행하지 말고 Poetry 환경을 사용합니다.

```powershell
poetry run python -m unittest discover -s tests -v
poetry run python -m py_compile app/main.py app/ktas_engine.py app/stt_cleaner.py
```

## 프론트엔드 설치 및 실행

```powershell
cd front
npm.cmd install
Copy-Item .env.example .env
npm.cmd run dev -- --host 127.0.0.1 --port 3000
```

프론트엔드 빌드 확인:

```powershell
cd front
npm.cmd run build
```

## 환경변수 설정

루트 `.env.example` 기준:

```dotenv
OPENAI_API_KEY=your_openai_api_key
ERMCT_SERVICE_KEY=your_ermct_service_key
TMAP_APP_KEY=your_backend_tmap_key
KAKAO_REST_API_KEY=your_kakao_rest_key
VITE_TMAP_API_KEY=your_tmap_key
VITE_KAKAO_MAP_KEY=your_kakao_js_key
```

설명:

- `OPENAI_API_KEY`: SBAR JSON 추출, KTAS RAG 분류, embedding 생성에 사용합니다.
- `ERMCT_SERVICE_KEY`: 응급의료기관 기본정보, 실시간 병상, 중증질환 수용 가능 정보 조회에 사용합니다.
- `TMAP_APP_KEY`: 백엔드에서 거리/ETA 및 경로 좌표를 조회할 때 사용합니다.
- `KAKAO_REST_API_KEY`: 위도/경도에서 현재 시군구를 역지오코딩할 때 사용합니다.
- `VITE_TMAP_API_KEY`: 프론트엔드 지도/경로 기능에서 사용할 Tmap 키입니다.
- `VITE_KAKAO_MAP_KEY`: 프론트엔드 Kakao 지도 SDK용 JavaScript 키입니다.

프론트엔드 `front/.env.example` 기준:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_DEMO_AUTH=false
VITE_TMAP_API_KEY=your_tmap_key
VITE_KAKAO_MAP_KEY=your_kakao_js_key
```

`VITE_DEMO_AUTH=true`는 시연용 데모 로그인 흐름에서만 사용합니다. 실제 Supabase Auth 흐름을 확인하려면 `VITE_DEMO_AUTH=false`로 설정합니다.

프론트엔드 Supabase 클라이언트는 `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`도 사용할 수 있습니다. 실제 배포에서는 공개 anon key만 프론트엔드에 넣고, service role key는 절대 프론트엔드, README, Wiki, 브라우저 코드에 포함하지 않습니다.

## KTAS RAG 인덱스 준비

`rag_based` KTAS를 사용하려면 guideline vector index가 필요합니다. 프로젝트에는 `scripts/build_ktas_rag_index.py`와 `data/ktas_guideline_index.json` 구조가 있습니다.

```powershell
poetry run python scripts/build_ktas_rag_index.py
```

인덱스가 없거나 로드에 실패하면 `rag_based` 요청은 백엔드 내부에서 `rule_based`로 fallback합니다. 응답에는 `fallback_from: "rag_based"`와 `fallback_reason`이 포함될 수 있습니다.

## Supabase 설정 개요

Supabase는 다음 기능에 사용됩니다.

- Auth: 구급대원/병원 계정 로그인
- `profiles`: 사용자 역할과 소속 병원 매핑
- `hospitals`: 병원 기본 마스터 데이터
- `hospital_status`: 병원별 수용 가능 병상 상태
- `transfer_requests`: 이송 요청 상태 관리
- `patient_cases`: 환자 케이스와 추천 결과 스냅샷 저장
- Realtime: 병원 상태 및 이송 요청 변경 알림

자세한 SQL과 RLS 정책은 [Supabase Setup](Supabase-Setup.md)을 참고하세요.
