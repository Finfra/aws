# 1.3.3: MFA 셋팅 및 키 생성

## 목표
* MFA(Multi-Factor Authentication) 설정으로 보안 강화
* Access Key 및 Secret Key 생성 및 관리
* 보안 모범 사례 적용

## 실습 단계

### 1. MFA 디바이스 설정
* IAM Console → Users → 사용자 선택 → Security credentials
* Multi-factor authentication (MFA) → Assign MFA device
* Virtual MFA device 선택

### 2. 인증 앱 설정
* Google Authenticator, Authy, Microsoft Authenticator 등 사용
* QR 코드 스캔 또는 secret key 수동 입력
* 연속된 두 개의 MFA 코드 입력하여 활성화

### 3. Access Key 생성
* Security credentials → Access keys → Create access key
* Use case: `Command Line Interface (CLI)`
* **Download .csv file** 클릭하여 키 정보 저장
* **중요**: Secret key는 한 번만 표시됨

### 4. AWS CLI 구성
```bash
# AWS CLI 설치 (Ubuntu)
sudo apt update
sudo apt install awscli

# 자격 증명 구성
aws configure
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]  
# Default region name: ap-northeast-2
# Default output format: json
```

### 5. MFA 필수 정책 적용
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "iam:GetUser",
        "iam:ListMFADevices",
        "iam:ListVirtualMFADevices",
        "iam:ResyncMFADevice",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### 6. 임시 자격 증명 사용
```bash
# MFA와 함께 임시 자격 증명 요청
aws sts get-session-token --serial-number arn:aws:iam::123456789012:mfa/user-name --token-code 123456

# 임시 자격 증명을 환경변수로 설정
export AWS_ACCESS_KEY_ID=temp-access-key
export AWS_SECRET_ACCESS_KEY=temp-secret-key
export AWS_SESSION_TOKEN=temp-session-token
```

## 보안 모범 사례
* **키 로테이션**: 정기적으로 Access Key 갱신
* **최소 권한**: 필요한 권한만 부여
* **키 보관**: 안전한 위치에 저장 (1Password, AWS Secrets Manager 등)
* **모니터링**: CloudTrail로 API 호출 추적

## 주의사항
* Root 계정에도 MFA 설정 필수
* Access Key를 코드에 하드코딩 금지
* 사용하지 않는 키는 즉시 삭제
* MFA 디바이스 분실 시 복구 계획 수립

## 다음 단계
* AWS Secrets Manager 활용
* IAM Identity Center 설정
* 단일 사인온(SSO) 구성
