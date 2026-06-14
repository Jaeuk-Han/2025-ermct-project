# ERMCT Emergency Transfer Project Wiki

## 프로젝트 개요

이 프로젝트는 119 구급대의 응급 이송 의사결정을 돕기 위한 FastAPI 백엔드와 React 프론트엔드 기반 시스템입니다. 환자 상태를 텍스트 또는 음성으로 입력하면 SBAR 형태로 정리하고, KTAS 등급과 주호소를 추정한 뒤, 응급의료기관 공개 API와 Tmap 경로 API를 활용해 이송 후보 병원을 추천합니다.

프론트엔드는 구급대원 화면, 병원 대시보드, 응급실 태블릿 화면을 포함합니다. Supabase는 로그인, 사용자 역할, 병원 상태, 이송 요청, 환자 케이스 저장 및 Realtime 알림 흐름에 사용됩니다.

## 주요 기능

- 텍스트 기반 KTAS 분석: `/api/ktas/predict-text`
- 음성 업로드 기반 KTAS 분석: `/api/ktas/predict-audio`
- KTAS 결과와 위치/시군구 정보 기반 병원 후보 추천: `/api/ktas/route/seoul`
- 후보 병원 중 Tmap 거리/ETA 기준 Top 3 계산: `/api/ktas/route/seoul/nearest`
- 출발지-목적지 경로 좌표 조회: `/api/ktas/route/path`
- 응급의료기관 실시간 병상, 기본정보, 중증질환 수용 가능 정보 조회
- 병원별 처치/시술 그룹 가용 병상 계산
- Supabase 기반 이송 요청 생성, 병원 승인/거절, 환자 케이스 기록
- KTAS 방식 선택: `rule_based` 또는 `rag_based`
- RAG 실패 시 rule-based KTAS로 자동 fallback

## 전체 시스템 흐름

1. 구급대원이 프론트엔드에서 환자 정보, 활력징후, 현 위치, 기존 진료 병원 등을 입력합니다.
2. 텍스트 또는 음성을 백엔드 KTAS 분석 API로 전송합니다.
3. 백엔드는 OpenAI 기반 SBAR 추출 후 `rule_based` 또는 `rag_based` 방식으로 KTAS 후보를 계산합니다.
4. `rag_based` 선택 시 KTAS guideline vector index를 조회합니다. 인덱스 미로드, 검색 실패, JSON 파싱 실패 등 예외가 발생하면 `rule_based` 결과로 fallback합니다.
5. 프론트엔드는 KTAS 결과의 `ktas_level`, `chief_complaint`, `hospital_followup`, 위치 정보를 `/api/ktas/route/seoul`로 전송합니다.
6. 백엔드는 주호소를 complaint category로 매핑하고 필요한 procedure group과 실시간 병상 정보를 조합해 후보 병원을 필터링합니다.
7. 후보가 부족하거나 지역 조회가 실패하면 시군구 인접 검색 또는 전체 인덱스 기반 fallback 조회를 수행합니다.
8. 프론트엔드는 `/api/ktas/route/seoul/nearest`와 `/api/ktas/route/path`로 거리, ETA, 경로 좌표를 보강합니다.
9. 구급대원이 병원을 선택하면 Supabase `transfer_requests`와 `patient_cases`에 이송 요청과 환자 케이스 스냅샷을 저장합니다.
10. 병원/응급실 화면은 Supabase Realtime으로 요청 상태 변경을 감지하고 승인, 거절, 이송 중, 완료 흐름을 처리합니다.

## Wiki 목차

- [Installation](Installation.md): 로컬 실행 환경, 백엔드/프론트엔드 실행, 환경변수, Supabase 설정 개요
- [Tech Stack](Tech-Stack.md): Backend, Frontend, Database, External APIs, AI/NLP 구성
- [API Reference](API-Reference.md): 현재 코드에 존재하는 FastAPI endpoint 설명
- [Example Usage](Example-Usage.md): curl 및 Python requests 예제
- [Supabase Setup](Supabase-Setup.md): 주요 테이블, RLS, Realtime, 운영 주의사항
- [Limitations and Future Work](Limitations-and-Future-Work.md): 현재 한계와 개선 방향
