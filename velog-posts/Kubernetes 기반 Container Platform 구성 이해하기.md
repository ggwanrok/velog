<p>앞에서는 Kubernetes가 여러 Container 기반 Workload를 Cluster 단위에서 어떻게 관리하는지 살펴봤다.</p>
<pre><code class="language-text">Desired State
      ↓
Kubernetes
      ↓
Cluster
├─ Control Plane
└─ Worker Node
      ↓
     Pod
      ↓
 Container</code></pre>
<p>그런데 Kubernetes Cluster 하나를 구성했다고 해서 실제 서비스를 운영하기 위한 환경이 모두 완성되는 것은 아니다.</p>
<p>실제 운영 환경에서는 Kubernetes 외에도 여러 기능이 필요하다.</p>
<pre><code class="language-text">Container Image는 어디에 저장할까?

Kubernetes Cluster는 어떻게 설치할까?

Pod끼리는 어떻게 통신할까?

외부 Traffic은 어떻게 받을까?

Data는 어디에 저장할까?

Secret과 사용자 인증은 어떻게 관리할까?

Application 배포를 어떻게 자동화할까?</code></pre>
<p>결국 Kubernetes를 중심으로 여러 Software와 Infrastructure를 결합해야 실제 Container 기반 서비스를 운영할 수 있다.</p>
<p>이번에는 이러한 <strong>Container Platform의 구성</strong>을 실제 실습에서 사용하게 될 <strong>K-PaaS Container Platform</strong>을 중심으로 살펴보자.</p>
<hr />
<h2 id="container-platform">Container Platform</h2>
<h3 id="정의">정의</h3>
<p><strong>Container Platform</strong>은 Kubernetes와 같은 Container Orchestrator를 중심으로 Container Runtime, Network, Storage, Registry, Security, Deployment 등의 기술을 결합하여 <strong>Container 기반 Application을 개발·배포·운영할 수 있도록 구성한 통합 환경</strong>이다.</p>
<p>Container 자체는 Application과 실행에 필요한 종속성을 Image로 패키징하여 환경 간 이식성을 높여준다.</p>
<p>하지만 실제 서비스에서는 Container만으로 모든 것이 해결되지 않는다.</p>
<pre><code class="language-text">Application
     │
     ▼
Container
     │
     ├─ Network 필요
     ├─ Storage 필요
     ├─ Registry 필요
     ├─ Security 필요
     ├─ Monitoring 필요
     └─ Orchestration 필요</code></pre>
<p>따라서 Container Platform은 이러한 기능들을 하나의 운영 환경으로 결합한다.</p>
<pre><code class="language-text">Container Platform

├─ Infrastructure / Provisioning
├─ Container Runtime
├─ Container Orchestration
├─ Network / Traffic
├─ Storage
├─ Registry
├─ Security / IAM
└─ Deployment / Operation</code></pre>
<h3 id="kubernetes와의-관계">Kubernetes와의 관계</h3>
<p>Kubernetes와 Container Platform은 완전히 같은 개념은 아니다.</p>
<pre><code class="language-text">Kubernetes
→ Container Orchestration의 중심


Container Platform
→ Kubernetes를 포함하여
   실제 Container 기반 서비스를
   운영하기 위한 전체 환경</code></pre>
<p>즉 Kubernetes가</p>
<blockquote>
<p><strong>많은 Container 기반 Workload를 어떻게 배치하고 원하는 상태로 유지할 것인가</strong></p>
</blockquote>
<p>를 담당한다면,</p>
<p>Container Platform은 그 Kubernetes가 실제 운영 환경에서 동작할 수 있도록 필요한 여러 기술들을 함께 제공하는 더 넓은 개념이다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0b229d6a-913f-409c-8487-12fd2b3381b5/image.png" /></p>
<hr />
<h2 id="k-paas-container-platform">K-PaaS Container Platform</h2>
<p>Container Platform은 목적과 운영 환경에 따라 다양한 구성으로 만들어질 수 있다.</p>
<p>이번 과정에서는 그중 <strong>K-PaaS Container Platform</strong>을 이용하여 실제 Container Platform 환경을 구성하고 사용한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/bd0bde05-a6b4-46bc-aee9-ee1ee5bd623c/image.png" /></p>
<p>K-PaaS Container Platform 역시 Kubernetes를 중심으로 여러 Open Source Software를 결합하여 구성된다.</p>
<p>큰 그림은 다음과 같다.</p>
<pre><code class="language-text">Cloud Infrastructure
        │
        ▼
Infrastructure Provisioning
        │
        ▼
Kubernetes Cluster
        │
        ├─ Container Runtime
        ├─ Network
        ├─ Storage
        ├─ Registry
        ├─ Security
        └─ Deployment Tool
        │
        ▼
Container Platform
        │
        ▼
Application</code></pre>
<p>이후 등장하는 Software들은 각각 이 구조 안에서 특정한 문제를 해결한다.</p>
<hr />
<h2 id="k-paas-container-platform-배포-방식">K-PaaS Container Platform 배포 방식</h2>
<p>K-PaaS Container Platform에서는 환경에 따라 여러 형태로 Platform을 배포할 수 있다.</p>
<h3 id="단독형-배포">단독형 배포</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8d4519d7-31d0-4ff7-af45-26181f5a2e83/image.png" /></p>
<ul>
<li>독립된 Kubernetes Cluster 구성</li>
<li>Container Platform 단독 운영</li>
<li>일반적인 Cloud / Data Center 환경에 적용</li>
</ul>
<pre><code class="language-text">Infrastructure
      ↓
Kubernetes Cluster
      ↓
Container Platform
      ↓
Application</code></pre>
<blockquote>
<p><strong>하나의 독립적인 Kubernetes 환경을 구성하여 Container Platform을 운영하는 방식</strong></p>
</blockquote>
<hr />
<h3 id="edge-배포">Edge 배포</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f2d957cc-f5e6-437e-834e-a3c7fb841edf/image.png" /></p>
<ul>
<li>Edge 환경에 Kubernetes Cluster 구성</li>
<li>중앙 Cloud와 떨어진 위치에서 Workload 실행</li>
<li>현장 중심의 Data 처리</li>
<li>Network 지연 감소가 필요한 환경에 활용</li>
</ul>
<pre><code class="language-text">Central Cloud
      │
      │ 관리 / 연동
      ▼
Edge Environment
      │
      ▼
Kubernetes Cluster
      │
      ▼
Application</code></pre>
<blockquote>
<p><strong>Kubernetes Cluster를 Edge 환경에 배치하여 현장에 가까운 위치에서 Application을 실행하는 방식</strong></p>
</blockquote>
<hr />
<h2 id="container-platform-주요-software">Container Platform 주요 Software</h2>
<p>K-PaaS Container Platform에는 다양한 Open Source Software가 사용된다.</p>
<blockquote>
<p><strong>Container Platform 주요 Software 목록</strong></p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f603edac-5866-4d25-b24e-3bb6803a8416/image.png" /></p>
<p>처음 보면 Software의 종류가 많아 보인다.</p>
<p>하지만 이름을 하나씩 외우기보다,</p>
<blockquote>
<p><strong>Container Platform을 구성하면서 어떤 문제를 해결하기 위해 사용되는가?</strong></p>
</blockquote>
<p>를 기준으로 나누면 이해하기 쉽다.</p>
<pre><code class="language-text">Infrastructure
    ↓
Cluster 구성
    ↓
Runtime
    ↓
Network
    ↓
Storage
    ↓
Application 배포
    ↓
Registry / Security / IAM</code></pre>
<hr />
<h2 id="infrastructure--provisioning">Infrastructure / Provisioning</h2>
<p>Container Platform을 만들기 위해서는 먼저 Kubernetes가 올라갈 Infrastructure가 필요하다.</p>
<pre><code class="language-text">Compute
Network
Storage
   │
   ▼
Infrastructure 구성
   │
   ▼
Kubernetes Cluster</code></pre>
<h3 id="opentofu">OpenTofu</h3>
<blockquote>
<p>클라우드 환경의 Infrastructure를 Code로 생성하고 관리하기 위한 Open Source Provisioning Tool</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4a2b1c9e-9a7b-4332-bb15-cc4d78676824/image.png" /></p>
<h4 id="역할">역할</h4>
<ul>
<li>Infrastructure as Code</li>
<li>Compute Resource 구성</li>
<li>Network 구성</li>
<li>Storage 구성</li>
<li>Infrastructure Provisioning 자동화</li>
</ul>
<pre><code class="language-text">Infrastructure 정의
        ↓
     OpenTofu
        ↓
Cloud Infrastructure 생성</code></pre>
<p>Container Platform 관점에서는</p>
<blockquote>
<p><strong>Kubernetes Cluster가 올라갈 기반 Infrastructure를 준비하는 역할</strong></p>
</blockquote>
<p>로 볼 수 있다.</p>
<hr />
<h3 id="kubespray">Kubespray</h3>
<blockquote>
<p>Kubernetes Cluster 설치 및 구성을 자동화하는 도구</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3dd57047-29b2-4960-ac8b-bbb2be70c5a6/image.png" /></p>
<h4 id="역할-1">역할</h4>
<ul>
<li>Kubernetes Cluster 설치 자동화</li>
<li>여러 Node 구성</li>
<li>Ansible 기반 자동화</li>
<li>반복 가능한 Cluster 구축</li>
</ul>
<pre><code class="language-text">Infrastructure
      │
      ▼
  Kubespray
      │
      ▼
Kubernetes Cluster</code></pre>
<p>즉,</p>
<pre><code class="language-text">OpenTofu
→ Infrastructure 준비

Kubespray
→ 그 Infrastructure 위에
  Kubernetes Cluster 구성</code></pre>
<p>으로 연결해서 볼 수 있다.</p>
<hr />
<h2 id="cluster--container-runtime">Cluster / Container Runtime</h2>
<p>Infrastructure와 Cluster가 준비되었다면 실제 Workload를 관리하고 Container를 실행해야 한다.</p>
<h3 id="kubernetes">Kubernetes</h3>
<blockquote>
<p>Container 기반 Application을 자동으로 배포하고 확장하며 관리하는 Container Orchestration Platform</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9b8a911a-927c-4b2e-8020-675b926a5cda/image.png" /></p>
<h4 id="역할-2">역할</h4>
<ul>
<li>Workload 배치</li>
<li>Desired State 유지</li>
<li>Scaling</li>
<li>Self-Healing</li>
<li>Rollout / Rollback</li>
</ul>
<p>앞 글에서 구조를 자세하게 다뤘으므로 여기서는</p>
<pre><code class="language-text">Kubernetes
→ Container Platform의
  Orchestration 중심</code></pre>
<p>정도로 연결해서 이해하면 된다.</p>
<hr />
<h3 id="cri-o">CRI-O</h3>
<blockquote>
<p>Kubernetes의 CRI(Container Runtime Interface)를 구현하는 Container Runtime</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/60d3a3c5-0b2e-418a-869f-689fc7a68cb9/image.png" /></p>
<p>Kubernetes가 Workload를 어디에 배치할지 결정하더라도 실제 Container를 실행할 Runtime은 별도로 필요하다.</p>
<pre><code class="language-text">Kubernetes
     │
     ▼
   kubelet
     │
     │ CRI
     ▼
   CRI-O
     │
     ▼
Container</code></pre>
<h4 id="역할-3">역할</h4>
<ul>
<li>Kubernetes와 Container Runtime 연결</li>
<li>OCI Container 실행</li>
<li>Container Lifecycle 관리</li>
</ul>
<p>즉,</p>
<pre><code class="language-text">Kubernetes
→ 무엇을 어디에서 실행할지 관리

CRI-O
→ 실제 Container 실행</code></pre>
<p>으로 역할을 구분할 수 있다.</p>
<hr />
<h2 id="network--traffic">Network / Traffic</h2>
<p>Container Platform에서는 여러 Pod와 Service가 서로 통신해야 하며 외부 Traffic도 Cluster 내부로 전달해야 한다.</p>
<pre><code class="language-text">Pod ↔ Pod
Service ↔ Service
External Client → Service</code></pre>
<p>각 영역마다 서로 다른 Network Software가 사용된다.</p>
<hr />
<h3 id="calico">Calico</h3>
<blockquote>
<p>Container 및 Kubernetes 환경에서 Network를 구성하는 Open Source Networking Solution</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/5e9df837-0db5-4016-8ab1-a8612548fcaf/image.png" /></p>
<h4 id="역할-4">역할</h4>
<ul>
<li>Kubernetes Pod Network 구성</li>
<li>Pod 간 통신</li>
<li>Network Policy 적용</li>
<li>CNI 기반 Network 제공</li>
</ul>
<pre><code class="language-text">Pod A
  │
  │ Calico Network
  ▼
Pod B</code></pre>
<p>Container Platform 관점에서는</p>
<blockquote>
<p><strong>Kubernetes Pod들이 서로 통신할 수 있는 Network 기반을 제공</strong></p>
</blockquote>
<p>하는 역할이다.</p>
<hr />
<h3 id="metallb">MetalLB</h3>
<blockquote>
<p>Kubernetes 환경에서 <code>LoadBalancer</code> Type Service를 사용할 수 있도록 지원하는 Load Balancer 구현체</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/754c2f6b-e349-44d6-8ed0-e3a829777798/image.png" /></p>
<p>Cloud Provider에서는 LoadBalancer Service를 생성하면 Cloud의 Load Balancer와 연결되는 경우가 많다.</p>
<p>반면 자체 구축 환경이나 Bare Metal 환경에서는 이러한 기능을 별도로 제공해야 할 수 있다.</p>
<pre><code class="language-text">External Client
      │
      ▼
   MetalLB
      │
      ▼
LoadBalancer Service
      │
      ▼
     Pod</code></pre>
<h4 id="역할-5">역할</h4>
<ul>
<li>LoadBalancer Service 지원</li>
<li>외부 IP 제공</li>
<li>Bare Metal / Private 환경의 Load Balancing 지원</li>
</ul>
<hr />
<h3 id="ingress-nginx-controller">Ingress NGINX Controller</h3>
<blockquote>
<p>Kubernetes Ingress 규칙을 실제 HTTP/HTTPS Traffic 처리로 구현하는 Ingress Controller</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b1f6ea1a-91a5-4508-8a3c-cacaa685cf35/image.png" /></p>
<p>앞에서 Kubernetes의 <code>Ingress</code>는 외부 HTTP/HTTPS Routing 규칙이라고 살펴봤다.</p>
<p>하지만 Ingress Resource 자체는 <strong>규칙</strong>이다.</p>
<p>실제 Traffic을 처리하는 Controller가 필요하다.</p>
<pre><code class="language-text">Client
   │
   ▼
Ingress NGINX Controller
   │
   │ Ingress Rule
   ▼
Service
   │
   ▼
Pod</code></pre>
<h4 id="역할-6">역할</h4>
<ul>
<li>HTTP / HTTPS Traffic 처리</li>
<li>Host 기반 Routing</li>
<li>Path 기반 Routing</li>
<li>Ingress Resource 구현</li>
</ul>
<hr />
<h3 id="istio">Istio</h3>
<blockquote>
<p>Kubernetes 기반 Application을 위한 Service Mesh</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c9c71335-e907-44f4-a7fe-2d93001a86d3/image.png" /></p>
<p>Application이 MSA 구조로 커지면 Service 사이의 통신 자체를 관리해야 하는 문제가 생긴다.</p>
<pre><code class="language-text">Service A
   │
   ▼
Service B
   │
   ▼
Service C</code></pre>
<p>Istio는 이러한 Service 간 통신에 대한 추가적인 관리 기능을 제공한다.</p>
<h4 id="역할-7">역할</h4>
<ul>
<li>Service 간 Traffic 관리</li>
<li>Traffic Policy</li>
<li>Observability</li>
<li>Security Policy</li>
</ul>
<p>정리하면 Network 영역은 다음처럼 볼 수 있다.</p>
<pre><code class="language-text">Pod Network
→ Calico

외부 IP / LoadBalancer
→ MetalLB

HTTP / HTTPS 진입
→ Ingress NGINX Controller

Service 간 Traffic 관리
→ Istio</code></pre>
<hr />
<h2 id="application--deployment">Application / Deployment</h2>
<p>Container Platform에서는 Application을 반복적으로 빌드하고 배포하기 위한 도구도 필요하다.</p>
<h3 id="helm">Helm</h3>
<blockquote>
<p>Kubernetes Application을 Package 형태로 관리하고 배포하기 위한 Package Manager</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1f384aab-118e-42d8-bc7a-77d1bd210afe/image.png" /></p>
<p>Kubernetes Application이 커지면 여러 Manifest가 필요할 수 있다.</p>
<pre><code class="language-text">Deployment.yaml
Service.yaml
ConfigMap.yaml
Secret.yaml
...</code></pre>
<p>이를 Application 단위로 묶어 관리할 수 있도록 Helm에서는 <strong>Chart</strong>라는 Package 단위를 사용한다.</p>
<pre><code class="language-text">Kubernetes Manifest
       │
       ▼
      Chart
       │
       ▼
      Helm
       │
       ▼
Application 배포</code></pre>
<h4 id="역할-8">역할</h4>
<ul>
<li>Kubernetes Package 관리</li>
<li>Manifest Template화</li>
<li>반복 배포</li>
<li>환경별 설정 관리</li>
</ul>
<hr />
<h3 id="podman">Podman</h3>
<blockquote>
<p>Linux 환경에서 Container Image와 Container를 개발·관리·실행하기 위한 Container Tool</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/97e1e05b-7a9f-489a-a5e3-20d576836dbb/image.png" /></p>
<h4 id="역할-9">역할</h4>
<ul>
<li>Container Image Build</li>
<li>Container 실행</li>
<li>Container 관리</li>
<li>Daemonless 방식 지원</li>
</ul>
<p>Container Platform의 전체 흐름에서는</p>
<pre><code class="language-text">Application
     │
     ▼
Container Image
     │
   Podman
     │
     ▼
Registry
     │
     ▼
Kubernetes</code></pre>
<p>와 같이 Application을 Container Image로 만들고 관리하는 도구로 연결해서 볼 수 있다.</p>
<hr />
<h2 id="storage">Storage</h2>
<p>Pod는 언제든지 재생성될 수 있기 때문에 Application과 Data의 생명주기를 분리할 Storage가 필요하다.</p>
<pre><code class="language-text">Pod Lifecycle
      ≠
Data Lifecycle</code></pre>
<p>K-PaaS Container Platform에서는 이를 위한 다양한 Storage Solution을 사용할 수 있다.</p>
<hr />
<h3 id="nfs">NFS</h3>
<blockquote>
<p>Network를 통해 여러 Host가 File을 공유할 수 있도록 하는 Network File System</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4e05578e-13c2-4a40-b05e-1ff7a1962534/image.png" /></p>
<h4 id="역할-10">역할</h4>
<ul>
<li>Network 기반 File 공유</li>
<li>여러 Node에서 공통 Storage 접근</li>
<li>비교적 단순한 Shared Storage 구성</li>
</ul>
<pre><code class="language-text">Node A ─┐
Node B ─┼──▶ NFS Storage
Node C ─┘</code></pre>
<hr />
<h3 id="rook--ceph">Rook / Ceph</h3>
<blockquote>
<p>Kubernetes 환경에서 분산 Storage를 구성하기 위한 Rook과 Ceph</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a4db766f-c9ff-4ae3-a8fe-498f4c186366/image.png" /></p>
<p>둘은 역할이 다르다.</p>
<pre><code class="language-text">Ceph
→ 실제 Distributed Storage System


Rook
→ Kubernetes에서 Ceph를
  배포하고 관리하는 Operator</code></pre>
<h4 id="ceph">Ceph</h4>
<ul>
<li>Distributed Storage</li>
<li>높은 확장성</li>
<li>Block / File / Object Storage 지원</li>
</ul>
<h4 id="rook">Rook</h4>
<ul>
<li>Kubernetes 기반 Storage Orchestration</li>
<li>Ceph Cluster 배포 및 관리 자동화</li>
</ul>
<p>전체적으로 보면</p>
<pre><code class="language-text">Kubernetes
    │
    ▼
   Rook
    │
    ▼
   Ceph
    │
    ▼
Distributed Storage</code></pre>
<p>구조로 볼 수 있다.</p>
<hr />
<h2 id="platform-운영-software">Platform 운영 Software</h2>
<p>Kubernetes Cluster가 동작하더라도 Platform 운영을 위해서는 Image 저장, Secret 관리, 사용자 인증 등의 기능이 추가로 필요하다.</p>
<hr />
<h3 id="harbor">Harbor</h3>
<blockquote>
<p>Open Source Container Registry</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e2ebe20f-5b8c-4907-b412-eabb819a7024/image.png" /></p>
<h4 id="역할-11">역할</h4>
<ul>
<li>Container Image 저장</li>
<li>Private Registry</li>
<li>Image 관리</li>
<li>Kubernetes에서 사용할 Image 제공</li>
</ul>
<pre><code class="language-text">Application
     │
     ▼
Container Image
     │
     ▼
   Harbor
     │
     ▼
Kubernetes Pull</code></pre>
<hr />
<h3 id="vault">Vault</h3>
<blockquote>
<p>Secret과 암호화 정보를 관리하는 System</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e908387f-5c67-471a-a849-0721004bb9c0/image.png" /></p>
<h4 id="관리-대상">관리 대상</h4>
<ul>
<li>Password</li>
<li>Token</li>
<li>API Key</li>
<li>Certificate</li>
<li>Encryption Key</li>
</ul>
<pre><code class="language-text">Application
     │
     ▼
   Vault
     │
     ▼
Secret 제공</code></pre>
<p>Container Platform의 여러 Component가 필요한 Secret을 중앙에서 안전하게 관리하기 위한 도구로 사용될 수 있다.</p>
<hr />
<h3 id="keycloak">Keycloak</h3>
<blockquote>
<p>Open Source IAM(Identity and Access Management) Software</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/95f311ac-8d77-4a3e-9872-85ad7c16e88d/image.png" /></p>
<h4 id="역할-12">역할</h4>
<ul>
<li>Authentication</li>
<li>Authorization</li>
<li>SSO</li>
<li>Identity 관리</li>
<li>OAuth 2.0 / OpenID Connect / SAML 지원</li>
</ul>
<pre><code class="language-text">User
  │
  ▼
Keycloak
  │
  ▼
Authentication / Authorization
  │
  ▼
Platform</code></pre>
<hr />
<h3 id="mariadb">MariaDB</h3>
<blockquote>
<p>Open Source Relational Database Management System</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d25b47ae-39f5-4098-b9bb-23e049dd4d25/image.png" /></p>
<p>K-PaaS Container Platform에서는 Portal 등 Platform 구성 요소가 필요한 관계형 Data를 저장하기 위한 Database로 사용된다.</p>
<h4 id="역할-13">역할</h4>
<ul>
<li>Portal Data 저장</li>
<li>Platform 관련 관계형 Data 관리</li>
</ul>
<p>여기서는 MariaDB 자체의 동작보다</p>
<blockquote>
<p><strong>Platform 내부 Application 역시 Data 저장을 위한 Database가 필요하다</strong></p>
</blockquote>
<p>는 관점으로 이해하면 된다.</p>
<hr />
<h2 id="container-platform-전체-구성">Container Platform 전체 구성</h2>
<p>지금까지 살펴본 Software들을 다시 합쳐보면 각각의 역할이 보인다.</p>
<pre><code class="language-text">                     Container Platform

┌─────────────────────────────────────────────────┐
│ Infrastructure                                  │
│                                                 │
│ OpenTofu                                        │
│    ↓                                            │
│ Cloud Infrastructure                            │
│    ↓                                            │
│ Kubespray                                       │
│    ↓                                            │
│ Kubernetes Cluster                              │
├─────────────────────────────────────────────────┤
│ Cluster / Runtime                               │
│                                                 │
│ Kubernetes                                      │
│ CRI-O                                           │
├─────────────────────────────────────────────────┤
│ Network / Traffic                               │
│                                                 │
│ Calico                                          │
│ MetalLB                                         │
│ Ingress NGINX Controller                        │
│ Istio                                           │
├─────────────────────────────────────────────────┤
│ Storage                                         │
│                                                 │
│ NFS                                             │
│ Rook / Ceph                                     │
├─────────────────────────────────────────────────┤
│ Application / Deployment                        │
│                                                 │
│ Podman                                          │
│ Helm                                            │
├─────────────────────────────────────────────────┤
│ Platform Service                                │
│                                                 │
│ Harbor   Vault   Keycloak   MariaDB             │
└─────────────────────────────────────────────────┘</code></pre>
<p>각 Software를 따로 외우기보다는 다음 흐름으로 이해하는 것이 좋다.</p>
<pre><code class="language-text">Infrastructure 생성
→ OpenTofu

Kubernetes Cluster 설치
→ Kubespray

Workload 관리
→ Kubernetes

Container 실행
→ CRI-O

Pod Network
→ Calico

외부 LoadBalancer
→ MetalLB

HTTP / HTTPS Traffic
→ Ingress NGINX Controller

Service Mesh
→ Istio

Application Package 배포
→ Helm

Container Image 관리
→ Podman / Harbor

Persistent Storage
→ NFS / Rook / Ceph

Secret
→ Vault

Identity / Access
→ Keycloak

Portal Data
→ MariaDB</code></pre>
<p>결국 Container Platform은 특정 Software 하나를 의미하는 것이 아니다.</p>
<blockquote>
<p><strong>Kubernetes를 중심으로 Container 기반 서비스를 실제로 운영하는 데 필요한 Infrastructure, Network, Storage, Security, Registry, Deployment 등의 기술을 하나의 환경으로 조립한 것</strong></p>
</blockquote>
<p>으로 이해할 수 있다.</p>
<hr />
<h2 id="container-platform이-올라갈-cloud-infrastructure">Container Platform이 올라갈 Cloud Infrastructure</h2>
<p>지금까지는 Container Platform 내부에 어떤 Software가 존재하는지 살펴봤다.</p>
<p>하지만 이러한 Platform도 결국 실제 Infrastructure 위에서 실행된다.</p>
<pre><code class="language-text">Cloud Infrastructure
        ↓
VM / Network / Storage
        ↓
Kubernetes Cluster
        ↓
Container Platform
        ↓
Application</code></pre>
<p>이후 실습에서는 실제 Cloud Infrastructure를 구성하고 그 위에 Kubernetes Cluster와 Container Platform을 배포해본다.</p>
<h3 id="nhn-cloud">NHN Cloud</h3>
<p>실습은 <strong>NHN Cloud</strong> 환경에서 진행한다.</p>
<p>NHN Cloud Architecture의 예시는 다음과 같다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6e2b86ec-650d-4e5f-b1c5-94d15adb6354/image.png" /></p>
<p>Infrastructure 관점에서는</p>
<ul>
<li>VPC</li>
<li>Subnet</li>
<li>Compute Instance</li>
<li>Load Balancer</li>
<li>Storage</li>
<li>Network</li>
</ul>
<p>등의 Resource를 구성하고,</p>
<p>그 위에 Kubernetes Cluster 및 Container Platform을 올리는 흐름으로 이어진다.</p>
<hr />
<h3 id="aws-architecture-참고">AWS Architecture 참고</h3>
<p>Cloud Provider는 달라도 기본적인 Infrastructure 구성 관점은 유사하다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/af49750c-4a10-4f19-b3f1-b8f6f995b041/image.png" /></p>
<pre><code class="language-text">Cloud Provider

VPC
 ↓
Subnet
 ↓
Compute / Network / Storage
 ↓
Kubernetes
 ↓
Container Platform</code></pre>
<p>즉 특정 Cloud Provider의 이름보다</p>
<blockquote>
<p><strong>Container Platform 역시 결국 Compute, Network, Storage라는 IaaS Resource 위에 구축된다</strong></p>
</blockquote>
<p>는 점이 중요하다.</p>
<hr />
<h2 id="전체-흐름">전체 흐름</h2>
<p>앞 글에서 배웠던 Kubernetes부터 이번 글의 Container Platform까지 연결하면 다음과 같다.</p>
<pre><code class="language-text">Container
    │
    ▼
Kubernetes
Container Orchestration
    │
    ▼
Cluster
    │
    │ 이것만으로 운영 환경이
    │ 완성되는 것은 아님
    ▼
Container Platform
    │
    ├─ Infrastructure
    ├─ Runtime
    ├─ Network
    ├─ Storage
    ├─ Registry
    ├─ Security
    └─ Deployment
    │
    ▼
실제 Container 기반 서비스 운영</code></pre>
<p>K-PaaS Container Platform의 관점에서는 다음처럼 연결할 수 있다.</p>
<pre><code class="language-text">Cloud Infrastructure
        │
        ▼
     OpenTofu
        │
        ▼
     Kubespray
        │
        ▼
 Kubernetes Cluster
        │
        ├─ CRI-O
        ├─ Calico
        ├─ MetalLB
        ├─ Ingress NGINX
        ├─ Istio
        ├─ NFS / Rook / Ceph
        ├─ Helm
        ├─ Harbor
        ├─ Vault
        └─ Keycloak
        │
        ▼
Container Platform
        │
        ▼
Application</code></pre>
<hr />
<h2 id="마치며">마치며</h2>
<p>앞에서는 Kubernetes가 Container 기반 Workload를 <strong>어떻게 관리하는가</strong>를 살펴봤다.</p>
<p>이번에는 한 단계 더 나아가,</p>
<blockquote>
<p><strong>그 Kubernetes를 실제 서비스 운영을 위한 Platform으로 만들기 위해 어떤 기술들이 필요한가</strong></p>
</blockquote>
<p>를 살펴봤다.</p>
<p>Kubernetes는 Container Orchestration의 중심 역할을 하지만 실제 Platform을 구성하기 위해서는</p>
<pre><code class="language-text">Infrastructure
Runtime
Network
Storage
Registry
Security
Deployment</code></pre>
<p>등 여러 영역이 함께 필요하다.</p>
<p>그리고 K-PaaS Container Platform은 이러한 영역에 다양한 Open Source Software를 조합하여 하나의 Container 운영 환경을 구성한다.</p>