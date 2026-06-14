# Tech Stack

## Backend

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- Poetry
- requests, httpx
- python-dotenv
- xmltodict
- python-multipart

백엔드는 외부 공공 API와 Tmap API를 호출하고, KTAS 분석 결과를 병원 추천 API 입력 형태로 변환합니다. 모든 Python 실행 및 검증은 Poetry 환경에서 수행합니다.

## Frontend

- React 18
- Vite
- TypeScript
- Supabase JavaScript SDK
- Radix UI components
- lucide-react
- Recharts
- Sonner

주요 화면:

- `ParamedicDashboard`: 환자 입력, KTAS 분석, 병원 추천, 이송 요청
- `HospitalDashboard`: 병원 계정의 요청 확인 및 수용 상태 관리
- `ERTabletDashboard`: 응급실 태블릿용 요청/환자 상태 표시
- `LoginPage`: Supabase Auth 로그인

프론트엔드 API 클라이언트는 `front/src/utils/api.ts`에 있으며, 기본 백엔드 주소는 `VITE_API_BASE_URL` 또는 `http://localhost:8000`입니다.

## Database

- Supabase PostgreSQL
- Supabase Auth
- Row Level Security
- Supabase Realtime

핵심 테이블:

- `profiles`
- `hospitals`
- `hospital_status`
- `transfer_requests`
- `patient_cases`

## External APIs

- ERMCT / 응급의료기관 공개 API
  - 실시간 응급실 병상 정보
  - 응급의료기관 기본정보
  - 중증질환 수용 가능 정보
  - 응급/중증 메시지
  - 외상센터 정보
- Tmap routes API
  - 병원 후보별 거리와 예상 이동 시간
  - 출발지-목적지 경로 polyline 좌표
- Kakao local API
  - 현재 위도/경도를 시군구로 변환하는 보조 기능

## AI / NLP Components

- OpenAI Chat Completions
  - 구급대원 발화 또는 입력 텍스트를 SBAR JSON으로 구조화
  - RAG 기반 KTAS 후보 생성
- OpenAI Embeddings
  - KTAS guideline vector index 생성 및 검색
- Whisper
  - 음성 업로드 파일을 텍스트로 변환
- Rule-based KTAS engine
  - SBAR의 의식, 혈압, 호흡수, SpO2, 체온, 증상 modifier 등을 기준으로 KTAS 1~3 중심 분류
- RAG-based KTAS engine
  - KTAS guideline index 검색 결과와 SBAR를 함께 사용해 KTAS 후보, 근거, confidence를 생성
  - 실패 시 rule-based로 fallback
