import web
import random
import json
from datetime import datetime

# URL 라우팅 설정
urls = (
    '/', 'RandomValue'
)

# 랜덤 값과 타임스탬프를 출력하는 클래스
class RandomValue:
    def GET(self):
        random_value = random.randint(1, 100)  # 1부터 100 사이의 랜덤 값 생성
        timestamp = datetime.now().isoformat()  # ISO 8601 형식의 타임스탬프 생성
        web.header('Content-Type', 'application/json')  # 응답 헤더 설정
        return json.dumps({"timestamp": timestamp, "val": random_value})  # JSON 데이터 반환

# 애플리케이션 실행
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()