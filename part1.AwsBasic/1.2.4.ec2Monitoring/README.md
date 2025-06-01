# 1.2.4: EC2 인스턴스 모니터링 및 관리

## 목표
* CloudWatch를 통한 EC2 성능 모니터링
* 인스턴스 상태 관리 및 EIP 활용

## 실습 단계

### 1. CloudWatch 모니터링
* EC2 Console → Instances → Monitoring 탭
* CPU 사용률, 네트워크 트래픽, 디스크 I/O 확인
* CloudWatch 대시보드 생성

### 2. 인스턴스 상태 관리
* 인스턴스 중지(Stop): 상태 저장, 과금 중단
* 인스턴스 시작(Start): 새로운 Public IP 할당
* 재부팅(Reboot): IP 유지
* 종료(Terminate): 완전 삭제

### 3. Public IP 변경 확인
```bash
# 인스턴스 중지 전 IP 확인
curl ifconfig.me

# 인스턴스 재시작 후 IP 확인
curl ifconfig.me
```

### 4. EIP(Elastic IP) 활용
* VPC → Elastic IPs → Allocate Elastic IP address
* 생성된 EIP를 인스턴스에 Associate
* 고정 IP로 안정적인 연결 보장

### 5. 모니터링 알람 설정
* CloudWatch → Alarms → Create alarm
* CPU 사용률 80% 초과 시 알림 설정
* SNS 토픽 생성하여 이메일 알림 구성

## 주요 메트릭
* **CPUUtilization**: CPU 사용률
* **NetworkIn/Out**: 네트워크 트래픽
* **DiskReadOps/WriteOps**: 디스크 작업 수
* **StatusCheckFailed**: 인스턴스 상태 체크

## 주의사항
* EIP는 사용하지 않을 때 과금됨
* 인스턴스 종료 시 EIP 해제 필요
* CloudWatch 세부 모니터링은 추가 비용 발생

## 다음 단계
* 로그 모니터링 설정
* 자동 스케일링 구성
