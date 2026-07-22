<h1 id="dockerfile-작성법">Dockerfile 작성법</h1>
<p>Spring Boot 애플리케이션을 Docker 이미지로 만들기 위해 프로젝트 루트에 <code>Dockerfile</code>을 작성했다.</p>
<pre><code class="language-dockerfile">FROM eclipse-temurin:17-jre

WORKDIR /app

ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar

EXPOSE 8080

ENTRYPOINT [&quot;java&quot;, &quot;-jar&quot;, &quot;app.jar&quot;]</code></pre>
<p>이 Dockerfile은 GitHub Actions에서 빌드된 jar 파일을 컨테이너 내부로 복사하고, 컨테이너 실행 시 <code>java -jar app.jar</code> 명령으로 Spring Boot 애플리케이션을 실행하는 역할을 한다.</p>
<ul>
<li>GHCR에 push할 이미지를 구성할 때 사용됨.</li>
</ul>
<hr />
<h2 id="라인별-설명">라인별 설명</h2>
<h3 id="dockerfile-작성법-1">Dockerfile 작성법-1</h3>
<pre><code class="language-dockerfile">FROM eclipse-temurin:17-jre</code></pre>
<p>이 줄은 Docker 이미지의 기반 이미지를 지정한다.</p>
<p><code>eclipse-temurin:17-jre</code>는 Java 17 실행 환경을 포함한 이미지다. 여기서 중요한 점은 <code>jre</code>를 사용했다는 것이다.</p>
<p>Java 애플리케이션을 빌드하려면 JDK가 필요하지만, 이미 GitHub Actions에서 <code>bootJar</code>를 통해 jar 파일을 생성한다. 따라서 Docker 이미지 안에서는 Java 코드를 컴파일할 필요가 없다. 이미 만들어진 jar 파일을 실행하기만 하면 된다.</p>
<p>그래서 역할이 다음처럼 나뉜다.</p>
<pre><code class="language-text">GitHub Actions
→ Java 코드를 컴파일하고 테스트하고 jar를 생성해야 함
→ JDK 필요

Docker Container
→ 이미 만들어진 jar 파일을 실행만 하면 됨
→ JRE면 충분</code></pre>
<p>따라서 Docker 이미지에는 JDK가 아닌 JRE 기반 이미지를 사용했다.</p>
<hr />
<h3 id="dockerfile-작성법-2">Dockerfile 작성법-2</h3>
<pre><code class="language-dockerfile">WORKDIR /app</code></pre>
<p>컨테이너 내부의 작업 디렉토리를 <code>/app</code>으로 지정한다.</p>
<p>이후 실행되는 명령어들은 기본적으로 <code>/app</code> 디렉토리를 기준으로 동작한다.</p>
<p>즉, 아래 명령어는</p>
<pre><code class="language-dockerfile">COPY ${JAR_FILE} app.jar</code></pre>
<p>실제로는 다음과 같은 의미가 된다.</p>
<pre><code class="language-text">GitHub Actions에서 생성된 jar 파일을
컨테이너 내부 /app/app.jar 위치에 복사한다.</code></pre>
<p>컨테이너 내부 구조는 대략 다음과 같다.</p>
<pre><code class="language-text">/app
 └── app.jar</code></pre>
<hr />
<h3 id="dockerfile-작성법-3">Dockerfile 작성법-3</h3>
<pre><code class="language-dockerfile">ARG JAR_FILE=build/libs/*.jar</code></pre>
<p><code>ARG</code>는 Docker 이미지를 빌드할 때 사용하는 빌드 시점 변수다.</p>
<p>Spring Boot 프로젝트에서 다음 명령을 실행하면</p>
<pre><code class="language-bash">./gradlew bootJar</code></pre>
<p>보통 아래와 같은 jar 파일이 생성된다.</p>
<pre><code class="language-text">build/libs/solve-sync-spring-server-0.0.1-SNAPSHOT.jar</code></pre>
<p>하지만 jar 파일 이름은 프로젝트명, 버전, Gradle 설정에 따라 달라질 수 있다. 그래서 정확한 파일명을 고정하지 않고 <code>build/libs/*.jar</code>로 지정했다.</p>
<p>즉, 이 설정은 다음 의미다.</p>
<pre><code class="language-text">Docker 이미지를 빌드할 때 build/libs 디렉토리 안의 jar 파일을 사용한다.</code></pre>
<hr />
<h3 id="dockerfile-작성법-4">Dockerfile 작성법-4</h3>
<pre><code class="language-dockerfile">COPY ${JAR_FILE} app.jar</code></pre>
<p>이 줄은 빌드된 jar 파일을 Docker 이미지 내부로 복사한다.</p>
<p>예를 들어 GitHub Actions에서 다음 파일이 생성되었다고 하자.</p>
<pre><code class="language-text">build/libs/solve-sync-spring-server-0.0.1-SNAPSHOT.jar</code></pre>
<p>Dockerfile의 <code>COPY</code> 명령에 의해 이 파일은 컨테이너 내부에서 다음 이름으로 복사된다.</p>
<pre><code class="language-text">/app/app.jar</code></pre>
<p>원래 jar 파일 이름이 길더라도 컨테이너 내부에서는 항상 <code>app.jar</code>라는 이름으로 실행할 수 있게 된다.</p>
<hr />
<h3 id="dockerfile-작성법-5">Dockerfile 작성법-5</h3>
<pre><code class="language-dockerfile">EXPOSE 8080</code></pre>
<p>이 줄은 컨테이너가 8080 포트를 사용한다는 것을 명시한다.</p>
<p>Spring Boot의 기본 포트가 보통 8080이므로, 컨테이너 내부에서 애플리케이션이 8080 포트로 실행된다는 의미를 나타낸다.</p>
<p>다만 <code>EXPOSE 8080</code>만으로 외부 접속이 가능해지는 것은 아니다.</p>
<p>실제로 EC2의 포트와 컨테이너 내부 포트를 연결하는 것은 <code>docker-compose.yml</code>의 <code>ports</code> 설정이다.</p>
<p>예를 들어 다음 설정이 있다면</p>
<pre><code class="language-yaml">ports:
  - &quot;127.0.0.1:8080:8080&quot;</code></pre>
<p>이는 다음 의미다.</p>
<pre><code class="language-text">EC2 내부의 127.0.0.1:8080
→ 컨테이너 내부의 8080 포트</code></pre>
<p>즉, 컨테이너 내부에서는 8080으로 실행되지만, 외부 공개 여부는 Compose 또는 Nginx 설정에 의해 결정된다.</p>
<hr />
<h3 id="dockerfile-작성법-6">Dockerfile 작성법-6</h3>
<pre><code class="language-dockerfile">ENTRYPOINT [&quot;java&quot;, &quot;-jar&quot;, &quot;app.jar&quot;]</code></pre>
<p>컨테이너가 실행될 때 수행할 기본 명령어를 지정한다.</p>
<p>이 Docker 이미지로 컨테이너가 실행되면 내부적으로 다음 명령이 실행된다.</p>
<pre><code class="language-bash">java -jar app.jar</code></pre>
<p>즉, Spring Boot 애플리케이션이 실행된다.</p>
<p>정리하면 이 Dockerfile은 다음과 같은 역할을 한다.</p>
<pre><code class="language-text">1. Java 17 실행 환경을 준비한다.
2. 컨테이너 내부 작업 디렉토리를 /app으로 지정한다.
3. GitHub Actions에서 생성된 jar 파일을 app.jar로 복사한다.
4. 8080 포트를 사용한다고 명시한다.
5. 컨테이너 실행 시 java -jar app.jar를 실행한다.</code></pre>
<hr />