# 1.2.2: EC2 보안 그룹 설정 및 연결

## 실습 목표
* 보안 그룹의 개념과 역할 이해하기
* 인바운드/아웃바운드 규칙 설정하기
* 기존 인스턴스에 보안 그룹 변경하기

## 보안 그룹 기본 개념
* **보안 그룹**: 인스턴스 레벨의 방화벽
* **인바운드 규칙**: 인스턴스로 들어오는 트래픽 제어
* **아웃바운드 규칙**: 인스턴스에서 나가는 트래픽 제어
* **Stateful**: 허용된 인바운드 트래픽의 응답은 자동 허용

## 실습 단계

### Step 1: 보안 그룹 생성
* https://ap-northeast-2.console.aws.amazon.com/ec2/home?region=ap-northeast-2#SecurityGroups:
* "Create security group" 클릭
* **Security group name**: `web-server-sg`
* **Description**: `Security group for web server`
* **VPC**: 기본 VPC 선택

### Step 2: 인바운드 규칙 설정
* **SSH (22)**: 관리용 접속
  - Type: SSH
  - Port: 22
  - Source: My IP (또는 0.0.0.0/0 - 주의 필요)

* **HTTP (80)**: 웹 서비스용
  - Type: HTTP
  - Port: 80
  - Source: 0.0.0.0/0

* **HTTPS (443)**: 보안 웹 서비스용
  - Type: HTTPS
  - Port: 443
  - Source: 0.0.0.0/0

* **Custom TCP**: 애플리케이션 포트
  - Type: Custom TCP
  - Port: 8080, 9411
  - Source: 0.0.0.0/0

### Step 3: 아웃바운드 규칙 확인
* 기본적으로 모든 아웃바운드 트래픽 허용
* 필요 시 제한적 규칙 설정

### Step 4: 기존 인스턴스에 보안 그룹 적용
* EC2 인스턴스 선택
* Actions > Security > Change security groups
* 새로 생성한 보안 그룹 선택
* "Save" 클릭

## 보안 그룹 vs NACL

| 구분      | 보안 그룹      | NACL      |
| --------- | -------------- | --------- |
| 레벨      | 인스턴스       | 서브넷    |
| 상태      | Stateful       | Stateless |
| 규칙 유형 | 허용만         | 허용/거부 |
| 적용 순서 | 모든 규칙 적용 | 번호 순서 |

## 실습 검증
* SSH 접속 테스트
* 웹 서버 설치 후 HTTP 접속 테스트
```bash
sudo apt update
sudo apt install -y nginx
sudo systemctl start nginx
curl http://localhost
```

## 보안 모범 사례
* 최소 권한 원칙 적용
* 특정 IP 대역으로 SSH 접근 제한
* 불필요한 포트 개방 금지
* 정기적인 보안 그룹 검토

## 주의사항
* 0.0.0.0/0 사용 시 전 세계 접근 허용
* SSH 포트 변경 고려 (보안 강화)
* 규칙 변경 시 즉시 적용됨

## 관련 문서
* [보안 그룹 규칙](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html)
* [네트워크 보안](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html)
