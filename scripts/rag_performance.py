import requests
import pandas as pd
import re

URL = "http://127.0.0.1:8000/api/ktas/predict-text"

raw_texts = pd.read_csv('data/ER_Call_Scenarios_Custom_KTAS.csv')
print(raw_texts)
print(raw_texts.shape)

# raw_texts = raw_texts.iloc[:152, :2] # 1 to 3
# raw_texts = raw_texts.iloc[:5, :2] # test
raw_texts = raw_texts.iloc[:192, :2] # full test, 1 to 5
# raw_texts = raw_texts.iloc[:24, :2] # semi test
print(len(raw_texts))
print(raw_texts.shape)
print(raw_texts)

results = []

# raw_texts의 첫번째 행부터 각 행에 대해 API 호출하여 KTAS 예측 결과를 얻고, 결과를 리스트에 저장
for idx, row in enumerate(raw_texts.itertuples()):
        
    # 디버깅용
    print(f"processing {idx+1}")
    # print(idx)
    print(row[1])
    # print(row[2])
    response = requests.post(
        URL,
        json={
            "text": row[2]
        }
    )

    data = response.json()
    print(data["ktas_options"][0]["ktas"], data["ktas_options"][0]["confidence"], data["ktas_options"][0]["reason"])

    results.append({
        "index": row[1],
        "ktas": data["ktas_options"][0]["ktas"],
        "confidence": data["ktas_options"][0]["confidence"],
        "reason": data["ktas_options"][0]["reason"]
    })



# 5. 결과 출력
for item in results:
    print("=" * 50)
    print("입력:", item["index"])
    print("결과:", item["ktas"])
    print("신뢰도:", item["confidence"])
    print("이유:", item["reason"])

df = pd.DataFrame(results)

df.to_csv(
    "data/full_test_rag_performance_test_1to5_geminipromts_gpt5_large.csv",
    index=False,
    encoding="utf-8-sig"
)
