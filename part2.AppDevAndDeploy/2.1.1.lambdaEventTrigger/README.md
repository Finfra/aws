# 2.1.1: Lambda 이벤트 트리거 설정

## 실습 목표
* Lambda 함수 생성 및 기본 설정
* S3 이벤트 트리거 설정
* CloudWatch 로그를 통한 함수 실행 모니터링

## Lambda 기본 개념
* **서버리스 컴퓨팅**: 서버 관리 없이 코드 실행
* **이벤트 기반**: 다양한 AWS 서비스에서 발생하는 이벤트에 응답
* **자동 스케일링**: 요청량에 따라 자동으로 확장/축소

## 실습 단계

### Step 1: Lambda 함수 생성
* Lambda 서비스로 이동
* "Create a function" 클릭
* **함수 이름**: `processS3Event`
* **런타임**: Python 3.12
* **Execution role**: Create a new role from AWS policy templates
  - **Role name**: `s3read`
  - **Policy templates**: Amazon S3 object read-only permissions

### Step 2: Lambda 함수 코드 작성
```python
import json
import urllib.parse

def lambda_handler(event, context):
   print("Lambda function started")
   
   records = event.get('Records', [])
   processed_files = []
   
   for record in records:
       bucket_name = record['s3']['bucket']['name']
       object_key = urllib.parse.unquote_plus(
           record['s3']['object']['key'], encoding='utf-8'
       )
       object_size = record['s3']['object']['size']
       
       print(f"Processing file: {object_key}")
       print(f"Bucket: {bucket_name}, Size: {object_size} bytes")
       
       # 파일 타입별 처리
       if object_key.endswith(('.jpg', '.png')):
           print("Image file detected - processing...")
       elif object_key.endswith('.txt'):
           print("Text file detected - processing...")
       
       # 처리된 파일명을 리스트에 추가
       processed_files.append(object_key)
   
   return {
       'statusCode': 200,
       'body': json.dumps({
           'message': 'S3 Event Processed Successfully!!',
           'processed_files_count': len(records),
           'processed_files': processed_files
       })
   }
```
* 코드소스의 사이드바의 S3UploadTrigger의 편집 버튼을 누르고 S3UploadTrigger.json의 내용을 붙여넣고 테스트 가능함.


### Step 3: 테스트 이벤트 구성
* Test 탭 클릭
* **Event name**: `s3-test-event`
* **Template**: `s3-put`
* Test 실행 및 결과 확인

### Step 4: S3 버킷 생성
* S3 서비스로 이동
* "Create bucket" 클릭
* **Bucket name**: `lambda-trigger-실습용이름` (고유한 이름)
* **Region**: Asia Pacific (Seoul) ap-northeast-2
* 기본 설정으로 생성

### Step 5: S3 이벤트 알림 설정
* 생성한 S3 버킷 선택
* Properties 탭 > Event notifications
* "Create event notification" 클릭

#### 이벤트 알림 설정
* **Event name**: `S3UploadTrigger`
* **Prefix**: `uploads/` (선택사항)
* **Suffix**: `.jpg` (선택사항)
* **Event types**: 
  - s3:ObjectCreated:Put
  - s3:ObjectCreated:Post
* **Destination**: Lambda function
* **Lambda function**: `processS3Event`

### Step 6: 권한 설정 확인
* Lambda 함수의 실행 역할에 S3 읽기 권한 확인
* S3 버킷에서 Lambda 함수 호출 권한 자동 생성 확인

### Step 7: 실습 테스트

#### 파일 업로드 테스트
* S3 버킷에 파일 업로드:
  - `uploads/test-image.jpg`
  - `uploads/sample.txt`

#### Lambda 실행 확인
* Lambda 함수 > Monitor 탭
* "View CloudWatch Logs" 클릭
* 로그 스트림에서 실행 결과 확인

#### 예상 로그 출력
```
START RequestId: xxx-xxx-xxx Version: $LATEST
Lambda function started
Processing file: uploads/test-image.jpg
Bucket: lambda-trigger-yourbucket
Size: 45678 bytes
Image file detected - processing...
END RequestId: xxx-xxx-xxx
REPORT RequestId: xxx-xxx-xxx Duration: 245.67 ms Billed Duration: 246 ms Memory Size: 128 MB Max Memory Used: 54 MB
```

## 추가 트리거 설정 (선택사항)

### CloudWatch Events/EventBridge 트리거
* 시간 기반 스케줄링
* cron 표현식 사용

### DynamoDB 트리거
* 테이블 변경 시 자동 실행
* 스트림 설정 필요

### API Gateway 트리거
* HTTP 요청에 응답하는 Lambda 함수
* RESTful API 구현

## 모니터링 및 디버깅
* CloudWatch Logs를 통한 실시간 로그 확인
* X-Ray를 통한 분산 추적
* CloudWatch Metrics를 통한 성능 모니터링

## 주의사항
* S3 버킷명은 전역적으로 고유해야 함
* Lambda 함수 타임아웃 설정 확인 (기본 3초)
* 동시 실행 제한 고려
* 비용 최적화를 위한 메모리 설정 조정

## 관련 문서
* [Lambda 이벤트 소스](https://docs.aws.amazon.com/lambda/latest/dg/invocation-eventsourcemapping.html)
* [S3 이벤트 알림](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html)
