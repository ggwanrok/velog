<p>지난 글에서는 Spring의 <strong>Proxy와 AOP</strong>를 살펴봤다.</p>
<p>Spring은 우리가 만든 Bean을 그대로 사용하는 것에서 끝나지 않는다.</p>
<p>필요하다면 Bean 앞에 Proxy를 두고 Method 호출을 먼저 가로챌 수 있다.</p>
<pre><code class="language-text">Caller
  │
  ▼
Proxy
  │
  ├─ 부가 기능
  ▼
Target</code></pre>
<p>그래서 핵심 비즈니스 로직을 직접 수정하지 않고도 Transaction이나 Logging 같은 부가 기능을 적용할 수 있었다.</p>
<p>그리고 마지막에는 중요한 원칙 하나를 확인했다.</p>
<blockquote>
<p><strong>Proxy 기반 기능은 실제 호출이 Proxy를 통과해야 적용된다.</strong></p>
</blockquote>
<p>이번에는 Spring이 처리해주는 또 다른 중요한 기능인 <strong>입력값 검증, Validation</strong>을 살펴본다.</p>
<p>그런데 Validation부터 바로 시작하기 전에 먼저 한 가지 질문을 해보자.</p>
<p>Client가 다음 데이터를 보냈다고 하자.</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;,
  &quot;age&quot;: 25
}</code></pre>
<p>Spring Application에서는 이 데이터를 <strong>어떤 객체에 담아야 할까?</strong></p>
<p>그리고 더 중요한 질문이 있다.</p>
<blockquote>
<p><strong>Client가 보내준 값을 그대로 믿어도 될까?</strong></p>
</blockquote>
<p>이번 글은 이 두 질문에서 시작한다.</p>
<hr />
<h1 id="믿을-수-없는-외부-데이터">믿을 수 없는 외부 데이터</h1>
<p>정상적인 요청만 들어온다면 큰 문제가 없다.</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;,
  &quot;age&quot;: 25
}</code></pre>
<p>하지만 Client는 다음과 같은 값도 얼마든지 보낼 수 있다.</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;&quot;,
  &quot;email&quot;: &quot;hello&quot;,
  &quot;age&quot;: -100
}</code></pre>
<p>혹은 필수 데이터 자체가 누락될 수도 있다.</p>
<pre><code class="language-json">{
  &quot;name&quot;: null,
  &quot;email&quot;: null
}</code></pre>
<p>이런 값이 아무런 검사 없이 Application 안쪽까지 흘러간다면</p>
<pre><code class="language-text">Client
  │
  │ 잘못된 입력
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
<p>잘못된 데이터를 기준으로 비즈니스 로직이 실행되거나 DB에 저장될 수도 있다.</p>
<p>따라서 Application의 경계에서는 최소한 다음과 같은 조건을 검사해야 한다.</p>
<pre><code class="language-text">이름이 비어 있지는 않은가?

Email 형식이 올바른가?

나이가 허용된 범위인가?

반드시 있어야 하는 값이 누락되지는 않았는가?</code></pre>
<p>이것이 <strong>Validation</strong>, 유효성 검증이다.</p>
<p>그런데 Validation의 대상이 되려면 먼저 Client의 데이터를 받아줄 객체가 필요하다.</p>
<p>여기서 <strong>DTO</strong>가 등장한다.</p>
<hr />
<h1 id="dto">DTO</h1>
<p>DTO는 <strong>Data Transfer Object</strong>의 약자다.</p>
<p>이름 그대로</p>
<blockquote>
<p><strong>데이터를 전달하기 위한 객체</strong></p>
</blockquote>
<p>다.</p>
<p>예를 들어 사용자 생성 API가 다음 JSON을 받는다고 하자.</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;,
  &quot;age&quot;: 25
}</code></pre>
<p>이에 대응하는 Java 객체를 만들 수 있다.</p>
<pre><code class="language-java">public record UserCreateRequest(
        String name,
        String email,
        Integer age
) {
}</code></pre>
<p>Request가 들어오면 Spring은 JSON 데이터를 Java Object로 변환한다.</p>
<pre><code class="language-text">HTTP Request

JSON
 │
 ▼
UserCreateRequest
 │
 ▼
Controller</code></pre>
<p>즉 DTO는 외부에서 들어온 데이터를 Application 내부로 전달하는 <strong>데이터 상자</strong> 역할을 한다.</p>
<p>DTO 자체가 할인율을 계산하거나,</p>
<p>DB를 조회하거나,</p>
<p>주문 가능 여부를 판단할 필요는 없다.</p>
<pre><code class="language-text">DTO
→ 데이터 전달

Service / Domain
→ 비즈니스 로직</code></pre>
<p>으로 책임을 나누는 것이 자연스럽다.</p>
<hr />
<h2 id="dto를-쓰는-이유">DTO를 쓰는 이유</h2>
<p>여기서 가장 많이 드는 의문이 있다.</p>
<p>Application 내부에 이미 <code>User</code>라는 객체가 있다고 해보자.</p>
<pre><code class="language-java">public class User {

    private Long id;
    private String name;
    private String email;
    private String passwordHash;
    private LocalDateTime createdAt;
}</code></pre>
<p>그렇다면 굳이 <code>UserCreateRequest</code>를 하나 더 만들지 않고</p>
<pre><code class="language-java">@PostMapping(&quot;/users&quot;)
public void createUser(
        @RequestBody User user
) {
}</code></pre>
<p>처럼 바로 받아도 되는 것 아닐까?</p>
<p>기술적으로 가능할 수는 있다.</p>
<p>하지만 <strong>외부 API에서 필요한 데이터와 Application 내부에서 관리해야 하는 데이터는 목적이 다르다.</strong></p>
<p>예를 들어 사용자 생성 요청에 필요한 값은</p>
<pre><code class="language-text">name
email
age</code></pre>
<p>뿐일 수 있다.</p>
<p>반면 내부 User 객체에는</p>
<pre><code class="language-text">id
name
email
passwordHash
createdAt
updatedAt
status</code></pre>
<p>같은 데이터가 존재할 수 있다.</p>
<p>Client에게 내부 객체를 그대로 열어주면 두 영역이 강하게 연결된다.</p>
<pre><code class="language-text">Client
   │
   ▼
Internal Model
   │
   ▼
DB</code></pre>
<p>API의 입력 형식이 Application 내부 데이터 구조와 동일해지는 것이다.</p>
<p>그래서 두 영역 사이에 DTO라는 경계를 둔다.</p>
<pre><code class="language-text">Client
   │
   │ JSON
   ▼
Request DTO
   │
   ▼
Application</code></pre>
<hr />
<h2 id="dto와-entity">DTO와 Entity</h2>
<p>이 시점에서 DTO와 함께 자주 등장하는 개념이 <strong>Entity</strong>다.</p>
<p>JPA를 사용하는 Application이라면 Entity는 보통 <strong>Application 내부에서 영속화되는 데이터를 표현하는 객체</strong>라고 생각할 수 있다.</p>
<p>예를 들어 다음과 같은 User Entity가 있다고 하자.</p>
<pre><code class="language-java">@Entity
public class User {

    @Id
    private Long id;

    private String name;

    private String email;

    private String passwordHash;
}</code></pre>
<p>개념적으로는</p>
<pre><code class="language-text">Java Application

User Entity
    │
    ▼
Database</code></pre>
<p>처럼 Application의 객체와 DB의 데이터를 연결하는 모델이다.</p>
<p>아직까진 JPA의 세부 동작까지 알 필요는 없다.</p>
<p>중요한 것은 <strong>DTO와 Entity가 만들어진 목적이 다르다</strong>는 점이다.</p>
<table>
<thead>
<tr>
<th>구분</th>
<th>DTO</th>
<th>Entity</th>
</tr>
</thead>
<tbody><tr>
<td>목적</td>
<td>데이터 전달</td>
<td>내부 데이터 상태 표현 및 영속화</td>
</tr>
<tr>
<td>주요 위치</td>
<td>API / 계층 경계</td>
<td>Application 내부</td>
</tr>
<tr>
<td>Client 노출</td>
<td>필요한 데이터를 선택하여 사용</td>
<td>직접 노출은 가급적 피함</td>
</tr>
<tr>
<td>변경 이유</td>
<td>API 요구사항 변경</td>
<td>내부 Domain / Persistence 변경</td>
</tr>
</tbody></table>
<p>쉽게 말하면</p>
<pre><code class="language-text">DTO
→ 밖과 이야기하기 위한 객체

Entity
→ 안에서 데이터를 관리하기 위한 객체</code></pre>
<p>라고 볼 수 있다.</p>
<hr />
<h3 id="entity를-dto처럼-사용할-때">Entity를 DTO처럼 사용할 때</h3>
<p>예를 들어 User Entity가 다음 정보를 가지고 있다고 하자.</p>
<pre><code class="language-text">User Entity

id
name
email
passwordHash
createdAt
updatedAt</code></pre>
<p>그런데 Client에게 필요한 정보는</p>
<pre><code class="language-text">id
name
email</code></pre>
<p>뿐이다.</p>
<p>Entity를 그대로 반환한다면 내부에 존재하는 데이터가 의도하지 않게 API에 포함될 위험이 있다.</p>
<p>또한 Entity에 필드가 추가될 때</p>
<pre><code class="language-text">Entity 변경
     │
     ▼
API Response 변경</code></pre>
<p>처럼 API의 구조까지 영향을 받을 수 있다.</p>
<p>반대로 DTO를 하나 두면</p>
<pre><code class="language-text">Entity
  │
  │ 필요한 데이터만 선택
  ▼
Response DTO
  │
  ▼
Client</code></pre>
<p>라는 경계가 생긴다.</p>
<p>Application 내부 구조와 외부 API 구조가 분리되는 것이다.</p>
<hr />
<h1 id="request-dto와-response-dto">Request DTO와 Response DTO</h1>
<p>DTO도 하나를 모든 상황에서 재사용하기보다 목적에 따라 나누는 것이 좋다.</p>
<p>사용자 생성 요청을 생각해보자.</p>
<p>Client가 보내야 하는 정보는</p>
<pre><code class="language-text">name
email
age</code></pre>
<p>이다.</p>
<p>따라서 Request DTO는</p>
<pre><code class="language-java">public record UserCreateRequest(
        String name,
        String email,
        Integer age
) {
}</code></pre>
<p>처럼 구성할 수 있다.</p>
<p>그런데 사용자 생성이 완료된 뒤 Client에게 반환할 정보는 다를 수 있다.</p>
<pre><code class="language-java">public record UserResponse(
        Long id,
        String name,
        String email
) {
}</code></pre>
<p><code>id</code>는 DB에 저장되는 과정에서 만들어질 수 있기 때문에 Request에는 필요하지 않았지만 Response에는 필요하다.</p>
<pre><code class="language-text">UserCreateRequest

name
email
age</code></pre>
<pre><code class="language-text">UserResponse

id
name
email</code></pre>
<p>따라서</p>
<pre><code class="language-text">Request DTO
→ Client가 Server에게 보내야 하는 데이터

Response DTO
→ Server가 Client에게 공개해야 하는 데이터</code></pre>
<p>라고 역할을 분리할 수 있다.</p>
<p><code>UserDto</code>라는 하나의 객체를 모든 곳에서 사용하는 것보다</p>
<pre><code class="language-text">UserCreateRequest
UserUpdateRequest
UserResponse</code></pre>
<p>처럼 목적을 이름에 드러내면 그 객체가 왜 존재하는지도 코드에서 바로 알 수 있다.</p>
<hr />
<h1 id="validation">Validation</h1>
<p>이제 다시 처음의 문제로 돌아가 보자.</p>
<p>Client가 보내는 데이터를 Request DTO로 받기로 했다.</p>
<pre><code class="language-text">Client
  │
  │ JSON
  ▼
UserCreateRequest
  │
  ▼
Controller</code></pre>
<p>그렇다면</p>
<blockquote>
<p><strong>Client가 반드시 지켜야 하는 입력 조건도 Request DTO에 표현할 수 있지 않을까?</strong></p>
</blockquote>
<p>예를 들어 사용자 생성 조건이 다음과 같다고 하자.</p>
<pre><code class="language-text">name
→ 반드시 존재
→ 공백 불가

email
→ 반드시 존재
→ Email 형식

age
→ 반드시 존재
→ 18 이상</code></pre>
<p>Bean Validation을 이용하면 이 규칙을 DTO에 직접 표현할 수 있다.</p>
<pre><code class="language-java">public record UserCreateRequest(

        @NotBlank
        String name,

        @NotBlank
        @Email
        String email,

        @NotNull
        @Min(18)
        Integer age
) {
}</code></pre>
<p>DTO만 봐도 이 API가 요구하는 입력 조건을 알 수 있다.</p>
<pre><code class="language-text">name
→ @NotBlank

email
→ @NotBlank
→ @Email

age
→ @NotNull
→ @Min(18)</code></pre>
<p>이런 Annotation을 <strong>Constraint</strong>라고 한다.</p>
<hr />
<h2 id="bean-validation">Bean Validation</h2>
<p>물론 직접 <code>if</code>문으로 값을 검사할 수도 있다.</p>
<pre><code class="language-java">if (name == null || name.isBlank()) {
    throw new IllegalArgumentException();
}

if (age &lt; 18) {
    throw new IllegalArgumentException();
}</code></pre>
<p>하지만 API가 많아질수록 이런 코드가 반복된다.</p>
<pre><code class="language-text">Controller A
→ null 검사
→ 길이 검사
→ Email 검사

Controller B
→ null 검사
→ 길이 검사
→ 숫자 검사</code></pre>
<p>그리고 실제 비즈니스 로직보다 입력 검사 코드가 더 많이 보이기 시작한다.</p>
<p>Bean Validation은 이런 <strong>일반적인 값 검증 규칙을 Annotation으로 선언할 수 있도록 하는 방식</strong>이다.</p>
<p>대표적인 Constraint는 다음과 같다.</p>
<table>
<thead>
<tr>
<th>Annotation</th>
<th>의미</th>
</tr>
</thead>
<tbody><tr>
<td><code>@NotNull</code></td>
<td><code>null</code> 금지</td>
</tr>
<tr>
<td><code>@NotEmpty</code></td>
<td><code>null</code>, 빈 값 금지</td>
</tr>
<tr>
<td><code>@NotBlank</code></td>
<td><code>null</code>, 빈 문자열, 공백 문자열 금지</td>
</tr>
<tr>
<td><code>@Size</code></td>
<td>문자열·Collection 등의 길이 제한</td>
</tr>
<tr>
<td><code>@Min</code></td>
<td>최소 숫자</td>
</tr>
<tr>
<td><code>@Max</code></td>
<td>최대 숫자</td>
</tr>
<tr>
<td><code>@Positive</code></td>
<td>양수</td>
</tr>
<tr>
<td><code>@PositiveOrZero</code></td>
<td>0 이상</td>
</tr>
<tr>
<td><code>@Email</code></td>
<td>Email 형식</td>
</tr>
<tr>
<td><code>@Pattern</code></td>
<td>정규표현식 조건</td>
</tr>
<tr>
<td><code>@Past</code></td>
<td>과거 날짜</td>
</tr>
<tr>
<td><code>@Future</code></td>
<td>미래 날짜</td>
</tr>
</tbody></table>
<p>예를 들어 상품 생성 요청이라면</p>
<pre><code class="language-java">public record ProductCreateRequest(

        @NotBlank
        @Size(max = 100)
        String name,

        @Positive
        Integer price,

        @PositiveOrZero
        Integer stockQuantity
) {
}</code></pre>
<p>처럼 입력 조건 자체를 DTO에 선언할 수 있다.</p>
<hr />
<h3 id="notnull-notempty-notblank">NotNull, NotEmpty, NotBlank</h3>
<p>이 세 Annotation은 이름이 비슷해서 특히 많이 헷갈린다.</p>
<p>먼저 <code>@NotNull</code>이다.</p>
<pre><code class="language-java">@NotNull
String name;</code></pre>
<p>말 그대로 <code>null</code>만 허용하지 않는다.</p>
<pre><code class="language-text">null     → X
&quot;&quot;       → O
&quot;   &quot;    → O
&quot;Alice&quot;  → O</code></pre>
<hr />
<p><code>@NotEmpty</code>는 값이 비어 있는 것도 허용하지 않는다.</p>
<pre><code class="language-java">@NotEmpty
String name;</code></pre>
<pre><code class="language-text">null     → X
&quot;&quot;       → X
&quot;   &quot;    → O
&quot;Alice&quot;  → O</code></pre>
<p>공백 문자열은 길이가 존재하기 때문에 통과할 수 있다.</p>
<hr />
<p><code>@NotBlank</code>는 문자열의 공백까지 확인한다.</p>
<pre><code class="language-java">@NotBlank
String name;</code></pre>
<pre><code class="language-text">null     → X
&quot;&quot;       → X
&quot;   &quot;    → X
&quot;Alice&quot;  → O</code></pre>
<p>그래서 이름이나 제목처럼 <strong>실제 문자가 반드시 들어와야 하는 문자열</strong>에는 <code>@NotBlank</code>가 자주 사용된다.</p>
<hr />
<h2 id="활용법">활용법</h2>
<p>여기서 중요한 부분이 있다.</p>
<p>DTO에 다음과 같이 Constraint를 붙였다고 하자.</p>
<pre><code class="language-java">public record UserCreateRequest(

        @NotBlank
        String name,

        @Email
        String email
) {
}</code></pre>
<p>이 Annotation은</p>
<pre><code class="language-text">어떤 조건을 만족해야 하는가?</code></pre>
<p>를 정의한다.</p>
<p>하지만 아직</p>
<pre><code class="language-text">지금 이 객체를 검증해라.</code></pre>
<p>라는 요청은 하지 않았다.</p>
<p>실제로 Validation을 실행시킬 진입점이 필요하다.</p>
<p>Controller에서는 보통 <strong><code>@Valid</code></strong>가 그 역할을 한다.</p>
<hr />
<h2 id="valid">@Valid</h2>
<p>다음 Controller를 보자.</p>
<pre><code class="language-java">@PostMapping(&quot;/users&quot;)
public UserResponse createUser(
        @Valid
        @RequestBody UserCreateRequest request
) {

    return userService.createUser(request);
}</code></pre>
<p>여기에는 두 Annotation이 붙어 있다.</p>
<pre><code class="language-java">@RequestBody</code></pre>
<p>와</p>
<pre><code class="language-java">@Valid</code></pre>
<p>이다.</p>
<p>둘의 역할은 다르다.</p>
<pre><code class="language-text">@RequestBody
→ HTTP Request Body를 Java Object로 변환

@Valid
→ 만들어진 객체의 Constraint를 검증</code></pre>
<p>즉 요청이</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;,
  &quot;age&quot;: 25
}</code></pre>
<p>라면</p>
<pre><code class="language-text">HTTP Request Body
       │
       ▼
JSON
       │
       ▼
UserCreateRequest
       │
       ▼
Validation
       │
       ▼
Controller</code></pre>
<p>순서로 처리된다.</p>
<hr />
<h3 id="valid-동작위치">@Valid 동작위치</h3>
<p>이 부분은 앞에서 Spring MVC를 공부했던 내용과 연결하면 이해하기 쉽다.</p>
<p>Controller Method가 실행되기 전에 Spring MVC는 Method Parameter를 준비한다.</p>
<pre><code class="language-java">@PostMapping(&quot;/users&quot;)
public UserResponse createUser(
        @Valid
        @RequestBody UserCreateRequest request
) {
}</code></pre>
<p>Spring은 <code>request</code> Parameter를 그냥 만들어주는 것이 아니다.</p>
<p>개념적으로는</p>
<pre><code class="language-text">HTTP Request
     │
     ▼
DispatcherServlet
     │
     ▼
HandlerAdapter
     │
     ▼
Argument Resolver
     │
     ├─ Request Body 읽기
     ├─ JSON → DTO 변환
     └─ Validation
     │
     ▼
Controller</code></pre>
<p>라는 흐름을 거친다.</p>
<p>즉</p>
<pre><code class="language-text">DTO + @Valid</code></pre>
<p>검증은 <strong>IoC Container가 Bean을 생성하는 과정이 아니라 Spring MVC가 Controller Argument를 준비하는 과정</strong>에 속한다.</p>
<p>이 구분이 중요하다.</p>
<hr />
<h3 id="검증에-실패하면">검증에 실패하면?</h3>
<p>다음 Request를 보내보자.</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;&quot;,
  &quot;email&quot;: &quot;hello&quot;,
  &quot;age&quot;: 10
}</code></pre>
<p>DTO는 다음 조건을 요구한다.</p>
<pre><code class="language-java">@NotBlank
String name;

@Email
String email;

@Min(18)
Integer age;</code></pre>
<p>그러면</p>
<pre><code class="language-text">name
→ 실패

email
→ 실패

age
→ 실패</code></pre>
<p>한다.</p>
<p>전체 흐름은 다음과 같다.</p>
<pre><code class="language-text">HTTP Request
     │
     ▼
DTO Binding
     │
     ▼
Validation
     │
     X
Controller</code></pre>
<p>검증을 통과하지 못했기 때문에 Controller의 비즈니스 처리까지 진행하지 않는다.</p>
<p>일반적인 DTO 검증 실패에서는 <code>MethodArgumentNotValidException</code>과 같은 Validation 관련 예외가 발생할 수 있고, 결과적으로 Client에게 잘못된 요청임을 알릴 수 있다.</p>
<p>즉 잘못된 데이터가</p>
<pre><code class="language-text">Controller
    ↓
Service
    ↓
Repository</code></pre>
<p>안쪽으로 흘러가기 전에 막는 것이다.</p>
<hr />
<h3 id="valid가-검증-규칙을-만드는-것은-아니다">@Valid가 검증 규칙을 만드는 것은 아니다</h3>
<p>여기서 또 하나 많이 헷갈리는 부분이 있다.</p>
<pre><code class="language-java">@Valid</code></pre>
<p>자체가</p>
<pre><code class="language-text">이름은 비어 있으면 안 된다.

Email 형식이어야 한다.

나이는 18 이상이어야 한다.</code></pre>
<p>라고 판단하는 것은 아니다.</p>
<p>실제 검증 규칙은</p>
<pre><code class="language-java">@NotBlank
@Email
@Min</code></pre>
<p>같은 Constraint가 가지고 있다.</p>
<p><code>@Valid</code>는 쉽게 말하면</p>
<blockquote>
<p><strong>“이 객체에 정의된 Validation 규칙을 지금 검사해라.”</strong></p>
</blockquote>
<p>라는 역할이다.</p>
<p>따라서 DTO가</p>
<pre><code class="language-java">public record UserRequest(
        String name,
        String email
) {
}</code></pre>
<p>처럼 아무런 Constraint를 가지고 있지 않다면</p>
<pre><code class="language-java">@Valid
@RequestBody UserRequest request</code></pre>
<p>라고 작성해도 검사할 규칙이 없다.</p>
<pre><code class="language-text">@Valid
  │
  ▼
Constraint 확인
  │
  └─ 없음
       │
       ▼
      통과</code></pre>
<p><code>@Valid</code>가 데이터의 옳고 그름을 스스로 추측하는 것이 아니다.</p>
<hr />
<h2 id="service-에서의-사용법">Service 에서의 사용법</h2>
<p>여기까지는 Controller의 Validation이었다.</p>
<pre><code class="language-text">HTTP Request
      │
      ▼
Spring MVC
      │
      ├─ Binding
      └─ Validation
      │
      ▼
Controller</code></pre>
<p>그런데 Service Method는 상황이 다르다.</p>
<pre><code class="language-java">userService.createUser(request);</code></pre>
<p>이건 HTTP Request Binding 과정이 아니다.</p>
<p>그냥 Java의 Method 호출이다.</p>
<pre><code class="language-text">Controller
     │
     │ Java Method Call
     ▼
UserService</code></pre>
<p>따라서 Spring MVC의 Argument Resolver가 중간에 나타나서 Service Parameter를 검증해주지 않는다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Service
public class UserService {

    public void deleteUser(
            @Min(1) Long id
    ) {
        ...
    }
}</code></pre>
<p>라고 작성했다고 해보자.</p>
<p>우리는 <code>id</code>가 1 이상인지 확인하고 싶다.</p>
<p>하지만 이 Method 호출은</p>
<pre><code class="language-text">HTTP Request
→ Argument Resolver</code></pre>
<p>과정을 거치는 호출이 아니다.</p>
<p>그렇다면 Spring은 Service Method의 Parameter를 어떻게 검증할까?</p>
<p>여기서 <strong><code>@Validated</code></strong>가 등장한다.</p>
<hr />
<h2 id="validated">@Validated</h2>
<p>Service에 다음과 같이 적용할 수 있다.</p>
<pre><code class="language-java">@Service
@Validated
public class UserService {

    public void deleteUser(
            @Min(1) Long id
    ) {
        ...
    }
}</code></pre>
<p>이제 Service의 Method Parameter 자체를 Validation 대상으로 만들 수 있다.</p>
<pre><code class="language-text">deleteUser(10L)
→ 검증 성공

deleteUser(0L)
→ 검증 실패</code></pre>
<p>그런데 이 검증은 Controller의 <code>@Valid</code>와 동작하는 위치가 다르다.</p>
<p>그리고 여기서 바로 지난 글의 <strong>Proxy</strong>가 다시 등장한다.</p>
<hr />
<h3 id="validated와-proxy">@Validated와 Proxy</h3>
<p>지난 글에서 Spring은 Bean 앞에 Proxy를 둘 수 있다고 했다.</p>
<pre><code class="language-text">Caller
  │
  ▼
Proxy
  │
  ▼
Target</code></pre>
<p><code>@Validated</code>가 적용된 Service의 Method Validation도 같은 방식으로 이해할 수 있다.</p>
<pre><code class="language-text">Controller
     │
     ▼
UserService Proxy
     │
     ├─ Parameter Validation
     │
     ▼
UserService Target</code></pre>
<p>Controller가</p>
<pre><code class="language-java">userService.deleteUser(0L);</code></pre>
<p>을 호출하면 바로 Target Method가 실행되는 것이 아니라 Proxy가 먼저 호출을 받는다.</p>
<pre><code class="language-text">deleteUser(0L)
      │
      ▼
Validation Proxy
      │
      ├─ @Min(1) 검사
      │
      └─ 실패
           X
        Target</code></pre>
<p>반대로 검증에 성공하면</p>
<pre><code class="language-text">deleteUser(10L)
      │
      ▼
Validation Proxy
      │
      ├─ 검증 성공
      ▼
Target.deleteUser()</code></pre>
<p>실제 Service Method가 실행된다.</p>
<p>즉</p>
<pre><code class="language-text">Controller의 @Valid
→ Spring MVC 요청 Binding 과정

Service의 @Validated
→ Bean Method 호출
→ AOP Proxy</code></pre>
<p>라는 차이가 있다.</p>
<p>이 둘을 구분해서 이해하는 것이 중요하다.</p>
<hr />
<h3 id="service에서-dto-검증-방법">Service에서 DTO 검증 방법</h3>
<p>Service Parameter가 단순한 <code>Long</code>이 아니라 DTO일 수도 있다.</p>
<pre><code class="language-java">@Service
@Validated
public class UserService {

    public void createUser(
            @Valid UserCreateRequest request
    ) {
        ...
    }
}</code></pre>
<p>여기서는 두 Annotation의 역할이 나뉜다.</p>
<pre><code class="language-text">@Validated
→ 이 Bean의 Method 호출을 Validation 대상으로 만든다.

@Valid
→ 전달받은 객체 내부의 Constraint까지 검증한다.</code></pre>
<p>구조적으로 보면</p>
<pre><code class="language-text">Controller
    │
    ▼
UserService Proxy
    │
    ├─ Method Validation
    │
    └─ @Valid
          │
          ▼
    UserCreateRequest
       ├─ @NotBlank
       ├─ @Email
       └─ @Min
    │
    ▼
UserService Target</code></pre>
<p>라고 볼 수 있다.</p>
<hr />
<h1 id="valid와-validated-구분">@Valid와 @Validated 구분</h1>
<p>둘이 이름도 비슷하고 Validation에 함께 등장하다 보니</p>
<pre><code class="language-text">@Valid
→ Controller

@Validated
→ Service</code></pre>
<p>라고 외우기 쉽다.</p>
<p>처음 방향을 잡을 때는 크게 틀린 접근은 아니지만, 조금 더 정확하게 구분할 필요가 있다.</p>
<p><code>@Valid</code>는 <strong>Jakarta Validation</strong>에서 제공한다.</p>
<p>주요 역할은 객체의 Validation을 수행하고, 필요하다면 내부 객체까지 Validation을 이어가는 것이다.</p>
<p>반면 <code>@Validated</code>는 <strong>Spring에서 제공하는 Annotation</strong>이다.</p>
<p>Spring의 Method Validation과 연결하거나 Validation Group 같은 추가 기능을 사용할 때 활용된다.</p>
<p>따라서 이번 글의 흐름에서는 다음처럼 기억하면 충분하다.</p>
<pre><code class="language-text">Controller

@Valid + Request DTO
       │
       ▼
Spring MVC Validation</code></pre>
<pre><code class="language-text">Service

@Validated
    │
    ▼
Method Validation Proxy</code></pre>
<p>그리고 DTO 자체를 Service Method에서도 검증하고 싶다면</p>
<pre><code class="language-text">@Validated
    +
@Valid DTO</code></pre>
<p>를 함께 사용할 수 있다.</p>
<hr />
<h2 id="self-invocation-조심">Self Invocation 조심</h2>
<p>지난 글에서 이런 코드를 봤다.</p>
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
<p><code>outer()</code>에서 <code>inner()</code>를 호출하면</p>
<pre><code class="language-text">Target.outer()
     │
     ▼
Target.inner()</code></pre>
<p>로 직접 호출되어 Proxy를 다시 통과하지 않았다.</p>
<p>Method Validation도 Proxy 기반이라면 같은 원리를 생각할 수 있다.</p>
<pre><code class="language-java">@Service
@Validated
public class UserService {

    public void outer() {

        deleteUser(0L);
    }

    public void deleteUser(
            @Min(1) Long id
    ) {

        ...
    }
}</code></pre>
<p>외부 Bean에서 <code>deleteUser()</code>를 호출하면</p>
<pre><code class="language-text">Caller
  │
  ▼
Validation Proxy
  │
  ▼
Target.deleteUser()</code></pre>
<p>를 거친다.</p>
<p>하지만 같은 객체 내부에서 호출하면</p>
<pre><code class="language-text">UserService.outer()
       │
       ▼
UserService.deleteUser()</code></pre>
<p>가 된다.</p>
<p>Proxy가 다시 호출을 가로채지 못한다.</p>
<p>결국 지난 글에서 정리했던 질문이 그대로 돌아온다.</p>
<blockquote>
<p><strong>Annotation이 붙어 있는가?</strong></p>
</blockquote>
<p>뿐만 아니라</p>
<blockquote>
<p><strong>이 호출이 실제로 어떤 처리 경로를 통과하는가?</strong></p>
</blockquote>
<p>를 봐야 한다.</p>
<hr />
<h1 id="validation-오남용-금지">Validation 오남용 금지</h1>
<p>여기까지 보면 모든 검증을</p>
<pre><code class="language-java">@NotBlank
@Email
@Min</code></pre>
<p>으로 해결하면 될 것처럼 보인다.</p>
<p>하지만 Validation에도 종류가 있다.</p>
<p>예를 들어 다음 조건을 생각해보자.</p>
<pre><code class="language-text">이름이 비어 있는가?

Email 형식이 올바른가?

수량이 1 이상인가?</code></pre>
<p>이런 조건은 <strong>현재 들어온 값만 보면 판단할 수 있다.</strong></p>
<p>DTO와 Bean Validation이 잘 어울린다.</p>
<pre><code class="language-text">Request DTO
     │
     ├─ @NotBlank
     ├─ @Email
     └─ @Min</code></pre>
<p>그런데 다음 조건은 어떨까?</p>
<pre><code class="language-text">이미 가입된 Email인가?

상품 재고가 충분한가?

현재 사용자가 이 주문의 소유자인가?

현재 주문 상태에서 취소가 가능한가?</code></pre>
<p>이건 단순히 Request 값 하나만 봐서는 판단할 수 없다.</p>
<p>DB 상태나 다른 객체, 현재 사용자, 현재 시점 등을 확인해야 한다.</p>
<p>이런 검증은 <strong>비즈니스 규칙</strong>이다.</p>
<p>그래서 보통 역할을 나눈다.</p>
<pre><code class="language-text">DTO / Bean Validation

→ 값의 형태가 올바른가?
→ 필수값이 존재하는가?
→ 범위가 올바른가?</code></pre>
<pre><code class="language-text">Service / Domain

→ 이 작업이 비즈니스적으로 가능한가?</code></pre>
<p>예를 들어 Email 중복 검사는</p>
<pre><code class="language-java">public UserResponse createUser(
        UserCreateRequest request
) {

    if (userRepository.existsByEmail(
            request.email()
    )) {

        throw new DuplicateEmailException();
    }

    ...
}</code></pre>
<p>처럼 Service에서 수행할 수 있다.</p>
<p>즉 Bean Validation은 <strong>Service의 비즈니스 검증을 없애주는 기술이 아니다.</strong></p>
<p>서로 다른 종류의 검증을 서로 다른 책임에 배치하는 것이다.</p>
<hr />
<h2 id="방지-대책">방지 대책</h2>
<p>사용자 생성 API의 조건이 다음과 같다고 하자.</p>
<pre><code class="language-text">name
→ 필수

email
→ 필수
→ Email 형식

age
→ 18 이상</code></pre>
<p>이건 <code>User</code>라는 Entity 자체의 모든 상황에서 지켜야 할 규칙이라기보다</p>
<blockquote>
<p><strong>사용자 생성 API가 Client에게 요구하는 입력 계약</strong></p>
</blockquote>
<p>에 가깝다.</p>
<p>따라서</p>
<pre><code class="language-java">public record UserCreateRequest(

        @NotBlank
        String name,

        @NotBlank
        @Email
        String email,

        @Min(18)
        Integer age
) {
}</code></pre>
<p>처럼 Request DTO에 두는 것이 자연스럽다.</p>
<p>특히 생성과 수정 API를 생각하면 더 명확해진다.</p>
<p>사용자 생성은</p>
<pre><code class="language-text">name
→ 필수

email
→ 필수</code></pre>
<p>일 수 있다.</p>
<p>하지만 수정에서는</p>
<pre><code class="language-text">name
→ 선택

email
→ 선택</code></pre>
<p>일 수도 있다.</p>
<p>그러면</p>
<pre><code class="language-text">UserCreateRequest</code></pre>
<p>와</p>
<pre><code class="language-text">UserUpdateRequest</code></pre>
<p>가 서로 다른 Validation 규칙을 가지게 된다.</p>
<pre><code class="language-text">Create API 규칙
       │
       ▼
UserCreateRequest</code></pre>
<pre><code class="language-text">Update API 규칙
       │
       ▼
UserUpdateRequest</code></pre>
<p>Entity 하나에 모든 외부 API Validation 규칙을 몰아넣으면</p>
<pre><code class="language-text">Create 요구사항
Update 요구사항
Entity 내부 규칙</code></pre>
<p>이 하나의 객체 안에 섞일 수 있다.</p>
<p>DTO를 나누는 이유가 여기서 다시 드러난다.</p>
<hr />
<h2 id="실행-흐름으로-이해하기">실행 흐름으로 이해하기</h2>
<p>지금까지의 내용을 하나의 사용자 생성 요청으로 연결해보자.</p>
<p>Client가 다음 Request를 보낸다.</p>
<pre><code class="language-json">{
  &quot;name&quot;: &quot;Alice&quot;,
  &quot;email&quot;: &quot;alice@example.com&quot;,
  &quot;age&quot;: 25
}</code></pre>
<p>Controller는 다음과 같다.</p>
<pre><code class="language-java">@PostMapping(&quot;/users&quot;)
public UserResponse createUser(
        @Valid
        @RequestBody UserCreateRequest request
) {

    return userService.createUser(request);
}</code></pre>
<p>먼저 Spring MVC가 Request Body를 읽는다.</p>
<pre><code class="language-text">HTTP Request
     │
     ▼
JSON</code></pre>
<p>그리고 DTO로 변환한다.</p>
<pre><code class="language-text">JSON
 │
 ▼
UserCreateRequest</code></pre>
<p>DTO의 Constraint를 검사한다.</p>
<pre><code class="language-text">UserCreateRequest

name
└─ @NotBlank

email
├─ @NotBlank
└─ @Email

age
└─ @Min(18)</code></pre>
<p>검증에 실패하면 Controller까지 들어오지 않는다.</p>
<pre><code class="language-text">Request DTO
    │
    ▼
Validation
    │
    X
Controller</code></pre>
<p>검증에 성공하면 Controller가 Service를 호출한다.</p>
<pre><code class="language-text">Request DTO
    │
    ▼
Controller
    │
    ▼
Service</code></pre>
<p>Service에서는 API 입력 형식이 아니라 실제 비즈니스 규칙을 처리한다.</p>
<pre><code class="language-text">&quot;Email 형식인가?&quot;
→ 이미 DTO에서 검사

&quot;이미 가입된 Email인가?&quot;
→ Service에서 확인</code></pre>
<p>그리고 필요하다면 DTO의 데이터를 이용해 Entity를 만든다.</p>
<pre><code class="language-text">UserCreateRequest
        │
        ▼
      Service
        │
        ▼
    User Entity</code></pre>
<p>Entity는 Repository를 통해 저장된다.</p>
<pre><code class="language-text">Entity
  │
  ▼
Repository
  │
  ▼
DB</code></pre>
<p>응답할 때는 Entity를 그대로 반환하지 않고 Client에게 필요한 데이터만 Response DTO로 만든다.</p>
<pre><code class="language-text">DB
 │
 ▼
Entity
 │
 ▼
UserResponse
 │
 ▼
Controller
 │
 ▼
Client</code></pre>
<p>결국 전체 구조는 다음과 같다.</p>
<pre><code class="language-text">Client
  │
  │ JSON
  ▼
Request DTO
  │
  ├─ Bean Validation
  ▼
Controller
  │
  ▼
Service
  │
  ├─ Business Validation
  ▼
Entity
  │
  ▼
Repository
  │
  ▼
DB</code></pre>
<p>응답은</p>
<pre><code class="language-text">DB
 │
 ▼
Entity
 │
 ▼
Response DTO
 │
 ▼
Controller
 │
 ▼
Client</code></pre>
<p>로 돌아간다.</p>
<hr />
<h1 id="앞서-배운-spring-구조와-함께-이해하기">앞서 배운 Spring 구조와 함께 이해하기</h1>
<p>처음에는 각각 별개의 개념처럼 보였다.</p>
<pre><code class="language-text">Spring MVC

DTO

Validation

IoC / DI

Proxy

AOP</code></pre>
<p>하지만 지금까지 공부한 내용을 연결하면 그렇지 않다.</p>
<p>HTTP Request가 들어오면 Spring MVC가 요청을 처리한다.</p>
<pre><code class="language-text">HTTP Request
     │
     ▼
DispatcherServlet
     │
     ▼
HandlerAdapter
     │
     ▼
Argument Resolver
     │
     ├─ DTO Binding
     └─ @Valid Validation
     │
     ▼
Controller</code></pre>
<p>Controller가 Service를 호출한다.</p>
<pre><code class="language-text">Controller
    │
    ▼
Service Bean</code></pre>
<p>Service에 Method Validation이 필요하다면 Proxy가 개입할 수 있다.</p>
<pre><code class="language-text">Controller
    │
    ▼
Service Proxy
    │
    ├─ Method Validation
    ▼
Service Target</code></pre>
<p>그리고 Service는 내부 데이터를 Entity로 다룬다.</p>
<pre><code class="language-text">Service
  │
  ▼
Entity
  │
  ▼
Repository</code></pre>
<p>결국 하나의 요청 안에서 지금까지 살펴본 개념들이 모두 다시 만난다.</p>
<pre><code class="language-text">HTTP Request
      │
      ▼
Spring MVC
      │
      ├─ Request Mapping
      ├─ Argument Binding
      └─ @Valid
      │
      ▼
Controller Bean
      │
      ▼
Service Proxy
      │
      └─ @Validated Method Validation
      │
      ▼
Service Target
      │
      ▼
Entity
      │
      ▼
Repository</code></pre>
<p>Spring을 공부할수록 Annotation 이름 자체보다</p>
<blockquote>
<p><strong>이 Annotation이 어느 처리 과정에 참여하는가?</strong></p>
</blockquote>
<p>를 보는 것이 중요해진다.</p>
<hr />
<h1 id="정리">정리</h1>
<p>이번 글에서는 DTO와 Validation을 살펴봤다.</p>
<p>DTO는 단순히</p>
<pre><code class="language-text">Java Object 하나 더 만드는 것</code></pre>
<p>이 아니다.</p>
<p>외부 API와 Application 내부 사이에 경계를 만드는 객체다.</p>
<pre><code class="language-text">Client
  │
  ▼
DTO
  │
  ▼
Application</code></pre>
<p>Entity는 Application 내부에서 데이터를 표현하고 영속화하기 위한 모델이고,</p>
<p>DTO는 Client 또는 계층 사이에서 필요한 데이터만 전달하기 위한 모델이다.</p>
<pre><code class="language-text">DTO
→ 전달을 위한 모델

Entity
→ 내부 데이터 모델</code></pre>
<p>그래서 Request와 Response 역시 목적에 따라 분리할 수 있다.</p>
<pre><code class="language-text">UserCreateRequest
→ Client 입력

UserResponse
→ Client 출력</code></pre>
<p>그리고 Request DTO에는 Client가 지켜야 할 입력 조건을 표현할 수 있다.</p>
<pre><code class="language-java">@NotBlank
@Email
@Min
@Size</code></pre>
<p>이 Constraint들을 실제로 Controller Request에 적용할 때는 <code>@Valid</code>를 사용한다.</p>
<pre><code class="language-text">HTTP Request
      │
      ▼
DTO Binding
      │
      ▼
@Valid
      │
      ▼
Bean Validation
      │
      ▼
Controller</code></pre>
<p>여기서 중요한 것은</p>
<blockquote>
<p><strong>Controller의 <code>@Valid</code>는 Spring MVC의 요청 바인딩 과정에서 동작한다.</strong></p>
</blockquote>
<p>는 점이다.</p>
<p>반면 Service의 Method Parameter를 검증하려면 Spring MVC가 아닌 다른 과정이 필요하다.</p>
<pre><code class="language-text">Caller
  │
  ▼
Validation Proxy
  │
  ▼
Service Target</code></pre>
<p>그래서 Service에서는 <code>@Validated</code> 기반 Method Validation이 등장하고,</p>
<p>이 구조는 지난 글에서 살펴본 <strong>AOP Proxy</strong>와 다시 연결된다.</p>
<pre><code class="language-text">@Valid
→ Spring MVC의 Request Validation

@Validated
→ Service Bean의 Method Validation
→ Proxy와 연결</code></pre>
<p>그리고 Validation 자체도 두 종류로 나눠서 생각해야 한다.</p>
<pre><code class="language-text">입력 형식 검증

@NotBlank
@Email
@Min
...

→ DTO / Bean Validation</code></pre>
<pre><code class="language-text">비즈니스 규칙 검증

Email 중복
재고 부족
주문 상태
권한

→ Service / Domain</code></pre>
<p>결국 이번 글의 핵심은 Annotation을 많이 외우는 것이 아니다.</p>
<pre><code class="language-text">어떤 데이터가 외부에서 들어오는가?

그 데이터를 어떤 객체가 받아야 하는가?

어디까지가 API의 입력 규칙인가?

어느 시점에서 검증해야 하는가?

그 검증은 Spring MVC가 수행하는가?

아니면 Proxy가 Bean Method 호출을 가로채는가?</code></pre>
<p>이 흐름을 이해하는 것이다.</p>
<p>Spring의 Validation 역시 독립적으로 존재하는 기능이 아니라,</p>
<p>지금까지 살펴본</p>
<pre><code class="language-text">Spring MVC
IoC / DI
Proxy
AOP</code></pre>
<p>위에서 자연스럽게 동작하고 있다.</p>