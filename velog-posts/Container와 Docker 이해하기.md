<p>앞서 클라우드 네이티브에 대해 다루며, <strong>Container와 Container Orchestration</strong>에 대해서 간단하게 알아본 바 있다.</p>
<p>당시에는</p>
<blockquote>
<p>Container는 VM보다 가볍고, 애플리케이션을 빠르고 일관된 환경에서 실행할 수 있게 해준다.</p>
</blockquote>
<p>정도로 큰 그림을 살펴봤다.</p>
<p>이번에는 여기서 조금 더 들어가,</p>
<blockquote>
<p><strong>Container는 왜 가벼운지, Docker Image와 Container는 실제로 어떤 관계인지, Dockerfile은 왜 필요한지</strong></p>
</blockquote>
<p>를 중심으로 알아보자.</p>
<hr />
<h1 id="컨테이너-기술-및-도구-이해">컨테이너 기술 및 도구 이해</h1>
<h2 id="container">Container</h2>
<h3 id="정의">정의</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3872cfcd-699e-48cc-adf8-6ce9267db46c/image.png" /></p>
<p>Container는 애플리케이션과 실행에 필요한 환경을 <strong>격리된 하나의 실행 단위</strong>로 구성하는 기술이다.</p>
<p>그런데 단순히</p>
<blockquote>
<p>&quot;VM보다 가벼운 실행 환경&quot;</p>
</blockquote>
<p>정도로만 이해하면 Container의 특징이 왜 만들어지는지 잘 와닿지 않는다.</p>
<p>이를 이해하기 위해서는 VM과 Container가 <strong>각각 무엇을 해결하려 했는지</strong>부터 볼 필요가 있다.</p>
<hr />
<h3 id="vm은-무엇을-해결했고-container는-무엇을-해결했을까">VM은 무엇을 해결했고, Container는 무엇을 해결했을까?</h3>
<h4 id="hypervisor-vs-container">Hypervisor vs Container</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/003ed118-ebe1-4dee-842b-efd0586d8aa2/image.png" /></p>
<p>Hypervisor 기반 VM은 하나의 물리 서버를 여러 개의 가상 서버처럼 사용할 수 있도록 만든다.</p>
<pre><code class="language-text">Physical Server
      ↓
Hypervisor
      ↓
 ┌────┼────┐
VM 1  VM 2  VM 3</code></pre>
<p>즉,</p>
<blockquote>
<p><strong>VM은 물리적인 Infrastructure 자원을 효율적으로 나누어 사용하는 문제를 해결했다.</strong></p>
</blockquote>
<p>하지만 각각의 VM은 자신만의 Guest OS와 Kernel을 가지기 때문에,</p>
<pre><code class="language-text">VM 1
Application
Runtime
Guest OS
Guest Kernel

VM 2
Application
Runtime
Guest OS
Guest Kernel</code></pre>
<p>처럼 각각 하나의 독립된 컴퓨터를 실행하는 것에 가깝다.</p>
<p>Application 관점에서는 VM을 하나 만들 때마다 여전히</p>
<pre><code class="language-text">OS 환경 준비
    ↓
Runtime 설치
    ↓
Library 설치
    ↓
환경 설정
    ↓
Application 배포</code></pre>
<p>와 같은 과정이 필요하다.</p>
<p>Container는 여기에서 접근 방법을 바꾼다.</p>
<hr />
<h3 id="container는-linux-kernel을-공유한다">Container는 Linux Kernel을 공유한다</h3>
<p>Container는 VM처럼 실행 단위마다 자신의 Kernel을 하나씩 가지지 않는다.</p>
<p>대신 여러 Container가 <strong>Host의 Linux Kernel을 공유한다.</strong></p>
<pre><code class="language-text">Container A      Container B      Container C
───────────      ───────────      ───────────
Application      Application      Application
Runtime / Lib    Runtime / Lib    Runtime / Lib
────────────────────────────────────────────
                Linux Kernel
────────────────────────────────────────────
                    Host</code></pre>
<p>Container Image에는</p>
<ul>
<li>Application</li>
<li>Runtime</li>
<li>Library</li>
<li>Binary</li>
<li>각종 User Space File</li>
</ul>
<p>등이 들어가지만, VM처럼 별도의 Guest Kernel을 하나씩 실행하지 않는다.</p>
<p>이 때문에 Container를 실행하는 것은</p>
<blockquote>
<p>새로운 컴퓨터 하나를 Boot하는 것</p>
</blockquote>
<p>보다</p>
<blockquote>
<p><strong>이미 실행 중인 Linux Kernel 위에 격리된 Application Process를 하나 더 실행하는 것</strong></p>
</blockquote>
<p>에 가깝다.</p>
<p>그래서 일반적으로 VM에 비해</p>
<ul>
<li>실행이 빠르고</li>
<li>필요한 용량이 작으며</li>
<li>하나의 Host에서 더 많은 실행 단위를 운영할 수 있다.</li>
</ul>
<blockquote>
<p>즉 Container가 가벼운 핵심적인 이유는 단순히 파일 몇 개가 적어서가 아니라,
<strong>각 Container마다 OS Kernel을 별도로 Boot하지 않고 Host Kernel을 공유하기 때문이다.</strong></p>
</blockquote>
<hr />
<h3 id="mac-에서-docker의-동작방식">mac 에서 Docker의 동작방식</h3>
<p>여기서 한 가지 의문이 생긴다.</p>
<p>Linux Container가 Linux Kernel을 공유한다면,</p>
<pre><code class="language-bash">docker run ubuntu</code></pre>
<p>를 macOS에서는 어떻게 실행할 수 있을까?</p>
<p>macOS는 Linux Kernel이 아니라 <strong>XNU Kernel</strong>을 사용한다.</p>
<p>따라서 Linux Container가 macOS Kernel 위에서 직접 실행되는 것은 아니다.</p>
<p>Docker Desktop이 내부적으로 Linux 환경을 제공한다.</p>
<pre><code class="language-text">macOS
XNU Kernel
    │
    ▼
Docker Desktop
    │
    ▼
Linux VM
Linux Kernel
    │
    ├── Container A
    ├── Container B
    └── Container C</code></pre>
<p>여기서 중요한 것은</p>
<blockquote>
<p><strong>Container가 반드시 VM을 요구하는 것이 아니다.</strong></p>
</blockquote>
<p>Linux Container가 필요로 하는 것은 <strong>Linux Kernel</strong>이다.</p>
<p>Linux Server에서는 Host Kernel을 그대로 사용할 수 있고,</p>
<p>macOS처럼 Linux Kernel이 없는 환경에서는 Docker Desktop이 Linux VM을 이용해 필요한 Kernel 환경을 만들어주는 것이다.</p>
<p>따라서 VM과 Container는 반드시 경쟁 기술이라고 볼 필요도 없다.</p>
<pre><code class="language-text">VM
→ Infrastructure를 가상화

Container
→ Application 실행 환경을 격리</code></pre>
<p>서로 다른 계층의 문제를 해결한다고 보는 것이 더 정확하다.</p>
<hr />
<h3 id="특징">특징</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/965af892-b1e5-4870-adfb-2eba833cda82/image.png" /></p>
<p>이러한 구조를 바탕으로 Container는 다음과 같은 특징을 가진다.</p>
<ul>
<li>Application과 실행 환경을 하나의 Image로 만들 수 있다.</li>
<li>Image를 이용해 개발/테스트/운영 환경의 일관성을 높일 수 있다.</li>
<li>VM에 비해 가볍고 빠르게 생성·종료할 수 있다.</li>
<li>각각의 Application을 서로 격리된 실행 단위로 관리할 수 있다.</li>
<li>Image 단위로 빌드하고 배포할 수 있어 CI/CD와 잘 결합된다.</li>
<li>실행 단위를 빠르게 추가하거나 제거할 수 있어 Cloud 환경의 확장 방식과 잘 어울린다.</li>
</ul>
<hr />
<h2 id="container-engine--container-runtime">Container Engine &amp; Container Runtime</h2>
<p>앞에서 Container는</p>
<blockquote>
<p>Host Kernel을 공유하면서 격리된 Process를 실행한다.</p>
</blockquote>
<p>고 했다.</p>
<p>그렇다면 실제로</p>
<pre><code class="language-text">Image를 가져오고
↓
격리 환경을 만들고
↓
Process를 실행하는 작업</code></pre>
<p>은 누가 수행할까?</p>
<p>여기에서 <strong>Container Engine과 Container Runtime</strong>이 등장한다.</p>
<hr />
<h3 id="container-engine">Container Engine</h3>
<p>Container Engine은 사용자가 Container를 편하게 다룰 수 있도록 API나 CLI 등을 제공하는 관리 계층이다.</p>
<p>예를 들어 사용자가</p>
<pre><code class="language-bash">docker run nginx</code></pre>
<p>를 실행하면 Container Engine은</p>
<pre><code class="language-text">Image 존재 여부 확인
        ↓
필요하면 Registry에서 Pull
        ↓
Container 실행 설정 구성
        ↓
Runtime에 실행 요청</code></pre>
<p>과 같은 작업을 처리한다.</p>
<p>Docker Engine이나 Podman 등이 이런 Container 관리 도구에 해당한다.</p>
<blockquote>
<p><strong>Container Engine은 사용자의 요청을 받아 Image, Container, Network, Volume 등의 자원을 관리하고 실제 Container 실행을 Runtime에 요청하는 계층</strong>이라고 이해할 수 있다.</p>
</blockquote>
<hr />
<h3 id="container-runtime">Container Runtime</h3>
<p>Container Runtime은 실제 Container 실행에 더 가까운 역할을 담당한다.</p>
<p>Engine으로부터</p>
<ul>
<li>Root File System</li>
<li>실행할 Process</li>
<li>Container 설정</li>
</ul>
<p>등을 전달받고, Linux Kernel 기능을 이용해 격리 환경을 구성한 뒤 Process를 실행한다.</p>
<pre><code class="language-text">사용자
  │
  ▼
Docker CLI
  │
  ▼
Docker Engine
  │
  ▼
Container Runtime
  │
  ▼
Linux Kernel
  │
  ▼
Application Process</code></pre>
<p>대표적으로 OCI 표준을 구현하는 <code>runc</code>가 실제 Container Process 생성에 사용되며, <code>containerd</code>와 같은 상위 Runtime이 Container Lifecycle을 관리한다.</p>
<p>결국 Container Runtime의 가장 중요한 역할을 단순화하면</p>
<blockquote>
<p><strong>Image를 기반으로 격리된 실행 환경을 만들고 그 안에서 Process를 시작하는 것</strong></p>
</blockquote>
<p>이라고 할 수 있다.</p>
<hr />
<h4 id="결국-container는-process를-실행한다">결국 Container는 Process를 실행한다</h4>
<p>이 관점을 잡으면 Docker 명령도 조금 다르게 보인다.</p>
<pre><code class="language-bash">docker run -it ubuntu /bin/bash</code></pre>
<p>를 실행했다고 하자.</p>
<p>이것은</p>
<blockquote>
<p>Ubuntu 컴퓨터 한 대를 켰다.</p>
</blockquote>
<p>보다는,</p>
<pre><code class="language-text">Ubuntu Image 준비
      ↓
격리된 Container 환경 구성
      ↓
/bin/bash Process 실행</code></pre>
<p>에 가깝다.</p>
<p>Container의 중심이 되는 Process가 종료되면 Container 역시 더 이상 실행 상태를 유지하지 않는다.</p>
<p>그래서 <code>/bin/bash</code>를 Main Process로 실행한 Container에서</p>
<pre><code class="language-bash">exit</code></pre>
<p>를 입력하면 Bash가 종료되고 Container도 <code>Exited</code> 상태가 된다.</p>
<p>이러한 <strong>Process 관점</strong>은 이후 <code>docker run</code>, <code>docker exec</code>, <code>CMD</code>, <code>ENTRYPOINT</code>를 이해할 때 중요하다.</p>
<hr />
<h2 id="docker">Docker</h2>
<p>앞서 Container 자체의 동작 구조를 알아봤다면, 이제 대표적인 Container Platform인 <strong>Docker</strong>를 살펴보자.</p>
<h3 id="정의-1">정의</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c61088bc-bd4a-47eb-9578-c87ba20444f6/image.png" /></p>
<p>Docker는 Application과 실행 환경을 <strong>Image로 만들고</strong>, 이를 이용하여 Container를 생성하고 실행할 수 있도록 도와주는 Container Platform이다.</p>
<p>Docker의 전체 흐름은 크게 다음과 같다.</p>
<pre><code class="language-text">Dockerfile
    │
    │ build
    ▼
Docker Image
    │
    │ run
    ▼
Docker Container</code></pre>
<p>그런데 이 세 가지를 단순히 정의로만 외우기보다 실제 관계를 이해하는 것이 중요하다.</p>
<hr />
<h3 id="docker-image">Docker Image</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6844204e-b8ac-40e1-9cc1-2651d486f372/image.png" /></p>
<p>Docker Image는 Container 실행에 필요한 File과 설정을 담아둔 <strong>재사용 가능한 실행 환경</strong>이다.</p>
<p>예를 들어</p>
<pre><code class="language-bash">docker pull nginx</code></pre>
<p>를 실행했다고 해서 Nginx가 실행된 것은 아니다.</p>
<p>단지</p>
<blockquote>
<p>Nginx Container를 만들 수 있는 Image를 가져온 것</p>
</blockquote>
<p>이다.</p>
<hr />
<h3 id="docker-container">Docker Container</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/cbc9d5e8-deb6-48fe-8c91-bbf670efac19/image.png" /></p>
<p>Image를</p>
<pre><code class="language-bash">docker run nginx</code></pre>
<p>과 같이 실행하면 실제 Container가 만들어진다.</p>
<pre><code class="language-text">Image
  │
  │ docker run
  ▼
Container</code></pre>
<p>하나의 Image에서는 여러 개의 Container를 만들 수도 있다.</p>
<pre><code class="language-text">               ┌─ Container A
Docker Image ──┼─ Container B
               └─ Container C</code></pre>
<p>그런데 여기서 중요한 질문이 하나 생긴다.</p>
<blockquote>
<p><strong>하나의 Image를 여러 Container가 함께 사용한다면 각각의 Container에서 파일을 수정할 수 있는 이유는 무엇일까?</strong></p>
</blockquote>
<p>이를 이해하려면 Docker Image의 <strong>Layer 구조</strong>를 알아야 한다.</p>
<hr />
<h3 id="image의-layer-구성">Image의 Layer 구성</h3>
<p>Docker Image는 하나의 거대한 덩어리라기보다 여러 개의 <strong>Read Only Layer</strong>가 쌓여 만들어진 구조에 가깝다.</p>
<pre><code class="language-text">Docker Image

┌─────────────────┐
│ Application     │
├─────────────────┤
│ Runtime / Lib   │
├─────────────────┤
│ Base Image      │
└─────────────────┘

      Read Only</code></pre>
<p>예를 들어</p>
<pre><code class="language-dockerfile">FROM ubuntu:22.04

RUN apt-get install -y nginx

COPY index.html /var/www/html/</code></pre>
<p>처럼 Image를 만들었다면,</p>
<p>개념적으로</p>
<pre><code class="language-text">┌────────────────────┐
│ index.html         │ ← COPY
├────────────────────┤
│ nginx 관련 변경      │ ← RUN
├────────────────────┤
│ Ubuntu Base Layer  │ ← FROM
└────────────────────┘</code></pre>
<p>와 같이 변경 내용이 Layer 형태로 쌓인다.</p>
<p>Layer를 사용하는 중요한 이유 중 하나는 <strong>재사용</strong>이다.</p>
<pre><code class="language-text">Image A             Image B

Layer C             Layer D
Layer B ─────────── Layer B
Layer A ─────────── Layer A</code></pre>
<p>동일한 Layer가 이미 존재한다면 다른 Image도 이를 재사용할 수 있다.</p>
<p>이 때문에 Image를 Pull할 때 이미 가지고 있는 Layer를 다시 받을 필요가 없고, Build 과정에서도 이전 Layer Cache를 활용할 수 있다.</p>
<hr />
<h4 id="container의-수정-방법">Container의 수정 방법</h4>
<p>Image 자체의 Layer는 기본적으로 Read Only다.</p>
<p>하지만 Image로 Container를 만들면 가장 위에 <strong>Container만의 Writable Layer</strong>가 추가된다.</p>
<pre><code class="language-text">Container

┌─────────────────────┐
│ Writable Layer      │ ← Container 변경사항
├─────────────────────┤
│ Application Layer   │
├─────────────────────┤
│ Library Layer       │
├─────────────────────┤
│ Base Image Layer    │
└─────────────────────┘
        Read Only</code></pre>
<p>그래서 Container 안에서</p>
<pre><code class="language-bash">touch test.txt</code></pre>
<p>를 하거나 파일을 수정할 수 있다.</p>
<p>원본 Image를 수정하는 것이 아니라,</p>
<blockquote>
<p><strong>해당 Container의 Writable Layer에 변경 내용을 기록하는 것</strong></p>
</blockquote>
<p>이다.</p>
<p>따라서 같은 Image를 이용해 Container 두 개를 만들더라도</p>
<pre><code class="language-text">Docker Image
   │
   ├─ Container A
   │     └─ Writable Layer A
   │
   └─ Container B
         └─ Writable Layer B</code></pre>
<p>각 Container의 변경 사항은 서로 독립적이다.</p>
<p>이 구조가</p>
<blockquote>
<p><strong>Image는 실행 환경의 원본이고, Container는 그 위에 자신만의 변경 영역을 가진 실행 Instance다.</strong></p>
</blockquote>
<p>라는 관계를 만들어준다.</p>
<hr />
<h2 id="dockerfile">Dockerfile</h2>
<h3 id="dockerfile-없이도-환경은-만들-수-있다">Dockerfile 없이도 환경은 만들 수 있다</h3>
<p>사실 Dockerfile이 없어도 Container 환경을 만들 수 있다.</p>
<p>예를 들어 Ubuntu Container를 실행한다.</p>
<pre><code class="language-bash">docker run -it ubuntu:22.04 /bin/bash</code></pre>
<p>그 안에서 직접</p>
<pre><code class="language-bash">apt-get update
apt-get install -y python3</code></pre>
<p>를 실행하고 Application File을 넣은 뒤</p>
<pre><code class="language-bash">python3 webserver.py</code></pre>
<p>를 실행하면 된다.</p>
<pre><code class="language-text">Ubuntu
  +
Python
  +
Application</code></pre>
<p>환경이 이미 만들어졌다.</p>
<p>즉,</p>
<blockquote>
<p><strong>Dockerfile이 없어서 Container를 구성하지 못하는 것은 아니다.</strong></p>
</blockquote>
<p>문제는 이 과정을 사람이 직접 했다는 것이다.</p>
<p>새로운 Container에서도 같은 환경이 필요하다면 다시</p>
<pre><code class="language-text">Container 실행
    ↓
Package 설치
    ↓
Runtime 설치
    ↓
File 복사
    ↓
환경 설정
    ↓
Application 실행</code></pre>
<p>을 반복해야 한다.</p>
<p>다른 개발자가 같은 환경을 만들 때도 동일한 작업을 정확하게 수행해야 한다.</p>
<p>Dockerfile은 바로 이 문제를 해결한다.</p>
<hr />
<h3 id="dockerfile-1">Dockerfile</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4c3abcdb-dc05-45ac-b349-7ae5507c8f43/image.png" /></p>
<p>Dockerfile은 <strong>사람이 Container 안에서 직접 구성하던 Application 실행 환경을 코드로 선언하는 파일</strong>이다.</p>
<p>앞에서 수동으로 했던 작업을</p>
<pre><code class="language-dockerfile">FROM ubuntu:22.04

RUN apt-get update &amp;&amp; \
    apt-get install -y python3

WORKDIR /app

COPY webserver.py .

CMD [&quot;python3&quot;, &quot;webserver.py&quot;]</code></pre>
<p>처럼 표현할 수 있다.</p>
<p>이후</p>
<pre><code class="language-bash">docker build -t webserver:1.0 .</code></pre>
<p>으로 Image를 만들면,</p>
<pre><code class="language-bash">docker run webserver:1.0</code></pre>
<p>만으로 동일한 실행 환경을 반복해서 만들 수 있다.</p>
<blockquote>
<p><strong>Dockerfile의 핵심은 단순히 Image를 만드는 것이 아니라, 사람이 수동으로 구성하던 Application 실행 환경을 재현 가능한 코드로 바꾸는 것에 있다.</strong></p>
</blockquote>
<hr />
<h3 id="주요-dockerfile-명령">주요 Dockerfile 명령</h3>
<p>기존에 살펴본 주요 명령은 다음과 같다.</p>
<ul>
<li><code>FROM</code> : Image의 기반이 되는 Base Image 지정</li>
<li><code>WORKDIR</code> : 이후 명령을 수행할 작업 Directory 설정</li>
<li><code>COPY</code> : Build Context의 File을 Image로 복사</li>
<li><code>RUN</code> : Image Build 과정에서 명령 실행</li>
<li><code>ARG</code> : Build 시점에 사용할 변수</li>
<li><code>ENV</code> : Image/Container에서 사용할 환경 변수</li>
<li><code>EXPOSE</code> : Container가 사용할 Port에 대한 정보를 Image에 기록</li>
<li><code>CMD</code> : Container 실행 시 사용할 기본 명령 또는 인자</li>
<li><code>ENTRYPOINT</code> : Container가 기본적으로 실행할 프로그램 지정</li>
</ul>
<p>여기서 중요한 점이 하나 있다.</p>
<p><strong>모든 Dockerfile 명령이 동일한 종류의 Layer를 만드는 것은 아니다.</strong></p>
<pre><code class="language-text">File System을 변경
→ RUN
→ COPY
→ ADD</code></pre>
<p>와</p>
<pre><code class="language-text">실행 설정을 기록
→ CMD
→ ENTRYPOINT
→ ENV
→ EXPOSE
→ USER
...</code></pre>
<p>는 역할이 다르다.</p>
<p>즉 Dockerfile은 단순한 Shell Script라기보다,</p>
<blockquote>
<p><strong>Image의 File System과 Container 실행 설정을 함께 정의하는 명세서</strong></p>
</blockquote>
<p>에 가깝다.</p>
<hr />
<h3 id="layer와-stage">Layer와 Stage</h3>
<p>Dockerfile을 배우면서 헷갈리기 쉬운 개념이 <strong>Layer와 Stage</strong>다.</p>
<p>둘은 전혀 같은 개념이 아니다.</p>
<h4 id="layer">Layer</h4>
<p>Layer는 앞에서 살펴본 것처럼</p>
<blockquote>
<p><strong>Image File System의 변경 단위</strong> (RUN, COPY, ADD 로 쌓인다)</p>
</blockquote>
<p>다.</p>
<hr />
<h4 id="stage">Stage</h4>
<p>Stage는 Dockerfile에서 <strong><code>FROM</code>을 기준으로 시작되는 하나의 Build 환경</strong>이다.</p>
<p>예를 들어,</p>
<pre><code class="language-dockerfile">FROM node:22-alpine AS builder

COPY package.json .
RUN npm install

COPY . .
RUN npm run build


FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html</code></pre>
<p>가 있다고 하자.</p>
<p>구조는 다음과 같다.</p>
<pre><code class="language-text">Stage 1 : Builder

Node Base
├─ COPY Layer
├─ npm install Layer
├─ Source Layer
└─ Build Layer
       │
       │ dist만 전달
       ▼

Stage 2 : Runtime

Nginx Base
└─ dist Layer</code></pre>
<p>즉,</p>
<pre><code class="language-text">Stage
└─ Layer
└─ Layer
└─ Layer</code></pre>
<p>처럼 <strong>하나의 Stage 안에 여러 Layer가 존재할 수 있다.</strong></p>
<hr />
<h3 id="multi-stage-build">Multi-Stage Build</h3>
<p>위처럼 여러 Stage를 사용하는 방식을 <strong>Multi-Stage Build</strong>라고 한다.</p>
<p>Vue Application을 Build할 때는</p>
<pre><code class="language-text">Node.js
npm
Source
node_modules</code></pre>
<p>가 필요하지만,</p>
<p>Build가 끝난 운영 환경에서는 실제로</p>
<pre><code class="language-text">dist/</code></pre>
<p>안의 HTML, CSS, JavaScript만 있으면 된다.</p>
<p>따라서</p>
<pre><code class="language-text">Stage 1

Build를 위해 필요한 모든 환경
        │
        │ build
        ▼
      dist
        │
        │ 필요한 결과물만 전달
        ▼

Stage 2

Nginx
+
dist</code></pre>
<p>형태로 분리할 수 있다.</p>
<blockquote>
<p><strong>Multi-Stage의 핵심은 Stage를 여러 개 사용하는 것 자체가 아니라, Build에만 필요한 환경과 실제 Runtime 환경을 분리하여 최종 Image에는 필요한 결과물만 남기는 것이다.</strong></p>
</blockquote>
<p>이를 통해</p>
<ul>
<li>최종 Image 크기를 줄이고</li>
<li>불필요한 Build Tool을 제거하며</li>
<li>Runtime Image의 구성을 단순하게 만들 수 있다.</li>
</ul>
<hr />
<h2 id="container의-실행">Container의 실행</h2>
<p>앞에서 Container는 결국 <strong>Process를 실행하는 환경</strong>이라고 했다.</p>
<p>이 관점으로 Docker CLI의 몇 가지 명령을 보면 훨씬 이해하기 쉽다.</p>
<hr />
<h3 id="docker-run">docker run</h3>
<pre><code class="language-bash">docker run -it ubuntu /bin/bash</code></pre>
<p>은</p>
<pre><code class="language-text">Ubuntu Image
     ↓
Container 생성
     ↓
/bin/bash Process 실행</code></pre>
<p>을 의미한다.</p>
<p><code>run</code>은 기존 Container를 단순히 켜는 것이 아니라,</p>
<blockquote>
<p><strong>Image를 기반으로 새로운 Container를 생성하고 Main Process를 실행한다.</strong></p>
</blockquote>
<hr />
<h4 id="-it"><code>-it</code></h4>
<p>여기서</p>
<pre><code class="language-text">-i
→ STDIN을 열린 상태로 유지한다.

-t
→ Pseudo-TTY를 할당한다.

/bin/bash
→ 실제로 실행하는 Process다.</code></pre>
<p>이다.</p>
<p>그래서</p>
<pre><code class="language-bash">docker run -it ubuntu /bin/bash</code></pre>
<p>를 실행하면</p>
<blockquote>
<p>내 Terminal의 입력과 Container 안에서 실행되는 Bash Process를 연결하여 대화형으로 사용할 수 있다.</p>
</blockquote>
<p>중요한 점은</p>
<blockquote>
<p><strong><code>-it</code>가 Bash를 실행시키는 것이 아니다.</strong></p>
</blockquote>
<p>Bash를 실행하는 것은 <code>/bin/bash</code>이고,</p>
<p><code>-it</code>는 그 Process와 상호작용할 수 있는 Terminal 환경을 제공하는 옵션이다.</p>
<hr />
<h3 id="docker-exec">docker exec</h3>
<p>이미 Nginx Container가 실행 중이라고 하자.</p>
<pre><code class="language-text">Container
└─ nginx</code></pre>
<p>여기에</p>
<pre><code class="language-bash">docker exec -it nginx-container /bin/bash</code></pre>
<p>를 실행한다.</p>
<p>이것은 기존 Nginx Process에 접속하는 것이 아니다.</p>
<p>같은 Container 안에서 <strong>새로운 <code>/bin/bash</code> Process를 하나 더 실행하는 것</strong>이다.</p>
<pre><code class="language-text">Container

PID 1  nginx

PID N  /bin/bash
           ↑
        내 Terminal</code></pre>
<p>그래서 Bash에서 <code>exit</code> 하더라도 Nginx Process가 살아 있다면 Container는 계속 실행된다.</p>
<pre><code class="language-text">docker run
→ Container 생성 + Main Process 실행

docker exec
→ 실행 중인 Container 안에서 추가 Process 실행</code></pre>
<p>으로 구분하면 된다.</p>
<hr />
<h3 id="cmd와-entrypoint">CMD와 ENTRYPOINT</h3>
<p>Container가 실행될 때 어떤 Process를 시작할 것인지 Docker Image에 기본값을 지정할 수 있다.</p>
<p>대표적인 것이 <code>CMD</code>와 <code>ENTRYPOINT</code>다.</p>
<p>예를 들어,</p>
<pre><code class="language-dockerfile">ENTRYPOINT [&quot;ping&quot;]
CMD [&quot;-c&quot;, &quot;3&quot;, &quot;localhost&quot;]</code></pre>
<p>라고 작성했다고 하자.</p>
<p>기본 실행은</p>
<pre><code class="language-text">ENTRYPOINT        CMD
    ↓              ↓

   ping + -c 3 localhost</code></pre>
<p>즉,</p>
<pre><code class="language-bash">ping -c 3 localhost</code></pre>
<p>가 된다.</p>
<p>그런데 사용자가</p>
<pre><code class="language-bash">docker run image google.com</code></pre>
<p>이라고 실행하면 CMD의 기본값 대신 사용자가 넘긴 값이 사용된다.</p>
<pre><code class="language-text">ENTRYPOINT       사용자 입력
    ↓                ↓

   ping      +   google.com</code></pre>
<p>결과적으로</p>
<pre><code class="language-bash">ping google.com</code></pre>
<p>이 실행된다.</p>
<p>간단하게 구분하면</p>
<pre><code class="language-text">ENTRYPOINT
→ 이 Container가 기본적으로 실행할 프로그램

CMD
→ 기본 명령 또는 ENTRYPOINT에 전달할 기본 인자</code></pre>
<p>정도로 이해하면 좋다.</p>
<hr />
<h2 id="container와-데이터">Container와 데이터</h2>
<p>Container에는 Image 위에 <strong>Writable Layer</strong>가 존재한다고 했다.</p>
<p>MariaDB가 Container 내부에 데이터를 저장한다고 생각해보자.</p>
<pre><code class="language-text">Container

Writable Layer
└─ /var/lib/mysql</code></pre>
<p>문제는 Container를 삭제하면 이 Writable Layer 역시 Container와 함께 사라진다는 것이다.</p>
<pre><code class="language-text">Container 삭제
       ↓
Writable Layer 삭제
       ↓
DB Data 삭제</code></pre>
<p>Application Container는 같은 Image로 다시 만들면 되지만,</p>
<p>DB의 중요한 Data까지 함께 사라지면 안 된다.</p>
<p>그래서</p>
<blockquote>
<p><strong>Application의 생명주기와 Data의 생명주기를 분리해야 한다.</strong></p>
</blockquote>
<hr />
<h3 id="volume">Volume</h3>
<p>Volume은 Container 외부의 저장 공간을 Container 내부 Directory에 연결하는 방식이다.</p>
<p>예를 들어,</p>
<pre><code class="language-bash">docker run -d \
  --name mariadb \
  -v $(pwd)/db-data:/var/lib/mysql \
  mariadb:latest</code></pre>
<p>라고 실행하면</p>
<pre><code class="language-text">Host

./db-data
    │
    │ Mount
    ▼

Container

/var/lib/mysql</code></pre>
<p>형태로 연결된다.</p>
<p>MariaDB는 여전히 <code>/var/lib/mysql</code>에 데이터를 저장한다고 생각하지만,</p>
<p>실제 데이터는 Host의 <code>./db-data</code>에 유지된다.</p>
<p>따라서 Container를 삭제하더라도 데이터는 남을 수 있다.</p>
<p>Container와 Volume을 이해할 때 중요한 관점은 이것이다.</p>
<pre><code class="language-text">Application 실행 환경
→ Container

보존해야 할 Data
→ Volume</code></pre>
<blockquote>
<p><strong>Container를 오래 살려서 데이터를 보존하는 것이 아니라, Container는 언제든 다시 만들 수 있게 하고 보존해야 할 State는 외부로 분리한다.</strong></p>
</blockquote>
<p>이러한 사고방식은 이후 Kubernetes의 Pod와 Persistent Volume을 이해할 때도 그대로 이어진다.</p>
<hr />
<h2 id="타사-container-engine---podman">타사 Container Engine - Podman</h2>
<blockquote>
<p><strong>Podman</strong></p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/042719cc-03e7-47b7-b2b4-efb06a887767/image.png" /></p>
<p>Podman은 Docker와 유사하게 Container와 Image를 관리할 수 있는 Container Engine이며, 대표적인 특징 중 하나로 <strong>Daemonless 구조</strong>를 가진다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1b1bfd67-4d84-44a7-b94f-8965584961ca/image.png" /></p>
<p><strong>Docker 방식</strong></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/013fe238-01dd-4ce9-9324-05a85da2d636/image.png" /></p>
<p><strong>Podman 방식</strong></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ebff88ea-5474-4681-b95e-603d3ee6310b/image.png" /></p>
<p>Docker와 내부 구조에는 차이가 있지만,</p>
<pre><code class="language-text">Image
→ Container
→ Process</code></pre>
<p>라는 Container의 기본적인 사고방식을 이해하고 있다면 다른 Container Engine 역시 훨씬 쉽게 이해할 수 있다.</p>
<hr />
<h2 id="docker-cli">Docker CLI</h2>
<p>Docker CLI는 일반적으로</p>
<pre><code class="language-bash">docker [command] [options]</code></pre>
<p>형태로 사용한다.</p>
<p>명령어 자체를 모두 외우기보다 <strong>지금 내가 Image를 다루는지, Container를 다루는지</strong>를 구분하는 것이 중요하다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/615c0c3e-65d3-49aa-aaf8-de45f8511018/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4be2eb68-6a8c-42a4-b193-9f2a580cf064/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/829b25d7-367c-4285-aa9e-b0d42978bfc6/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3d6b5e5e-ffb8-4788-b457-1277e245fa3d/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1ee1b4b2-cf98-4733-acac-73ebbe1348f4/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ebaddcc4-104d-45d4-b786-128a1b6743f3/image.png" /></p>
<p>큰 흐름은 다음 정도로 기억하면 된다.</p>
<pre><code class="language-text">Image
├─ pull
├─ build
├─ images
└─ rmi

Container
├─ run
├─ ps
├─ start
├─ stop
├─ exec
└─ rm</code></pre>
<hr />
<h2 id="docker의-전체-흐름">Docker의 전체 흐름</h2>
<p>지금까지의 내용을 한 번 연결해보자.</p>
<pre><code class="language-text">Dockerfile
│
│ Application 실행 환경을 코드로 정의
▼

Docker Image
│
│ Read Only Layer들의 집합
▼

docker run
│
▼

Docker Container
│
├─ Main Process
│
└─ Writable Layer
│
├──── 필요한 외부 Data ────▶ Volume
│
└──── 여러 Container 운영 ─▶ Orchestration</code></pre>
<p>결국 각 개념은 다음과 같이 연결된다.</p>
<blockquote>
<p><strong>Dockerfile은 사람이 수동으로 만들던 실행 환경을 재현 가능한 코드로 만든다.</strong></p>
</blockquote>
<blockquote>
<p><strong>Image는 그 실행 환경을 Read Only Layer 형태로 저장한 결과물이다.</strong></p>
</blockquote>
<blockquote>
<p><strong>Container는 Image를 기반으로 Writable Layer를 추가하고 실제 Process를 실행한다.</strong></p>
</blockquote>
<blockquote>
<p><strong>Volume은 Container와 보존해야 할 Data의 생명주기를 분리한다.</strong></p>
</blockquote>
<hr />
<h2 id="container가-많아진다면">Container가 많아진다면?</h2>
<p>Container 몇 개 정도라면 Docker를 이용하여 직접 관리할 수 있다.</p>
<p>하지만 하나의 서비스가 수십, 수백 개의 Container로 구성되기 시작한다면 이야기가 달라진다.</p>
<pre><code class="language-text">Frontend Container × N
Backend Container × N
AI Container × N
Database
Cache
...</code></pre>
<p>관리자는</p>
<ul>
<li>어떤 서버에서 Container를 실행할지</li>
<li>Container가 죽으면 어떻게 복구할지</li>
<li>트래픽이 증가하면 몇 개를 더 실행할지</li>
<li>새로운 Version을 어떻게 배포할지</li>
<li>Container 간 Network를 어떻게 연결할지</li>
</ul>
<p>등을 지속적으로 관리해야 한다.</p>
<p>이러한 여러 Container의 <strong>배포, 확장, 복구, 네트워크와 생명주기 관리 등을 자동화하는 것</strong>을</p>
<p><strong>Container Orchestration</strong>이라고 한다.</p>
<p>대표적인 플랫폼이 <strong>Kubernetes</strong>다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e261288f-b670-4725-9c2a-a71836f5dd54/image.png" /></p>
<pre><code class="language-text">Docker / Container Runtime
→ Container를 실행

Kubernetes
→ 많은 Container가 원하는 상태로 동작하도록 관리</code></pre>
<p>이번 글에서는 Kubernetes의 세부 리소스까지 들어가기보다는,</p>
<blockquote>
<p><strong>Docker를 통해 하나의 Container를 이해한 다음, 많은 Container를 운영하기 위해 Kubernetes가 등장한다.</strong></p>
</blockquote>
<p>정도의 연결만 알아두자.</p>
<p>Kubernetes의 Cluster 구조와 Pod, Deployment, Service 등의 리소스는 이후 글에서 별도로 자세히 살펴본다.</p>
<hr />
<h2 id="마치며">마치며</h2>
<p>Docker를 공부하기 전에는 Container를 단순히 VM보다 가벼운 가상환경 정도로 생각하기 쉽다.</p>
<p>하지만 실제 구조를 따라가보면,</p>
<pre><code class="language-text">Linux Kernel 공유
        ↓
격리된 Process 실행
        ↓
Dockerfile로 실행 환경 정의
        ↓
Read Only Layer로 Image 구성
        ↓
Writable Layer를 가진 Container 실행
        ↓
State는 Volume으로 분리</code></pre>
<p>라는 하나의 흐름으로 연결된다.</p>
<p>결국 Docker는 단순히 애플리케이션을 격리해서 실행하는 도구가 아니라,</p>
<p><strong>Application의 실행 환경을 재현 가능한 Image로 만들고,
이를 독립적인 Process 단위로 실행할 수 있도록 만드는 기술</strong></p>
<p>이라고 이해할 수 있다.</p>
<p>이제 하나의 Container가 어떻게 만들어지고 실행되는지는 알았다.</p>
<p>다음부터는 이러한 Container가 많아졌을 때,
이를 실제 서비스 환경에서 어떻게 관리할 것인지로 넘어가보자.</p>