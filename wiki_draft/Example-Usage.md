# Example Usage

이 문서의 예시는 로컬 백엔드가 `http://localhost:8000`에서 실행 중이라고 가정합니다. 실제 API key, 환자 실명, 주민등록번호, 연락처 등 민감정보는 요청 예시에 넣지 마세요.

## 텍스트 기반 KTAS 예시

### curl

```bash
curl -X POST "http://localhost:8000/api/ktas/predict-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "70세 남성, 갑작스러운 호흡곤란과 흉부 불편감. SpO2 88%, 호흡수 30회, 수축기혈압 92, 의식은 명료합니다.",
    "ktas_method": "rule_based"
  }'
```

### Python requests

```python
import requests

base_url = "http://localhost:8000"

payload = {
    "text": "70세 남성, 갑작스러운 호흡곤란과 흉부 불편감. SpO2 88%, 호흡수 30회, 수축기혈압 92, 의식은 명료합니다.",
    "ktas_method": "rag_based",
}

response = requests.post(f"{base_url}/api/ktas/predict-text", json=payload, timeout=60)
response.raise_for_status()
data = response.json()

print(data["case"]["ktas"])
print(data.get("ktas_method"))
print(data.get("fallback_from"))
```

## 음성 기반 KTAS 예시

### curl

```bash
curl -X POST "http://localhost:8000/api/ktas/predict-audio?ktas_method=rule_based" \
  -F "audio=@sample.webm;type=audio/webm"
```

### Python requests

```python
import requests

base_url = "http://localhost:8000"

with open("sample.webm", "rb") as audio_file:
    files = {"audio": ("sample.webm", audio_file, "audio/webm")}
    response = requests.post(
        f"{base_url}/api/ktas/predict-audio",
        params={"ktas_method": "rag_based"},
        files=files,
        timeout=120,
    )

response.raise_for_status()
data = response.json()
print(data["case"])
print(data.get("stt_vitals"))
```

## 병원 추천 예시

KTAS 분석 결과에서 `ktas_level`, `chief_complaint`, `hospital_followup` 등을 추출한 뒤 routing API로 전달합니다.

### curl

```bash
curl -X POST "http://localhost:8000/api/ktas/route/seoul" \
  -H "Content-Type: application/json" \
  -d '{
    "ktas_level": 2,
    "chief_complaint": "dyspnea",
    "hospital_followup": null,
    "current_sigungu_name": "종로구",
    "user_lat": 37.5665,
    "user_lon": 126.9780,
    "min_valid_hospitals": 3
  }'
```

### Python requests

```python
import requests

base_url = "http://localhost:8000"

route_payload = {
    "ktas_level": 2,
    "chief_complaint": "dyspnea",
    "hospital_followup": None,
    "current_sigungu_name": "종로구",
    "user_lat": 37.5665,
    "user_lon": 126.9780,
    "min_valid_hospitals": 3,
}

response = requests.post(f"{base_url}/api/ktas/route/seoul", json=route_payload, timeout=60)
response.raise_for_status()
routing = response.json()

for hospital in routing["hospitals"][:3]:
    print(hospital["name"], hospital["total_effective_beds"], hospital["reason_summary"])
```

## 거리/ETA 조회 예시

`/api/ktas/route/seoul` 응답 전체에 `user_lat`, `user_lon`을 추가해 전송합니다.

```python
import requests

base_url = "http://localhost:8000"

routing["user_lat"] = 37.5665
routing["user_lon"] = 126.9780

response = requests.post(
    f"{base_url}/api/ktas/route/seoul/nearest",
    json=routing,
    timeout=60,
)
response.raise_for_status()
nearest = response.json()

for hospital in nearest["hospitals"]:
    print(
        hospital["name"],
        hospital.get("distance"),
        hospital.get("duration_sec"),
    )
```

## 경로 조회 예시

### curl

```bash
curl -X POST "http://localhost:8000/api/ktas/route/path" \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 37.5665,
    "start_lon": 126.9780,
    "end_lat": 37.5796,
    "end_lon": 126.9990
  }'
```

### Python requests

```python
import requests

base_url = "http://localhost:8000"

payload = {
    "start_lat": 37.5665,
    "start_lon": 126.9780,
    "end_lat": 37.5796,
    "end_lon": 126.9990,
}

response = requests.post(f"{base_url}/api/ktas/route/path", json=payload, timeout=60)
response.raise_for_status()
route = response.json()

print(route["distance"])
print(route["duration_sec"])
print(route["path"][:3])
```

## 병원 정보 조회 예시

```bash
curl "http://localhost:8000/api/hospitals/summary/by-region?sido=서울특별시&sigungu=종로구&num_rows=50"
```

```python
import requests

base_url = "http://localhost:8000"

response = requests.get(
    f"{base_url}/api/hospitals/procedure-beds/by-region",
    params={"sido": "서울특별시", "sigungu": "종로구", "complaint_id": 2},
    timeout=60,
)
response.raise_for_status()
for row in response.json()[:5]:
    print(row["id"], row["name"], row["er_beds"], row["has_any_bed"])
```

## KTAS method 선택 흐름

프론트엔드는 `rule_based`와 `rag_based` 중 하나를 선택해 전송합니다.

- 텍스트: JSON body의 `ktas_method`
- 음성: query parameter의 `ktas_method`

`rag_based` 요청에서 guideline index가 없거나 RAG 분류가 실패하면 백엔드는 rule-based 결과를 반환합니다. 이 경우 `fallback_from`과 `fallback_reason`을 UI에 표시하면 시연 중 어떤 방식으로 최종 KTAS가 결정되었는지 설명할 수 있습니다.
