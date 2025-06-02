# 1.2.3: SSH Client 연결

## 실습 목표
* SSH를 이용하여 EC2 인스턴스에 접속하기
* PuTTY 사용법 익히기 (Windows)
* 터미널 사용법 익히기 (macOS/Linux)

## SSH 기본 개념
* **SSH (Secure Shell)**: 안전한 원격 접속 프로토콜
* **Public Key**: EC2에 저장되는 공개키
* **Private Key**: 로컬에 저장되는 개인키 (.pem 파일)

## 실습 단계

### Step 1: EC2 인스턴스 정보 확인
* EC2 대시보드에서 인스턴스 선택
* **Public IPv4 address** 복사
* **Key pair name** 확인

### Step 2-A: Windows 환경 (PuTTY 사용)

#### PuTTY 설치 및 설정
* PuTTY 다운로드: https://www.putty.org/
* PuTTYgen을 사용하여 .pem 파일을 .ppk로 변환:
  - PuTTYgen 실행
  - Load > .pem 파일 선택
  - Save private key > .ppk 파일로 저장


#### PuTTY 연결 설정
* **Host Name**: ubuntu@[EC2-Public-IP]
* **Port**: 22
* **Connection Type**: SSH
* **Auth > Private key file**: .ppk 파일 선택
* Session 저장 후 Open
* pem으로 ssh접속(잘못 받은 분들만) cmd.exe실행
```
ssh -i pem파일 ubuntu@퍼블릭아이피
```

### Step 2-B: macOS/Linux 환경 (터미널 사용)

#### 키 파일 권한 설정
```bash
chmod 400 ~/Downloads/mykey.pem
```

#### SSH 연결
```bash
ssh -i ~/Downloads/mykey.pem ubuntu@[EC2-Public-IP]
```

#### SSH Config 파일 설정 (선택사항)
```bash
# ~/.ssh/config 파일 생성
Host i1
    HostName [EC2-Public-IP]
    User ubuntu
    IdentityFile ~/Downloads/mykey.pem
    
# 간단한 연결
ssh i1
```

### Step 3: 연결 확인
* 성공적으로 연결되면 Ubuntu 프롬프트 확인
* 기본 명령어 테스트:
```bash
whoami
pwd
ls -la
df -h
free -m
```

### Step 4: EIP (Elastic IP) 설정

#### EIP 생성
* https://ap-northeast-2.console.aws.amazon.com/ec2/home?region=ap-northeast-2#Addresses:
* "Allocate Elastic IP address" 클릭
* 할당 완료

#### EIP 인스턴스에 연결
* 생성된 EIP 선택
* Actions > Associate Elastic IP address
* 대상 인스턴스 선택 후 Associate

#### 연결 확인
* 새로운 EIP로 SSH 재연결
* Public IP가 고정됨을 확인

## 연결 문제 해결

### 일반적인 오류와 해결방법

| 오류                         | 원인             | 해결방법                              |
| ---------------------------- | ---------------- | ------------------------------------- |
| Connection timeout           | 보안 그룹 설정   | SSH(22) 포트 허용 확인                |
| Permission denied            | 키 파일 권한     | chmod 400 적용                        |
| Host key verification failed | known_hosts 충돌 | ~/.ssh/known_hosts에서 해당 항목 삭제 |
| Wrong user                   | 잘못된 사용자명  | Ubuntu AMI는 'ubuntu' 사용            |

### 연결 테스트 명령어
```bash
# 네트워크 연결 테스트
ping -c 4 8.8.8.8

# 포트 열림 확인 (로컬에서 실행)
telnet [EC2-Public-IP] 22

# SSH 상세 로그
ssh -v -i mykey.pem ubuntu@[EC2-Public-IP]
```

## 보안 강화 방법
* SSH 포트 변경 (22 → 다른 포트)
* SSH 키 기반 인증만 허용
* fail2ban 설치로 brute force 공격 방지
* 특정 IP 대역에서만 SSH 접근 허용

## 관련 문서
* [EC2 인스턴스 연결](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstances.html)
* [SSH 키 페어](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)
