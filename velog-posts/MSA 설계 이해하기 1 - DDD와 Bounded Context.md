<h2 id="microservice-경계의-출발점">Microservice 경계의 출발점</h2>
<p>Microservice Architecture를 처음 접하면 하나의 Application을 여러 Service로 나누는 모습을 먼저 떠올리게 된다.</p>
<pre><code class="language-text">Monolith

┌─────────────────────────────┐
│ 회원 │ 주문 │ 결제 │ 배송 │
└─────────────────────────────┘

            ↓

Microservices

회원 Service
주문 Service
결제 Service
배송 Service</code></pre>
<p>문제는 <strong>무엇을 기준으로 나눌 것인가</strong>다.</p>
<p>기능이나 화면을 기준으로 단순히 잘게 나누면 실제 Business에서는 항상 함께 움직이는 기능이 서로 다른 Service로 갈라질 수 있다.</p>
<p>반대로 하나의 Service 안에 서로 다른 Business 책임이 뒤섞일 수도 있다.</p>
<p>Microservice는 작은 Service를 많이 만드는 것이 아니라 <strong>독립적으로 변경되고 배포될 수 있는 경계를 찾는 것</strong>이 중요하다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/425420ed-ba4c-41e9-b6f8-2054a5fec17d/image.png" /></p>
<p>그래서 MSA의 Service Boundary를 찾을 때는 기술 구조보다 먼저 Business Domain을 바라보게 된다.</p>
<hr />
<h2 id="domain-중심의-설계">Domain 중심의 설계</h2>
<p>예를 들어 쇼핑몰을 기술 구조로 바라보면 다음과 같이 나눌 수 있다.</p>
<pre><code class="language-text">Controller
Service
Repository
Database</code></pre>
<p>Application 구현에는 필요한 구조지만 이것만으로는 주문과 결제의 책임이 어디에서 나뉘는지, 재고와 주문이 얼마나 강하게 연결되는지 알 수 없다.</p>
<p>MSA에서 필요한 것은 기술 계층의 분리가 아니라 <strong>Business Capability를 기준으로 독립적인 영역을 찾는 것</strong>이다.</p>
<pre><code class="language-text">Shopping Domain

├─ 회원
├─ 상품
├─ 주문
├─ 결제
└─ 배송</code></pre>
<p>Software가 해결하려는 전체 Business 문제 영역을 <strong>Domain</strong>이라고 한다.</p>
<p>그리고 하나의 Domain 안에서도 서로 다른 Business 문제 영역을 나눌 수 있는데, 이를 <strong>Subdomain</strong>이라고 한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6d80f943-59dc-483c-ba9e-4a6f530b77c1/image.png" /></p>
<p>Subdomain은 Business에서 가지는 역할에 따라 다음과 같이 구분하기도 한다.</p>
<pre><code class="language-text">Core Subdomain
Supporting Subdomain
Generic Subdomain</code></pre>
<h3 id="core-subdomain">Core Subdomain</h3>
<p>Business의 핵심 경쟁력을 만드는 영역이다.</p>
<p>예를 들어 배송 최적화 자체가 서비스의 차별점이라면 배송 최적화가 Core Subdomain이 될 수 있다.</p>
<h3 id="supporting-subdomain">Supporting Subdomain</h3>
<p>Core Subdomain을 지원하는 Business 영역이다.</p>
<p>Business에 필요하지만 핵심적인 차별화 요소는 아닌 영역이다.</p>
<h3 id="generic-subdomain">Generic Subdomain</h3>
<p>여러 Business에서 비슷한 형태로 사용할 수 있는 일반적인 영역이다.</p>
<p>인증이나 일반적인 알림 기능 등이 상황에 따라 여기에 해당할 수 있다.</p>
<p>이렇게 Domain을 나누는 이유는 단순히 기능을 분류하기 위해서가 아니다.</p>
<p><strong>서로 다른 Business 문제를 하나의 Model 안에 억지로 넣지 않기 위해서다.</strong></p>
<hr />
<h2 id="ubiquitous-language와-domain-model">Ubiquitous Language와 Domain Model</h2>
<p>Domain을 나누다 보면 같은 단어가 영역에 따라 다른 의미로 사용되는 경우가 나타난다.</p>
<p>예를 들어 <code>상품</code>을 생각해보자.</p>
<pre><code class="language-text">판매 영역의 상품

상품명
판매가
할인율
판매 상태</code></pre>
<p>재고 영역에서는 같은 상품이라도 관심사가 다르다.</p>
<pre><code class="language-text">재고 영역의 상품

SKU
창고 위치
현재 재고
안전 재고</code></pre>
<p><code>고객</code> 역시 마찬가지다.</p>
<pre><code class="language-text">주문에서의 고객
→ 주문을 생성한 사람

배송에서의 고객
→ 상품을 전달받는 사람

마케팅에서의 고객
→ 구매 행동을 분석할 대상</code></pre>
<p>이런 차이를 무시하고 하나의 <code>Customer</code>, <code>Product</code> Model에 모든 정보를 넣기 시작하면 Model의 책임과 의미가 계속 커진다.</p>
<p>DDD에서는 Domain 전문가와 개발자가 Business에서 사용하는 개념을 명확하게 정의하고, 그 언어를 대화뿐 아니라 Model과 Code에서도 일관되게 사용한다.</p>
<p>이를 <strong>Ubiquitous Language</strong>라고 한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/27c317cc-fc9e-4e23-9a36-61c6597b420c/image.png" /></p>
<p>예를 들어 Business에서 <code>주문 확정</code>이라고 부르는 개념이 있다면 Code에서도 그 의미가 드러나는 형태로 표현하는 것이다.</p>
<pre><code class="language-java">order.confirm();</code></pre>
<p>Ubiquitous Language의 목적은 단순한 용어 통일이 아니다.</p>
<blockquote>
<p><strong>Business에서 사용하는 언어와 Software가 표현하는 Domain Model 사이의 간격을 줄이는 것</strong></p>
</blockquote>
<p>이 핵심이다.</p>
<hr />
<h2 id="bounded-context">Bounded Context</h2>
<p>같은 단어가 Domain에 따라 다른 의미를 가진다면 그 의미가 유효한 범위도 명확하게 나눌 필요가 있다.</p>
<p>이 경계가 <strong>Bounded Context</strong>다.</p>
<pre><code class="language-text">┌──────── Order Context ────────┐

Order
Customer
OrderItem

Customer
→ 주문을 생성한 사용자

└──────────────────────────────┘


┌────── Delivery Context ───────┐

Delivery
Receiver
Address

Customer
→ 상품을 전달받는 대상

└──────────────────────────────┘</code></pre>
<p>Bounded Context는 단순한 Package나 Directory 경계가 아니다.</p>
<blockquote>
<p><strong>특정 Domain Model과 Ubiquitous Language가 일관된 의미를 가지는 경계</strong></p>
</blockquote>
<p>라고 볼 수 있다.</p>
<h3 id="subdomain과-bounded-context">Subdomain과 Bounded Context</h3>
<p>Subdomain과 Bounded Context는 비슷해 보이지만 관점이 다르다.</p>
<pre><code class="language-text">Subdomain
→ Business 문제 영역

Bounded Context
→ 해당 문제를 Software Model로 표현하는 경계</code></pre>
<p>즉 Business에서 문제 영역을 발견하고, 이를 Software 안에서 명확한 Model의 경계로 표현하는 과정에서 Bounded Context가 등장한다.</p>
<p>하나의 Subdomain과 하나의 Bounded Context가 자연스럽게 대응될 수도 있지만 항상 1:1일 필요는 없다.</p>
<p>중요한 것은 개수가 아니라 <strong>Context 내부에서 Language와 Model의 의미가 일관적인가</strong>다.</p>
<h3 id="context-map">Context Map</h3>
<p>Bounded Context를 나눴다고 Context들이 서로 완전히 독립되는 것은 아니다.</p>
<p>주문, 결제, 배송은 서로 다른 Context지만 하나의 Business Flow 안에서는 관계를 가진다.</p>
<pre><code class="language-text">Order Context
      ↓
Payment Context
      ↓
Delivery Context</code></pre>
<p>이처럼 Bounded Context 사이의 관계를 표현한 것이 <strong>Context Map</strong>이다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/07d2ebe4-ae3e-4a75-8833-7b3b4985eb3d/image.png" /></p>
<p>Context Map에서는 어떤 Context가 존재하고 서로 어떤 관계를 가지는지를 확인한다.</p>
<p>이 단계에서 REST나 Kafka 같은 실제 통신 기술까지 결정하는 것은 아니다.</p>
<p>먼저 <strong>Business와 Domain Model 관점의 Dependency를 확인하는 것</strong>이 중요하다.</p>
<hr />
<h2 id="event-storming">Event Storming</h2>
<p>DDD의 개념을 이해했다고 해서 실제 프로젝트에서 Bounded Context가 바로 보이는 것은 아니다.</p>
<p>Business Rule은 문서에 명확하게 정리되어 있지 않을 수도 있고, 여러 업무 담당자의 경험 속에 흩어져 있을 수도 있다.</p>
<p>이런 Domain을 여러 이해관계자가 함께 펼쳐놓고 탐색하는 방법 중 하나가 <strong>Event Storming</strong>이다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3b78fccb-5916-4390-b7e6-1b9647f0fc36/image.png" /></p>
<p>Event Storming에서는 처음부터</p>
<pre><code class="language-text">Order Service
Payment Service
Inventory Service</code></pre>
<p>처럼 기술 구조를 정하지 않는다.</p>
<h3 id="domain-event-도출">Domain Event 도출</h3>
<p>먼저 실제 Business에서 발생한 사건을 찾는다.</p>
<pre><code class="language-text">회원이 가입되었다.

주문이 생성되었다.

결제가 승인되었다.

재고가 차감되었다.

배송이 시작되었다.</code></pre>
<p>이처럼 Business에서 이미 발생한 의미 있는 사건을 <strong>Domain Event</strong>라고 한다.</p>
<p>Domain Event는 이미 발생한 사실이므로 일반적으로 과거형으로 표현한다.</p>
<pre><code class="language-text">주문 생성
X

주문이 생성되었다
O</code></pre>
<p>이 Event들을 시간 순서로 펼쳐놓으면 Business의 전체 흐름이 나타나기 시작한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a0ae4689-8779-449a-8a0d-5c7fd1061802/image.png" /></p>
<h3 id="command와-business-flow">Command와 Business Flow</h3>
<p>Event가 정리되면 해당 Event를 발생시킨 행동을 찾는다.</p>
<p>이를 <strong>Command</strong>라고 한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/eb00579b-02ef-4a21-99cd-b2f57709a8ee/image.png" /></p>
<pre><code class="language-text">주문 생성
    ↓
주문이 생성되었다


결제 승인
    ↓
결제가 승인되었다</code></pre>
<p>여기에 Command를 실행한 Actor, 특정 Event 이후 다음 행동을 발생시키는 Policy, 외부 시스템 등을 붙이면 Business Flow가 구체화된다.</p>
<pre><code class="language-text">Actor
  ↓
Command
  ↓
Aggregate
  ↓
Domain Event
  ↓
Policy
  ↓
Next Command</code></pre>
<p>Event Storming의 핵심은 각각의 요소를 외우는 것이 아니다.</p>
<p>Business Flow를 펼쳐놓고</p>
<pre><code class="language-text">이 Event는 왜 발생했는가

누가 이 행동을 시작했는가

어떤 Rule을 통과해야 하는가

이후에는 어떤 행동이 이어지는가

서로 다른 의미를 가진 영역은 어디에서 나뉘는가</code></pre>
<p>를 찾아가는 데 있다.</p>
<h3 id="aggregate">Aggregate</h3>
<p>Command가 상태를 변경할 때 해당 Business Rule과 데이터 일관성을 책임지는 Domain Model의 경계가 필요하다.</p>
<p>이를 <strong>Aggregate</strong>라고 한다.</p>
<p>예를 들어 주문을 다음과 같이 구성할 수 있다.</p>
<pre><code class="language-text">Order Aggregate

Order ← Aggregate Root
├─ OrderItem
└─ DeliveryAddress</code></pre>
<p>외부에서는 Aggregate Root인 <code>Order</code>를 통해 주문 상태를 변경한다.</p>
<p>이를 통해</p>
<pre><code class="language-text">취소된 주문에는 상품을 추가할 수 없다.

주문 금액은 OrderItem의 합계와 일치해야 한다.</code></pre>
<p>같은 Business Rule을 하나의 일관성 경계 안에서 관리할 수 있다.</p>
<p>Aggregate는 Entity 하나와 같은 개념도 아니고 DB Table을 묶는 기준도 아니다.</p>
<blockquote>
<p><strong>함께 일관성을 지켜야 하는 Domain Object의 경계</strong></p>
</blockquote>
<p>라고 보는 것이 적절하다.</p>
<h3 id="bounded-context-후보-식별">Bounded Context 후보 식별</h3>
<p>Event와 Command, Aggregate를 전체 Business Flow에 배치하면 서로 강하게 관련된 영역이 보이기 시작한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e254a496-a2e0-4da7-bd76-a0bc872ec905/image.png" /></p>
<p>예를 들어</p>
<pre><code class="language-text">회원 가입
회원 탈퇴
회원 정보 수정</code></pre>
<p>과 관련된 Model과 Rule은 하나의 영역으로 묶일 수 있다.</p>
<p>반면</p>
<pre><code class="language-text">게시글 작성
게시글 수정
댓글 작성</code></pre>
<p>은 다른 Business Language와 Model을 가질 수 있다.</p>
<p>이때 다음과 같은 기준을 함께 살펴볼 수 있다.</p>
<pre><code class="language-text">같은 Business Language를 사용하는가

같은 Business Rule에 의해 변경되는가

함께 변경되는 Model인가

같은 용어가 다른 의미로 사용되기 시작하는가</code></pre>
<p>이런 경계를 따라 Bounded Context 후보를 찾는다.</p>
<p>Event Storming에서 Bounded Context가 자동으로 계산되어 나오는 것은 아니다.</p>
<p><strong>Business Flow와 Model을 충분히 펼친 뒤 응집도가 높은 영역과 의미가 달라지는 지점을 발견하는 과정</strong>이다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c81a9a69-173a-4d35-87b5-54c38d115a39/image.png" /></p>
<hr />
<h2 id="bounded-context에서-microservice로">Bounded Context에서 Microservice로</h2>
<p>Domain 분석을 통해 다음과 같은 Bounded Context가 나왔다고 해보자.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/13e6c3c1-0fba-4375-85e4-da763c9dc8dd/image.png" /></p>
<pre><code class="language-text">회원 관리 Context

게시판 Context

Q&amp;A Context</code></pre>
<p>각 Context가 독립적인 Business 책임과 Domain Model을 가지고 있다면 자연스럽게 Microservice 후보가 될 수 있다.</p>
<pre><code class="language-text">회원 관리 Context
        ↓
회원 Service

게시판 Context
        ↓
게시판 Service

Q&amp;A Context
        ↓
Q&amp;A Service</code></pre>
<p>다만 다음처럼 기계적으로 대응시키는 것은 아니다.</p>
<pre><code class="language-text">Bounded Context 1개
=
Microservice 1개</code></pre>
<p>Bounded Context는 <strong>Domain Model의 경계</strong>이고 Microservice는 <strong>독립적으로 개발하고 배포할 수 있는 Software Unit</strong>이다.</p>
<p>실제 Service Boundary를 확정하려면 Domain Boundary뿐 아니라 다음과 같은 운영적인 조건도 함께 봐야 한다.</p>
<pre><code class="language-text">변경 빈도

배포 단위

Data 관리

Transaction 범위

Service 간 통신량

팀 구조</code></pre>
<p>Microservice를 지나치게 작게 나누면 오히려</p>
<pre><code class="language-text">Service A
  ↓
Service B
  ↓
Service C
  ↓
Service D</code></pre>
<p>처럼 계속 서로를 호출해야 하는 강하게 결합된 분산 시스템이 될 수도 있다.</p>
<p>따라서 Bounded Context는 Microservice의 정답이라기보다 <strong>Service Boundary를 판단할 수 있는 강력한 후보 경계</strong>라고 보는 것이 적절하다.</p>
<hr />
<h2 id="msa-설계의-다음-단계">MSA 설계의 다음 단계</h2>
<p>지금까지의 흐름을 정리하면 다음과 같다.</p>
<pre><code class="language-text">Business Domain
      ↓
Subdomain
      ↓
Ubiquitous Language
      ↓
Bounded Context
      ↓
Context Map
      ↓
Microservice 후보</code></pre>
<p>Event Storming은 이 과정에서 실제 Business Flow를 펼쳐 Domain과 Boundary를 탐색하는 방법으로 활용할 수 있다.</p>
<pre><code class="language-text">Event Storming
      ↓
Domain Event
      ↓
Command / Actor
      ↓
Aggregate
      ↓
Bounded Context 후보</code></pre>
<p>결국 중요한 것은 기술 구조부터 먼저 나누는 것이 아니다.</p>
<p><strong>Business에서 함께 움직이는 Model과 Rule을 찾고, 서로 다른 의미와 책임이 나타나는 지점에서 경계를 만드는 것</strong>이 먼저다.</p>
<p>이렇게 Microservice 후보를 도출하면 다음 단계부터는 다른 문제가 시작된다.</p>
<pre><code class="language-text">Order Service
      │
      │ Network
      ▼
Payment Service</code></pre>
<p>Application 내부에서 끝나던 호출이 Network를 넘어가고, 각 Service가 별도의 Database를 가지면서 Transaction의 범위도 달라진다.</p>
<p>즉 첫 번째 설계 단계가</p>
<blockquote>
<p><strong>어디까지 하나의 Service로 볼 것인가</strong></p>
</blockquote>
<p>였다면,</p>
<p>다음 단계는</p>
<blockquote>
<p><strong>나뉜 Service들이 분산 환경에서 어떻게 협력할 것인가</strong></p>
</blockquote>
<p>가 된다.</p>
<p>다음 글에서는 Service Dependency와 통신 방식, Circuit Breaker, Event 기반 통신, 분산 Transaction과 Saga 등 <strong>Microservice를 나눈 이후의 설계</strong>를 이어서 살펴본다.</p>