# 1.5.2: 수동으로 EBS 볼륨 연결 및 포맷

## 목표
* 연결된 EBS 볼륨 파티셔닝
* 파일시스템 생성 및 마운트
* 영구 마운트 설정

## 실습 단계

### 1. 볼륨 확인 및 파티셔닝
```bash
# 연결된 볼륨 확인
lsblk

# fdisk로 파티션 생성
sudo fdisk /dev/xvdbb

# fdisk 명령어 순서:
# n (새 파티션 생성)
# p (Primary 파티션)
# 1 (파티션 번호)
# Enter (시작 섹터 기본값)
# Enter (끝 섹터 기본값)
# p (파티션 테이블 확인)
# w (변경사항 저장)
```

### 2. 파일시스템 생성
```bash
# ext4 파일시스템 생성
sudo mkfs.ext4 /dev/xvdbb1

# 다른 파일시스템 옵션들:
# sudo mkfs.xfs /dev/xvdbb1     # XFS 파일시스템
# sudo mkfs.ext3 /dev/xvdbb1    # ext3 파일시스템
```

### 3. 마운트 포인트 생성 및 마운트
```bash
# 마운트 포인트 디렉토리 생성
sudo mkdir /data1

# 볼륨 마운트
sudo mount /dev/xvdbb1 /data1

# 마운트 확인
df -h
lsblk
```

### 4. 영구 마운트 설정
```bash
# UUID 확인
sudo blkid /dev/xvdbb1

# fstab 파일에 추가 (UUID 사용 권장)
echo "UUID=your-uuid-here /data1 ext4 defaults 0 2" | sudo tee -a /etc/fstab

# 또는 디바이스명으로 추가
echo "/dev/xvdbb1 /data1 ext4 defaults 0 1" | sudo tee -a /etc/fstab

# fstab 설정 테스트
sudo mount -a
```

### 5. 권한 설정 및 테스트
```bash
# 마운트된 볼륨 소유권 변경
sudo chown $USER:$USER /data1

# 테스트 파일 생성
echo "Test data" > /data1/test.txt
cat /data1/test.txt

# 디스크 사용량 확인
du -sh /data1/*
```

### 6. 파일시스템 관리
```bash
# 파일시스템 체크
sudo fsck /dev/xvdbb1

# 파일시스템 정보 확인
sudo tune2fs -l /dev/xvdbb1

# 볼륨 라벨 설정
sudo e2label /dev/xvdbb1 "DataVolume"
```

## fstab 옵션 설명

| 옵션     | 설명                                                  |
| -------- | ----------------------------------------------------- |
| defaults | 기본 마운트 옵션 (rw,suid,dev,exec,auto,nouser,async) |
| noatime  | 파일 접근 시간 업데이트 비활성화 (성능 향상)          |
| rw       | 읽기/쓰기 모드                                        |
| ro       | 읽기 전용 모드                                        |
| auto     | 부팅 시 자동 마운트                                   |
| noauto   | 수동 마운트만 허용                                    |

## 파일시스템 타입별 특징

| 타입  | 특징                  | 최대 파일 크기 | 최대 볼륨 크기 |
| ----- | --------------------- | -------------- | -------------- |
| ext4  | 안정성, 호환성 우수   | 16TB           | 1EB            |
| xfs   | 대용량 파일 처리 우수 | 8EB            | 8EB            |
| btrfs | 스냅샷, 압축 지원     | 16EB           | 16EB           |

## 문제 해결

### 마운트 실패 시
```bash
# 마운트 포인트가 사용 중인지 확인
lsof +D /data1

# 강제 언마운트
sudo umount -f /data1

# 지연 언마운트
sudo umount -l /data1
```

### 부팅 시 마운트 실패 방지
```bash
# fstab에서 nofail 옵션 추가
/dev/xvdbb1 /data1 ext4 defaults,nofail 0 2
```

## 주의사항
* 마운트 해제 전 해당 디렉토리에서 작업 중인 프로세스 확인
* fstab 설정 오류 시 부팅 실패 가능성
* UUID 사용 시 디바이스명 변경에도 안정적
* 정기적인 파일시스템 체크 권장

## 성능 최적화
```bash
# I/O 스케줄러 확인 및 변경
cat /sys/block/xvdbb/queue/scheduler
echo noop | sudo tee /sys/block/xvdbb/queue/scheduler

# 마운트 옵션 최적화
# noatime: 접근 시간 업데이트 비활성화
# barrier=0: 쓰기 배리어 비활성화 (성능 향상, 안정성 감소)
```

## 다음 단계
* LVM(Logical Volume Manager) 활용
* RAID 구성
* 볼륨 스냅샷 생성 및 복원
