<h1 id="github-actions-workflow-작성">GitHub Actions workflow 작성</h1>
<p>CI/CD의 핵심은 <code>.github/workflows/deploy.yml</code> 파일이다.</p>
<p>이 파일은 GitHub Actions가 어떤 조건에서 실행되고, 어떤 순서로 작업을 수행할지 정의한다.</p>
<pre><code class="language-yaml">name: Deploy

on:
  push:
    branches:
      - dev
  workflow_dispatch:

permissions:
  contents: read
  packages: write

env:
  IMAGE_NAME: ghcr.io/solvesyncproject/solve_sync_spring_server

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v5

      - name: Set up Java
        uses: actions/setup-java@v5
        with:
          distribution: temurin
          java-version: '17'

      - name: Build
        run: |
          chmod +x ./gradlew
          ./gradlew clean test bootJar

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v7
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE_NAME }}:latest
            ${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Deploy to EC2
        env:
          EC2_HOST: ${{ secrets.EC2_HOST }}
          EC2_USER: ${{ secrets.EC2_USER }}
          EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
          GHCR_USERNAME: ${{ secrets.GHCR_USERNAME }}
          GHCR_PAT: ${{ secrets.GHCR_PAT }}
        run: |
          mkdir -p ~/.ssh
          echo &quot;$EC2_SSH_KEY&quot; &gt; ~/.ssh/ec2_key
          chmod 600 ~/.ssh/ec2_key

          ssh -i ~/.ssh/ec2_key -o StrictHostKeyChecking=no &quot;$EC2_USER@$EC2_HOST&quot; &quot;
            cd ~/solvesync &amp;&amp;
            echo '$GHCR_PAT' | docker login ghcr.io -u '$GHCR_USERNAME' --password-stdin &amp;&amp;
            docker compose pull app &amp;&amp;
            docker compose up -d
          &quot;</code></pre>
<h2 id="상세-흐름설명">상세 흐름설명</h2>
<p>이제 각 부분을 하나씩 살펴보자.</p>
<hr />
<h3 id="workflow-이름">workflow 이름</h3>
<pre><code class="language-yaml">name: Deploy</code></pre>
<p>GitHub Actions 화면에 표시될 workflow 이름이다.</p>
<p>GitHub Repository의 <code>Actions</code> 탭에 들어가면 <code>Deploy</code>라는 이름으로 실행 기록을 확인할 수 있다.</p>
<hr />
<h3 id="workflow-실행-조건">workflow 실행 조건</h3>
<pre><code class="language-yaml">on:
  push:
    branches:
      - dev
  workflow_dispatch:</code></pre>
<p>이 부분은 workflow가 언제 실행될지 정의한다.</p>
<hr />
<h4 id="workflow-실행-조건-1-dev-브랜치-push-시-자동-실행">workflow 실행 조건-1. <code>dev</code> 브랜치 push 시 자동 실행</h4>
<pre><code class="language-yaml">push:
  branches:
    - dev</code></pre>
<p>이 설정은 <code>dev</code> 브랜치에 push가 발생하면 workflow를 자동으로 실행한다는 의미다.</p>
<p>예를 들어 다음 명령을 실행하면</p>
<pre><code class="language-bash">git push origin dev</code></pre>
<p>GitHub는 <code>dev</code> 브랜치에 push 이벤트가 발생한 것을 감지하고, <code>Deploy</code> workflow를 실행한다.</p>
<p>즉, 현재 구조에서 <code>dev</code> 브랜치는 배포 기준 브랜치 역할을 한다.</p>
<p>일반적인 개발 흐름은 다음과 같다.</p>
<pre><code class="language-text">feature 브랜치에서 기능 개발
  ↓
Pull Request 생성
  ↓
dev 브랜치로 merge
  ↓
dev 브랜치에 push 이벤트 발생
  ↓
GitHub Actions 자동 배포 실행</code></pre>
<hr />
<h4 id="workflow-실행-조건-2-수동-실행-지원">workflow 실행 조건-2. 수동 실행 지원</h4>
<pre><code class="language-yaml">workflow_dispatch:</code></pre>
<p><code>workflow_dispatch</code>는 GitHub Actions 화면에서 수동으로 workflow를 실행할 수 있게 해준다.</p>
<p>즉, 이 workflow는 두 가지 방식으로 실행될 수 있다.</p>
<pre><code class="language-text">1. dev 브랜치에 push될 때 자동 실행
2. GitHub Actions 화면에서 Run workflow 버튼으로 수동 실행</code></pre>
<p>수동 실행 기능을 넣어두면, 서버에서 문제가 발생했거나 같은 커밋을 다시 배포하고 싶을 때 유용하다.</p>
<hr />
<h3 id="github-actions-권한-설정">GitHub Actions 권한 설정</h3>
<pre><code class="language-yaml">permissions:
  contents: read
  packages: write</code></pre>
<p>GitHub Actions에서 사용할 권한을 명시한 부분이다.</p>
<hr />
<h4 id="github-actions-권한-설정-1-contents-read">GitHub Actions 권한 설정-1. <code>contents: read</code></h4>
<pre><code class="language-yaml">contents: read</code></pre>
<p>Repository의 코드를 읽을 수 있는 권한이다.</p>
<p>workflow의 첫 단계에서 사용하는 <code>actions/checkout</code>은 GitHub Repository의 코드를 Actions Runner로 가져온다.</p>
<p>따라서 Repository 내용을 읽을 수 있어야 한다.</p>
<hr />
<h4 id="github-actions-권한-설정-2-packages-write">GitHub Actions 권한 설정-2. <code>packages: write</code></h4>
<pre><code class="language-yaml">packages: write</code></pre>
<p>GitHub Packages, 즉 GHCR에 이미지를 업로드하기 위한 권한이다.</p>
<p>GitHub Actions에서 Docker 이미지를 빌드한 뒤 GHCR에 push하려면 package write 권한이 필요하다.</p>
<p>이 권한 덕분에 다음 이미지 push가 가능해진다.</p>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server:latest
ghcr.io/solvesyncproject/solve_sync_spring_server:${github.sha}</code></pre>
<hr />
<h3 id="workflow-전역-환경-변수">workflow 전역 환경 변수</h3>
<pre><code class="language-yaml">env:
  IMAGE_NAME: ghcr.io/solvesyncproject/solve_sync_spring_server</code></pre>
<p>workflow 전체에서 사용할 환경 변수를 정의한 부분이다.</p>
<p><code>IMAGE_NAME</code>에는 Docker 이미지 이름을 저장했다.</p>
<p>이미지 이름 구조는 다음과 같다.</p>
<pre><code class="language-text">ghcr.io/{GitHub 조직 또는 계정명}/{이미지 이름}</code></pre>
<p>이번 프로젝트에서는 다음 이름을 사용했다.</p>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server</code></pre>
<p>환경 변수로 분리한 이유는 같은 이미지 이름을 여러 곳에서 반복해서 작성하지 않기 위해서다.</p>
<p>예를 들어 이미지 태그를 붙일 때 다음처럼 재사용할 수 있다.</p>
<pre><code class="language-yaml">tags: |
  ${{ env.IMAGE_NAME }}:latest
  ${{ env.IMAGE_NAME }}:${{ github.sha }}</code></pre>
<p>이렇게 하면 이미지 이름이 변경되더라도 <code>env</code> 부분만 수정하면 된다.</p>
<hr />
<h3 id="job-설정">Job 설정</h3>
<pre><code class="language-yaml">jobs:
  deploy:
    runs-on: ubuntu-latest</code></pre>
<p>GitHub Actions에서 실제 작업 단위를 <code>job</code>이라고 한다.</p>
<p>여기서는 <code>deploy</code>라는 job 하나를 정의했다.</p>
<pre><code class="language-yaml">runs-on: ubuntu-latest</code></pre>
<p>이 설정은 GitHub가 제공하는 Ubuntu 기반 가상 머신에서 작업을 실행한다는 뜻이다.</p>
<p>즉, CI/CD 작업은 내 로컬 PC나 EC2에서 처음부터 실행되는 것이 아니라, GitHub Actions가 임시로 제공하는 서버에서 실행된다.</p>
<pre><code class="language-text">GitHub Actions Runner
  ↓
ubuntu-latest 환경 생성
  ↓
checkout
  ↓
Java 설치
  ↓
Gradle build
  ↓
Docker image build
  ↓
GHCR push
  ↓
EC2 SSH 접속</code></pre>
<hr />
<h3 id="step-1-repository-checkout">Step 1: Repository checkout</h3>
<pre><code class="language-yaml">- name: Checkout
  uses: actions/checkout@v5</code></pre>
<p>이 단계는 GitHub Repository의 코드를 Actions Runner로 가져오는 역할을 한다.</p>
<p>쉽게 말해 Actions Runner에서 다음과 비슷한 작업을 수행하는 것이다.</p>
<pre><code class="language-bash">git clone https://github.com/SolveSyncProject/solve_sync_spring_server.git</code></pre>
<p>이 단계가 끝나면 Actions Runner에는 프로젝트 파일들이 존재하게 된다.</p>
<pre><code class="language-text">Actions Runner 작업 디렉토리
├── src
├── build.gradle
├── settings.gradle
├── gradlew
├── Dockerfile
└── .github/workflows/deploy.yml</code></pre>
<p>이후 단계들은 이 코드를 기준으로 빌드와 Docker 이미지 생성을 진행한다.</p>
<hr />
<h3 id="step-2-java-17-환경-설정">Step 2: Java 17 환경 설정</h3>
<pre><code class="language-yaml">- name: Set up Java
  uses: actions/setup-java@v5
  with:
    distribution: temurin
    java-version: '17'</code></pre>
<p>이 단계는 Actions Runner에 Java 17 환경을 설정한다.</p>
<p>Spring Boot 프로젝트가 Java 17 기반으로 작성되어 있기 때문에, 빌드를 수행하려면 Java 17이 필요하다.</p>
<p>여기서는 <code>temurin</code> 배포판을 사용했다.</p>
<p>앞서 Dockerfile에서는 <code>eclipse-temurin:17-jre</code>를 사용했는데, 둘의 역할은 다르다.</p>
<pre><code class="language-text">GitHub Actions의 Java 17
→ 프로젝트를 컴파일하고 테스트하고 jar를 생성하기 위한 환경

Dockerfile의 Java 17 JRE
→ 생성된 jar를 컨테이너 안에서 실행하기 위한 환경</code></pre>
<p>즉, GitHub Actions에서는 빌드가 필요하므로 JDK가 필요하고, Docker 컨테이너에서는 실행만 하면 되므로 JRE를 사용했다.</p>
<hr />
<h3 id="step-3-gradle-build">Step 3: Gradle build</h3>
<pre><code class="language-yaml">- name: Build
  run: |
    chmod +x ./gradlew
    ./gradlew clean test bootJar</code></pre>
<p>이 단계에서는 Spring Boot 프로젝트를 빌드한다.</p>
<hr />
<h4 id="gradle-build-1-chmod-x-gradlew">Gradle build-1. <code>chmod +x ./gradlew</code></h4>
<pre><code class="language-bash">chmod +x ./gradlew</code></pre>
<p>Linux 환경에서 <code>gradlew</code> 파일을 실행할 수 있도록 실행 권한을 부여한다.</p>
<p>권한이 없으면 다음 명령을 실행할 수 없다.</p>
<pre><code class="language-bash">./gradlew</code></pre>
<p>GitHub Actions Runner는 Ubuntu 환경이므로, <code>gradlew</code> 실행 권한을 명시적으로 부여해주는 것이 안전하다.</p>
<hr />
<h4 id="gradle-build-2-gradlew-clean-test-bootjar">Gradle build-2. <code>./gradlew clean test bootJar</code></h4>
<pre><code class="language-bash">./gradlew clean test bootJar</code></pre>
<p>이 명령은 세 가지 작업을 순서대로 수행한다.</p>
<pre><code class="language-text">clean
→ 이전 빌드 결과물 삭제

test
→ 테스트 코드 실행

bootJar
→ 실행 가능한 Spring Boot jar 파일 생성</code></pre>
<p><code>clean</code>은 기존 <code>build</code> 디렉토리의 결과물을 정리한다.</p>
<p><code>test</code>는 테스트 코드를 실행한다. 테스트가 실패하면 이후 단계로 넘어가지 않는다. 즉, 테스트가 실패한 코드는 Docker 이미지로 만들어지지도 않고 EC2에 배포되지도 않는다.</p>
<p><code>bootJar</code>는 Spring Boot 실행 가능한 jar 파일을 생성한다.</p>
<p>실행 후에는 보통 다음 경로에 jar 파일이 생성된다.</p>
<pre><code class="language-text">build/libs/*.jar</code></pre>
<p>이 jar 파일은 이후 Dockerfile에서 사용된다.</p>
<pre><code class="language-dockerfile">ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar</code></pre>
<p>따라서 이 단계는 CI/CD 전체 흐름에서 매우 중요하다.</p>
<pre><code class="language-text">Gradle build 성공
  ↓
jar 파일 생성
  ↓
Docker 이미지 생성 가능

(or)

Gradle build 실패
  ↓
workflow 중단
  ↓
이미지 push 안 됨
  ↓
EC2 배포 안 됨</code></pre>
<hr />
<h3 id="step-4-docker-buildx-설정">Step 4: Docker Buildx 설정</h3>
<pre><code class="language-yaml">- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3</code></pre>
<p>Docker Buildx는 Docker 이미지를 빌드하기 위한 확장 빌드 도구다.</p>
<p>일반적인 <code>docker build</code>보다 더 다양한 기능을 제공한다.</p>
<p>예를 들면 다음과 같다.</p>
<pre><code class="language-text">멀티 플랫폼 이미지 빌드
빌드 캐시 활용
고급 빌드 옵션 지원
GitHub Actions와의 자연스러운 통합</code></pre>
<p>이번 프로젝트에서는 복잡한 멀티 플랫폼 빌드를 사용하지는 않았지만, <code>docker/build-push-action</code>을 사용하기 위한 표준적인 구성으로 Buildx를 설정했다.</p>
<hr />
<h3 id="step-5-ghcr-로그인">Step 5: GHCR 로그인</h3>
<pre><code class="language-yaml">- name: Login to GHCR
  uses: docker/login-action@v4
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}</code></pre>
<p>이 단계는 GitHub Actions Runner가 GHCR에 Docker 이미지를 push할 수 있도록 로그인하는 단계다.</p>
<hr />
<h4 id="ghcr-로그인-1-registry-ghcrio">GHCR 로그인-1. <code>registry: ghcr.io</code></h4>
<pre><code class="language-yaml">registry: ghcr.io</code></pre>
<p>로그인할 Docker Registry를 지정한다.</p>
<p>여기서는 GitHub Container Registry를 사용하므로 <code>ghcr.io</code>를 지정했다.</p>
<hr />
<h4 id="ghcr-로그인-2-username--githubactor-">GHCR 로그인-2. <code>username: ${{ github.actor }}</code></h4>
<pre><code class="language-yaml">username: ${{ github.actor }}</code></pre>
<p><code>github.actor</code>는 현재 workflow를 실행한 GitHub 사용자 또는 주체를 의미한다.</p>
<p>예를 들어 내가 <code>dev</code> 브랜치에 push해서 workflow가 실행되었다면, 내 GitHub 계정명이 들어간다.</p>
<hr />
<h4 id="ghcr-로그인-3-password--secretsgithub_token-">GHCR 로그인-3. <code>password: ${{ secrets.GITHUB_TOKEN }}</code></h4>
<pre><code class="language-yaml">password: ${{ secrets.GITHUB_TOKEN }}</code></pre>
<p><code>GITHUB_TOKEN</code>은 GitHub Actions가 자동으로 제공하는 토큰이다.</p>
<p>이 토큰은 별도로 GitHub Secrets에 등록하지 않아도 사용할 수 있다.</p>
<p>앞서 권한 설정에서 다음 권한을 부여했다.</p>
<pre><code class="language-yaml">permissions:
  contents: read
  packages: write</code></pre>
<p>따라서 이 <code>GITHUB_TOKEN</code>은 GHCR에 이미지를 push할 수 있는 권한을 갖는다.</p>
<p>여기서 중요한 점은 <code>GITHUB_TOKEN</code>과 <code>GHCR_PAT</code>의 역할이 다르다는 것이다.</p>
<pre><code class="language-text">GITHUB_TOKEN
→ GitHub Actions 내부에서 GHCR에 이미지를 push할 때 사용

GHCR_PAT
→ EC2 서버가 GHCR에서 이미지를 pull할 때 사용</code></pre>
<p>GitHub Actions 내부에서는 <code>GITHUB_TOKEN</code>을 사용할 수 있지만, EC2는 GitHub Actions 내부 환경이 아니므로 별도의 PAT가 필요하다.</p>
<hr />
<h3 id="step-6-docker-이미지-build--push">Step 6: Docker 이미지 build &amp; push</h3>
<pre><code class="language-yaml">- name: Build and push image
  uses: docker/build-push-action@v7
  with:
    context: .
    push: true
    tags: |
      ${{ env.IMAGE_NAME }}:latest
      ${{ env.IMAGE_NAME }}:${{ github.sha }}</code></pre>
<p>이 단계는 Dockerfile을 기반으로 Docker 이미지를 빌드하고, GHCR에 push하는 단계다.</p>
<hr />
<h4 id="docker-이미지-build--push-1-context-">Docker 이미지 build &amp; push-1. <code>context: .</code></h4>
<pre><code class="language-yaml">context: .</code></pre>
<p>Docker 빌드 컨텍스트를 현재 프로젝트 루트로 지정한다.</p>
<p>즉, Docker는 현재 Repository 루트를 기준으로 Dockerfile과 필요한 파일을 찾는다.</p>
<p>현재 구조는 다음과 같다.</p>
<pre><code class="language-text">프로젝트 루트
├── Dockerfile
├── build/libs/*.jar
├── src
├── build.gradle
└── .github/workflows/deploy.yml</code></pre>
<p>Dockerfile은 프로젝트 루트에 있고, Gradle build 결과물인 jar 파일도 <code>build/libs</code> 아래에 존재한다.</p>
<p>따라서 <code>context: .</code>로 지정하면 Dockerfile의 다음 명령이 정상적으로 동작한다.</p>
<pre><code class="language-dockerfile">ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar</code></pre>
<hr />
<h4 id="docker-이미지-build--push-2-push-true">Docker 이미지 build &amp; push-2. <code>push: true</code></h4>
<pre><code class="language-yaml">push: true</code></pre>
<p>이미지를 빌드한 뒤 Registry에 업로드하겠다는 의미다.</p>
<p>만약 <code>push: false</code>라면 이미지는 GitHub Actions Runner 내부에서만 생성되고, GHCR에는 올라가지 않는다.</p>
<p>EC2는 GHCR에서 이미지를 pull 받아야 하므로 반드시 <code>push: true</code>가 필요하다.</p>
<hr />
<h4 id="docker-이미지-build--push-3-이미지-태그-설정">Docker 이미지 build &amp; push-3. 이미지 태그 설정</h4>
<pre><code class="language-yaml">tags: |
  ${{ env.IMAGE_NAME }}:latest
  ${{ env.IMAGE_NAME }}:${{ github.sha }}</code></pre>
<p>이미지에 두 개의 태그를 붙인다.</p>
<p>예를 들어 커밋 SHA가 <code>abc123</code>이라면 다음 두 이미지 태그가 생성된다.</p>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server:latest
ghcr.io/solvesyncproject/solve_sync_spring_server:abc123</code></pre>
<p>두 태그는 같은 이미지를 가리키지만, 목적이 다르다.</p>
<hr />
<h4 id="docker-이미지-build--push-4-latest-태그">Docker 이미지 build &amp; push-4. <code>latest</code> 태그</h4>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server:latest</code></pre>
<p><code>latest</code>는 최신 배포 이미지를 쉽게 가져오기 위해 사용한다.</p>
<p>EC2의 <code>docker-compose.yml</code>에서는 다음과 같이 이미지를 지정한다.</p>
<pre><code class="language-yaml">image: ghcr.io/solvesyncproject/solve_sync_spring_server:latest</code></pre>
<p>따라서 EC2에서는 다음 명령으로 최신 애플리케이션 이미지를 가져올 수 있다.</p>
<pre><code class="language-bash">docker compose pull app</code></pre>
<hr />
<h4 id="docker-이미지-build--push-5--githubsha--태그">Docker 이미지 build &amp; push-5. <code>${{ github.sha }}</code> 태그</h4>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server:${github.sha}</code></pre>
<p><code>github.sha</code>는 현재 workflow를 실행한 커밋의 고유 해시값이다.</p>
<p>이 태그를 함께 남겨두면 특정 커밋과 Docker 이미지를 연결할 수 있다.</p>
<p>예를 들어 배포 후 문제가 발생했을 때 다음과 같은 추적이 가능하다.</p>
<pre><code class="language-text">현재 배포된 latest 이미지는 어떤 커밋에서 만들어졌는가?
문제가 생긴 버전의 커밋은 무엇인가?
이전 커밋 이미지로 롤백할 수 있는가?</code></pre>
<p>따라서 <code>latest</code>는 운영 편의성을 위한 태그이고, <code>github.sha</code>는 추적성과 롤백 가능성을 높이기 위한 태그라고 볼 수 있다.</p>
<hr />
<h3 id="step-7-ec2-배포">Step 7: EC2 배포</h3>
<pre><code class="language-yaml">- name: Deploy to EC2
  env:
    EC2_HOST: ${{ secrets.EC2_HOST }}
    EC2_USER: ${{ secrets.EC2_USER }}
    EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
    GHCR_USERNAME: ${{ secrets.GHCR_USERNAME }}
    GHCR_PAT: ${{ secrets.GHCR_PAT }}
  run: |
    mkdir -p ~/.ssh
    echo &quot;$EC2_SSH_KEY&quot; &gt; ~/.ssh/ec2_key
    chmod 600 ~/.ssh/ec2_key

    ssh -i ~/.ssh/ec2_key -o StrictHostKeyChecking=no &quot;$EC2_USER@$EC2_HOST&quot; &quot;
      cd ~/solvesync &amp;&amp;
      echo '$GHCR_PAT' | docker login ghcr.io -u '$GHCR_USERNAME' --password-stdin &amp;&amp;
      docker compose pull app &amp;&amp;
      docker compose up -d
    &quot;</code></pre>
<p>이 단계는 GitHub Actions가 EC2에 SSH로 접속해 실제 서버를 갱신하는 부분이다.</p>
<hr />
<h4 id="ec2-배포-1-ec2-배포에-필요한-환경-변수">EC2 배포-1. EC2 배포에 필요한 환경 변수</h4>
<pre><code class="language-yaml">env:
  EC2_HOST: ${{ secrets.EC2_HOST }}
  EC2_USER: ${{ secrets.EC2_USER }}
  EC2_SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
  GHCR_USERNAME: ${{ secrets.GHCR_USERNAME }}
  GHCR_PAT: ${{ secrets.GHCR_PAT }}</code></pre>
<p>이 값들은 GitHub Repository Secrets에 등록해둔 값이다.</p>
<p>각각의 의미는 다음과 같다.</p>
<pre><code class="language-text">EC2_HOST
→ EC2 퍼블릭 IP 또는 도메인

EC2_USER
→ EC2 SSH 접속 사용자
→ Ubuntu AMI 기준 보통 ubuntu

EC2_SSH_KEY
→ EC2 접속용 private key 전체 내용

GHCR_USERNAME
→ GHCR 로그인에 사용할 GitHub 계정명

GHCR_PAT
→ EC2에서 GHCR private image를 pull하기 위한 Personal Access Token</code></pre>
<p>민감한 값들은 코드에 직접 작성하지 않고 GitHub Secrets에 저장했다.</p>
<p>특히 다음 값들은 절대 Repository에 올리면 안 된다.</p>
<pre><code class="language-text">EC2 private key
GHCR PAT
DB password
JWT secret
OAuth client secret
OpenAI API key</code></pre>
<hr />
<h4 id="ec2-배포-2-ssh-key-파일-생성">EC2 배포-2. SSH key 파일 생성</h4>
<pre><code class="language-bash">mkdir -p ~/.ssh
echo &quot;$EC2_SSH_KEY&quot; &gt; ~/.ssh/ec2_key
chmod 600 ~/.ssh/ec2_key</code></pre>
<p>GitHub Actions Runner는 매번 새로 생성되는 임시 서버다. 따라서 EC2 접속용 SSH key 파일이 기본적으로 존재하지 않는다.</p>
<p>그래서 GitHub Secrets에 저장해둔 <code>EC2_SSH_KEY</code> 값을 꺼내서 파일로 만든다.</p>
<pre><code class="language-bash">echo &quot;$EC2_SSH_KEY&quot; &gt; ~/.ssh/ec2_key</code></pre>
<p>이후 SSH key 권한을 제한한다.</p>
<pre><code class="language-bash">chmod 600 ~/.ssh/ec2_key</code></pre>
<p>SSH private key는 권한이 너무 열려 있으면 SSH 클라이언트가 보안상 사용을 거부할 수 있다.</p>
<p><code>600</code> 권한은 다음 의미다.</p>
<pre><code class="language-text">소유자만 읽기/쓰기 가능
다른 사용자 접근 불가</code></pre>
<hr />
<h4 id="ec2-배포-3-ec2-ssh-접속">EC2 배포-3. EC2 SSH 접속</h4>
<pre><code class="language-bash">ssh -i ~/.ssh/ec2_key -o StrictHostKeyChecking=no &quot;$EC2_USER@$EC2_HOST&quot; &quot;
  ...
&quot;</code></pre>
<p>이 명령은 GitHub Actions Runner에서 EC2로 SSH 접속을 수행한다.</p>
<p>예를 들어 Secrets 값이 다음과 같다면</p>
<pre><code class="language-text">EC2_USER=ubuntu
EC2_HOST=13.125.xxx.xxx</code></pre>
<p>실제 명령은 다음과 비슷하게 동작한다.</p>
<pre><code class="language-bash">ssh -i ~/.ssh/ec2_key ubuntu@13.125.xxx.xxx</code></pre>
<p><code>-i ~/.ssh/ec2_key</code>는 사용할 private key 파일을 지정하는 옵션이다.</p>
<pre><code class="language-bash">-o StrictHostKeyChecking=no</code></pre>
<p>이 옵션은 처음 접속하는 서버의 host key 확인 절차를 생략한다.</p>
<p>초기 자동 배포 환경에서는 편리하지만, 보안적으로는 개선 여지가 있다. 실제 운영 환경에서는 EC2 host key를 <code>known_hosts</code>에 등록하고 검증하는 방식이 더 안전하다.</p>
<hr />
<h4 id="ec2-배포-4-ec2-내부에서-실행되는-명령어">EC2 배포-4. EC2 내부에서 실행되는 명령어</h4>
<p>SSH 접속 이후 아래 명령들이 EC2 내부에서 실행된다.</p>
<pre><code class="language-bash">cd ~/solvesync &amp;&amp;
echo '$GHCR_PAT' | docker login ghcr.io -u '$GHCR_USERNAME' --password-stdin &amp;&amp;
docker compose pull app &amp;&amp;
docker compose up -d</code></pre>
<p>중요한 점은 이 명령들이 GitHub Actions Runner가 아니라 EC2 서버 안에서 실행된다는 것이다.</p>
<pre><code class="language-text">GitHub Actions Runner
→ SSH 접속 명령 실행

EC2
→ cd ~/solvesync
→ docker login ghcr.io
→ docker compose pull app
→ docker compose up -d</code></pre>
<hr />
<h4 id="ec2-배포-5-cd-solvesync">EC2 배포-5. <code>cd ~/solvesync</code></h4>
<pre><code class="language-bash">cd ~/solvesync</code></pre>
<p>EC2 내부의 배포 디렉토리로 이동한다.</p>
<p>이 디렉토리에는 <code>docker-compose.yml</code>, <code>application.yml</code>, <code>.env</code> 등의 파일이 있어야 한다.</p>
<pre><code class="language-text">~/solvesync
├── docker-compose.yml
├── application.yml
└── .env</code></pre>
<p>GitHub Actions는 이 디렉토리에서 Docker Compose 명령을 실행한다.</p>
<hr />
<h4 id="ec2-배포-6-ghcr-로그인">EC2 배포-6. GHCR 로그인</h4>
<pre><code class="language-bash">echo '$GHCR_PAT' | docker login ghcr.io -u '$GHCR_USERNAME' --password-stdin</code></pre>
<p>EC2에서 GHCR에 로그인하는 명령어다.</p>
<p>GHCR 이미지가 private이면 인증 없이 pull할 수 없다. 따라서 EC2가 이미지를 pull하기 전에 GHCR 로그인이 필요하다.</p>
<p><code>--password-stdin</code>을 사용한 이유는 토큰을 명령어 인자에 직접 노출하지 않기 위해서다.</p>
<hr />
<h4 id="ec2-배포-7-최신-app-이미지-pull">EC2 배포-7. 최신 app 이미지 pull</h4>
<pre><code class="language-bash">docker compose pull app</code></pre>
<p><code>docker-compose.yml</code>에 정의된 <code>app</code> 서비스의 이미지를 최신 버전으로 pull한다.</p>
<p>예를 들어 Compose 파일에 다음 설정이 있다면</p>
<pre><code class="language-yaml">services:
  app:
    image: ghcr.io/solvesyncproject/solve_sync_spring_server:latest</code></pre>
<p>이 명령은 GHCR에서 다음 이미지를 가져온다.</p>
<pre><code class="language-text">ghcr.io/solvesyncproject/solve_sync_spring_server:latest</code></pre>
<p>여기서 <code>app</code>만 pull하기 때문에 MySQL, RabbitMQ, Dozzle 이미지를 매번 다시 가져오지는 않는다.</p>
<hr />
<h4 id="ec2-배포-8-docker-compose-재실행">EC2 배포-8. Docker Compose 재실행</h4>
<pre><code class="language-bash">docker compose up -d</code></pre>
<p>Docker Compose에 정의된 서비스들을 백그라운드에서 실행한다.</p>
<p>이미 컨테이너가 실행 중이고, <code>app</code> 이미지가 새로 pull되었다면 기존 app 컨테이너를 새 이미지 기준으로 교체한다.</p>
<p>대략 다음과 같은 일이 일어난다.</p>
<pre><code class="language-text">기존 solvesync-app 컨테이너 확인
  ↓
새로운 latest 이미지 존재 확인
  ↓
기존 app 컨테이너 중지
  ↓
새 이미지로 app 컨테이너 재생성
  ↓
MySQL, RabbitMQ 볼륨은 유지
  ↓
Spring Boot 애플리케이션 재시작</code></pre>
<p><code>-d</code> 옵션은 detached mode를 의미한다. 즉, 컨테이너를 백그라운드에서 실행한다.</p>
<hr />