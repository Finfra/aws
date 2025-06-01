# 1.4.3: Terraform 상태 파일 관리 및 백업

## 목표
* terraform.tfstate 파일의 중요성 이해
* 상태 파일 백업 및 관리 방법 학습
* terraform state 명령어 활용

## 실습 단계

### 1. Terraform State 파일 이해
* **terraform.tfstate**: 인프라의 현재 상태를 추적하는 JSON 파일
* **중요성**: 실제 인프라와 Terraform 구성 간의 매핑 정보
* **위치**: 프로젝트 루트 디렉토리에 생성

### 2. State 파일 내용 확인
```bash
# 현재 상태 확인
terraform show

# 상태 파일을 사람이 읽기 쉬운 형태로 출력
terraform show -json | jq '.'

# 특정 리소스 상태 확인
terraform state show aws_instance.example
```

### 3. State 명령어 활용
```bash
# 상태에 있는 모든 리소스 목록
terraform state list

# 특정 리소스의 상세 정보
terraform state show aws_instance.web

# 리소스 이름 변경
terraform state mv aws_instance.old_name aws_instance.new_name

# 상태에서 리소스 제거 (실제 리소스는 유지)
terraform state rm aws_instance.example
```

### 4. State 파일 백업
```bash
# 수동 백업
cp terraform.tfstate terraform.tfstate.backup.$(date +%Y%m%d_%H%M%S)

# 백업 디렉토리 생성
mkdir -p backups
cp terraform.tfstate backups/terraform.tfstate.$(date +%Y%m%d_%H%M%S)
```

### 5. Remote State 설정 (S3 백엔드)
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "path/to/my/key"
    region = "ap-northeast-2"
    
    # State 잠금을 위한 DynamoDB 테이블
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### 6. State 마이그레이션
```bash
# 로컬에서 원격으로 마이그레이션
terraform init -migrate-state

# 백엔드 재구성
terraform init -reconfigure
```

## State 파일 구조 예시
```json
{
  "version": 4,
  "terraform_version": "1.0.0",
  "serial": 1,
  "lineage": "unique-id",
  "outputs": {},
  "resources": [
    {
      "mode": "managed",
      "type": "aws_instance",
      "name": "example",
      "provider": "provider[\"registry.terraform.io/hashicorp/aws\"]",
      "instances": [...]
    }
  ]
}
```

## 주의사항
* **보안**: State 파일에는 민감한 정보 포함 가능
* **동시성**: 여러 사용자가 동시에 작업할 때 충돌 방지
* **버전 관리**: State 파일을 Git에 커밋하지 말 것
* **백업**: 정기적인 백업 및 복구 계획 수립

## 문제 해결
```bash
# State 파일 손상 시 강제 해제
terraform force-unlock LOCK_ID

# State 새로고침
terraform refresh

# Import 기존 리소스
terraform import aws_instance.example i-1234567890abcdef0
```

## 다음 단계
* Terraform Cloud/Enterprise 활용
* State 파일 암호화
* 팀 협업을 위한 워크플로우 구성
