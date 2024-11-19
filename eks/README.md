## Terraform Apply
```
cd ~/aws/eks
terraform apply -auto-approve
```
## **kubectl 다운로드 및 설치**
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```
- Kubernetes CLI 툴인 `kubectl`을 다운로드함.
- 해당 파일에 실행 권한을 부여 (`chmod +x ./kubectl`).
- `/usr/local/bin`으로 이동시켜 전역적으로 사용할 수 있게 설정.

## **EKS 클러스터 연결 설정**
```bash
eksName=my-eks-cluster
rm ~/.kube/config
aws eks update-kubeconfig --region ap-northeast-2 --name $eksName
```
- 기존의 kubeconfig 파일을 삭제 (`rm ~/.kube/config`).
- `aws eks update-kubeconfig` 명령어를 사용하여, 지정된 EKS 클러스터 (`my-eks-cluster`)와 연결하기 위한 kubeconfig 파일을 업데이트함.
- 이 작업으로 로컬의 `kubectl`이 AWS에서 생성된 EKS 클러스터와 상호작용할 수 있게 됨.

## **클러스터 확인 작업**
```bash
cat ~/.kube/config
```
- kubeconfig 파일을 확인하여 연결 설정이 제대로 되었는지 확인.

```bash
kubectl version --client
kubectl cluster-info
kubectl get nodes
```

## **실습 후 제거**
```
terraform destroy -auto-approve
```
