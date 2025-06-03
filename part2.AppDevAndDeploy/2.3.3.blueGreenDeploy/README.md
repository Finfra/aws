# 2.3.3: Blue/Green 배포 전략 (무중단 배포)

## 실습 목표
* Blue/Green 배포 전략 이해 및 구현
* 완전한 무중단 배포 실현
* Application Load Balancer를 통한 즉시 트래픽 전환
* 안전한 롤백 프로세스 구축

## Blue/Green 배포 개념
* **Blue**: 현재 운영 중인 환경
* **Green**: 새 버전이 배포될 환경
* **무중단 배포**: ALB가 즉시 트래픽을 Green으로 전환
* **즉시 롤백**: 문제 발생 시 Blue로 즉시 복구

## 사전 준비사항
* 2.3.2 실습 완료 (Rolling 배포 환경)

## 실습 단계

### Step 1: Blue/Green용 Target Group 생성

**기존 Green Target Group 생성**
1. EC2 > Target Groups > **Create target group**
2. **Name**: `codedeploy-green-tg`
3. **Protocol**: HTTP:80
4. **Health check**: 기존 설정과 동일

### Step 2: Blue/Green 배포 그룹 생성

**CodeDeploy에서 Blue/Green 배포 그룹 설정**
1. CodeDeploy > SampleWebApp > **Create deployment group**
2. **Name**: `BlueGreen-DeploymentGroup`
3. **Service role**: CodeDeployServiceRole
4. **Deployment type**: **Blue/green**
5. **Environment configuration**:
   - **Automatically copy Auto Scaling group**: codedeploy-asg 선택
   - **Copy Auto Scaling group**: Yes
6. **Load balancer**:
   - **Production traffic route**: codedeploy-multi-alb
   - **Target group 1**: codedeploy-multi-tg (Blue)
   - **Target group 2**: codedeploy-green-tg (Green)
7. **Deployment settings**:
   - **Reroute traffic immediately**
   - **Terminate original instances**: 5 minutes after successful deployment

### Step 3: 애플리케이션 버전 3.0 준비

```bash
cd ~/sample-app
cp -r . ../sample-app-v3

# Green 환경용 애플리케이션 (버전 3.0) 생성
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Blue/Green Deployment v3.0</title>
    <style>
        body { 
            font-family: Arial; 
            text-align: center; 
            background: linear-gradient(135deg, #28a745, #20c997); 
            color: white; 
            padding: 50px; 
        }
        .version { color: #ffeb3b; font-size: 36px; font-weight: bold; }
        .info { background: rgba(255,255,255,0.1); padding: 20px; margin: 20px; border-radius: 10px; }
        .green { color: #90EE90; font-size: 24px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🟢 GREEN ENVIRONMENT</h1>
    <p class="version">Version 3.0</p>
    <p class="green">Blue/Green Deployment - Zero Downtime!</p>
    
    <div class="info">
        <h3>✨ New Features</h3>
        <p>• Instant traffic switching</p>
        <p>• Zero downtime deployment</p>
        <p>• Immediate rollback capability</p>
    </div>
    
    <div class="info">
        <h3>🚀 Deployment Type</h3>
        <p>Blue/Green Strategy</p>
    </div>
    
    <p><strong>Deployed at:</strong> <span id="time"></span></p>
    <script>
        document.getElementById('time').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
EOF

# 배포 패키지 생성 및 업로드
zip -r sample-app-v3.zip . -x "*.git*" "*backup*"
aws s3 cp sample-app-v3.zip s3://codedeploy-bucket-kitri-자기번호/
```

### Step 4: Blue/Green 배포 실행

**배포 실행**
1. CodeDeploy > SampleWebApp > BlueGreen-DeploymentGroup
2. **Create deployment**
3. **Revision location**: `s3://codedeploy-bucket-kitri-자기번호/sample-app-v3.zip`
4. **Description**: `Blue/Green deployment v3.0`

**배포 과정 관찰**
1. **Green 환경 생성**: 새로운 Auto Scaling Group 및 인스턴스 생성
2. **애플리케이션 배포**: Green 환경에 v3.0 배포
3. **헬스 체크**: Green 환경 정상성 확인
4. **트래픽 전환**: ALB가 즉시 Green으로 모든 트래픽 전환
5. **Blue 환경 대기**: 5분 후 Blue 인스턴스 자동 종료

### Step 5: 배포 검증

```bash
# ALB DNS 확인
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --names codedeploy-multi-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

# Green 환경 배포 확인
echo "=== Blue/Green 배포 검증 ==="
curl "http://$ALB_DNS/" | grep "Version 3.0" && echo "✅ Green 환경 배포 성공"

# Target Group 상태 확인
echo "=== Blue Target Group 상태 ==="
aws elbv2 describe-target-health \
    --target-group-arn $(aws elbv2 describe-target-groups \
        --names codedeploy-multi-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text) \
    --query 'TargetHealthDescriptions[0].TargetHealth.State' \
    --output text

echo "=== Green Target Group 상태 ==="
aws elbv2 describe-target-health \
    --target-group-arn $(aws elbv2 describe-target-groups \
        --names codedeploy-green-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text) \
    --query 'TargetHealthDescriptions[0].TargetHealth.State' \
    --output text
```

### Step 6: 트래픽 전환 확인

```bash
# 트래픽 전환 테스트
cat > test-traffic-switch.sh << 'EOF'
#!/bin/bash

ALB_DNS="your-alb-dns-name"  # 실제 ALB DNS로 변경

echo "=== 트래픽 전환 테스트 ==="
echo "배포 전후 페이지 변화 확인..."

for i in {1..10}; do
    RESPONSE=$(curl -s "http://$ALB_DNS/")
    VERSION=$(echo "$RESPONSE" | grep -o "Version [0-9.]*")
    ENVIRONMENT=$(echo "$RESPONSE" | grep -o "GREEN ENVIRONMENT\|Multi-Instance")
    
    echo "요청 $i: $VERSION - $ENVIRONMENT"
    sleep 2
done

echo ""
echo "모든 요청이 Green 환경(v3.0)에서 응답되면 성공!"
EOF

chmod +x test-traffic-switch.sh
```

### Step 7: 롤백 테스트 

#### 의도적 문제 상황 생성
```bash
# 문제가 있는 버전 3.1 생성
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Broken Version 3.1</title>
    <style>body { background: red; color: white; text-align: center; padding: 50px; }</style>
</head>
<body>
    <h1>⚠️ Version 3.1 - BROKEN</h1>
    <p>This version has critical issues!</p>
    <script>
        // 의도적 에러 발생
        setInterval(() => {
            throw new Error("Critical application error");
        }, 1000);
    </script>
</body>
</html>
EOF

# 실패 배포 패키지 생성
zip -r sample-app-v3.1-broken.zip . -x "*.git*" "*backup*"
aws s3 cp sample-app-v3.1-broken.zip s3://codedeploy-bucket-kitri-자기번호/
```

#### 실패 배포 실행 및 롤백
1. 문제 버전으로 Blue/Green 배포 실행
2. 배포 실패 시 자동 롤백 확인
3. 또는 수동으로 "Stop and rollback" 실행

### Step 8: 카나리 배포 실습 (추가)

**ALB에서 가중치 기반 트래픽 분할**
1. ALB > Listeners > View/edit rules
2. **Add rule** 클릭
3. **Conditions**: Path = /*
4. **Actions**: 
   - Forward to target groups
   - codedeploy-multi-tg (Blue): 90%
   - codedeploy-green-tg (Green): 10%

```bash
# 카나리 배포 테스트
for i in {1..20}; do
    RESPONSE=$(curl -s "http://$ALB_DNS/")
    VERSION=$(echo "$RESPONSE" | grep -o "Version [0-9.]*")
    echo "요청 $i: $VERSION"
done

# 결과: 약 90%는 Blue(v2.0), 10%는 Green(v3.0) 응답
```

### Step 9: 모니터링 설정

```bash
# CloudWatch 알람 생성 (Green 환경 모니터링)
aws cloudwatch put-metric-alarm \
    --alarm-name "Green-Environment-HighErrorRate" \
    --alarm-description "Monitor error rate in Green environment" \
    --metric-name "HTTPCode_Target_5XX_Count" \
    --namespace "AWS/ApplicationELB" \
    --statistic "Sum" \
    --period 300 \
    --threshold 10 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 2 \
    --dimensions Name=TargetGroup,Value=targetgroup/codedeploy-green-tg/xxx

# 응답 시간 모니터링
aws cloudwatch put-metric-alarm \
    --alarm-name "Green-Environment-HighLatency" \
    --alarm-description "Monitor response time in Green environment" \
    --metric-name "TargetResponseTime" \
    --namespace "AWS/ApplicationELB" \
    --statistic "Average" \
    --period 300 \
    --threshold 2.0 \
    --comparison-operator "GreaterThanThreshold" \
    --evaluation-periods 2
```

### Step 10: 리소스 정리

```bash
# 추가로 생성된 리소스 정리
# Green Target Group 삭제 (콘솔에서)
# Blue/Green 배포 그룹 삭제 (콘솔에서)

# CloudWatch 알람 삭제
aws cloudwatch delete-alarms \
    --alarm-names "Green-Environment-HighErrorRate" "Green-Environment-HighLatency"

echo "✅ Blue/Green 배포 실습 정리 완료"
```

## 배포 전략 비교

| 전략       | 다운타임 | 리소스 비용  | 롤백 시간 | 위험도 |
| ---------- | -------- | ------------ | --------- | ------ |
| Rolling    | 없음     | 기본         | 느림      | 중간   |
| Blue/Green | 없음     | 2배 (일시적) | 즉시      | 낮음   |
| Canary     | 없음     | 약간 증가    | 즉시      | 낮음   |

## 체크리스트

### 필수 완료 항목
- [ ] Green Target Group 생성
- [ ] Blue/Green 배포 그룹 생성
- [ ] Blue/Green 배포 성공 (v3.0)
- [ ] 트래픽 즉시 전환 확인
- [ ] Blue 환경 자동 종료 확인
- [ ] 롤백 테스트 완료

### 선택 완료 항목
- [ ] 카나리 배포 (가중치 기반) 테스트
- [ ] CloudWatch 알람 설정
- [ ] 배포 전략별 성능 비교

## Blue/Green vs Rolling 배포 차이점

### Blue/Green 장점
* **완전한 무중단**: 즉시 트래픽 전환
* **빠른 롤백**: 문제 발생 시 즉시 복구
* **안전한 테스트**: Green 환경에서 충분한 검증 가능

### Blue/Green 단점
* **높은 비용**: 배포 시 리소스 2배 사용
* **복잡성**: 데이터베이스 동기화 등 고려사항 많음

## 실무 적용 시 고려사항

### 데이터베이스 호환성
* 스키마 변경 시 하위 호환성 유지
* 데이터 마이그레이션 전략 수립

### 상태 저장 애플리케이션
* 세션 데이터 외부 저장소 활용
* 상태 정보 동기화 방안 마련

### 비용 최적화
* 배포 시간 최소화
* Spot 인스턴스 활용 고려

## 요약

이번 실습에서 학습한 내용:
* **Blue/Green 배포**: 완전한 무중단 배포 구현
* **즉시 트래픽 전환**: ALB를 통한 seamless 전환
* **빠른 롤백**: 문제 발생 시 즉시 복구 능력
* **카나리 배포**: 점진적 트래픽 분산을 통한 위험 최소화
* **모니터링**: 배포 과정 및 애플리케이션 상태 추적

Blue/Green 배포는 안정성이 가장 중요한 운영 환경에서 활용하며, 비용과 복잡성을 고려하여 적절한 상황에서 선택적으로 사용하는 것이 중요함.

