# 2.4.2: 애플리케이션 배포 및 스케일링

## 실습 목표
* Kubernetes 기본 리소스 생성 및 관리
* 애플리케이션 배포 및 서비스 노출
* 수평 및 수직 스케일링 구현
* AWS Load Balancer Controller 설정

## 사전 준비
* 2.4.1 EKS 클러스터 설정 완료
* kubectl 설치 및 클러스터 연결 완료
* Docker 이미지 준비 (ECR 또는 Docker Hub)

## 실습 단계

### Step 1: 클러스터 상태 확인

#### 기본 확인
```bash
# 클러스터 연결 확인
kubectl cluster-info

# 노드 상태 확인
kubectl get nodes -o wide

# 네임스페이스 확인
kubectl get namespaces

# kube-system Pod 확인
kubectl get pods -n kube-system
```

### Step 2: 첫 번째 애플리케이션 배포

#### Nginx 배포 예시
```yaml
# nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 20
```

#### 서비스 생성
```yaml
# nginx-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
```

#### 배포 실행
```bash
# 배포 파일 적용
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml

# 배포 상태 확인
kubectl get deployments
kubectl get pods -l app=nginx
kubectl get services

# Pod 상세 정보 확인
kubectl describe pod <pod-name>

# 로그 확인
kubectl logs -l app=nginx
```

### Step 3: AWS Load Balancer Controller 설치

#### eksctl 설치 (필요한 경우)
```bash
# eksctl 다운로드 및 설치
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl version
```

#### OIDC Provider 생성
```bash
# 클러스터 이름 설정
CLUSTER_NAME=my-eks-cluster
REGION=ap-northeast-2

# OIDC Provider 생성
eksctl utils associate-iam-oidc-provider \
    --region $REGION \
    --cluster $CLUSTER_NAME \
    --approve
```

#### AWS Load Balancer Controller IAM 역할 생성
```bash
# 정책 다운로드
curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.0/docs/install/iam_policy.json

# IAM 정책 생성
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam-policy.json

# 서비스 계정 생성
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --region $REGION \
  --approve
```

#### Helm을 이용한 Controller 설치
```bash
# Helm 저장소 추가
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# AWS Load Balancer Controller 설치
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=$CLUSTER_NAME \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=$REGION \
  --set vpcId=$(aws eks describe-cluster --name $CLUSTER_NAME --query "cluster.resourcesVpcConfig.vpcId" --output text)

# 설치 확인
kubectl get deployment -n kube-system aws-load-balancer-controller
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

### Step 4: Application Load Balancer로 서비스 노출

#### Ingress 리소스 생성
```yaml
# nginx-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'
    alb.ingress.kubernetes.io/healthcheck-path: /
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
```

#### 배포 및 확인
```bash
# Ingress 배포
kubectl apply -f nginx-ingress.yaml

# Ingress 상태 확인
kubectl get ingress nginx-ingress

# ALB 주소 확인
kubectl get ingress nginx-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# 브라우저 또는 curl로 접속 테스트
ALB_URL=$(kubectl get ingress nginx-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl http://$ALB_URL
```

### Step 5: 수평 Pod 자동 스케일링 (HPA)

#### Metrics Server 설치 확인
```bash
# Metrics Server 상태 확인
kubectl get deployment metrics-server -n kube-system

# 없으면 설치
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 메트릭 확인
kubectl top nodes
kubectl top pods
```

#### HPA 생성
```yaml
# nginx-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### HPA 테스트
```bash
# HPA 적용
kubectl apply -f nginx-hpa.yaml

# HPA 상태 확인
kubectl get hpa nginx-hpa
kubectl describe hpa nginx-hpa

# 부하 테스트용 Pod 생성
kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh

# 부하 테스트 (Pod 내에서 실행)
while true; do wget -q -O- http://nginx-service/; done

# HPA 동작 확인 (다른 터미널에서)
kubectl get hpa nginx-hpa --watch
kubectl get pods -l app=nginx --watch
```

### Step 6: 실전 웹 애플리케이션 배포

#### Node.js 애플리케이션 배포
```yaml
# webapp-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
  labels:
    app: webapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        volumeMounts:
        - name: webapp-content
          mountPath: /usr/share/nginx/html
      volumes:
      - name: webapp-content
        configMap:
          name: webapp-content
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-content
data:
  index.html: |
    <!DOCTYPE html>
    <html>
    <head>
        <title>EKS Web App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
            .container { max-width: 800px; margin: 0 auto; }
            .info { background: #f0f0f0; padding: 20px; margin: 20px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to EKS Web Application!</h1>
            <div class="info">
                <h3>Pod Information</h3>
                <p><strong>Hostname:</strong> <span id="hostname"></span></p>
                <p><strong>Timestamp:</strong> <span id="timestamp"></span></p>
            </div>
            <div class="info">
                <h3>Environment</h3>
                <p>Running on Amazon EKS</p>
                <p>Deployed with Kubernetes</p>
            </div>
        </div>
        <script>
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
            fetch('/api/hostname')
                .then(response => response.text())
                .then(data => document.getElementById('hostname').textContent = data)
                .catch(() => document.getElementById('hostname').textContent = 'N/A');
        </script>
    </body>
    </html>
---
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: webapp-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}]'
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: webapp-service
            port:
              number: 80
```

### Step 7: 롤링 업데이트 및 롤백

#### 배포 전략 설정
```yaml
# rolling-update-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-update-demo
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: rolling-demo
  template:
    metadata:
      labels:
        app: rolling-demo
        version: v1
    spec:
      containers:
      - name: app
        image: nginx:1.20-alpine
        ports:
        - containerPort: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 롤링 업데이트 실행
```bash
# 초기 배포
kubectl apply -f rolling-update-deployment.yaml

# 이미지 업데이트 (v2로 업데이트)
kubectl set image deployment/rolling-update-demo app=nginx:1.21-alpine

# 업데이트 진행 상황 확인
kubectl rollout status deployment/rolling-update-demo

# 실시간 Pod 변화 확인
kubectl get pods -l app=rolling-demo --watch

# 배포 기록 확인
kubectl rollout history deployment/rolling-update-demo
```

#### 롤백 실행
```bash
# 이전 버전으로 롤백
kubectl rollout undo deployment/rolling-update-demo

# 특정 리비전으로 롤백
kubectl rollout undo deployment/rolling-update-demo --to-revision=1

# 롤백 상태 확인
kubectl rollout status deployment/rolling-update-demo
```

### Step 8: 모니터링 및 헬스 체크

#### 상세 모니터링
```bash
# 클러스터 전체 리소스 확인
kubectl top nodes
kubectl top pods --all-namespaces

# 특정 네임스페이스 리소스 사용량
kubectl top pods -n default

# 노드 상세 정보
kubectl describe nodes

# 이벤트 모니터링
kubectl get events --sort-by=.metadata.creationTimestamp

# 실시간 이벤트 확인
kubectl get events --watch
```

#### 애플리케이션 로그 및 디버깅
```bash
# 특정 Pod 로그
kubectl logs <pod-name>

# 라벨 기반 로그 확인
kubectl logs -l app=webapp

# 실시간 로그 스트리밍
kubectl logs -f <pod-name>

# 컨테이너 내부 접속
kubectl exec -it <pod-name> -- /bin/sh

# 포트 포워딩으로 로컬 테스트
kubectl port-forward pod/<pod-name> 8080:80
```

### Step 9: 네임스페이스 기반 멀티 환경 구성

#### 개발/스테이징 환경 분리
```yaml
# namespaces.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
  labels:
    environment: dev
---
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    environment: staging
---
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: prod
```

#### 환경별 리소스 할당
```yaml
# resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "10"
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: staging-quota
  namespace: staging
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

### Step 10: 정리 및 리소스 삭제

#### 개별 리소스 삭제
```bash
# 배포된 애플리케이션 삭제
kubectl delete deployment nginx-deployment webapp-deployment
kubectl delete service nginx-service webapp-service
kubectl delete ingress nginx-ingress webapp-ingress
kubectl delete hpa nginx-hpa

# ConfigMap 삭제
kubectl delete configmap webapp-content

# 네임스페이스 삭제 (네임스페이스 내 모든 리소스 삭제)
kubectl delete namespace development staging production
```

#### 전체 정리
```bash
# Load Balancer Controller 삭제
helm uninstall aws-load-balancer-controller -n kube-system

# OIDC Provider 삭제 (선택사항)
# eksctl utils disassociate-iam-oidc-provider --region $REGION --cluster $CLUSTER_NAME

# 클러스터 전체 삭제는 2.4.1에서 terraform destroy로 수행
```

## 문제 해결

### 일반적인 이슈

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| Pod이 Pending 상태 | 리소스 부족 또는 노드 부족 | kubectl describe pod로 상세 확인 |
| ImagePullBackOff | 잘못된 이미지명 또는 권한 | 이미지명 확인, ECR 권한 점검 |
| CrashLoopBackOff | 애플리케이션 오류 | 로그 확인, 헬스 체크 설정 |
| Service 연결 안됨 | 라벨 셀렉터 불일치 | Service와 Pod 라벨 확인 |
| Ingress 동작 안함 | ALB Controller 미설치 | Controller 설치 상태 확인 |

### 유용한 디버깅 명령어
```bash
# Pod 문제 진단
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous

# 서비스 엔드포인트 확인
kubectl get endpoints

# DNS 해상도 테스트
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# 네트워크 연결 테스트
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never

# 리소스 사용량 모니터링
watch kubectl top pods
watch kubectl get pods
```

## 다음 단계
* 2.4.3: Helm을 사용한 패키지 관리
* 고급 배포 패턴 (Blue/Green, Canary)
* 서비스 메시 (Istio) 도입 고려

## 관련 문서
* [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
* [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
* [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
