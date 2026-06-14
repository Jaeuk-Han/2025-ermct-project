# Supabase Setup

Supabase는 프론트엔드의 인증, 역할 기반 접근, 병원 상태, 이송 요청, 환자 케이스 저장에 사용됩니다. SQL 원본은 `front/src/SUPABASE_SETUP_GUIDE.md`를 기준으로 정리했습니다.

민감정보 주의:

- service role key는 프론트엔드, README, Wiki, 브라우저 로그에 포함하지 않습니다.
- 프론트엔드는 anon public key만 사용합니다.
- 환자 실명, 주민등록번호, 상세 연락처 등 실제 개인정보는 저장하지 않거나 마스킹합니다.

## profiles

사용자 계정과 역할을 연결하는 테이블입니다.

주요 필드:

- `id`: Supabase Auth user id
- `role`: `paramedic` 또는 `hospital`
- `name`: 표시 이름
- `organization`: 소속 기관
- `phone`: 연락처
- `paramedic_unit`: 구급대 소속
- `hospital_id`: 병원 계정인 경우 연결된 `hospitals.id`

역할 규칙:

- 구급대원은 `role = 'paramedic'`
- 병원 사용자는 `role = 'hospital'`이고 `hospital_id`가 필요합니다.

## hospitals

병원 마스터 데이터입니다. 백엔드 ERMCT API의 HPID와 맞추기 위해 `id`는 `TEXT`입니다.

주요 필드:

- `id`: HPID 또는 앱에서 사용하는 병원 id
- `name`
- `address`
- `phone`
- `emergency_phone`
- `latitude`
- `longitude`
- `region_sido`
- `region_sigungu`
- `is_active`

추천 API 결과를 Supabase 이송 요청과 연결하려면 FastAPI 응답의 병원 `id`와 Supabase `hospitals.id`가 일치해야 합니다.

## hospital_status

병원별 수용 가능 상태와 병상 정보를 저장합니다.

주요 필드:

- `hospital_id`: `hospitals.id`
- `available_beds`, `total_beds`
- `er_available_beds`, `er_total_beds`
- `icu_available_beds`, `icu_total_beds`
- `isolation_available_beds`, `isolation_total_beds`
- `bed_services`: UI 표시용 세부 병상 JSON
- `is_accepting`: 현재 수용 가능 여부
- `status_note`: 병원 상태 메모
- `updated_by`: 마지막 수정 사용자

병원 대시보드는 자기 병원의 status를 업데이트하고, 구급대원 화면은 병원 상태를 조회해 이송 판단에 참고할 수 있습니다.

## transfer_requests

구급대원이 병원에 보내는 이송 요청의 상태를 관리합니다.

주요 필드:

- `hospital_id`
- `paramedic_id`
- `status`: `waiting`, `approved`, `rejected`, `transferring`, `completed`, `cancelled`
- `rejection_reason`
- `ktas_level`, `ktas_label`
- `symptoms`, `consciousness`
- `vitals_bp`, `vitals_pulse`, `vitals_resp`, `vitals_spo2`, `vitals_temp`
- `route_eta_min`, `route_distance_km`
- `paramedic_name`, `paramedic_unit`, `paramedic_contact`
- 상태별 timestamp: `requested_at`, `approved_at`, `rejected_at`, `transferring_at`, `completed_at`, `cancelled_at`

프론트엔드 병원 화면은 `transfer_requests`를 구독해 새 요청과 상태 변경을 실시간으로 반영합니다.

## patient_cases

환자 케이스 상세와 추천 결과 스냅샷을 저장합니다. `transfer_request_id`와 1:1로 연결됩니다.

주요 필드:

- `transfer_request_id`
- `paramedic_id`
- `display_name`: 마스킹된 표시 이름
- `age`, `gender`
- `symptoms`, `extra_note`, `summary`
- `ktas_level`, `ktas_label`, `ktas_name`
- `complaint_id`, `complaint_label`
- `consciousness`
- `vitals_bp`, `vitals_pulse`, `vitals_resp`, `vitals_spo2`, `vitals_temp`
- `existing_hospital`
- `assigned_hospital_id`, `assigned_hospital_name`, `assigned_hospital_address`, `assigned_hospital_phone`
- `origin_lat`, `origin_lon`
- `route_eta_min`, `route_distance_km`
- `recommendation_reason`
- `recommendation_snapshot`: 추천 API 응답 일부를 JSON으로 저장
- `status`

원본 음성, 환자 실명, 주민등록번호, 상세 주소 같은 민감정보는 저장하지 않는 설계를 권장합니다.

## role 기반 접근 구조

RLS 정책의 핵심 의도:

- 모든 authenticated 사용자는 병원 기본정보와 병원 상태를 조회할 수 있습니다.
- 사용자는 자기 `profiles`만 조회/수정할 수 있습니다.
- 병원 사용자는 자기 `hospital_id`에 해당하는 `hospital_status`만 수정할 수 있습니다.
- 구급대원은 자기 `transfer_requests`와 `patient_cases`를 생성하고 관리합니다.
- 병원 사용자는 자기 병원으로 들어온 이송 요청을 조회/수정할 수 있습니다.
- 병원 사용자는 자기 병원의 요청에 연결된 환자 케이스만 조회할 수 있습니다.

권장 role 값은 두 가지만 사용합니다.

```text
paramedic
hospital
```

## Realtime 사용 방식

Realtime publication 대상:

- `transfer_requests`
- `hospital_status`

선택적으로 `patient_cases`도 구독할 수 있습니다.

사용 흐름:

1. 구급대원이 추천 병원 중 하나를 선택합니다.
2. 프론트엔드가 `transfer_requests`에 `waiting` 상태 요청을 생성합니다.
3. 병원 화면은 자기 병원의 `transfer_requests` 변경을 Realtime으로 감지합니다.
4. 병원이 승인 또는 거절하면 row의 `status`와 timestamp를 업데이트합니다.
5. 구급대원 화면은 상태 변경을 구독해 이송 진행 상태를 갱신합니다.
6. 병상 수 변경이 필요한 경우 `hospital_status`를 업데이트하고 다른 화면에 반영합니다.

## 주의사항

- service role key는 로컬 서버 또는 보안 백엔드에서만 사용합니다.
- 브라우저 콘솔, 스크린샷, 문서에 실제 access token이나 refresh token을 남기지 않습니다.
- `hospitals.id`는 FastAPI 추천 결과의 `id`와 맞춰야 이송 요청이 자연스럽게 연결됩니다.
- Realtime은 RLS 정책의 영향을 받으므로 구독 전에 로그인 세션과 profile role을 확인해야 합니다.
- demo seed data를 사용할 때도 실제 병원 운영 상태처럼 오해될 수 있는 문구는 피합니다.
- `transfer_requests.status`와 `patient_cases.status`는 같은 status standard를 사용합니다.
