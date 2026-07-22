<h1 id="github-actions-docker-ghcr-ec2-docker-compose로-자동-배포하기">GitHub Actions, Docker, GHCR, EC2, Docker Compose로 자동 배포하기</h1>
<p>** 큰 흐름 **</p>
<pre><code>프로젝트는 GitHub Repository에서 관리하고 있으며, `dev` 브랜치에 코드가 push되면 GitHub Actions가 자동으로 실행된다. 
GitHub Actions는 프로젝트를 빌드하고 테스트한 뒤 Docker 이미지를 생성하고, 이를 GHCR, 즉 GitHub Container Registry에 업로드한다.
이후 EC2 서버에 SSH로 접속하여 최신 이미지를 pull 받고 Docker Compose를 통해 애플리케이션을 재실행한다.</code></pre><p>최종적으로 구성한 배포 흐름은 다음과 같다.</p>
<pre><code class="language-text">dev 브랜치 push
  ↓
GitHub Actions 실행
  ↓
Repository checkout
  ↓
Java 17 환경 구성
  ↓
Gradle test / bootJar
  ↓
Docker image build
  ↓
GHCR push
  ↓
EC2 SSH 접속
  ↓
docker compose pull app
  ↓
docker compose up -d
  ↓
Spring Boot + MySQL + RabbitMQ 실행</code></pre>
<p>배포 서버는 EC2 한 대를 기준으로 구성했고, Docker Compose를 사용해 Spring Boot 애플리케이션, MySQL, RabbitMQ, Dozzle을 함께 실행하도록 했다.</p>
<pre><code class="language-text">solvesync-app       Spring Boot 애플리케이션
solvesync-mysql     MySQL 8.0
solvesync-rabbitmq  RabbitMQ
solvesync-dozzle    컨테이너 로그 모니터링 도구</code></pre>
<p>이번 글에서는 단순히 “어떻게 설정했는가”뿐 아니라, 각 파일과 명령어가 실제로 어떤 역할을 하는지 상세히 정리한다.</p>
<hr />
<h1 id="cicd를-도입한-이유">CI/CD를 도입한 이유</h1>
<p>초기에는 EC2에 직접 접속해서 jar 파일을 실행하거나, 서버에서 직접 코드를 pull 받은 뒤 빌드하는 방식도 고려할 수 있다.</p>
<p>예를 들면 다음과 같은 방식이다.</p>
<pre><code class="language-text">EC2 접속
  ↓
git pull
  ↓
./gradlew build
  ↓
java -jar app.jar</code></pre>
<p>이 방식은 단순하지만 몇 가지 문제가 있다.</p>
<p>첫째, EC2에 Java, Gradle, 빌드 환경이 모두 설치되어 있어야 한다.
둘째, 배포할 때마다 서버에서 직접 빌드를 수행해야 하므로 서버 부담이 커진다.
셋째, MySQL, RabbitMQ 같은 의존 서비스까지 함께 관리하려면 환경 재현성이 떨어진다.
넷째, 사람이 직접 명령어를 실행해야 하므로 실수가 발생하기 쉽다.</p>
<p>그래서 이번 프로젝트에서는 다음과 같은 방향으로 배포 구조를 잡았다.</p>
<pre><code class="language-text">빌드와 테스트는 GitHub Actions에서 수행한다.
애플리케이션은 Docker 이미지로 패키징한다.
이미지는 GHCR에 저장한다.
EC2는 완성된 이미지를 pull 받아 실행만 한다.
MySQL, RabbitMQ 등 의존 서비스는 Docker Compose로 함께 관리한다.</code></pre>
<p>즉, EC2는 빌드 서버가 아니라 실행 서버로만 사용한다.</p>
<hr />
<h1 id="최종-아키텍처">최종 아키텍처</h1>
<pre><code class="language-text">[개발자 로컬 환경]
    |
    | git push origin dev
    v

[GitHub Repository]
    |
    | push event 감지
    v

[GitHub Actions Runner]
    |
    | 1. 코드 checkout
    | 2. Java 17 설정
    | 3. Gradle test / bootJar
    | 4. Docker image build
    | 5. GHCR push
    v

[GHCR]
    |
    | ghcr.io/solvesyncproject/solve_sync_spring_server:latest
    v

[EC2]
    |
    | 1. docker compose pull app
    | 2. docker compose up -d
    v

[Docker Containers]
    |
    |-- solvesync-app
    |-- solvesync-mysql
    |-- solvesync-rabbitmq
    |-- solvesync-dozzle</code></pre>
<p>이 구조에서 핵심 파일은 두 개다.</p>
<pre><code class="language-text">프로젝트 내부
├── Dockerfile
└── .github/workflows/deploy.yml</code></pre>
<p>각 파일의 역할은 다음과 같다.</p>
<pre><code class="language-text">Dockerfile
→ Spring Boot 애플리케이션을 Docker 이미지로 만드는 설계도

deploy.yml
→ GitHub Actions에서 빌드, 테스트, 이미지 push, EC2 배포를 자동화하는 파일</code></pre>
<p>그리고 EC2에는 다음 파일들이 필요하다.</p>
<pre><code class="language-text">EC2 내부
└── ~/solvesync
    ├── docker-compose.yml
    ├── application.yml
    └── .env</code></pre>
<hr />