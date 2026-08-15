<p>지난 글에서는 Spring MVC에서 HTTP Request가 어떻게 우리가 작성한 Controller까지 도달하는지 살펴봤다.</p>
<pre><code class="language-text">Client
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
Repository</code></pre>
<p>그리고 한 가지 질문이 남았다.</p>
<pre><code class="language-java">@RestController
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }
}</code></pre>
<p>우리는 어디에서도 다음과 같이 객체를 직접 생성하지 않았다.</p>
<pre><code class="language-java">UserService userService = new UserService();
UserController controller = new UserController(userService);</code></pre>
<p>그런데 Spring Boot를 실행하면 <code>UserController</code>도 존재하고 <code>UserService</code>도 존재한다.</p>
<p>심지어 <code>UserController</code> 안에는 필요한 <code>UserService</code>까지 이미 들어가 있다.</p>
<pre><code class="language-text">UserController
      │
      ▼
UserService</code></pre>
<p><strong>이 객체들은 누가 만들고, 누가 서로 연결해주는 걸까?</strong></p>
<p>이 질문에서 Spring의 핵심 개념인 <strong>DI와 IoC</strong>가 시작된다.</p>
<hr />
<h1 id="dependency">Dependency</h1>
<p>DI를 이해하려면 먼저 <strong>Dependency</strong>, 즉 의존성부터 알아야 한다.</p>
<p>의존성이란</p>
<blockquote>
<p><strong>어떤 객체가 자신의 기능을 수행하기 위해 다른 객체를 필요로 하는 관계</strong></p>
</blockquote>
<p>를 의미한다.</p>
<p>예를 들어 <code>UserController</code>가 사용자 조회를 직접 처리하지 않고 <code>UserService</code>에게 요청한다고 하자.</p>
<pre><code class="language-java">public class UserController {

    private UserService userService;

    public User getUser(Long id) {
        return userService.getUser(id);
    }
}</code></pre>
<p><code>UserController</code>가 자신의 기능을 수행하려면 <code>UserService</code>가 필요하다.</p>
<pre><code class="language-text">UserController
      │
      │ 사용
      ▼
UserService</code></pre>
<p>그래서</p>
<blockquote>
<p><strong>UserController는 UserService에 의존한다.</strong></p>
</blockquote>
<p>라고 표현한다.</p>
<p>Spring Application에서는 이런 의존 관계가 계속 이어진다.</p>
<pre><code class="language-text">Controller
   │
   │ 의존
   ▼
Service
   │
   │ 의존
   ▼
Repository</code></pre>
<p>Controller는 Service가 필요하고,</p>
<p>Service는 Repository가 필요하다.</p>
<p>여기까지는 자연스럽다.</p>
<p>문제는 다른 곳에 있다.</p>
<blockquote>
<p><strong>그 필요한 객체를 누가 만들 것인가?</strong></p>
</blockquote>
<hr />
<h2 id="직접-객체-생성">직접 객체 생성</h2>
<p>Spring이 없는 일반적인 Java 프로그램에서는 필요한 객체를 직접 만들 수 있다.</p>
<p>간단한 예제를 하나 생각해보자.</p>
<pre><code class="language-java">public interface Americano {
    void get();
}</code></pre>
<p>두 가지 구현체가 존재한다.</p>
<pre><code class="language-java">public class HotAmericano implements Americano {

    @Override
    public void get() {
        System.out.println(&quot;Hot Americano&quot;);
    }
}</code></pre>
<pre><code class="language-java">public class IceAmericano implements Americano {

    @Override
    public void get() {
        System.out.println(&quot;Ice Americano&quot;);
    }
}</code></pre>
<p>그리고 <code>Coffee</code>가 Americano를 사용한다.</p>
<p>Coffee가 사용할 객체까지 직접 만든다면 다음처럼 구현할 수 있다.</p>
<pre><code class="language-java">public class Coffee {

    private Americano americano;

    public Coffee(String type) {

        if (type.equals(&quot;hot&quot;)) {
            americano = new HotAmericano();
        } else if (type.equals(&quot;ice&quot;)) {
            americano = new IceAmericano();
        }
    }

    public void coffeeType() {
        americano.get();
    }
}</code></pre>
<p>구조를 보면 Coffee가 Americano를 <strong>사용하면서 동시에 생성까지 담당</strong>하고 있다.</p>
<pre><code class="language-text">Coffee
   │
   ├─ new HotAmericano()
   │
   └─ new IceAmericano()</code></pre>
<p>Coffee는 자신의 기능을 수행하기 위해</p>
<pre><code class="language-text">Americano를 사용한다.</code></pre>
<p>뿐만 아니라</p>
<pre><code class="language-text">어떤 Americano가 존재하는지

어떤 구현체를 사용할지

그 객체를 어떻게 생성할지</code></pre>
<p>까지 알아야 한다.</p>
<hr />
<h3 id="직접-생성의-문제점">직접 생성의 문제점</h3>
<p>새로운 구현체가 추가됐다고 하자.</p>
<pre><code class="language-java">public class ThinIceAmericano implements Americano {

    @Override
    public void get() {
        System.out.println(&quot;Thin Ice Americano&quot;);
    }
}</code></pre>
<p>그러면 Coffee 역시 수정해야 한다.</p>
<pre><code class="language-java">if (type.equals(&quot;hot&quot;)) {

    americano = new HotAmericano();

} else if (type.equals(&quot;ice&quot;)) {

    americano = new IceAmericano();

} else if (type.equals(&quot;thinIce&quot;)) {

    americano = new ThinIceAmericano();
}</code></pre>
<p>변경된 것은 Americano의 종류인데,</p>
<p>이를 사용하는 Coffee까지 영향을 받았다.</p>
<pre><code class="language-text">Americano 구현 변경
        │
        ▼
Coffee 수정</code></pre>
<p>Coffee가 두 가지 책임을 가지고 있기 때문이다.</p>
<pre><code class="language-text">Americano 사용
+
Americano 생성</code></pre>
<p>그렇다면 이 둘을 분리해볼 수 있다.</p>
<hr />
<h1 id="dependency-injection">Dependency Injection</h1>
<p>Coffee가 Americano를 직접 생성하지 않고 외부에서 받도록 바꿔보자.</p>
<pre><code class="language-java">public class Coffee {

    private final Americano americano;

    public Coffee(Americano americano) {
        this.americano = americano;
    }

    public void coffeeType() {
        americano.get();
    }
}</code></pre>
<p>이제 Coffee 안에는</p>
<pre><code class="language-java">new HotAmericano();
new IceAmericano();</code></pre>
<p>같은 코드가 존재하지 않는다.</p>
<p>Coffee가 아는 것은 단순하다.</p>
<pre><code class="language-java">americano.get();</code></pre>
<p>자신에게 들어온 Americano를 사용하면 된다.</p>
<p>어떤 구현체를 사용할지는 외부에서 결정한다.</p>
<pre><code class="language-java">Coffee hot =
        new Coffee(new HotAmericano());

Coffee ice =
        new Coffee(new IceAmericano());</code></pre>
<p>기존 구조가</p>
<pre><code class="language-text">Coffee
  │
  │ 직접 생성
  ▼
IceAmericano</code></pre>
<p>였다면,</p>
<p>이제는</p>
<pre><code class="language-text">외부
 │
 │ IceAmericano 생성
 │
 ▼
Coffee</code></pre>
<p>가 된다.</p>
<p>이렇게</p>
<blockquote>
<p><strong>객체가 필요한 의존 객체를 직접 생성하지 않고 외부에서 전달받는 것</strong></p>
</blockquote>
<p>을 <strong>Dependency Injection, DI</strong>라고 한다.</p>
<p>이것이 <strong>의존성 주입</strong>이다.</p>
<hr />
<h2 id="생성과-사용의-분리">생성과 사용의 분리</h2>
<p>DI를 단순히</p>
<blockquote>
<p>&quot;<code>new</code>를 사용하지 않는 방식&quot;</p>
</blockquote>
<p>이라고 이해하면 조금 부족하다.</p>
<p>핵심은 <strong>객체를 생성하는 책임과 사용하는 책임을 분리하는 것</strong>이다.</p>
<p>Coffee는 Americano를 사용한다.</p>
<pre><code class="language-text">Coffee
→ Americano를 사용</code></pre>
<p>하지만 어떤 Americano를 생성할지는 다른 곳에서 결정한다.</p>
<pre><code class="language-text">외부
→ Americano 생성 및 선택</code></pre>
<p>따라서 구현체가 바뀌더라도 Coffee 자체를 수정하지 않고 외부의 객체 연결만 바꿀 수 있다.</p>
<pre><code class="language-text">HotAmericano
      │
      ▼
    Coffee</code></pre>
<p>또는</p>
<pre><code class="language-text">IceAmericano
      │
      ▼
    Coffee</code></pre>
<p>처럼 말이다.</p>
<p>객체가 자신의 역할에 조금 더 집중할 수 있게 되는 것이다.</p>
<hr />
<h2 id="spring-더하기">Spring 더하기</h2>
<p>여기서 중요한 점이 있다.</p>
<p>다음 코드도 분명 DI다.</p>
<pre><code class="language-java">Coffee coffee =
        new Coffee(new IceAmericano());</code></pre>
<p>Coffee가 IceAmericano를 직접 만들지 않고 외부에서 전달받았기 때문이다.</p>
<p>하지만 아직 객체를 생성하고 연결하는 것은 <strong>개발자</strong>다.</p>
<pre><code class="language-text">개발자

├─ IceAmericano 생성
├─ Coffee 생성
└─ 두 객체 연결</code></pre>
<p>Spring에서는 이 역할까지 Framework가 가져간다.</p>
<p>여기서 <strong>IoC</strong>가 등장한다.</p>
<hr />
<h1 id="ioc---제어의-역전">IoC - 제어의 역전</h1>
<p>일반적인 Java 프로그램에서는 개발자가 객체의 생성과 연결을 직접 제어한다.</p>
<pre><code class="language-java">UserRepository repository =
        new UserRepository();

UserService service =
        new UserService(repository);

UserController controller =
        new UserController(service);</code></pre>
<p>개발자가</p>
<pre><code class="language-text">어떤 객체를 만들지

어떤 순서로 만들지

어떤 객체를 넣어줄지

객체를 어떻게 연결할지</code></pre>
<p>를 모두 결정한다.</p>
<pre><code class="language-text">개발자

├─ Repository 생성
├─ Service 생성
├─ Controller 생성
└─ 객체 연결</code></pre>
<p>즉 <strong>객체에 대한 제어권이 개발자에게 있다.</strong></p>
<p>Spring에서는 다르다.</p>
<p>우리는 다음처럼 객체와 객체 사이의 관계만 표현한다.</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p><code>UserService</code>는</p>
<pre><code class="language-text">&quot;나는 UserRepository가 필요하다.&quot;</code></pre>
<p>라는 사실만 표현한다.</p>
<p>실제로</p>
<pre><code class="language-text">UserRepository를 만들고

UserService를 만들고

UserRepository를 UserService에 넣는 것</code></pre>
<p>은 Spring이 담당한다.</p>
<pre><code class="language-text">Spring Framework

├─ Repository 생성
├─ Service 생성
├─ Controller 생성
└─ 객체 연결</code></pre>
<p>즉 객체 생성과 관리에 대한 제어권이</p>
<pre><code class="language-text">개발자
   │
   ▼
Spring Framework</code></pre>
<p>로 넘어간다.</p>
<p>이것이 <strong>Inversion of Control</strong>, 즉 <strong>제어의 역전</strong>이다.</p>
<hr />
<h1 id="ioc와-di의-차이">IoC와 DI의 차이</h1>
<p>IoC와 DI는 항상 같이 등장하기 때문에 같은 말처럼 느껴지기 쉽다.</p>
<p>하지만 둘은 <strong>같은 상황을 서로 다른 관점에서 바라본 개념</strong>이다.</p>
<p>다음 코드를 다시 보자.</p>
<pre><code class="language-java">public UserController(UserService userService) {
    this.userService = userService;
}</code></pre>
<h3 id="usercontroller의-입장에서-보면">UserController의 입장에서 보면</h3>
<pre><code class="language-text">&quot;UserService가 필요한데

내가 만들지 않았다.

밖에서 들어왔다.&quot;</code></pre>
<p>즉 <strong>의존성을 주입받았다.</strong></p>
<p>이 관점이 <strong>DI</strong>다.</p>
<p>반대로 Spring Framework의 입장에서 보면</p>
<pre><code class="language-text">&quot;UserService를 내가 만들고

UserController도 내가 만들고

둘을 내가 연결했다.&quot;</code></pre>
<p>객체에 대한 제어권을 Framework가 가지고 있다.</p>
<p>이 관점이 <strong>IoC</strong>다.</p>
<p>정리하면 다음과 같다.</p>
<pre><code class="language-text">IoC
→ 객체 생성과 관리의 제어권은 누구에게 있는가?

DI
→ 객체가 필요한 의존성을 어떻게 전달받는가?</code></pre>
<p>즉 Spring에서는</p>
<blockquote>
<p><strong>IoC라는 큰 원칙을 구현하기 위한 핵심 방법으로 DI를 사용한다.</strong></p>
</blockquote>
<p>라고 이해할 수 있다.</p>
<hr />
<h1 id="spring-ioc-container">Spring IoC Container</h1>
<p>IoC는 하나의 <strong>원칙</strong>이다.</p>
<p>그렇다면 실제로</p>
<pre><code class="language-text">객체를 생성하고

객체를 저장하고

객체를 연결하고

객체를 관리하는</code></pre>
<p>주체가 필요하다.</p>
<p>그것이 <strong>Spring Container</strong>, 정확히는 <strong>IoC Container</strong>다.</p>
<pre><code class="language-text">Spring IoC Container

┌───────────────────────────────┐
│                               │
│   UserController Bean         │
│           │                   │
│           ▼                   │
│   UserService Bean            │
│           │                   │
│           ▼                   │
│   UserRepository Bean         │
│                               │
└───────────────────────────────┘</code></pre>
<p>Spring Container가 담당하는 일을 크게 보면 다음과 같다.</p>
<pre><code class="language-text">Bean 생성
     │
     ▼
의존 관계 확인
     │
     ▼
DI
     │
     ▼
Bean 보관 및 제공
     │
     ▼
생명주기 관리</code></pre>
<p>즉</p>
<pre><code class="language-text">IoC
→ 객체 제어권을 Framework에 맡기는 원칙

IoC Container
→ 그 원칙을 실제로 수행하는 Spring의 Container</code></pre>
<p>라고 구분할 수 있다.</p>
<hr />
<h2 id="bean">Bean</h2>
<p>앞선 글에서 Bean을</p>
<blockquote>
<p><strong>Spring Container가 관리하는 객체</strong></p>
</blockquote>
<p>라고 설명했다.</p>
<p>이제 왜 Spring이 Bean을 관리하는지가 조금 더 명확해진다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Service
public class UserService {
}</code></pre>
<p>라는 클래스가 있다고 하자.</p>
<p>Component Scan을 통해 Spring이 이 클래스를 관리 대상으로 발견한다.</p>
<pre><code class="language-text">@Service
    │
    ▼
Component Scan
    │
    ▼
Bean 대상 발견
    │
    ▼
객체 생성
    │
    ▼
IoC Container에 등록</code></pre>
<p>즉 우리가 지금까지 본 내용이 하나로 연결된다.</p>
<pre><code class="language-text">@Component
@Service
@Controller
@Repository
      │
      ▼
Component Scan
      │
      ▼
Bean 대상 발견
      │
      ▼
IoC Container
      │
      ├─ 객체 생성
      ├─ DI
      └─ Bean 관리</code></pre>
<p>Bean이라는 특별한 종류의 Java 객체가 따로 존재하는 것은 아니다.</p>
<p>결국 일반 Java Object지만,</p>
<p><strong>Spring Container의 관리 대상이 되면 Bean이라고 부르는 것</strong>이다.</p>
<hr />
<h1 id="di-방식">DI 방식</h1>
<p>Spring에서는 대표적으로 세 가지 방식으로 의존성을 주입할 수 있다.</p>
<pre><code class="language-text">생성자 주입
필드 주입
Setter 주입</code></pre>
<p>각 방식은 결국 같은 일을 한다.</p>
<pre><code class="language-text">필요한 Bean
    │
    ▼
다른 Bean에 연결</code></pre>
<p>하지만 의존성을 표현하는 방법이 다르다.</p>
<hr />
<h2 id="생성자-주입">생성자 주입</h2>
<p>가장 일반적으로 권장되는 방식이다.</p>
<pre><code class="language-java">@Service
public class StockService {

    private final StockRepository stockRepository;

    public StockService(
            StockRepository stockRepository
    ) {
        this.stockRepository = stockRepository;
    }
}</code></pre>
<p>생성자를 보면 바로 알 수 있다.</p>
<pre><code class="language-text">StockService를 만들기 위해서는
StockRepository가 필요하다.</code></pre>
<p>즉 객체가 가진 <strong>필수 의존성</strong>이 생성자에 명확하게 나타난다.</p>
<p>Spring은 <code>StockService</code> Bean을 생성할 때 필요한 <code>StockRepository</code> Bean을 찾아 전달한다.</p>
<pre><code class="language-text">StockRepository Bean
        │
        │ 생성자 주입
        ▼
StockService Bean</code></pre>
<hr />
<h3 id="생성자-주입과-final">생성자 주입과 final</h3>
<p>생성자 주입에서는 다음처럼 <code>final</code>을 자주 사용한다.</p>
<pre><code class="language-java">private final StockRepository stockRepository;</code></pre>
<p><code>StockRepository</code>는 <code>StockService</code>가 만들어질 때 한 번 전달되고 이후 다른 객체로 변경되지 않는다.</p>
<pre><code class="language-text">StockService 생성
       │
       ▼
StockRepository 주입
       │
       ▼
이후 변경하지 않음</code></pre>
<p>의존성이</p>
<pre><code class="language-text">반드시 존재해야 하고
+
객체가 살아 있는 동안 유지되어야 한다.</code></pre>
<p>는 의도를 코드로 명확하게 표현할 수 있다.</p>
<hr />
<h3 id="의존성-가독성">의존성 가독성</h3>
<p>다음 클래스를 보자.</p>
<pre><code class="language-java">public OrderService(
        UserRepository userRepository,
        ProductRepository productRepository,
        OrderRepository orderRepository
) {
}</code></pre>
<p>생성자만 봐도 <code>OrderService</code>가 무엇을 필요로 하는지 알 수 있다.</p>
<pre><code class="language-text">OrderService

├─ UserRepository 필요
├─ ProductRepository 필요
└─ OrderRepository 필요</code></pre>
<p>클래스의 의존 관계가 명확하게 드러나는 것이다.</p>
<hr />
<h3 id="테스트-편리성">테스트 편리성</h3>
<p>Spring Container가 없어도 직접 객체를 만들 수 있다.</p>
<pre><code class="language-java">UserService userService =
        new UserService(fakeUserRepository);</code></pre>
<p>운영 환경에서는 실제 Repository를 전달하고</p>
<pre><code class="language-text">UserService
    │
    ▼
Real Repository</code></pre>
<p>테스트에서는 테스트용 객체를 전달할 수 있다.</p>
<pre><code class="language-text">UserService
    │
    ▼
Fake Repository</code></pre>
<p>객체가 자신의 의존성을 직접 생성하지 않기 때문에 가능한 구조다.</p>
<hr />
<h2 id="field-injection">Field Injection</h2>
<p>Field에 직접 Bean을 주입할 수도 있다.</p>
<pre><code class="language-java">@Service
public class StockService {

    @Autowired
    private StockRepository stockRepository;
}</code></pre>
<p>코드는 굉장히 간단하다.</p>
<p>하지만 의존성이 생성자에 드러나지 않는다.</p>
<pre><code class="language-java">new StockService();</code></pre>
<p>라는 코드만 보면 아무런 의존성이 없는 객체처럼 보이지만,</p>
<p>실제로는 <code>StockRepository</code> 없이는 정상적으로 동작하지 않는다.</p>
<p>또한 Field를 <code>final</code>로 두기 어렵고,</p>
<p>Spring Container 없이 순수 Java 객체로 테스트하기도 상대적으로 불편하다.</p>
<p>그래서 일반적인 Application 코드에서는 <strong>생성자 주입을 더 권장</strong>한다.</p>
<hr />
<h2 id="setter-injection">Setter Injection</h2>
<p>Setter Method를 통해 의존성을 주입할 수도 있다.</p>
<pre><code class="language-java">@Service
public class StockService {

    private StockRepository stockRepository;

    @Autowired
    public void setStockRepository(
            StockRepository stockRepository
    ) {
        this.stockRepository = stockRepository;
    }
}</code></pre>
<p>흐름은 다음과 같다.</p>
<pre><code class="language-text">StockService 생성
       │
       ▼
Setter 호출
       │
       ▼
StockRepository 주입</code></pre>
<p>생성자 주입과 달리 객체가 먼저 만들어진 후 의존성이 들어간다.</p>
<p>그리고 Setter가 존재하기 때문에 이후 다른 값으로 변경할 수도 있다.</p>
<p>그래서 보통</p>
<pre><code class="language-text">필수 의존성
→ 생성자 주입

선택적으로 변경 가능한 의존성
→ Setter 주입</code></pre>
<p>이라는 식으로 생각할 수 있다.</p>
<hr />
<h2 id="세-가지-주입-방식">세 가지 주입 방식</h2>
<p>정리하면 다음과 같다.</p>
<table>
<thead>
<tr>
<th>방식</th>
<th>특징</th>
</tr>
</thead>
<tbody><tr>
<td>생성자 주입</td>
<td>필수 의존성이 명확하고 <code>final</code> 사용 가능</td>
</tr>
<tr>
<td>Field 주입</td>
<td>코드가 간단하지만 의존성이 숨겨지고 테스트가 불편</td>
</tr>
<tr>
<td>Setter 주입</td>
<td>객체 생성 이후 선택적으로 의존성을 넣거나 변경 가능</td>
</tr>
</tbody></table>
<p>일반적인 Spring Application에서는</p>
<blockquote>
<p><strong>필수 의존성은 생성자 주입을 기본으로 사용한다.</strong></p>
</blockquote>
<p>라고 생각하면 된다.</p>
<hr />
<h2 id="autowired">@Autowired</h2>
<p>그렇다면 <code>@Autowired</code>는 무엇일까?</p>
<p>간단하게 말하면 Spring에게</p>
<blockquote>
<p><strong>여기에 필요한 Bean을 주입해야 한다.</strong></p>
</blockquote>
<p>고 알려주는 Annotation이다.</p>
<p>Field Injection에서는</p>
<pre><code class="language-java">@Autowired
private StockRepository stockRepository;</code></pre>
<p>처럼 사용한다.</p>
<p>Setter Injection에서는</p>
<pre><code class="language-java">@Autowired
public void setStockRepository(
        StockRepository stockRepository
) {
    this.stockRepository = stockRepository;
}</code></pre>
<p>처럼 사용할 수 있다.</p>
<p>일반 Java Method는 Spring이 임의로 호출하지 않기 때문에,</p>
<p>Setter Injection에서는 이 Method가 의존성 주입을 위한 Method라는 것을 알려줘야 한다.</p>
<hr />
<h3 id="생성자에는-왜-autowired가-없을까">생성자에는 왜 @Autowired가 없을까?</h3>
<p>Spring 코드에서는 다음 형태를 자주 볼 수 있다.</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p><code>@Autowired</code>가 없다.</p>
<p>클래스에 생성자가 하나만 존재하는 경우 Spring은 해당 생성자를 사용해 의존성을 주입할 수 있기 때문에 <code>@Autowired</code>를 생략할 수 있다.</p>
<p>그래서 요즘 흔히 보게 되는 구조가</p>
<pre><code class="language-java">private final UserRepository userRepository;

public UserService(
        UserRepository userRepository
) {
    this.userRepository = userRepository;
}</code></pre>
<p>다.</p>
<p>중요한 것은 <code>@Autowired</code>라는 Annotation 자체가 아니다.</p>
<p>핵심은</p>
<pre><code class="language-text">UserService
      │
      │ 필요
      ▼
UserRepository</code></pre>
<p>라는 의존 관계가 존재하고,</p>
<p>Spring Container가 그 관계를 찾아 실제 Bean을 연결한다는 것이다.</p>
<hr />
<h1 id="spring-container의-실제-모습">Spring Container의 실제 모습</h1>
<p>지금까지 계속 <strong>Spring Container</strong>라고 불렀다.</p>
<p>Spring에서는 Container 기능의 중심에 <code>BeanFactory</code>와 <code>ApplicationContext</code>가 있다.</p>
<hr />
<h2 id="beanfactory">BeanFactory</h2>
<p><code>BeanFactory</code>는 Spring Container의 가장 기본적인 Bean 관리 기능을 제공한다.</p>
<p>이름 그대로</p>
<pre><code class="language-text">Bean 생성
Bean 조회
Bean 관리</code></pre>
<p>와 같은 기본적인 역할을 담당한다.</p>
<hr />
<h2 id="applicationcontext">ApplicationContext</h2>
<p>실제 Spring Application에서는 일반적으로 <strong>ApplicationContext</strong>를 중심으로 동작한다.</p>
<p>ApplicationContext는 BeanFactory의 Bean 관리 기능을 포함하면서</p>
<pre><code class="language-text">환경 설정

Event

Message 처리

AOP 지원

다양한 Spring 기능</code></pre>
<p>등을 함께 제공한다.</p>
<p>따라서 Spring Boot를 사용하면서 우리가 흔히 말하는</p>
<pre><code class="language-text">Spring Container
IoC Container</code></pre>
<p>는 실제 Application에서는 <strong>ApplicationContext를 중심으로 이해하면 된다.</strong></p>
<hr />
<h1 id="spring-boot가-시작될-때">Spring Boot가 시작될 때</h1>
<p>이제 이전 글에서 봤던 Component Scan과 IoC를 하나로 연결할 수 있다.</p>
<p>Spring Boot Application을 실행하면</p>
<pre><code class="language-java">SpringApplication.run(
        MyappApplication.class,
        args
);</code></pre>
<p>Spring이 Application을 실행하기 위한 Container를 준비한다.</p>
<p>큰 흐름만 보면 다음과 같다.</p>
<pre><code class="language-text">Spring Boot 실행
      │
      ▼
ApplicationContext 준비
      │
      ▼
Component Scan
      │
      ▼
Bean 대상 탐색
      │
      ▼
Bean 생성
      │
      ▼
의존 관계 확인
      │
      ▼
DI
      │
      ▼
Application 준비 완료</code></pre>
<p>즉 HTTP Request가 들어온 뒤에 <code>UserController</code>와 <code>UserService</code>를 만드는 것이 아니다.</p>
<p>Request가 들어오기 전에 이미 Application의 주요 Bean들이 준비되어 있다.</p>
<pre><code class="language-text">Application 시작

UserRepository Bean 생성
        │
        ▼
UserService Bean 생성
        │
        ▼
UserController Bean 생성</code></pre>
<p>그 이후 HTTP Request가 들어오면 이미 만들어진 Bean들이 사용된다.</p>
<pre><code class="language-text">HTTP Request
      │
      ▼
UserController Bean
      │
      ▼
UserService Bean</code></pre>
<hr />
<h2 id="singleton-bean">Singleton Bean</h2>
<p>Spring Container는 기본적으로 Bean을 <strong>Singleton 방식으로 관리</strong>한다.</p>
<p>예를 들어 <code>UserService</code>가 여러 곳에서 필요하다고 해보자.</p>
<pre><code class="language-text">UserController

AdminController

OrderController</code></pre>
<p>각각 UserService를 새로 생성한다면</p>
<pre><code class="language-text">UserService #1
UserService #2
UserService #3</code></pre>
<p>처럼 여러 객체가 필요하다.</p>
<p>Spring Container에서는 기본적으로 하나의 Bean을 만들어 여러 곳에서 사용한다.</p>
<pre><code class="language-text">             UserService Bean
                   ▲
                   │
        ┌──────────┼──────────┐
        │          │          │
UserController  Admin      Order</code></pre>
<p>즉 Container가 이미 만들어 놓은 Bean을 필요한 객체에 전달한다.</p>
<pre><code class="language-text">Bean을 요청할 때마다 새로 생성
X

Container가 관리하는 기존 Bean 제공
O</code></pre>
<p>이 구조 덕분에 객체를 반복해서 생성하지 않고 재사용할 수 있다.</p>
<hr />
<h3 id="유의할-점">유의할 점</h3>
<p>하나의 Bean을 여러 곳에서 공유한다는 것은 주의할 점도 만든다.</p>
<p>다음과 같은 Service가 있다고 하자.</p>
<pre><code class="language-java">@Service
public class UserService {

    private String currentUser;
}</code></pre>
<p>여러 Request가 동시에 같은 <code>UserService</code> Bean을 사용한다면</p>
<pre><code class="language-text">Request A ──┐
            │
            ▼
       UserService
            ▲
            │
Request B ──┘</code></pre>
<p>같은 Field를 공유하게 된다.</p>
<p>따라서 일반적인 Service에서는 Request마다 달라지는 값을 Bean Field에 저장하기보다</p>
<pre><code class="language-java">public User getUser(Long id) {

    String name = ...;

    ...
}</code></pre>
<p>처럼 Method Parameter와 지역 변수를 중심으로 처리하는 것이 자연스럽다.</p>
<p>Spring Bean이 기본적으로 Singleton이라는 사실은 이후 동시성을 이해할 때도 중요한 부분이다.</p>
<hr />
<h1 id="참고-순환-참조">[참고] 순환 참조</h1>
<p>Container가 의존 관계를 자동으로 연결해준다고 해서 어떤 관계든 정상적으로 만들 수 있는 것은 아니다.</p>
<p>다음 구조를 생각해보자.</p>
<pre><code class="language-text">AService
   │
   ▼
BService</code></pre>
<p>그런데 BService 역시 AService를 필요로 한다.</p>
<pre><code class="language-text">AService
   │
   ▼
BService
   │
   ▼
AService</code></pre>
<p>코드로 보면 다음과 같다.</p>
<pre><code class="language-java">@Service
public class AService {

    private final BService bService;

    public AService(BService bService) {
        this.bService = bService;
    }
}</code></pre>
<pre><code class="language-java">@Service
public class BService {

    private final AService aService;

    public BService(AService aService) {
        this.aService = aService;
    }
}</code></pre>
<p>Spring이 <code>AService</code>를 만들려고 한다.</p>
<pre><code class="language-text">AService 생성
   │
   ▼
BService 필요</code></pre>
<p>그래서 BService를 만들려고 한다.</p>
<pre><code class="language-text">BService 생성
   │
   ▼
AService 필요</code></pre>
<p>그런데 AService는 아직 만들어지지 않았다.</p>
<pre><code class="language-text">AService
  ↓
BService
  ↓
AService
  ↓
BService
  ↓
...</code></pre>
<p>객체를 정상적으로 조립할 수 없다.</p>
<p>이것을 <strong>Circular Dependency, 순환 참조</strong>라고 한다.</p>
<hr />
<h2 id="순환-참조는-단순한-spring-설정-문제가-아니다">순환 참조는 단순한 Spring 설정 문제가 아니다</h2>
<p>순환 참조가 발생하면</p>
<pre><code class="language-text">@Autowired를 다른 곳에 붙여볼까?

Setter로 바꿀까?</code></pre>
<p>부터 생각하기 쉽다.</p>
<p>하지만 더 중요한 질문이 있다.</p>
<blockquote>
<p><strong>왜 A와 B가 서로 없으면 존재할 수 없는 구조가 되었을까?</strong></p>
</blockquote>
<p>순환 참조는 객체의 책임과 의존 관계가 지나치게 얽혀 있다는 신호일 수 있다.</p>
<pre><code class="language-text">A가 B에 의존

B도 A에 의존</code></pre>
<p>한다면</p>
<pre><code class="language-text">공통 책임을 다른 객체로 분리하거나

의존 관계의 방향을 다시 잡거나

Interface나 Event 구조로 역할을 분리하는 것</code></pre>
<p>을 고려할 수 있다.</p>
<p>즉 순환 참조는 단순히 Framework가 귀찮게 발생시키는 오류가 아니라,</p>
<p><strong>객체 설계를 다시 확인해보라는 신호</strong>로 보는 것이 좋다.</p>
<hr />
<h1 id="spring의-관계-파악-방법">Spring의 관계 파악 방법</h1>
<p>여기까지 보면 Spring Container가 해야 하는 일이 상당히 많다.</p>
<p>예를 들어 다음 코드를 보자.</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p>Spring은 실행 중에</p>
<pre><code class="language-text">이 Class가 Bean 대상인가?

어떤 생성자가 존재하는가?

생성자의 Parameter는 무엇인가?

UserRepository Bean이 존재하는가?</code></pre>
<p>같은 정보를 알아야 한다.</p>
<p>Java에서는 이를 가능하게 하는 기능 중 하나로 <strong>Reflection</strong>이 있다.</p>
<hr />
<p>ㅇㅇ. 지금 글의 <strong>Reflection 파트가 전체 글에 비해 확실히 얇아.</strong> 현재는 <code>&quot;실행 중에 Class 정보를 볼 수 있다 → @Service를 확인할 수 있다 → 생성자도 확인할 수 있다&quot;</code> 정도에서 바로 끝나서, 앞에서 열심히 설명한 IoC Container가 <strong>“그래서 Reflection으로 실제 뭘 할 수 있는데?”</strong>까지 연결되지는 않는다. ([Velog][1])</p>
<p>다만 Reflection 자체를 Java 문법 강의처럼 깊게 파기보다는, <strong><code>Class 정보 조회 → Annotation 확인 → Constructor 분석 → 필요한 타입 파악 → 객체 동적 생성</code></strong>까지 보여주는 게 이 글의 주제인 IoC/DI와 가장 잘 맞는다. Java Reflection API는 런타임에 클래스·생성자·메서드 등을 조사하고 다룰 수 있고, <code>RUNTIME</code>으로 유지된 Annotation도 조회할 수 있다. ([Oracle 문서][2]) Spring Container 역시 Bean의 생성·조립을 관리한다는 점에서 이 연결이 자연스럽다. ([Home][3])</p>
<p>지금 글의 <strong><code># Spring의 관계 파악 방법</code>부터 <code># 연결해 생각해보기</code> 직전까지</strong>를 아래처럼 바꾸는 걸 추천해.</p>
<hr />
<h1 id="spring은-객체의-정보를-어떻게-알-수-있을까">Spring은 객체의 정보를 어떻게 알 수 있을까?</h1>
<p>지금까지 Spring Container가 다음과 같은 일을 한다고 했다.</p>
<pre><code class="language-text">Bean 대상을 찾고

객체를 생성하고

필요한 의존성을 확인하고

다른 Bean을 주입한다.</code></pre>
<p>그런데 생각해보면 이것도 신기하다.</p>
<p>다음 코드가 있다고 하자.</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p>Spring은 이 코드를 보고 다음 사실들을 알아내야 한다.</p>
<pre><code class="language-text">이 Class에는 @Service가 붙어 있다.

UserService에는 생성자가 있다.

생성자에는 UserRepository가 필요하다.

따라서 UserService를 만들기 전에
UserRepository가 필요하다.</code></pre>
<p>개발자가 Spring에게 하나씩 알려준 것은 아니다.</p>
<p>그런데 Spring은 어떻게 <strong>Class의 구조를 실행 중에 확인할 수 있을까?</strong></p>
<p>여기서 Java의 <strong>Reflection</strong>이 등장한다.</p>
<hr />
<h2 id="reflection">Reflection</h2>
<p>Reflection은 간단하게 말하면</p>
<blockquote>
<p><strong>실행 중인 Java 프로그램이 Class의 구조와 정보를 확인하고, 필요한 경우 동적으로 접근하거나 실행할 수 있도록 하는 기능</strong></p>
</blockquote>
<p>이다.</p>
<p>보통 Java 코드를 작성할 때는 이미 어떤 객체와 Method를 사용할지 알고 있다.</p>
<pre><code class="language-java">UserService userService = new UserService(userRepository);

userService.getUser(10L);</code></pre>
<p>컴파일할 때부터</p>
<pre><code class="language-text">UserService라는 Class를 사용할 것이고

어떤 Constructor를 호출할 것이고

getUser라는 Method를 호출할 것이다.</code></pre>
<p>라는 내용이 코드에 직접 작성되어 있다.</p>
<p>하지만, 이를 실행하고자 하는 프레임워크는 이 맥락을 파악하기 위한 수단이 필요하다.</p>
<p>그 방법이 Reflection이다.</p>
<p>실행 중에 Class 자체를 하나의 정보로 가져와서</p>
<pre><code class="language-text">이 Class의 이름은 무엇인가?

어떤 Constructor가 있는가?

어떤 Field가 있는가?

어떤 Method가 있는가?

어떤 Annotation이 붙어 있는가?</code></pre>
<p>등을 확인할 수 있다.</p>
<hr />
<h3 id="class-다루기">Class 다루기</h3>
<p>예를 들어 다음 Class가 있다고 하자.</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p>Java에서는 다음과 같이 해당 Class의 정보를 가져올 수 있다.</p>
<pre><code class="language-java">Class&lt;?&gt; clazz = UserService.class;</code></pre>
<p>여기서 <code>clazz</code>가 <code>UserService</code> 객체 자체인 것은 아니다.</p>
<pre><code class="language-text">UserService Object
→ 실제로 동작하는 객체

Class&lt;UserService&gt;
→ UserService라는 Class에 대한 정보</code></pre>
<p>라고 구분하면 된다.</p>
<p>예를 들어</p>
<pre><code class="language-java">System.out.println(clazz.getName());</code></pre>
<p>을 이용하면 Class 이름을 확인할 수 있다.</p>
<pre><code class="language-text">com.example.service.UserService</code></pre>
<p>이제 이 <code>Class</code> 객체를 통해 UserService의 구조를 하나씩 들여다볼 수 있다.</p>
<hr />
<h3 id="annotation-확인하기">Annotation 확인하기</h3>
<p>먼저 Spring 입장에서 생각해보자.</p>
<p>Component Scan을 통해 Class를 찾았다고 하더라도 모든 Class를 Bean으로 만들 필요는 없다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Service
public class UserService {
}</code></pre>
<p>처럼 Spring이 관리해야 할 대상인지 구분해야 한다.</p>
<p>Reflection을 이용하면 Class에 특정 Annotation이 존재하는지 확인할 수 있다.</p>
<p>개념적인 코드는 다음과 같다.</p>
<pre><code class="language-java">Class&lt;?&gt; clazz = UserService.class;

boolean isService =
        clazz.isAnnotationPresent(Service.class);</code></pre>
<p>결과가 <code>true</code>라면</p>
<pre><code class="language-text">UserService
    │
    ▼
@Service 존재
    │
    ▼
관리할 대상</code></pre>
<p>이라고 판단할 수 있다.</p>
<p>즉 우리가 코드에 작성한</p>
<pre><code class="language-java">@Service</code></pre>
<p>는 단순히 사람에게 보여주는 주석이 아니다.</p>
<p>Framework가 Runtime에 읽을 수 있는 <strong>Metadata</strong>로 사용할 수 있다.</p>
<hr />
<h3 id="annotation-유효시점">Annotation 유효시점</h3>
<p>모든 Annotation을 실행 중에 읽을 수 있는 것은 아니다.</p>
<p>Annotation에는 <strong>Retention 정책</strong>이 있다.</p>
<p>예를 들어 직접 Annotation을 만든다면 다음처럼 작성할 수 있다.</p>
<pre><code class="language-java">@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface MyService {
}</code></pre>
<p>여기서</p>
<pre><code class="language-java">@Retention(RetentionPolicy.RUNTIME)</code></pre>
<p>은 이 Annotation 정보를 <strong>Runtime까지 유지하겠다</strong>는 의미다.</p>
<p>그래야 프로그램이 실행된 이후에도 Reflection을 통해</p>
<pre><code class="language-java">clazz.isAnnotationPresent(MyService.class);</code></pre>
<p>처럼 Annotation을 확인할 수 있다. Java Reflection API에서도 런타임에 유지된 Annotation을 조회할 수 있다.</p>
<p>구조적으로 보면</p>
<pre><code class="language-text">Source Code

@MyService
public class UserService
        │
        ▼
Compile
        │
        ▼
Runtime에도 Annotation 정보 유지
        │
        ▼
Reflection으로 조회</code></pre>
<p>가 된다.</p>
<p>이런 Metadata 활용이 Spring의 여러 Annotation 기반 기능을 이해하는 데 중요하다.</p>
<hr />
<h3 id="constructor-다루기">Constructor 다루기</h3>
<p>Bean 대상이라는 사실을 알았다고 끝이 아니다.</p>
<p>이제 실제 객체를 만들어야 한다.</p>
<p>Spring이 다음 <code>UserService</code>를 만들려고 한다고 하자.</p>
<pre><code class="language-java">public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p>그런데 그냥</p>
<pre><code class="language-java">new UserService();</code></pre>
<p>할 수 없다.</p>
<p>생성자에 <code>UserRepository</code>가 필요하기 때문이다.</p>
<p>Reflection을 사용하면 Class에 어떤 Constructor가 있는지 확인할 수 있다.</p>
<pre><code class="language-java">Constructor&lt;?&gt;[] constructors =
        clazz.getDeclaredConstructors();</code></pre>
<p>그리고 Constructor의 Parameter 정보도 확인할 수 있다.</p>
<pre><code class="language-java">Constructor&lt;?&gt; constructor =
        constructors[0];

Class&lt;?&gt;[] parameterTypes =
        constructor.getParameterTypes();</code></pre>
<p><code>UserService</code>라면 개념적으로 다음 정보를 얻게 된다.</p>
<pre><code class="language-text">UserService Constructor

UserService(UserRepository)

          │
          ▼

필요한 Parameter

UserRepository</code></pre>
<p>이제 Container 입장에서는</p>
<blockquote>
<p><strong>&quot;UserService를 만들려면 UserRepository가 필요하구나.&quot;</strong></p>
</blockquote>
<p>라는 사실을 알 수 있다.</p>
<hr />
<h2 id="di와-reflection이-연결되는-지점">DI와 Reflection이 연결되는 지점</h2>
<p>여기서 앞에서 배운 DI와 연결된다.</p>
<p>Spring Container 안에 이미 다음 Bean이 있다고 해보자.</p>
<pre><code class="language-text">IoC Container

UserRepository Bean</code></pre>
<p>그리고 Reflection으로 <code>UserService</code> 생성자를 확인했더니</p>
<pre><code class="language-text">UserService
     │
     └─ UserRepository 필요</code></pre>
<p>라는 사실을 알아냈다.</p>
<p>그러면 Container가 관리하고 있는 Bean 중에서 해당 타입을 찾을 수 있다.</p>
<p>개념적으로는</p>
<pre><code class="language-text">UserService 생성 필요
        │
        ▼
Constructor 확인
        │
        ▼
UserRepository Parameter 발견
        │
        ▼
Container에서 UserRepository Bean 탐색
        │
        ▼
발견</code></pre>
<p>이라는 과정이다.</p>
<p>그리고 찾아낸 객체를 Constructor에 넣어준다.</p>
<pre><code class="language-text">UserRepository Bean
        │
        │ DI
        ▼
UserService</code></pre>
<p>앞에서 이야기했던</p>
<blockquote>
<p><strong>Spring이 생성자를 보고 필요한 Bean을 넣어준다.</strong></p>
</blockquote>
<p>라는 말이 조금 더 구체적으로 보이기 시작한다.</p>
<hr />
<h3 id="method-다루기">Method 다루기</h3>
<p>Reflection은 Constructor뿐 아니라 Method도 다룰 수 있다.</p>
<p>예를 들어</p>
<pre><code class="language-java">public class UserService {

    public void hello() {
        System.out.println(&quot;hello&quot;);
    }
}</code></pre>
<p>가 있다면 Method 정보를 가져올 수 있다.</p>
<pre><code class="language-java">Method method =
        UserService.class.getDeclaredMethod(&quot;hello&quot;);</code></pre>
<p>그리고 대상 객체를 전달해 Method를 실행할 수도 있다.</p>
<pre><code class="language-java">method.invoke(userService);</code></pre>
<p>일반적인 호출은</p>
<pre><code class="language-java">userService.hello();</code></pre>
<p>지만 Reflection을 이용하면</p>
<pre><code class="language-text">Method 이름 또는 Metadata 확인
        │
        ▼
Method 객체 획득
        │
        ▼
실행할 객체 전달
        │
        ▼
동적 호출</code></pre>
<p>같은 구조를 만들 수 있다.</p>
<p>Java Reflection API는 Class뿐 아니라 Field, Method, Constructor 등을 조사하고 다룰 수 있도록 제공된다.</p>
<p>앞에서 Spring MVC를 살펴볼 때도</p>
<pre><code class="language-text">HTTP Request
      │
      ▼
Controller Method 탐색
      │
      ▼
Method 실행</code></pre>
<p>같은 구조가 있었다.</p>
<p>Framework가 <strong>Runtime에 어떤 객체와 Method를 사용할지 결정해야 하는 곳</strong>에서 Reflection이라는 기술이 중요한 기반 중 하나가 되는 이유다.</p>
<hr />
<h3 id="reflection이-없었다면">Reflection이 없었다면?</h3>
<p>만약 Runtime에 Class 정보를 확인할 방법이 없다고 생각해보자.</p>
<p>그러면 Framework가 다음 코드를 자동으로 처리하기 어렵다.</p>
<pre><code class="language-java">@Service
public class UserService {

    public UserService(
            UserRepository userRepository
    ) {
    }
}</code></pre>
<p>Framework가</p>
<pre><code class="language-text">@Service가 붙어 있는가?

생성자가 몇 개인가?

어떤 Parameter가 필요한가?

어떤 Method가 있는가?</code></pre>
<p>를 알아낼 수 없기 때문이다.</p>
<p>개발자가 모든 관계를 직접 작성해야 할 것이다.</p>
<pre><code class="language-java">UserRepository repository =
        new UserRepository();

UserService service =
        new UserService(repository);

container.put(
        &quot;userRepository&quot;,
        repository
);

container.put(
        &quot;userService&quot;,
        service
);</code></pre>
<p>Reflection을 활용하면 Framework가 Class의 Metadata를 기반으로 이러한 반복 작업을 자동화할 수 있다.</p>
<p>물론 실제 Spring Container의 Bean 생성 과정은 훨씬 복잡하고, 단순히 Reflection 몇 줄만으로 구성되는 것은 아니다. Spring은 <code>ApplicationContext</code>를 통해 Bean의 생성·구성·조립을 관리하고 다양한 Bean lifecycle 및 확장 지점을 함께 제공한다.</p>
<p>여기서 중요한 것은 Spring 내부 구현을 전부 외우는 것이 아니다.</p>
<blockquote>
<p><strong>Reflection 덕분에 Framework가 개발자가 작성한 Class를 Runtime에 분석하고, 그 정보를 바탕으로 동적인 동작을 수행할 수 있다.</strong></p>
</blockquote>
<p>정도로 이해하면 충분하다.</p>
<hr />
<h1 id="정리">정리</h1>
<p>이번 글에서 본 개념들은 따로 떨어져 있는 것이 아니다.</p>
<p>하나의 흐름으로 이어진다.</p>
<pre><code class="language-text">Dependency

객체가 다른 객체를 필요로 한다.
      │
      ▼
DI

필요한 객체를 직접 만들지 않고
외부에서 전달받는다.
      │
      ▼
IoC

객체 생성과 관리의 제어권까지
Framework에게 넘긴다.
      │
      ▼
IoC Container

Bean을 생성하고
의존 관계를 확인하고
DI하고
관리한다.</code></pre>
<p>가장 중요한 차이를 다시 정리하면 다음과 같다.</p>
<pre><code class="language-text">DI
→ 객체 입장

&quot;필요한 객체를 외부에서 받는다.&quot;</code></pre>
<pre><code class="language-text">IoC
→ 제어권의 관점

&quot;객체 생성과 관리의 주체가
개발자에서 Framework로 바뀐다.&quot;</code></pre>
<p>그리고 실제 Spring에서는</p>
<pre><code class="language-text">ApplicationContext
        │
        ├─ Bean 관리
        ├─ 의존 관계 연결
        ├─ DI
        └─ 생명주기 관리</code></pre>
<p>를 중심으로 Spring Container가 구성된다.</p>
<p>결국 우리가 다음과 같이 작성하면</p>
<pre><code class="language-java">@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(
            UserRepository userRepository
    ) {
        this.userRepository = userRepository;
    }
}</code></pre>
<p>개발자는</p>
<blockquote>
<p><strong>“UserService는 UserRepository가 필요하다.”</strong></p>
</blockquote>
<p>라는 관계에 집중한다.</p>
<p>Spring이</p>
<pre><code class="language-text">UserRepository를 찾고

Bean을 준비하고

UserService를 만들고

둘을 연결하고

만들어진 Bean을 관리하는 것</code></pre>
<p>을 담당한다.</p>
<p>따라서 Spring의 IoC와 DI는</p>
<blockquote>
<p><strong>객체의 생성과 조립에 대한 책임을 Framework로 넘기고, 개발자가 각 객체의 역할과 비즈니스 로직에 집중할 수 있게 만드는 Spring의 핵심 구조다.</strong></p>
</blockquote>
<p>그리고 Spring은 Container에서 Bean을 단순히 생성하고 보관하는 데서 끝나지 않는다.</p>
<p>필요하다면 우리가 만든 객체 앞에 <strong>다른 객체를 하나 세워서 호출을 대신 받도록 만들 수도 있다.</strong></p>
<pre><code class="language-text">호출자
  │
  ▼
Proxy
  │
  ▼
실제 Bean</code></pre>
<p>Spring의</p>
<pre><code class="language-text">@Transactional
@Async
@Validated
AOP</code></pre>
<p>같은 여러 기능을 이해하려면 이 구조가 중요하다.</p>
<p>다음에는 <strong>Proxy Pattern</strong>을 살펴볼 것이다.</p>