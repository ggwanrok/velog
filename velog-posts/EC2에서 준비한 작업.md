<h1 id="ec2에서-준비한-작업">EC2에서 준비한 작업</h1>
<p>GitHub Actions 파일만 작성한다고 자동 배포가 되는 것은 아니다. EC2에도 Docker 기반 배포를 위한 준비가 필요하다.</p>
<p>EC2에서 수행한 작업은 크게 다음과 같다.</p>
<pre><code class="language-text">1. 보안 그룹 설정
2. Docker 설치
3. Docker Compose 사용 가능 여부 확인
4. ubuntu 사용자를 docker 그룹에 추가
5. 배포 디렉토리 생성
6. docker-compose.yml 작성
7. application.yml 작성
8. 필요한 환경 변수 또는 .env 파일 구성
9. GHCR 이미지 pull 가능 여부 확인</code></pre>
<hr />
<h2 id="보안-그룹-설정">보안 그룹 설정</h2>
<p>보안 그룹에서는 필요한 포트만 열어야 한다.</p>
<p>기본적으로 필요한 포트는 다음과 같다.</p>
<pre><code class="language-text">22
→ SSH 접속용
→ 가능하면 내 IP 또는 GitHub Actions 접근 방식을 고려해 제한하는 것이 좋다.

80
→ HTTP 서비스 제공 시 사용

443
→ HTTPS 서비스 제공 시 사용

8080
→ Spring Boot 직접 접근 시 사용
→ Nginx를 앞에 둘 경우 외부에 열지 않아도 된다.

9999
→ Dozzle 접근 포트
→ 외부 공개는 권장하지 않는다.</code></pre>
<p>이번 Compose 설정에서는 Spring Boot 애플리케이션을 다음처럼 바인딩했다.</p>
<pre><code class="language-yaml">ports:
  - &quot;127.0.0.1:8080:8080&quot;</code></pre>
<p>이 설정은 EC2 외부에서 직접 <code>8080</code> 포트로 접근하지 못하게 하고, EC2 내부에서만 접근 가능하게 만든다.</p>
<p>이 구조는 보통 Nginx를 앞단에 둘 때 사용한다.</p>
<pre><code class="language-text">외부 사용자
  ↓
80 / 443
  ↓
Nginx
  ↓
127.0.0.1:8080
  ↓
Spring Boot app</code></pre>
<p>따라서 Nginx를 사용할 경우 8080 포트는 외부에 열 필요가 없다.</p>
<hr />
<h2 id="docker-설치">Docker 설치</h2>
<p>EC2에서 Docker를 설치했다.</p>
<p>설치 후 다음 명령으로 정상 설치 여부를 확인할 수 있다.</p>
<pre><code class="language-bash">docker --version
docker compose version</code></pre>
<p>GitHub Actions가 EC2 내부에서 다음 명령을 실행하므로 Docker와 Docker Compose가 반드시 설치되어 있어야 한다.</p>
<pre><code class="language-bash">docker login ghcr.io
docker compose pull app
docker compose up -d</code></pre>
<hr />
<h2 id="docker-권한-설정">Docker 권한 설정</h2>
<p>Ubuntu에서 Docker를 설치하면 기본적으로 Docker 명령 실행에 root 권한이 필요할 수 있다.</p>
<p>GitHub Actions는 EC2에 <code>ubuntu</code> 사용자로 접속하기 때문에, <code>ubuntu</code> 사용자가 Docker 명령을 실행할 수 있어야 한다.</p>
<p>이를 위해 다음 명령을 실행했다.</p>
<pre><code class="language-bash">sudo usermod -aG docker ubuntu</code></pre>
<p>이후 SSH 재접속을 해야 그룹 권한이 반영된다.</p>
<p>권한 설정이 되어 있지 않으면 다음과 같은 에러가 발생할 수 있다.</p>
<pre><code class="language-text">permission denied while trying to connect to the Docker daemon socket</code></pre>
<hr />
<h2 id="배포-디렉토리-생성">배포 디렉토리 생성</h2>
<p>GitHub Actions의 배포 단계에서 다음 명령을 실행한다.</p>
<pre><code class="language-bash">cd ~/solvesync</code></pre>
<p>따라서 EC2에 미리 <code>~/solvesync</code> 디렉토리를 생성해두어야 한다.</p>
<pre><code class="language-bash">mkdir -p ~/solvesync
cd ~/solvesync</code></pre>
<p>이 디렉토리는 운영 관련 파일들을 모아두는 위치다.</p>
<pre><code class="language-text">~/solvesync
├── docker-compose.yml
├── application.yml
└── .env</code></pre>
<hr />
<h2 id="ec2-docker-compose-구성">EC2 Docker Compose 구성</h2>
<p>EC2에는 <code>~/solvesync/docker-compose.yml</code> 파일을 작성했다.</p>
<p>예시는 다음과 같다.</p>
<pre><code class="language-yaml">services:
  app:
    image: ghcr.io/solvesyncproject/solve_sync_spring_server:latest
    container_name: solvesync-app
    volumes:
      - ./application.yml:/app/config/application.yml:ro
    ports:
      - &quot;127.0.0.1:8080:8080&quot;
    depends_on:
      - mysql
      - rabbitmq
    restart: always

  mysql:
    image: mysql:8.0
    container_name: solvesync-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: solvesync
      TZ: Asia/Seoul
    volumes:
      - solvesync_mysql:/var/lib/mysql
    command: &gt;
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_0900_ai_ci
    restart: always

  rabbitmq:
    image: rabbitmq:3.13-management
    container_name: solvesync-rabbitmq
    environment:
      TZ: Asia/Seoul
    volumes:
      - solvesync_rabbitmq:/var/lib/rabbitmq
    restart: always

  dozzle:
    image: amir20/dozzle:latest
    container_name: solvesync-dozzle
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    ports:
      - &quot;127.0.0.1:9999:8080&quot;
    restart: always

volumes:
  solvesync_mysql:
  solvesync_rabbitmq:</code></pre>
<hr />
<h3 id="app-서비스">app 서비스</h3>
<pre><code class="language-yaml">app:
  image: ghcr.io/solvesyncproject/solve_sync_spring_server:latest
  container_name: solvesync-app</code></pre>
<p><code>app</code> 서비스는 Spring Boot 애플리케이션 컨테이너다.</p>
<p>이미지는 GHCR에 업로드된 다음 이미지를 사용한다.</p>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server:latest</code></pre>
<p>GitHub Actions에서 이미지를 새로 push하면, EC2에서는 다음 명령으로 최신 이미지를 가져온다.</p>
<pre><code class="language-bash">docker compose pull app</code></pre>
<hr />
<h3 id="applicationyml-마운트">application.yml 마운트</h3>
<pre><code class="language-yaml">volumes:
  - ./application.yml:/app/config/application.yml:ro</code></pre>
<p>EC2에 있는 <code>application.yml</code>을 컨테이너 내부 <code>/app/config/application.yml</code>로 마운트한다.</p>
<pre><code class="language-text">EC2
~/solvesync/application.yml

→ 컨테이너 내부
/app/config/application.yml</code></pre>
<p><code>ro</code>는 read-only를 의미한다.</p>
<p>즉, 컨테이너 내부에서 이 파일을 수정할 수 없도록 읽기 전용으로 마운트한다.</p>
<p>이렇게 구성한 이유는 애플리케이션 이미지와 운영 설정을 분리하기 위해서다.</p>
<p>Docker 이미지에는 jar 파일만 포함하고, DB 주소, RabbitMQ 주소, OAuth Secret, JWT Secret 같은 운영 설정은 EC2의 설정 파일에서 관리한다.</p>
<hr />
<h3 id="app-포트-설정">app 포트 설정</h3>
<pre><code class="language-yaml">ports:
  - &quot;127.0.0.1:8080:8080&quot;</code></pre>
<p>이 설정은 EC2 내부의 <code>127.0.0.1:8080</code>을 컨테이너 내부의 <code>8080</code> 포트와 연결한다.</p>
<p>외부에서 직접 8080 포트로 접근할 수 없고, EC2 내부에서만 접근 가능하다.</p>
<p>이 방식은 Nginx를 앞단에 둘 때 적절하다.</p>
<pre><code class="language-text">Nginx
→ 127.0.0.1:8080
→ Spring Boot container</code></pre>
<hr />
<h3 id="depends_on">depends_on</h3>
<pre><code class="language-yaml">depends_on:
  - mysql
  - rabbitmq</code></pre>
<p><code>app</code> 컨테이너가 <code>mysql</code>, <code>rabbitmq</code> 컨테이너보다 뒤에 실행되도록 설정한다.</p>
<p>다만 주의할 점이 있다.</p>
<p><code>depends_on</code>은 컨테이너의 시작 순서를 보장하지만, MySQL이나 RabbitMQ가 완전히 준비된 상태인지까지 보장하지는 않는다.</p>
<p>즉, 다음 차이를 이해해야 한다.</p>
<pre><code class="language-text">depends_on이 보장하는 것
→ mysql 컨테이너를 먼저 시작한다.

depends_on이 보장하지 않는 것
→ MySQL이 실제로 연결 가능한 상태가 될 때까지 기다린다.</code></pre>
<p>따라서 더 안정적인 운영을 위해서는 MySQL healthcheck나 Spring Boot의 DB 연결 재시도 설정을 함께 고려할 수 있다.</p>
<hr />
<h3 id="mysql-서비스">MySQL 서비스</h3>
<pre><code class="language-yaml">mysql:
  image: mysql:8.0
  container_name: solvesync-mysql
  environment:
    MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    MYSQL_DATABASE: solvesync
    TZ: Asia/Seoul
  volumes:
    - solvesync_mysql:/var/lib/mysql
  command: &gt;
    --character-set-server=utf8mb4
    --collation-server=utf8mb4_0900_ai_ci
  restart: always</code></pre>
<p>MySQL 컨테이너를 실행하는 설정이다.</p>
<p><code>MYSQL_ROOT_PASSWORD</code>는 직접 작성하지 않고 <code>.env</code> 파일에서 가져오도록 했다.</p>
<pre><code class="language-env">MYSQL_ROOT_PASSWORD=실제비밀번호</code></pre>
<p>DB 데이터는 컨테이너 내부에만 저장하면 안 된다. 컨테이너가 삭제되면 데이터도 함께 사라질 수 있기 때문이다.</p>
<p>그래서 Docker volume을 사용했다.</p>
<pre><code class="language-yaml">volumes:
  - solvesync_mysql:/var/lib/mysql</code></pre>
<p>이렇게 하면 컨테이너를 재시작하거나 교체해도 MySQL 데이터는 volume에 유지된다.</p>
<hr />
<h3 id="rabbitmq-서비스">RabbitMQ 서비스</h3>
<pre><code class="language-yaml">rabbitmq:
  image: rabbitmq:3.13-management
  container_name: solvesync-rabbitmq
  environment:
    TZ: Asia/Seoul
  volumes:
    - solvesync_rabbitmq:/var/lib/rabbitmq
  restart: always</code></pre>
<p>RabbitMQ 컨테이너를 실행하는 설정이다.</p>
<p><code>rabbitmq:3.13-management</code> 이미지를 사용하면 RabbitMQ 관리 UI도 함께 제공된다.</p>
<p>RabbitMQ도 내부 상태를 유지해야 할 수 있으므로 volume을 연결했다.</p>
<pre><code class="language-yaml">volumes:
  - solvesync_rabbitmq:/var/lib/rabbitmq</code></pre>
<hr />
<h3 id="dozzle-서비스">Dozzle 서비스</h3>
<pre><code class="language-yaml">dozzle:
  image: amir20/dozzle:latest
  container_name: solvesync-dozzle
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  ports:
    - &quot;127.0.0.1:9999:8080&quot;
  restart: always</code></pre>
<p>Dozzle은 Docker 컨테이너 로그를 웹에서 확인할 수 있게 해주는 도구다.</p>
<p>다만 Dozzle은 컨테이너 로그를 볼 수 있기 때문에 외부에 직접 공개하면 위험할 수 있다. 로그에는 DB 연결 정보, 에러 메시지, 토큰 관련 정보 등이 포함될 수 있기 때문이다.</p>
<p>따라서 다음처럼 로컬 바인딩으로 제한했다.</p>
<pre><code class="language-yaml">ports:
  - &quot;127.0.0.1:9999:8080&quot;</code></pre>
<p>외부에서 접근하려면 Nginx에 인증을 붙이거나 SSH 터널링을 사용하는 방식이 더 안전하다.</p>
<hr />
<h2 id="applicationyml-구성">application.yml 구성</h2>
<p>로컬 환경과 Docker Compose 배포 환경은 DB와 RabbitMQ 주소가 다르다.</p>
<p>로컬에서 Spring Boot를 직접 실행하는 경우에는 보통 다음처럼 접근한다.</p>
<pre><code class="language-yaml">spring:
  datasource:
    url: jdbc:mysql://localhost:3307/solvesync

rabbitmq:
  host: localhost</code></pre>
<p>하지만 EC2 배포 환경에서는 Spring Boot 애플리케이션도 컨테이너 안에서 실행된다.</p>
<p>컨테이너 안에서 <code>localhost</code>는 EC2 서버 자체가 아니라 해당 컨테이너 자신을 의미한다.</p>
<p>즉, app 컨테이너 내부에서 <code>localhost:3306</code>으로 접근하면 MySQL 컨테이너가 아니라 app 컨테이너 자기 자신을 바라보게 된다.</p>
<p>따라서 Docker Compose 환경에서는 서비스 이름으로 접근해야 한다.</p>
<pre><code class="language-yaml">spring:
  datasource:
    url: jdbc:mysql://mysql:3306/solvesync

rabbitmq:
  host: rabbitmq</code></pre>
<p>Docker Compose는 같은 Compose 네트워크 안에서 서비스 이름을 DNS처럼 사용할 수 있게 해준다.</p>
<pre><code class="language-text">solvesync-app
  → mysql:3306
  → solvesync-mysql

solvesync-app
  → rabbitmq:5672
  → solvesync-rabbitmq</code></pre>
<p>따라서 배포 환경에서는 <code>localhost</code>가 아니라 <code>mysql</code>, <code>rabbitmq</code>를 사용해야 한다.</p>
<hr />
<h2 id="jpa-ddl-auto-설정">JPA ddl-auto 설정</h2>
<p>개발 환경에서는 편의를 위해 다음 설정을 사용할 수 있다.</p>
<pre><code class="language-yaml">spring:
  jpa:
    hibernate:
      ddl-auto: create</code></pre>
<p>하지만 운영 환경에서 <code>create</code>를 사용하면 애플리케이션 재시작 시 테이블을 다시 생성하면서 데이터가 삭제될 수 있다.</p>
<p>따라서 배포 환경에서는 최소한 다음처럼 설정했다.</p>
<pre><code class="language-yaml">spring:
  jpa:
    hibernate:
      ddl-auto: update</code></pre>
<p>다만 <code>update</code>도 완전한 운영용 스키마 관리 방식은 아니다.</p>
<p>실제 운영 단계에서는 Flyway나 Liquibase 같은 DB 마이그레이션 도구를 사용하는 것이 더 안전하다.</p>
<p>정리하면 다음과 같다.</p>
<pre><code class="language-text">create
→ 애플리케이션 시작 시 스키마 재생성
→ 데이터 손실 위험
→ 운영 환경 사용 부적절

update
→ 엔티티 변경사항을 기반으로 스키마 일부 갱신
→ 초기 운영이나 개발 서버에서는 편리
→ 실제 운영에서는 예측 어려운 변경 가능성 있음

Flyway / Liquibase
→ SQL migration 파일 기반으로 명시적 스키마 변경
→ 운영 환경에 더 적합</code></pre>
<hr />