# 2.2.2. Lambda와 통합된 API 배포

## 개요
API Gateway와 Lambda를 통합하여 서버리스 REST API를 구축하는 실습

## 실습 목표
* Lambda 함수와 API Gateway 통합
* 프록시 통합 설정
* API 응답 형식 최적화
* 통합 테스트 및 배포

## 실습 단계
### Python Flask 서비스
* Setting: i1
```
export DEBIAN_FRONTEND=noninteractive
sudo apt update
sudo apt install python3-pip -y
sudo pip install flask

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
* 브라우저에서 https://[api-id].execute-api.ap-northeast-2.amazonaws.com/dev/items 에 접속

### Node.js Express 서비스 예제
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

