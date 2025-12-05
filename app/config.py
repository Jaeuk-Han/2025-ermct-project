# app/config.py
import os
from dotenv import load_dotenv

# .env 로딩
load_dotenv()

ERMCT_SERVICE_KEY = os.getenv("ERMCT_SERVICE_KEY")

if not ERMCT_SERVICE_KEY:
    raise RuntimeError("ERMCT_SERVICE_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
