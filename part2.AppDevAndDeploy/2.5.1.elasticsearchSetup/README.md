# 2.5.1: Elasticsearch 클러스터 생성 및 설정

## 실습 목표
* Amazon OpenSearch Service(구 Elasticsearch Service) 이해
* OpenSearch 클러스터 생성 및 기본 설정
* 인덱스 및 매핑 구성
* 보안 설정 및 접근 제어

## OpenSearch 기본 개념
* **클러스터**: 하나 이상의 노드로 구성된 OpenSearch 집합
* **노드**: 데이터를 저장하고 검색 기능을 제공하는 단일 서버
* **인덱스**: 관련 문서들의 컬렉션 (RDB의 테이블과 유사)
* **샤드**: 인덱스를 분할한 단위 (수평 확장)
* **레플리카**: 샤드의 복사본 (고가용성)

## 실습 단계

### Step 1: OpenSearch 도메인 생성

#### 기본 설정
* OpenSearch Service로 이동
* "Create domain" 클릭
* **Domain name**: `log-analysis-cluster`
* **Version**: OpenSearch 2.3 (최신 버전)

#### 배포 설정
* **Deployment type**: Development and testing
* **Data nodes**: 
  - Instance type: t3.small.search
  - Number of nodes: 1
* **Storage**: 
  - EBS storage type: General Purpose (SSD)
  - EBS volume size: 20 GiB

#### 네트워크 설정
* **Network**: Public access
* **Fine-grained access control**: Disabled (실습용)
* **Encryption**: 
  - Encryption at rest: Enabled
  - Node-to-node encryption: Enabled
  - Encryption in transit: Enabled

### Step 2: 접근 정책 설정

#### IP 기반 접근 제어
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:ap-northeast-2:account-id:domain/log-analysis-cluster/*",
      "Condition": {
        "IpAddress": {
          "aws:sourceIp": ["YOUR-IP-ADDRESS/32"]
        }
      }
    }
  ]
}
```

### Step 3: 도메인 생성 완료 대기
* 도메인 생성에는 10-15분 소요
* 상태가 "Active"가 될 때까지 대기
* **Domain endpoint** URL 확인 및 저장

### Step 4: OpenSearch 대시보드 접속

#### 초기 접속
* Domain endpoint에 `/_dashboards` 추가하여 접속
* 예시: `https://search-log-analysis-cluster-xxx.ap-northeast-2.es.amazonaws.com/_dashboards`

#### 기본 설정 확인
* Dev Tools 접속하여 클러스터 상태 확인
```bash
GET _cluster/health

GET _cat/nodes?v

GET _cat/indices?v
```

### Step 5: 인덱스 템플릿 생성

#### 로그 데이터용 인덱스 템플릿
```json
PUT _index_template/web-logs-template
{
  "index_patterns": ["web-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "index.refresh_interval": "1s"
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "client_ip": {
          "type": "ip"
        },
        "request_method": {
          "type": "keyword"
        },
        "request_url": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "response_code": {
          "type": "integer"
        },
        "response_size": {
          "type": "long"
        },
        "user_agent": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword"
            }
          }
        },
        "referrer": {
          "type": "keyword"
        }
      }
    }
  }
}
```

### Step 6: 샘플 데이터 입력

#### 웹 로그 샘플 데이터
```json
POST web-logs-2025.01/_doc
{
  "@timestamp": "2025-01-15T10:30:00Z",
  "client_ip": "192.168.1.100",
  "request_method": "GET",
  "request_url": "/index.html",
  "response_code": 200,
  "response_size": 1024,
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "referrer": "https://google.com"
}

POST web-logs-2025.01/_doc
{
  "@timestamp": "2025-01-15T10:31:00Z",
  "client_ip": "192.168.1.101",
  "request_method": "POST",
  "request_url": "/api/login",
  "response_code": 401,
  "response_size": 256,
  "user_agent": "curl/7.68.0",
  "referrer": "-"
}

POST web-logs-2025.01/_doc
{
  "@timestamp": "2025-01-15T10:32:00Z",
  "client_ip": "10.0.1.50",
  "request_method": "GET",
  "request_url": "/dashboard",
  "response_code": 500,
  "response_size": 512,
  "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
  "referrer": "https://internal.company.com"
}
```

#### 벌크 데이터 입력 (성능 테스트용)
```bash
# Python 스크립트로 대량 데이터 생성 예시
import json
import random
from datetime import datetime, timedelta
import requests

def generate_log_data(count=1000):
    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = ["/", "/index.html", "/api/users", "/api/login", "/dashboard", "/admin"]
    codes = [200, 201, 400, 401, 403, 404, 500, 502]
    
    logs = []
    base_time = datetime.now()
    
    for i in range(count):
        log = {
            "@timestamp": (base_time - timedelta(minutes=random.randint(0, 1440))).isoformat() + "Z",
            "client_ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            "request_method": random.choice(methods),
            "request_url": random.choice(urls),
            "response_code": random.choice(codes),
            "response_size": random.randint(100, 5000),
            "user_agent": "Mozilla/5.0 (Sample Browser)",
            "referrer": random.choice(["-", "https://google.com", "https://github.com"])
        }
        logs.append(log)
    
    return logs

# 실행 예시 (로컬에서)
# logs = generate_log_data(1000)
# 벌크 API로 OpenSearch에 전송
```

### Step 7: 기본 검색 쿼리 실습

#### 전체 데이터 조회
```json
GET web-logs-*/_search
{
  "query": {
    "match_all": {}
  },
  "size": 10
}
```

#### 조건별 검색
```json
# 에러 로그만 조회 (4xx, 5xx)
GET web-logs-*/_search
{
  "query": {
    "range": {
      "response_code": {
        "gte": 400
      }
    }
  }
}

# 특정 IP에서의 요청
GET web-logs-*/_search
{
  "query": {
    "term": {
      "client_ip": "192.168.1.100"
    }
  }
}

# 시간 범위 검색
GET web-logs-*/_search
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "2025-01-15T10:00:00Z",
        "lte": "2025-01-15T11:00:00Z"
      }
    }
  }
}
```

#### 집계 쿼리
```json
# HTTP 상태 코드별 집계
GET web-logs-*/_search
{
  "size": 0,
  "aggs": {
    "status_codes": {
      "terms": {
        "field": "response_code"
      }
    }
  }
}

# 시간별 요청 수 집계
GET web-logs-*/_search
{
  "size": 0,
  "aggs": {
    "requests_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "1h"
      }
    }
  }
}

# Top 10 IP 주소
GET web-logs-*/_search
{
  "size": 0,
  "aggs": {
    "top_ips": {
      "terms": {
        "field": "client_ip",
        "size": 10
      }
    }
  }
}
```

### Step 8: 인덱스 라이프사이클 관리

#### ISM(Index State Management) 정책 생성
```json
PUT _plugins/_ism/policies/web-logs-policy
{
  "policy": {
    "description": "Web logs retention policy",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "warm",
            "conditions": {
              "min_index_age": "7d"
            }
          }
        ]
      },
      {
        "name": "warm",
        "actions": [
          {
            "allocation": {
              "require": {
                "box_type": "warm"
              }
            }
          }
        ],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "30d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ]
      }
    ]
  }
}
```

### Step 9: 모니터링 및 알림 설정

#### 클러스터 모니터링
* CloudWatch 메트릭 확인:
  - IndexingRate
  - SearchRate
  - ClusterStatus
  - StorageUtilization

#### 알림 설정
```json
# 디스크 사용량 90% 초과 시 알림
PUT _plugins/_alerting/monitors/disk-usage-monitor
{
  "type": "monitor",
  "name": "High Disk Usage Alert",
  "monitor_type": "query_level_monitor",
  "enabled": true,
  "schedule": {
    "period": {
      "interval": 1,
      "unit": "MINUTES"
    }
  },
  "inputs": [
    {
      "search": {
        "indices": ["_cluster"],
        "query": {
          "size": 0,
          "query": {
            "match_all": {}
          }
        }
      }
    }
  ],
  "triggers": [
    {
      "name": "Disk usage high",
      "severity": "1",
      "condition": {
        "script": {
          "source": "ctx.results[0].hits.total.value > 0",
          "lang": "painless"
        }
      },
      "actions": [
        {
          "name": "send-email",
          "destination_id": "email-destination",
          "message_template": {
            "source": "Disk usage is above 90%"
          }
        }
      ]
    }
  ]
}
```

## 보안 모범 사례

### VPC 내 배포 (프로덕션 권장)
* Private subnet에 클러스터 배포
* VPC endpoint 사용
* Security Group으로 접근 제어

### Fine-grained Access Control
* 사용자별 역할 기반 접근 제어
* 인덱스별 권한 관리
* 필드 레벨 보안

### 네트워크 보안
* HTTPS 강제 사용
* IP 기반 접근 제한
* AWS WAF 연동

## 성능 최적화

### 인덱싱 최적화
* 적절한 샤드 수 설정
* 벌크 요청 사용
* 리프레시 간격 조정

### 검색 최적화
* 적절한 매핑 타입 사용
* 쿼리 캐싱 활용
* 불필요한 필드 제외

### 저장소 최적화
* 압축 설정
* 인덱스 템플릿 활용
* 라이프사이클 정책 적용

## 문제 해결

### 일반적인 이슈

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| 클러스터 상태 Red | 샤드 할당 실패 | 샤드 재할당 또는 인덱스 복구 |
| 검색 응답 느림 | 부적절한 쿼리 | 쿼리 최적화 및 인덱스 튜닝 |
| 디스크 공간 부족 | 인덱스 크기 증가 | 라이프사이클 정책 적용 |
| 메모리 부족 | 힙 사이즈 부족 | 인스턴스 타입 업그레이드 |

### 유용한 진단 명령어
```bash
# 클러스터 상태 확인
GET _cluster/health?pretty

# 샤드 상태 확인
GET _cat/shards?v&s=index

# 인덱스 설정 확인
GET web-logs-*/_settings

# 매핑 확인
GET web-logs-*/_mapping

# 세그먼트 정보
GET _cat/segments?v

# 노드 상태
GET _nodes/stats
```

## 관련 문서
* [Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/)
* [OpenSearch Documentation](https://opensearch.org/docs/)
* [Index State Management](https://opensearch.org/docs/latest/im-plugin/ism/)
