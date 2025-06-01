# 1.6.3: RDS 성능 모니터링 및 튜닝

## 목표
* RDS 성능 테스트용 데이터 생성
* 쿼리 실행 계획 분석
* 인덱스 최적화 및 CloudWatch 모니터링

## 실습 단계

### 1. 데이터베이스 및 테이블 생성
```sql
-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS db1;
USE db1;

-- 성능 테스트용 테이블 생성
CREATE TABLE t1 (
    id1 INT NOT NULL AUTO_INCREMENT,
    id2 VARCHAR(255),
    data_field VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id1)
);
```

### 2. 대량 데이터 생성
```sql
-- 초기 데이터 입력
INSERT INTO t1 (id2, data_field) VALUES ('data_1', 'Sample data content for testing');

-- 데이터 증배 (충분히 느려질 때까지 반복)
INSERT INTO t1 (id2, data_field) 
SELECT CONCAT('data_', id1 + 1), CONCAT('Sample data content ', id1 + 1) 
FROM t1;

-- 데이터 수 확인
SELECT COUNT(*) FROM t1;

-- 10만 건 이상 될 때까지 반복 실행
-- 또는 한 번에 더 많은 데이터 생성:
INSERT INTO t1 (id2, data_field)
SELECT 
    CONCAT('data_', (@row_number:=@row_number+1)), 
    CONCAT('Sample data content ', @row_number)
FROM 
    (SELECT @row_number:=0) r
    CROSS JOIN (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t1
    CROSS JOIN (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t2
    CROSS JOIN (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t3
    CROSS JOIN (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t4;
```

### 3. 인덱스 생성 전후 성능 비교
```sql
-- 인덱스 생성 전 쿼리 성능 테스트
EXPLAIN SELECT * FROM t1 WHERE id2 = 'data_1234';

-- 실행 시간 측정
SET profiling = 1;
SELECT * FROM t1 WHERE id2 = 'data_1234';
SHOW PROFILES;

-- 인덱스 생성
CREATE INDEX idx_id2 ON t1 (id2);

-- 인덱스 생성 후 성능 비교
EXPLAIN SELECT * FROM t1 WHERE id2 = 'data_1234';
SELECT * FROM t1 WHERE id2 = 'data_1234';
SHOW PROFILES;
```

### 4. 쿼리 실행 계획 분석
```sql
-- EXPLAIN 결과 분석
EXPLAIN FORMAT=JSON SELECT * FROM t1 WHERE id2 LIKE 'data_1%';

-- 인덱스 사용 현황 확인
SHOW INDEX FROM t1;

-- 슬로우 쿼리 로그 활성화 (Parameter Group에서 설정)
-- slow_query_log = 1
-- long_query_time = 1

-- 쿼리 캐시 상태 확인
SHOW STATUS LIKE 'Qcache%';
```

### 5. 성능 최적화 쿼리들
```sql
-- 복합 인덱스 생성
CREATE INDEX idx_composite ON t1 (id2, created_at);

-- 파티셔닝된 쿼리 테스트
SELECT COUNT(*) FROM t1 WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY);

-- 집계 쿼리 성능 테스트
SELECT 
    DATE(created_at) as date,
    COUNT(*) as daily_count,
    AVG(LENGTH(data_field)) as avg_data_length
FROM t1 
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- JOIN 성능 테스트용 두 번째 테이블
CREATE TABLE t2 (
    id INT AUTO_INCREMENT PRIMARY KEY,
    t1_id INT,
    status VARCHAR(50),
    INDEX idx_t1_id (t1_id)
);

INSERT INTO t2 (t1_id, status)
SELECT id1, CASE WHEN id1 % 3 = 0 THEN 'active' WHEN id1 % 3 = 1 THEN 'inactive' ELSE 'pending' END
FROM t1 LIMIT 50000;

-- JOIN 쿼리 성능 측정
EXPLAIN SELECT t1.id2, t2.status 
FROM t1 
JOIN t2 ON t1.id1 = t2.t1_id 
WHERE t2.status = 'active';
```

### 6. CloudWatch 메트릭 모니터링
* **주요 메트릭들**:
  - `DatabaseConnections`: 현재 연결 수
  - `CPUUtilization`: CPU 사용률
  - `FreeableMemory`: 사용 가능한 메모리
  - `ReadLatency/WriteLatency`: 읽기/쓰기 지연시간
  - `ReadThroughput/WriteThroughput`: 읽기/쓰기 처리량
  - `NetworkReceiveThroughput/NetworkTransmitThroughput`: 네트워크 처리량

### 7. Performance Insights 활용
* RDS Console → Performance Insights 활성화
* Top SQL 문 분석
* Wait events 모니터링
* Database load 확인

### 8. 파라미터 그룹 최적화
```sql
-- 현재 설정 확인
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'query_cache_size';
SHOW VARIABLES LIKE 'tmp_table_size';

-- 권장 설정들 (Parameter Group에서 수정):
-- innodb_buffer_pool_size = (총 메모리의 70-80%)
-- max_connections = (적절한 연결 수, 기본값 조정)
-- query_cache_size = 0 (MySQL 8.0에서는 deprecated)
-- innodb_log_file_size = 256M (또는 더 큰 값)
```

### 9. 성능 부하 테스트
```bash
# EC2에서 mysqlslap을 사용한 부하 테스트
mysqlslap --defaults-file=/etc/mysql/my.cnf \
  --host=<RDS-Endpoint> \
  --user=root \
  --password=<password> \
  --concurrency=50 \
  --iterations=10 \
  --number-int-cols=2 \
  --number-char-cols=3 \
  --auto-generate-sql

# sysbench를 사용한 더 정교한 테스트
sudo apt install sysbench
sysbench oltp_read_write \
  --mysql-host=<RDS-Endpoint> \
  --mysql-user=root \
  --mysql-password=<password> \
  --mysql-db=db1 \
  --tables=10 \
  --table-size=100000 \
  prepare

sysbench oltp_read_write \
  --mysql-host=<RDS-Endpoint> \
  --mysql-user=root \
  --mysql-password=<password> \
  --mysql-db=db1 \
  --tables=10 \
  --table-size=100000 \
  --threads=16 \
  --time=300 \
  run
```

## 성능 최적화 체크리스트

### 인덱스 최적화
* 자주 사용되는 WHERE 절 컬럼에 인덱스 생성
* 복합 인덱스 순서 최적화 (선택도가 높은 컬럼을 앞에)
* 사용하지 않는 인덱스 제거

### 쿼리 최적화
* SELECT * 대신 필요한 컬럼만 선택
* LIMIT 사용으로 결과 제한
* 적절한 JOIN 타입 선택
* 서브쿼리 대신 JOIN 사용 검토

### 설정 최적화
* `innodb_buffer_pool_size`: 메모리의 70-80%
* `max_connections`: 적절한 연결 수 설정
* `innodb_log_file_size`: 충분한 로그 파일 크기

## 문제 진단 및 해결

### 느린 쿼리 식별
```sql
-- 슬로우 쿼리 로그 확인
SHOW PROCESSLIST;

-- 실행 중인 쿼리 확인
SELECT * FROM information_schema.PROCESSLIST WHERE TIME > 5;

-- 테이블 잠금 확인
SHOW OPEN TABLES WHERE In_use > 0;
```

### 인덱스 사용률 분석
```sql
-- 인덱스 카디널리티 확인
SELECT 
    TABLE_NAME,
    INDEX_NAME,
    CARDINALITY,
    SUB_PART,
    PACKED,
    NULLABLE,
    INDEX_TYPE
FROM information_schema.STATISTICS 
WHERE TABLE_SCHEMA = 'db1';

-- 사용되지 않는 인덱스 찾기
SELECT 
    s.schema_name,
    s.table_name,
    s.index_name
FROM sys.schema_unused_indexes s;
```

## 주의사항
* 운영 환경에서는 부하 테스트 전 백업 필수
* 파라미터 변경 시 인스턴스 재시작 필요할 수 있음
* 인덱스 생성은 테이블 크기에 따라 시간이 오래 걸릴 수 있음
* Performance Insights는 추가 비용 발생 가능
* 부하 테스트 시 RDS 인스턴스 성능에 영향 줄 수 있음

## 성능 모니터링 대시보드 설정
```sql
-- 실시간 성능 모니터링 쿼리
SELECT 
    CONCAT(ROUND(timer_wait/1000000000000,6), ' s') as duration,
    sql_text,
    current_schema
FROM performance_schema.events_statements_history_long 
WHERE timer_wait > 1000000000000
ORDER BY timer_wait DESC
LIMIT 10;

-- 테이블별 I/O 통계
SELECT 
    object_schema,
    object_name,
    count_read,
    count_write,
    count_fetch,
    count_insert,
    count_update,
    count_delete
FROM performance_schema.table_io_waits_summary_by_table
WHERE object_schema = 'db1'
ORDER BY count_read + count_write DESC;
```

## 알람 설정
* CloudWatch에서 다음 메트릭에 대한 알람 생성:
  - CPUUtilization > 80%
  - DatabaseConnections > 80% of max_connections
  - FreeableMemory < 100MB
  - ReadLatency > 200ms
  - WriteLatency > 200ms

## 백업 및 복구 전략
```bash
# 논리적 백업 (mysqldump)
mysqldump -h <RDS-Endpoint> -u root -p \
  --single-transaction \
  --routines \
  --triggers \
  db1 > db1_backup.sql

# 백업 복원
mysql -h <RDS-Endpoint> -u root -p db1 < db1_backup.sql
```

## 다음 단계
* Multi-AZ 배포로 고가용성 구성
* 읽기 전용 복제본으로 읽기 성능 향상
* Aurora로 마이그레이션 검토
* 데이터베이스 프록시 활용
* 파티셔닝 전략 수립
