import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()
TMAP_APP_KEY = os.getenv("TMAP_APP_KEY")

if not TMAP_APP_KEY:
    raise ValueError("TMAP_APP_KEY가 .env 파일에서 로드되지 않았습니다.")

# Tmap 비동기 호출
async def get_tmap_distance_async(start_lat, start_lon, end_lat, end_lon):
    url = "https://apis.openapi.sk.com/tmap/routes?version=1&format=json"

    headers = {
        "appKey": TMAP_APP_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "startX": str(start_lon),
        "startY": str(start_lat),
        "endX": str(end_lon),
        "endY": str(end_lat),
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "searchOption": "0"
    }

    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            response = await client.post(url, json=body, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            print(
                "[TMAP] request failed "
                f"start=({start_lat},{start_lon}) end=({end_lat},{end_lon}) error={exc}"
            )
            return None, None

        try:
            distance = data["features"][0]["properties"]["totalDistance"]
            duration = data["features"][0]["properties"]["totalTime"]
            return distance, duration
        except Exception:
            print(
                "[TMAP] unexpected response "
                f"start=({start_lat},{start_lon}) end=({end_lat},{end_lon}) data={data}"
            )
            return None, None

# 거리 계산 (JSON 병원 리스트 입력)
async def calculate_all_distances_async(user_lat, user_lon, hospitals):
    
    tasks = [
        get_tmap_distance_async(user_lat, user_lon, h["latitude"], h["longitude"])
        for h in hospitals
    ]

    results_raw = await asyncio.gather(*tasks)

    results = []

    for h, (dist, duration) in zip(hospitals, results_raw):
        if dist is None:
            continue
        
        results.append({
            "name": h["name"],
            "distance": dist,
            "duration_sec": duration,
            "reason_summary": h.get("reason_summary", "정보 없음")
        })

    print(
        "[TMAP] distance results "
        f"requested={len(hospitals)} resolved={len(results)}"
    )
    return results

# TOP3 반환
def get_top3(results):
    return sorted(results, key=lambda x: x["distance"])[:3]
