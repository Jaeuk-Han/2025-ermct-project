# API Reference

기본 주소:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

## 주요 endpoint 목록

### Core KTAS / Routing API

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/health` | 백엔드 상태 확인 |
| POST | `/api/ktas/predict-text` | 텍스트 기반 KTAS Stage 1 분석 |
| POST | `/api/ktas/predict-audio` | 음성 업로드 기반 KTAS Stage 1 분석 |
| POST | `/api/ktas/route/seoul` | KTAS 결과와 위치/시군구 정보 기반 병원 후보 추천 |
| POST | `/api/ktas/route/seoul/nearest` | 후보 병원 중 거리 기준 Top 3 |
| POST | `/api/ktas/route/path` | Tmap 경로 좌표, 거리, ETA 조회 |

### Hospital Information API

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/api/hospitals/realtime` | 지역별 실시간 응급실 병상 정보 |
| GET | `/api/hospitals/basic` | HPID 기준 병원 기본정보 |
| GET | `/api/hospitals/serious` | 지역별 중증질환 수용 가능 정보 |
| GET | `/api/hospitals/messages` | HPID 기준 응급/중증 메시지 |
| GET | `/api/hospitals/summary` | 단일 병원 통합 요약 |
| GET | `/api/hospitals/summary/by-region` | 지역별 병원 통합 요약 목록 |
| GET | `/api/hospitals/trauma/by-region` | 지역별 외상센터 정보 |
| GET | `/api/hospitals/complaint-coverage/by-region` | 병원별 지원 가능한 주호소 범주 |
| GET | `/api/hospitals/procedure-beds/by-region` | 지역별 처치/시술 group 병상 상태 |

### Triage / Reservation Demo API

| Method | Path | 설명 |
| --- | --- | --- |
| POST | `/api/triage/recommend` | legacy triage 기반 추천입니다. 최신 KTAS routing 흐름과 혼동하지 않도록 데모/비교용으로 사용합니다. |
| POST | `/api/triage/candidates` | legacy triage 기반 후보 병원 반환입니다. 튜닝, 로그 확인, 개발 보조 용도입니다. |
| POST | `/api/triage/reservations` | in-memory 병상 예약 반영 데모 API입니다. 서버 재시작 시 상태가 유지되지 않습니다. |
| POST | `/api/triage/reservations/release` | in-memory 병상 예약 해제 데모 API입니다. 운영 예약 저장소가 아닙니다. |

### Debug API

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/debug/triage/pending-assignments` | in-memory 예약 반영 상태를 확인하는 개발용 endpoint입니다. |
| GET | `/debug/hospitals/realtime/xml` | ERMCT 실시간 병상 raw XML 확인용 endpoint입니다. |
| GET | `/debug/hospitals/serious/xml` | ERMCT 중증질환 수용 가능 raw XML 확인용 endpoint입니다. |

`/debug/*` endpoint는 개발/시연용입니다. 운영 환경에서는 접근 제어 또는 비활성화를 권장합니다.

## KTAS 분석 API

### POST `/api/ktas/predict-text`

텍스트 보고를 받아 KTAS 분석 결과를 반환합니다. 현재 구현은 Stage 1 결과를 반환하며, 병원 routing은 별도로 `/api/ktas/route/seoul`에 요청합니다.

Request body:

```json
{
  "text": "70세 남성, 흉통과 호흡곤란, SpO2 88%, 수축기혈압 90, 의식은 명료합니다.",
  "ktas_method": "rag_based"
}
```

`ktas_method`:

- `rule_based`: 기본값. SBAR 추출 후 rule engine으로 KTAS를 계산합니다.
- `rag_based`: KTAS guideline vector index 검색과 LLM 후보 생성을 사용합니다.

Response 예시:

```json
{
  "followup_id": null,
  "case": {
    "ktas": 2,
    "complaint_id": 2,
    "complaint_label": "호흡곤란",
    "required_procedure_groups": ["respiratory"],
    "required_procedure_group_labels": ["호흡기 처치"]
  },
  "hospitals": [],
  "stt_vitals": {
    "sbp": 90,
    "hr": 118,
    "rr": 28,
    "spo2": 88
  },
  "ktas_method": "rag_based",
  "confidence": 0.73,
  "evidence": ["ktas-guideline-example"],
  "ktas_options": [
    {
      "ktas": 2,
      "reason": "저산소증과 호흡곤란",
      "confidence": 0.73
    }
  ],
  "fallback_from": null,
  "fallback_reason": null
}
```

RAG 실패 시 응답 예시:

```json
{
  "ktas_method": "rule_based",
  "fallback_from": "rag_based",
  "fallback_reason": "RAG fallback: RAG index is not loaded."
}
```

### POST `/api/ktas/predict-audio`

`multipart/form-data`로 음성 파일을 업로드합니다.

Query:

- `ktas_method`: `rule_based` 또는 `rag_based`, 기본값 `rule_based`

Form field:

- `audio`: webm, wav 등 브라우저에서 녹음한 오디오 파일

오디오 바이트 수가 너무 작으면 `400`과 `reason: "audio_too_small"`을 반환합니다.

## 병원 추천 API

### POST `/api/ktas/route/seoul`

Endpoint path에는 `seoul`이 포함되어 있지만, 현재 구현은 KTAS Stage 1 결과와 사용자 위치, 시군구 코드/이름, 인접 시군구 확장을 활용해 병원 후보를 찾는 흐름입니다. 현재 위치 시군구 코드/이름 또는 위도/경도를 함께 보내면 인접 시군구 검색을 먼저 수행하고, 후보가 부족하면 전체 인덱스 기반 fallback을 수행합니다.

Request body:

```json
{
  "ktas_level": 2,
  "chief_complaint": "dyspnea",
  "hospital_followup": "A1100010",
  "current_sigungu_code": "11110",
  "current_sigungu_name": "종로구",
  "user_lat": 37.5665,
  "user_lon": 126.9780,
  "min_valid_hospitals": 3
}
```

Response 주요 필드:

- `followup_id`: 기존 진료 병원 또는 후속 병원 HPID가 해석된 값
- `case`: KTAS, complaint id, complaint label, 필요한 procedure groups
- `hospitals`: 추천 후보 병원 목록
- `total_effective_beds`: 현재 이 환자 유형에 실질적으로 사용할 수 있는 병상 수
- `coverage_score`, `coverage_level`: 필요한 procedure group 충족도
- `priority_score`: 병상, 기존 진료 병원 우선순위, coverage를 반영한 정렬 점수
- `reason_summary`: 추천 이유 요약

### POST `/api/ktas/route/seoul/nearest`

`/api/ktas/route/seoul` 응답과 사용자 위치를 받아 Tmap 거리 기준 상위 3개 병원만 반환합니다.

Request body는 `RoutingCandidateResponse` 전체에 `user_lat`, `user_lon`을 추가한 형태입니다.

Response의 각 병원에는 다음 필드가 추가될 수 있습니다.

- `distance`: 도로 기준 거리, meter
- `duration_sec`: 예상 이동 시간, second

### POST `/api/ktas/route/path`

출발지와 목적지 좌표로 Tmap 경로 polyline을 조회합니다.

Request body:

```json
{
  "start_lat": 37.5665,
  "start_lon": 126.9780,
  "end_lat": 37.5796,
  "end_lon": 126.9990
}
```

Response:

```json
{
  "path": [
    { "lat": 37.5665, "lon": 126.9780 },
    { "lat": 37.5701, "lon": 126.9852 }
  ],
  "distance": 3200.0,
  "duration_sec": 680
}
```

Tmap 호출 또는 응답 파싱에 실패하면 `502`를 반환합니다.

## 병원 정보 API

### GET `/api/hospitals/realtime`

Query:

- `sido`: 시도명
- `sigungu`: 시군구명
- `num_rows`: 1~200, 기본값 50

예시:

```text
/api/hospitals/realtime?sido=서울특별시&sigungu=종로구&num_rows=50
```

### GET `/api/hospitals/basic`

Query:

- `hpid`: 병원 HPID

### GET `/api/hospitals/summary/by-region`

Query:

- `sido`
- `sigungu`
- `sm_type`: 기본값 1
- `num_rows`: 1~500, 기본값 200

병원 기본정보, 실시간 병상, 중증질환 수용 가능 정보, 응급 메시지를 통합한 목록을 반환합니다.

## 오류 상황

대표 오류:

- `400`: 지원하지 않는 `chief_complaint`, 잘못된 `complaint_id`, 너무 짧은 음성, STT 유효성 실패
- `422`: FastAPI/Pydantic request validation 실패
- `502`: Tmap route 계산 실패
- `500`: 필수 환경변수 누락, 외부 API 예외, OpenAI 호출 실패 등

환경변수 누락 예:

- `ERMCT_SERVICE_KEY`가 없으면 백엔드 import 단계에서 RuntimeError가 발생할 수 있습니다.
- `TMAP_APP_KEY`가 없으면 거리/경로 로직 import 단계에서 ValueError가 발생할 수 있습니다.
- `OPENAI_API_KEY`가 없으면 KTAS SBAR/RAG 호출 시 RuntimeError가 발생합니다.
