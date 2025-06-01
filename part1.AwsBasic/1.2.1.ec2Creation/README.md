# 1.2.1: 수동으로 EC2 인스턴스 생성

## 실습 목표
* AWS EC2 인스턴스를 수동으로 생성하는 과정 익히기
* AMI, 인스턴스 타입, 키 페어, 스토리지 설정 이해하기

## 실습 단계

### Step 1: EC2 서비스 접속
* https://ap-northeast-2.console.aws.amazon.com/ec2/home?region=ap-northeast-2#LaunchInstances:
* "Launch instances" 버튼 클릭

### Step 2: AMI 선택
* **Amazon Machine Image (AMI)**: 인스턴스의 운영체제 템플릿
* 권장: Ubuntu Server 22.04 LTS
* Free tier eligible 확인

### Step 3: 인스턴스 타입 선택
* **t2.micro**: Free tier (1 vCPU, 1GB RAM)
* **t2.small**: 실습 권장 (1 vCPU, 2GB RAM) 
* **t3.medium**: 성능 필요 시 (2 vCPU, 4GB RAM)

### Step 4: 키 페어 설정
* 새 키 페어 생성: `mykey`
* 윈도우 사용자의 경우 `.ppk` 파일 다운로드 및 안전한 위치에 저장
* 맥의 경우 `.pem` 파일 다운로드 및 안전한 위치에 저장
  - 권한 설정: `chmod 400 mykey.pem`

### Step 5: 네트워크 설정
* **VPC**: 기본 VPC 사용
* **Subnet**: Public subnet 선택
* **Auto-assign public IP**: Enable

### Step 6: 보안 그룹 설정
* 새 보안 그룹 생성 또는 기존 그룹 선택
* SSH (22번 포트) 허용
* 필요 시 추가 포트 개방

### Step 7: 스토리지 설정
* **Root volume**: 8GB (기본)
* **EBS Volume Type**: gp3 (범용 SSD)
* 실습 권장: 20GB 

### Step 8: 인스턴스 시작
* 설정 검토 후 "Launch instance" 클릭
* 인스턴스 상태 확인: Running

## 생성 후 확인사항
* Public IP 주소 할당 확인
* Security Group 설정 확인
* Instance State: Running
* Status Checks: 2/2 checks passed

## 주의사항
* 키 페어 파일은 분실 시 복구 불가
* 인스턴스 중지/시작 시 Public IP 변경됨
* Free tier 한도 초과 시 과금 발생

## 관련 문서
* [EC2 인스턴스 시작](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html)
* [EC2 인스턴스 타입](https://aws.amazon.com/ec2/instance-types/)
