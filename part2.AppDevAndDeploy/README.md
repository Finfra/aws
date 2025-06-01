# Part 2: 애플리케이션 개발 및 배포 - 실습 구조

클라우드 네이티브 애플리케이션 개발, 배포, 모니터링의 전 과정을 다루는 고급 과정입니다.

## 📂 실습 구조

### 2.1. Lambda (서버리스 컴퓨팅)
* **2.1.1.lambdaEventTrigger**: S3 이벤트 트리거 설정
* **2.1.2.lambdaCostOptimization**: Lambda 비용 최적화 전략

### 2.2. API Gateway (API 관리 서비스)
* **2.2.1.apiGatewayRest**: REST API 생성 및 기본 설정
* **2.2.2.lambdaIntegration**: Lambda와 API Gateway 통합

### 2.3. CodeDeploy (애플리케이션 배포)
* **2.3.1.codeDeploySetup**: CodeDeploy 환경 설정 및 기본 배포
* **2.3.2.ec2Deployment**: EC2 인스턴스 대상 배포 전략
* **2.3.3.blueGreenDeploy**: Blue/Green 무중단 배포 구현

### 2.4. EKS (Elastic Kubernetes Service)
* **2.4.1.eksClusterSetup**: EKS 클러스터 생성 및 노드 그룹 설정
* **2.4.2.appDeployment**: 애플리케이션 배포 및 스케일링
* **2.4.3.helmManagement**: Helm 패키지 관리 및 차트 작성

### 2.5. ELK Stack (로그 분석)
* **2.5.1.elasticsearchSetup**: Elasticsearch 클러스터 구성
* **2.5.2.logstashCollection**: Logstash 로그 수집 파이프라인
* **2.5.3.kibanaDashboard**: Kibana 대시보드 및 시각화

## 🎯 학습 목표

### 서버리스 아키텍처
* Function as a Service (FaaS) 개념
* 이벤트 기반 아키텍처 설계
* 서버리스 비용 최적화 전략
* Cold Start 최소화 기법

### API 설계 및 관리
* RESTful API 설계 원칙
* API Gateway를 통한 트래픽 관리
* API 보안 및 인증/인가
* API 버전 관리 전략

### CI/CD 파이프라인
* 지속적 통합/배포 개념
* 배포 전략 (Rolling, Blue/Green, Canary)
* 인프라와 애플리케이션 자동화
* 배포 롤백 및 모니터링

### 컨테이너 오케스트레이션
* Kubernetes 기본 개념
* 워크로드 배포 및 관리
* 서비스 메시 및 네트워킹
* 패키지 관리 (Helm)

### 로그 및 모니터링
* 중앙집중식 로깅 시스템
* 로그 수집 및 파싱
* 실시간 모니터링 대시보드
* 알림 및 이상 탐지

## 📋 실습 진행 순서

### Phase 1: 서버리스 기초
1. **Lambda 함수 개발**: 이벤트 처리 → 비용 최적화
2. **API 구축**: REST API 생성 → Lambda 통합 → 보안 설정

### Phase 2: 배포 자동화
3. **CI/CD 구축**: CodeDeploy 설정 → EC2 배포 → Blue/Green 전략

### Phase 3: 컨테이너 환경
4. **Kubernetes 클러스터**: EKS 설정 → 앱 배포 → Helm 관리

### Phase 4: 운영 및 모니터링
5. **로그 분석 시스템**: ELK Stack 구축 → 대시보드 구성

## 🏗️ 아키텍처 패턴

### 마이크로서비스 아키텍처
* 서비스 분리 및 독립 배포
* API Gateway를 통한 서비스 통합
* 서비스 간 통신 패턴

### 이벤트 기반 아키텍처
* 비동기 메시징
* 이벤트 소싱
* CQRS (Command Query Responsibility Segregation)

### 클라우드 네이티브 패턴
* 12-Factor App 원칙
* 장애 복구 및 자가 치유
* 탄력적 스케일링

## 🔧 사용 기술 스택

### 컴퓨팅
* AWS Lambda (서버리스)
* Amazon EKS (컨테이너)
* Amazon EC2 (가상머신)

### 네트워킹
* Amazon API Gateway
* Application Load Balancer
* Amazon VPC

### 데이터베이스
* Amazon RDS
* Amazon DynamoDB
* Amazon S3

### 모니터링
* Amazon CloudWatch
* Elasticsearch
* Kibana & Grafana

### 개발 도구
* AWS CodeDeploy
* Terraform
* Helm
* Docker

## 📊 성능 및 확장성

### 자동 스케일링
* Horizontal Pod Autoscaler (HPA)
* Vertical Pod Autoscaler (VPA)
* Cluster Autoscaler

### 부하 분산
* Application Load Balancer
* Service Mesh (Istio)
* DNS 기반 라우팅

### 캐싱 전략
* CloudFront CDN
* ElastiCache
* 애플리케이션 레벨 캐싱

## ⚠️ 실습 주의사항

### 리소스 관리
* EKS 클러스터는 시간당 $0.10 과금
* NAT Gateway 및 Load Balancer 비용 주의
* 실습 후 반드시 리소스 정리

### 보안 고려사항
* IAM 역할 최소 권한 적용
* 네트워크 보안 그룹 설정
* 컨테이너 이미지 보안 스캔

### 성능 최적화
* 적절한 인스턴스 타입 선택
* 리소스 요청/제한 설정
* 모니터링 메트릭 활용

## 🔄 DevOps 문화

### 지속적 개선
* 피드백 루프 구축
* 메트릭 기반 의사결정
* 장애 대응 및 포스트 모템

### 협업 도구
* Git 기반 버전 관리
* Infrastructure as Code
* 문서화 및 지식 공유

## 🔗 연계 학습

### 고급 주제
* Service Mesh (Istio, Linkerd)
* GitOps (ArgoCD, Flux)
* 보안 강화 (OPA Gatekeeper)
* 멀티 클라우드 전략

### 인증 준비
* AWS Certified Developer
* AWS Certified DevOps Engineer
* Certified Kubernetes Administrator (CKA)

## 📚 참고 자료
* [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
* [Kubernetes 공식 문서](https://kubernetes.io/docs/)
* [Cloud Native Computing Foundation](https://www.cncf.io/)
* [12-Factor App](https://12factor.net/)
* [ELK Stack 가이드](https://www.elastic.co/guide/)
