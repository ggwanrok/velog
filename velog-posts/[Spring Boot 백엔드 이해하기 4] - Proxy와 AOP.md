<p>지난 글에서는 Spring의 IoC와 DI를 살펴봤다.</p>
<p>Spring에서는 개발자가 객체를 직접 생성하고 연결하는 것이 아니라 IoC Container가 Bean을 생성하고 의존 관계를 구성한다.</p>
<pre><code class="language-text">Spring IoC Container

┌──────────────────────────────┐
│                              │
│  UserController Bean         │
│          │                   │
│          ▼                   │
│  UserService Bean            │
│          │                   │
│          ▼                   │
│  UserRepository Bean         │
│                              │
└──────────────────────────────┘</code></pre>
<p>그런데 Spring은 Bean을 단순히 생성하고 보관하는 것에서 끝나지 않는다.</p>
<p>때로는 우리가 만든 객체를 그대로 제공하지 않고 <strong>그 객체 앞에 또 다른 객체를 하나 세운다.</strong></p>
<pre><code class="language-text">호출자
  │
  ▼
Proxy
  │
  ▼
실제 Bean</code></pre>
<p>왜 굳이 중간에 객체를 하나 더 둘까?</p>
<p>예를 들어 모든 Service Method가 호출될 때마다 실행 시간을 측정하고 싶다고 해보자.</p>
<pre><code class="language-java">public User getUser(Long id) {

    long start = System.currentTimeMillis();

    User user = ...

    long end = System.currentTimeMillis();

    System.out.println(end - start);

    return user;
}</code></pre>
<p>다른 Method에도 동일한 기능이 필요하다면?</p>
<pre><code class="language-java">public void createUser(...) {

    long start = System.currentTimeMillis();

    ...

    long end = System.currentTimeMillis();

    System.out.println(end - start);
}</code></pre>
<pre><code class="language-java">public void deleteUser(...) {

    long start = System.currentTimeMillis();

    ...

    long end = System.currentTimeMillis();

    System.out.println(end - start);
}</code></pre>
<p>비즈니스 로직 사이에 실행 시간 측정 코드가 계속 섞이기 시작한다.</p>
<pre><code class="language-text">UserService

비즈니스 로직
실행 시간 측정

OrderService

비즈니스 로직
실행 시간 측정

ProductService

비즈니스 로직
실행 시간 측정</code></pre>
<p>우리가 정말 작성하고 싶은 것은</p>
<pre><code class="language-text">사용자 조회
주문 처리
상품 처리</code></pre>
<p>같은 비즈니스 로직이다.</p>
<p>그런데</p>
<pre><code class="language-text">Logging
성능 측정
Transaction
Validation
Security</code></pre>
<p>같은 부가 기능들이 여러 Class에 반복해서 들어온다.</p>
<p>이런 문제를 해결하는 중요한 기반이 <strong>Proxy Pattern</strong>이다.</p>
<hr />
<h1 id="proxy-pattern">Proxy Pattern</h1>
<p>Proxy는 한국어로 <strong>대리자</strong> 정도로 이해할 수 있다.</p>
<p>Client가 실제 객체를 직접 호출하지 않고,</p>
<p><strong>실제 객체와 동일한 역할을 하는 Proxy 객체를 먼저 호출하는 구조</strong>다.</p>
<pre><code class="language-text">Client
  │
  ▼
Proxy
  │
  ▼
RealSubject</code></pre>
<p>여기서 각 역할을 나누면 다음과 같다.</p>
<pre><code class="language-text">Client
→ 기능을 사용하는 객체

Proxy
→ 실제 객체를 대신해서 호출을 받는 객체

RealSubject
→ 실제 기능을 수행하는 객체</code></pre>
<p>중요한 것은 Client 입장에서 Proxy와 실제 객체를 비슷한 방식으로 사용할 수 있어야 한다는 것이다.</p>
<p>그래서 전형적인 Proxy Pattern에서는 같은 Interface를 구현한다.</p>
<pre><code class="language-text">             Subject
                ▲
        ┌───────┴───────┐
        │               │
      Proxy         RealSubject</code></pre>
<p>코드로 보면 다음과 같다.</p>
<pre><code class="language-java">public interface Subject {

    String operation(String name);
}</code></pre>
<p>실제 기능을 담당하는 객체가 있다.</p>
<pre><code class="language-java">public class RealSubject implements Subject {

    @Override
    public String operation(String name) {

        System.out.println(&quot;실제 작업 수행&quot;);

        return name;
    }
}</code></pre>
<p>그리고 Proxy도 동일한 Interface를 구현한다.</p>
<pre><code class="language-java">public class SubjectProxy implements Subject {

    private final Subject target;

    public SubjectProxy(Subject target) {
        this.target = target;
    }

    @Override
    public String operation(String name) {

        System.out.println(&quot;실행 전&quot;);

        String result = target.operation(name);

        System.out.println(&quot;실행 후&quot;);

        return result;
    }
}</code></pre>
<p>Client는 실제 객체 대신 Proxy를 사용한다.</p>
<pre><code class="language-java">Subject target = new RealSubject();

Subject proxy = new SubjectProxy(target);

proxy.operation(&quot;Alice&quot;);</code></pre>
<p>실제 흐름은 다음과 같다.</p>
<pre><code class="language-text">Client
  │
  │ operation()
  ▼
Proxy
  │
  ├─ 실행 전 처리
  │
  ▼
RealSubject
  │
  │ 실제 작업
  ▼
Proxy
  │
  ├─ 실행 후 처리
  │
  ▼
Client</code></pre>
<p>Proxy가 실제 객체를 내부에 가지고 있다가 요청을 넘기는 것이다.</p>
<p>이런 구조를 흔히 <strong>Wrapping</strong>한다고 표현한다. Proxy가 RealSubject를 감싸고 실제 Method 호출을 위임하면서 호출 전후에 추가 작업을 수행할 수 있다.</p>
<hr />
<h2 id="proxy가-중요한-이유">Proxy가 중요한 이유</h2>
<p>Proxy의 핵심은 단순히 객체를 한 번 더 거쳐간다는 데 있지 않다.</p>
<p><strong>실제 객체를 수정하지 않고 호출 과정에 새로운 기능을 삽입할 수 있다는 것</strong>이 중요하다.</p>
<p>기존 구조가</p>
<pre><code class="language-text">Client
   │
   ▼
UserService
   │
   ▼
Business Logic</code></pre>
<p>이었다면 Proxy를 이용해 다음처럼 만들 수 있다.</p>
<pre><code class="language-text">Client
   │
   ▼
UserServiceProxy
   │
   ├─ Logging
   ├─ Time Check
   ├─ Security
   │
   ▼
UserService
   │
   ▼
Business Logic</code></pre>
<p><code>UserService</code> 입장에서는 자신이 Proxy에 감싸져 있다는 사실조차 알 필요가 없다.</p>
<pre><code class="language-java">public class UserService {

    public User getUser(Long id) {

        // 사용자 조회라는
        // 자신의 비즈니스 로직에만 집중

        return ...;
    }
}</code></pre>
<p>부가 기능은 밖으로 빠진다.</p>
<pre><code class="language-text">Proxy
→ 부가 기능

Target
→ 핵심 기능</code></pre>
<p>이 분리가 이후 AOP로 이어진다.</p>
<hr />
<h2 id="실제-객체를-대신한다">실제 객체를 대신한다</h2>
<p>Proxy Pattern에서 중요한 포인트가 하나 더 있다.</p>
<p>Client는 실제 객체를 직접 사용하지 않는다.</p>
<pre><code class="language-text">X

Client
   │
   ▼
RealSubject</code></pre>
<p>Proxy를 사용하기로 했다면</p>
<pre><code class="language-text">O

Client
   │
   ▼
Proxy
   │
   ▼
RealSubject</code></pre>
<p>가 되어야 한다.</p>
<p>왜냐하면 Client가 원본 객체를 직접 호출해버리면 Proxy가 끼어들 기회 자체가 없기 때문이다.</p>
<pre><code class="language-text">Client ─────────────▶ RealSubject
                         ▲
                         │
                       Proxy

Proxy 우회
→ 부가 기능 실행 X</code></pre>
<p>이 사실이 Spring Proxy를 이해할 때 굉장히 중요하다.</p>
<hr />
<h2 id="proxy-bean-직접-만들기">Proxy Bean 직접 만들기</h2>
<p>지난 글에서 <code>@Configuration</code>과 <code>@Bean</code>을 살펴봤다.</p>
<p>Spring Bean은 Component Scan으로만 만들 수 있는 것이 아니다.</p>
<pre><code class="language-java">@Configuration
public class AppConfig {

    @Bean
    public UserService userService() {

        return new UserService();
    }
}</code></pre>
<p>처럼 직접 Bean을 등록할 수도 있다.</p>
<p>그렇다면 Container에 실제 <code>UserService</code>가 아니라 Proxy를 넣는 것도 가능하다.</p>
<pre><code class="language-java">@Configuration
public class AppConfig {

    @Bean
    public UserService userService(
            UserRepository userRepository
    ) {

        UserService target =
                new UserService(userRepository);

        return new UserServiceProxy(target);
    }
}</code></pre>
<p>구조적으로 보면</p>
<pre><code class="language-text">UserService
실제 객체 생성
      │
      ▼
UserServiceProxy가 감쌈
      │
      ▼
Spring Container에 등록</code></pre>
<p>이 된다.</p>
<p>여기서 중요한 점은 <strong>다른 Bean이 받아가는 객체가 무엇인가</strong>다.</p>
<p>예를 들어 Controller가</p>
<pre><code class="language-java">public UserController(
        UserService userService
) {
    this.userService = userService;
}</code></pre>
<p>라고 해도,</p>
<p>실제로 Container에서 전달받는 객체는 우리가 등록한 Proxy일 수 있다.</p>
<pre><code class="language-text">Spring IoC Container

UserService Bean
       │
       ▼
┌─────────────────────┐
│ UserServiceProxy    │
│                     │
│   ┌─────────────┐   │
│   │ UserService │   │
│   │   Target    │   │
│   └─────────────┘   │
│                     │
└─────────────────────┘</code></pre>
<p><strong>Container에서 다른 객체에게 제공되는 Bean Reference가 Proxy일 수 있다.</strong></p>
<p>그 Proxy 내부에 실제 Target 객체가 존재하는 구조다.</p>
<hr />
<h2 id="호출-흐름">호출 흐름</h2>
<p>Controller에서는 여전히 평범하게 호출한다.</p>
<pre><code class="language-java">userService.getUser(id);</code></pre>
<p>하지만 <code>userService</code>에 들어 있는 Reference가 Proxy라면 실제 흐름은</p>
<pre><code class="language-text">Controller
    │
    │ userService.getUser()
    ▼
Proxy
    │
    ├─ 실행 전 처리
    │
    ▼
Target UserService
    │
    │ getUser()
    ▼
Proxy
    │
    ├─ 실행 후 처리
    ▼
Controller</code></pre>
<p>가 된다.</p>
<p>Controller는 Proxy 존재 여부를 몰라도 된다.</p>
<p>이것이 Proxy Pattern의 장점이다.</p>
<hr />
<h2 id="동적-proxy-class-생성">동적 Proxy Class 생성</h2>
<p>여기까지의 Proxy는 개발자가 직접 작성했다.</p>
<pre><code class="language-java">public class UserServiceProxy
        implements UserService {

    private final UserService target;

    ...
}</code></pre>
<p>그런데 Service가 100개라면?</p>
<pre><code class="language-text">UserServiceProxy
OrderServiceProxy
ProductServiceProxy
PaymentServiceProxy
...</code></pre>
<p>비슷한 Proxy Class를 계속 만들어야 한다.</p>
<p>그리고 각각</p>
<pre><code class="language-text">Logging
실행 시간 측정
Transaction
Security</code></pre>
<p>같은 동일한 코드를 반복하게 될 수 있다.</p>
<p>이러면 Proxy Pattern으로 중복을 제거하려다가 <strong>Proxy 자체의 중복 코드가 생긴다.</strong></p>
<p>그래서 Java와 Spring은 Proxy를 동적으로 생성하는 방법을 사용한다.</p>
<hr />
<h3 id="dynamic-proxy">Dynamic Proxy</h3>
<p>Dynamic Proxy는 이름 그대로</p>
<blockquote>
<p><strong>개발자가 구체적인 Proxy Class를 직접 작성하지 않고 Runtime에 Proxy 객체를 생성하는 방식</strong></p>
</blockquote>
<p>이다.</p>
<p>Spring AOP에서 대표적으로 사용되는 Proxy 방식은 두 가지다.</p>
<pre><code class="language-text">Spring AOP Proxy

├─ JDK Dynamic Proxy
│
└─ CGLIB Proxy</code></pre>
<p>둘 다 목적은 같다.</p>
<pre><code class="language-text">호출자
   │
   ▼
동적으로 생성된 Proxy
   │
   ├─ 부가 기능
   │
   ▼
Target</code></pre>
<p>차이는 <strong>Proxy 객체를 어떤 타입 구조로 만들어내느냐</strong>에 있다.</p>
<hr />
<h4 id="jdk-dynamic-proxy">JDK Dynamic Proxy</h4>
<p>JDK Dynamic Proxy는 <strong>Interface를 기준으로 Proxy 객체를 생성하는 방식</strong>이다.</p>
<p>다음 구조를 보자.</p>
<pre><code class="language-text">              UserService
              Interface
              ▲       ▲
              │       │
              │       │
UserServiceImpl      JDK Proxy
    Target</code></pre>
<p>Target과 Proxy가 서로 상속 관계인 것은 아니다.</p>
<p>둘 다 <strong>같은 Interface를 구현한다.</strong></p>
<p>예를 들어 다음 Interface와 구현체가 있다고 하자.</p>
<pre><code class="language-java">public interface UserService {

    User getUser(Long id);
}</code></pre>
<pre><code class="language-java">public class UserServiceImpl
        implements UserService {

    @Override
    public User getUser(Long id) {
        ...
    }
}</code></pre>
<p>Java에서는 <code>java.lang.reflect.Proxy</code>를 이용해 <code>UserService</code> Interface를 구현하는 Proxy 객체를 Runtime에 생성할 수 있다.</p>
<p>개념적인 형태는 다음과 같다.</p>
<pre><code class="language-java">UserService target =
        new UserServiceImpl();

UserService proxy =
        (UserService) Proxy.newProxyInstance(
                UserService.class.getClassLoader(),
                new Class[]{UserService.class},
                (proxyObject, method, args) -&gt; {

                    System.out.println(&quot;실행 전&quot;);

                    Object result =
                            method.invoke(target, args);

                    System.out.println(&quot;실행 후&quot;);

                    return result;
                }
        );</code></pre>
<p>개발자가 다음 Class를 직접 작성하지 않았는데도</p>
<pre><code class="language-java">class UserServiceProxy
        implements UserService</code></pre>
<p><code>UserService</code>처럼 사용할 수 있는 Proxy 객체가 만들어진다.</p>
<p>실제 호출은 다음처럼 생각할 수 있다.</p>
<pre><code class="language-text">Controller
    │
    │ UserService.getUser()
    ▼
JDK Dynamic Proxy
    │
    │ InvocationHandler
    ├─ 실행 전 처리
    │
    ▼
UserServiceImpl
    │
    │ 실제 Method 실행
    ▼
JDK Dynamic Proxy
    │
    ├─ 실행 후 처리
    ▼
Controller</code></pre>
<p>여기서 중요한 것이 <code>InvocationHandler</code>다.</p>
<p>Proxy가 Method 호출을 받으면</p>
<pre><code class="language-text">어떤 Method가 호출됐는지
어떤 Argument가 들어왔는지</code></pre>
<p>를 전달받고, 필요한 부가기능을 수행한 뒤 실제 Target으로 호출을 넘긴다.</p>
<pre><code class="language-java">method.invoke(target, args);</code></pre>
<p>이전 글에서 살펴본 <strong>Reflection</strong>이 여기서 다시 등장한다.</p>
<pre><code class="language-text">JDK Dynamic Proxy

Interface
   +
InvocationHandler
   +
Reflection</code></pre>
<p>을 이용해 호출을 중간에서 가로채고 Target에게 위임할 수 있는 것이다.</p>
<p>즉 JDK Dynamic Proxy의 핵심은 단순히</p>
<pre><code class="language-text">Interface가 있으면 사용한다.</code></pre>
<p>가 아니라,</p>
<blockquote>
<p><strong>Target과 Proxy가 같은 Interface를 구현하고, Runtime에 만들어진 Proxy가 Method 호출을 가로챈다.</strong></p>
</blockquote>
<p>는 구조다.</p>
<hr />
<h4 id="cglib-proxy">CGLIB Proxy</h4>
<p>CGLIB는 접근 방식이 다르다.</p>
<p>Interface를 기준으로 별도의 Proxy 객체를 만드는 대신 <strong>Target Class를 상속한 Subclass를 Runtime에 생성한다.</strong></p>
<p>예를 들어 다음 Class가 있다고 하자.</p>
<pre><code class="language-java">public class UserService {

    public User getUser(Long id) {
        ...
    }
}</code></pre>
<p>CGLIB 방식은 개념적으로 다음과 같은 Proxy Class를 동적으로 만드는 것과 비슷하다.</p>
<pre><code class="language-java">public class UserServiceProxy
        extends UserService {

    @Override
    public User getUser(Long id) {

        // 실행 전 부가기능

        User result =
                super.getUser(id);

        // 실행 후 부가기능

        return result;
    }
}</code></pre>
<p>구조를 보면</p>
<pre><code class="language-text">UserService
   Target
     ▲
     │ extends
     │
UserService Proxy</code></pre>
<p>가 된다.</p>
<p>JDK Dynamic Proxy와 비교하면 차이가 분명해진다.</p>
<pre><code class="language-text">JDK Dynamic Proxy

Interface
   ▲       ▲
   │       │
Target   Proxy

→ 같은 Interface 구현</code></pre>
<pre><code class="language-text">CGLIB Proxy

Target Class
     ▲
     │ 상속
     │
Proxy Subclass

→ Target Class를 상속</code></pre>
<p>따라서 CGLIB는 별도의 Interface가 없어도 Class 자체를 기준으로 Proxy를 만들 수 있다.</p>
<p>호출을 단순화하면</p>
<pre><code class="language-text">Controller
    │
    ▼
UserService의 Subclass Proxy
    │
    ├─ Method 호출 가로채기
    │
    ▼
Target의 실제 Logic</code></pre>
<p>형태로 이해할 수 있다.</p>
<p>즉 CGLIB의 핵심은</p>
<pre><code class="language-text">Target Class 상속
        │
        ▼
Method Override
        │
        ▼
호출 가로채기</code></pre>
<p>다.</p>
<p>Spring Framework의 Spring AOP는 JDK Dynamic Proxy와 CGLIB 방식을 모두 사용할 수 있다.</p>
<p>다만 <strong>Spring Boot의 AOP Auto Configuration은 기본적으로 CGLIB 기반 Class Proxy를 사용한다.</strong></p>
<p>따라서 Spring Boot 기준으로</p>
<pre><code class="language-text">Interface가 있으면 무조건 JDK Proxy
Interface가 없으면 무조건 CGLIB</code></pre>
<p>라고 외우는 것은 정확하지 않다.</p>
<p>JDK Proxy를 사용하도록 바꾸고 싶다면 다음 설정을 사용할 수 있다.</p>
<pre><code class="language-properties">spring.aop.proxy-target-class=false</code></pre>
<p>정리하면</p>
<pre><code class="language-text">Spring AOP가 지원하는 Proxy 방식

JDK Dynamic Proxy
→ Interface 기반

CGLIB
→ Target Class 상속 기반</code></pre>
<p>그리고</p>
<pre><code class="language-text">Spring Boot AOP 기본 설정
→ CGLIB 기반 Class Proxy</code></pre>
<p>라고 구분해서 이해하면 된다.</p>
<hr />
<h4 id="cglib의-상속-제약">CGLIB의 상속 제약</h4>
<p>CGLIB가 Target Class를 상속하고 Method를 Override하는 방식이라는 점을 이해하면 제약도 자연스럽게 따라온다.</p>
<p>예를 들어</p>
<pre><code class="language-java">public final class UserService {
}</code></pre>
<p>처럼 Class 자체가 <code>final</code>이면 상속할 수 없다.</p>
<p>Method 역시</p>
<pre><code class="language-java">public final void updateUser() {
}</code></pre>
<p>라면 Override할 수 없다.</p>
<p><code>private</code> Method도 Subclass에서 Override할 수 없기 때문에 일반적인 CGLIB Proxy 방식으로 Advice를 적용할 수 없다.</p>
<p>결국 CGLIB의 제약은 전부</p>
<pre><code class="language-text">Target 상속
      │
      ▼
Method Override
      │
      ▼
호출 가로채기</code></pre>
<p>라는 동작 원리에서 나온다.</p>
<p>두 방식을 최종적으로 비교하면 다음과 같다.</p>
<pre><code class="language-text">JDK Dynamic Proxy
→ Interface를 구현하는 별도의 Proxy 객체를 Runtime에 생성

CGLIB
→ Target을 상속하는 Subclass Proxy를 Runtime에 생성</code></pre>
<p>따라서 단순히 <code>Interface 있음 / 없음</code>으로 외우기보다</p>
<blockquote>
<p><strong>Proxy 객체가 실제로 어떤 타입 구조로 만들어지는가</strong></p>
</blockquote>
<p>를 기준으로 이해하는 것이 좋다.</p>
<hr />
<h2 id="spring에서-proxy">Spring에서 Proxy</h2>
<p>Spring에서는 Proxy 기반으로 다양한 기능을 적용할 수 있다.</p>
<p>대표적으로</p>
<pre><code class="language-text">AOP

@Transactional

@Cacheable
@CacheEvict

@Async

@Validated</code></pre>
<p>같은 기능들이 있다.</p>
<p>개발자가 Service에</p>
<pre><code class="language-java">@Transactional
public void order() {
    ...
}</code></pre>
<p>라고 작성했다고 해서 <code>order()</code> Method 안에</p>
<pre><code class="language-java">transaction.begin();

...

transaction.commit();</code></pre>
<p>코드가 자동으로 들어가는 것은 아니다.</p>
<p>큰 개념으로 보면</p>
<pre><code class="language-text">호출자
   │
   ▼
Proxy
   │
   ├─ 부가 기능
   │
   ▼
Target</code></pre>
<p>구조를 이용해서 Target Method 호출 전후에 Spring이 필요한 작업을 수행할 수 있게 된다.</p>
<p>이제 이 구조를 개발자가 매번 직접 Proxy로 구현하지 않고 <strong>선언적으로 사용하고 싶다.</strong></p>
<p>여기서 AOP가 등장한다.</p>
<hr />
<h1 id="aop">AOP</h1>
<p>AOP는</p>
<p><strong>Aspect-Oriented Programming</strong></p>
<p>즉 <strong>관점 지향 프로그래밍</strong>이다.</p>
<p>AOP가 해결하려는 문제부터 보는 것이 이해하기 쉽다.</p>
<p>다음과 같은 Service들이 있다고 하자.</p>
<pre><code class="language-text">UserService
OrderService
PaymentService
DeliveryService</code></pre>
<p>각 Service는 서로 다른 핵심 기능을 가지고 있다.</p>
<pre><code class="language-text">UserService
→ 사용자 관리

OrderService
→ 주문 관리

PaymentService
→ 결제 관리

DeliveryService
→ 배송 관리</code></pre>
<p>이것들이 <strong>핵심 관심사(Core Concern)</strong>다.</p>
<p>그런데 모든 Service에 공통적으로 필요한 기능도 존재한다.</p>
<pre><code class="language-text">Logging
Transaction
Security
Performance Measurement</code></pre>
<p>이러한 기능은 한 Class에만 속하지 않고 여러 비즈니스 영역을 가로질러 등장한다.</p>
<pre><code class="language-text">                Logging
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼

UserService   OrderService   PaymentService

       ▲           ▲           ▲
       └───────────┼───────────┘
                   │
              Transaction</code></pre>
<p>이를 <strong>횡단 관심사(Cross-Cutting Concern)</strong>라고 한다. AOP는 이런 공통 관심사를 별도의 모듈로 분리하여 핵심 비즈니스 코드와 분리하는 방식이다.</p>
<hr />
<h2 id="oop와-aop">OOP와 AOP</h2>
<p>AOP가 OOP를 대체하는 것은 아니다.</p>
<p>OOP에서는 보통 기능별로 객체의 역할을 분리한다.</p>
<pre><code class="language-text">UserService

OrderService

PaymentService</code></pre>
<p>하지만 Logging 같은 기능은 객체 하나에만 속하기 어렵다.</p>
<pre><code class="language-text">UserService
 ├─ Business Logic
 └─ Logging

OrderService
 ├─ Business Logic
 └─ Logging

PaymentService
 ├─ Business Logic
 └─ Logging</code></pre>
<p>OOP만으로도 해결할 수는 있지만 공통 코드가 여러 객체에 흩어지기 쉽다.</p>
<p>AOP는 이 횡단 관심사를 별도로 분리한다.</p>
<pre><code class="language-text">          Logging Aspect
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼

 UserService OrderService PaymentService</code></pre>
<p>따라서</p>
<pre><code class="language-text">OOP
→ 핵심 비즈니스 객체를 역할별로 분리

AOP
→ 여러 객체를 가로지르는 공통 관심사를 분리</code></pre>
<p>라고 이해하면 좋다.</p>
<hr />
<h2 id="aop와-proxy의-관계">AOP와 Proxy의 관계</h2>
<p>여기서 Proxy와 AOP가 연결된다.</p>
<p>AOP는</p>
<pre><code class="language-text">&quot;이 Method 실행 전에 Logging을 수행해.&quot;</code></pre>
<p>라고 선언했다고 해서 Target Method의 Source Code를 직접 수정하는 것이 아니다.</p>
<p>Spring은 필요한 Bean에 Proxy를 적용하고,</p>
<p>호출을 Proxy가 먼저 받게 만든다.</p>
<pre><code class="language-text">호출자
   │
   ▼
AOP Proxy
   │
   ├─ Logging
   │
   ▼
Target Bean</code></pre>
<p>따라서 Spring AOP를 아주 크게 보면</p>
<blockquote>
<p><strong>Proxy Pattern을 이용해 공통 기능을 필요한 Method 호출 전후에 자동으로 적용하는 구조</strong></p>
</blockquote>
<p>라고 볼 수 있다.</p>
<p>Spring의 <code>@AspectJ</code> 스타일도 런타임 자체는 Spring AOP의 Proxy 기반으로 동작한다.</p>
<hr />
<h2 id="직접-proxy와-aop의-차이">직접 Proxy와 AOP의 차이</h2>
<p>직접 Proxy를 만들었을 때는</p>
<pre><code class="language-text">개발자

UserServiceProxy 직접 작성
        │
        ▼
Target 감싸기
        │
        ▼
Bean 등록</code></pre>
<p>까지 개발자가 해야 했다.</p>
<p>AOP를 사용하면</p>
<pre><code class="language-text">개발자

&quot;어떤 Method에&quot;

&quot;어떤 부가기능을&quot;

&quot;언제 실행할지&quot;

선언
      │
      ▼
Spring
      │
      ▼
Proxy 자동 생성</code></pre>
<p>이 된다.</p>
<p>즉 AOP를 이해할 때는</p>
<pre><code class="language-text">Proxy
→ 부가기능을 끼워 넣는 구조

AOP
→ 그 Proxy 적용을 선언적으로 관리하는 방식</code></pre>
<p>으로 연결하면 훨씬 이해하기 쉽다.</p>
<hr />
<h2 id="spring-aop의-구성요소">Spring AOP의 구성요소</h2>
<p>Spring AOP 코드를 보면 처음에는 용어가 많아서 복잡해 보인다.</p>
<p>대표적인 용어는 다음과 같다.</p>
<pre><code class="language-text">Aspect
Pointcut
Advice
JoinPoint
Target
Proxy</code></pre>
<p>하나의 코드로 먼저 보자.</p>
<pre><code class="language-java">@Aspect
@Component
public class LoggingAspect {

    @Pointcut(
        &quot;execution(* com.example.service.*.*(..))&quot;
    )
    public void serviceMethods() {
    }

    @Before(&quot;serviceMethods()&quot;)
    public void before(
            JoinPoint joinPoint
    ) {

        System.out.println(
            joinPoint.getSignature()
        );
    }
}</code></pre>
<p>각 요소를 하나씩 분리해보자.</p>
<hr />
<h3 id="aspect">Aspect</h3>
<p>Aspect는 <strong>공통 관심사를 모아놓은 단위</strong>다.</p>
<p>예를 들어 Logging을 모아놓은 Class라면</p>
<pre><code class="language-java">@Aspect
@Component
public class LoggingAspect {
}</code></pre>
<p>가 된다.</p>
<pre><code class="language-text">LoggingAspect

├─ 실행 전 Logging
├─ 실행 후 Logging
└─ 예외 Logging</code></pre>
<p>같은 기능을 하나의 Aspect에서 관리할 수 있다.</p>
<p>여기서 <code>@Aspect</code>는</p>
<pre><code class="language-text">&quot;이 Class는 AOP 설정을 담고 있다.&quot;</code></pre>
<p>는 의미다.</p>
<p>그리고 Spring AOP가 해당 Aspect를 사용하려면 Spring이 관리할 수 있는 Bean이어야 한다.</p>
<p>그래서 흔히</p>
<pre><code class="language-java">@Aspect
@Component</code></pre>
<p>를 함께 사용한다.</p>
<p><code>@Aspect</code> 자체만으로 Component Scan의 대상이 되는 것은 아니기 때문에 Aspect를 일반 Bean처럼 등록하려면 <code>@Component</code> 또는 별도의 <code>@Bean</code> 등록이 필요하다.</p>
<hr />
<h3 id="target">Target</h3>
<p>Target은 Advice가 적용되는 <strong>실제 비즈니스 객체</strong>다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Service
public class UserService {

    public User getUser(Long id) {
        ...
    }
}</code></pre>
<p>에 AOP를 적용했다면</p>
<pre><code class="language-text">UserService
=
Target</code></pre>
<p>이다.</p>
<p>Proxy가 감싸고 있는 실제 원본 객체라고 보면 된다.</p>
<hr />
<h3 id="proxy">Proxy</h3>
<p>Proxy는 Target 앞에 만들어지는 대리 객체다.</p>
<pre><code class="language-text">Controller
    │
    ▼
UserService Proxy
    │
    ▼
UserService Target</code></pre>
<p>실제 호출을 먼저 받아 Advice를 실행하고 Target에게 요청을 위임한다.</p>
<hr />
<h3 id="joinpoint">JoinPoint</h3>
<p>JoinPoint는</p>
<blockquote>
<p><strong>AOP를 적용할 수 있는 실행 지점</strong></p>
</blockquote>
<p>을 의미한다.</p>
<p>일반적인 AOP 개념에서는 여러 실행 지점이 존재할 수 있지만 <strong>Spring AOP는 Spring Bean의 Method 실행을 중심으로 JoinPoint를 제공한다.</strong></p>
<p>그래서 Spring AOP를 처음 이해할 때는</p>
<pre><code class="language-text">JoinPoint
≈ 실행되고 있는 Method 지점</code></pre>
<p>으로 생각해도 좋다.</p>
<p>예를 들어</p>
<pre><code class="language-java">userService.getUser(10L);</code></pre>
<p>이라는 호출이 있다면</p>
<pre><code class="language-text">UserService.getUser()</code></pre>
<p>Method 실행이 JoinPoint가 된다.</p>
<p>Advice에서는 <code>JoinPoint</code> 객체를 이용해서 현재 Method에 대한 정보를 얻을 수 있다.</p>
<pre><code class="language-java">@Before(&quot;serviceMethods()&quot;)
public void before(
        JoinPoint joinPoint
) {

    String methodName =
            joinPoint
                    .getSignature()
                    .getName();
}</code></pre>
<p><code>JoinPoint</code>를 통해 대표적으로</p>
<pre><code class="language-text">어떤 Method인지

어떤 Target인지

어떤 Argument가 들어왔는지</code></pre>
<p>같은 정보를 확인할 수 있다.</p>
<hr />
<h3 id="pointcut">Pointcut</h3>
<p>JoinPoint가</p>
<pre><code class="language-text">&quot;AOP가 적용될 수 있는 Method 실행 지점&quot;</code></pre>
<p>이라면 Pointcut은</p>
<blockquote>
<p><strong>그중 실제로 Advice를 적용할 대상을 선택하는 조건</strong></p>
</blockquote>
<p>이다.</p>
<p>예를 들어 Service Package의 모든 Method에 Logging을 적용하고 싶다고 하자.</p>
<pre><code class="language-java">@Pointcut(
    &quot;execution(* com.example.service.*.*(..))&quot;
)
public void serviceMethods() {
}</code></pre>
<p>이 Pointcut은</p>
<pre><code class="language-text">수많은 Method 실행 지점
        │
        ▼
Pointcut 조건 적용
        │
        ▼
Service Method만 선택</code></pre>
<p>하는 역할을 한다.</p>
<p>정리하면</p>
<pre><code class="language-text">JoinPoint
→ 후보가 될 수 있는 실행 지점

Pointcut
→ 그중 어디에 적용할지 선택하는 조건</code></pre>
<p>이다.</p>
<hr />
<h3 id="advice">Advice</h3>
<p>Pointcut을 통해</p>
<pre><code class="language-text">어디에 적용할지</code></pre>
<p>정했다면,</p>
<p>실제로 실행할 기능이 필요하다.</p>
<p>그것이 <strong>Advice</strong>다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Before(&quot;serviceMethods()&quot;)
public void before(
        JoinPoint joinPoint
) {

    System.out.println(&quot;실행 전&quot;);
}</code></pre>
<p>에서</p>
<pre><code class="language-text">System.out.println(&quot;실행 전&quot;);</code></pre>
<p>같은 실제 공통 기능이 Advice다.</p>
<p>즉</p>
<pre><code class="language-text">Pointcut
→ 어디에?

Advice
→ 무엇을?</code></pre>
<p>이라고 생각하면 쉽다.</p>
<hr />
<h3 id="aspect-정리">Aspect 정리</h3>
<p>예를 들어</p>
<pre><code class="language-java">@Aspect
@Component
public class LoggingAspect {

    @Pointcut(
        &quot;execution(* com.example.service.*.*(..))&quot;
    )
    public void serviceMethods() {
    }

    @Before(&quot;serviceMethods()&quot;)
    public void before(
            JoinPoint joinPoint
    ) {

        System.out.println(
            &quot;[Before] &quot;
            + joinPoint.getSignature()
        );
    }
}</code></pre>
<p>가 있다고 하자.</p>
<p>이를 해석하면</p>
<pre><code class="language-text">Aspect
→ Logging이라는 공통 관심사를 모아둔 Class

Pointcut
→ Service의 Method를 선택

Advice
→ Method 실행 전에 Logging 수행

JoinPoint
→ 현재 실행 중인 Method에 대한 정보

Target
→ 실제 Service 객체

Proxy
→ Target 앞에서 Advice를 실행하는 객체</code></pre>
<p>가 된다.</p>
<hr />
<h4 id="pointcut-표현식">Pointcut 표현식</h4>
<p>Pointcut에서 가장 많이 볼 수 있는 것이 <code>execution</code>이다.</p>
<pre><code class="language-java">execution(* com.example.service.*.*(..))</code></pre>
<p>처음 보면 암호처럼 보인다.</p>
<p>하나씩 쪼개보자.</p>
<pre><code class="language-text">execution(
    *
    com.example.service.*
    .*
    (..)
)</code></pre>
<p>대략 다음 의미다.</p>
<pre><code class="language-text">*
→ 모든 반환 타입

com.example.service.*
→ 해당 Package의 Class

.*
→ 모든 Method

(..)
→ Parameter 개수와 타입에 관계없이</code></pre>
<p>즉</p>
<blockquote>
<p><strong><code>com.example.service</code> Package의 모든 Class에 있는 모든 Method 실행</strong></p>
</blockquote>
<p>을 대상으로 한다.</p>
<p>Spring AOP에서 <code>execution</code>은 Method 실행을 선택하는 대표적인 Pointcut Designator다.</p>
<hr />
<h4 id="within">within</h4>
<p>특정 Class 또는 Package 내부의 Method를 대상으로 할 수도 있다.</p>
<pre><code class="language-java">@Pointcut(
    &quot;within(com.example.service..*)&quot;
)
public void serviceLayer() {
}</code></pre>
<p>여기서</p>
<pre><code class="language-text">*
→ 하나의 이름 영역

..
→ 하위 Package까지 포함</code></pre>
<p>으로 이해할 수 있다.</p>
<p>따라서</p>
<pre><code class="language-text">com.example.service..*</code></pre>
<p>는 <code>service</code>와 하위 Package 영역을 대상으로 사용할 수 있다.</p>
<hr />
<h4 id="bean">bean</h4>
<p>Spring Bean의 이름을 기준으로 선택할 수도 있다.</p>
<pre><code class="language-java">@Pointcut(&quot;bean(orderService)&quot;)
public void orderService() {
}</code></pre>
<p>또는</p>
<pre><code class="language-java">@Pointcut(&quot;bean(*Service)&quot;)
public void allServices() {
}</code></pre>
<p>처럼 Pattern도 사용할 수 있다.</p>
<p>즉</p>
<pre><code class="language-text">execution
→ Method Signature 기준

within
→ Class / Package 기준

bean
→ Spring Bean 이름 기준</code></pre>
<p>으로 볼 수 있다.</p>
<hr />
<h4 id="annotation">@annotation</h4>
<p>개인적으로 Spring AOP에서 굉장히 직관적인 방식이 Annotation 기반 Pointcut이다.</p>
<p>예를 들어 직접 Annotation을 만든다.</p>
<pre><code class="language-java">@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Metrics {
}</code></pre>
<p>그리고 원하는 Method에 붙인다.</p>
<pre><code class="language-java">@Metrics
public User getUser(Long id) {

    ...
}</code></pre>
<p>Pointcut은 다음처럼 정의할 수 있다.</p>
<pre><code class="language-java">@Pointcut(
    &quot;@annotation(com.example.aop.Metrics)&quot;
)
public void metrics() {
}</code></pre>
<p>이제</p>
<pre><code class="language-text">@Metrics가 붙은 Method</code></pre>
<p>만 AOP 대상이 된다.</p>
<hr />
<h4 id="advice의-종류">Advice의 종류</h4>
<p>Spring AOP에서는 대표적으로 다섯 가지 Advice 유형을 사용한다.</p>
<table>
<thead>
<tr>
<th>Advice</th>
<th>실행 시점</th>
</tr>
</thead>
<tbody><tr>
<td><code>@Before</code></td>
<td>Method 실행 전</td>
</tr>
<tr>
<td><code>@After</code></td>
<td>Method 종료 후, 정상/예외와 관계없이</td>
</tr>
<tr>
<td><code>@AfterReturning</code></td>
<td>정상적으로 반환된 후</td>
</tr>
<tr>
<td><code>@AfterThrowing</code></td>
<td>예외가 발생한 후</td>
</tr>
<tr>
<td><code>@Around</code></td>
<td>Method 전체 실행을 감쌈</td>
</tr>
</tbody></table>
<p>하나씩 보면 더 쉽다.</p>
<hr />
<h5 id="before">@Before</h5>
<p>Target Method가 실행되기 전에 실행한다.</p>
<pre><code class="language-java">@Before(&quot;serviceMethods()&quot;)
public void before(
        JoinPoint joinPoint
) {

    System.out.println(&quot;Method 실행 전&quot;);
}</code></pre>
<p>흐름은</p>
<pre><code class="language-text">호출
 │
 ▼
Proxy
 │
 ▼
@Before
 │
 ▼
Target Method</code></pre>
<p>이다.</p>
<p>로그를 남기거나 Method 실행 전에 필요한 정보를 확인할 때 사용할 수 있다.</p>
<hr />
<h5 id="after">@After</h5>
<p>Target Method가 끝난 뒤 실행한다.</p>
<pre><code class="language-java">@After(&quot;serviceMethods()&quot;)
public void after(
        JoinPoint joinPoint
) {

    System.out.println(&quot;Method 종료&quot;);
}</code></pre>
<p><code>@After</code>는 정상적으로 Return했든 예외가 발생했든 최종적으로 실행되는 성격이다.</p>
<pre><code class="language-text">Target 성공 ──┐
              ├─▶ @After
Target 예외 ──┘</code></pre>
<p><code>finally</code>와 비슷한 느낌으로 이해할 수 있다.</p>
<hr />
<h5 id="afterreturning">@AfterReturning</h5>
<p>Method가 <strong>정상적으로 종료된 경우</strong> 실행한다.</p>
<pre><code class="language-java">@AfterReturning(&quot;serviceMethods()&quot;)
public void success() {

    System.out.println(&quot;정상 종료&quot;);
}</code></pre>
<pre><code class="language-text">Target Method
     │
     ├─ 정상 Return
     │      │
     │      ▼
     │ @AfterReturning
     │
     └─ Exception
            │
            └─ 실행 X</code></pre>
<hr />
<h5 id="afterthrowing">@AfterThrowing</h5>
<p>반대로 예외가 발생한 경우 실행한다.</p>
<pre><code class="language-java">@AfterThrowing(&quot;serviceMethods()&quot;)
public void error() {

    System.out.println(&quot;예외 발생&quot;);
}</code></pre>
<pre><code class="language-text">Target Method
     │
     ├─ 정상 Return
     │      │
     │      └─ 실행 X
     │
     └─ Exception
            │
            ▼
      @AfterThrowing</code></pre>
<hr />
<h5 id="around">@Around</h5>
<p><code>@Around</code>는 다른 Advice보다 조금 특별하다.</p>
<p>Target Method 전체를 감싼다.</p>
<pre><code class="language-java">@Around(&quot;serviceMethods()&quot;)
public Object around(
        ProceedingJoinPoint joinPoint
) throws Throwable {

    System.out.println(&quot;실행 전&quot;);

    Object result =
            joinPoint.proceed();

    System.out.println(&quot;실행 후&quot;);

    return result;
}</code></pre>
<p>흐름은</p>
<pre><code class="language-text">@Around 시작
     │
     ├─ 실행 전 작업
     │
     ▼
joinPoint.proceed()
     │
     ▼
Target Method
     │
     ▼
@Around 복귀
     │
     ├─ 실행 후 작업
     │
     ▼
Return</code></pre>
<p>가 된다.</p>
<hr />
<h5 id="around만-proceedingjoinpoint인-이유">Around만 ProceedingJoinPoint인 이유</h5>
<p>앞에서 <code>@Before</code>는 다음처럼 작성했다.</p>
<pre><code class="language-java">@Before(...)
public void before(
        JoinPoint joinPoint
) {
}</code></pre>
<p>그런데 <code>@Around</code>는</p>
<pre><code class="language-java">@Around(...)
public Object around(
        ProceedingJoinPoint joinPoint
) {
}</code></pre>
<p>를 사용한다.</p>
<p>왜 타입이 다를까?</p>
<p><code>@Before</code>는 단순히 <strong>현재 어떤 Method가 호출되는지에 대한 정보</strong>가 필요하다.</p>
<pre><code class="language-text">JoinPoint

→ Method 정보
→ Target 정보
→ Argument 정보</code></pre>
<p>하지만 <code>@Around</code>는 Target Method의 실행 자체를 제어해야 한다.</p>
<pre><code class="language-java">joinPoint.proceed();</code></pre>
<p>를 호출해야 실제 Target Method가 실행된다.</p>
<p>그래서 <code>ProceedingJoinPoint</code>에는</p>
<blockquote>
<p><strong>“이제 실제 Method를 계속 실행해라.”</strong></p>
</blockquote>
<p>라는 의미의 <code>proceed()</code>가 존재한다.</p>
<pre><code class="language-text">JoinPoint
→ 실행 지점에 대한 정보

ProceedingJoinPoint
→ 실행 지점 정보
  +
  실제 실행을 계속 진행하는 proceed()</code></pre>
<p>라고 이해하면 된다.</p>
<hr />
<h3 id="실행-시간-측정-예시">실행 시간 측정 예시</h3>
<p>예를 들어 Service Method의 실행 시간을 측정한다고 하자.</p>
<pre><code class="language-java">@Around(
    &quot;execution(* com.example.service.*.*(..))&quot;
)
public Object measure(
        ProceedingJoinPoint joinPoint
) throws Throwable {

    long start =
            System.currentTimeMillis();

    try {

        return joinPoint.proceed();

    } finally {

        long elapsed =
                System.currentTimeMillis()
                - start;

        System.out.println(
            joinPoint
                .getSignature()
                .getName()
            + &quot; : &quot;
            + elapsed
            + &quot;ms&quot;
        );
    }
}</code></pre>
<p>실제 구조는</p>
<pre><code class="language-text">Service Method 호출
        │
        ▼
AOP Proxy
        │
        ├─ start 시간 측정
        │
        ▼
Target Service Method
        │
        ▼
AOP Proxy
        │
        ├─ 종료 시간 측정
        ├─ 소요 시간 계산
        ▼
Return</code></pre>
<p>이다.</p>
<p>비즈니스 Method는 실행 시간 측정에 대해 아무것도 알 필요가 없다.</p>
<pre><code class="language-java">public User getUser(Long id) {

    return ...;
}</code></pre>
<p>이게 AOP를 사용하는 이유를 아주 잘 보여주는 예다.</p>
<hr />
<h1 id="bean과-aop">Bean과 AOP</h1>
<p>이제 IoC Container와 AOP를 하나로 연결해보자.</p>
<p>우리가 다음 Bean을 만들었다.</p>
<pre><code class="language-java">@Service
public class UserService {

    public User getUser(Long id) {
        ...
    }
}</code></pre>
<p>그리고 해당 Bean Method가 AOP 대상이라고 하자.</p>
<p>개념적으로 Spring은 Target Bean을 준비한 뒤 Proxy를 통해 호출이 가로채질 수 있는 구조를 만든다.</p>
<pre><code class="language-text">원본

UserService Bean</code></pre>
<p>AOP가 적용되면 호출 구조는</p>
<pre><code class="language-text">Spring IoC Container

┌───────────────────────────────┐
│                               │
│   UserService Proxy           │
│          │                    │
│          ▼                    │
│   UserService Target          │
│                               │
└───────────────────────────────┘</code></pre>
<p>가 된다.</p>
<p>다른 Bean이 <code>UserService</code>를 주입받아 호출하면 Proxy Reference를 통해 호출이 들어간다.</p>
<pre><code class="language-text">Controller
     │
     ▼
UserService Proxy
     │
     ├─ Advice
     │
     ▼
UserService Target</code></pre>
<p>AOP 대상 Bean이 Proxy로 Wrapping되어 외부 호출이 Proxy를 거치도록 하는 구조가 Spring AOP의 핵심이다.</p>
<hr />
<h2 id="transactional">@Transactional</h2>
<p>이제 Spring에서 자주 보게 되는 Annotation들이 왜 Proxy와 관련 있는지 이해할 수 있다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Transactional
public void order() {

    ...
}</code></pre>
<p>라는 Method가 있다.</p>
<p>개념적으로는</p>
<pre><code class="language-text">호출자
   │
   ▼
Transactional Proxy
   │
   ├─ Transaction 시작
   │
   ▼
Target.order()
   │
   ▼
Transactional Proxy
   │
   ├─ Commit / Rollback
   ▼
호출자</code></pre>
<p>같은 구조를 생각할 수 있다.</p>
<p>핵심 비즈니스 Method 안에는 Transaction 관리 코드가 없다.</p>
<pre><code class="language-java">public void order() {

    decreaseStock();
    createOrder();
}</code></pre>
<p>Transaction이라는 횡단 관심사가 Proxy 영역으로 분리된 것이다.</p>
<p><code>@Async</code>, Method Validation, Cache 등도 이런 <strong>Spring이 Bean 호출을 가로채 부가기능을 적용할 수 있는 구조</strong>를 이해하고 나면 훨씬 자연스럽게 볼 수 있다.</p>
<hr />
<h2 id="유의사항">유의사항</h2>
<p>Proxy 구조를 이해하면 Spring에서 굉장히 유명한 문제 하나도 자연스럽게 이해할 수 있다.</p>
<p><strong>자기 자신 내부 호출(Self Invocation)</strong>이다.</p>
<p>다음 코드가 있다고 하자.</p>
<pre><code class="language-java">@Service
public class UserService {

    public void outer() {

        inner();
    }

    @Transactional
    public void inner() {

        ...
    }
}</code></pre>
<p>외부 객체가 <code>inner()</code>를 호출하면</p>
<pre><code class="language-text">Controller
    │
    ▼
UserService Proxy
    │
    ├─ @Transactional 처리
    │
    ▼
UserService.inner()</code></pre>
<p>처럼 Proxy를 통과할 수 있다.</p>
<p>그런데 <code>outer()</code>가 실행된 뒤 내부에서</p>
<pre><code class="language-java">inner();</code></pre>
<p>를 호출하면 상황이 다르다.</p>
<p>이미 Target 객체 내부에 들어와 있다.</p>
<pre><code class="language-text">Controller
    │
    ▼
Proxy
    │
    ▼
UserService Target
    │
    │ outer()
    │
    └──▶ inner()</code></pre>
<p><code>outer()</code>에서 <code>inner()</code>로 가는 호출은 다시 Proxy 밖으로 나갔다 들어오는 것이 아니다.</p>
<p>Target 내부에서</p>
<pre><code class="language-text">this.inner()</code></pre>
<p>에 가까운 직접 호출이 발생한다.</p>
<p>따라서</p>
<pre><code class="language-text">Proxy
→ 우회</code></pre>
<p>하게 된다.</p>
<p>Spring 공식 문서 역시 Proxy 기반 Spring AOP에서는 Target 내부에서 발생한 자기 호출이 Proxy에 의해 다시 intercept되지 않는다고 설명한다.</p>
<hr />
<h1 id="aop-사용-흐름-정리">AOP 사용 흐름 정리</h1>
<p>다음 Aspect가 있다고 하자.</p>
<pre><code class="language-java">@Aspect
@Component
public class LoggingAspect {

    @Pointcut(
        &quot;execution(* com.example.service.*.*(..))&quot;
    )
    public void serviceMethods() {
    }

    @Before(&quot;serviceMethods()&quot;)
    public void before(
            JoinPoint joinPoint
    ) {

        System.out.println(
            &quot;Method 시작&quot;
        );
    }

    @Around(&quot;serviceMethods()&quot;)
    public Object around(
            ProceedingJoinPoint joinPoint
    ) throws Throwable {

        long start =
                System.currentTimeMillis();

        try {

            return joinPoint.proceed();

        } finally {

            long elapsed =
                    System.currentTimeMillis()
                    - start;

            System.out.println(
                &quot;실행 시간: &quot;
                + elapsed
            );
        }
    }
}</code></pre>
<p>그리고 다음 Method가 있다.</p>
<pre><code class="language-java">@Service
public class UserService {

    public User getUser(Long id) {

        return ...;
    }
}</code></pre>
<p>Controller에서 호출한다.</p>
<pre><code class="language-java">userService.getUser(10L);</code></pre>
<p>전체 흐름은 다음처럼 이해할 수 있다.</p>
<pre><code class="language-text">Controller

userService.getUser(10)
        │
        ▼
──────────────────────────
      AOP Proxy
──────────────────────────
        │
        ├─ Pointcut 확인
        │
        ├─ @Around 시작
        │
        ├─ @Before 실행
        │
        ▼
──────────────────────────
      Target Bean
──────────────────────────
        │
        ▼
UserService.getUser(10)
        │
        ▼
Return
        │
        ▼
──────────────────────────
      AOP Proxy
──────────────────────────
        │
        ├─ Around 후처리
        │
        ▼
Controller</code></pre>
<p>이제</p>
<pre><code class="language-text">Aspect
Pointcut
Advice
JoinPoint
Target
Proxy</code></pre>
<p>라는 용어가 하나의 구조 안에서 연결된다.</p>
<hr />
<h1 id="전체-구조">전체 구조</h1>
<p>지금까지 배운 Spring의 흐름에 Proxy까지 추가하면 다음과 같이 볼 수 있다.</p>
<pre><code class="language-text">                 Spring IoC Container

┌────────────────────────────────────────┐
│                                        │
│  Controller Bean                       │
│       │                                │
│       ▼                                │
│  Service Proxy                         │
│       │                                │
│       ├─ Advice                        │
│       │                                │
│       ▼                                │
│  Service Target                        │
│       │                                │
│       ▼                                │
│  Repository Bean                       │
│                                        │
└────────────────────────────────────────┘</code></pre>
<p>HTTP Request 흐름으로 보면</p>
<pre><code class="language-text">Client
  │
  ▼
Tomcat
  │
  ▼
DispatcherServlet
  │
  ▼
Controller
  │
  ▼
Service Proxy
  │
  ├─ Logging
  ├─ Transaction
  ├─ Validation
  ├─ Async
  │
  ▼
Service Target
  │
  ▼
Repository</code></pre>
<p>정도로 큰 구조를 생각할 수 있다.</p>
<p>물론 모든 기능이 항상 같은 Proxy 하나에서 동일하게 처리된다는 의미는 아니다.</p>
<p>중요한 것은 <strong>Spring의 여러 선언적 기능이 Bean Method 호출을 가로채는 Proxy 구조와 밀접하게 연결되어 있다</strong>는 점이다.</p>
<hr />
<h1 id="정리">정리</h1>
<p>Proxy Pattern의 핵심부터 다시 보면</p>
<pre><code class="language-text">Client
  │
  ▼
Proxy
  │
  ▼
Target</code></pre>
<p>이다.</p>
<p>Proxy는 Target 대신 호출을 받아 실제 Method 호출 전후에 추가 기능을 수행할 수 있다.</p>
<pre><code class="language-text">Proxy

실행 전 기능
     │
     ▼
Target Method
     │
     ▼
실행 후 기능</code></pre>
<p>Spring은 이를 Dynamic Proxy 형태로 자동화할 수 있으며 대표적으로 JDK Dynamic Proxy와 CGLIB 기반 Proxy가 사용된다.</p>
<p>그리고 Proxy를 직접 하나씩 작성하지 않고</p>
<pre><code class="language-text">어디에 적용할 것인가?

무엇을 실행할 것인가?

언제 실행할 것인가?</code></pre>
<p>를 선언적으로 분리한 것이 Spring AOP를 이해하는 핵심이다.</p>
<pre><code class="language-text">Aspect
→ 공통 관심사를 모아놓은 단위

JoinPoint
→ AOP가 적용될 수 있는 Method 실행 지점

Pointcut
→ 어떤 JoinPoint를 대상으로 할 것인지

Advice
→ 실제로 수행할 공통 기능

Target
→ 실제 비즈니스 객체

Proxy
→ Target을 감싸 호출을 가로채는 객체</code></pre>
<p>Advice는 실행 시점에 따라</p>
<pre><code class="language-text">@Before

@After

@AfterReturning

@AfterThrowing

@Around</code></pre>
<p>으로 나눌 수 있다.</p>
<p>특히 <code>@Around</code>는</p>
<pre><code class="language-java">joinPoint.proceed();</code></pre>
<p>를 통해 실제 Target Method 실행 자체를 제어할 수 있기 때문에 Method 실행 전후를 모두 다룰 수 있다.</p>
<p>그리고 Spring Proxy에서 가장 중요한 주의점은 <strong>Proxy를 통과해야 부가기능이 적용된다는 것</strong>이다.</p>
<pre><code class="language-text">외부 호출

Caller
  │
  ▼
Proxy
  │
  ▼
Target

→ AOP 적용 가능</code></pre>
<p>반면</p>
<pre><code class="language-text">내부 호출

Target.outer()
    │
    ▼
Target.inner()

→ Proxy 우회</code></pre>
<p>가 될 수 있다.</p>
<p>그래서 <code>@Transactional</code>, AOP Advice와 같은 Proxy 기반 기능을 사용할 때</p>
<blockquote>
<p><strong>“Annotation이 붙어 있는가?”</strong></p>
</blockquote>
<p>뿐만 아니라</p>
<blockquote>
<p><strong>“이 호출이 Proxy를 통과하는가?”</strong></p>
</blockquote>
<p>를 함께 생각해야 한다.</p>
<p>지난 글에서 Spring Container가</p>
<pre><code class="language-text">Bean 생성
DI
Bean 관리</code></pre>
<p>를 담당한다고 했다.</p>
<p>이번 글까지 연결하면 한 단계 더 확장된다.</p>
<pre><code class="language-text">Spring IoC Container
       │
       ├─ Bean 생성
       ├─ DI
       ├─ Bean 관리
       │
       └─ 필요하면 Proxy 적용
                    │
                    ├─ AOP
                    ├─ Transaction
                    ├─ Validation
                    ├─ Async
                    └─ Cache</code></pre>
<p>즉 Spring에서 Proxy는 단순한 디자인 패턴 하나가 아니라,</p>
<p><strong>Spring의 여러 선언적 기능을 이해하기 위한 핵심 기반 구조</strong>다.</p>
<p>다음에는 이 Proxy 구조 위에서 동작하는 기능 중 하나인 <strong>입력값 검증과 Bean Validation</strong>을 살펴본다.</p>