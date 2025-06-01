# 2.5.2. Logstash로 로그 데이터 수집

## 개요
Logstash를 사용하여 다양한 소스에서 로그 데이터를 수집하고 처리하는 실습

## 실습 목표
* Logstash 설치 및 구성
* 다양한 입력 소스 설정
* 로그 필터링 및 파싱
* Elasticsearch 출력 설정

## 실습 단계

### 1. Logstash 설치 및 구성
* EC2 인스턴스에 Logstash 설치
* 입력, 필터, 출력 플러그인 설정

### 2. 로그 수집 설정
```ruby
input {
  file {
    path => "/var/log/nginx/access.log"
    start_position => "beginning"
    type => "nginx-access"
  }
  
  beats {
    port => 5044
  }
}

filter {
  if [type] == "nginx-access" {
    grok {
      match => { "message" => "%{NGINXACCESS}" }
    }
    
    date {
      match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["your-elasticsearch-endpoint"]
    index => "logstash-nginx-%{+YYYY.MM.dd}"
  }
}
```

### 3. Beats를 이용한 로그 수집
* Filebeat 설치 및 설정
* 다양한 로그 소스에서 데이터 수집
* 로그 파싱 및 구조화

## 주요 포인트
* Grok 패턴 작성
* 필터 체인 구성
* 성능 튜닝
