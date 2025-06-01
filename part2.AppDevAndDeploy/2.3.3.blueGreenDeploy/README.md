# 2.3.3: Blue/Green 배포 전략 적용

## 실습 목표
* Blue/Green 배포 전략 이해 및 구현
* 무중단 배포 프로세스 실습
* Application Load Balancer를 이용한 트래픽 전환
* 롤백 전략 수립 및 실행

## Blue/Green 배포 기본 개념
* **Blue 환경**: 현재 운영 중인 애플리케이션 환경
* **Green 환경**: 새 버전이 배포될 환경
* **트래픽 전환**: Load Balancer를 통한 즉시 전환
* **무중단 배포**: 서비스 중단 없이 새 버전 배포

## 실습 아키텍처
```
Internet Gateway
    |
Application Load Balancer
    |
Target Groups
    |
+-- Blue Environment (현재 버전)
    |
    +-- EC2 Instance 1 (Blue)
    +-- EC2 Instance 2 (Blue)
    
+-- Green Environment (새 버전)
    |
    +-- EC2 Instance 1 (Green)
    +-- EC2 Instance 2 (Green)
```

## 실습 단계

### Step 1: 사전 준비
* 2.3.1에서 구성한 CodeDeploy 환경 활용
* Application Load Balancer 생성 준비
* Auto Scaling Group 구성

### Step 2: Application Load Balancer 생성

#### ALB 기본 설정
* EC2 > Load Balancers > Create Application Load Balancer
* **Name**: `webapp-alb`
* **Scheme**: Internet-facing
* **IP address type**: IPv4

#### 리스너 및 라우팅 설정
* **Protocol**: HTTP
* **Port**: 80
* **Default action**: Forward to target group

### Step 3: Target Group 생성

#### Blue Target Group
* **Name**: `webapp-blue-tg`
* **Target type**: Instances
* **Protocol**: HTTP
* **Port**: 80
* **Health check path**: `/`

#### Green Target Group
* **Name**: `webapp-green-tg`
* **Target type**: Instances  
* **Protocol**: HTTP
* **Port**: 80
* **Health check path**: `/`

### Step 4: Auto Scaling Group 설정

#### Launch Template 생성
```bash
# User Data 스크립트
#!/bin/bash
yum update -y
yum install -y nginx
systemctl start nginx
systemctl enable nginx

# CodeDeploy Agent 설치
yum install -y ruby wget
cd /home/ec2-user
wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
chmod +x ./install
./install auto
service codedeploy-agent start
```

#### Blue Auto Scaling Group
* **Name**: `webapp-blue-asg`
* **Launch Template**: webapp-launch-template
* **Min/Max/Desired**: 2/4/2
* **Target Group**: webapp-blue-tg
* **Tags**: Environment=Blue

#### Green Auto Scaling Group  
* **Name**: `webapp-green-asg`
* **Launch Template**: webapp-launch-template
* **Min/Max/Desired**: 0/4/0 (초기에는 0)
* **Target Group**: webapp-green-tg
* **Tags**: Environment=Green

### Step 5: CodeDeploy 애플리케이션 수정

#### Blue/Green 배포 구성 생성
* CodeDeploy > Applications > Create deployment configuration
* **Configuration name**: `BlueGreenDeployment`
* **Compute platform**: EC2/On-premises
* **Type**: Blue/green
* **Environment configuration**: Auto Scaling groups
* **Deployment settings**:
  - Terminate original instances: 5 minutes
  - Deployment configuration: Linear 50% every 10 minutes

#### 새로운 배포 그룹 생성
* **Deployment group name**: `webapp-bluegreen-dg`
* **Service role**: CodeDeployServiceRole
* **Deployment type**: Blue/green
* **Environment configuration**: 
  - Blue/green environment: Auto Scaling groups
  - Production traffic route: webapp-alb
  - Target groups: webapp-blue-tg, webapp-green-tg

### Step 6: 애플리케이션 v2.0 준비

#### 새 버전 애플리케이션 생성
```bash
# 애플리케이션 v2.0 생성
cd ~/sample-app-v2
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>CodeDeploy Test App v2.0</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 50px; 
            background-color: #e8f5e8;
        }
        .container { text-align: center; }
        .version { 
            color: #28a745; 
            font-size: 24px; 
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to CodeDeploy Test App</h1>
        <p class="version">Version 2.0 - GREEN DEPLOYMENT</p>
        <p>Deployed with AWS CodeDeploy Blue/Green Strategy</p>
        <p>New Features Added!</p>
    </div>
</body>
</html>
EOF

# appspec.yml은 동일하게 사용
cp ../sample-app/appspec.yml .
cp -r ../sample-app/scripts .

# 새 배포 패키지 생성
zip -r sample-app-v2.zip . -x "*.git*"

# S3에 업로드
aws s3 cp sample-app-v2.zip s3://your-codedeploy-bucket-name/
```

### Step 7: Blue/Green 배포 실행

#### 배포 시작
* CodeDeploy > Deployments > Create deployment
* **Application**: SampleWebApp
* **Deployment group**: webapp-bluegreen-dg
* **Revision location**: s3://your-codedeploy-bucket-name/sample-app-v2.zip

#### 배포 과정 모니터링
1. **Green 환경 프로비저닝**: 새 인스턴스 생성
2. **애플리케이션 배포**: Green 환경에 v2.0 배포
3. **헬스 체크**: Green 환경 정상성 확인
4. **트래픽 전환**: ALB에서 Green으로 트래픽 라우팅
5. **Blue 환경 종료**: 설정된 시간 후 Blue 인스턴스 종료

### Step 8: 배포 검증

#### 트래픽 확인
```bash
# ALB DNS 이름으로 접속 테스트
curl http://webapp-alb-1234567890.ap-northeast-2.elb.amazonaws.com/

# 응답 확인 (v2.0 표시되어야 함)
# 브라우저에서도 확인
```

#### 인스턴스 상태 확인
* Blue ASG: 인스턴스 수 0 (종료됨)
* Green ASG: 인스턴스 수 2 (운영 중)
* Target Group Health Check: Green 타겟들 Healthy

### Step 9: 롤백 시나리오 실습

#### 문제 상황 시뮬레이션
```bash
# Green 환경에 일부러 문제 발생시키기
# (실제 운영에서는 하지 말 것!)
ssh -i mykey.pem ubuntu@[green-instance-ip]
sudo systemctl stop nginx
```

#### 수동 롤백 실행
* CodeDeploy Console에서 "Stop and rollback" 실행
* 또는 ALB Target Group에서 수동으로 Blue로 트래픽 전환

#### 자동 롤백 설정
* 배포 그룹 설정에서 자동 롤백 조건 설정:
  - Deployment fails
  - Alarm thresholds are met
  - Deployment stops

## 카나리 배포 (추가 실습)

### 가중치 기반 트래픽 분할
* ALB에서 가중치 기반 라우팅 설정
* 90% Blue, 10% Green으로 시작
* 점진적으로 Green 비중 증가

### CloudWatch 메트릭 모니터링
* 에러율, 응답 시간, 트래픽 분석
* 임계값 초과 시 자동 롤백 트리거

## 고급 배포 전략

### 링 배포 (Ring Deployment)
* 지역별, 사용자 그룹별 점진적 배포
* 단계적 위험 관리

### 피처 토글 (Feature Toggle)
* 코드 레벨에서 기능 on/off 제어
* 배포와 릴리스 분리

## 모니터링 및 알림

### CloudWatch 대시보드
* 배포 진행률 시각화
* 애플리케이션 메트릭 모니터링
* 에러율 및 응답 시간 추적

### SNS 알림 설정
* 배포 성공/실패 알림
* 임계값 초과 시 알림
* 롤백 실행 알림

## 비용 고려사항
* Blue/Green 배포 시 일시적으로 인스턴스 수 2배 증가
* ALB 및 Target Group 추가 비용
* 배포 시간 동안의 리소스 중복 사용

## 모범 사례
* 충분한 헬스 체크 시간 확보
* 데이터베이스 스키마 호환성 고려
* 설정 파일 외부화 (환경 변수, Parameter Store)
* 모니터링 임계값 적절히 설정
* 롤백 시나리오 사전 테스트

## 문제 해결

### 일반적인 이슈

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| Green 환경 헬스 체크 실패 | 애플리케이션 시작 지연 | 헬스 체크 대기 시간 증가 |
| 트래픽 전환 실패 | Target Group 설정 오류 | ALB 리스너 규칙 확인 |
| 배포 타임아웃 | 인스턴스 프로비저닝 지연 | 타임아웃 값 조정 |
| 데이터 불일치 | 데이터베이스 동기화 문제 | 스키마 마이그레이션 전략 수립 |

## 관련 문서
* [CodeDeploy Blue/Green 배포](https://docs.aws.amazon.com/codedeploy/latest/userguide/applications-create-blue-green.html)
* [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
* [Auto Scaling Groups](https://docs.aws.amazon.com/autoscaling/ec2/userguide/AutoScalingGroup.html)
