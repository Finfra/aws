# 1.3.2: Role 생성 및 적용

## 목표
* IAM 역할의 개념 이해
* EC2 인스턴스용 역할 생성 및 연결
* 서비스 간 권한 위임 설정

## 실습 단계

### 1. IAM 역할 개념 이해
* **역할(Role)**: 임시 자격 증명을 제공하는 IAM 엔티티
* **사용자와의 차이**: 영구 자격 증명 vs 임시 자격 증명
* **신뢰 관계**: 어떤 엔티티가 역할을 맡을 수 있는지 정의

### 2. EC2 인스턴스용 역할 생성
* IAM Console → Roles → Create role
* Trusted entity type: `AWS service`
* Use case: `EC2`
* Permissions policies 선택:
  - `AmazonS3ReadOnlyAccess`
  - `CloudWatchAgentServerPolicy`

### 3. 역할을 EC2 인스턴스에 연결
* EC2 Console → Instances → Actions → Security → Modify IAM role
* 생성한 역할 선택하여 적용

### 4. 역할 권한 테스트
```bash
# AWS CLI로 S3 버킷 목록 확인 (Access Key 없이)
aws s3 ls

# 인스턴스 메타데이터에서 임시 자격 증명 확인
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### 5. 교차 계정 역할 생성
* 다른 AWS 계정이나 서비스가 역할을 맡을 수 있도록 설정
* Trust policy 수정하여 외부 계정 ARN 추가

## 역할 사용 사례
* **EC2 → S3**: 인스턴스에서 S3 버킷 접근
* **Lambda → DynamoDB**: Lambda 함수에서 DB 접근
* **Cross-Account**: 다른 계정 리소스 접근

## Trust Policy 예시
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## 주의사항
* 최소 권한 원칙 적용
* 역할 세션 시간 제한 설정
* CloudTrail로 역할 사용 추적

## 다음 단계
* 교차 계정 역할 설정
* STS(Security Token Service) 활용
