# 1.3.1: Terraform을 위한 IAM 사용자 생성

## 목표
* Terraform에서 사용할 IAM 사용자 생성
* 적절한 권한 부여 및 Access Key 생성

## 실습 단계

### 1. IAM 서비스 접속
* AWS Console에서 IAM 서비스 접속
* URL: https://us-east-1.console.aws.amazon.com/iamv2/home#/users

### 2. "terraform" 사용자 생성
* Users → Add users 클릭
* User name: `terraform` 입력
* Access type: `Programmatic access` 선택

### 3. 권한 부여
* Attach existing policies directly 선택
* 다음 정책 부여:
  - `AdministratorAccess`
  - `PowerUserAccess`

### 4. Access Key 및 Secret Key 생성
* Create user 후 Access Key 정보 확인
* `Download.csv file`로 보안 키 저장
* **중요**: 이 정보는 한 번만 표시되므로 반드시 저장

### 5. 환경변수 설정
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-northeast-2"
```

## 주의사항
* Access Key는 안전한 곳에 보관
* 정기적인 키 로테이션 권장
* 불필요한 권한은 최소화하여 부여

## 다음 단계
* Terraform 설치 및 설정
* AWS Provider 구성
