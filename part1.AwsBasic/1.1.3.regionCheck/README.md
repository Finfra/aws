# 1.1.3: 리전 확인과 이동

## 실습 목표
* AWS 리전 개념 이해
* 리전 간 이동 방법 익히기
* 한국 리전과 유럽 리전 차이점 확인

## AWS 리전 기본 개념
* **리전**: 지리적으로 분리된 AWS 데이터 센터 그룹
* **가용 영역(AZ)**: 리전 내 물리적으로 분리된 데이터 센터
* **엣지 로케이션**: CloudFront CDN을 위한 캐시 서버

## 실습 단계

### Step 1: 현재 리전 확인
* 화면 오른쪽 상단에서 현재 리전 확인
* 서울 리전: `ap-northeast-2`
* 도쿄 리전: `ap-northeast-1`

### Step 2: 리전 간 이동 실습
* **서울 리전 EC2 대시보드**: 
  - https://ap-northeast-2.console.aws.amazon.com/ec2/home?region=ap-northeast-2#Home:

* **아일랜드 리전 EC2 대시보드**:
  - https://eu-west-1.console.aws.amazon.com/ec2/home?region=eu-west-1#Home:

### Step 3: 리전별 차이점 확인
* 각 리전에서 사용 가능한 서비스 확인
* 인스턴스 타입별 가용성 확인
* 가격 차이 비교

### Step 4: 리전 선택 기준
* **지연 시간**: 사용자와의 물리적 거리
* **법적 요구사항**: 데이터 저장 위치 규제
* **서비스 가용성**: 특정 리전에서만 제공되는 서비스
* **비용**: 리전별 가격 차이

## 한국에서 주로 사용하는 리전
* **ap-northeast-2 (서울)**: 최저 지연시간
* **ap-northeast-1 (도쿄)**: 서울 리전 장애 시 백업
* **us-east-1 (버지니아 북부)**: 글로벌 서비스, 최저 비용

## 주의사항
* 리전 간 데이터 전송 시 비용 발생
* 일부 서비스는 특정 리전에서만 제공
* 법적 규제로 인한 데이터 위치 제한 고려

## 관련 문서
* [AWS 글로벌 인프라](https://aws.amazon.com/about-aws/global-infrastructure/)
* [리전별 서비스 가용성](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/)
