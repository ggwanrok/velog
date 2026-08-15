<p>지난 글에서는 REST API를 통해 클라이언트와 서버가 어떤 방식으로 통신하는지 살펴봤다.</p>
<p>이번에는 한 단계 안쪽으로 들어가 보자.</p>
<p>클라이언트가 다음과 같은 요청을 보냈다고 하자.</p>
<pre><code class="language-http">GET /api/users/10</code></pre>
<p>Spring Boot에서는 보통 이런 코드를 작성한다.</p>
<pre><code class="language-java">@GetMapping(&quot;/users/{id}&quot;)
public UserResponse getUser(@PathVariable Long id) {
    return userService.getUser(id);
}</code></pre>
<p>코드만 보면 자연스럽다.</p>
<p>하지만 조금만 생각해보면 이상하다.</p>
<p>브라우저는 Java의 <code>getUser()</code>라는 메서드를 모른다.</p>
<p>Tomcat도 우리가 만든</p>
<pre><code class="language-java">@GetMapping(&quot;/users/{id}&quot;)</code></pre>
<p>이라는 Spring Annotation의 의미를 직접 알고 있는 것은 아니다.</p>
<p>그런데 어떻게</p>
<pre><code class="language-text">GET /api/users/10</code></pre>
<p>이라는 <strong>HTTP Request</strong>가</p>
<pre><code class="language-java">getUser(10L)</code></pre>
<p>이라는 <strong>Java Method 호출</strong>로 연결되는 걸까?</p>
<p>이 과정의 중심에 <strong>Spring MVC</strong>가 있다.</p>
<p>Spring Boot 백엔드 전체 흐름을 먼저 보면 다음과 같다.</p>
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
  │      &quot;어느 Controller Method가 처리하지?&quot;
  │
  ├─ HandlerAdapter
  │      &quot;이 Method를 어떻게 실행하지?&quot;
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
<p>이번 글에서는 HTTP Request 하나가 이 구조를 어떻게 통과하는지 따라가 본다.</p>
<hr />
<h1 id="요청이-들어오기-전에">요청이 들어오기 전에</h1>
<p>HTTP Request가 들어오는 순간 갑자기 <code>UserController</code>와 <code>UserService</code> 객체가 만들어지는 것은 아니다.</p>
<p>Spring Boot 애플리케이션이 시작될 때 Spring은 먼저 자신이 사용할 객체들을 찾아 생성하고 관리할 준비를 한다.</p>
<p>여기서 먼저 알아야 하는 개념이 <strong>Bean</strong>이다.</p>
<hr />
<h1 id="bean이란">Bean이란?</h1>
<p>일반적인 Java에서는 필요한 객체를 개발자가 직접 만든다.</p>
<pre><code class="language-java">UserService userService = new UserService();</code></pre>
<p>즉 객체의</p>
<pre><code class="language-text">생성
사용
관리</code></pre>
<p>를 개발자가 직접 담당한다.</p>
<p>Spring에서는 조금 다르다.</p>
<pre><code class="language-java">@Service
public class UserService {
}</code></pre>
<p>이처럼 Spring이 관리 대상으로 인식한 객체는 개발자가 직접 <code>new</code> 하지 않아도 Spring이 생성하고 관리할 수 있다.</p>
<p>이렇게</p>
<blockquote>
<p><strong>Spring IoC Container가 생성하고 관리하는 객체를 Bean이라고 한다.</strong></p>
</blockquote>
<p>간단하게 비교하면 다음과 같다.</p>
<pre><code class="language-text">일반 Java

개발자
  │
  │ new
  ▼
UserService


Spring

Spring IoC Container
  │
  │ 생성 및 관리
  ▼
UserService Bean</code></pre>
<p>Spring이 Bean을 관리한다는 것은 단순히 객체를 하나 만들어 보관한다는 의미만은 아니다.</p>
<p>필요한 객체끼리 연결할 수도 있다.</p>
<p>예를 들어 다음 Controller가 있다고 하자.</p>
<pre><code class="language-java">@RestController
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }
}</code></pre>
<p>우리는 다음과 같은 코드를 직접 작성하지 않았다.</p>
<pre><code class="language-java">UserService userService = new UserService();
UserController controller = new UserController(userService);</code></pre>
<p>대신 Spring이 관리하고 있는 <code>UserService Bean</code>을 <code>UserController</code>가 필요로 하는 위치에 연결해준다.</p>
<pre><code class="language-text">Spring IoC Container

┌────────────────────────────┐
│                            │
│  UserService Bean          │
│         │                  │
│         │ 주입             │
│         ▼                  │
│  UserController Bean       │
│                            │
└────────────────────────────┘</code></pre>
<p>이러한 의존성 연결이 이후 살펴볼 <strong>DI(Dependency Injection)</strong>다.</p>
<p>지금은 일단</p>
<pre><code class="language-text">Bean
=
Spring이 생성하고 관리하는 객체</code></pre>
<p>정도로 잡으면 충분하다.</p>
<p>그렇다면 새로운 질문이 생긴다.</p>
<blockquote>
<p>Spring은 우리가 작성한 수많은 클래스 중에서 무엇을 Bean으로 만들어야 하는지 어떻게 알아낼까?</p>
</blockquote>
<p>정답은 <strong>Component Scan</strong>이다.</p>
<hr />
<h1 id="component-scan">Component Scan</h1>
<p>Component Scan은 Spring이 지정된 Package를 탐색하면서 <strong>Bean으로 관리해야 할 클래스들을 자동으로 찾는 기능</strong>이다.</p>
<p>대표적으로 다음 Annotation들이 대상이 된다.</p>
<pre><code class="language-text">@Component
@Controller
@RestController
@Service
@Repository
@Configuration</code></pre>
<p>예를 들어 다음 클래스가 있다고 하자.</p>
<pre><code class="language-java">@Service
public class UserService {
}</code></pre>
<p>Spring은 애플리케이션을 시작하면서 Package를 탐색하다가 <code>@Service</code>가 붙은 클래스를 발견한다.</p>
<pre><code class="language-text">Package 탐색
      │
      ▼
@Service 발견
      │
      ▼
UserService를 Bean 대상으로 인식
      │
      ▼
Spring IoC Container에서 관리</code></pre>
<p>즉 Component Scan을 한 문장으로 정리하면</p>
<blockquote>
<p><strong>개발자가 작성한 클래스 중 Spring이 관리해야 하는 대상을 찾아 Bean으로 등록하기 위한 기능</strong></p>
</blockquote>
<p>이라고 볼 수 있다.</p>
<hr />
<h2 id="springbootapplication">@SpringBootApplication</h2>
<p>Spring Boot 프로젝트의 시작 클래스에는 보통 다음 Annotation이 붙어 있다.</p>
<pre><code class="language-java">@SpringBootApplication
public class MyappApplication {

    public static void main(String[] args) {
        SpringApplication.run(MyappApplication.class, args);
    }
}</code></pre>
<p><code>@SpringBootApplication</code>은 Spring Boot 실행에 필요한 여러 기능을 묶은 Meta Annotation이다.</p>
<p>큰 틀에서 보면 다음 역할들이 포함되어 있다.</p>
<pre><code class="language-text">@SpringBootApplication
        │
        ├─ @Configuration
        │
        ├─ @EnableAutoConfiguration
        │
        └─ @ComponentScan</code></pre>
<h3 id="configuration">@Configuration</h3>
<p>Spring 설정 정보를 정의하는 클래스임을 나타낸다.</p>
<p>Java 코드 기반으로 Bean을 구성할 수 있다.</p>
<h3 id="enableautoconfiguration">@EnableAutoConfiguration</h3>
<p>프로젝트에 포함된 Library와 환경을 기반으로 필요한 Spring 설정을 자동으로 구성한다.</p>
<p>예를 들어 Spring Web 관련 Dependency가 있다면 Web Application을 실행하기 위한 여러 설정을 Spring Boot가 자동으로 준비한다.</p>
<h3 id="componentscan">@ComponentScan</h3>
<p>개발자가 작성한 Spring Component를 탐색하고 Bean 대상으로 등록한다.</p>
<hr />
<h2 id="component-scan의-범위">Component Scan의 범위</h2>
<p>Component Scan은 기본적으로</p>
<pre><code class="language-java">@SpringBootApplication</code></pre>
<p>이 선언된 클래스의 Package를 기준으로 <strong>하위 Package 전체</strong>를 탐색한다.</p>
<p>다음과 같은 구조를 생각해보자.</p>
<pre><code class="language-text">com.sk.skala.myapp
│
├─ MyappApplication.java
│
├─ controller
│   └─ UserController.java
│
├─ service
│   └─ UserService.java
│
└─ repository
    └─ UserRepository.java</code></pre>
<p><code>MyappApplication</code>이</p>
<pre><code class="language-text">com.sk.skala.myapp</code></pre>
<p>에 있으므로</p>
<pre><code class="language-text">controller
service
repository</code></pre>
<p>도 모두 탐색 범위에 포함된다.</p>
<p>따라서 각각의</p>
<pre><code class="language-text">@RestController
@Service
@Repository</code></pre>
<p>등을 Spring이 찾아낼 수 있다.</p>
<p>반대로 Component Scan 범위 밖에 클래스를 만들어버리면 Annotation을 붙여도 자동 등록되지 않을 수 있다.</p>
<p>필요한 경우 범위를 직접 지정할 수도 있다.</p>
<pre><code class="language-java">@SpringBootApplication(
    scanBasePackages = {
        &quot;com.skala.stock&quot;,
        &quot;com.sk.common&quot;
    }
)
public class StockApiApplication {
}</code></pre>
<p>Spring Boot 프로젝트에서 Application 클래스를 보통 상위 Package에 두는 이유 중 하나가 바로 Component Scan 때문이다.</p>
<hr />
<h1 id="spring-mvc">Spring MVC</h1>
<p>필요한 Bean들이 준비됐으니 이제 HTTP Request가 들어왔을 때의 흐름을 살펴보자.</p>
<p>먼저 MVC는</p>
<blockquote>
<p><strong>Model - View - Controller</strong></p>
</blockquote>
<p>의 약자다.</p>
<p>Spring만의 개념은 아니며 각 역할을 분리하기 위한 전통적인 Architecture Pattern이다.</p>
<p>기본 구조는 다음과 같다.</p>
<pre><code class="language-text">Client
  │
  │ Request
  ▼
Controller
  │
  ▼
Model
  │
  ▼
View
  │
  │ Response
  ▼
Client</code></pre>
<p>역할을 나누면 다음과 같다.</p>
<pre><code class="language-text">Controller
→ 요청을 받고 전체 흐름을 제어

Model
→ 데이터와 비즈니스 로직

View
→ 사용자에게 보여줄 결과</code></pre>
<p>Spring은 이 MVC 구조를 Web Application 개발에 맞게 Framework로 구현한 것이 <strong>Spring MVC</strong>다.</p>
<hr />
<h2 id="전통적인-spring-mvc">전통적인 Spring MVC</h2>
<p>전통적인 MVC Web Application에서는 서버가 HTML까지 만들어 반환하는 경우가 많았다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Controller
public class UserController {

    @GetMapping(&quot;/users&quot;)
    public String users(Model model) {

        model.addAttribute(&quot;name&quot;, &quot;Alice&quot;);

        return &quot;users&quot;;
    }
}</code></pre>
<p>여기서</p>
<pre><code class="language-java">return &quot;users&quot;;</code></pre>
<p>는 단순한 문자열 응답이 아니다.</p>
<p>Spring은 이를 View 이름으로 해석한다.</p>
<pre><code class="language-text">Controller
    │
    │ &quot;users&quot;
    ▼
ViewResolver
    │
    ▼
Thymeleaf / JSP
    │
    ▼
HTML</code></pre>
<p>즉 Controller가 데이터를 준비하고 ViewResolver가 적절한 View를 찾아 HTML을 만들어 응답하는 구조다.</p>
<hr />
<h2 id="rest-api-기반-spring-mvc">REST API 기반 Spring MVC</h2>
<p>하지만 Spring Boot로 REST API 서버를 만들 때는 일반적으로 HTML을 반환하지 않는다.</p>
<pre><code class="language-java">@RestController
public class UserController {

    @GetMapping(&quot;/users/1&quot;)
    public User getUser() {
        return user;
    }
}</code></pre>
<p><code>User</code> 객체를 반환하면 Spring은 이를 View 이름으로 해석하지 않는다.</p>
<p>HTTP Response Body에 들어갈 데이터로 처리한다.</p>
<p>개념적으로</p>
<pre><code class="language-text">@RestController

=

@Controller
+
@ResponseBody</code></pre>
<p>로 이해할 수 있다.</p>
<p>그리고 Java Object는 JSON 같은 형태로 변환된다.</p>
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
<p>지난 글에서 살펴본 REST의 <strong>Representation</strong>이 실제 Spring MVC 안에서는 이런 방식으로 만들어진다.</p>
<p>따라서 크게 보면</p>
<pre><code class="language-text">@Controller
     │
     ▼
ViewResolver
     │
     ▼
HTML</code></pre>
<p>과</p>
<pre><code class="language-text">@RestController
     │
     ▼
HTTPMessageConverter
     │
     ▼
JSON</code></pre>
<p>의 차이라고 볼 수 있다.</p>
<hr />
<h1 id="http-request-처리과정">HTTP Request 처리과정</h1>
<p>애플리케이션이 실행된 상태에서 다음 요청이 들어왔다고 하자.</p>
<pre><code class="language-http">GET /api/users/10</code></pre>
<p>가장 먼저 요청을 받는 것은 <code>UserController</code>가 아니다.</p>
<p>Spring MVC 기반 Spring Boot Web Application에서는 기본적으로 <strong>Tomcat</strong>과 같은 Servlet Container가 요청을 받는다.</p>
<hr />
<h2 id="tomcat">Tomcat</h2>
<p>Spring Boot Web Application을 실행하면 흔히 다음과 같은 로그를 볼 수 있다.</p>
<pre><code class="language-text">Tomcat started on port 8080</code></pre>
<p>Tomcat은 지정된 Port를 열고 Client의 연결을 기다린다.</p>
<pre><code class="language-text">Client
   │
   │ TCP
   ▼
Tomcat :8080</code></pre>
<p>HTTP는 TCP 위에서 전달된다.</p>
<p>따라서 Tomcat은 TCP Connection을 통해 전달된 데이터를 HTTP Protocol에 맞게 해석한다.</p>
<pre><code class="language-text">TCP Data
   │
   ▼
HTTP Parsing</code></pre>
<p>그리고 HTTP Request와 Response를 Java 환경에서 다룰 수 있도록 Servlet API 객체를 준비한다.</p>
<p>대표적인 것이</p>
<pre><code class="language-text">HttpServletRequest
HttpServletResponse</code></pre>
<p>다.</p>
<hr />
<h3 id="httpservletrequest">HttpServletRequest</h3>
<p>다음 HTTP Request를 생각해보자.</p>
<pre><code class="language-http">GET /api/users/10?detail=true HTTP/1.1
Host: localhost:8080
Authorization: Bearer abc...</code></pre>
<p>Request 안에는 여러 정보가 존재한다.</p>
<pre><code class="language-text">HTTP Method
Path
Query Parameter
Header
Cookie
Body</code></pre>
<p>Tomcat은 HTTP Message를 Parsing해서 Spring이 사용할 수 있는 <code>HttpServletRequest</code> 형태로 전달한다.</p>
<pre><code class="language-text">HTTP Request
     │
     ▼
Tomcat
     │
     ▼
HttpServletRequest</code></pre>
<p>즉 이후 Spring MVC가</p>
<pre><code class="language-text">GET
/api/users/10
detail=true
Authorization</code></pre>
<p>같은 정보를 Java 환경에서 다룰 수 있게 된다.</p>
<hr />
<h3 id="httpservletresponse">HttpServletResponse</h3>
<p>반대로 Client에게 반환할 HTTP Response를 표현하는 객체가 <code>HttpServletResponse</code>다.</p>
<p>Response에는 대표적으로</p>
<pre><code class="language-text">HTTP Status
Header
Body</code></pre>
<p>등이 들어간다.</p>
<p>전체 흐름은 다음과 같다.</p>
<pre><code class="language-text">Application
     │
     ▼
HttpServletResponse
     │
     ▼
Tomcat
     │
     ▼
HTTP Response
     │
     ▼
Client</code></pre>
<hr />
<h3 id="tomcat은-getmapping을-모른다">Tomcat은 @GetMapping을 모른다</h3>
<p>여기서 중요한 경계가 하나 있다.</p>
<p>Tomcat은</p>
<pre><code class="language-text">TCP
HTTP
Servlet</code></pre>
<p>영역을 담당한다.</p>
<p>하지만</p>
<pre><code class="language-java">@GetMapping(&quot;/users/{id}&quot;)</code></pre>
<p>이라는 Spring MVC Annotation의 의미를 직접 처리하는 것은 아니다.</p>
<p>그래서 Tomcat이 받은 Request는 Spring MVC의 핵심 Servlet에게 전달된다.</p>
<p>바로 <strong>DispatcherServlet</strong>이다.</p>
<hr />
<h2 id="dispatcherservlet">DispatcherServlet</h2>
<p><code>DispatcherServlet</code>은 Spring MVC의 <strong>Front Controller</strong>다.</p>
<p>Front Controller란 여러 Controller 앞에 하나의 공통 진입점을 두는 구조다.</p>
<p>예를 들어 다음 Controller들이 있다고 하자.</p>
<pre><code class="language-text">UserController
OrderController
ProductController</code></pre>
<p>각 Controller가 Client Request를 직접 받는 것이 아니다.</p>
<p>Spring MVC에서는 모든 요청을 먼저 DispatcherServlet이 받는다.</p>
<pre><code class="language-text">                    ┌─ UserController
                    │
Client ──▶ DispatcherServlet ─── OrderController
                    │
                    └─ ProductController</code></pre>
<p>즉 DispatcherServlet은</p>
<blockquote>
<p><strong>Spring MVC의 모든 HTTP Request를 받아 적절한 Controller로 연결해주는 중앙 진입점</strong></p>
</blockquote>
<p>이라고 볼 수 있다.</p>
<p>현재까지 흐름은 다음과 같다.</p>
<pre><code class="language-text">Client
  │
  │ HTTP Request
  ▼
Tomcat
  │
  ├─ TCP 처리
  ├─ HTTP Parsing
  ├─ HttpServletRequest
  └─ HttpServletResponse
  │
  ▼
DispatcherServlet</code></pre>
<p>그런데 DispatcherServlet이 다음 Request를 받았다고 하자.</p>
<pre><code class="language-http">GET /api/users/10</code></pre>
<p>아직 어떤 Controller Method를 실행해야 하는지는 모른다.</p>
<p>이를 찾는 역할이 <strong>HandlerMapping</strong>이다.</p>
<hr />
<h2 id="handlermapping">HandlerMapping</h2>
<p>HandlerMapping은 현재 Request를 처리할 <strong>Handler</strong>를 찾는다.</p>
<p>Spring MVC에서 일반적인 Handler는 Controller Method라고 이해하면 된다.</p>
<p>다음 Controller가 있다고 하자.</p>
<pre><code class="language-java">@RestController
@RequestMapping(&quot;/api&quot;)
public class UserController {

    @GetMapping(&quot;/users/{id}&quot;)
    public UserResponse getUser(
            @PathVariable Long id
    ) {
        ...
    }
}</code></pre>
<p>Spring 입장에서는 다음 Mapping 관계가 존재한다.</p>
<pre><code class="language-text">GET /api/users/{id}

        ↓

UserController.getUser()</code></pre>
<p>실제 Request가 들어오면 HandlerMapping은 등록된 Mapping 정보를 확인한다.</p>
<pre><code class="language-text">GET /api/users/10
        │
        ▼
HandlerMapping
        │
        ▼
UserController.getUser(...)</code></pre>
<p>대표적으로 <code>RequestMappingHandlerMapping</code>이 이러한 역할을 한다.</p>
<p>즉 HandlerMapping의 역할을 한 문장으로 정리하면</p>
<blockquote>
<p><strong>누가 이 Request를 처리할 것인가?</strong></p>
</blockquote>
<p>이다.</p>
<hr />
<h2 id="handleradapter">HandlerAdapter</h2>
<p>Handler를 찾았다고 바로 Controller Method를 실행하는 것은 아니다.</p>
<p>DispatcherServlet이 모든 Handler의 구체적인 호출 방법까지 직접 알고 있게 만들면 DispatcherServlet이 너무 많은 구현에 의존하게 된다.</p>
<p>그래서 Handler 실행을 별도의 Adapter에게 맡긴다.</p>
<p>바로 <strong>HandlerAdapter</strong>다.</p>
<pre><code class="language-text">DispatcherServlet
       │
       │ &quot;누가 처리하지?&quot;
       ▼
HandlerMapping
       │
       │ UserController.getUser()
       ▼
DispatcherServlet
       │
       │ &quot;어떻게 실행하지?&quot;
       ▼
HandlerAdapter
       │
       ▼
Controller Method</code></pre>
<p>둘을 비교하면 명확하다.</p>
<pre><code class="language-text">HandlerMapping
→ 누구를 실행할 것인가?

HandlerAdapter
→ 그 Handler를 어떻게 실행할 것인가?</code></pre>
<p>간단하게는</p>
<pre><code class="language-text">Mapping
→ 찾기

Adapter
→ 실행 연결</code></pre>
<p>이라고 기억할 수 있다.</p>
<hr />
<h2 id="이제-controller로">이제 Controller로</h2>
<p>HandlerMapping이 요청을 처리할 Controller Method를 찾았고, HandlerAdapter가 해당 Handler를 실행할 준비를 했다.</p>
<p>지금까지의 흐름을 다시 보면 다음과 같다.</p>
<pre><code class="language-text">GET /api/users/10
        │
        ▼
Tomcat
        │
        ▼
DispatcherServlet
        │
        ▼
HandlerMapping
        │
        │ 어떤 Method?
        ▼
UserController.getUser()
        │
        ▼
HandlerAdapter
        │
        │ Method 실행
        ▼
Controller</code></pre>
<p>이제 드디어 우리가 직접 작성한 코드가 실행되는 영역으로 들어온다.</p>
<hr />
<h2 id="controller">Controller</h2>
<p>Controller는 <strong>HTTP Request와 Application 내부 로직을 연결하는 진입점</strong>이다.</p>
<p>예를 들어 다음과 같은 Controller가 있다고 하자.</p>
<pre><code class="language-java">@RestController
@RequestMapping(&quot;/api&quot;)
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping(&quot;/users/{id}&quot;)
    public UserResponse getUser(
            @PathVariable Long id
    ) {
        return userService.getUser(id);
    }
}</code></pre>
<p>Client가</p>
<pre><code class="language-http">GET /api/users/10</code></pre>
<p>을 요청하면 Spring MVC가 이 Request를 위 Method와 연결하고,</p>
<pre><code class="language-java">getUser(10L)</code></pre>
<p>형태로 실행할 수 있도록 처리한다.</p>
<p>Controller는 결국</p>
<pre><code class="language-text">HTTP 세계
   │
   ▼
Controller
   │
   ▼
Application 내부</code></pre>
<p>사이의 경계라고 볼 수 있다.</p>
<p>Controller에서는 주로 다음과 같은 일을 담당한다.</p>
<pre><code class="language-text">요청 URL 연결
HTTP Method 연결
Request 데이터 수신
입력값 검증
Service 호출
Response 반환
HTTP Status 결정</code></pre>
<p>반대로 실제 비즈니스 규칙이나 DB 접근 로직까지 Controller에 몰아넣는 것은 피하는 것이 좋다.</p>
<pre><code class="language-text">Controller
→ HTTP 요청 / 응답

Service
→ 비즈니스 로직

Repository
→ 데이터 접근</code></pre>
<p>처럼 각 계층의 책임을 나누는 것이 기본적인 구조다.</p>
<hr />
<h3 id="restcontroller">@RestController</h3>
<p>REST API를 만들 때 가장 흔하게 사용하는 것이 <code>@RestController</code>다.</p>
<pre><code class="language-java">@RestController
public class UserController {
}</code></pre>
<p>개념적으로는</p>
<pre><code class="language-text">@RestController

=

@Controller
+
@ResponseBody</code></pre>
<p>라고 이해할 수 있다.</p>
<p><code>@Controller</code>가 기본적으로 View를 찾는 MVC Controller라면,</p>
<p><code>@ResponseBody</code>가 붙은 반환값은 View 이름으로 해석하지 않고 <strong>HTTP Response Body에 작성할 데이터</strong>로 처리한다.</p>
<p>따라서</p>
<pre><code class="language-java">@GetMapping(&quot;/users/10&quot;)
public UserResponse getUser() {
    return response;
}</code></pre>
<p>처럼 Java Object를 반환하면</p>
<pre><code class="language-text">Java Object
     │
     ▼
HTTPMessageConverter
     │
     ▼
JSON
     │
     ▼
HTTP Response Body</code></pre>
<p>형태로 변환된다.</p>
<p>즉 REST API에서 Controller의 반환 객체가 지난 글에서 살펴본 <strong>Representation</strong>으로 변환되는 지점이다.</p>
<hr />
<h3 id="http-request와-controller-method-연결하기">HTTP Request와 Controller Method 연결하기</h3>
<p>Controller 안에는 여러 Method가 존재할 수 있다.</p>
<pre><code class="language-java">@RestController
@RequestMapping(&quot;/api&quot;)
public class UserController {

    @GetMapping(&quot;/users&quot;)
    public List&lt;UserResponse&gt; getUsers() {
        ...
    }

    @GetMapping(&quot;/users/{id}&quot;)
    public UserResponse getUser(Long id) {
        ...
    }

    @PostMapping(&quot;/users&quot;)
    public UserResponse createUser(...) {
        ...
    }
}</code></pre>
<p>Spring MVC는 HTTP Method와 URL을 이용해 어떤 Method를 실행할 것인지 구분한다.</p>
<p>REST API의 HTTP Method는 Spring에서는 다음 Annotation으로 표현할 수 있다.</p>
<pre><code class="language-text">GET
→ @GetMapping

POST
→ @PostMapping

PUT
→ @PutMapping

PATCH
→ @PatchMapping

DELETE
→ @DeleteMapping</code></pre>
<p>예를 들어</p>
<pre><code class="language-java">@GetMapping(&quot;/users&quot;)</code></pre>
<p>은</p>
<pre><code class="language-http">GET /users</code></pre>
<p>와 연결된다.</p>
<pre><code class="language-java">@PostMapping(&quot;/users&quot;)</code></pre>
<p>은</p>
<pre><code class="language-http">POST /users</code></pre>
<p>와 연결된다.</p>
<p>지난 글에서 REST를 다음처럼 정리했다.</p>
<pre><code class="language-text">URI
→ Resource

HTTP Method
→ Resource에 대한 행위</code></pre>
<p>Spring MVC에서는 이 HTTP Method와 URI를 Mapping Annotation으로 코드에 표현하는 것이다.</p>
<hr />
<h4 id="requestmapping">@RequestMapping</h4>
<p><code>@RequestMapping</code>은 HTTP Request를 Controller와 연결하는 가장 기본적인 Mapping Annotation이다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@RequestMapping(
    value = &quot;/users&quot;,
    method = RequestMethod.GET
)</code></pre>
<p>은</p>
<pre><code class="language-java">@GetMapping(&quot;/users&quot;)</code></pre>
<p>과 같은 Request를 처리할 수 있다.</p>
<p>실제로는 클래스 단위로 공통 Path를 지정할 때도 많이 사용한다.</p>
<pre><code class="language-java">@RestController
@RequestMapping(&quot;/api&quot;)
public class UserController {

    @GetMapping(&quot;/users&quot;)
    public List&lt;UserResponse&gt; getUsers() {
        ...
    }
}</code></pre>
<p>이 경우 실제 Endpoint는</p>
<pre><code class="language-text">@RequestMapping(&quot;/api&quot;)
+
@GetMapping(&quot;/users&quot;)

=

GET /api/users</code></pre>
<p>가 된다.</p>
<p>즉 클래스에는 공통 영역을,</p>
<pre><code class="language-java">@RequestMapping(&quot;/api&quot;)</code></pre>
<p>각 Method에는 실제 Resource를</p>
<pre><code class="language-java">@GetMapping(&quot;/users&quot;)</code></pre>
<p>지정하는 방식이다.</p>
<hr />
<h3 id="http-데이터를-java-parameter로-어떻게-받을까">HTTP 데이터를 Java Parameter로 어떻게 받을까?</h3>
<p>여기서 다음 코드를 다시 보자.</p>
<pre><code class="language-java">@GetMapping(&quot;/users/{id}&quot;)
public UserResponse getUser(
        @PathVariable Long id
) {
    return userService.getUser(id);
}</code></pre>
<p>Client가 실제로 보내는 것은 Java의 <code>Long</code> 타입이 아니다.</p>
<pre><code class="language-http">GET /api/users/10</code></pre>
<p>단지 HTTP Message 안에 <code>10</code>이라는 값이 들어 있을 뿐이다.</p>
<p>그런데 Controller Method가 실행될 때는</p>
<pre><code class="language-java">Long id = 10L;</code></pre>
<p>처럼 Java에서 사용할 수 있는 값이 들어온다.</p>
<p>즉 Spring MVC가 HTTP Request의 데이터를 읽어 <strong>Controller Method의 Parameter에 연결해주는 과정</strong>이 필요하다.</p>
<p>이것을 <strong>Parameter Binding</strong>이라고 한다.</p>
<pre><code class="language-text">HTTP Request

/api/users/10
      │
      ▼
Spring MVC
      │
      ▼
Controller

Long id = 10L</code></pre>
<p>개발자는 HTTP Request를 직접 Parsing하지 않고 Annotation을 이용해서 어떤 값을 받을지만 선언하면 된다.</p>
<hr />
<h4 id="pathvariable">@PathVariable</h4>
<p>URL Path 자체에 포함된 값을 받는다.</p>
<pre><code class="language-java">@GetMapping(&quot;/users/{id}&quot;)
public UserResponse getUser(
        @PathVariable Long id
) {
    ...
}</code></pre>
<p>다음 Request가 들어왔다고 하자.</p>
<pre><code class="language-http">GET /users/100</code></pre>
<p>Spring은</p>
<pre><code class="language-text">/users/{id}
        │
        ▼
       100
        │
        ▼
Long id = 100</code></pre>
<p>으로 연결한다.</p>
<p>보통 특정 Resource를 식별하는 값에 많이 사용한다.</p>
<pre><code class="language-text">/users/10

/orders/20

/products/30</code></pre>
<p>REST에서 Path를 통해 특정 Resource를 식별했던 것과 자연스럽게 연결된다.</p>
<hr />
<h4 id="requestparam">@RequestParam</h4>
<p>Query Parameter를 받기 위해 사용한다.</p>
<pre><code class="language-java">@GetMapping(&quot;/users&quot;)
public List&lt;UserResponse&gt; getUsers(
        @RequestParam String name
) {
    ...
}</code></pre>
<p>다음 Request가 들어오면</p>
<pre><code class="language-http">GET /users?name=alice</code></pre>
<p>Spring이</p>
<pre><code class="language-text">name=alice
     │
     ▼
String name = &quot;alice&quot;</code></pre>
<p>로 연결한다.</p>
<p>Query Parameter는 보통</p>
<pre><code class="language-text">검색
필터
정렬
Paging</code></pre>
<p>같은 조건을 전달하는 데 사용한다.</p>
<p>예를 들어</p>
<pre><code class="language-http">GET /users?age=20&amp;sort=name</code></pre>
<p>처럼 사용할 수 있다.</p>
<p>필수가 아닌 Parameter나 기본값도 지정할 수 있다.</p>
<pre><code class="language-java">@RequestParam(
    required = false,
    defaultValue = &quot;all&quot;
)
String type</code></pre>
<hr />
<h4 id="requestbody">@RequestBody</h4>
<p>POST나 PUT처럼 데이터를 전달해야 하는 Request에서는 HTTP Body가 많이 사용된다.</p>
<p>예를 들어 다음과 같은 요청이 들어온다고 하자.</p>
<pre><code class="language-http">POST /users
Content-Type: application/json</code></pre>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;
}</code></pre>
<p>Controller에서는 다음처럼 받을 수 있다.</p>
<pre><code class="language-java">@PostMapping(&quot;/users&quot;)
public UserResponse createUser(
        @RequestBody CreateUserRequest request
) {
    ...
}</code></pre>
<p>Spring은 JSON을 Java Object로 변환한다.</p>
<pre><code class="language-text">HTTP Request Body

{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;
}

        │
        ▼

HTTPMessageConverter

        │
        ▼

CreateUserRequest</code></pre>
<p>따라서 Controller에서는 이미 Java Object가 된 상태로 데이터를 사용할 수 있다.</p>
<pre><code class="language-java">request.getName();
request.getEmail();</code></pre>
<p>Request와 Response를 함께 보면 구조가 대칭적이다.</p>
<pre><code class="language-text">Request

JSON
 │
 ▼
HTTPMessageConverter
 │
 ▼
Java Object</code></pre>
<pre><code class="language-text">Response

Java Object
 │
 ▼
HTTPMessageConverter
 │
 ▼
JSON</code></pre>
<hr />
<h4 id="그-밖의-request-데이터">그 밖의 Request 데이터</h4>
<p>HTTP Header를 받아야 하는 경우에는</p>
<pre><code class="language-java">@RequestHeader</code></pre>
<p>를 사용할 수 있다.</p>
<pre><code class="language-java">@GetMapping(&quot;/users/me&quot;)
public UserResponse getMe(
        @RequestHeader(&quot;Authorization&quot;) String token
) {
    ...
}</code></pre>
<pre><code class="language-http">Authorization: Bearer abc123</code></pre>
<p>이라는 Header가</p>
<pre><code class="language-java">String token</code></pre>
<p>에 전달된다.</p>
<p>Cookie 역시</p>
<pre><code class="language-java">@CookieValue</code></pre>
<p>를 이용해 받을 수 있다.</p>
<p>즉 Spring MVC가 제공하는 Binding 기능 덕분에 개발자가 매번</p>
<pre><code class="language-text">HttpServletRequest

→ URL 직접 분석
→ Query String 직접 분석
→ Header 직접 분석
→ Body 직접 Parsing</code></pre>
<p>할 필요가 없다.</p>
<p>Controller Method에서 <strong>필요한 데이터가 무엇인지 선언하기만 하면 된다.</strong></p>
<p>대표적인 Binding Annotation을 정리하면 다음과 같다.</p>
<table>
<thead>
<tr>
<th>Annotation</th>
<th>가져오는 값</th>
</tr>
</thead>
<tbody><tr>
<td><code>@PathVariable</code></td>
<td>URL Path</td>
</tr>
<tr>
<td><code>@RequestParam</code></td>
<td>Query Parameter</td>
</tr>
<tr>
<td><code>@RequestBody</code></td>
<td>HTTP Body</td>
</tr>
<tr>
<td><code>@RequestHeader</code></td>
<td>HTTP Header</td>
</tr>
<tr>
<td><code>@CookieValue</code></td>
<td>Cookie</td>
</tr>
<tr>
<td><code>@ModelAttribute</code></td>
<td>Query/Form 데이터를 객체에 Binding</td>
</tr>
</tbody></table>
<p>모두 외우기보다는</p>
<pre><code class="language-text">HTTP의 어느 부분에서 데이터를 가져오는가?</code></pre>
<p>를 기준으로 이해하는 것이 좋다.</p>
<hr />
<h3 id="spring의-controller-method-실행-방법">Spring의 Controller Method 실행 방법</h3>
<p>여기까지 오면 한 가지 질문이 남는다.</p>
<p>우리는 코드 어디에서도 다음과 같이 직접 Controller Method를 호출하지 않았다.</p>
<pre><code class="language-java">userController.getUser(10L);</code></pre>
<p>그런데 Spring은 Request가 들어오면 적절한 Controller와 Method를 찾아 실제로 실행한다.</p>
<p>이 과정에서 Java의 <strong>Reflection</strong>이라는 기능이 활용된다.</p>
<p>개발자는 본인이 짠 코드에 대해서 어디서 뭘 사용해야하는지 파악하고 있지만,
스프링은 그런걸 모르기에, 해당 정보를 인지할 수 있게 해주는 작업이 <strong>Reflection</strong>이다.</p>
<p>Reflection은 간단하게 말하면</p>
<blockquote>
<p><strong>실행 중인 Java 프로그램이 클래스나 메서드의 정보를 확인하고 동적으로 다룰 수 있도록 제공하는 기능</strong></p>
</blockquote>
<p>이다.</p>
<p>일반적으로 Java Method는 코드에 직접 작성해서 호출한다.</p>
<pre><code class="language-java">userController.getUser(10L);</code></pre>
<p>Reflection을 이용하면 실행 중에 Method 정보를 가져와 호출할 수도 있다.</p>
<p>개념적인 형태는 다음과 같다.</p>
<pre><code class="language-java">Method method = ...;

method.invoke(controller, arguments);</code></pre>
<p>Spring MVC 역시 미리 파악해둔 Controller와 Method 정보를 이용해 적절한 Method를 실행한다.</p>
<pre><code class="language-text">HTTP Request
      │
      ▼
HandlerMapping
      │
      ▼
Controller Method 정보
      │
      ▼
HandlerAdapter
      │
      ├─ Parameter 준비
      │
      └─ Method 실행
      │
      ▼
Controller</code></pre>
<p>여기서 Reflection의 내부 동작까지 알지 못하더라도,</p>
<p>Spring MVC 관점에서</p>
<blockquote>
<p><strong>Spring이 실행 시점에 Controller Method 정보를 알고 있기 때문에 Request에 맞는 Method를 직접 호출할 수 있다.</strong></p>
</blockquote>
<p>정도로 이해해도 충분하다.</p>
<p>Reflection은 이후 Spring의 Annotation, IoC, DI 등의 내부 동작을 이해할 때 다시 등장한다.</p>
<hr />
<h2 id="controller에서-service로">Controller에서 Service로</h2>
<p>Controller는 Client의 HTTP Request를 Application 내부로 연결하는 계층이다.</p>
<p>그렇다고 실제 업무 로직까지 전부 Controller에 작성하는 것은 좋지 않다.</p>
<p>예를 들어 사용자 정보를 수정하는 API가 있다고 하자.</p>
<pre><code class="language-java">@PutMapping(&quot;/users/{id}&quot;)
public UserResponse updateUser(
        @PathVariable Long id,
        @RequestBody UpdateUserRequest request
) {

    // 사용자가 존재하는지 확인
    // 수정 가능한 상태인지 확인
    // 전달받은 데이터 검증
    // 사용자 정보 변경
    // 저장
    // 응답 생성
}</code></pre>
<p>기능이 단순할 때는 큰 문제가 없어 보인다.</p>
<p>하지만 Application이 커질수록 Controller가</p>
<pre><code class="language-text">HTTP 처리
+
비즈니스 규칙
+
데이터 접근</code></pre>
<p>을 모두 담당하게 된다.</p>
<p>그래서 일반적으로 역할을 다음과 같이 나눈다.</p>
<pre><code class="language-text">Controller
→ HTTP 요청과 응답 처리

Service
→ 비즈니스 로직 처리

Repository
→ 데이터 접근</code></pre>
<p>구조로 보면 다음과 같다.</p>
<pre><code class="language-text">Client
   │
   │ HTTP
   ▼
Controller
   │
   │ Method 호출
   ▼
Service
   │
   │ 데이터 요청
   ▼
Repository
   │
   ▼
DB</code></pre>
<p>Controller는 Client와 가까운 계층이고,</p>
<p>Service로 들어가는 순간부터는 HTTP보다 <strong>Application이 수행해야 하는 업무 자체</strong>에 집중하게 된다.</p>
<hr />
<h2 id="service">Service</h2>
<p>Service는 Application의 <strong>핵심 비즈니스 로직을 담당하는 계층</strong>이다.</p>
<p>예를 들어 주문을 생성한다고 생각해보자.</p>
<p>주문 생성은 단순히 데이터를 한 줄 저장하는 작업만을 의미하지 않는다.</p>
<p>실제로는 다음과 같은 여러 규칙이 존재할 수 있다.</p>
<pre><code class="language-text">사용자가 존재하는가?

상품이 존재하는가?

현재 주문 가능한 상품인가?

재고가 충분한가?

구매 가능한 수량인가?

주문 정보를 어떻게 구성할 것인가?</code></pre>
<p>이런 규칙들을 판단하고 하나의 업무 흐름으로 구성하는 것이 Service의 역할이다.</p>
<pre><code class="language-text">Controller

&quot;이 사용자가 상품을 주문하려고 한다.&quot;

        │
        ▼

Service

사용자 확인
상품 확인
재고 확인
주문 가능 여부 판단
주문 처리</code></pre>
<p>즉 Service에서는</p>
<blockquote>
<p><strong>무엇을 해야 하는가</strong></p>
</blockquote>
<p>에 집중한다.</p>
<hr />
<h3 id="service는-여러-작업을-조합한다">Service는 여러 작업을 조합한다</h3>
<p>하나의 비즈니스 기능이 하나의 데이터만 사용하는 것은 아니다.</p>
<p>예를 들어 주문 처리에는</p>
<pre><code class="language-text">User
Product
Order</code></pre>
<p>정보가 모두 필요할 수 있다.</p>
<p>Service는 필요한 데이터 접근 객체들을 조합해서 하나의 업무를 완성한다.</p>
<pre><code class="language-text">                  ┌─ UserRepository
                  │
Controller ──▶ Service ──┼─ ProductRepository
                  │
                  └─ OrderRepository</code></pre>
<p>즉 Service는 단순히</p>
<pre><code class="language-text">Controller와 Repository 사이에 있으니까 Service</code></pre>
<p>인 것이 아니다.</p>
<p>여러 데이터와 규칙을 조합해 <strong>Application이 실제로 수행해야 하는 업무 단위</strong>를 표현하는 계층이다.</p>
<hr />
<h2 id="repository">Repository</h2>
<p>Service가 업무를 처리하려면 데이터가 필요하다.</p>
<p>예를 들어</p>
<pre><code class="language-text">&quot;10번 User가 존재하는가?&quot;</code></pre>
<p>를 확인해야 한다고 하자.</p>
<p>Service가 직접 SQL까지 작성할 수도 있다.</p>
<pre><code class="language-sql">SELECT *
FROM users
WHERE id = 10;</code></pre>
<p>하지만 이렇게 되면 Service가</p>
<pre><code class="language-text">비즈니스 규칙
+
데이터베이스 접근 방법</code></pre>
<p>을 동시에 알아야 한다.</p>
<p>그래서 데이터 접근 역할을 별도의 계층으로 분리한다.</p>
<p>그 계층이 <strong>Repository</strong>다.</p>
<pre><code class="language-text">Service

&quot;10번 User를 찾아줘.&quot;

        │
        ▼

Repository

&quot;어떤 방식으로 데이터를 가져올지는
내가 담당할게.&quot;</code></pre>
<p>Service는 데이터를 <strong>왜 필요한지</strong>에 집중하고,</p>
<p>Repository는 데이터를 <strong>어떻게 가져올지</strong>를 담당한다.</p>
<hr />
<h3 id="repository의-역할">Repository의 역할</h3>
<p>Repository는 Application과 데이터 저장소 사이의 경계라고 볼 수 있다.</p>
<pre><code class="language-text">Application
     │
     ▼
Repository
     │
     ▼
Data Source</code></pre>
<p>주요 역할은 다음과 같다.</p>
<pre><code class="language-text">데이터 조회
데이터 저장
데이터 수정
데이터 삭제</code></pre>
<p>즉 기본적인 CRUD를 담당한다.</p>
<p>예를 들어 Repository를 다음과 같은 형태로 생각할 수 있다.</p>
<pre><code class="language-java">public interface UserRepository {

    List&lt;User&gt; findAll();

    Optional&lt;User&gt; findById(Long id);

    User save(User user);

    void deleteById(Long id);
}</code></pre>
<p>Service 입장에서는 실제 데이터가 어떤 방법으로 저장되어 있는지보다</p>
<pre><code class="language-java">userRepository.findById(id);</code></pre>
<p>처럼 필요한 기능을 사용할 수 있다는 것이 중요하다.</p>
<p>구체적인 데이터 저장 기술은 이후 별도의 영역에서 다룰 수 있다.</p>
<p>이번 글에서는</p>
<blockquote>
<p><strong>Repository가 데이터 접근 책임을 다른 계층으로부터 분리해준다.</strong></p>
</blockquote>
<p>정도로 이해하면 충분하다.</p>
<hr />
<h3 id="왜-controller가-repository를-바로-호출하지-않을까">왜 Controller가 Repository를 바로 호출하지 않을까?</h3>
<p>그렇다면 이런 의문이 생길 수 있다.</p>
<pre><code class="language-text">Controller
    │
    ▼
Repository</code></pre>
<p>로 바로 호출하면 더 간단하지 않을까?</p>
<p>기술적으로는 가능하다.</p>
<p>단순히 모든 사용자를 조회하는 정도라면</p>
<pre><code class="language-text">Controller
→ Repository</code></pre>
<p>만으로도 동작할 수 있다.</p>
<p>문제는 Application이 커졌을 때다.</p>
<p>예를 들어 회원 가입 기능에서</p>
<pre><code class="language-text">이메일 중복 확인
닉네임 중복 확인
회원 생성
초기 권한 설정
가입 이력 생성</code></pre>
<p>이라는 작업이 필요하다고 하자.</p>
<p>이를 Controller가 직접 처리하면</p>
<pre><code class="language-text">Controller

├─ UserRepository 호출
├─ RoleRepository 호출
├─ HistoryRepository 호출
├─ 중복 검사
├─ 회원 생성 규칙
└─ 응답 처리</code></pre>
<p>처럼 Controller가 HTTP뿐만 아니라 비즈니스 로직까지 모두 알게 된다.</p>
<p>반대로 Service를 사이에 두면</p>
<pre><code class="language-text">Controller

&quot;회원 가입 요청이 들어왔다.&quot;
        │
        ▼
Service

&quot;회원 가입 업무를 처리한다.&quot;
        │
        ├─ UserRepository
        ├─ RoleRepository
        └─ HistoryRepository</code></pre>
<p>로 역할을 분리할 수 있다.</p>
<p>Controller는 여전히 HTTP에 집중하고,</p>
<p>Service는 회원 가입이라는 업무에 집중한다.</p>
<hr />
<h2 id="계층을-분리하는-이유">계층을 분리하는 이유</h2>
<p>결국 Controller, Service, Repository를 나누는 핵심은 <strong>역할 분리</strong>다.</p>
<pre><code class="language-text">Controller

HTTP를 이해한다.
Application의 업무를 직접 구현하지 않는다.


Service

Application의 업무를 이해한다.
HTTP나 데이터 저장 방법에는 최대한 의존하지 않는다.


Repository

데이터 접근을 이해한다.
HTTP 요청 처리나 비즈니스 규칙을 담당하지 않는다.</code></pre>
<p>각 계층이 자신의 책임에 집중하게 만드는 것이다.</p>
<p>이를 그림으로 보면 더 명확하다.</p>
<pre><code class="language-text">HTTP 영역

Client
   │
   ▼
Controller
────────────────────
Application 영역

Service
────────────────────
Data Access 영역

Repository
   │
   ▼
DB</code></pre>
<p>따라서 어느 한 영역이 바뀌더라도 다른 영역에 미치는 영향을 줄일 수 있다.</p>
<p>예를 들어 HTTP API 형식이 변경되어도 Service의 핵심 업무 로직은 그대로 유지할 수 있고,</p>
<p>데이터 저장 방식이 변경되어도 Controller가 직접 영향을 받을 필요는 없다.</p>
<hr />
<h2 id="연결-예시코드">연결 예시코드</h2>
<p>실제 코드는 다음처럼 작성할 수 있다.</p>
<pre><code class="language-java">@RestController
@RequestMapping(&quot;/api&quot;)
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping(&quot;/users/{id}&quot;)
    public User getUser(
            @PathVariable Long id
    ) {
        return userService.getUserById(id)
                .orElse(null);
    }
}</code></pre>
<p>Controller는 <code>UserService</code>에게 실제 작업을 요청한다.</p>
<pre><code class="language-text">GET /api/users/10
        │
        ▼
UserController
        │
        │ getUserById(10)
        ▼
UserService</code></pre>
<p>Service는 필요한 데이터를 Repository에게 요청한다.</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }

    public Optional&lt;User&gt; getUserById(Long id) {
        return userRepository.findById(id);
    }
}</code></pre>
<p>흐름은 다음과 같다.</p>
<pre><code class="language-text">Controller

&quot;10번 User 조회&quot;
       │
       ▼
Service

&quot;User 조회 업무 처리&quot;
       │
       ▼
Repository

&quot;10번 데이터를 가져온다.&quot;</code></pre>
<hr />
<h3 id="bean으로-연결-이해하기">Bean으로 연결 이해하기</h3>
<p>여기서 앞에서 살펴본 Bean 개념이 다시 등장한다.</p>
<pre><code class="language-java">@RestController
public class UserController {
}</code></pre>
<pre><code class="language-java">@Service
public class UserService {
}</code></pre>
<pre><code class="language-java">@Repository
public class UserRepository {
}</code></pre>
<p>이 객체들은 모두 Spring이 관리하는 Bean이 될 수 있다.</p>
<p>그리고 각 객체는 자신이 필요한 객체를 생성자를 통해 요구하고 있다.</p>
<pre><code class="language-text">UserController
      │
      │ 필요
      ▼
UserService
      │
      │ 필요
      ▼
UserRepository</code></pre>
<p>코드로 보면</p>
<pre><code class="language-java">public UserController(UserService userService) {
    this.userService = userService;
}</code></pre>
<p>그리고</p>
<pre><code class="language-java">public UserService(UserRepository userRepository) {
    this.userRepository = userRepository;
}</code></pre>
<p>이다.</p>
<p>개발자가 직접</p>
<pre><code class="language-java">new UserRepository();
new UserService(...);
new UserController(...);</code></pre>
<p>를 반복하지 않는다.</p>
<p>Spring이 Bean을 생성하고 서로 필요한 객체를 연결해준다.</p>
<pre><code class="language-text">Spring IoC Container

UserRepository
      │
      ▼
UserService
      │
      ▼
UserController</code></pre>
<p>이것이 이후 자세히 살펴볼 <strong>Dependency Injection</strong>과 연결된다.</p>
<p>현재는</p>
<blockquote>
<p>Spring이 Bean을 만들고, Bean 사이의 필요한 관계도 연결할 수 있다.</p>
</blockquote>
<p>정도로 이해하면 충분하다.</p>
<hr />
<h1 id="framework-영역과-개발자-영역">Framework 영역과 개발자 영역</h1>
<p>이 흐름을 이해할 때 한 번 더 나누어 보면 좋다.</p>
<p>우리가 직접 구현하는 영역과 Spring이 대신 처리하는 영역이다.</p>
<pre><code class="language-text">┌──────────── Framework 영역 ────────────┐

Tomcat
  │
DispatcherServlet
  │
HandlerMapping
  │
HandlerAdapter

└───────────────────────────────────────┘
                 │
                 ▼
┌──────────── 개발자 영역 ───────────────┐

Controller
  │
Service
  │
Repository

└───────────────────────────────────────┘</code></pre>
<p>물론 내부적으로는 훨씬 많은 Component들이 동작한다.</p>
<p>하지만 개발자 입장에서 중요한 것은</p>
<blockquote>
<p><strong>Framework가 HTTP Request를 우리가 작성한 Controller Method까지 연결해준다는 것</strong></p>
</blockquote>
<p>이다.</p>
<p>그 이후부터 우리가 작성한 Controller, Service, Repository가 Application의 기능을 수행한다.</p>
<hr />
<h2 id="spring-mvc를-직접-만든다면">Spring MVC를 직접 만든다면?</h2>
<p>지금까지의 구조를 보면 Spring MVC가 굉장히 많은 일을 대신하고 있다는 것을 알 수 있다.</p>
<p>Spring Framework가 없다면 개발자가 직접</p>
<pre><code class="language-text">Socket으로 요청 받기

HTTP Message 분석하기

URL과 Method를 비교하기

어떤 Controller를 실행할지 찾기

Request 값을 Method Parameter로 변환하기

Controller Method 실행하기

Response Message 만들기</code></pre>
<p>같은 작업들을 구현해야 한다.</p>
<p>Spring MVC는 이 구조를 Framework 내부에 이미 구현해두고</p>
<pre><code class="language-java">@GetMapping(&quot;/users/{id}&quot;)</code></pre>
<p>같은 선언만으로 사용할 수 있게 해준다.</p>
<p>따라서 Spring Boot가 편리하다는 것은 내부 과정이 사라졌다는 뜻이 아니다.</p>
<blockquote>
<p><strong>복잡한 Web Server 처리 구조를 Framework가 대신 구현하고 연결해주고 있다는 의미다.</strong></p>
</blockquote>
<hr />
<h1 id="정리">정리</h1>
<p>이번 글에서는 하나의 HTTP Request가 Spring Boot Application 내부에서 어떻게 처리되는지를 살펴봤다.</p>
<p>전체 구조는 다음과 같다.</p>
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
DB</code></pre>
<p>각 영역의 역할을 정리하면</p>
<pre><code class="language-text">Tomcat
→ HTTP 요청을 받아 Servlet 환경으로 전달

DispatcherServlet
→ Spring MVC의 Front Controller

HandlerMapping
→ Request를 처리할 Controller Method 검색

HandlerAdapter
→ 찾아낸 Handler 실행

Controller
→ HTTP Request와 Application 연결

Service
→ 비즈니스 로직 수행

Repository
→ 데이터 접근</code></pre>
<p>이라고 볼 수 있다.</p>
<p>그리고 Controller, Service, Repository 같은 객체들은 앞에서 살펴본 Component Scan을 통해 Spring Bean으로 관리될 수 있다.</p>
<pre><code class="language-text">Component Scan
      │
      ▼
Bean 등록
      │
      ▼
Controller
Service
Repository</code></pre>
<p>여기까지 보면 Spring Boot Backend의 큰 흐름은 다음처럼 정리된다.</p>
<pre><code class="language-text">                     Spring Framework

Client
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
────────────────────────────────
                  개발자 코드
  │
Controller
  │
Service
  │
Repository
  │
DB</code></pre>
<p>그리고 아직 남아 있는 중요한 질문이 있다.</p>
<p>우리는 다음 코드를 작성했을 뿐이다.</p>
<pre><code class="language-java">public UserController(UserService userService) {
    this.userService = userService;
}</code></pre>
<p>그런데 <code>UserController</code>도 직접 만들지 않았고,</p>
<p><code>UserService</code>도 직접 만들지 않았다.</p>
<p>그럼에도 두 객체는 생성되어 있고 서로 연결되어 있다.</p>
<blockquote>
<p><strong>이 객체의 생성과 연결에 대한 제어권은 정확히 누가 가지고 있는 것일까?</strong></p>
</blockquote>
<p>여기서부터 Spring의 핵심 개념인 <strong>IoC와 DI</strong>로 이어진다.</p>