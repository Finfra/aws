# 2.3.2: EC2 다중 인스턴스 배포 및 Rolling 배포 전략

## 실습 목표
* Auto Scaling Group과 CodeDeploy 연동
* 다중 인스턴스에 대한 Rolling 배포 구현
* Application Load Balancer와 배포 프로세스 연동
* 배포 모니터링 및 롤백 테스트

## 사전 준비사항
* 2.3.1 실습 완료 (CodeDeploy 기본 설정)

## 실습 단계

### Step 1: Launch Template 생성

**EC2 Console에서 설정**
1. EC2 > Launch Templates > **Create launch template**
2. **Name**: `codedeploy-multi-template`
3. **AMI**: Ubuntu Server 22.04 LTS (Application and OS Images → Quickstart → Ubuntu 22.04 )
4. **Instance type**: t3.micro
5. **Key pari** : `mykey`
6. **Advanced details → IAM instance profile**: CodeDeployInstanceProfile
7. **User data**:
```bash
#!/bin/bash
apt-get update
apt-get install -y ruby wget nginx
cd /tmp
wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
chmod +x ./install
./install auto
systemctl start codedeploy-agent
systemctl enable codedeploy-agent
systemctl enable nginx
systemctl start nginx
```
8. **Create launch template** 클릭


### Step 2: Auto Scaling Group 생성

**ASG 설정**
1. EC2 > Auto Scaling Groups > **Create Auto Scaling group**
2. **Name**: `codedeploy-asg`
3. **Launch template**: codedeploy-multi-template → "Next"
4. **VPC**: Default VPC, **Subnets**: 2개 이상 선택 → "Next"
5. **Load balancing** → **Attach to a new load balancer** → Listeners and routing Create a target group → "Next"  → "Next"
6. **Group size**: Desired=2, Min=1, Max=3  → "Next"
7. **Tags**: Environment=production, Application=web-app  → "Next"
8. **Create Auto Scaling group** 클릭

### Step 3: Application Load Balancer 설정

#### Target Group 생성
1. EC2 > Target Groups > **Create target group**
2. **Name**: `codedeploy-multi-tg`
3. **Protocol**: HTTP:80
4. **Health check path**: `/`  → "Next"
5. **Create target group** 클릭

#### ALB 생성
1. EC2 > Load Balancers > **Create load balancer**
2. **Name**: `codedeploy-multi-alb`
3. **Type**: Application Load Balancer → **Create** 클릭
4. **Load balancer name** :  codedeploy-multi-alb
5. **Availability Zones and subnets** → ASG에서 선택한 zone 선택
6. **Listeners and routing**: HTTP:80 → **codedeploy-multi-tg** → **create load balancer** 클릭

#### ASG와 Target Group 연결
1. Auto Scaling Groups > codedeploy-asg > **Edit**
3. **Health Checkse** → `EDIT` →  Turn on Elastic Load Balancing health Checks 체크 → Update

### Step 4: 배포 그룹 생성

**CodeDeploy 설정**
1. CodeDeploy > Applications > SampleWebApp > **Create deployment group**
2. **Name**: `MultiInstance-DeploymentGroup`
3. **Service role**: CodeDeployServiceRole
4. **Deployment type**: In-place
5. Amazon EC2 Auto Scaling groups 체크 → codedeploy-asg
6. **Environment**: Amazon EC2 Auto Scaling groups 체크
7. **Auto Scaling groups**: codedeploy-asg
8. **Deployment configuration**: OneAtATimeEC2AutoScaling (90%로 생성)
9. **Load balancer**: Enable 

### Step 5: 애플리케이션 버전 2.0 준비

```bash
cd ~/sample-app
cp -r . ../sample-app-backup

# 새로운 index.html 생성
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Instance App v2.0</title>
    <style>
        body { 
            font-family: Arial; 
            text-align: center; 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            padding: 50px; 
        }
        .version { color: #ffeb3b; font-size: 32px; font-weight: bold; }
        .info { background: rgba(255,255,255,0.1); padding: 20px; margin: 20px; border-radius: 10px; }
    </style>
</head>
<body>
    <h1>🚀 Multi-Instance Deployment</h1>
    <p class="version">Version 2.0</p>
    <p>Rolling Deployment with Auto Scaling Group</p>
    
    <div class="info">
        <h3>📊 Deployment Strategy</h3>
        <p>One-at-a-time Rolling Update</p>
    </div>
    
    <div class="info">
        <h3>⚖️ Load Balancing</h3>
        <p>Application Load Balancer</p>
    </div>
    
    <p><strong>Deploy Time:</strong> <span id="time"></span></p>
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
EOF

# 배포 패키지 생성 및 업로드
zip -r sample-app-v2.zip . -x "*.git*" "*backup*"
aws s3 cp sample-app-v2.zip s3://codedeploy-bucket-kitri-자기번호/
```

### Step 6: Rolling 배포 실행

**배포 실행**
1. CodeDeploy > SampleWebApp > MultiInstance-DeploymentGroup
2. Deployments → **Create deployment**
3. Deployment group → SampleWebApp-DeploymentGroup
4. **Revision location**: `s3://codedeploy-bucket-kitri-자기번호/sample-app-v2.zip`
5. **Description**: `Multi-instance rolling deployment v2.0`

### Step 7: 배포 검증

```bash
# ALB DNS 확인
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names codedeploy-multi-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

echo "ALB DNS: $ALB_DNS"
# 안나오면 
#   ec2 > Target groups > codedeploy-multi-tg에서 Target Instance에서 인스턴스 추가
#   SecurityGroup확인



# 웹 서비스 테스트 
curl "http://$ALB_DNS/" | grep "Version 2.0"
# 안나오면
#   cat /usr/share/nginx/html/index.html

# 로드 밸런싱 테스트 (여러 번 요청)
for i in {1..5}; do
    echo "요청 $i:"
    curl -s "http://$ALB_DNS/" | grep "Deploy Time"
    sleep 1
done
```

### Step 8: 롤백 테스트

```bash
# 실패 버전 생성
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Broken Version 2.1</title></head>
<body>
    <h1>Version 2.1 - Broken for rollback test</h1>
    <script>throw new Error("Simulated error");</script>
</body>
</html>
EOF

# 실패하는 검증 스크립트
cat > scripts/validate_service.sh << 'EOF'
#!/bin/bash
echo "ERROR: Validation failed"
exit 1
EOF

chmod +x scripts/validate_service.sh

# 실패 버전 배포
zip -r sample-app-v2.1-broken.zip . -x "*.git*" "*backup*"
aws s3 cp sample-app-v2.1-broken.zip s3://codedeploy-bucket-kitri-자기번호/

# CodeDeploy에서 이 버전으로 배포 실행 → 자동 롤백 확인
```

### Step 9: 배포 전략 비교

#### HalfAtATime 테스트
1. 새 배포 그룹 생성: `HalfAtATime-DeploymentGroup`
2. **Deployment configuration**: `CodeDeployDefault.HalfAtATimeEC2AutoScaling`
3. 배포 시간 비교

```bash
# 버전 2.2 생성 (색상 변경)
sed 's/#667eea, #764ba2/#28a745, #20c997/g' index.html > index_new.html
mv index_new.html index.html
sed 's/Version 2.0/Version 2.2/g' index.html > index_new.html
mv index_new.html index.html

zip -r sample-app-v2.2.zip . -x "*.git*" "*backup*"
aws s3 cp sample-app-v2.2.zip s3://codedeploy-bucket-kitri-자기번호/
```

### Step 10: 리소스 정리

```bash
# Auto Scaling Group 삭제
aws autoscaling delete-auto-scaling-group --auto-scaling-group-name codedeploy-asg --force-delete

# Launch Template 삭제
aws ec2 delete-launch-template --launch-template-name codedeploy-multi-template

# S3 정리
aws s3 rm s3://codedeploy-bucket-kitri-자기번호/ --recursive

# ALB, Target Group은 콘솔에서 수동 삭제
```

## 배포 전략 비교

| 전략        | 배포 시간 | 가용성 | 적용 시나리오 |
| ----------- | --------- | ------ | ------------- |
| OneAtATime  | 오래 걸림 | 높음   | 운영 환경     |
| HalfAtATime | 중간      | 중간   | 균형잡힌 배포 |
| AllAtOnce   | 빠름      | 낮음   | 개발/테스트   |

## 체크리스트

### 필수 완료 항목
- [ ] Launch Template 생성
- [ ] Auto Scaling Group 생성 (3개 인스턴스)
- [ ] ALB 및 Target Group 설정
- [ ] ASG와 Target Group 연결
- [ ] 다중 인스턴스 배포 그룹 생성
- [ ] Rolling 배포 성공 (v2.0)
- [ ] ALB를 통한 로드 밸런싱 확인
- [ ] 롤백 테스트 완료

### 선택 완료 항목
- [ ] HalfAtATime 배포 전략 테스트
- [ ] 배포 시간 측정 및 비교
- [ ] 리소스 정리

## 요약

이번 실습에서 학습한 내용:
* **Auto Scaling Group 연동**: 동적 인프라에서의 배포 관리
* **Rolling 배포**: 서비스 가용성을 유지하며 단계적 배포
* **Load Balancer 통합**: 무중단 서비스를 위한 트래픽 분산
* **배포 전략 비교**: 상황에 맞는 적절한 배포 방식 선택
* **롤백 프로세스**: 장애 상황에서의 빠른 복구

다음 실습(2.3.3)에서는 Blue/Green 배포를 통한 완전한 무중단 배포를 학습할 예정.
