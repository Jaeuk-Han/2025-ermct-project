# P-실무 임시 공유

## 실행 명령어

```bash
uvicorn app.main:app --reload --port 8000
```
## Fast API Swagger

```text
http://127.0.0.1:8000/docs
```

## 현재 출력 예제

```json
{
  "followup_id": "A1100017",
  "case": {
    "ktas": 2,
    "complaint_id": 2,
    "complaint_label": "호흡곤란 (Dyspnea / Respiratory distress)",
    "required_procedure_groups": [
      "ACS_MI",
      "ACS_STROKE",
      "AORTIC_EMERGENCY",
      "BRONCHOSCOPY",
      "GI_ENDOSCOPY"
    ],
    "required_procedure_group_labels": [
      "심근경색/ACS (응급 PCI)",
      "뇌졸중 (재관류/중재)",
      "대동맥 응급(박리/파열)",
      "기관지 내시경",
      "소화기 내시경(출혈 포함)"
    ]
  },
  "hospitals": [
    {
      "id": "A1100001",
      "name": "경희대학교병원",
      "address": "서울특별시 동대문구 경희대로 23 (회기동)",
      "phone": "02-958-8114",
      "emergency_phone": "02-958-8114",
      "latitude": 37.5938765502235,
      "longitude": 127.05183223390303,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 10,
          "effective_beds": 10
        },
        "ACS_STROKE": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 10,
          "effective_beds": 10
        },
        "GI_ENDOSCOPY": {
          "api_beds": 10,
          "effective_beds": 10
        }
      },
      "total_effective_beds": 27,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "ACS_STROKE",
        "BRONCHOSCOPY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "뇌졸중 (재관류/중재)",
        "기관지 내시경",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy12",
        "MKioskTy13",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy24",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.8,
      "coverage_level": "HIGH",
      "priority_score": 25.9,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 뇌졸중 (재관류/중재), 기관지 내시경, 소화기 내시경(출혈 포함) 기준 총 유효 병상 27개가 남아 있어 후보로 선정됨. (시술 커버리지: 핵심 시술 대부분 가능, 약 80% 충족)"
    },
    {
      "id": "A1100007",
      "name": "연세대학교의과대학세브란스병원",
      "address": "서울특별시 서대문구 연세로 50-1 (신촌동)",
      "phone": "02-2228-0114",
      "emergency_phone": "02-2227-7777",
      "latitude": 37.56211711412639,
      "longitude": 126.94082769649863,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 6,
          "effective_beds": 6
        },
        "ACS_STROKE": {
          "api_beds": 3,
          "effective_beds": 3
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 6,
          "effective_beds": 6
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 6,
          "effective_beds": 6
        }
      },
      "total_effective_beds": 27,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "ACS_STROKE",
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "뇌졸중 (재관류/중재)",
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy13",
        "MKioskTy14",
        "MKioskTy15",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy24",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy27",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.8,
      "coverage_level": "HIGH",
      "priority_score": 25.9,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 뇌졸중 (재관류/중재), 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 27개가 남아 있어 후보로 선정됨. (시술 커버리지: 핵심 시술 대부분 가능, 약 80% 충족)"
    },
    {
      "id": "A1100014",
      "name": "고려대학교의과대학부속구로병원",
      "address": "서울특별시 구로구 구로동로 148, 고려대부속구로병원 (구로동)",
      "phone": "02-2626-1114",
      "emergency_phone": "02-2626-1550",
      "latitude": 37.49211114525054,
      "longitude": 126.8847449363546,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 3,
          "effective_beds": 3
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 3,
          "effective_beds": 3
        },
        "BRONCHOSCOPY": {
          "api_beds": 3,
          "effective_beds": 3
        },
        "GI_ENDOSCOPY": {
          "api_beds": 22,
          "effective_beds": 22
        }
      },
      "total_effective_beds": 25,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY",
        "BRONCHOSCOPY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)",
        "기관지 내시경",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy12",
        "MKioskTy13",
        "MKioskTy14",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy24",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy27",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.8,
      "coverage_level": "HIGH",
      "priority_score": 24,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열), 기관지 내시경, 소화기 내시경(출혈 포함) 기준 총 유효 병상 25개가 남아 있어 후보로 선정됨. (시술 커버리지: 핵심 시술 대부분 가능, 약 80% 충족)"
    },
    {
      "id": "A1100009",
      "name": "재단법인아산사회복지재단서울아산병원",
      "address": "서울특별시 송파구 올림픽로43길 88, 서울아산병원 (풍납동)",
      "phone": "02-3010-3114",
      "emergency_phone": "02-3010-3333",
      "latitude": 37.526563966361216,
      "longitude": 127.10823825113607,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 28,
          "effective_beds": 28
        }
      },
      "total_effective_beds": 30,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_STROKE",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "뇌졸중 (재관류/중재)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy24",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 23.1,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 뇌졸중 (재관류/중재), 소화기 내시경(출혈 포함) 기준 총 유효 병상 30개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100043",
      "name": "강동경희대학교의대병원",
      "address": "서울특별시 강동구 동남로 892 (상일동)",
      "phone": "02-440-7114",
      "emergency_phone": "02-440-7000",
      "latitude": 37.5520459324005,
      "longitude": 127.157084787845,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 8,
          "effective_beds": 8
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 8,
          "effective_beds": 8
        },
        "BRONCHOSCOPY": {
          "api_beds": 8,
          "effective_beds": 8
        },
        "GI_ENDOSCOPY": {
          "api_beds": 15,
          "effective_beds": 15
        }
      },
      "total_effective_beds": 23,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY",
        "BRONCHOSCOPY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)",
        "기관지 내시경",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy13",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy6",
        "MKioskTy9"
      ],
      "coverage_score": 0.8,
      "coverage_level": "HIGH",
      "priority_score": 22.1,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열), 기관지 내시경, 소화기 내시경(출혈 포함) 기준 총 유효 병상 23개가 남아 있어 후보로 선정됨. (시술 커버리지: 핵심 시술 대부분 가능, 약 80% 충족)"
    },
    {
      "id": "A1100035",
      "name": "서울특별시서울의료원",
      "address": "서울특별시 중랑구 신내로 156 (신내동)",
      "phone": "02-2276-7000",
      "emergency_phone": "02-2276-7000",
      "latitude": 37.61286931510163,
      "longitude": 127.0980910949257,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "ACS_STROKE": {
          "api_beds": 1,
          "effective_beds": 1
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "BRONCHOSCOPY": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "GI_ENDOSCOPY": {
          "api_beds": 18,
          "effective_beds": 18
        }
      },
      "total_effective_beds": 21,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "ACS_STROKE",
        "AORTIC_EMERGENCY",
        "BRONCHOSCOPY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "뇌졸중 (재관류/중재)",
        "대동맥 응급(박리/파열)",
        "기관지 내시경",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy13",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy19",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy24",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 1,
      "coverage_level": "FULL",
      "priority_score": 21.6,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 뇌졸중 (재관류/중재), 대동맥 응급(박리/파열), 기관지 내시경, 소화기 내시경(출혈 포함) 기준 총 유효 병상 21개가 남아 있어 후보로 선정됨. (시술 커버리지: 요청된 시술을 거의 모두 커버, 약 100% 충족)"
    },
    {
      "id": "A1100015",
      "name": "연세대학교의과대학강남세브란스병원",
      "address": "서울특별시 강남구 언주로 211, 강남세브란스병원 (도곡동)",
      "phone": "02-2019-3114",
      "emergency_phone": "02-2019-3333",
      "latitude": 37.492806984645476,
      "longitude": 127.04631254186798,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 7,
          "effective_beds": 7
        },
        "ACS_STROKE": {
          "api_beds": 3,
          "effective_beds": 3
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 7,
          "effective_beds": 7
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 7,
          "effective_beds": 7
        }
      },
      "total_effective_beds": 21,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "ACS_STROKE",
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "뇌졸중 (재관류/중재)",
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.8,
      "coverage_level": "HIGH",
      "priority_score": 20.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 뇌졸중 (재관류/중재), 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 21개가 남아 있어 후보로 선정됨. (시술 커버리지: 핵심 시술 대부분 가능, 약 80% 충족)"
    },
    {
      "id": "A1100040",
      "name": "서울특별시보라매병원",
      "address": "서울특별시 동작구 보라매로5길 20 (신대방동)",
      "phone": "02-870-2114",
      "emergency_phone": "02-870-2119",
      "latitude": 37.4937184009319,
      "longitude": 126.92404876254014,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 24,
          "effective_beds": 24
        }
      },
      "total_effective_beds": 24,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 18,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 24개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100005",
      "name": "이화여자대학교의과대학부속목동병원",
      "address": "서울특별시 양천구 안양천로 1071 (목동)",
      "phone": "02-2650-5114",
      "emergency_phone": "02-2650-5911",
      "latitude": 37.53654282637804,
      "longitude": 126.8862159683056,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 4,
          "effective_beds": 4
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 17,
          "effective_beds": 17
        }
      },
      "total_effective_beds": 21,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_STROKE",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "뇌졸중 (재관류/중재)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy13",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy27",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 16.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 뇌졸중 (재관류/중재), 소화기 내시경(출혈 포함) 기준 총 유효 병상 21개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100004",
      "name": "순천향대학교 부속 서울병원",
      "address": "서울특별시 용산구 대사관로 59 (한남동)",
      "phone": "02-709-9114",
      "emergency_phone": "02-709-9117",
      "latitude": 37.53384172231443,
      "longitude": 127.00441798640304,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 4,
          "effective_beds": 4
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 17,
          "effective_beds": 17
        }
      },
      "total_effective_beds": 21,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy2",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 16.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 소화기 내시경(출혈 포함) 기준 총 유효 병상 21개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1120796",
      "name": "이화여자대학교의과대학부속서울병원",
      "address": "서울특별시 강서구 공항대로 260, 이화의대부속서울병원 (마곡동)",
      "phone": "1522-7000",
      "emergency_phone": "02-6986-5119",
      "latitude": 37.557261149,
      "longitude": 126.8362659275,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 18,
          "effective_beds": 18
        }
      },
      "total_effective_beds": 20,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_STROKE",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "뇌졸중 (재관류/중재)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 15.4,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 뇌졸중 (재관류/중재), 소화기 내시경(출혈 포함) 기준 총 유효 병상 20개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100054",
      "name": "성애의료재단성애병원",
      "address": "서울특별시 영등포구 여의대방로53길 22 (신길동, 성애병원)",
      "phone": "02-840-7114",
      "emergency_phone": "02-840-7115",
      "latitude": 37.51205044957338,
      "longitude": 126.92236733617031,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 7,
          "effective_beds": 7
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 7,
          "effective_beds": 7
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        }
      },
      "total_effective_beds": 20,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        6,
        8
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy28",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 15.4,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열) 기준 총 유효 병상 20개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100008",
      "name": "학교법인고려중앙학원고려대학교의과대학부속병원(안암병원)",
      "address": "서울특별시 성북구 고려대로 73, 고려대병원 (안암동5가)",
      "phone": "1577-0083",
      "emergency_phone": "02-920-5374",
      "latitude": 37.58715608002366,
      "longitude": 127.02647086385966,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 20,
          "effective_beds": 20
        }
      },
      "total_effective_beds": 20,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy24",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy27",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 15,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 20개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100055",
      "name": "한림대학교강남성심병원",
      "address": "서울특별시 영등포구 신길로 1 (대림동, 강남성심병원)",
      "phone": "02-829-5114",
      "emergency_phone": "02-829-5119",
      "latitude": 37.4932492859,
      "longitude": 126.9086725295,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 19,
          "effective_beds": 19
        }
      },
      "total_effective_beds": 19,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy13",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy19",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 14.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 19개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100052",
      "name": "국립중앙의료원",
      "address": "서울특별시 중구 을지로 245, 국립중앙의료원 (을지로6가)",
      "phone": "02-2260-7114",
      "emergency_phone": "02-2276-2114",
      "latitude": 37.56733955813183,
      "longitude": 127.00579539705473,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 5,
          "effective_beds": 5
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        }
      },
      "total_effective_beds": 19,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        6,
        8
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy18",
        "MKioskTy23",
        "MKioskTy26",
        "MKioskTy28"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 14.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI) 기준 총 유효 병상 19개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100013",
      "name": "한양대학교병원",
      "address": "서울특별시 성동구 왕십리로 222-1 (사근동)",
      "phone": "02-2290-8114",
      "emergency_phone": "02-2290-8284",
      "latitude": 37.559944533564746,
      "longitude": 127.04488284061982,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 1,
          "effective_beds": 1
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 1,
          "effective_beds": 1
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 15,
          "effective_beds": 15
        }
      },
      "total_effective_beds": 16,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.6,
      "coverage_level": "MEDIUM",
      "priority_score": 14.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 16개가 남아 있어 후보로 선정됨. (시술 커버리지: 일부 핵심 시술만 가능, 약 60% 충족)"
    },
    {
      "id": "A1100006",
      "name": "강북삼성병원",
      "address": "서울특별시 종로구 새문안로 29 (평동)",
      "phone": "02-2001-2001",
      "emergency_phone": "02-2001-1000",
      "latitude": 37.568497631233825,
      "longitude": 126.96793805451702,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 6,
          "effective_beds": 6
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 6,
          "effective_beds": 6
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 10,
          "effective_beds": 10
        }
      },
      "total_effective_beds": 16,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy12",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.6,
      "coverage_level": "MEDIUM",
      "priority_score": 14.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 16개가 남아 있어 후보로 선정됨. (시술 커버리지: 일부 핵심 시술만 가능, 약 60% 충족)"
    },
    {
      "id": "A1100028",
      "name": "성심의료재단강동성심병원",
      "address": "서울특별시 강동구 성안로 150 (길동)",
      "phone": "02-2224-2114",
      "emergency_phone": "02-2224-2358",
      "latitude": 37.53598408220376,
      "longitude": 127.13526354631517,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 4,
          "effective_beds": 4
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 4,
          "effective_beds": 4
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 11,
          "effective_beds": 11
        }
      },
      "total_effective_beds": 15,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.6,
      "coverage_level": "MEDIUM",
      "priority_score": 13.3,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 15개가 남아 있어 후보로 선정됨. (시술 커버리지: 일부 핵심 시술만 가능, 약 60% 충족)"
    },
    {
      "id": "A1100003",
      "name": "중앙대학교병원",
      "address": "서울특별시 동작구 흑석로 102 (흑석동)",
      "phone": "1800-1114",
      "emergency_phone": "02-6299-1338",
      "latitude": 37.50707428493414,
      "longitude": 126.96079378447554,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 7,
          "effective_beds": 7
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 7,
          "effective_beds": 7
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 8,
          "effective_beds": 8
        }
      },
      "total_effective_beds": 15,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.6,
      "coverage_level": "MEDIUM",
      "priority_score": 13.3,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 15개가 남아 있어 후보로 선정됨. (시술 커버리지: 일부 핵심 시술만 가능, 약 60% 충족)"
    },
    {
      "id": "A1100019",
      "name": "홍익병원",
      "address": "서울특별시 양천구 목동로 225, 홍익병원본관 (신정동)",
      "phone": "02-2693-5555",
      "emergency_phone": "02-2600-0777",
      "latitude": 37.52844147447355,
      "longitude": 126.8636640030062,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 6,
          "effective_beds": 6
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 6,
          "effective_beds": 6
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        }
      },
      "total_effective_beds": 15,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "AORTIC_EMERGENCY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "대동맥 응급(박리/파열)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        6
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "의식 변화 (Altered mental status / syncope)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy2",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 11.6,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 대동맥 응급(박리/파열) 기준 총 유효 병상 15개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100053",
      "name": "한국보훈복지의료공단중앙보훈병원",
      "address": "서울특별시 강동구 진황도로61길 53 (둔촌동)",
      "phone": "02-2225-1111",
      "emergency_phone": "02-2225-1100",
      "latitude": 37.528220900896635,
      "longitude": 127.14671886173552,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 15,
          "effective_beds": 15
        }
      },
      "total_effective_beds": 15,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)"
      ],
      "mkiosk_flags": [
        "MKioskTy11",
        "MKioskTy25",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 11.2,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 15개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100002",
      "name": "건국대학교병원",
      "address": "서울특별시 광진구 능동로 120-1 (화양동)",
      "phone": "1588-1533",
      "emergency_phone": "02-2030-5555",
      "latitude": 37.54084479467721,
      "longitude": 127.0721229093036,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 14,
          "effective_beds": 14
        }
      },
      "total_effective_beds": 14,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy12",
        "MKioskTy13",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 10.5,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 14개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100048",
      "name": "노원을지대학교병원",
      "address": "서울특별시 노원구 한글비석로 68, 을지병원 (하계동)",
      "phone": "02-970-8000",
      "emergency_phone": "02-970-8282",
      "latitude": 37.636442927386746,
      "longitude": 127.07000281991385,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 14,
          "effective_beds": 14
        }
      },
      "total_effective_beds": 14,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        9
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)"
      ],
      "mkiosk_flags": [
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy2",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 10.5,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 14개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100021",
      "name": "삼육서울병원",
      "address": "서울특별시 동대문구 망우로 82 (휘경동)",
      "phone": "02-2244-0191",
      "emergency_phone": "02-2210-3566",
      "latitude": 37.587992001305395,
      "longitude": 127.0653288266823,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 4,
          "effective_beds": 4
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 9,
          "effective_beds": 9
        }
      },
      "total_effective_beds": 13,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        8
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy23",
        "MKioskTy28",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 10,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI), 소화기 내시경(출혈 포함) 기준 총 유효 병상 13개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100041",
      "name": "의료법인서울효천의료재단에이치플러스양지병원",
      "address": "서울특별시 관악구 남부순환로 1636, 양지병원 (신림동)",
      "phone": "02-1877-8875",
      "emergency_phone": "070-4665-9119",
      "latitude": 37.48427507045319,
      "longitude": 126.93253922577287,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 12,
          "effective_beds": 12
        }
      },
      "total_effective_beds": 12,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        8
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy11",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 9,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 12개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100049",
      "name": "희명병원",
      "address": "서울특별시 금천구 시흥대로 244 (시흥동)",
      "phone": "02-804-0002",
      "emergency_phone": "02-809-0122",
      "latitude": 37.45567063464179,
      "longitude": 126.90056251863875,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 1,
          "effective_beds": 1
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        }
      },
      "total_effective_beds": 10,
      "has_any_bed": true,
      "groups_with_beds": [
        "ACS_MI"
      ],
      "groups_with_beds_labels": [
        "심근경색/ACS (응급 PCI)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        6,
        7
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy26",
        "MKioskTy28",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 7.5,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 심근경색/ACS (응급 PCI) 기준 총 유효 병상 10개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100024",
      "name": "명지성모병원",
      "address": "서울특별시 영등포구 도림로 156, 명지성모병원 (대림동)",
      "phone": "02-1899-1475",
      "emergency_phone": "02-829-7800",
      "latitude": 37.4938507104387,
      "longitude": 126.89925446922592,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 2,
          "effective_beds": 2
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        }
      },
      "total_effective_beds": 10,
      "has_any_bed": true,
      "groups_with_beds": [
        "AORTIC_EMERGENCY"
      ],
      "groups_with_beds_labels": [
        "대동맥 응급(박리/파열)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        6
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "의식 변화 (Altered mental status / syncope)"
      ],
      "mkiosk_flags": [
        "MKioskTy2",
        "MKioskTy3",
        "MKioskTy4"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 7.5,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 대동맥 응급(박리/파열) 기준 총 유효 병상 10개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100044",
      "name": "녹색병원",
      "address": "서울특별시 중랑구 사가정로49길 53 (면목동)",
      "phone": "02-490-2000",
      "emergency_phone": "02-490-2113",
      "latitude": 37.58362083896108,
      "longitude": 127.08605546969358,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 1,
          "effective_beds": 1
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 1,
          "effective_beds": 1
        }
      },
      "total_effective_beds": 7,
      "has_any_bed": true,
      "groups_with_beds": [
        "AORTIC_EMERGENCY",
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "대동맥 응급(박리/파열)",
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)"
      ],
      "mkiosk_flags": [
        "MKioskTy11",
        "MKioskTy4",
        "MKioskTy7",
        "MKioskTy9"
      ],
      "coverage_score": 0.4,
      "coverage_level": "LOW",
      "priority_score": 5.4,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 대동맥 응급(박리/파열), 소화기 내시경(출혈 포함) 기준 총 유효 병상 7개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 40% 충족)"
    },
    {
      "id": "A1100016",
      "name": "인제대학교상계백병원",
      "address": "서울특별시 노원구 동일로 1342, 상계백병원 (상계동)",
      "phone": "02-950-1114",
      "emergency_phone": "02-950-1119",
      "latitude": 37.6485812672986,
      "longitude": 127.06311619032103,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 6,
          "effective_beds": 6
        }
      },
      "total_effective_beds": 6,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)"
      ],
      "mkiosk_flags": [
        "MKioskTy11",
        "MKioskTy2",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 4.5,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 6개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    },
    {
      "id": "A1100012",
      "name": "학교법인가톨릭학원가톨릭대학교서울성모병원",
      "address": "서울특별시 서초구 반포대로 222 (반포동)",
      "phone": "0215881511",
      "emergency_phone": "02-2258-2370",
      "latitude": 37.501800804785276,
      "longitude": 127.00472725970137,
      "procedure_beds": {
        "ACS_MI": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "ACS_STROKE": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "AORTIC_EMERGENCY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "BRONCHOSCOPY": {
          "api_beds": 0,
          "effective_beds": 0
        },
        "GI_ENDOSCOPY": {
          "api_beds": 6,
          "effective_beds": 6
        }
      },
      "total_effective_beds": 6,
      "has_any_bed": true,
      "groups_with_beds": [
        "GI_ENDOSCOPY"
      ],
      "groups_with_beds_labels": [
        "소화기 내시경(출혈 포함)"
      ],
      "supported_complaints": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10
      ],
      "supported_complaint_labels": [
        "가슴 통증 (Chest pain)",
        "호흡곤란 (Dyspnea / Respiratory distress)",
        "신경학적 증상 (Stroke-like symptoms: 편마비, 말어눌함, 경련)",
        "복통 / 소화기 증상 (Abdominal pain / GI bleeding / vomiting)",
        "출혈 (External bleeding / hematemesis / melena)",
        "의식 변화 (Altered mental status / syncope)",
        "외상 (Trauma: 교통사고, 낙상, 절단, 화상 포함)",
        "산부인과 응급 (OB-GYN emergency: 분만, 산과/부인과 통증)",
        "소아 응급 (Pediatric acute illness: 열, 경련, 탈수 등)",
        "정신과적 응급 (Psychiatric emergency: 자살위험, 폭력성, 급성정신병)"
      ],
      "mkiosk_flags": [
        "MKioskTy1",
        "MKioskTy10",
        "MKioskTy11",
        "MKioskTy12",
        "MKioskTy13",
        "MKioskTy14",
        "MKioskTy15",
        "MKioskTy16",
        "MKioskTy17",
        "MKioskTy18",
        "MKioskTy2",
        "MKioskTy20",
        "MKioskTy21",
        "MKioskTy22",
        "MKioskTy23",
        "MKioskTy24",
        "MKioskTy25",
        "MKioskTy26",
        "MKioskTy27",
        "MKioskTy28",
        "MKioskTy3",
        "MKioskTy4",
        "MKioskTy5",
        "MKioskTy6",
        "MKioskTy7",
        "MKioskTy8",
        "MKioskTy9"
      ],
      "coverage_score": 0.2,
      "coverage_level": "LOW",
      "priority_score": 4.5,
      "reason_summary": "KTAS 2, 주증상 '호흡곤란 (Dyspnea / Respiratory distress)' 환자에 대해 소화기 내시경(출혈 포함) 기준 총 유효 병상 6개가 남아 있어 후보로 선정됨. (시술 커버리지: 필수 시술 중 일부만 가능, 약 20% 충족)"
    }
  ]
}
```