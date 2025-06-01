# 2.4.1: EKS 클러스터 생성 및 노드 그룹 설정

## 실습 목표
* Terraform을 이용한 EKS 클러스터 생성
* VPC 및 네트워킹 구성
* IAM 역할 및 정책 설정
* 노드 그룹 설정 및 관리

## EKS 기본 개념
* **EKS (Elastic Kubernetes Service)**: AWS에서 관리하는 Kubernetes 서비스
* **Control Plane**: Kubernetes API 서버 및 관리 구성 요소
* **Node Group**: 워커 노드들의 그룹 (EC2 인스턴스)
* **Fargate**: 서버리스 컨테이너 실행 환경

## 실습 단계

### Step 1: 사전 준비
* Terraform 설치 완료 (1.4.1 실습 완료)
* AWS CLI 구성 완료
* kubectl 설치 필요

### Step 2: Terraform 코드 준비

#### main.tf 파일 생성
```hcl
# Terraform을 이용한 AWS EKS 클러스터 생성

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = "learning"
      Project     = "eks-cluster"
      ManagedBy   = "terraform"
    }
  }
}

# 사용 가능한 가용 영역 조회
data "aws_availability_zones" "available" {
  state = "available"
}

# 현재 AWS 계정 정보
data "aws_caller_identity" "current" {}
```

#### variables.tf 파일 생성
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "my-eks-cluster"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "node_group_desired_size" {
  description = "Desired number of nodes"
  type        = number
  default     = 2
}

variable "node_group_min_size" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "node_group_max_size" {
  description = "Maximum number of nodes"
  type        = number
  default     = 4
}

variable "node_instance_types" {
  description = "EC2 instance types for nodes"
  type        = list(string)
  default     = ["t3.medium"]
}
```

#### vpc.tf 파일 생성
```hcl
# VPC 생성
resource "aws_vpc" "eks_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.cluster_name}-vpc"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

# 인터넷 게이트웨이
resource "aws_internet_gateway" "eks_igw" {
  vpc_id = aws_vpc.eks_vpc.id

  tags = {
    Name = "${var.cluster_name}-igw"
  }
}

# Public 서브넷
resource "aws_subnet" "eks_public_subnet" {
  count = 2

  vpc_id                  = aws_vpc.eks_vpc.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.cluster_name}-public-subnet-${count.index + 1}"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb" = "1"
  }
}

# Private 서브넷
resource "aws_subnet" "eks_private_subnet" {
  count = 2

  vpc_id            = aws_vpc.eks_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.cluster_name}-private-subnet-${count.index + 1}"
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "eks_nat_eip" {
  count = 2
  domain = "vpc"

  tags = {
    Name = "${var.cluster_name}-nat-eip-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.eks_igw]
}

# NAT Gateway
resource "aws_nat_gateway" "eks_nat_gateway" {
  count = 2

  allocation_id = aws_eip.eks_nat_eip[count.index].id
  subnet_id     = aws_subnet.eks_public_subnet[count.index].id

  tags = {
    Name = "${var.cluster_name}-nat-gateway-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.eks_igw]
}

# Public 라우팅 테이블
resource "aws_route_table" "eks_public_rt" {
  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks_igw.id
  }

  tags = {
    Name = "${var.cluster_name}-public-rt"
  }
}

# Private 라우팅 테이블
resource "aws_route_table" "eks_private_rt" {
  count = 2

  vpc_id = aws_vpc.eks_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.eks_nat_gateway[count.index].id
  }

  tags = {
    Name = "${var.cluster_name}-private-rt-${count.index + 1}"
  }
}

# 라우팅 테이블 연결 - Public
resource "aws_route_table_association" "eks_public_rta" {
  count = 2

  subnet_id      = aws_subnet.eks_public_subnet[count.index].id
  route_table_id = aws_route_table.eks_public_rt.id
}

# 라우팅 테이블 연결 - Private
resource "aws_route_table_association" "eks_private_rta" {
  count = 2

  subnet_id      = aws_subnet.eks_private_subnet[count.index].id
  route_table_id = aws_route_table.eks_private_rt[count.index].id
}
```

#### iam.tf 파일 생성
```hcl
# EKS 클러스터 서비스 역할
resource "aws_iam_role" "eks_cluster_role" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-cluster-role"
  }
}

# EKS 클러스터 정책 연결
resource "aws_iam_role_policy_attachment" "eks_cluster_AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}

resource "aws_iam_role_policy_attachment" "eks_cluster_AmazonEKSVPCResourceController" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSVPCResourceController"
  role       = aws_iam_role.eks_cluster_role.name
}

# EKS 노드 그룹 역할
resource "aws_iam_role" "eks_node_group_role" {
  name = "${var.cluster_name}-node-group-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-node-group-role"
  }
}

# 노드 그룹 정책 연결
resource "aws_iam_role_policy_attachment" "eks_node_group_AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_node_group_AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node_group_role.name
}

resource "aws_iam_role_policy_attachment" "eks_node_group_AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node_group_role.name
}

# 추가 권한: CloudWatch 로깅
resource "aws_iam_role_policy_attachment" "eks_node_group_CloudWatchAgentServerPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.eks_node_group_role.name
}
```

#### eks.tf 파일 생성
```hcl
# EKS 클러스터
resource "aws_eks_cluster" "eks_cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.28"

  vpc_config {
    subnet_ids              = concat(aws_subnet.eks_public_subnet[*].id, aws_subnet.eks_private_subnet[*].id)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
    security_group_ids      = [aws_security_group.eks_cluster_sg.id]
  }

  # 로깅 활성화
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = {
    Name = var.cluster_name
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.eks_cluster_AmazonEKSVPCResourceController,
    aws_cloudwatch_log_group.eks_cluster_log_group
  ]
}

# CloudWatch 로그 그룹
resource "aws_cloudwatch_log_group" "eks_cluster_log_group" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = 7

  tags = {
    Name = "${var.cluster_name}-cluster-logs"
  }
}

# EKS 노드 그룹
resource "aws_eks_node_group" "eks_node_group" {
  cluster_name    = aws_eks_cluster.eks_cluster.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.eks_node_group_role.arn
  subnet_ids      = aws_subnet.eks_private_subnet[*].id
  
  instance_types = var.node_instance_types
  
  scaling_config {
    desired_size = var.node_group_desired_size
    max_size     = var.node_group_max_size
    min_size     = var.node_group_min_size
  }

  update_config {
    max_unavailable = 1
  }

  # Launch Template
  launch_template {
    id      = aws_launch_template.eks_node_group_lt.id
    version = aws_launch_template.eks_node_group_lt.latest_version
  }

  tags = {
    Name = "${var.cluster_name}-node-group"
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_node_group_AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.eks_node_group_AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.eks_node_group_AmazonEC2ContainerRegistryReadOnly,
  ]
}

# Launch Template for Node Group
resource "aws_launch_template" "eks_node_group_lt" {
  name_prefix   = "${var.cluster_name}-node-group-"
  image_id      = data.aws_ami.eks_worker.id
  instance_type = var.node_instance_types[0]

  vpc_security_group_ids = [aws_security_group.eks_node_group_sg.id]

  user_data = base64encode(templatefile("${path.module}/userdata.sh", {
    cluster_name = var.cluster_name
    endpoint     = aws_eks_cluster.eks_cluster.endpoint
    ca_data      = aws_eks_cluster.eks_cluster.certificate_authority[0].data
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.cluster_name}-node"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

# EKS Worker Node AMI
data "aws_ami" "eks_worker" {
  filter {
    name   = "name"
    values = ["amazon-eks-node-1.28-v*"]
  }

  most_recent = true
  owners      = ["602401143452"] # Amazon EKS AMI Account ID
}
```

#### security_groups.tf 파일 생성
```hcl
# EKS 클러스터 보안 그룹
resource "aws_security_group" "eks_cluster_sg" {
  name_prefix = "${var.cluster_name}-cluster-sg"
  vpc_id      = aws_vpc.eks_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-cluster-sg"
  }
}

resource "aws_security_group_rule" "cluster_ingress_node_443" {
  description              = "Allow pods to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_cluster_sg.id
  source_security_group_id = aws_security_group.eks_node_group_sg.id
  to_port                  = 443
  type                     = "ingress"
}

# EKS 노드 그룹 보안 그룹
resource "aws_security_group" "eks_node_group_sg" {
  name_prefix = "${var.cluster_name}-node-sg"
  vpc_id      = aws_vpc.eks_vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-node-sg"
  }
}

resource "aws_security_group_rule" "node_ingress_self" {
  description              = "Allow node to communicate with each other"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.eks_node_group_sg.id
  source_security_group_id = aws_security_group.eks_node_group_sg.id
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "node_ingress_cluster" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane"
  from_port                = 1025
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_node_group_sg.id
  source_security_group_id = aws_security_group.eks_cluster_sg.id
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "node_ingress_cluster_443" {
  description              = "Allow pods running extension API servers on port 443 to receive communication from cluster control plane"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.eks_node_group_sg.id
  source_security_group_id = aws_security_group.eks_cluster_sg.id
  to_port                  = 443
  type                     = "ingress"
}
```

#### userdata.sh 파일 생성
```bash
#!/bin/bash
/etc/eks/bootstrap.sh ${cluster_name}
```

#### outputs.tf 파일 생성
```hcl
output "cluster_id" {
  description = "EKS cluster ID"
  value       = aws_eks_cluster.eks_cluster.id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = aws_eks_cluster.eks_cluster.arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.eks_cluster.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = aws_eks_cluster.eks_cluster.vpc_config[0].cluster_security_group_id
}

output "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  value       = aws_eks_cluster.eks_cluster.version
}

output "cluster_ca_certificate" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.eks_cluster.certificate_authority[0].data
}

output "node_group_arn" {
  description = "Amazon Resource Name (ARN) of the EKS Node Group"
  value       = aws_eks_node_group.eks_node_group.arn
}

output "node_group_status" {
  description = "Status of the EKS Node Group"
  value       = aws_eks_node_group.eks_node_group.status
}

output "kubectl_config_command" {
  description = "kubectl config command"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
}
```

### Step 3: EKS 클러스터 배포

#### Terraform 초기화 및 배포
```bash
# 폴더 이동
cd ~/aws/2.4.1.eksClusterSetup

# Terraform 초기화
terraform init

# 계획 확인
terraform plan

# 배포 실행
terraform apply -auto-approve
```

### Step 4: kubectl 설치 및 설정

#### kubectl 다운로드 및 설치
```bash
# kubectl 최신 버전 다운로드
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# 실행 권한 부여
chmod +x ./kubectl

# 전역 경로로 이동
sudo mv ./kubectl /usr/local/bin/kubectl

# 설치 확인
kubectl version --client
```

#### EKS 클러스터 연결 설정
```bash
# 클러스터 이름 설정
eksName=my-eks-cluster

# 기존 kubeconfig 백업 (선택사항)
mv ~/.kube/config ~/.kube/config.backup 2>/dev/null || true

# EKS 클러스터 연결 설정
aws eks update-kubeconfig --region ap-northeast-2 --name $eksName

# 설정 확인
cat ~/.kube/config
```

### Step 5: 클러스터 검증

#### 기본 연결 확인
```bash
# kubectl 버전 확인
kubectl version --short

# 클러스터 정보 확인
kubectl cluster-info

# 노드 상태 확인
kubectl get nodes

# 노드 상세 정보
kubectl get nodes -o wide

# 클러스터 상태 확인
kubectl get componentstatuses
```

#### 네임스페이스 및 시스템 Pod 확인
```bash
# 모든 네임스페이스 확인
kubectl get namespaces

# kube-system 네임스페이스의 Pod 확인
kubectl get pods -n kube-system

# CoreDNS 상태 확인
kubectl get deployment -n kube-system coredns

# AWS Load Balancer Controller 설치 확인 (추후 설치)
kubectl get deployment -n kube-system aws-load-balancer-controller
```

## AWS CLI 문제 해결

### AWS CLI 재설치 (필요시)
```bash
# 관리자 권한으로 전환
sudo -i

# 기존 AWS CLI 제거
python3 -m pip uninstall --break-system-packages awscli

# 최신 AWS CLI 설치
python3 -m pip install --break-system-packages awscli

# SSL 관련 패키지 업그레이드
pip install pyopenssl --upgrade
pip install pyopenssl --break-system-packages --upgrade

# 일반 사용자로 복귀
exit

# AWS 자격 증명 설정
aws configure
```

## 모니터링 및 로깅

### CloudWatch 로그 확인
```bash
# AWS CLI로 로그 그룹 확인
aws logs describe-log-groups --log-group-name-prefix "/aws/eks"

# 로그 스트림 확인
aws logs describe-log-streams --log-group-name "/aws/eks/my-eks-cluster/cluster"
```

### 클러스터 메트릭 확인
```bash
# 노드 리소스 사용량 확인
kubectl top nodes

# Pod 리소스 사용량 확인
kubectl top pods --all-namespaces
```

## 비용 관리

### 리소스 사용량 확인
* EKS 클러스터: 시간당 $0.10
* EC2 노드: 인스턴스 타입에 따라 과금
* NAT Gateway: 시간당 $0.045 + 데이터 처리 비용
* EBS 볼륨: 사용량에 따라 과금

### 실습 후 정리
```bash
# Terraform으로 모든 리소스 삭제
terraform destroy -auto-approve

# kubeconfig 파일 정리 (선택사항)
rm ~/.kube/config
```

## 문제 해결

### 일반적인 이슈

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| kubectl 명령 실패 | kubeconfig 설정 오류 | aws eks update-kubeconfig 재실행 |
| 노드가 Ready 상태가 아님 | CNI 플러그인 문제 | aws-node daemonset 확인 |
| Terraform apply 실패 | IAM 권한 부족 | AdministratorAccess 정책 확인 |
| 클러스터 생성 시간 초과 | 서브넷 설정 오류 | VPC 및 서브넷 설정 재확인 |

### 유용한 디버깅 명령어
```bash
# 노드 상세 정보 및 이벤트
kubectl describe node <node-name>

# Pod 로그 확인
kubectl logs <pod-name> -n <namespace>

# 이벤트 확인
kubectl get events --sort-by=.metadata.creationTimestamp

# 클러스터 권한 확인
kubectl auth can-i "*" "*"
```

## 다음 단계
* 2.4.2: 애플리케이션 배포 및 스케일링
* 2.4.3: Helm을 사용한 패키지 관리

## 관련 문서
* [Amazon EKS 사용자 가이드](https://docs.aws.amazon.com/eks/)
* [Kubernetes 공식 문서](https://kubernetes.io/docs/)
* [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
