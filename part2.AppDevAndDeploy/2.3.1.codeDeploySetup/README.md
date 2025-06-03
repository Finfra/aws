# 2.3.1: CodeDeploy 설정 및 배포 테스트

## 실습 목표
* CodeDeploy 서비스 이해 및 설정
* EC2 인스턴스에 CodeDeploy Agent 설치
* 기본 배포 파이프라인 구성
* 간단한 애플리케이션 배포 테스트

## CodeDeploy 기본 개념
* **Application**: 배포 단위의 논리적 그룹
* **Deployment Group**: 배포 대상 인스턴스 그룹
* **Deployment Configuration**: 배포 전략 및 설정
* **Revision**: 배포할 애플리케이션 버전

## 실습 전 준비사항
* EC2 인스턴스 실행 중 (i1)
* IAM 역할 및 사용자 설정
* S3 버킷 생성 (배포 아티팩트 저장용)

## 실습 단계

### Step 1: IAM 역할 생성

#### CodeDeploy 서비스 역할
* IAM > Roles > Create role
* **Trusted entity**: AWS service → "Next"
* **Service or use case**: CodeDeploy → "Next"
* **Permissions Policy**: AWSCodeDeployRole 확인 → "Next"
* **Role name**: `CodeDeployServiceRole` → "Create role"

#### EC2 인스턴스 역할
* IAM > Roles > Create role
* **Trusted entity**: AWS service → "Next"
* **Service or use case**: EC2 → "Next"
* **Policies**: 
  - AmazonS3ReadOnlyAccess
  - CloudWatchLogsFullAccess
     → "Next"
* **Role name**: `CodeDeployInstanceProfile` → "Create role"

### Step 2: EC2 인스턴스에 IAM 역할 연결
* EC2 > Instances > 인스턴스 선택
* Actions > Security > Modify IAM role
* **IAM role**: CodeDeployInstanceProfile

### Step 3: EC2에 CodeDeploy Agent 설치
```bash
# i1 인스턴스에 SSH 접속 후 실행
sudo apt update
sudo apt install -y ruby wget

# CodeDeploy Agent 다운로드 및 설치
cd /home/ubuntu
wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto

# Agent 상태 확인
sudo service codedeploy-agent start
sudo service codedeploy-agent status
```

### Step 4: 샘플 애플리케이션 준비
```bash
# 애플리케이션 디렉토리 생성
mkdir -p ~/sample-app
cd ~/sample-app

# 간단한 웹 애플리케이션 생성
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>CodeDeploy Test App v1.0</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        .container { text-align: center; }
        .version { color: #007bff; font-size: 24px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to CodeDeploy Test App</h1>
        <p class="version">Version 1.0</p>
        <p>Deployed with AWS CodeDeploy</p>
    </div>
</body>
</html>
EOF

# CodeDeploy 설정 파일 생성
cat > appspec.yml << 'EOF'
version: 0.0
os: linux
files:
  - source: /
    destination: /usr/share/nginx/html
    overwrite: yes
permissions:
  - object: /usr/share/nginx/html
    pattern: "**"
    owner: www-data
    group: www-data
    mode: 644
hooks:
  BeforeInstall:
    - location: scripts/install_dependencies.sh
      timeout: 300
      runas: root
  ApplicationStart:
    - location: scripts/start_server.sh
      timeout: 300
      runas: root
  ApplicationStop:
    - location: scripts/stop_server.sh
      timeout: 300
      runas: root
EOF

# 스크립트 디렉토리 생성
mkdir -p scripts

# 의존성 설치 스크립트
cat > scripts/install_dependencies.sh << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y nginx
EOF

# 서버 시작 스크립트
cat > scripts/start_server.sh << 'EOF'
#!/bin/bash
systemctl start nginx
systemctl enable nginx
EOF

# 서버 중지 스크립트
cat > scripts/stop_server.sh << 'EOF'
#!/bin/bash
systemctl stop nginx || true
EOF

# 스크립트에 실행 권한 부여
chmod +x scripts/*.sh

# 배포 패키지 생성
zip -r sample-app-v1.zip . -x "*.git*"
```

### Step 5: S3에 배포 아티팩트 업로드
```bash
# S3 버킷 생성 (CLI 사용)
aws s3 mb s3://codedeploy-bucket-kitri-자기번호

# 배포 패키지 업로드
aws s3 cp sample-app-v1.zip s3://codedeploy-bucket-kitri-자기번호/
```

### Step 6: CodeDeploy 애플리케이션 생성
* CodeDeploy Applications로 이동 : https://console.aws.amazon.com/codesuite/codedeploy/applications
* Applications > Create application
* **Application name**: `SampleWebApp`
* **Compute platform**: EC2/On-premises
* → "Create Application

### Step 7: 배포 그룹 생성
* SampleWebApp > "Create deployment group"
* **Deployment group name**: `SampleWebApp-DeploymentGroup`
* **Service role**: CodeDeployServiceRole
* **Deployment type**: In-place
* **Environment configuration**: Amazon EC2 instances
* **Tag filters**: 
  - Key: Name, Value: i1 (또는 인스턴스 태그에 맞게)
* **Install AWS CodeDeploy Agent**: Never (이미 설치함)
* Deployment settings
 → **Deployment configuration**: CodeDeployDefault.AllAtOneTime
* Enable load balancing 체크 제거 
* "Create deployment group" 

### Step 8: 배포 실행
* Applications에서 SampleWebApp-DeploymentGroup선택 → Create deployment 
* **Application**: SampleWebApp
* **Deployment group**: SampleWebApp-DeploymentGroup
* **Revision type**: My application is stored in Amazon S3
* **Revision location**: s3://codedeploy-bucket-kitri-자기번호/sample-app-v1.zip
* **Deployment description**: Initial deployment v1.0
* → Create Deployment

### Step 9: 배포 모니터링 및 검증
* 배포 진행 상황 실시간 확인
* 각 단계별 로그 확인:
  - BeforeInstall
  - Download
  - Install
  - ApplicationStart

### Step 10: 결과 확인
```bash
# 웹 서버 상태 확인
sudo systemctl status nginx

# 웹 페이지 접속 테스트
curl http://localhost
curl http://[EC2-Public-IP]

# 배포된 파일 확인
ls -la /var/www/html/
```

## 배포 후 검증 항목

| 항목         | 확인 방법                       | 기대 결과                |
| ------------ | ------------------------------- | ------------------------ |
| 웹 서버 상태 | `systemctl status nginx`        | Active (running)         |
| 파일 배포    | `ls /var/www/html/`             | index.html 존재          |
| 웹 접속      | 브라우저에서 EC2 Public IP 접속 | CodeDeploy Test App 표시 |
| 권한 설정    | `ls -la /var/www/html/`         | www-data 소유권          |

## 문제 해결

### 일반적인 오류와 해결방법

| 오류               | 원인                    | 해결방법                            |
| ------------------ | ----------------------- | ----------------------------------- |
| Agent 연결 실패    | IAM 권한 부족           | EC2 역할에 S3 읽기 권한 추가        |
| 스크립트 실행 실패 | 실행 권한 부족          | chmod +x 로 실행 권한 부여          |
| 배포 타임아웃      | 스크립트 실행 시간 초과 | appspec.yml의 timeout 값 증가       |
| 파일 권한 오류     | 잘못된 소유자/권한      | appspec.yml의 permissions 섹션 확인 |

### 로그 확인 방법
```bash
# CodeDeploy Agent 로그
sudo tail -f /var/log/aws/codedeploy-agent/codedeploy-agent.log

# 배포 로그
sudo tail -f /opt/codedeploy-agent/deployment-root/deployment-logs/codedeploy-agent-deployments.log

# 시스템 로그
sudo journalctl -u codedeploy-agent -f
```

## 모범 사례
* appspec.yml 파일 형식 검증
* 배포 전 스크립트 로컬 테스트
* 롤백 계획 수립
* 배포 알림 설정 (SNS 연동)
* 헬스 체크 구현

## 관련 문서
* [CodeDeploy 사용자 가이드](https://docs.aws.amazon.com/codedeploy/latest/userguide/)
* [appspec.yml 참조](https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html)
