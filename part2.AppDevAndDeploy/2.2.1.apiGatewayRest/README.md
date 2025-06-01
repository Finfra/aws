# 2.2.1: API Gateway로 REST API 생성

## 실습 목표
* API Gateway를 사용하여 REST API 생성하기
* 백엔드 서비스와 연동하기
* API 테스트 및 배포하기

## API Gateway 기본 개념
* **REST API**: RESTful 웹 서비스를 위한 API
* **리소스**: API의 경로 (ex: /users, /orders)
* **메서드**: HTTP 메서드 (GET, POST, PUT, DELETE)
* **스테이지**: API 버전 관리를 위한 배포 환경

## 실습 단계

### Step 1: 백엔드 서비스 준비 (netcat 사용)
* EC2 인스턴스(i1)에 SSH 접속
* 보안 그룹에 4444 포트 추가
* netcat으로 간단한 서비스 실행:
```bash
# 터미널 1: 서비스 대기
nc -l 0.0.0.0 4444
```

```
# 터미널 2: 테스트 연결[단, 원격에서 연결하려면 양방향 통신 필요]
nc 127.0.0.1 4444
# 메시지 입력 후 Enter
ctl+c
```



### Step 2: API Gateway 생성
* API Gateway 서비스로 이동
* https://ap-northeast-2.console.aws.amazon.com/apigateway/main/apis?region=ap-northeast-2
* "Create API" > REST API > "Build" 클릭

#### API 기본 설정
* **API name**: `myRestAPI`
* **Description**: `Simple REST API for testing`
* **Endpoint Type**: Regional

### Step 3: 리소스 생성
* "Create resource" 클릭
* **Resource path**: `/`
* **Resource name**: `items`
* **Enable CORS**: 체크 (웹 브라우저 테스트용)

### Step 4: 메서드 생성
* `/items` 리소스 선택
* "Create method" 클릭
* **Method type**: GET
* **Integration type**: HTTP
* **HTTP method**: GET
* **Endpoint URL**: `http://[i1-public-dns]:4444/items`
* "Create method" 클릭

### Step 5: API 테스트
* 생성된 GET 메서드 선택
* "Test" 탭 클릭
* i1서버에 다시 아래 명령 실행
```
nc -l 0.0.0.0 4444
```
* "Test" 버튼 클릭
* i1 콘솔에서 요청 수신 확인
* AWS 콘솔에서 응답 상태 확인

#### 테스트 결과 예시
* **Status**: 504 Gateway Timeout (netcat 서비스 특성상 정상)
* i1 서버에서 GET 요청 수신 로그 확인

### Step 6: API 배포
* 상단 "Deploy API" 버튼 클릭
* **Deployment stage**: New stage
* **Stage name**: `dev`
* **Description**: `Development stage`
* "Deploy" 클릭

### Step 7: 배포된 API 테스트
* i1서버에 다시 아래 명령 실행
```
nc -l 0.0.0.0 4444
```
* **Invoke URL** 복사 : dev → / → items → GET 
* 웹 브라우저에서 `[Invoke-URL]/items` 접속
* i1 서버에서 실제 HTTP 요청 수신 확인

#### netcat 서비스 재시작
```bash
# i1에서 서비스 재시작
nc -l 4444
```

### Step 8: curl을 이용한 API 테스트
```bash
# 로컬 또는 다른 서버에서 테스트
curl -X GET https://[api-id].execute-api.ap-northeast-2.amazonaws.com/dev/items

# 헤더 포함 테스트
curl -v https://[api-id].execute-api.ap-northeast-2.amazonaws.com/dev/items
```

## API Gateway 고급 설정

### 요청/응답 변환
* **Mapping Templates**: 요청/응답 데이터 변환
* **Models**: API 스키마 정의
* **Validators**: 요청 데이터 검증

### 스로틀링 설정
* **Rate limiting**: 초당 요청 수 제한
* **Burst limiting**: 순간 요청 수 제한

### 캐싱 설정
* **TTL**: 캐시 유지 시간
* **Cache key**: 캐시 키 설정

## 실제 백엔드 서비스 연동 예시

### Python Flask 서비스
* Setting: i1
```
export DEBIAN_FRONTEND=noninteractive
sudo apt update
sudo apt install python3-pip -y
sudo pip install flask
```
```bash
cat > app.py <<EOF
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify({
        'items': [
            {'id': 1, 'name': 'Item 1'},
            {'id': 2, 'name': 'Item 2'}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444)
EOF
python3 app.py
```

### Node.js Express 서비스
```javascript
const express = require('express');
const app = express();

app.get('/items', (req, res) => {
    res.json({
        items: [
            {id: 1, name: 'Item 1'},
            {id: 2, name: 'Item 2'}
        ]
    });
});

app.listen(4444, '0.0.0.0', () => {
    console.log('Server running on port 4444');
});
```

## 모니터링 및 로깅
* CloudWatch Logs를 통한 API 호출 로그 확인
* CloudWatch Metrics를 통한 성능 모니터링
* X-Ray를 통한 분산 추적

## 비용 최적화
* 캐싱을 통한 백엔드 호출 최소화
* 압축 설정으로 데이터 전송량 감소
* 적절한 스로틀링으로 과도한 사용 방지

## 주의사항
* API Gateway는 29초 타임아웃 제한
* 10MB 페이로드 크기 제한
* CORS 설정 시 브라우저 보안 정책 고려
* HTTP vs HTTPS 설정 주의

## 관련 문서
* [API Gateway REST API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-rest-api.html)
* [API Gateway 배포](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-deploy-api.html)
