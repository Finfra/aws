# 2.4.3: Helm을 사용한 패키지 관리

## 실습 목표
* Helm의 기본 개념 이해 및 설치
* 기존 Helm 차트를 이용한 애플리케이션 배포
* 커스텀 Helm 차트 작성 및 관리
* 환경별 값 설정 및 배포 전략

## Helm 기본 개념
* **Helm**: Kubernetes용 패키지 매니저
* **Chart**: Helm 패키지 (Kubernetes 리소스 템플릿 모음)
* **Release**: 클러스터에 설치된 차트의 인스턴스
* **Repository**: 차트들이 저장된 저장소
* **Values**: 차트 설정을 위한 변수들

## 사전 준비
* 2.4.1 EKS 클러스터 설정 완료
* 2.4.2 기본 애플리케이션 배포 경험
* kubectl 설치 및 클러스터 연결 완료

## 실습 단계

### Step 1: Helm 설치

#### Helm CLI 설치 (Linux/macOS)
```bash
# 스크립트를 이용한 설치
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 또는 수동 다운로드
curl -LO https://get.helm.sh/helm-v3.13.0-linux-amd64.tar.gz
tar -zxvf helm-v3.13.0-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm

# 설치 확인
helm version
```

#### Helm 초기 설정
```bash
# Helm 저장소 추가
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# 저장소 업데이트
helm repo update

# 저장소 목록 확인
helm repo list

# 사용 가능한 차트 검색
helm search repo nginx
helm search repo prometheus
```

### Step 2: 기존 Helm 차트로 애플리케이션 배포

#### Redis 배포 예시
```bash
# Redis 차트 정보 확인
helm show chart bitnami/redis
helm show values bitnami/redis

# 사용자 정의 values 파일 생성
cat > redis-values.yaml << 'EOF'
# Redis 인증 설정
auth:
  enabled: true
  password: "redis123"

# 아키텍처 설정 (standalone 모드)
architecture: standalone

# 마스터 설정
master:
  persistence:
    enabled: true
    size: 8Gi
  resources:
    requests:
      memory: 256Mi
      cpu: 100m
    limits:
      memory: 512Mi
      cpu: 200m

# 메트릭 활성화
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
EOF

# Redis 설치
helm install my-redis bitnami/redis -f redis-values.yaml

# 설치 상태 확인
helm status my-redis
helm list
kubectl get pods
kubectl get pvc

# Redis 연결 테스트
export REDIS_PASSWORD=$(kubectl get secret --namespace default my-redis -o jsonpath="{.data.redis-password}" | base64 -d)
kubectl run --namespace default redis-client --rm --tty -i --restart='Never' \
  --image docker.io/bitnami/redis:7.2.1-debian-11-r0 -- bash

# Redis 클라이언트 내에서 실행
redis-cli -h my-redis-master -a $REDIS_PASSWORD
```

### Step 3: 모니터링 스택 배포 (Prometheus + Grafana)

#### Prometheus Operator 설치
```bash
# kube-prometheus-stack 설치
helm install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set alertmanager.alertmanagerSpec.storage.volumeClaimTemplate.spec.resources.requests.storage=10Gi \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.size=10Gi \
  --set grafana.adminPassword=admin123

# 설치 확인
kubectl get pods -n monitoring
kubectl get services -n monitoring

# Grafana 접속을 위한 포트 포워딩
kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80 &

# 또는 LoadBalancer로 노출
kubectl patch svc prometheus-stack-grafana -n monitoring -p '{"spec": {"type": "LoadBalancer"}}'
```

### Step 4: 커스텀 Helm 차트 생성

#### 차트 기본 구조 생성
```bash
# 새 차트 생성
helm create my-webapp

# 생성된 구조 확인
ls -la my-webapp/
```

#### 차트 구조 설명
```
my-webapp/
├── Chart.yaml          # 차트 메타데이터
├── values.yaml         # 기본 설정 값
├── charts/             # 의존성 차트들
├── templates/          # Kubernetes 리소스 템플릿
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── _helpers.tpl    # 템플릿 헬퍼 함수
│   ├── NOTES.txt       # 설치 후 표시될 노트
│   └── tests/          # 테스트 파일들
└── .helmignore        # 무시할 파일 패턴
```

#### Chart.yaml 수정
```yaml
# my-webapp/Chart.yaml
apiVersion: v2
name: my-webapp
description: A Helm chart for my custom web application
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - webapp
  - kubernetes
  - demo
home: https://github.com/yourusername/my-webapp
sources:
  - https://github.com/yourusername/my-webapp
maintainers:
  - name: Your Name
    email: your.email@example.com
```

#### values.yaml 커스터마이징
```yaml
# my-webapp/values.yaml
replicaCount: 2

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "1.21-alpine"

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext: 
  fsGroup: 2000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: "alb"
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
  hosts:
    - host: my-webapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

# 커스텀 설정
config:
  message: "Hello from Helm Chart!"
  environment: "development"

# ConfigMap 활성화
configMap:
  enabled: true
```

#### 템플릿 파일 수정

##### deployment.yaml 업데이트
```yaml
# my-webapp/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-webapp.fullname" . }}
  labels:
    {{- include "my-webapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "my-webapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "my-webapp.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "my-webapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- if .Values.configMap.enabled }}
          env:
            - name: APP_MESSAGE
              valueFrom:
                configMapKeyRef:
                  name: {{ include "my-webapp.fullname" . }}-config
                  key: message
            - name: APP_ENVIRONMENT
              valueFrom:
                configMapKeyRef:
                  name: {{ include "my-webapp.fullname" . }}-config
                  key: environment
          {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

##### ConfigMap 템플릿 추가
```yaml
# my-webapp/templates/configmap.yaml
{{- if .Values.configMap.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-webapp.fullname" . }}-config
  labels:
    {{- include "my-webapp.labels" . | nindent 4 }}
data:
  message: {{ .Values.config.message | quote }}
  environment: {{ .Values.config.environment | quote }}
  {{- range $key, $value := .Values.config }}
  {{- if not (has $key (list "message" "environment")) }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
  {{- end }}
{{- end }}
```

##### HPA 템플릿 추가
```yaml
# my-webapp/templates/hpa.yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "my-webapp.fullname" . }}
  labels:
    {{- include "my-webapp.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "my-webapp.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
```

### Step 5: 환경별 설정 파일 관리

#### 개발 환경 설정
```yaml
# values-dev.yaml
replicaCount: 1

image:
  tag: "dev-latest"

config:
  message: "Hello from Development!"
  environment: "development"
  debug: "true"

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

ingress:
  enabled: true
  hosts:
    - host: my-webapp-dev.example.com
      paths:
        - path: /
          pathType: Prefix
```

#### 스테이징 환경 설정
```yaml
# values-staging.yaml
replicaCount: 2

image:
  tag: "staging-v1.0.0"

config:
  message: "Hello from Staging!"
  environment: "staging"
  debug: "false"

resources:
  limits:
    cpu: 300m
    memory: 384Mi
  requests:
    cpu: 150m
    memory: 192Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  hosts:
    - host: my-webapp-staging.example.com
      paths:
        - path: /
          pathType: Prefix
```

#### 프로덕션 환경 설정
```yaml
# values-prod.yaml
replicaCount: 3

image:
  tag: "v1.0.0"

config:
  message: "Hello from Production!"
  environment: "production"
  debug: "false"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 60

ingress:
  enabled: true
  hosts:
    - host: my-webapp.example.com
      paths:
        - path: /
          pathType: Prefix

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - my-webapp
        topologyKey: kubernetes.io/hostname
```

### Step 6: 차트 테스트 및 배포

#### 차트 유효성 검증
```bash
# 차트 구문 검사
helm lint my-webapp/

# 차트 템플릿 렌더링 테스트
helm template my-webapp my-webapp/ --values my-webapp/values-dev.yaml

# 차트 패키징
helm package my-webapp/

# 드라이런으로 설치 테스트
helm install my-webapp-dev my-webapp/ \
  --values my-webapp/values-dev.yaml \
  --namespace development \
  --create-namespace \
  --dry-run --debug
```

#### 환경별 배포
```bash
# 개발 환경 배포
helm install my-webapp-dev my-webapp/ \
  --values my-webapp/values-dev.yaml \
  --namespace development \
  --create-namespace

# 스테이징 환경 배포
helm install my-webapp-staging my-webapp/ \
  --values my-webapp/values-staging.yaml \
  --namespace staging \
  --create-namespace

# 프로덕션 환경 배포 (신중하게!)
helm install my-webapp-prod my-webapp/ \
  --values my-webapp/values-prod.yaml \
  --namespace production \
  --create-namespace
```

### Step 7: 릴리스 관리

#### 릴리스 상태 확인
```bash
# 모든 릴리스 목록
helm list --all-namespaces

# 특정 네임스페이스의 릴리스
helm list -n development

# 릴리스 상태 상세 확인
helm status my-webapp-dev -n development

# 릴리스 기록 확인
helm history my-webapp-dev -n development
```

#### 릴리스 업그레이드
```bash
# 값 변경 후 업그레이드
helm upgrade my-webapp-dev my-webapp/ \
  --values my-webapp/values-dev.yaml \
  --set replicaCount=2 \
  --namespace development

# 특정 버전으로 업그레이드
helm upgrade my-webapp-dev my-webapp/ \
  --values my-webapp/values-dev.yaml \
  --set image.tag=dev-v1.1.0 \
  --namespace development

# 업그레이드 상태 확인
helm status my-webapp-dev -n development
```

#### 롤백 수행
```bash
# 이전 버전으로 롤백
helm rollback my-webapp-dev 1 -n development

# 특정 리비전으로 롤백
helm rollback my-webapp-dev 2 -n development

# 롤백 상태 확인
helm history my-webapp-dev -n development
```

### Step 8: Chart Repository 구성

#### 로컬 Chart Repository 생성
```bash
# Chart 패키징
helm package my-webapp/

# Repository 인덱스 생성
helm repo index . --url http://my-charts.example.com

# 간단한 HTTP 서버로 제공 (테스트용)
python3 -m http.server 8080 &

# 로컬 저장소 추가
helm repo add my-charts http://localhost:8080

# 저장소에서 차트 검색
helm search repo my-charts
```

#### GitHub Pages를 이용한 Chart Repository
```bash
# GitHub 저장소 생성 및 클론
git clone https://github.com/yourusername/helm-charts.git
cd helm-charts

# 차트 복사 및 패키징
cp -r ../my-webapp .
helm package my-webapp/

# 인덱스 파일 생성
helm repo index . --url https://yourusername.github.io/helm-charts

# GitHub Pages 활성화를 위한 푸시
git add .
git commit -m "Add my-webapp chart"
git push origin main
```

### Step 9: Helm Hooks 활용

#### Pre-install Hook 예시
```yaml
# my-webapp/templates/pre-install-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-webapp.fullname" . }}-pre-install
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: pre-install
        image: busybox
        command: ['sh', '-c']
        args:
          - |
            echo "Pre-install hook running..."
            echo "Preparing environment for {{ include "my-webapp.fullname" . }}"
            sleep 10
            echo "Pre-install hook completed!"
```

#### Post-install Hook 예시
```yaml
# my-webapp/templates/post-install-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-webapp.fullname" . }}-install-info
  annotations:
    "helm.sh/hook": post-install
    "helm.sh/hook-weight": "0"
data:
  install-time: {{ now | date "2006-01-02T15:04:05Z" | quote }}
  chart-version: {{ .Chart.Version | quote }}
  app-version: {{ .Chart.AppVersion | quote }}
```

### Step 10: 고급 템플릿 기법

#### 조건부 리소스 생성
```yaml
# my-webapp/templates/secret.yaml
{{- if .Values.secret.enabled }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "my-webapp.fullname" . }}-secret
  labels:
    {{- include "my-webapp.labels" . | nindent 4 }}
type: Opaque
data:
  {{- range $key, $value := .Values.secret.data }}
  {{ $key }}: {{ $value | b64enc | quote }}
  {{- end }}
{{- end }}
```

#### 반복문 활용
```yaml
# my-webapp/templates/configmap-multi.yaml
{{- range $name, $config := .Values.configs }}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "my-webapp.fullname" $ }}-{{ $name }}
  labels:
    {{- include "my-webapp.labels" $ | nindent 4 }}
data:
  {{- range $key, $value := $config }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
{{- end }}
```

### Step 11: 정리 및 삭제

#### 릴리스 삭제
```bash
# 개별 릴리스 삭제
helm uninstall my-webapp-dev -n development
helm uninstall my-webapp-staging -n staging
helm uninstall prometheus-stack -n monitoring
helm uninstall my-redis

# 네임스페이스 삭제 (네임스페이스 내 모든 리소스 삭제)
kubectl delete namespace development staging monitoring

# Helm 저장소 제거
helm repo remove bitnami
helm repo remove prometheus-community
```

## 모범 사례

### Chart 작성 모범 사례
* 의미있는 기본값 설정
* 모든 리소스에 라벨과 셀렉터 일관성 유지
* 리소스 제한 및 요청 명시
* 헬스 체크 및 프로브 구성
* 보안 컨텍스트 적용

### 버전 관리 전략
* 시맨틱 버전닝 사용 (Chart.yaml의 version)
* 애플리케이션 버전과 차트 버전 분리
* 변경 로그 유지
* 태그 기반 이미지 사용 (latest 태그 지양)

### 보안 고려사항
* 시크릿 관리 (Helm Secrets, Sealed Secrets)
* RBAC 설정
* 네트워크 정책 적용
* 이미지 보안 스캔

## 문제 해결

### 일반적인 이슈

| 문제 | 원인 | 해결방법 |
|------|------|----------|
| 템플릿 렌더링 오류 | 문법 오류 또는 값 누락 | helm template으로 디버깅 |
| 릴리스 설치 실패 | 리소스 충돌 또는 권한 부족 | kubectl 로그 확인 |
| 차트 업그레이드 실패 | 호환되지 않는 변경사항 | 롤백 후 점진적 변경 |
| Hook 실행 실패 | Hook 스크립트 오류 | Hook 로그 확인 |

### 유용한 디버깅 명령어
```bash
# 템플릿 렌더링 확인
helm template my-app ./my-webapp --debug

# 드라이런으로 설치 테스트
helm install my-app ./my-webapp --dry-run --debug

# 릴리스 상태 확인
helm status my-app

# 차트 유효성 검사
helm lint ./my-webapp

# 값 확인
helm get values my-app
```

## 다음 단계
* Helm Operator 활용
* GitOps와 Helm 연동 (ArgoCD, Flux)
* 차트 보안 강화 (OPA Gatekeeper)
* 멀티 클러스터 배포 전략

## 관련 문서
* [Helm 공식 문서](https://helm.sh/docs/)
* [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
* [Artifact Hub](https://artifacthub.io/) - 공개 Helm 차트 저장소
