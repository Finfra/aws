# 1.6.1: 수동으로 RDS 셋팅

## 목표
* AWS Console을 통한 RDS 인스턴스 생성
* MySQL 데이터베이스 설정 및 연결
* 보안 그룹 구성으로 EC2에서 접근 허용

## 실습 단계

### 1. RDS 인스턴스 생성
* RDS Console 접속: https://ap-northeast-2.console.aws.amazon.com/rds/home?region=ap-northeast-2#launch-dbinstance:
* Create database 클릭
* 데이터베이스 생성 방법: `Standard create`

### 2. 엔진 옵션 설정
* Engine type: `MySQL`
* Engine Version: `MySQL 8.0.35` (최신 버전)
* Templates: `Free tier` (비용 절약)

### 3. 설정 정보 입력
* DB instance identifier: `mydb-instance`
* Master username: `root`
* Master password: `MyPassword123!` (메모 필수)
* Confirm password: 동일하게 입력

### 4. 인스턴스 구성
* DB instance class: `db.t3.micro` (Free tier eligible)
* Storage type: `General Purpose SSD (gp2)`
* Allocated storage: `20 GiB`
* Storage autoscaling: 활성화

### 5. 연결 설정
* Virtual Private Cloud (VPC): Default VPC
* Subnet group: `default`
* Public access: `Yes` (실습용, 운영환경에서는 No 권장)
* VPC security group: `Create new`
* New VPC security group name: `rds-security-group`

### 6. 추가 구성
* Initial database name: `testdb`
* DB parameter group: `default.mysql8.0`
* Option group: `default:mysql-8-0`
* Backup retention period: `7 days`
* **Delete protection**: `Disable` (실습 후 삭제 위해)

### 7. 보안 그룹 설정
* RDS 생성 후 보안 그룹 수정
* EC2 Security Groups → `rds-security-group` 선택
* Inbound rules 편집:
  - Type: `MySQL/Aurora`
  - Port: `3306`
  - Source: EC2 인스턴스의 보안 그룹 또는 `0.0.0.0/0` (실습용)

### 8. 연결 테스트
```bash
# EC2 인스턴스에서 MySQL 클라이언트 설치
sudo apt update
sudo apt install mysql-client-core-8.0

# RDS 연결 테스트
mysql -h <RDS-Endpoint> -P 3306 -u admin -p

# 연결 성공 시 다음 명령어 실행
SHOW DATABASES;
USE testdb;
SHOW TABLES;
```

## RDS 엔드포인트 확인
* RDS Console → Databases → 인스턴스 선택
* Connectivity & security 탭에서 Endpoint 정보 확인
* 예시: `mydb-instance.abc123def456.ap-northeast-2.rds.amazonaws.com`

## 기본 데이터베이스 작업
```sql
-- 데이터베이스 생성
CREATE DATABASE sampledb;
USE sampledb;

-- 테이블 생성
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 데이터 삽입
INSERT INTO users (username, email) VALUES 
('john_doe', 'john@example.com'),
('jane_smith', 'jane@example.com');

-- 데이터 조회
SELECT * FROM users;
```

## RDS 인스턴스 클래스

| 클래스      | vCPU | 메모리 | 네트워크 성능 | 용도          |
| ----------- | ---- | ------ | ------------- | ------------- |
| db.t3.micro | 2    | 1 GiB  | 최대 5 Gbps   | 개발/테스트   |
| db.t3.small | 2    | 2 GiB  | 최대 5 Gbps   | 소규모 운영   |
| db.m5.large | 2    | 8 GiB  | 최대 10 Gbps  | 일반 운영     |
| db.r5.large | 2    | 16 GiB | 최대 10 Gbps  | 메모리 집약적 |

## 백업 및 스냅샷
```bash
# 수동 스냅샷 생성
# RDS Console → Snapshots → Take snapshot

# 자동 백업 설정 확인
# RDS Console → Databases → 인스턴스 → Maintenance & backups
```

## 모니터링 설정
* CloudWatch 메트릭 확인:
  - DatabaseConnections
  - CPUUtilization
  - FreeableMemory
  - ReadLatency/WriteLatency

## 파라미터 그룹 커스터마이징
```sql
-- 현재 설정 확인
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- 파라미터 그룹에서 수정 가능한 설정들:
-- max_connections: 최대 연결 수
-- innodb_buffer_pool_size: InnoDB 버퍼 풀 크기
-- slow_query_log: 슬로우 쿼리 로그 활성화
```

## 주의사항
* **비밀번호 관리**: 강력한 비밀번호 사용 및 안전한 보관
* **보안 그룹**: 최소 권한 원칙 적용
* **백업**: 중요 데이터는 정기적 백업 필수
* **삭제 보호**: 운영 환경에서는 삭제 보호 활성화
* **비용**: Free tier 한도 초과 시 과금 발생

## 실습 후 정리
```sql
-- 연결 종료
EXIT;
```

```bash
# RDS 인스턴스 삭제
# 1. RDS Console → Databases → 인스턴스 선택
# 2. Actions → Delete
# 3. Delete protection 해제 후 삭제 진행
# 4. 최종 스냅샷 생성 옵션 해제 (실습용)
```

## 다음 단계
* Multi-AZ 배포 설정
* 읽기 전용 복제본 생성
* 성능 모니터링 및 튜닝
