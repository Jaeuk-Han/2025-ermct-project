# Limitations and Future Work

## 현재 한계

- KTAS 결과는 의료진 판단을 대체하지 않습니다. 구급대원 입력, STT 품질, SBAR 추출, rule/RAG 분류 결과에 따라 오차가 발생할 수 있습니다.
- `predict-text`와 `predict-audio`는 현재 Stage 1 KTAS 분석 응답을 반환하고, 병원 routing은 `/api/ktas/route/seoul`로 별도 호출해야 합니다.
- 음성 입력은 녹음 품질, 배경 소음, 발화 속도, 의학 용어 인식률에 영향을 받습니다.
- `rule_based` KTAS는 코드에 정의된 조건 중심으로 작동하므로 모든 KTAS guideline 상황을 완전하게 포괄하지 않습니다.
- `rag_based` KTAS는 guideline index, embedding 품질, 검색 결과, LLM 응답 JSON 품질에 의존합니다.
- RAG 실패 시 fallback은 안정성을 높이지만, 최종 결과가 rule-based로 바뀌므로 UI에서 fallback 여부를 표시해야 합니다.
- 병원 추천은 실시간 API 응답, 병원 좌표, MKioskTy flag, procedure group mapping, 병상 수 계산에 의존합니다.
- 외부 공공 API 또는 Tmap API 장애, rate limit, 네트워크 지연이 추천 결과 품질과 응답 시간에 영향을 줄 수 있습니다.
- `transfer_requests`와 `patient_cases`의 실제 운영 연동은 Supabase RLS, 계정 role, 병원 id mapping이 정확히 맞아야 합니다.
- 일부 debug endpoint와 in-memory reservation 기능은 시연/개발 보조용이며 서버 재시작 시 상태가 유지되지 않습니다.

## 정량 평가 한계

- 현재 Wiki 기준으로 공개된 정량 임상 검증 지표는 포함하지 않았습니다.
- KTAS 예측 정확도는 실제 응급 사례 gold label dataset과 비교해 평가해야 합니다.
- 추천 병원 품질은 실제 수용 결과, 이송 시간, 병상 상태 정확도, 병원 거절률 등을 함께 측정해야 합니다.
- RAG 기반 KTAS는 검색 hit 품질, guideline coverage, fallback 비율을 별도로 기록해야 평가할 수 있습니다.
- STT 기반 입력은 텍스트 원문, STT transcript, SBAR 추출값, KTAS 결과를 분리해 오류 원인을 분석해야 합니다.
- 외부 API의 실시간 병상 데이터가 실제 현장 수용 가능성과 항상 일치한다고 볼 수 없습니다.

권장 평가 항목:

- KTAS exact match accuracy
- KTAS 1~2 고위험군 recall
- `rag_based` fallback rate
- SBAR 필드 추출 성공률
- SpO2, 혈압, 맥박, 호흡수, 체온 등 활력징후 추출 정확도
- 병원 추천 후보 중 실제 수용 가능 병원 비율
- Tmap ETA와 실제 이송 시간 차이
- API 평균/95th percentile 응답 시간

## 향후 개선 방향

- Stage 1 KTAS 분석과 Stage 2 병원 routing을 명확한 워크플로 API로 통합하거나, 프론트엔드에서 단계별 상태를 더 분명하게 표시합니다.
- KTAS guideline index 생성 과정을 문서화하고, index 버전과 생성 일시를 응답 metadata에 포함합니다.
- `rag_based` 결과의 evidence 문서 id, confidence, fallback reason을 사용자 화면에서 확인 가능하게 만듭니다.
- 실제 테스트셋을 구축해 `rule_based`, `rag_based`, fallback 결과를 비교 평가합니다.
- STT transcript와 SBAR JSON을 의료정보 보호 기준에 맞춰 저장/비저장 옵션으로 분리합니다.
- 병원 추천에서 Supabase `hospital_status`와 ERMCT 실시간 병상 정보를 병합하는 정책을 명확히 합니다.
- in-memory reservation을 영속 저장소 기반 reservation으로 전환합니다.
- debug endpoint를 운영 환경에서 비활성화하거나 인증을 적용합니다.
- 외부 API 장애 시 stale cache, retry, circuit breaker, 사용자 안내 메시지를 추가합니다.
- 병원 id mapping, 지역명 normalization, 시군구 adjacency 검색 로그를 운영 모니터링 지표로 남깁니다.
- 프론트엔드에서 빈 optional field는 `-`로 표시하고, 누락된 SpO2 등 활력징후는 안전하게 생략합니다.
