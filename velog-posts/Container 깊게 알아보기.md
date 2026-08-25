<p>앞선 글에서는 Container가 등장하게 된 배경부터 Dockerfile, Image, Layer, Volume, Container 실행까지 전반적인 구조를 살펴봤다.</p>
<p>그 과정에서 Docker의 흐름을 대략 다음과 같이 정리했다.</p>
<pre><code class="language-text">Dockerfile
    ↓
Image
    ↓
Container
    ↓
Application</code></pre>
<p>그리고 VM과 달리 Container는 Guest OS를 하나 새로 띄우는 것이 아니라, <strong>Host의 Linux Kernel을 공유하며 Application을 실행한다</strong>는 것도 알아봤다.</p>
<p>여기까지만 보면 꽤 단순하다.</p>
<p>그런데 여기서 한 가지 의문이 생긴다.</p>
<p><strong>왜 Container는 Linux Kernel 위에서 동작해야 하는 걸까?</strong></p>
<p>Container를 실제로 사용하다 보면 조금 이상한 점들이 보이기 시작한다.</p>
<p>Image Layer는 Read-Only인데 Container에서는 파일을 자유롭게 만들고 수정할 수 있다. Host에서는 수천 번대 PID를 가진 Process가 Container 안에서는 PID 1이라고 나오고, 평범한 Linux Process라고 했는데 자기만의 <code>/</code>, IP, Network Interface까지 가진 것처럼 보인다. 심지어 CPU와 Memory도 Container마다 따로 제한할 수 있다.</p>
<p>그런데 우리는 이런 환경을 직접 만든 적이 없다.</p>
<pre><code class="language-bash">docker run ...</code></pre>
<p>이 한 줄이면 끝이다.</p>
<p>결국 Container를 이해하려면 Docker 명령어보다 더 아래로 내려가야 한다.</p>
<p><strong>Linux Kernel이 제공하는 File System, Namespace, Cgroup, Network, Security 기능들이 어떻게 하나의 Container 실행 환경으로 조합되는지</strong>를 볼 필요가 있다.</p>
<p>앞선 글에서 Container를 하나의 실행 단위로 바라봤다면, 이번에는 그 상자를 열어 실제 내부 구조를 조금 더 깊게 살펴보자.</p>
<hr />
<h2 id="container의-본질">Container의 본질</h2>
<p>먼저 가장 중요한 전제부터 잡고 가자.</p>
<p><strong>Container 안에서 실행되는 Application은 결국 Linux Process다.</strong></p>
<p>Docker만의 특별한 Process가 따로 존재하는 것이 아니다. Host의 다른 Process와 마찬가지로 Linux Kernel이 Scheduling하고, Memory를 할당하며, System Call을 처리한다.</p>
<pre><code class="language-text">Linux Kernel
    │
    ├─ Host Process
    ├─ Host Process
    ├─ Container Process
    └─ Container Process</code></pre>
<p>그렇다면 평범한 Process와 Container Process의 차이는 무엇일까?</p>
<p>Container는 Process 자체가 특별한 것이 아니라, <strong>그 Process가 실행되는 환경을 특별하게 구성한 것</strong>에 가깝다.</p>
<p>Process가 바라보는 File System을 따로 만들고, Process 목록과 Network를 격리하고, CPU와 Memory 사용량을 제한하며, 사용할 수 있는 권한도 줄인다.</p>
<p>즉 Container를 조금 단순하게 표현하면 다음과 같다.</p>
<pre><code class="language-text">Container
=
Linux Process
+
격리된 실행 환경</code></pre>
<p>이 관점이 잡히면 이후의 개념들이 하나씩 연결되기 시작한다.</p>
<hr />
<h2 id="container-file-system">Container File System</h2>
<p>Process가 실행되려면 먼저 File System이 필요하다.</p>
<p>Python Application이라면 Python Binary와 Library가 있어야 하고, Spring Boot Application이라면 JRE와 JAR 파일이 있어야 한다.</p>
<p>Docker에서는 이런 실행 환경을 Image에 담는다.</p>
<h3 id="image-layer">Image Layer</h3>
<p>Container Image는 하나의 거대한 파일이라기보다 여러 <strong>Read-Only Layer와 Metadata</strong>의 묶음에 가깝다.</p>
<p>예를 들어 다음 Dockerfile이 있다고 하자.</p>
<pre><code class="language-dockerfile">FROM ubuntu:24.04

RUN apt-get update &amp;&amp; \
    apt-get install -y python3

COPY webserver.py /app/</code></pre>
<p>개념적으로는 Ubuntu File System 위에 Python 설치 결과가 쌓이고, 그 위에 Application 파일이 추가된다.</p>
<pre><code class="language-text">Application
────────────── Layer 3

Python
────────────── Layer 2

Ubuntu RootFS
────────────── Layer 1</code></pre>
<p>각 Layer는 Read-Only다.</p>
<p>이 구조 덕분에 여러 Image가 동일한 Base Layer를 공유할 수 있고, Image 전체를 매번 복제하지 않아도 된다.</p>
<p>문제는 Container가 실행된 이후다.</p>
<p>Image Layer가 Read-Only라면 Container 안에서 파일을 생성하고 수정하는 것은 어떻게 가능한 걸까?</p>
<h3 id="overlayfs와-rootfs">OverlayFS와 RootFS</h3>
<p>Docker가 Linux에서 사용하는 대표적인 Storage 구조 중 하나가 <code>overlay2</code>이고, 그 기반에 <strong>OverlayFS</strong>가 있다.</p>
<p>OverlayFS의 핵심은 여러 File System Layer를 하나의 File System처럼 보여주는 것이다.</p>
<pre><code class="language-text">                Container
                    │
                read / write
                    ▼
                 Merged
                    │
                OverlayFS
               /         \
          UpperDir       LowerDir
             RW             RO</code></pre>
<p><code>LowerDir</code>에는 Image의 Read-Only Layer가 놓이고, <code>UpperDir</code>에는 Container가 실행된 이후 발생한 변경 결과가 저장된다.</p>
<p>Container Process가 실제로 바라보는 것은 <code>Merged</code>다.</p>
<p>Application은 그냥 자신의 <code>/app/test.txt</code>에 파일을 쓰는 것처럼 동작하고, OverlayFS가 그 요청을 처리해 실제 변경 결과를 UpperDir에 기록한다.</p>
<p>새로운 파일을 만들면 UpperDir에 생성된다.</p>
<p>LowerDir에만 존재하는 파일을 수정하면 먼저 UpperDir으로 복사한 뒤 수정하는 <strong>Copy-on-Write</strong>가 수행된다.</p>
<pre><code class="language-text">LowerDir
/etc/example.conf
        │
        │ Copy-Up
        ▼
UpperDir
/etc/example.conf  ← 수정</code></pre>
<p>그래서 Image의 원본 Layer는 그대로 유지하면서 Container마다 서로 다른 변경 상태를 가질 수 있다.</p>
<p>삭제도 비슷하다.</p>
<p>LowerDir의 파일을 실제로 지우는 대신 UpperDir에 Whiteout 정보를 남겨 Merged에서는 파일이 사라진 것처럼 보이게 한다.</p>
<p><code>WorkDir</code>은 이런 OverlayFS 내부 처리를 위해 사용하는 작업 공간이다.</p>
<p>결국 역할을 정리하면 다음과 같다.</p>
<ul>
<li><code>LowerDir</code>: Image의 Read-Only 원본</li>
<li><code>UpperDir</code>: Container 변경 결과가 저장되는 Writable 영역</li>
<li><code>Merged</code>: Container가 실제로 바라보는 통합 File System</li>
<li><code>WorkDir</code>: OverlayFS 내부 작업 공간</li>
</ul>
<p>그리고 이 <code>Merged</code> 영역을 Container Process의 <code>/</code>로 사용하도록 구성한 것이 <strong>Container RootFS</strong>다.</p>
<pre><code class="language-text">Image Layers
    +
Writable Layer
      ↓
  OverlayFS
      ↓
   Merged
      ↓
Container RootFS</code></pre>
<p>Container마다 새로운 Disk가 하나 생기는 것이 아니다.</p>
<p><strong>Image Layer와 Writable Layer를 조합한 File System View를 Process의 Root로 보여주는 것</strong>이다.</p>
<hr />
<h2 id="container의-격리">Container의 격리</h2>
<p>File System만 따로 보여준다고 Container가 완성되는 것은 아니다.</p>
<p>Host의 Process 목록이 그대로 보이고, Hostname이나 Mount 구성이 모두 같다면 여전히 하나의 독립적인 실행 환경처럼 느껴지기 어렵다.</p>
<p>이때 사용하는 것이 <strong>Linux Namespace</strong>다.</p>
<h3 id="namespace">Namespace</h3>
<p>Namespace는 Process가 바라볼 수 있는 Kernel Resource의 범위를 분리한다.</p>
<table>
<thead>
<tr>
<th>Namespace</th>
<th>격리하는 대상</th>
</tr>
</thead>
<tbody><tr>
<td>PID</td>
<td>Process ID와 Process 목록</td>
</tr>
<tr>
<td>MNT</td>
<td>Mount Point와 File System View</td>
</tr>
<tr>
<td>NET</td>
<td>Network Interface, IP, Port, Routing</td>
</tr>
<tr>
<td>UTS</td>
<td>Hostname</td>
</tr>
<tr>
<td>IPC</td>
<td>Shared Memory, Message Queue</td>
</tr>
<tr>
<td>USER</td>
<td>UID / GID</td>
</tr>
</tbody></table>
<p>핵심은 Container마다 Kernel을 새로 만드는 것이 아니라는 점이다.</p>
<p><strong>Kernel은 하나지만, Process마다 서로 다른 View를 제공한다.</strong></p>
<p>예를 들어 Host에서는 어떤 Application Process가 PID 4821이라고 보일 수 있다.</p>
<pre><code class="language-text">Host PID Namespace
PID 4821  python</code></pre>
<p>하지만 Container의 PID Namespace 안에서는 같은 Process가 PID 1로 보일 수 있다.</p>
<pre><code class="language-text">Container PID Namespace
PID 1  python</code></pre>
<p>Process가 두 개 존재하는 것이 아니다.</p>
<p><strong>같은 Process를 서로 다른 PID Namespace에서 보고 있는 것</strong>이다.</p>
<p>Mount Namespace 역시 같은 방식으로 Process마다 서로 다른 Mount 구성을 보여주고, UTS Namespace는 Hostname을 분리한다.</p>
<p>Network Namespace는 Process가 바라보는 Network 환경을 분리하는데, 이 부분은 뒤에서 별도로 살펴보자.</p>
<p>Namespace는 반드시 분리해야 하는 것도 아니다.</p>
<p>필요하다면 특정 Namespace를 Host와 공유하도록 구성할 수도 있다.</p>
<p>결국 Docker의 여러 격리 옵션도 아래로 내려가 보면 <strong>어떤 Namespace를 분리하고 어떤 Namespace를 공유할 것인가</strong>의 문제로 연결된다.</p>
<h3 id="cgroup">Cgroup</h3>
<p>Namespace가 Process에게 <strong>무엇을 보여줄 것인가</strong>를 제어한다면, Cgroup은 <strong>얼마나 사용할 수 있는가</strong>를 제어한다.</p>
<p>Container는 Host의 CPU, Memory, Disk 같은 실제 Hardware Resource를 공유한다.</p>
<p>따라서 아무런 제한이 없다면 하나의 Container가 Resource를 과도하게 점유해 다른 Container와 Host Process까지 영향을 줄 수 있다.</p>
<p>Cgroup은 Process Group 단위로 CPU, Memory, I/O, Process 수 등을 관리한다.</p>
<p>예를 들어 CPU 사용량이 설정된 한도에 도달하면 실행 시간을 제한하는 <strong>Throttling</strong>이 발생할 수 있다.</p>
<p>반면 Memory Limit을 초과하고 추가 Memory를 확보할 수 없다면 OOM 상황으로 이어져 Process가 종료될 수 있다.</p>
<pre><code class="language-text">Namespace
→ 보이는 환경을 분리한다.

Cgroup
→ 사용할 수 있는 Resource를 제한한다.</code></pre>
<p>둘을 함께 사용함으로써 같은 Kernel 위의 Process들을 서로 다른 실행 환경처럼 운영할 수 있다.</p>
<h3 id="권한-제어">권한 제어</h3>
<p>Container Process도 결국 Host Kernel에 System Call을 요청한다.</p>
<p>따라서 환경과 Resource를 분리하는 것만으로는 충분하지 않고, <strong>무엇을 할 수 있는가</strong>도 제한해야 한다.</p>
<p>Container Runtime은 Linux의 User, Capability, seccomp, AppArmor 같은 Security 기능을 활용할 수 있다.</p>
<p>Application이 root 권한을 필요로 하지 않는다면 일반 User로 실행하고, 모든 root 권한이 필요한 것이 아니라면 필요한 Capability만 허용할 수 있다.</p>
<p><code>seccomp</code>를 이용하면 Process가 사용할 수 있는 System Call 자체도 제한할 수 있다.</p>
<p>즉 Container의 격리는 하나의 기능으로 만들어지는 것이 아니다.</p>
<p><strong>Namespace, Cgroup, Linux Security 기능이 함께 조합된 결과</strong>다.</p>
<hr />
<h2 id="container-network">Container Network</h2>
<p>일반적인 Linux Process는 자신이 속한 Network Namespace의 Network 환경을 사용한다.</p>
<p>Docker는 Container를 독립된 실행 환경으로 만들기 위해 각 Container에 별도의 <strong>Network Namespace</strong>를 구성한다.</p>
<h3 id="network-namespace">Network Namespace</h3>
<p>Network Namespace는 Process가 바라보는 Network 환경을 분리한다.</p>
<p>각 Container는 서로 다른 Network Namespace를 가지며, 그 안에서 자신만의 Network Interface, IP Address, Routing Table, Port 공간을 가진다.</p>
<pre><code class="language-text">Container A Network Namespace

eth0
172.18.0.2
Routing Table
Port 공간


Container B Network Namespace

eth0
172.18.0.3
Routing Table
Port 공간</code></pre>
<p>그래서 두 Container가 모두 <code>8080</code> Port를 사용해도 충돌하지 않는다.</p>
<pre><code class="language-text">Container A
172.18.0.2:8080

Container B
172.18.0.3:8080</code></pre>
<p>서로 다른 Network Namespace 안에 있기 때문에 각자 독립된 Network 공간을 사용하는 것이다.</p>
<p>하지만 Network Namespace를 분리하는 것만으로는 문제가 하나 생긴다.</p>
<p>Container의 Network가 Host와 분리되었으니 <strong>Host나 다른 Container와 통신할 경로도 필요하다.</strong></p>
<p>이를 다시 연결하기 위해 사용하는 것이 <code>veth pair</code>다.</p>
<p><code>veth</code>는 Virtual Ethernet Interface로, 두 개의 Interface가 한 쌍으로 연결되어 있다.</p>
<p>쉽게 말하면 양쪽 끝이 연결된 가상의 Network Cable이다.</p>
<p>Docker는 한쪽을 Container의 Network Namespace 안으로 넣어 <code>eth0</code>로 사용하고, 반대쪽은 Host Network Namespace에 남긴다.</p>
<pre><code class="language-text">┌─────────────────────────┐        ┌─────────────────────────┐
│ Container Network NS    │        │ Host Network NS         │
│                         │        │                         │
│        eth0             │◀══════▶│       vethXXXX          │
│   172.18.0.2            │ veth   │           │             │
│                         │ pair   │           ▼             │
└─────────────────────────┘        │      Linux Bridge       │
                                   └─────────────────────────┘</code></pre>
<p>Container가 <code>eth0</code>를 통해 Packet을 보내면 veth pair의 반대편인 Host의 veth로 전달된다.</p>
<p>즉 역할을 단순하게 나누면 다음과 같다.</p>
<blockquote>
<p><strong>Network Namespace는 Container의 Network 공간을 분리하고, veth는 분리된 Container Network와 Host Network 사이를 연결한다.</strong></p>
</blockquote>
<h3 id="host로-들어온-요청은-container까지-어떻게-전달될까">Host로 들어온 요청은 Container까지 어떻게 전달될까?</h3>
<p>예를 들어 Spring Application이 Container 내부의 <code>8080</code> Port에서 실행되고 있다고 하자.</p>
<pre><code class="language-text">Container
172.18.0.2:8080</code></pre>
<p>외부 Client는 일반적으로 Container의 내부 IP를 직접 사용하는 대신 Host로 요청을 보낸다.</p>
<p>그래서 다음과 같이 Host의 <code>8888</code> Port와 Container의 <code>8080</code> Port를 연결한다.</p>
<pre><code class="language-bash">docker run -p 8888:8080 my-app</code></pre>
<p>사용자는 다음 주소로 요청한다.</p>
<pre><code class="language-text">HostIP:8888</code></pre>
<p>Host에서는 Port Publishing에 따라 이 요청의 목적지를 Container의 IP와 Port로 전달할 수 있도록 Network 규칙이 구성된다.</p>
<p>개념적으로 보면 다음과 같다.</p>
<pre><code class="language-text">HostIP:8888
      ↓
DNAT
      ↓
172.18.0.2:8080</code></pre>
<p>그리고 Packet은 Host의 Network 구조를 따라 Container까지 전달된다.</p>
<pre><code class="language-text">Client
   │
   │ HostIP:8888
   ▼
Host Network
   │
   │ DNAT
   ▼
172.18.0.2:8080
   │
   ▼
Linux Bridge
   │
   ▼
Host의 veth
   ║
   ║ veth pair
   ▼
Container eth0
   │
   ▼
Application :8080</code></pre>
<p>즉 <code>-p 8888:8080</code>을 사용했을 때 벌어지는 일을 단순하게 보면,</p>
<blockquote>
<p><strong>Host의 8888 Port로 들어온 요청의 목적지를 Container의 IP:8080으로 연결하고, Bridge와 veth를 통해 해당 Container의 Network Namespace까지 전달하는 것</strong></p>
</blockquote>
<p>이다.</p>
<p>여기에서 각 기능의 역할은 구분할 필요가 있다.</p>
<p>Container의 <code>172.18.0.2</code> 같은 IP를 관리하고 할당하는 것은 Docker Network의 <strong>IPAM</strong>이고, NAT는 이미 구성된 Network 사이에서 <strong>주소를 변환</strong>하는 역할을 한다.</p>
<p>Dockerfile의</p>
<pre><code class="language-dockerfile">EXPOSE 8080</code></pre>
<p>은 Container가 어떤 Port를 사용할지 나타내는 Metadata에 가깝다.</p>
<p>실제로 Host Port와 Container Port를 연결하는 것은</p>
<pre><code class="language-bash">-p 8888:8080</code></pre>
<p>과 같은 Port Publishing이다.</p>
<h3 id="container끼리는-어떻게-통신할까">Container끼리는 어떻게 통신할까?</h3>
<p>Container A와 Container B는 서로 다른 Network Namespace를 사용한다.</p>
<pre><code class="language-text">Container A NS                  Container B NS

172.18.0.2                      172.18.0.3
    eth0                            eth0</code></pre>
<p>따라서 두 Container가 Network Namespace 자체를 공유하는 것은 아니다.</p>
<p>대신 각 Container의 <code>eth0</code>와 연결된 veth pair의 반대쪽 끝이 Host Network Namespace에 존재한다.</p>
<p>그리고 Host 쪽 veth들을 <strong>Linux Bridge</strong>에 연결한다.</p>
<p>Linux Bridge는 여러 Network Interface를 연결하는 가상의 Switch와 비슷하다.</p>
<pre><code class="language-text">┌─────────────────┐                  ┌─────────────────┐
│ Container A NS  │                  │ Container B NS  │
│                 │                  │                 │
│ 172.18.0.2      │                  │ 172.18.0.3      │
│     eth0        │                  │     eth0        │
└──────┬──────────┘                  └──────┬──────────┘
       ║                                    ║
       ║ veth pair                          ║ veth pair
       ║                                    ║
     vethA                                vethB
       │                                    │
       └────────── Linux Bridge ────────────┘
                     Host NS</code></pre>
<p>Container A가 Container B로 Packet을 보내면 다음 경로를 거친다.</p>
<pre><code class="language-text">Container A
172.18.0.2
     │
    eth0
     │
     ║ veth pair
     ▼
Host vethA
     │
     ▼
Linux Bridge
     │
     ▼
Host vethB
     ║
     ║ veth pair
     ▼
    eth0
     │
Container B
172.18.0.3</code></pre>
<p>즉 서로 다른 Network Namespace끼리 직접 연결되는 것이 아니다.</p>
<blockquote>
<p><strong>각 Network Namespace를 veth를 통해 Host로 연결하고, Host 쪽 veth들을 같은 Linux Bridge에 묶어 Container끼리 통신할 수 있게 만드는 것</strong>이다.</p>
</blockquote>
<p>Docker의 기본 <code>bridge</code> Network에서는 <code>docker0</code> Bridge를 통해 Container끼리 IP 기반으로 통신할 수 있다.</p>
<p>하지만 기본 <code>bridge</code> Network에서는 Container 이름을 이용한 자동 DNS Resolution이 기본적으로 제공되지 않는다.</p>
<p>여러 Container를 함께 구성할 때는 보통 User-defined Bridge Network를 만든다.</p>
<pre><code class="language-bash">docker network create skala</code></pre>
<p>그리고 여러 Container를 <code>skala</code> Network에 연결하면 각자의 Network Namespace와 IP를 유지한 상태로 같은 Bridge Network를 통해 통신한다.</p>
<pre><code class="language-text">Container A NS
      │
     veth
      │
      ▼
  skala Bridge
      ▲
      │
     veth
      │
Container B NS</code></pre>
<p>User-defined Bridge Network에서는 Docker의 Embedded DNS도 사용할 수 있다.</p>
<p>예를 들어 Backend와 MariaDB Container가 같은 <code>skala</code> Network에 있다면,</p>
<pre><code class="language-text">backend → mariadb:3306</code></pre>
<p>처럼 Container 이름이나 Network Alias를 이용해 접근할 수 있다.</p>
<p>여기서도 두 Container가 같은 Network Namespace를 사용하는 것은 아니다.</p>
<p>각자의 Network Namespace와 IP는 그대로 유지하면서, <strong>같은 Bridge Network에 연결되고 Docker DNS가 이름을 상대 Container의 IP로 변환해주는 것</strong>이다.</p>
<p>결국 Container Network의 구조는 다음과 같이 정리할 수 있다.</p>
<pre><code class="language-text">Network Namespace
→ Container마다 독립적인 Network 공간을 만든다.

veth pair
→ Container Network와 Host Network를 연결한다.

Linux Bridge
→ 여러 Container의 Host 쪽 veth를 연결한다.

Port Publishing
→ Host로 들어온 요청을 특정 Container로 전달한다.

Docker DNS
→ 같은 User-defined Network의 Container를 이름으로 찾을 수 있게 한다.</code></pre>
<p>즉 Docker는 Container의 Network를 먼저 <strong>Namespace로 분리하고</strong>, 필요한 통신 경로만 <strong>veth와 Bridge를 통해 다시 연결하는 방식</strong>으로 Container Network를 구성한다.</p>
<hr />
<h2 id="container-process">Container Process</h2>
<p>지금까지 Process가 살아갈 환경을 만들었다.</p>
<p>RootFS가 준비됐고, Namespace로 환경을 격리했으며, Cgroup으로 Resource를 제한했고 Network까지 연결했다.</p>
<p>이제 그 안에서 실제 Application Process를 실행하면 된다.</p>
<h3 id="main-process와-pid-1">Main Process와 PID 1</h3>
<p>Container에는 생명주기의 기준이 되는 <strong>Main Process</strong>가 있다.</p>
<p>예를 들어 다음 Dockerfile을 실행했다고 하자.</p>
<pre><code class="language-dockerfile">CMD [&quot;python3&quot;, &quot;webserver.py&quot;]</code></pre>
<p>Container의 PID Namespace 안에서 이 Application은 PID 1이 될 수 있다.</p>
<pre><code class="language-text">Host
PID 4821  python
      │
      │ same process
      ▼
Container
PID 1     python</code></pre>
<p>Container의 실행 상태는 이 Main Process와 강하게 연결된다.</p>
<p>Main Process가 실행 중이면 Container는 Running 상태이고, Main Process가 종료되면 Container도 종료된다.</p>
<p>따라서 어떤 Process가 PID 1이 되는가는 꽤 중요하다.</p>
<h3 id="cmd와-process-구조">CMD와 Process 구조</h3>
<p>Exec Form을 사용하면 Application이 직접 PID 1이 된다.</p>
<pre><code class="language-dockerfile">CMD [&quot;python3&quot;, &quot;webserver.py&quot;]</code></pre>
<p>반면 Shell을 거쳐 실행하면 Shell이 PID 1이 되고 Application은 Child Process가 된다.</p>
<pre><code class="language-dockerfile">CMD [&quot;/bin/sh&quot;, &quot;-c&quot;, &quot;python3 webserver.py&quot;]</code></pre>
<p>Shell 기능이 필요하면서 Application을 PID 1로 만들고 싶다면 <code>exec</code>를 사용할 수 있다.</p>
<pre><code class="language-dockerfile">CMD [&quot;/bin/sh&quot;, &quot;-c&quot;, &quot;exec python3 webserver.py&quot;]</code></pre>
<p><code>exec</code>는 새로운 Child Process를 추가하는 것이 아니라 현재 Shell Process를 Application으로 치환한다.</p>
<p>이 차이가 중요한 이유는 종료 Signal 때문이다.</p>
<h3 id="signal과-graceful-shutdown">Signal과 Graceful Shutdown</h3>
<p><code>docker stop</code>을 실행하면 Docker는 먼저 Container의 Main Process에 종료 Signal을 전달한다.</p>
<pre><code class="language-text">docker stop
    │
    │ SIGTERM
    ▼
PID 1</code></pre>
<p>Application이 SIGTERM을 정상적으로 처리하면 새로운 요청을 중단하고, 처리 중인 작업과 Network/DB 연결을 정리한 뒤 종료할 수 있다.</p>
<p>이것이 <strong>Graceful Shutdown</strong>이다.</p>
<p>반대로 Shell이 PID 1이고 Application이 Child Process로 실행되고 있다면 Signal이 Application까지 기대한 방식으로 전달되지 않을 수 있다.</p>
<p>그래서 Container의 CMD는 단순히 어떤 명령을 실행할지를 넘어, <strong>어떤 Process가 Container의 생명주기를 대표할 것인가</strong>와 연결된다.</p>
<p><code>docker exec -it container /bin/bash</code> 역시 별도의 컴퓨터에 접속하는 것이 아니다.</p>
<p>기존 Container의 Namespace 안에서 새로운 Shell Process를 실행하고 현재 Terminal의 STDIN/STDOUT을 연결하는 동작이다.</p>
<hr />
<h2 id="container-runtime">Container Runtime</h2>
<p>여기까지 보면 Container 하나를 실행하려면 꽤 많은 준비가 필요하다.</p>
<p>Image Layer를 File System으로 구성하고, RootFS를 준비하고, Namespace와 Cgroup을 설정하고, Network를 연결하고, Security 정책을 적용한 뒤 Application Process를 실행해야 한다.</p>
<p>그런데 사용자가 직접 하는 일은 대부분 다음 한 줄이다.</p>
<pre><code class="language-bash">docker run nginx</code></pre>
<p>이 복잡한 작업을 Docker의 여러 Runtime 계층이 나누어 처리한다.</p>
<h3 id="docker-engine에서-runc까지">Docker Engine에서 runc까지</h3>
<p>Docker의 실행 구조를 단순화하면 다음과 같다.</p>
<pre><code class="language-text">Docker CLI
    │
    ▼
Docker Engine
    │
    ├─ Image / Network / Volume 관리
    │
    ▼
containerd
    │
    ▼
containerd-shim
    │
    ▼
runc
    │
    ▼
Linux Kernel
    │
    ▼
Application PID 1</code></pre>
<p>Docker Engine은 Docker CLI의 요청을 받아 Image, Container, Network, Volume 같은 Docker의 상위 기능을 관리한다.</p>
<p>그 아래의 <code>containerd</code>는 Image 준비, Layer Unpack, Snapshot, RootFS 준비, Container Lifecycle과 같은 <strong>High-Level Runtime 역할</strong>을 담당한다.</p>
<p>앞에서 살펴본 Image Layer와 OverlayFS도 이 실행 준비 과정과 연결된다.</p>
<p>containerd가 Image를 준비하고 Snapshot을 구성하면서 Container가 사용할 RootFS를 마련한다.</p>
<p>그 다음 <code>containerd-shim</code>이 Container Process와 Runtime 사이에 남아 Process의 PID, Exit Status, STDOUT/STDERR, I/O 같은 실행 상태를 관리한다.</p>
<p>마지막으로 <code>runc</code>가 실제 Linux Kernel과 가까운 곳에서 Container Process의 실행 환경을 구성한다.</p>
<pre><code class="language-text">runc
├─ Namespace
├─ Cgroup
├─ RootFS / Mount
├─ Security
└─ Process 실행</code></pre>
<p>앞에서 살펴본 Namespace, Cgroup, RootFS, Security 같은 Linux 실행 환경을 실제 Process에 적용하고 Application을 실행하는 것이 <code>runc</code>의 핵심 역할이다.</p>
<p>여기서 Network는 조금 구분해서 볼 필요가 있다.</p>
<p><code>runc</code>는 Container가 사용할 <strong>Network Namespace라는 격리 기반</strong>을 구성할 수 있지만, Docker에서 사용하는 veth, Linux Bridge, IPAM, Port Publishing 같은 Network 구성 전체를 runc가 혼자 담당하는 것은 아니다.</p>
<p>이런 Docker Network 구성은 Docker의 Network 관리 계층이 Container 생성 과정과 함께 구성한다.</p>
<p>즉 Container를 실행한다는 것은 하나의 프로그램이 모든 작업을 처리하는 것이 아니라,</p>
<pre><code class="language-text">Docker Engine
→ Docker 기능과 전체 실행 요청 관리

containerd
→ Container 실행 준비와 Lifecycle 관리

containerd-shim
→ 실행 중인 Container Process 관리

runc
→ Linux Kernel 기능을 이용해 실제 Process 실행</code></pre>
<p>처럼 여러 계층이 역할을 나누는 과정에 가깝다.</p>
<hr />
<h3 id="oci">OCI</h3>
<p>Docker만 Container를 실행하는 것은 아니다.</p>
<p>containerd, CRI-O, Podman 등 다양한 Container 도구가 같은 Image와 Runtime 생태계를 사용할 수 있는 이유는 <strong>OCI(Open Container Initiative)</strong>라는 표준이 있기 때문이다.</p>
<p>OCI는 크게 세 가지 영역을 정의한다.</p>
<ul>
<li><strong>OCI Image Spec</strong>: Container Image의 Layer와 Metadata 형식</li>
<li><strong>OCI Runtime Spec</strong>: Container를 어떤 설정으로 실행할지에 대한 규칙</li>
<li><strong>OCI Distribution Spec</strong>: Registry에서 Image를 Push/Pull하는 방식</li>
</ul>
<p>특히 Runtime 관점에서는 <code>rootfs</code>와 <code>config.json</code>으로 구성된 OCI Bundle이 중요하다.</p>
<pre><code class="language-text">bundle/
├─ config.json
└─ rootfs/</code></pre>
<p><code>rootfs</code>는 Process가 사용할 File System이고, <code>config.json</code>에는 Process, Environment, Namespace, Mount, Resource 같은 실행 설정이 들어간다.</p>
<p>이를 OCI Runtime인 runc에 전달하면 Linux Kernel 기능을 이용해 Container Process를 실행할 수 있다.</p>
<pre><code class="language-text">rootfs
+
config.json
+
runc
    ↓
Container Process</code></pre>
<p>그래서 Docker Engine 없이도 OCI Bundle과 runc를 직접 준비하면 Container를 실행할 수 있다.</p>
<p>이 구조가 보여주는 것은 명확하다.</p>
<blockquote>
<p><strong>Docker가 곧 Container는 아니다.</strong></p>
</blockquote>
<p>Docker는 Container를 Build하고 실행하고 관리하기 쉽게 만들어주는 Platform이고, 더 아래에는 OCI Runtime과 Linux Kernel의 Container 기능이 존재한다.</p>
<hr />
<h2 id="docker-run의-전체-흐름">docker run의 전체 흐름</h2>
<p>이제 처음의 한 줄로 돌아가보자.</p>
<pre><code class="language-bash">docker run my-app</code></pre>
<p>그 뒤에서 일어나는 일을 지금까지의 내용으로 연결하면 다음과 같다.</p>
<pre><code class="language-text">docker run
    │
    ▼
Docker Engine
    │
    ├─ Network 구성
    │   ├─ IP 할당
    │   ├─ veth
    │   ├─ Bridge 연결
    │   └─ Port Publishing
    │
    ▼
containerd
    │
    ├─ Image 준비
    ├─ Layer / Snapshot
    └─ RootFS 준비
    │
    ▼
containerd-shim
    │
    ▼
runc
    │
    ├─ Namespace
    ├─ Cgroup
    ├─ RootFS / Mount
    └─ Security
    │
    ▼
Application Process
PID 1</code></pre>
<p>File System 관점에서는 Image의 Read-Only Layer 위에 Writable Layer를 더하고 OverlayFS로 하나의 RootFS를 만든다.</p>
<p>Process 관점에서는 Namespace로 보이는 환경을 나누고, Cgroup으로 Resource 사용량을 제한하며, 필요한 Security 설정을 적용한다.</p>
<p>Network 관점에서는 독립된 Network Namespace를 만들고 veth와 Bridge를 이용해 Host 및 다른 Container와 통신할 수 있는 경로를 구성한다.</p>
<p>그리고 마지막에 Application Process가 실행된다.</p>
<p>결국 <code>docker run</code>은 단순히</p>
<blockquote>
<p>Image를 실행한다.</p>
</blockquote>
<p>라고 보기보다,</p>
<blockquote>
<p><strong>Image를 Process가 사용할 File System으로 구성하고, Linux Kernel의 격리와 Resource 제어 기능을 적용하고, 필요한 Network를 연결한 뒤 그 환경에서 Application Process를 실행하는 과정</strong></p>
</blockquote>
<p>이라고 이해하는 편이 더 정확하다.</p>
<hr />
<h2 id="마치며">마치며</h2>
<p>처음 Container를 보면 작은 Server가 여러 개 떠 있는 것처럼 보인다.</p>
<p>하지만 내부까지 내려가보면 Container마다 Kernel이 하나씩 존재하는 것이 아니다.</p>
<pre><code class="language-text">                    Linux Kernel
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       Process         Process         Process
          │              │              │
       RootFS          RootFS          RootFS
       Namespace       Namespace       Namespace
       Cgroup          Cgroup          Cgroup
       Network         Network         Network</code></pre>
<p>하나의 Linux Kernel이 각각의 Process에게 서로 다른 File System과 Process View, Network, Resource 경계를 제공한다.</p>
<p>그래서 Container를 한 문장으로 표현하면 다음과 같이 정리할 수 있다.</p>
<blockquote>
<p><strong>Container는 작은 컴퓨터라기보다, Linux Process에게 독립된 컴퓨터를 사용하는 것처럼 보이는 실행 환경을 만들어준 것이다.</strong></p>
</blockquote>
<p>앞선 글에서는</p>
<pre><code class="language-text">Dockerfile
    ↓
Image
    ↓
Container</code></pre>
<p>라는 Docker의 바깥 흐름을 살펴봤다.</p>
<p>이번에는 마지막에 있던 Container라는 상자를 열어봤다.</p>
<p>그리고 처음 던졌던 질문으로 돌아가면, Container가 Linux Kernel 위에서 동작하는 이유도 자연스럽게 보인다.</p>
<p>Container를 구성하는 핵심 기능인 Namespace, Cgroup, Mount, Network, Capability, seccomp 등이 결국 <strong>Linux Kernel이 제공하는 기능</strong>이기 때문이다.</p>
<p>Docker는 완전히 새로운 가상 컴퓨터를 만드는 것이 아니라, 이러한 Linux 기능들을 조합해 평범한 Process를 독립된 실행 환경 안에서 동작하도록 만든다.</p>
<p>이 구조를 이해하면 이후 Kubernetes에서 등장하는 개념들도 조금 덜 낯설어진다.</p>
<p>Pod의 Network 역시 Network Namespace와 veth 같은 Linux Network 개념 위에서 만들어지고, <code>securityContext</code> 역시 Linux User와 Capability 같은 기능으로 내려간다.</p>
<p>Kubernetes가 Container를 실행할 때도 결국 Runtime을 통해 Linux Process를 만든다.</p>
<p>Docker에서 배웠던 원리가 사라지고 완전히 새로운 기술이 등장하는 것이 아니다.</p>
<p><strong>하나의 Host에서 이해했던 Container 구조가 더 많은 Container와 더 많은 Node를 다루도록 확장되는 것이다.</strong></p>
<p>이제 Container 하나가 어떻게 만들어지고 실행되는지는 꽤 깊게 살펴봤다.</p>
<p>다음 문제는 현실의 Application이 Container 하나로 끝나지 않는다는 것이다.</p>
<p>Frontend, Backend, Database처럼 여러 Container가 함께 움직이기 시작하면 관심사는</p>
<blockquote>
<p>Container 하나를 어떻게 실행할 것인가?</p>
</blockquote>
<p>에서</p>
<blockquote>
<p><strong>여러 Container를 어떻게 하나의 Application처럼 구성하고 운영할 것인가?</strong></p>
</blockquote>
<p>로 넘어간다.</p>
<p>그때부터 Docker Compose와 Container Orchestration 이야기가 시작된다.</p>