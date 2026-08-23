<p>앞서 Container와 Docker를 살펴보면서 하나의 Application 실행 환경이 어떻게 Image로 만들어지고, Container로 실행되는지 알아봤다.</p>
<pre><code class="language-text">Dockerfile
    ↓
Image
    ↓
Container</code></pre>
<p>Container 몇 개 정도라면 Docker를 통해 직접 관리하는 것도 어렵지 않다.</p>
<pre><code class="language-bash">docker run ...
docker stop ...
docker start ...</code></pre>
<p>하지만 실제 서비스에서는 Container 하나만 실행되는 경우가 드물다.</p>
<pre><code class="language-text">Frontend × N
Backend × N
AI Server × N
Cache
Database
Monitoring
...</code></pre>
<p>Container가 여러 Server에 걸쳐 실행되기 시작하면 새로운 문제가 생긴다.</p>
<pre><code class="language-text">어디에서 실행할까?

몇 개를 실행할까?

하나가 죽으면?

Traffic이 증가하면?

새 Version은 어떻게 배포할까?

각 Container는 어떻게 통신할까?</code></pre>
<p>즉 관심사가 바뀐다.</p>
<pre><code class="language-text">Container 하나를 실행
        ↓
Docker / Container Runtime


많은 Container를 운영
        ↓
Container Platform / Orchestration</code></pre>
<p>이번에는 Container 기반 Application을 운영하기 위한 <strong>Container Platform</strong>과, 그 중심에서 Container Orchestration을 담당하는 <strong>Kubernetes</strong>를 알아보자.</p>
<hr />
<h2 id="container-platform">Container Platform</h2>
<p>Container Runtime이 있다고 해서 실제 서비스 운영 환경이 완성되는 것은 아니다.</p>
<p>Container 기반 Application을 운영하려면 여러 기능이 함께 필요하다.</p>
<h3 id="필요한-기능">필요한 기능</h3>
<ul>
<li>Container 실행</li>
<li>Image 저장 / 배포</li>
<li>Container 배치</li>
<li>Network 연결</li>
<li>Load Balancing</li>
<li>Storage 연결</li>
<li>Configuration 관리</li>
<li>장애 복구</li>
<li>Scaling</li>
<li>Monitoring / Logging</li>
<li>Application 배포 관리</li>
</ul>
<p>이러한 기능들을 결합하여 <strong>Container 기반 Application을 개발하고 배포하고 운영할 수 있도록 구성한 환경</strong>을 넓은 의미에서 Container Platform이라고 볼 수 있다.</p>
<pre><code class="language-text">Container Platform

├─ Container Runtime
├─ Image Registry
├─ Network
├─ Storage
├─ Configuration
├─ Monitoring / Logging
└─ Container Orchestration</code></pre>
<hr />
<pre><code class="language-text">Container Runtime
→ Container 자체를 실행

Container Platform
→ Container 기반 서비스를 운영할 환경 제공</code></pre>
<p>그중에서도 여러 Container의 배치와 상태를 조정하는 핵심 영역이 <strong>Container Orchestration</strong>이다.</p>
<hr />
<h3 id="container-orchestration">Container Orchestration</h3>
<p><code>Orchestration</code>은 여러 요소를 하나의 목적에 맞게 <strong>조율하고 관리하는 것</strong>을 의미한다.</p>
<p>Container 환경에서는 다음과 같은 문제를 다룬다.</p>
<pre><code class="language-text">Container를 어느 Node에 배치할까?

몇 개를 유지할까?

죽은 Container는 어떻게 복구할까?

Traffic 증가 시 어떻게 확장할까?

새 Version은 어떻게 교체할까?</code></pre>
<h4 id="역할">역할</h4>
<ul>
<li>Workload 배치</li>
<li>실행 개수 유지</li>
<li>Scaling</li>
<li>장애 복구</li>
<li>Rollout / Rollback</li>
<li>Network 연결</li>
<li>Storage 연결</li>
<li>Lifecycle 관리</li>
</ul>
<p>정리하면,</p>
<pre><code class="language-text">Container Runtime
→ &quot;Container를 실행한다.&quot;


Container Orchestration
→ &quot;많은 Container를 어떤 상태로 운영할지 관리한다.&quot;</code></pre>
<p>이러한 Container Orchestration을 대표하는 플랫폼이 <strong>Kubernetes</strong>다.</p>
<hr />
<h2 id="kubernetes">Kubernetes</h2>
<h3 id="정의">정의</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e261288f-b670-4725-9c2a-a71836f5dd54/image.png" /></p>
<p><strong>Kubernetes(K8s)</strong> 는 Container 기반 Application의 배포와 운영을 자동화하기 위한 <strong>Open Source Container Orchestration Platform</strong>이다.</p>
<h3 id="주요-기능">주요 기능</h3>
<ul>
<li>Service Discovery / Load Balancing</li>
<li>Scheduling</li>
<li>Scaling</li>
<li>Storage Orchestration</li>
<li>Automated Rollout / Rollback</li>
<li>Self-Healing</li>
<li>Secret / Configuration 관리</li>
</ul>
<p>Docker와 비교하면 다루는 문제의 범위가 다르다.</p>
<pre><code class="language-text">Docker / Container Runtime

Container를 어떻게 실행할까?


Kubernetes

어떤 Application을
어느 Node에
몇 개 실행하고
어떤 상태로 유지할까?</code></pre>
<p>여기서 Kubernetes를 단순히</p>
<blockquote>
<p>Container를 많이 실행해주는 Tool</p>
</blockquote>
<p>정도로 이해하면 조금 부족하다.</p>
<p>Kubernetes의 핵심은 <strong>원하는 상태를 선언하고 그 상태를 계속 유지한다는 것</strong>에 있다.</p>
<hr />
<h2 id="kubernetes의-관리-방식">Kubernetes의 관리 방식</h2>
<h3 id="desired-state">Desired State</h3>
<p>예를 들어 Backend Application을 항상 3개 실행해야 한다고 해보자.</p>
<pre><code class="language-text">Backend Application
        ↓
항상 3개 실행</code></pre>
<p>Kubernetes 입장에서는 이것이 <strong>Desired State</strong>, 즉 원하는 상태다.</p>
<pre><code class="language-text">Desired State

Backend Pod = 3</code></pre>
<p>현재 상태도 3개라면 별다른 작업이 필요 없다.</p>
<pre><code class="language-text">Desired State : 3
Current State : 3

        ↓

      일치</code></pre>
<p>그런데 하나가 장애로 사라졌다.</p>
<pre><code class="language-text">Desired State : 3
Current State : 2</code></pre>
<p>두 상태 사이에 차이가 생긴다.</p>
<pre><code class="language-text">Desired State
      3
      │
      │ ≠
      ▼
Current State
      2</code></pre>
<p>Kubernetes는 필요한 작업을 수행하여 다시 3개로 맞춘다.</p>
<pre><code class="language-text">Pod 1개 추가 생성
        ↓

Current State : 3</code></pre>
<hr />
<h3 id="reconciliation">Reconciliation</h3>
<p>Kubernetes는 원하는 상태를 한 번 만들어놓고 끝나는 것이 아니다.</p>
<p>지속적으로 현재 상태를 관찰한다.</p>
<pre><code class="language-text">Desired State
      │
      ▼
Current State 관찰
      │
      ▼
차이 확인
      │
      ▼
필요한 작업 수행
      │
      ▼
Desired State로 수렴</code></pre>
<p>이처럼 <strong>현재 상태와 원하는 상태의 차이를 계속 줄여가는 과정</strong>을 <code>Reconciliation</code>이라고 한다.</p>
<h4 id="핵심">핵심</h4>
<ul>
<li>Desired State 선언</li>
<li>Current State 관찰</li>
<li>상태 비교</li>
<li>차이 발생 시 조정</li>
<li>Desired State 유지</li>
</ul>
<p>이러한 구조를 기반으로 Kubernetes의</p>
<ul>
<li>Self-Healing</li>
<li>Replica 유지</li>
<li>Scaling</li>
<li>Rolling Update</li>
</ul>
<p>등이 가능해진다.</p>
<pre><code class="language-text">사용자가 작업 절차를 하나씩 명령
              X

사용자가 최종적으로 원하는 상태를 선언
              O</code></pre>
<hr />
<h2 id="kubernetes-cluster">Kubernetes Cluster</h2>
<p>Kubernetes가 Workload를 관리하는 전체 운영 단위를 <strong>Cluster</strong>라고 한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6e2288d3-9ad5-4def-8d64-4a046cf386c7/image.png" /></p>
<p>Cluster는 크게 두 영역으로 나누어 볼 수 있다.</p>
<p>기존 자료에서는 <code>Master Node</code>라는 표현도 많이 사용했지만, 현재는 일반적으로 <strong>Control Plane</strong>이라는 표현을 사용한다.</p>
<hr />
<h3 id="control-plane">Control Plane</h3>
<p>Cluster 전체를 판단하고 관리하는 영역.</p>
<h4 id="역할-1">역할</h4>
<ul>
<li>Cluster 상태 관리</li>
<li>Kubernetes API 제공</li>
<li>Workload 배치 결정</li>
<li>Desired State 유지</li>
<li>Worker Node 관리</li>
</ul>
<pre><code class="language-text">Control Plane

무엇을 실행할까?

몇 개가 필요할까?

어디에서 실행할까?

현재 상태는 정상인가?</code></pre>
<hr />
<h3 id="worker-node">Worker Node</h3>
<p>실제 Application Workload가 실행되는 영역.</p>
<h4 id="역할-2">역할</h4>
<ul>
<li>Pod 실행</li>
<li>Container 실행</li>
<li>Pod 상태 관리</li>
<li>Network 처리</li>
</ul>
<pre><code class="language-text">Worker Node

├─ Pod
│   └─ Container
│
├─ Pod
│   └─ Container
│
└─ Pod
    └─ Container</code></pre>
<p>Node는 반드시 물리 Server일 필요는 없다.</p>
<ul>
<li>Physical Server</li>
<li>Virtual Machine</li>
<li>Cloud VM</li>
</ul>
<p>등이 Node가 될 수 있다.</p>
<h3 id="정리">정리</h3>
<pre><code class="language-text">Control Plane
→ 판단 / 관리

Worker Node
→ 실제 Workload 실행</code></pre>
<hr />
<h2 id="cluster-내부-구성요소">Cluster 내부 구성요소</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8700ffde-b809-420b-88d4-24d17fec1653/image.png" /></p>
<p>Kubernetes Component를 이름부터 외우면 상당히 복잡하다.</p>
<p>각 Component가 <strong>왜 필요한가</strong>를 기준으로 보면 훨씬 단순해진다.</p>
<hr />
<h3 id="control-plane-구성요소">Control Plane 구성요소</h3>
<h4 id="kube-apiserver">kube-apiserver</h4>
<p><strong>Kubernetes Cluster의 API 진입점</strong></p>
<pre><code class="language-text">사용자
   │
   │ kubectl
   ▼
kube-apiserver</code></pre>
<h5 id="역할-3">역할</h5>
<ul>
<li>Kubernetes API 제공</li>
<li>Resource 요청 처리</li>
<li>Cluster 관리 요청의 진입점</li>
<li>Kubernetes Component 간 통신 중심</li>
</ul>
<pre><code class="language-text">Cluster와 대화하려면?
        ↓
kube-apiserver</code></pre>
<hr />
<h4 id="etcd">etcd</h4>
<p><strong>Cluster 상태 저장소</strong></p>
<h5 id="역할-4">역할</h5>
<ul>
<li>Kubernetes Resource 정보 저장</li>
<li>Cluster Configuration 저장</li>
<li>Desired State 저장</li>
<li>각종 Metadata 저장</li>
</ul>
<pre><code class="language-text">Cluster State
      │
      ▼
     etcd</code></pre>
<h5 id="특징">특징</h5>
<ul>
<li>Distributed Key-Value Store</li>
<li>Kubernetes Cluster 상태의 핵심 저장소</li>
</ul>
<pre><code class="language-text">현재 Cluster가
어떤 상태인지 어디에 기억할까?
        ↓
       etcd</code></pre>
<hr />
<h4 id="kube-scheduler">kube-scheduler</h4>
<p><strong>새로운 Pod의 실행 위치 결정</strong></p>
<pre><code class="language-text">Pod 실행 필요
      │
      ▼
  Scheduler
      │
      ▼
Worker Node 선택</code></pre>
<h5 id="고려-대상">고려 대상</h5>
<ul>
<li>CPU</li>
<li>Memory</li>
<li>Node 상태</li>
<li>Resource 요구사항</li>
<li>Scheduling 조건</li>
</ul>
<pre><code class="language-text">이 Pod를
어느 Node에 실행할까?
        ↓
kube-scheduler</code></pre>
<hr />
<h4 id="kube-controller-manager">kube-controller-manager</h4>
<p><strong>Desired State 유지</strong></p>
<pre><code class="language-text">Desired State
      │
      ▼
Controller
      │
      ▼
Current State
      │
      ▼
필요한 조정</code></pre>
<p>예를 들어,</p>
<pre><code class="language-text">Desired Pod : 3
Current Pod : 2</code></pre>
<p>상태라면 필요한 Controller가 이를 확인하고 원하는 상태로 맞추도록 동작한다.</p>
<h5 id="핵심-1">핵심</h5>
<pre><code class="language-text">원하는 상태와
현재 상태가 다른데?
        ↓
Controller
        ↓
Reconciliation</code></pre>
<hr />
<h4 id="cloud-controller-manager">cloud-controller-manager</h4>
<p><strong>Kubernetes와 Cloud Provider 연동</strong></p>
<h5 id="연동-대상">연동 대상</h5>
<ul>
<li>Load Balancer</li>
<li>Cloud Node</li>
<li>Route</li>
<li>Cloud Storage</li>
</ul>
<pre><code class="language-text">Kubernetes
     │
     ▼
Cloud Controller Manager
     │
     ▼
Cloud Infrastructure</code></pre>
<p>Cloud 환경에서 필요한 Infrastructure 연동 기능을 담당한다.</p>
<hr />
<h3 id="worker-node-구성요소">Worker Node 구성요소</h3>
<h4 id="kubelet">kubelet</h4>
<p><strong>Worker Node에서 Pod 상태를 관리</strong></p>
<pre><code class="language-text">Control Plane
      │
      ▼
    kubelet
      │
      ▼
Container Runtime
      │
      ▼
Container</code></pre>
<h5 id="역할-5">역할</h5>
<ul>
<li>Pod 실행 상태 관리</li>
<li>Container Runtime과 연결</li>
<li>Node 상태 확인</li>
<li>Pod 상태 확인</li>
<li>API Server에 상태 보고</li>
</ul>
<p>앞서 Container를 공부하면서 배운 구조와 연결하면 다음과 같다.</p>
<pre><code class="language-text">Kubernetes
→ &quot;이 Pod가 필요하다.&quot;

kubelet
→ Node에서 Pod 상태 관리

Container Runtime
→ 실제 Container 실행

Linux Kernel
→ Process 실행</code></pre>
<hr />
<h4 id="container-runtime">Container Runtime</h4>
<p><strong>실제 Container 실행</strong></p>
<h5 id="대표적인-runtime">대표적인 Runtime</h5>
<ul>
<li>containerd</li>
<li>CRI-O</li>
</ul>
<pre><code class="language-text">kubelet
   │
   ▼
Container Runtime
   │
   ▼
Container Process</code></pre>
<p>즉 Kubernetes가 Container 실행 기술 자체를 새로 만드는 것은 아니다.</p>
<pre><code class="language-text">Kubernetes
→ Workload 배치 / 관리

Container Runtime
→ 실제 Container 실행</code></pre>
<hr />
<h4 id="kube-proxy">kube-proxy</h4>
<p><strong>Kubernetes Service Network 지원</strong></p>
<h5 id="역할-6">역할</h5>
<ul>
<li>Node Network Rule 구성</li>
<li>Service Traffic 전달 지원</li>
</ul>
<p>Service가 정확히 어떻게 Pod와 연결되는지는 이후 Kubernetes Network Resource에서 자세하게 다룬다.</p>
<hr />
<h2 id="cluster-전체-동작-흐름">Cluster 전체 동작 흐름</h2>
<p>각 Component를 하나의 흐름으로 연결하면 다음과 같다.</p>
<pre><code class="language-text">사용자
   │
   │ 원하는 상태 전달
   ▼
kube-apiserver
   │
   ├──────────▶ etcd
   │             상태 저장
   │
   ├──────────▶ Scheduler
   │             Pod 배치 결정
   │
   └──────────▶ Controller
                 상태 비교 / 조정
                       │
                       ▼
                  Worker Node
                       │
                     kubelet
                       │
                       ▼
               Container Runtime
                       │
                       ▼
                      Pod
                       │
                       ▼
                   Container</code></pre>
<p>각 Component가 따로 움직이는 것처럼 보이지만 전체적으로는 하나의 흐름이다.</p>
<pre><code class="language-text">원하는 상태 전달
      ↓
상태 저장
      ↓
실행 위치 결정
      ↓
실제 Workload 실행
      ↓
현재 상태 관찰
      ↓
차이 발생 시 조정</code></pre>
<hr />
<h2 id="kubernetes의-관리-단위">Kubernetes의 관리 단위</h2>
<p>Cluster의 구조를 알아봤다면 이제 Kubernetes가 <strong>무엇을 관리하는지</strong> 살펴보자.</p>
<hr />
<h3 id="pod">Pod</h3>
<p>Docker에서는 Container 자체를 실행 단위로 다뤘다.</p>
<p>Kubernetes에서는 그 위에 <strong>Pod</strong>라는 개념이 추가된다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f5d81506-4136-4f85-a396-ddee632bf08b/image.png" /></p>
<pre><code class="language-text">Docker

Container


Kubernetes

Pod
 ↓
Container</code></pre>
<p>Pod는 Kubernetes의 <strong>최소 배포 단위</strong>다.</p>
<h4 id="특징-1">특징</h4>
<ul>
<li>하나 이상의 Container 포함 가능</li>
<li>같은 Pod의 Container는 함께 배치</li>
<li>동일한 Network Namespace 공유</li>
<li>Volume 공유 가능</li>
<li>Pod 단위로 배치 / 관리</li>
</ul>
<pre><code class="language-text">Pod

├─ Container A
└─ Container B</code></pre>
<p>실제로는 하나의 Application Container만 가진 Pod도 흔하게 사용된다.</p>
<h4 id="핵심-2">핵심</h4>
<pre><code class="language-text">Docker
→ Container를 실행

Kubernetes
→ Container를 Pod 단위로 관리</code></pre>
<p>Pod의 구체적인 생성과 ReplicaSet, Deployment와의 관계는 이후 Resource 관리 글에서 자세하게 다룬다.</p>
<hr />
<h3 id="namespace">Namespace</h3>
<p>하나의 Cluster에는 많은 Resource가 존재할 수 있다.</p>
<p>이를 논리적인 영역으로 나누는 단위가 <strong>Namespace</strong>다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d15cb51b-3b4c-4f0d-a35b-597b04b7719b/image.png" /></p>
<pre><code class="language-text">Kubernetes Cluster

├─ Namespace : dev
│
├─ Namespace : staging
│
└─ Namespace : prod</code></pre>
<h4 id="역할-7">역할</h4>
<ul>
<li>Resource 논리적 분리</li>
<li>Team 구분</li>
<li>Environment 구분</li>
<li>권한 관리 기준</li>
<li>ResourceQuota 적용</li>
<li>NetworkPolicy 적용</li>
</ul>
<h4 id="핵심-3">핵심</h4>
<pre><code class="language-text">Cluster
→ 전체 Kubernetes 운영 범위

Namespace
→ Cluster 내부의 논리적 관리 범위</code></pre>
<p>대부분의 Application Resource는 Namespace에 속한다.</p>
<p>반면 Node와 같이 Cluster 전체 범위에서 관리되는 Resource도 존재한다.</p>
<p>Namespace의 실제 생성과 관리 방법은 이후 <code>Node / Namespace</code> 글에서 다룬다.</p>
<hr />
<h2 id="kubernetes-resource">Kubernetes Resource</h2>
<p>Kubernetes에서는 Application 운영에 필요한 요소를 <strong>Resource</strong>라는 형태로 표현한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0d3901e8-975f-4c03-92ce-f32904872564/image.png" /></p>
<p>중요한 것은 Resource 이름을 모두 외우는 것이 아니다.</p>
<p>각 Resource는 <strong>Application 운영에서 서로 다른 문제를 담당한다.</strong></p>
<hr />
<h3 id="workload-resource">Workload Resource</h3>
<p><strong>Application을 어떻게 실행하고 유지할 것인가</strong></p>
<pre><code class="language-text">Pod
ReplicaSet
Deployment
StatefulSet
DaemonSet
Job
CronJob</code></pre>
<h4 id="역할-8">역할</h4>
<ul>
<li><p><code>Pod</code></p>
<ul>
<li>Container 실행 단위</li>
</ul>
</li>
<li><p><code>ReplicaSet</code></p>
<ul>
<li>Pod 개수 유지</li>
</ul>
</li>
<li><p><code>Deployment</code></p>
<ul>
<li>Application 배포 / 업데이트 관리</li>
</ul>
</li>
<li><p><code>StatefulSet</code></p>
<ul>
<li>상태와 정체성이 필요한 Workload</li>
</ul>
</li>
<li><p><code>DaemonSet</code></p>
<ul>
<li>Node 단위 Workload</li>
</ul>
</li>
<li><p><code>Job / CronJob</code></p>
<ul>
<li>일회성 / 주기적 작업</li>
</ul>
</li>
</ul>
<hr />
<h3 id="network-resource">Network Resource</h3>
<p><strong>Application에 어떻게 접근할 것인가</strong></p>
<pre><code class="language-text">Service
Ingress</code></pre>
<h4 id="역할-9">역할</h4>
<ul>
<li><p><code>Service</code></p>
<ul>
<li>Pod 집합의 안정적인 접근점</li>
</ul>
</li>
<li><p><code>Ingress</code></p>
<ul>
<li>외부 HTTP / HTTPS Routing</li>
</ul>
</li>
</ul>
<hr />
<h3 id="storage-resource">Storage Resource</h3>
<p><strong>Application의 Data를 어떻게 유지할 것인가</strong></p>
<pre><code class="language-text">Volume
PersistentVolume
PersistentVolumeClaim
StorageClass</code></pre>
<p>Docker에서도 다음과 같은 문제를 살펴봤다.</p>
<pre><code class="language-text">Container Lifecycle
        ≠
Data Lifecycle</code></pre>
<p>Kubernetes에서도 Pod와 Data의 생명주기를 분리하기 위한 Storage Resource가 존재한다.</p>
<hr />
<h3 id="configuration-resource">Configuration Resource</h3>
<p><strong>Application 설정을 어떻게 분리할 것인가</strong></p>
<pre><code class="language-text">ConfigMap
Secret</code></pre>
<h4 id="역할-10">역할</h4>
<ul>
<li><p><code>ConfigMap</code></p>
<ul>
<li>일반 Configuration</li>
</ul>
</li>
<li><p><code>Secret</code></p>
<ul>
<li>민감한 Configuration</li>
</ul>
</li>
</ul>
<hr />
<h3 id="resource-전체-구조">Resource 전체 구조</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c1df13fe-78b2-4a03-a2c3-47b4b2925a79/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4cc92ce2-4e4c-4a07-8462-15abf3bfac75/image.png" /></p>
<p>각 Resource의 관계를 크게 보면 다음과 같다.</p>
<pre><code class="language-text">Application 실행
        ↓
       Pod
        ↓
    Container


배포 / 개수 관리
        ↓
   Deployment
        ↓
   ReplicaSet
        ↓
       Pod


Network 접근
        ↓
     Ingress
        ↓
     Service
        ↓
       Pod


Data 관리
        ↓
 Storage Resource


Configuration
        ↓
ConfigMap / Secret
        ↓
       Pod</code></pre>
<h3 id="핵심-4">핵심</h3>
<blockquote>
<p><strong>Kubernetes는 하나의 거대한 Resource로 Application을 관리하는 것이 아니라, 각각의 문제를 담당하는 Resource들을 조합하여 Application의 상태를 표현한다.</strong></p>
</blockquote>
<p>각 Resource의 세부적인 동작과 사용 방법은 이후 Resource별 글에서 하나씩 살펴본다.</p>
<hr />
<h2 id="kubernetes의-선언적-관리">Kubernetes의 선언적 관리</h2>
<p>앞에서 Kubernetes는 <strong>Desired State</strong>를 유지한다고 했다.</p>
<p>그렇다면 사용자는 원하는 상태를 Kubernetes에 어떻게 전달할까?</p>
<p>Kubernetes에서는 주로 <strong>선언적 관리(Declarative Management)</strong> 방식을 사용한다.</p>
<hr />
<h3 id="명령형-관리">명령형 관리</h3>
<p>수행할 작업을 하나씩 지정한다.</p>
<pre><code class="language-text">Pod 하나 만들어

하나 더 만들어

하나 삭제해

죽으면 다시 만들어</code></pre>
<hr />
<h3 id="선언형-관리">선언형 관리</h3>
<p>최종적으로 원하는 상태를 지정한다.</p>
<pre><code class="language-text">Backend Pod가
항상 3개 존재해야 한다.</code></pre>
<p>그 이후 상태 조정은 Kubernetes가 담당한다.</p>
<pre><code class="language-text">Desired State 선언
        ↓
Current State 관찰
        ↓
차이 비교
        ↓
Reconciliation
        ↓
Desired State 유지</code></pre>
<h3 id="핵심-5">핵심</h3>
<pre><code class="language-text">명령형
→ &quot;어떻게 할 것인가?&quot;


선언형
→ &quot;어떤 상태여야 하는가?&quot;</code></pre>
<hr />
<h2 id="kubernetes-manifest">Kubernetes Manifest</h2>
<p>원하는 Resource의 상태는 일반적으로 YAML 또는 JSON 형태의 <strong>Manifest</strong>로 정의한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d4402a5b-2317-4e74-89cf-51ad7e8a28ca/image.png" /></p>
<p>대표적인 YAML 구조는 다음과 같다.</p>
<pre><code class="language-yaml">apiVersion:
kind:
metadata:
spec:</code></pre>
<h3 id="apiversion">apiVersion</h3>
<p><strong>사용할 Kubernetes API</strong></p>
<hr />
<h3 id="kind">kind</h3>
<p><strong>Resource 종류</strong></p>
<pre><code class="language-text">Pod
Deployment
Service
ConfigMap
...</code></pre>
<hr />
<h3 id="metadata">metadata</h3>
<p><strong>Resource 식별 정보</strong></p>
<ul>
<li>name</li>
<li>namespace</li>
<li>labels</li>
<li>annotations</li>
</ul>
<hr />
<h3 id="spec">spec</h3>
<p><strong>Resource의 Desired State</strong></p>
<p>개념적으로 보면 다음과 같다.</p>
<pre><code class="language-text">apiVersion
→ 어떤 API를 사용할까?

kind
→ 무엇을 만들까?

metadata
→ 누구인가?

spec
→ 어떤 상태여야 하는가?</code></pre>
<p>Manifest는 작업 순서를 기록한 Script라기보다</p>
<blockquote>
<p><strong>Kubernetes Resource가 가져야 할 원하는 상태를 표현한 선언문</strong></p>
</blockquote>
<p>에 가깝다.</p>
<p>Deployment나 Service의 실제 YAML 구조는 이후 각 Resource를 직접 사용하면서 살펴본다.</p>
<hr />
<h2 id="kubectl">kubectl</h2>
<p>Kubernetes Cluster와 통신할 때 사용하는 대표적인 CLI가 <strong>kubectl</strong>이다.</p>
<pre><code class="language-text">사용자
   │
   │ kubectl
   ▼
kube-apiserver
   │
   ▼
Kubernetes Cluster</code></pre>
<p><code>kubectl</code>이 직접 Worker Node에 접속하여 Container를 실행하는 것은 아니다.</p>
<h3 id="역할-11">역할</h3>
<ul>
<li>Kubernetes API 호출</li>
<li>Resource 생성 / 조회 / 수정 / 삭제 요청</li>
<li>Cluster 상태 확인</li>
</ul>
<h3 id="기본-형태">기본 형태</h3>
<pre><code class="language-bash">kubectl [command] [TYPE] [NAME] [flags]</code></pre>
<blockquote>
<p><strong>kubectl 사용 자료</strong></p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ab8c36a8-f677-4315-8139-01777e9dbbaa/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ceac8aae-547f-4fd1-bd22-9653064bb774/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/401af68b-0f3a-462a-94f1-99de4247a668/image.png" /></p>
<h3 id="핵심-6">핵심</h3>
<pre><code class="language-text">Manifest
   │
   │ Desired State 정의
   ▼
kubectl
   │
   │ API 요청
   ▼
kube-apiserver
   │
   ▼
Kubernetes</code></pre>
<p>즉,</p>
<pre><code class="language-text">kubectl
= Kubernetes API Client</code></pre>
<p>라고 이해하면 된다.</p>
<p>실제 <code>kubectl</code> 명령과 각 Resource 관리 방법은 이후 실습에서 다룬다.</p>
<hr />
<h2 id="전체-흐름">전체 흐름</h2>
<p>이번 글의 흐름을 처음부터 연결하면 다음과 같다.</p>
<pre><code class="language-text">Container
    │
    │ 수가 증가
    ▼

Container Orchestration
    │
    ▼

Kubernetes
    │
    ├─ Desired State
    │
    ├─ Reconciliation
    │
    └─ Cluster
         │
         ├─ Control Plane
         │    ├─ API Server
         │    ├─ etcd
         │    ├─ Scheduler
         │    └─ Controller
         │
         └─ Worker Node
              ├─ kubelet
              ├─ Container Runtime
              └─ Pod
                   │
                   ▼
               Container</code></pre>
<p>Application 관리 관점에서는 다음과 같다.</p>
<pre><code class="language-text">Kubernetes Resource

├─ Workload
│
├─ Network
│
├─ Storage
│
└─ Configuration</code></pre>
<p>그리고 사용자는 이를 직접 하나씩 조작하기보다,</p>
<pre><code class="language-text">Manifest
   │
   │ Desired State 선언
   ▼
kubectl
   │
   ▼
API Server
   │
   ▼
Kubernetes
   │
   ▼
Desired State 유지</code></pre>
<p>의 방식으로 관리한다.</p>
<hr />
<h2 id="마치며">마치며</h2>
<p>Docker에서는 하나의 Container가 만들어지고 실행되는 구조를 살펴봤다면,
이번에는 그 실행 단위가 많아졌을 때 Kubernetes가 어떻게 이를 관리하는지 알아봤다.</p>
<p>사용자가 원하는 상태를 선언하면 Kubernetes는 Cluster의 현재 상태를 관찰하고,
Control Plane과 Worker Node의 여러 Component를 통해 실제 상태를 계속 원하는 상태에 맞춘다.</p>
<p>다음에는 이러한 Kubernetes를 중심으로 실제 Container Platform이 어떤 구성요소들로 만들어지는지 살펴보자.</p>