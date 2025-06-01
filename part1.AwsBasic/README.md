# Part 1: AWS Basic - 실습 구조

AWS의 기본 서비스들을 익히고 인프라스트럭처 관리의 기초를 다지는 과정입니다.

## 📂 실습 구조

### 1.1. AWS 소개
* **1.1.1.awsAccountSetup**: AWS 계정 생성 및 기본 설정
* **1.1.2.serviceExploration**: AWS Management Console 탐색
* **1.1.3.regionCheck**: 리전 개념 이해 및 리전 간 이동

### 1.2. EC2 (Elastic Compute Cloud)
* **1.2.1.ec2Creation**: 수동으로 EC2 인스턴스 생성
* **1.2.2.securityGroupSetup**: 보안 그룹 설정 및 관리
* **1.2.3.sshConnection**: SSH 클라이언트 연결 및 EIP 설정

### 1.3. IAM (Identity and Access Management)
* **1.3.1.iamUserCreation**: Terraform용 IAM 사용자 생성
* **1.3.2.roleCreation**: IAM 역할 생성 및 적용
* **1.3.3.mfaSetup**: MFA 설정 및 액세스 키 생성

### 1.4. Terraform (Infrastructure as Code)
* **1.4.1.terraformInstall**: Terraform 설치 및 기본 설정
* **1.4.2.HostProvisioning**: Terraform으로 EC2 인스턴스 생성
* **1.4.3.stateManagement**: Terraform 상태 파일 관리

### 1.5. EBS (Elastic Block Store)
* **1.5.1.manualVolumeCreation**: 수동으로 EBS 볼륨 생성
* **1.5.2.ebsFormat**: EBS 볼륨 포맷 및 마운트
* **1.5.3.Ec2EBS**: Terraform으로 EBS 볼륨 생성
* **1.5.4.UserdataAndCloudinit**: User Data로 EBS 자동 설정

### 1.6. RDS (Relational Database Service)
* **1.6.1.manualRdsSetup**: 수동으로 RDS 인스턴스 생성
* **1.6.2.RDS**: Terraform으로 RDS 구성
* **1.6.3.rdsMonitoring**: RDS 성능 모니터링 및 튜닝

## 🎯 학습 목표

### 기본 개념 이해
* AWS 클라우드 서비스의 기본 개념
* 리전과 가용 영역의 차이점
* 클라우드 인프라의 장점과 특징

### 컴퓨팅 서비스
* EC2 인스턴스 생성 및 관리
* 보안 그룹과 네트워크 보안
* 인스턴스 유형과 성능 최적화

### 보안 관리
* IAM 사용자, 그룹, 역할의 차이점
* 최소 권한 원칙 적용
* MFA를 통한 계정 보안 강화

### 인프라스트럭처 코드
* Infrastructure as Code (IaC) 개념
* Terraform 기본 문법과 활용
* 상태 관리와 버전 제어

### 스토리지 서비스
* EBS 볼륨 타입과 특성
* 볼륨 연결 및 파일시스템 구성
* 백업과 스냅샷 관리

### 데이터베이스 서비스
* 관리형 데이터베이스의 장점
* RDS 인스턴스 설정과 관리
* 데이터베이스 성능 최적화

## 📋 실습 진행 순서

1. **환경 설정**: AWS 계정 생성 → 서비스 탐색 → 리전 설정
2. **기본 인프라**: EC2 생성 → 보안 설정 → SSH 연결
3. **보안 설정**: IAM 사용자 → 역할 설정 → MFA 활성화
4. **자동화 도구**: Terraform 설치 → 인프라 코드 작성 → 상태 관리
5. **스토리지 연동**: EBS 볼륨 생성 → 포맷/마운트 → 자동화
6. **데이터베이스**: RDS 설정 → 연결 테스트 → 성능 모니터링

## ⚠️ 실습 주의사항

### 비용 관리
* Free Tier 한도 확인
* 실습 후 리소스 정리 필수
* EIP 사용 후 반드시 해제

### 보안 고려사항
* 루트 계정 직접 사용 금지
* 강력한 패스워드 설정
* 액세스 키 안전한 보관

### 실습 환경
* 서울 리전(ap-northeast-2) 권장
* t2.micro/t3.micro 인스턴스 사용
* 실습용 태그 일관성 유지

## 🔗 다음 단계

Part 1 완료 후 **Part 2: 애플리케이션 개발 및 배포**로 진행하여:
* 서버리스 컴퓨팅 (Lambda)
* API 관리 (API Gateway)
* CI/CD (CodeDeploy)
* 컨테이너 오케스트레이션 (EKS)
* 로그 분석 (ELK Stack)

을 학습하게 됩니다.

## 📚 참고 자료
* [AWS 공식 문서](https://docs.aws.amazon.com/)
* [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
* [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
