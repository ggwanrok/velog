<p>Spring Boot 백엔드를 가장 크게 보면 결국 하나의 요청이 아래 흐름을 따라 이동한다.</p>
<pre><code class="language-text">사용자
  │
  │ HTTP Request
  ▼
Tomcat
  │
  │ HttpServletRequest / HttpServletResponse
  ▼
DispatcherServlet
  │
  ├─ HandlerMapping
  │      &quot;어느 Controller 메서드가 처리하지?&quot;
  │
  ├─ HandlerAdapter
  │      &quot;이 Controller 메서드를 어떻게 호출하지?&quot;
  │
  ▼
Controller
  │
  │ DTO
  ▼
Service
  │
  │ Entity
  ▼
Repository
  │
  ▼
Spring Data JPA
  │
  ▼
JPA
  │
  ▼
Hibernate
  │
  ▼
JDBC
  │
  ▼
DB</code></pre>
<p>그리고 이 과정에서 사용하는 객체들을 뒤에서 생성하고 연결하고 관리하는 것이 <strong>Spring IoC Container</strong>다.</p>
<pre><code class="language-text">Spring IoC Container
       │
       ├─ Bean 생성
       ├─ Bean 저장
       ├─ DI
       ├─ 생명주기 관리
       │
       └─ 필요한 Bean은 Proxy로 감싸기
                 │
                 ├─ @Transactional
                 ├─ @Async
                 ├─ @Validated
                 └─ AOP</code></pre>
<p>처음 Spring Boot를 배우면 <code>@RestController</code>, <code>@Service</code>, <code>JpaRepository</code> 같은 어노테이션부터 보게 된다.</p>
<p>하지만 각각의 기술을 따로 외우는 것보다,</p>
<blockquote>
<p><strong>HTTP 요청 하나가 들어와 DB에 도달하고 다시 HTTP 응답으로 나가기까지 Spring이 어떤 일을 대신해주는가</strong></p>
</blockquote>
<p>를 기준으로 이해하면 Spring Boot의 여러 기능들이 하나의 구조로 연결되기 시작한다.</p>
<p>이번 글부터 이 흐름을 하나씩 따라가 보려고 한다.</p>
<p>첫 번째는 Spring Boot 애플리케이션의 출발점인 <strong>REST API</strong>다.</p>
<hr />
<h1 id="rest-api">REST API</h1>
<p>Spring Boot를 배우기 전에 REST를 배우는 이유가 있다.</p>
<p>Spring Boot를 이용해 우리가 주로 만드는 것이</p>
<blockquote>
<p><strong>HTTP를 통해 클라이언트와 데이터를 주고받는 REST API 서버</strong></p>
</blockquote>
<p>이기 때문이다.</p>
<p>우선 가장 기본적인 웹 애플리케이션 구조를 보면 다음과 같다.</p>
<pre><code class="language-text">Client
  │
  │ HTTP
  ▼
Web Server
  │
  ▼
WAS
  │
  ▼
DB</code></pre>
<p>Client는 Browser나 Mobile Application처럼 사용자가 접근하는 영역이다.</p>
<p>Frontend에서는 보통 다음과 같은 기술이 사용된다.</p>
<pre><code class="language-text">HTML
CSS
JavaScript

Vue
React
Angular</code></pre>
<p>반대로 서버에서는 요청을 처리하기 위한 애플리케이션이 동작한다.</p>
<pre><code class="language-text">Java        → Spring Boot
Python      → Django / FastAPI
JavaScript  → Node.js</code></pre>
<p>Spring Boot 역시 결국 <strong>클라이언트의 HTTP 요청을 받아 필요한 로직을 수행하고 결과를 HTTP 응답으로 돌려주는 서버 애플리케이션</strong>이다.</p>
<hr />
<h1 id="web-server와-was">Web Server와 WAS</h1>
<p>웹 서버 구조를 보다 보면 <strong>Web Server</strong>와 <strong>WAS</strong>라는 용어를 자주 만나게 된다.</p>
<p>둘의 가장 큰 차이는 무엇을 처리하느냐다.</p>
<pre><code class="language-text">Web Server
→ 정적인 데이터

WAS
→ 동적인 데이터</code></pre>
<p>예를 들어 사용자가 다음 파일을 요청했다고 생각해보자.</p>
<pre><code class="language-http">GET /logo.png</code></pre>
<p>이미 만들어져 있는 <code>logo.png</code> 파일을 찾아서 그대로 반환하면 된다.</p>
<pre><code class="language-text">Client
   ↓
Web Server
   ↓
logo.png 반환</code></pre>
<p>이런 작업에 특화된 것이 Web Server다.</p>
<p>대표적으로 다음과 같은 서버가 있다.</p>
<pre><code class="language-text">Apache
Nginx</code></pre>
<p>주로 처리하는 자원 역시 이미 만들어져 있는 정적 파일이다.</p>
<pre><code class="language-text">HTML
CSS
JavaScript
Image</code></pre>
<p>반대로 다음 요청은 조금 다르다.</p>
<pre><code class="language-http">GET /api/users/10</code></pre>
<p>단순히 파일 하나를 반환하는 것이 아니라 서버 내부 프로그램을 실행해야 한다.</p>
<pre><code class="language-text">요청 수신

→ User 조회 로직 실행
→ DB 조회
→ 결과 객체 생성
→ JSON 변환
→ 응답</code></pre>
<p>이처럼 <strong>비즈니스 로직을 실행해서 동적으로 결과를 만들어주는 서버</strong>가 WAS(Web Application Server)다.</p>
<p>Java 진영에서는 대표적으로 <strong>Tomcat</strong>이 있다.</p>
<pre><code class="language-text">Web Server
정적 Resource 반환
        │
        │
        └─ Nginx, Apache


WAS
Application 실행
        │
        │
        └─ Tomcat</code></pre>
<p>Spring Boot에서는 Tomcat이 내장되어 있기 때문에 별도의 WAS를 설치하지 않고도 애플리케이션을 실행할 수 있다.</p>
<pre><code class="language-bash">java -jar myapp.jar</code></pre>
<p>Spring Boot 애플리케이션이 실행되면서 내부 Tomcat도 같이 실행되고 HTTP 요청을 기다리게 된다.</p>
<hr />
<h1 id="frontend와-backend의-분리">Frontend와 Backend의 분리</h1>
<p>전통적인 웹 애플리케이션에서는 서버가 HTML까지 만들어 전달하는 경우가 많았다.</p>
<pre><code class="language-text">Browser
   ↓
Server
   ↓
HTML 생성
   ↓
Browser</code></pre>
<p>하지만 React나 Vue 같은 Frontend Framework를 사용하는 구조에서는 조금 다르다.</p>
<p>최초에는 HTML, JavaScript, CSS 같은 정적 Resource를 내려받고,</p>
<p>이후 데이터가 필요할 때 Backend API를 호출한다.</p>
<pre><code class="language-text">Browser
   │
   │ HTML / JS / CSS
   ▼
Frontend Application
   │
   │ HTTP Request
   ▼
Backend REST API
   │
   ▼
DB</code></pre>
<p>예를 들어 Vue나 React에서 다음 요청을 보낸다고 하자.</p>
<pre><code class="language-javascript">fetch(&quot;/api/users/10&quot;)</code></pre>
<p>Backend는 다음과 같은 JSON을 반환할 수 있다.</p>
<pre><code class="language-json">{
  &quot;id&quot;: 10,
  &quot;name&quot;: &quot;Alice&quot;
}</code></pre>
<p>Frontend는 이 데이터를 이용해 화면을 구성한다.</p>
<p>여기서 중요한 것은 <strong>Frontend와 Backend가 서로의 내부 구현을 알 필요가 없다는 것</strong>이다.</p>
<p>Frontend 입장에서는 Backend가</p>
<pre><code class="language-text">Java인지
Python인지

MySQL인지
PostgreSQL인지

JPA인지
MyBatis인지</code></pre>
<p>알 필요가 없다.</p>
<p>약속된 API로 데이터를 요청하고 약속된 형태의 응답만 받으면 된다.</p>
<p>이러한 Client와 Server의 역할 분리 역시 REST의 중요한 설계 원칙 중 하나다.</p>
<hr />
<h1 id="rest란">REST란?</h1>
<p>REST는</p>
<p><strong>Representational State Transfer</strong></p>
<p>의 약자다.</p>
<p>Roy Fielding이 웹 아키텍처를 설계하기 위한 원칙으로 제안한 개념이다.</p>
<p>REST에서는 웹을 수많은 <strong>Resource의 집합</strong>으로 바라본다.</p>
<p>예를 들어 서비스에 다음 데이터들이 있다고 하자.</p>
<pre><code class="language-text">User
Product
Order
Article
Comment</code></pre>
<p>REST에서는 이것들을 모두 하나의 <strong>Resource</strong>로 바라본다.</p>
<p>그리고 어떤 Resource를 대상으로 어떤 행동을 할 것인지를 HTTP를 이용해 표현한다.</p>
<p>핵심 개념을 간단하게 정리하면 다음과 같다.</p>
<pre><code class="language-text">Resource
→ 무엇을 다룰 것인가?

URI
→ 그 Resource를 어떻게 식별할 것인가?

HTTP Method
→ 그 Resource에 어떤 행동을 할 것인가?

Representation
→ 그 Resource를 어떤 형태로 주고받을 것인가?</code></pre>
<p>예를 들어 다음 요청을 보자.</p>
<pre><code class="language-http">GET /users/10</code></pre>
<p>이를 REST 관점으로 분해하면</p>
<pre><code class="language-text">User
→ Resource

/users/10
→ 10번 User를 식별하는 URI

GET
→ 조회

JSON
→ Response Representation</code></pre>
<p>이 된다.</p>
<hr />
<h2 id="resource">Resource</h2>
<p>REST에서 가장 먼저 생각해야 하는 것이 <strong>Resource</strong>다.</p>
<p>Resource는 서버가 제공하고 클라이언트가 조작할 수 있는 대상을 의미한다.</p>
<p>예를 들어</p>
<pre><code class="language-text">User
Product
Article
Order
Review
Image</code></pre>
<p>등이 Resource가 될 수 있다.</p>
<p>여기서 중요한 것은 REST API를 <strong>행동 중심이 아니라 자원 중심으로 설계한다는 것</strong>이다.</p>
<p>예를 들어 사용자 조회 기능을 만든다고 해서</p>
<pre><code class="language-text">getUser</code></pre>
<p>라는 동작 자체를 Resource로 생각하는 것이 아니다.</p>
<p>Resource는</p>
<pre><code class="language-text">User</code></pre>
<p>이고,</p>
<p>조회라는 행위는 HTTP Method가 담당한다.</p>
<hr />
<h3 id="uri는-resource를-식별한다">URI는 Resource를 식별한다</h3>
<p>Resource가 있다면 각각의 Resource를 구분할 방법이 필요하다.</p>
<p>REST에서는 이를 URI로 표현한다.</p>
<p>예를 들어</p>
<pre><code class="language-text">/users</code></pre>
<p>는 User Resource의 집합을 의미할 수 있고,</p>
<pre><code class="language-text">/users/10</code></pre>
<p>은 10번 User를 의미할 수 있다.</p>
<pre><code class="language-text">/users
     │
     └─ User Resource 전체

/users/10
         │
         └─ ID가 10인 User Resource</code></pre>
<p>여기서 REST API의 중요한 설계 규칙 하나가 나온다.</p>
<blockquote>
<p><strong>URI에는 가능하면 행위가 아니라 Resource를 표현한다.</strong></p>
</blockquote>
<p>그래서 다음과 같은 API는 REST스럽지 않다.</p>
<pre><code class="language-text">/createUser
/getUser
/updateUser
/deleteUser</code></pre>
<p>URI 자체에 이미 행동이 포함되어 있기 때문이다.</p>
<p>REST에서는 이를 다음과 같이 표현한다.</p>
<pre><code class="language-text">POST    /users
GET     /users/10
PUT     /users/10
PATCH   /users/10
DELETE  /users/10</code></pre>
<p>URI는 계속</p>
<pre><code class="language-text">/users
/users/10</code></pre>
<p>이라는 Resource를 가리킨다.</p>
<p>달라지는 것은 <strong>HTTP Method</strong>다.</p>
<p>그래서 REST API 설계에서 자주 사용하는 표현이 있다.</p>
<blockquote>
<p><strong>URI는 명사, 행위는 HTTP Method.</strong></p>
</blockquote>
<hr />
<h2 id="http-method">HTTP Method</h2>
<p>URI로 Resource를 지정했다면 이제 그 Resource에 어떤 행동을 할지 결정해야 한다.</p>
<p>REST에서는 HTTP Method를 이용한다.</p>
<p>대표적으로 CRUD와 다음과 같이 대응된다.</p>
<table>
<thead>
<tr>
<th>기능</th>
<th>HTTP Method</th>
<th>예시</th>
</tr>
</thead>
<tbody><tr>
<td>생성</td>
<td>POST</td>
<td><code>POST /users</code></td>
</tr>
<tr>
<td>조회</td>
<td>GET</td>
<td><code>GET /users/10</code></td>
</tr>
<tr>
<td>전체 수정</td>
<td>PUT</td>
<td><code>PUT /users/10</code></td>
</tr>
<tr>
<td>일부 수정</td>
<td>PATCH</td>
<td><code>PATCH /users/10</code></td>
</tr>
<tr>
<td>삭제</td>
<td>DELETE</td>
<td><code>DELETE /users/10</code></td>
</tr>
</tbody></table>
<hr />
<h3 id="get">GET</h3>
<p>Resource를 조회한다.</p>
<pre><code class="language-http">GET /users</code></pre>
<p>전체 사용자 목록을 조회하거나,</p>
<pre><code class="language-http">GET /users/10</code></pre>
<p>특정 사용자를 조회한다.</p>
<hr />
<h3 id="post">POST</h3>
<p>새로운 Resource를 생성할 때 주로 사용한다.</p>
<pre><code class="language-http">POST /users
Content-Type: application/json</code></pre>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;
}</code></pre>
<p>서버에서는 전달받은 데이터를 이용해 새로운 User를 생성한다.</p>
<hr />
<h3 id="put과-patch">PUT과 PATCH</h3>
<p>둘 다 Resource를 수정할 때 사용한다.</p>
<p>다만 의미에 차이가 있다.</p>
<pre><code class="language-text">PUT
→ Resource 전체 수정

PATCH
→ Resource 일부 수정</code></pre>
<p>예를 들어 다음 User가 있다고 하자.</p>
<pre><code class="language-json">{
  &quot;id&quot;: 10,
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;
}</code></pre>
<p>이름만 변경한다면 PATCH를 사용할 수 있다.</p>
<pre><code class="language-http">PATCH /users/10</code></pre>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Bob&quot;
}</code></pre>
<p>반대로 Resource 전체를 새로운 표현으로 교체하는 의미라면 PUT을 사용한다.</p>
<hr />
<h3 id="delete">DELETE</h3>
<p>Resource를 삭제한다.</p>
<pre><code class="language-http">DELETE /users/10</code></pre>
<p>즉 REST에서는</p>
<pre><code class="language-text">URI
→ 대상

HTTP Method
→ 행동</code></pre>
<p>의 역할을 명확히 분리한다.</p>
<hr />
<h2 id="representation">Representation</h2>
<p>REST의 이름에는 <strong>Representational</strong>이라는 단어가 들어간다.</p>
<p>서버에 존재하는 Resource 자체가 네트워크를 통해 이동하는 것은 아니다.</p>
<p>예를 들어 서버 내부에 Java 객체가 있다고 생각해보자.</p>
<pre><code class="language-java">User user = new User(10L, &quot;Alice&quot;);</code></pre>
<p>이 Java 객체 자체가 Browser로 전달되는 것은 아니다.</p>
<p>클라이언트가 이해할 수 있는 형태로 표현해서 전달한다.</p>
<p>대표적으로 JSON을 많이 사용한다.</p>
<pre><code class="language-json">{
  &quot;id&quot;: 10,
  &quot;name&quot;: &quot;Alice&quot;
}</code></pre>
<p>이것이 <strong>Representation</strong>이다.</p>
<p>Representation은 JSON만 가능한 것은 아니다.</p>
<p>자료에서는 다음과 같은 형태를 소개한다.</p>
<pre><code class="language-text">JSON
XML
YAML
HTML
Text
Image
Binary
PDF</code></pre>
<p>Spring Boot REST API에서는 일반적으로 JSON을 가장 많이 사용한다.</p>
<p>나중에 Spring MVC를 살펴보면 이 과정 역시 Spring이 대신 처리해준다는 것을 알 수 있다.</p>
<pre><code class="language-text">Java Object
     │
     ▼
HTTPMessageConverter
     │
     ▼
JSON
     │
     ▼
HTTP Response</code></pre>
<p>개발자는 Controller에서 Java 객체를 반환하지만 실제 HTTP Response에서는 JSON Representation이 전달되는 것이다.</p>
<hr />
<h2 id="제약조건">제약조건</h2>
<p>REST를 처음 배우면 보통</p>
<pre><code class="language-text">GET
POST
PUT
DELETE</code></pre>
<p>정도로 이해하기 쉽다.</p>
<p>하지만 REST는 단순한 API URL 작성법이 아니라 <strong>웹 시스템을 설계하기 위한 아키텍처 스타일</strong>이다.</p>
<p>REST에는 다음 6개의 제약 조건이 있다.</p>
<pre><code class="language-text">1. Client-Server
2. Stateless
3. Cacheable
4. Uniform Interface
5. Layered System
6. Code on Demand (선택사항)</code></pre>
<hr />
<h3 id="client-server">Client-Server</h3>
<p>Client와 Server의 역할을 분리한다.</p>
<pre><code class="language-text">Client
→ UI
→ 사용자 입력
→ 화면 표현

Server
→ 비즈니스 로직
→ 데이터 처리
→ DB 접근</code></pre>
<p>두 영역은 API라는 계약을 기준으로 통신한다.</p>
<p>예를 들어 Client는</p>
<pre><code class="language-http">GET /users/10</code></pre>
<p>이라고 요청하고,</p>
<p>Server가</p>
<pre><code class="language-json">{
  &quot;id&quot;: 10,
  &quot;name&quot;: &quot;Alice&quot;
}</code></pre>
<p>를 반환하기만 하면 된다.</p>
<p>Server 내부에서</p>
<pre><code class="language-text">Spring Boot를 사용하든
Node.js를 사용하든

MySQL을 사용하든
PostgreSQL을 사용하든</code></pre>
<p>Client는 알 필요가 없다.</p>
<p>반대로 서버 역시 Client가 React인지 Vue인지 알 필요가 없다.</p>
<p>이렇게 역할을 분리함으로써 Frontend와 Backend를 독립적으로 개발하고 변경하기 쉬워진다.</p>
<hr />
<h3 id="stateless">Stateless</h3>
<p>REST에서 굉장히 중요한 원칙이다.</p>
<p>Stateless는 말 그대로</p>
<blockquote>
<p><strong>서버가 클라이언트의 이전 요청 상태를 기억하지 않는 것</strong></p>
</blockquote>
<p>을 의미한다.</p>
<p>예를 들어</p>
<pre><code class="language-text">Request A
Request B
Request C</code></pre>
<p>가 있다고 하자.</p>
<p>서버가</p>
<pre><code class="language-text">&quot;A 요청 때 이 사용자가 로그인했으니까
B 요청에서는 그걸 기억해서 처리해야겠다.&quot;</code></pre>
<p>처럼 이전 요청의 상태에 의존하지 않는다는 것이다.</p>
<p>각 Request는 자신의 요청을 처리하는 데 필요한 정보를 가지고 있어야 한다.</p>
<p>예를 들어 인증이 필요한 API라면</p>
<pre><code class="language-http">GET /api/users/me
Authorization: Bearer eyJ...</code></pre>
<p>처럼 현재 요청에 인증 정보를 포함시킨다.</p>
<p>그러면 서버는</p>
<pre><code class="language-text">&quot;이 사용자가 이전 요청에서 로그인했었나?&quot;</code></pre>
<p>를 기억하는 대신</p>
<pre><code class="language-text">&quot;이번 Request가 가진 인증 정보가 유효한가?&quot;</code></pre>
<p>를 확인한다.</p>
<hr />
<h4 id="stateless와-서버확장">Stateless와 서버확장</h4>
<p>Stateless의 장점은 서버를 여러 대로 확장할 때 더욱 명확해진다.</p>
<pre><code class="language-text">Client
   │
   ▼
Load Balancer
   │
   ├── Server A
   ├── Server B
   └── Server C</code></pre>
<p>만약 사용자 상태가 Server A 내부에만 저장되어 있다면 문제가 생길 수 있다.</p>
<pre><code class="language-text">첫 번째 Request
→ Server A

두 번째 Request
→ Server B</code></pre>
<p>Server B는 Server A가 가지고 있는 상태를 모른다.</p>
<p>반대로 각각의 요청이 필요한 정보를 가지고 있다면</p>
<pre><code class="language-text">Request
+ Authorization
+ 필요한 Parameter</code></pre>
<p>어느 서버가 받아도 동일하게 처리할 수 있다.</p>
<pre><code class="language-text">Server A  가능
Server B  가능
Server C  가능</code></pre>
<p>그래서 Stateless 구조는 <strong>Scale-out에 유리하다.</strong></p>
<hr />
<h3 id="cacheable">Cacheable</h3>
<p>모든 요청을 항상 서버까지 전달해야 하는 것은 아니다.</p>
<p>변경 가능성이 낮은 데이터라면 일정 시간 동안 기존 응답을 재사용할 수 있다.</p>
<p>HTTP에서는 이를 위한 캐시 기능을 제공한다.</p>
<p>예를 들어 서버가 다음과 같이 응답할 수 있다.</p>
<pre><code class="language-http">HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=600</code></pre>
<p>이는 해당 응답을 일정 시간 동안 캐시해서 사용할 수 있음을 나타낸다.</p>
<pre><code class="language-text">첫 번째 요청
Client → Server

응답 Cache 저장

두 번째 요청
Client → Cache</code></pre>
<p>적절한 캐시를 사용하면</p>
<pre><code class="language-text">네트워크 요청 감소
서버 부하 감소
응답 속도 증가</code></pre>
<p>효과를 얻을 수 있다.</p>
<p>REST에서는 서버 응답이 캐시 가능한지 여부가 명확하게 표현되어야 한다.</p>
<hr />
<h3 id="uniform-interface">Uniform Interface</h3>
<p>REST API는 서비스 전체에서 일관된 인터페이스를 사용해야 한다.</p>
<p>예를 들어 User API가</p>
<pre><code class="language-text">GET /users/10</code></pre>
<p>인데 Product API는</p>
<pre><code class="language-text">/getProduct?id=10</code></pre>
<p>처럼 전혀 다른 규칙으로 만들어져 있다면 API를 사용하는 입장에서 구조를 예측하기 어렵다.</p>
<p>REST에서는 Resource와 HTTP 표준을 중심으로 일관성 있는 인터페이스를 만들려고 한다.</p>
<p>대표적인 규칙은 다음과 같다.</p>
<h4 id="resource는-명사로-표현한다">Resource는 명사로 표현한다.</h4>
<pre><code class="language-text">/users
/products
/orders</code></pre>
<h4 id="행위는-http-method로-표현한다">행위는 HTTP Method로 표현한다.</h4>
<pre><code class="language-text">GET     /products
POST    /products
PUT     /products/10
DELETE  /products/10</code></pre>
<h4 id="resource-사이-관계도-uri로-표현할-수-있다">Resource 사이 관계도 URI로 표현할 수 있다.</h4>
<pre><code class="language-text">/users/10/orders</code></pre>
<p>이는</p>
<blockquote>
<p><strong>10번 User의 Order 목록</strong></p>
</blockquote>
<p>이라는 관계를 자연스럽게 표현한다.</p>
<p>좀 더 구체적으로는</p>
<pre><code class="language-text">/users/10/orders/3</code></pre>
<p>처럼 표현할 수도 있다.</p>
<hr />
<h4 id="query-parameter">Query Parameter</h4>
<p>Resource 자체가 달라지는 것이 아니라 <strong>조회 조건만 달라진다면 Query Parameter</strong>를 사용할 수 있다.</p>
<p>예를 들어</p>
<pre><code class="language-http">GET /users?age=20</code></pre>
<p>은 새로운 종류의 Resource를 의미하는 것이 아니라</p>
<pre><code class="language-text">users라는 동일한 Resource 집합 중
age가 20인 데이터</code></pre>
<p>를 조회한다는 의미다.</p>
<p>정렬 역시 마찬가지다.</p>
<pre><code class="language-http">GET /users?sort=name</code></pre>
<p>여러 조건을 함께 사용할 수도 있다.</p>
<pre><code class="language-http">GET /users?age=20&amp;sort=name</code></pre>
<p>일반적으로</p>
<pre><code class="language-text">Path
→ Resource 식별

Query Parameter
→ 검색 / 필터 / 정렬 조건</code></pre>
<p>정도로 생각하면 이해하기 쉽다.</p>
<hr />
<h4 id="http-status-code">HTTP Status Code</h4>
<p>REST API는 요청 처리 결과도 HTTP가 제공하는 표준을 활용한다.</p>
<p>대표적으로 다음과 같은 상태 코드가 있다.</p>
<pre><code class="language-text">200 OK
→ 요청 성공

201 Created
→ Resource 생성 성공

400 Bad Request
→ 잘못된 요청

404 Not Found
→ Resource를 찾을 수 없음</code></pre>
<p>예를 들어 새로운 User를 성공적으로 생성했다면</p>
<pre><code class="language-http">HTTP/1.1 201 Created
Location: /users/10
Content-Type: application/json</code></pre>
<p>처럼 응답할 수 있다.</p>
<p>HTTP 메시지 자체만 보더라도</p>
<pre><code class="language-text">요청이 성공했는가?
Resource가 생성되었는가?
어디에 생성되었는가?
어떤 형태의 데이터인가?</code></pre>
<p>를 어느 정도 파악할 수 있게 만드는 것이다.</p>
<hr />
<h3 id="layered-system">Layered System</h3>
<p>REST에서 Client는 Server 내부가 어떤 계층으로 구성되어 있는지 알 필요가 없다.</p>
<p>실제 서비스는 다음과 같이 구성될 수도 있다.</p>
<pre><code class="language-text">Client
   │
   ▼
Load Balancer
   │
   ▼
API Gateway
   │
   ▼
Authentication Server
   │
   ▼
Backend Server
   │
   ▼
Database</code></pre>
<p>하지만 Client는 내부에</p>
<pre><code class="language-text">Load Balancer가 있는지
Gateway가 있는지
Backend Server가 몇 개인지</code></pre>
<p>알 필요가 없다.</p>
<p>그저 하나의 API Endpoint에 요청하면 된다.</p>
<p>이런 구조 덕분에 서버 내부에는 필요에 따라</p>
<pre><code class="language-text">인증
인가
캐싱
로드밸런싱
프록시
모니터링</code></pre>
<p>같은 계층을 추가할 수 있다.</p>
<hr />
<h4 id="monolith와-msa에서도-동일하다">Monolith와 MSA에서도 동일하다</h4>
<p>Layered System이라는 개념은 Monolith와 MSA에도 동일하게 적용된다.</p>
<p>Monolith라면 Backend 하나 안에 여러 기능이 들어갈 수 있다.</p>
<pre><code class="language-text">Client
   │
   ▼
Spring Boot
 ├─ User
 ├─ Order
 ├─ Payment
 └─ Product</code></pre>
<p>MSA라면 서비스를 각각 분리할 수 있다.</p>
<pre><code class="language-text">Client
   │
   ▼
API Gateway
   │
   ├─ User Service
   ├─ Order Service
   ├─ Payment Service
   └─ Product Service</code></pre>
<p>하지만 Client의 입장에서는 내부 서비스 구조를 직접 알아야 할 필요가 없다.</p>
<p>그리고 기억할만한 것은 <strong>MSA가 Monolith보다 무조건 좋은 구조는 아니라는 것</strong>이다.</p>
<p>작은 규모의 프로젝트라면 Monolith가</p>
<pre><code class="language-text">배포가 단순하고
디버깅하기 쉽고
트랜잭션 관리가 쉽고
운영 복잡도가 낮다.</code></pre>
<p>라는 명확한 장점이 있다.</p>
<p>서비스 규모와 요구사항에 따라 적합한 아키텍처를 선택하는 것이 중요하다.</p>
<hr />
<h3 id="code-on-demand">Code on Demand</h3>
<p>REST의 6가지 원칙 중 선택적인 원칙이다.</p>
<p>서버가 클라이언트에게 단순 데이터가 아니라 <strong>실행 가능한 코드</strong>를 내려주는 방식이다.</p>
<p>웹에서는 JavaScript가 대표적인 예가 될 수 있다.</p>
<pre><code class="language-text">Server
   │
   │ JavaScript
   ▼
Browser
   │
   └─ 코드 실행</code></pre>
<p>이를 통해 서버가 내려주는 코드에 따라 클라이언트 기능을 동적으로 확장할 수 있다.</p>
<hr />
<h1 id="정리">정리</h1>
<p>REST를 단순히</p>
<pre><code class="language-text">GET
POST
PUT
DELETE</code></pre>
<p>를 사용하는 방식으로만 이해하면 이후 Spring Boot의 여러 기능이 따로 놀기 시작한다.</p>
<p>REST의 핵심은 <strong>Resource를 중심으로 HTTP 인터페이스를 설계하는 것</strong>이다.</p>
<pre><code class="language-text">Resource
   │
   ├─ URI로 식별하고
   │
   ├─ HTTP Method로 행동을 표현하고
   │
   └─ JSON 등의 Representation으로 전달한다.</code></pre>
<p>그리고 Spring Boot는 바로 이 HTTP 기반 API 서버를 쉽게 만들기 위해 수많은 작업을 대신 처리해준다.</p>
<p>앞으로 우리가 살펴볼 것은 그 내부다.</p>
<pre><code class="language-text">HTTP Request
     │
     ▼
Tomcat
     │
     ▼
DispatcherServlet
     │
     ├─ HandlerMapping
     └─ HandlerAdapter
     │
     ▼
Controller
     │
     ▼
Service
     │
     ▼
Repository
     │
     ▼
JPA
     │
     ▼
DB</code></pre>
<p>그리고 그 모든 객체의 생성과 연결을 뒤에서 담당하는</p>
<pre><code class="language-text">Spring IoC Container</code></pre>
<p>까지 이해하면,</p>
<p><code>@RestController</code>, <code>@Service</code>, <code>@Transactional</code>, <code>JpaRepository</code> 같은 Spring의 기능들이 더 이상 서로 다른 기술이 아니라 <strong>하나의 요청을 처리하기 위해 연결된 구조</strong>로 보이기 시작한다.</p>
<p>다음에는 HTTP Request가 Spring Boot에 들어온 이후, <strong>Tomcat과 Servlet, DispatcherServlet을 거쳐 Controller가 호출되는 과정</strong>을 따라가 볼 수 있다.</p>