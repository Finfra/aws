# 1.5.1: 수동으로 볼륨 생성 및 연결

## 목표
* AWS Console을 통한 EBS 볼륨 생성
* EC2 인스턴스에 볼륨 연결
* 볼륨 상태 확인 및 관리

## 실습 단계

### 1. EBS 볼륨 생성
* EC2 Console 접속: https://ap-northeast-2.console.aws.amazon.com/ec2/home?region=ap-northeast-2#Volumes:
* Create Volume 클릭
* 볼륨 설정:
  - Volume Type: `gp3` (General Purpose SSD)
  - Size: `10 GiB`
  - Availability Zone: EC2 인스턴스와 동일한 AZ
  - Encryption: 활성화 권장

### 2. 볼륨을 EC2 인스턴스에 연결
* 생성된 볼륨 선택 → Actions → Attach Volume
* Instance: 대상 EC2 인스턴스 선택
* Device name: `/dev/xvdbb` (또는 다른 사용 가능한 디바이스명)
* Attach 클릭

### 3. 볼륨 인식 확인
```bash
# 연결된 블록 디바이스 확인
lsblk

# 파일시스템 확인
sudo fdisk -l

# 새로 연결된 볼륨 확인 (보통 /dev/xvdbb)
ls -la /dev/xvd*
```

### 4. 볼륨 상태 모니터링
* AWS Console에서 볼륨 상태 확인:
  - State: `in-use`
  - Attachment state: `attached`
* CloudWatch 메트릭 확인:
  - VolumeReadOps/VolumeWriteOps
  - VolumeTotalReadTime/VolumeTotalWriteTime

### 5. 볼륨 분리 및 정리
```bash

# AWS Console에서 볼륨 분리
# Actions → Detach Volume

# 볼륨 삭제 (필요시)
# Actions → Delete Volume
```

## EBS 볼륨 타입 비교

| 타입 | 설명                     | IOPS         | 처리량          | 용도                |
| ---- | ------------------------ | ------------ | --------------- | ------------------- |
| gp3  | General Purpose SSD v3   | 3,000-16,000 | 125-1,000 MiB/s | 범용 워크로드       |
| gp2  | General Purpose SSD v2   | 100-16,000   | 128-250 MiB/s   | 범용 워크로드       |
| io2  | Provisioned IOPS SSD     | 100-64,000   | 256-4,000 MiB/s | 고성능 데이터베이스 |
| st1  | Throughput Optimized HDD | 500          | 40-500 MiB/s    | 빅데이터, 로그 처리 |
| sc1  | Cold HDD                 | 250          | 12-250 MiB/s    | 비용 최적화         |

## 주의사항
* 볼륨과 인스턴스는 동일한 AZ에 있어야 함
* 볼륨 암호화는 생성 시에만 설정 가능
* 루트 볼륨과 추가 볼륨의 차이점 이해
* 볼륨 스냅샷으로 백업 생성 권장

## 다음 단계
* 볼륨 파티셔닝 및 포맷
* 파일시스템 마운트
* 자동 마운트 설정
