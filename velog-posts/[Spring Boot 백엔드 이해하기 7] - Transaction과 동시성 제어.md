<p>지난 글에서는 JPA가 Entity를 Persistence Context 안에서 관리하는 과정을 살펴봤다.</p>
<pre><code class="language-text">Entity 조회
    ↓
Persistence Context
    ↓
Managed Entity
    ↓
상태 변경
    ↓
Dirty Checking
    ↓
flush
    ↓
Database</code></pre>
<p>그 과정에서 마지막으로 Transaction이라는 경계가 등장했다.</p>
<p>예를 들어 주문을 생성한다고 해보자.</p>
<pre><code class="language-text">상품 조회
   ↓
재고 감소
   ↓
주문 생성</code></pre>
<p>재고 감소에는 성공했는데 주문 생성이 실패한다면 어떻게 될까?</p>
<pre><code class="language-text">재고
→ 감소됨

주문
→ 생성되지 않음</code></pre>
<p>각각의 Database 작업 자체는 성공했지만, 하나의 비즈니스 작업으로 보면 잘못된 결과다.</p>
<p>우리가 원하는 것은 둘 중 하나다.</p>
<pre><code class="language-text">모두 성공
→ 전체 반영

하나라도 실패
→ 전체 취소</code></pre>
<p>이처럼 여러 Database 작업을 하나의 논리적인 작업 단위로 묶는 것이 Transaction이다.</p>
<p>그런데 Spring에서 Transaction을 사용하다 보면 곧 더 복잡한 문제가 생긴다.</p>
<pre><code class="language-text">@Transactional은 어떻게 동작할까?

Transaction 안에서
다른 @Transactional Method를 호출하면?

둘은 같은 Transaction일까?

새로운 Transaction을 만들 수도 있을까?

Exception이 발생하면 언제 Rollback될까?

Transaction을 사용하면
동시성 문제도 해결될까?</code></pre>
<p>이번 글에서는 이 질문들을 하나씩 연결해보자.</p>
<hr />
<h1 id="transaction">Transaction</h1>
<p>Transaction은 여러 Database 작업을 하나의 작업 단위로 묶는다.</p>
<p>예를 들어 주문을 생성하면서 재고도 감소시켜야 한다고 하자.</p>
<pre><code class="language-java">public void order(
        Long productId,
        int quantity
) {

    decreaseStock(productId, quantity);

    createOrder(productId, quantity);
}</code></pre>
<p>두 작업은 따로 성공해서는 안 된다.</p>
<pre><code class="language-text">Transaction BEGIN
       │
       ▼
재고 감소
       │
       ▼
주문 생성
       │
       ▼
COMMIT</code></pre>
<p>둘 다 정상적으로 수행되면 결과를 확정한다.</p>
<p>반대로 중간에 문제가 발생하면</p>
<pre><code class="language-text">Transaction BEGIN
       │
       ▼
재고 감소
       │
       ▼
주문 생성
       │
       X
Exception
       │
       ▼
ROLLBACK</code></pre>
<p>이미 수행한 변경까지 취소한다.</p>
<p>즉 Transaction의 핵심은</p>
<blockquote>
<p><strong>여러 Database 작업을 하나의 성공과 실패로 묶는 것</strong></p>
</blockquote>
<p>이다.</p>
<hr />
<h2 id="acid">ACID</h2>
<p>Transaction의 성질은 흔히 ACID로 표현한다.</p>
<pre><code class="language-text">Atomicity
→ 전부 성공하거나 전부 실패한다.

Consistency
→ Transaction 전후에 데이터의 일관성을 유지한다.

Isolation
→ 동시에 실행되는 Transaction 사이의 영향을 제어한다.

Durability
→ Commit된 결과는 지속적으로 저장된다.</code></pre>
<p>여기서 특히 이번 글에서 중요하게 볼 것은 두 가지다.</p>
<pre><code class="language-text">Atomicity
→ 하나의 업무를 어디까지 묶을 것인가?

Isolation
→ 여러 Transaction이 동시에 접근하면 어떻게 할 것인가?</code></pre>
<p>첫 번째는 <code>@Transactional</code>과 Transaction 전파로 이어지고,</p>
<p>두 번째는 글 후반의 동시성 제어와 Lock으로 이어진다.</p>
<hr />
<h1 id="spring에서의-transactional">Spring에서의 @Transactional</h1>
<p>Spring에서는 Transaction을 직접 열고 닫는 대신 주로 <code>@Transactional</code>을 사용한다.</p>
<pre><code class="language-java">@Transactional
public void order(
        Long productId,
        int quantity
) {

    decreaseStock(productId, quantity);

    createOrder(productId, quantity);
}</code></pre>
<p>겉으로 보면 Annotation 하나만 붙였다.</p>
<p>하지만 실제로 필요한 작업은 훨씬 많다.</p>
<pre><code class="language-text">Transaction 시작

Business Logic 실행

성공 여부 확인

flush

Commit 또는 Rollback

Transaction 종료</code></pre>
<p>그렇다면 이 코드는 누가 실행할까?</p>
<p>이미 앞에서 배웠던 Proxy가 다시 등장한다.</p>
<hr />
<h2 id="transactional의-proxy">@Transactional의 Proxy</h2>
<p>Spring에서 일반적인 <code>@Transactional</code>은 Proxy를 통해 동작한다.</p>
<pre><code class="language-text">Caller
   │
   ▼
Transaction Proxy
   │
   ├─ Transaction BEGIN
   │
   ▼
Service Target
   │
   │ Business Logic
   ▼
Transaction Proxy
   │
   ├─ 성공 → COMMIT
   └─ 실패 → ROLLBACK</code></pre>
<p>실제 Service Method에는 Transaction 관리 코드가 없다.</p>
<pre><code class="language-java">public void order() {

    decreaseStock();

    createOrder();
}</code></pre>
<p>대신 Proxy가 Method 호출을 먼저 받아 Transaction을 시작하고 실제 Business Logic을 호출한다.</p>
<p>정상적으로 끝나면 Commit한다.</p>
<p>문제가 발생하면 Rollback한다.</p>
<p>결국</p>
<pre><code class="language-java">@Transactional</code></pre>
<p>은 단순히 Method에 특별한 능력을 넣어주는 Annotation이 아니다.</p>
<pre><code class="language-text">Caller
   ↓
Proxy
   ↓
Target</code></pre>
<p>이라는 호출 구조를 통해 Transaction 기능이 적용되는 것이다.</p>
<hr />
<h2 id="조회만-하는-transaction">조회만 하는 Transaction</h2>
<p>모든 Transaction이 데이터를 변경하는 것은 아니다.</p>
<p>조회만 하는 Method에는 다음과 같이 사용할 수 있다.</p>
<pre><code class="language-java">@Transactional(readOnly = true)
public User getUser(Long id) {

    return userRepository
            .findById(id)
            .orElseThrow();
}</code></pre>
<p><code>readOnly = true</code>는</p>
<blockquote>
<p><strong>이 Transaction은 조회를 목적으로 사용한다.</strong></p>
</blockquote>
<p>는 의도를 전달한다.</p>
<p>그래서 조회가 많은 Service라면 Class Level에 기본 설정을 둘 수도 있다.</p>
<pre><code class="language-java">@Service
@Transactional(readOnly = true)
public class UserService {

    public User getUser(Long id) {

        return userRepository
                .findById(id)
                .orElseThrow();
    }

    @Transactional
    public void changeName(
            Long id,
            String name
    ) {

        User user = userRepository
                .findById(id)
                .orElseThrow();

        user.changeName(name);
    }
}</code></pre>
<p>기본적으로는</p>
<pre><code class="language-text">UserService
→ readOnly = true</code></pre>
<p>로 동작하고,</p>
<p>변경이 필요한 Method만</p>
<pre><code class="language-java">@Transactional</code></pre>
<p>로 다시 지정하는 방식이다.</p>
<p>다만 <code>readOnly = true</code>를</p>
<pre><code class="language-text">&quot;INSERT / UPDATE를 절대 실행할 수 없게
Database를 잠가버리는 설정&quot;</code></pre>
<p>처럼 이해해서는 안 된다.</p>
<p>Framework와 Persistence Provider에 조회 Transaction이라는 의도를 전달하고 최적화에 활용될 수 있는 설정에 가깝다.</p>
<hr />
<h2 id="transaction-안에서-다른-transaction을-호출">Transaction 안에서 다른 Transaction을 호출</h2>
<p>이제 조금 더 실제적인 상황을 보자.</p>
<p>다음 두 Service가 있다.</p>
<pre><code class="language-text">OrderService
     │
     ▼
PaymentService</code></pre>
<p>둘 다 <code>@Transactional</code>이라면 어떻게 될까?</p>
<pre><code class="language-java">@Transactional
public void order() {

    paymentService.pay();
}</code></pre>
<pre><code class="language-java">@Transactional
public void pay() {

    ...
}</code></pre>
<p>질문은 이것이다.</p>
<blockquote>
<p><code>pay()</code>를 호출할 때 새로운 Transaction을 만들까?</p>
</blockquote>
<p>아니면</p>
<blockquote>
<p>이미 실행 중인 <code>order()</code>의 Transaction을 그대로 사용할까?</p>
</blockquote>
<p>이 동작을 결정하는 것이 Transaction Propagation, 트랜잭션 전파다.</p>
<hr />
<h3 id="required">REQUIRED</h3>
<p><code>@Transactional</code>의 기본 전파 방식은 <code>REQUIRED</code>다.</p>
<pre><code class="language-java">@Transactional(
    propagation = Propagation.REQUIRED
)</code></pre>
<p>의미는 간단하다.</p>
<pre><code class="language-text">기존 Transaction이 있다
→ 거기에 참여한다.

기존 Transaction이 없다
→ 새로운 Transaction을 만든다.</code></pre>
<p>예를 들어 <code>OrderService</code>에서 Transaction A가 시작되었다.</p>
<pre><code class="language-text">Transaction A

OrderService.order()
        │
        ▼
PaymentService.pay()</code></pre>
<p><code>pay()</code>도 <code>REQUIRED</code>라면 새로운 Transaction을 만들지 않는다.</p>
<pre><code class="language-text">Transaction A

┌─────────────────────────────┐
│                             │
│ OrderService.order()        │
│         │                   │
│         ▼                   │
│ PaymentService.pay()        │
│                             │
└─────────────────────────────┘</code></pre>
<p>둘은 같은 Transaction이다.</p>
<p>따라서 <code>pay()</code>에서 문제가 발생하고 Transaction이 Rollback되어야 한다면 주문 과정 전체도 영향을 받는다.</p>
<p>이게 <code>REQUIRED</code>의 핵심이다.</p>
<blockquote>
<p><strong>호출되는 Method가 Transaction을 하나 더 만드는 것이 아니라, 이미 존재하는 업무 단위에 참여한다.</strong></p>
</blockquote>
<hr />
<h3 id="requires_new">REQUIRES_NEW</h3>
<p>그런데 가끔은 내부 작업을 외부 Transaction과 분리하고 싶을 수 있다.</p>
<p>대표적인 예가 감사 기록이나 실패 Log 저장이다.</p>
<pre><code class="language-text">주문 처리
    ↓
실패
    ↓
주문 Transaction은 Rollback

하지만
실패 기록은 DB에 남기고 싶다.</code></pre>
<p>만약 Log 저장도 같은 Transaction을 사용하면</p>
<pre><code class="language-text">Main Business
      │
      ├─ 주문 변경
      ├─ Log 저장
      │
      X Exception
      │
      ▼
ROLLBACK</code></pre>
<p>Business 데이터뿐 아니라 Log도 같이 Rollback될 수 있다.</p>
<p>이럴 때 독립적인 Transaction이 필요할 수 있다.</p>
<pre><code class="language-java">@Transactional(
    propagation = Propagation.REQUIRES_NEW
)
public void saveLog(...) {

    ...
}</code></pre>
<p><code>REQUIRES_NEW</code>는 이름 그대로 새로운 Transaction을 요구한다.</p>
<pre><code class="language-text">Outer Transaction A
       │
       │ suspend
       ▼
Inner Transaction B
       │
       │ 작업
       ▼
COMMIT / ROLLBACK
       │
       ▼
Outer Transaction A
resume</code></pre>
<p>Inner Transaction은 자신의 결과를 독립적으로 결정한다.</p>
<p>예를 들어</p>
<pre><code class="language-text">Transaction A
주문 처리
     │
     ▼

Transaction B
Audit Log 저장
     │
     ▼
COMMIT

     │
     ▼

Transaction A
Exception
     │
     ▼
ROLLBACK</code></pre>
<p>이 발생했다면</p>
<pre><code class="language-text">주문 데이터
→ Rollback

Audit Log
→ 이미 별도 Transaction에서 Commit</code></pre>
<p>이 될 수 있다.</p>
<p>Logging 같은 작업에서 독립 Transaction을 사용하는 이유도 바로 이것이다.</p>
<p>바깥 Transaction의 성공 여부와 관계없이 결과를 남겨야 하는 작업을 분리할 수 있다.</p>
<p>물론 새로운 Transaction은 별도의 Database Connection 같은 Resource를 추가로 사용할 수 있기 때문에 모든 내부 호출을 무조건 <code>REQUIRES_NEW</code>로 만드는 것은 좋지 않다.</p>
<hr />
<h4 id="required와-requires_new의-차이">REQUIRED와 REQUIRES_NEW의 차이</h4>
<p>두 개를 그림 하나로 비교하면 명확하다.</p>
<pre><code class="language-text">REQUIRED

Outer
  │
  ▼
Transaction A
  │
  ├─ 작업 1
  ├─ Inner
  │    └─ 작업 2
  └─ 작업 3

→ 전부 하나의 Transaction</code></pre>
<p>반면</p>
<pre><code class="language-text">REQUIRES_NEW

Outer
  │
  ▼
Transaction A
  │
  ├─ 작업 1
  │
  │   suspend
  │
  ├───────────────┐
  │               ▼
  │        Transaction B
  │           Inner
  │             │
  │           COMMIT
  │               │
  ◀───────────────┘
  │
  ├─ 작업 3
  ▼
COMMIT / ROLLBACK</code></pre>
<p>따라서 중요한 질문은</p>
<blockquote>
<p><strong>이 작업이 바깥 업무와 반드시 함께 성공하고 실패해야 하는가?</strong></p>
</blockquote>
<p>다.</p>
<p>그렇다면 같은 Transaction에 참여시키고,</p>
<p>정말 독립적으로 확정되어야 하는 작업이라면 별도의 Transaction 경계를 고려한다.</p>
<hr />
<h3 id="proxy를-통과해야-transaction-설정이-적용된다">Proxy를 통과해야 Transaction 설정이 적용된다</h3>
<p>여기서 한 가지 주의할 점이 있다.</p>
<p><code>@Transactional</code>은 Proxy 기반으로 동작하기 때문에 같은 객체 내부에서 Method를 직접 호출하면 Proxy를 다시 거치지 않는다.</p>
<pre><code class="language-java">@Transactional
public void outer() {
    inner();
}

@Transactional(
    propagation = Propagation.REQUIRES_NEW
)
public void inner() {
}</code></pre>
<p>외부에서 <code>outer()</code>를 호출할 때는 Transaction Proxy를 통과한다.</p>
<p>하지만 <code>outer()</code> 내부에서 실행되는</p>
<pre><code class="language-java">inner();</code></pre>
<p>호출은 같은 객체 안에서 직접 이루어진다.</p>
<pre><code class="language-text">Caller
  │
  ▼
Proxy
  │
  ▼
outer()
  │
  ▼
inner()</code></pre>
<p>즉 <code>outer()</code>는 Proxy를 통과하지만, <code>inner()</code> 호출은 다시 Proxy를 통과하지 않는다.</p>
<p>그러면 Proxy가 <code>inner()</code>에 선언된</p>
<pre><code class="language-java">Propagation.REQUIRES_NEW</code></pre>
<p>를 확인하고 새로운 Transaction을 시작할 기회가 없다.</p>
<p>이것이 <strong>Self Invocation 문제</strong>다.</p>
<p>따라서 <code>@Transactional</code>에서는 Annotation이 붙어 있다는 사실만 보는 것이 아니라</p>
<blockquote>
<p><strong>해당 Method 호출이 실제 Transaction Proxy를 통과하는가?</strong></p>
</blockquote>
<p>도 함께 봐야 한다.</p>
<hr />
<h2 id="exception과-rollback">Exception과 Rollback</h2>
<p>Transaction을 사용하면 흔히 이렇게 생각한다.</p>
<pre><code class="language-text">Exception 발생
→ Rollback</code></pre>
<p>하지만 실제로는 조금 더 정확하게 이해해야 한다.</p>
<p>Spring의 기본적인 선언적 Transaction에서는 일반적으로</p>
<pre><code class="language-text">RuntimeException
Error</code></pre>
<p>가 Method 밖으로 전파되면 Rollback 대상이 된다.</p>
<p>예를 들어</p>
<pre><code class="language-java">@Transactional
public void order() {

    decreaseStock();

    throw new IllegalStateException();
}</code></pre>
<p>이라면 Transaction은 Rollback될 수 있다.</p>
<p>반면 Checked Exception은 기본 Rollback 규칙이 다르다.</p>
<p>필요하다면 명시적으로 설정할 수 있다.</p>
<pre><code class="language-java">@Transactional(
    rollbackFor = Exception.class
)
public void process()
        throws Exception {

    ...
}</code></pre>
<p>즉 Transaction의 Rollback은</p>
<pre><code class="language-text">Exception이 발생했는가?</code></pre>
<p>만 보는 것이 아니라</p>
<pre><code class="language-text">어떤 Exception인가?

밖으로 전파되었는가?

Rollback 정책은 어떻게 설정했는가?</code></pre>
<p>도 함께 봐야 한다.</p>
<hr />
<h3 id="exception을-잡아버리면">Exception을 잡아버리면?</h3>
<p>다음 코드를 보자.</p>
<pre><code class="language-java">@Transactional
public void process() {

    try {

        dangerousOperation();

    } catch (Exception e) {

        log.error(&quot;작업 실패&quot;, e);
    }
}</code></pre>
<p>내부에서는 분명 Exception이 발생했다.</p>
<p>하지만 Catch에서 처리한 뒤 Method가 정상적으로 끝났다.</p>
<p>Proxy의 관점에서는</p>
<pre><code class="language-text">Target Method 호출
       │
       ▼
정상 Return</code></pre>
<p>처럼 보일 수 있다.</p>
<p>따라서</p>
<blockquote>
<p><strong>예외를 Catch했다고 해서 Transaction도 자동으로 실패 상태가 되는 것은 아니다.</strong></p>
</blockquote>
<p>는 점을 주의해야 한다.</p>
<p>데이터 변경을 Rollback해야 하는 실패라면 예외를 다시 던지거나, Transaction 정책을 의도에 맞게 설계해야 한다.</p>
<p>즉</p>
<pre><code class="language-text">Exception 처리 전략</code></pre>
<p>과</p>
<pre><code class="language-text">Transaction Rollback 전략</code></pre>
<p>은 서로 분리해서 생각할 수 없다.</p>
<hr />
<h2 id="transactional과-동시성-문제">@Transactional과 동시성 문제</h2>
<p>여기까지 보면 Transaction이 Database의 정합성을 모두 해결해주는 것처럼 느껴질 수 있다.</p>
<p>하지만 중요한 문제가 하나 남아 있다.</p>
<blockquote>
<p><strong>여러 Transaction이 동시에 같은 데이터를 수정하면 어떻게 될까?</strong></p>
</blockquote>
<p>예를 들어 상품 재고가 10개다.</p>
<p>Transaction A가 조회한다.</p>
<pre><code class="language-text">stock = 10</code></pre>
<p>거의 동시에 Transaction B도 조회한다.</p>
<pre><code class="language-text">stock = 10</code></pre>
<p>두 Transaction 모두 재고를 하나 감소시킨다.</p>
<pre><code class="language-text">Transaction A
10 → 9</code></pre>
<pre><code class="language-text">Transaction B
10 → 9</code></pre>
<p>두 번 감소했으므로 우리가 원하는 결과는</p>
<pre><code class="language-text">stock = 8</code></pre>
<p>이다.</p>
<p>하지만 두 Transaction이 각각 자신이 읽었던 <code>10</code>을 기준으로 계산한 뒤 저장한다면 최종 결과가</p>
<pre><code class="language-text">stock = 9</code></pre>
<p>가 될 수 있다.</p>
<p>하나의 변경 결과가 다른 변경을 덮어버린 것이다.</p>
<p>이를 Lost Update라고 한다.</p>
<hr />
<h3 id="transaction과-동시성-제어는-다른-문제">Transaction과 동시성 제어는 다른 문제</h3>
<p>각 Transaction 내부에서는 문제가 없었다.</p>
<pre><code class="language-text">Transaction A
조회 → 감소 → Commit

Transaction B
조회 → 감소 → Commit</code></pre>
<p>둘 다 자신의 입장에서는 정상적인 Transaction이었다.</p>
<p>문제는 두 Transaction 사이의 경쟁이다.</p>
<pre><code class="language-text">Transaction A ─┐
               ├─ 같은 데이터
Transaction B ─┘</code></pre>
<p>따라서</p>
<pre><code class="language-java">@Transactional</code></pre>
<p>을 붙였다고 해서 모든 동시성 문제가 자동으로 해결되는 것은 아니다.</p>
<p>Transaction은</p>
<pre><code class="language-text">이 업무를 어디까지
하나의 성공/실패로 묶을 것인가?</code></pre>
<p>를 해결한다.</p>
<p>동시성 제어는</p>
<pre><code class="language-text">여러 Transaction이
같은 데이터에 접근할 때
어떻게 충돌을 제어할 것인가?</code></pre>
<p>를 해결한다.</p>
<p>서로 관련되어 있지만 다른 문제다.</p>
<hr />
<h3 id="동시성-문제">동시성 문제</h3>
<p>동시성 상황에서는 Lost Update뿐 아니라 Non-Repeatable Read, Phantom Read와 같은 여러 이상 현상이 발생할 수 있다.</p>
<p>Database의 <strong>Isolation Level</strong>은 이러한 현상을 제어하는 중요한 수단이다.</p>
<p>하지만 이번 글에서 집중할 문제는 앞에서 살펴본 것처럼</p>
<blockquote>
<p><strong>여러 Transaction이 같은 데이터를 동시에 수정할 때 발생하는 충돌</strong></p>
</blockquote>
<p>이다.</p>
<p>Application에서</p>
<pre><code class="language-text">&quot;누가 먼저 수정했는지 감지해야 한다.&quot;

&quot;이 Row는 내가 수정하는 동안
다른 Transaction이 건드리면 안 된다.&quot;</code></pre>
<p>와 같은 요구사항이 있다면 JPA에서는 대표적으로 <strong>Optimistic Lock</strong>과 <strong>Pessimistic Lock</strong>을 사용할 수 있다.</p>
<hr />
<h3 id="optimistic-lock">Optimistic Lock</h3>
<p>Optimistic Lock, 낙관적 락은 이름 그대로 조금 낙관적인 전략이다.</p>
<blockquote>
<p><strong>충돌이 자주 발생하지 않을 것이라고 보고, 먼저 Database Row를 잠그지 않은 채 작업한 뒤 수정 시점에 충돌 여부를 확인한다.</strong></p>
</blockquote>
<p>JPA에서는 <code>@Version</code>을 사용할 수 있다.</p>
<pre><code class="language-java">@Entity
public class Product {

    @Id
    private Long id;

    private Integer stock;

    @Version
    private Long version;
}</code></pre>
<p>처음 Database 상태가 다음과 같다고 하자.</p>
<pre><code class="language-text">stock = 10
version = 3</code></pre>
<p>Transaction A와 B가 동시에 조회한다.</p>
<pre><code class="language-text">Transaction A

stock = 10
version = 3</code></pre>
<pre><code class="language-text">Transaction B

stock = 10
version = 3</code></pre>
<p>A가 먼저 수정한다.</p>
<pre><code class="language-text">stock = 9
version = 4</code></pre>
<p>이제 B가 자신의 변경을 반영하려 한다.</p>
<p>B가 읽었던 Version은</p>
<pre><code class="language-text">3</code></pre>
<p>이다.</p>
<p>하지만 Database의 현재 Version은</p>
<pre><code class="language-text">4</code></pre>
<p>다.</p>
<pre><code class="language-text">내가 조회했을 때
version = 3

        ↓

현재 Database
version = 4

        ↓

누군가 먼저 수정했다.</code></pre>
<p>이 차이를 통해 충돌을 감지할 수 있다.</p>
<hr />
<h4 id="낙관적-락은-막는-것이-아니라-감지한다">낙관적 락은 막는 것이 아니라 감지한다</h4>
<p>이 부분이 중요하다.</p>
<p>낙관적 락은 처음부터 다른 Transaction의 접근을 막지 않는다.</p>
<pre><code class="language-text">A 조회 ───────────────┐
                     │
B 조회 ───────────────┤
                     │
둘 다 작업 가능       │
                     ▼
                수정 시 충돌 확인</code></pre>
<p>즉 핵심은</p>
<pre><code class="language-text">Lock을 먼저 획득한다.</code></pre>
<p>가 아니라</p>
<blockquote>
<p><strong>Version을 이용해 내가 읽은 뒤 다른 Transaction이 먼저 수정했는지 확인한다.</strong></p>
</blockquote>
<p>는 것이다.</p>
<p>충돌이 발견되면 해당 작업은 실패하게 되고 Application에서 다시 시도할지, 사용자에게 실패를 알릴지 결정해야 한다.</p>
<p>재시도는 <code>@Version</code>이 자동으로 해주는 것이 아니다.</p>
<p>필요하다면 별도의 Retry 정책을 만들어야 한다.</p>
<hr />
<h4 id="언제-optimistic-lock을-고려할까">언제 Optimistic Lock을 고려할까?</h4>
<p>예를 들어 한 데이터에 대한 수정 충돌이 비교적 드물다고 하자.</p>
<pre><code class="language-text">조회는 많음

동시 수정은 드묾</code></pre>
<p>이런 상황에서 모든 조회부터 Database Lock을 잡아버리면 불필요한 대기가 많아질 수 있다.</p>
<p>낙관적 락은 자유롭게 작업하도록 두고</p>
<pre><code class="language-text">충돌이 실제로 발생한 경우
→ 감지해서 처리</code></pre>
<p>한다.</p>
<p>따라서</p>
<blockquote>
<p><strong>충돌은 드물지만, 발생했을 때 조용히 덮어쓰는 것은 허용할 수 없는 경우</strong></p>
</blockquote>
<p>에 사용할 수 있는 전략이다.</p>
<hr />
<h3 id="pessimistic-lock">Pessimistic Lock</h3>
<p>반대로 충돌 가능성이 높다면 처음부터 접근을 제어할 수도 있다.</p>
<p>이것이 Pessimistic Lock, 비관적 락이다.</p>
<blockquote>
<p><strong>충돌이 발생할 것이라고 보고, 데이터를 사용하는 동안 Database Lock을 확보하는 방식이다.</strong></p>
</blockquote>
<p>Spring Data JPA에서는 예를 들어 다음처럼 표현할 수 있다.</p>
<pre><code class="language-java">@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query(&quot;&quot;&quot;
    select p
    from Product p
    where p.id = :id
&quot;&quot;&quot;)
Optional&lt;Product&gt; findByIdWithLock(
        @Param(&quot;id&quot;) Long id
);</code></pre>
<p>그리고 Transaction 안에서 사용한다.</p>
<pre><code class="language-java">@Transactional
public void decreaseStock(
        Long productId,
        int quantity
) {

    Product product =
            productRepository
                .findByIdWithLock(productId)
                .orElseThrow();

    product.decreaseStock(quantity);
}</code></pre>
<p>개념적인 흐름은 다음과 같다.</p>
<pre><code class="language-text">Transaction A
      │
      ▼
Product 조회
      │
      ▼
Lock 획득
      │
      ▼
재고 수정
      │
      ▼
COMMIT
      │
      ▼
Lock 해제</code></pre>
<p>그 사이 같은 데이터를 변경하려는 Transaction B는 상황에 따라 기다리게 된다.</p>
<pre><code class="language-text">Transaction A

Row Lock 획득
      │
      │ 수정 중
      │
      ▼
    COMMIT
      │
      ▼
Lock 해제


Transaction B

Row 변경 시도
      │
      ▼
    대기
      │
      ▼
A의 Lock 해제 후 진행</code></pre>
<hr />
<h4 id="비관적-락의-대가">비관적 락의 대가</h4>
<p>비관적 락은 충돌을 강하게 제어할 수 있다.</p>
<p>하지만 공짜는 아니다.</p>
<p>Lock을 잡고 있는 동안 다른 Transaction은 기다려야 한다.</p>
<pre><code class="language-text">Lock 유지 시간 증가
        ↓
다른 Transaction 대기
        ↓
처리량 감소</code></pre>
<p>여러 Row를 서로 다른 순서로 Lock하면 Deadlock 가능성도 생긴다.</p>
<p>따라서</p>
<pre><code class="language-text">&quot;정합성이 중요하니까
무조건 PESSIMISTIC_WRITE&quot;</code></pre>
<p>라고 접근해서는 안 된다.</p>
<p>충돌 빈도와 업무 특성을 보고 선택해야 한다.</p>
<hr />
<h3 id="optimistic과-pessimistic">Optimistic과 Pessimistic</h3>
<p>둘의 차이를 흐름으로 보면 가장 쉽다.</p>
<pre><code class="language-text">Optimistic

조회
 │
 ▼
자유롭게 작업
 │
 ▼
수정 / Commit
 │
 ▼
Version 확인
 │
 ├─ 같음 → 성공
 │
 └─ 다름 → 충돌</code></pre>
<p>반면</p>
<pre><code class="language-text">Pessimistic

조회
 │
 ▼
Lock 획득
 │
 ▼
작업
 │
 ▼
Commit
 │
 ▼
Lock 해제</code></pre>
<p>낙관적 락은</p>
<blockquote>
<p><strong>일단 작업하고 나중에 충돌을 확인한다.</strong></p>
</blockquote>
<p>비관적 락은</p>
<blockquote>
<p><strong>먼저 접근을 제어하고 작업한다.</strong></p>
</blockquote>
<p>라고 이해하면 된다.</p>
<hr />
<h2 id="transaction의-범위설정">Transaction의 범위설정</h2>
<p>이제 지금까지 내용을 조금 더 실제 코드 관점에서 생각해보자.</p>
<p>Transaction은 데이터를 안전하게 처리하기 위해 필요하다.</p>
<p>그렇다고 Method 전체를 무조건 길게 Transaction으로 묶는 것이 좋은 것은 아니다.</p>
<p>예를 들어</p>
<pre><code class="language-text">Transaction BEGIN
      │
      ▼
DB 조회
      │
      ▼
외부 API 호출
      │
      │ 5초 대기
      ▼
파일 작업
      │
      ▼
DB 수정
      │
      ▼
COMMIT</code></pre>
<p>처럼 Database와 직접 관계없는 긴 작업이 Transaction 안에 들어가면 Transaction이 필요 이상으로 오래 유지될 수 있다.</p>
<p>특히 Lock까지 사용하고 있다면 더욱 문제가 커질 수 있다.</p>
<pre><code class="language-text">긴 Transaction
      ↓
Connection 점유 증가
      ↓
Lock 유지 증가
      ↓
다른 Transaction 대기</code></pre>
<p>그래서 Transaction은 단순히 크게 묶는 것이 아니라</p>
<blockquote>
<p><strong>같이 성공하고 실패해야 하는 Business Logic의 범위를 기준으로 명확하게 잡는 것</strong></p>
</blockquote>
<p>이 중요하다.</p>
<hr />
<h1 id="정리">정리</h1>
<p>Transaction의 가장 기본적인 역할은 여러 Database 작업을 하나의 논리적인 작업 단위로 묶는 것이다.</p>
<pre><code class="language-text">BEGIN
  │
  ▼
작업 1
  │
작업 2
  │
작업 3
  │
  ▼
COMMIT</code></pre>
<p>중간에 문제가 발생하면</p>
<pre><code class="language-text">ROLLBACK</code></pre>
<p>하여 전체 작업을 취소한다.</p>
<p>Spring에서는 <code>@Transactional</code>을 통해 이를 선언적으로 사용할 수 있다.</p>
<p>하지만 실제 동작은 Proxy를 기반으로 한다.</p>
<pre><code class="language-text">Caller
   │
   ▼
Transaction Proxy
   │
   ├─ BEGIN
   ▼
Target Method
   │
   ▼
Transaction Proxy
   │
   ├─ COMMIT / ROLLBACK
   ▼
Caller</code></pre>
<p>그리고 Transactional Method가 다른 Transactional Method를 호출하면 전파 방식에 따라 Transaction의 경계가 결정된다.</p>
<pre><code class="language-text">REQUIRED

기존 Transaction 있음
→ 참여

기존 Transaction 없음
→ 새로 생성</code></pre>
<pre><code class="language-text">REQUIRES_NEW

기존 Transaction이 있어도
→ 별도의 Transaction 생성</code></pre>
<p>하지만 <code>@Transactional</code>은 Proxy 기반이기 때문에 같은 객체 내부의 Self Invocation에서는 새로운 Transaction 설정이 적용되지 않을 수 있다.</p>
<pre><code class="language-text">Proxy를 통과하는가?

→ Transaction 설정이 실제로 적용되는지를
  판단할 때 매우 중요하다.</code></pre>
<p>Rollback 역시 단순히 Exception이 발생했다는 사실만 보는 것이 아니다.</p>
<pre><code class="language-text">Exception 종류
전파 여부
Rollback 정책</code></pre>
<p>을 함께 봐야 한다.</p>
<p>그리고 가장 중요한 점이 하나 남는다.</p>
<blockquote>
<p><strong>Transaction이 존재한다고 해서 여러 사용자의 동시 접근 문제가 자동으로 해결되는 것은 아니다.</strong></p>
</blockquote>
<pre><code class="language-text">Transaction
→ 하나의 업무를 원자적으로 처리

Concurrency Control
→ 여러 Transaction 사이의 충돌을 제어</code></pre>
<p>동시에 같은 데이터를 변경할 때는 Lost Update와 같은 문제가 발생할 수 있다.</p>
<p>이때 JPA에서는 상황에 따라</p>
<pre><code class="language-text">Optimistic Lock

@Version
→ 충돌을 나중에 감지</code></pre>
<p>또는</p>
<pre><code class="language-text">Pessimistic Lock

@Lock(PESSIMISTIC_WRITE)
→ 먼저 DB Lock을 확보</code></pre>
<p>같은 방법을 사용할 수 있다.</p>
<p><code>@Version</code>을 이용한 충돌 감지와 비관적 Lock에 의한 접근 제어는 각각 다른 비용과 동작 방식을 가진다.</p>
<p>결국 Transaction을 한 문장으로 정리하면 다음과 같다.</p>
<blockquote>
<p><strong>Transaction은 여러 Database 작업을 하나의 일관된 업무 단위로 묶어 성공과 실패의 경계를 만들고, Spring은 이를 Proxy 기반의 <code>@Transactional</code>로 관리한다. 그리고 여러 Transaction 사이에서 발생하는 충돌은 별도의 동시성 제어 전략으로 해결해야 한다.</strong></p>
</blockquote>
<hr />
<p>이번 7편까지 연결하면 지금까지 따로 공부했던 Spring의 개념들도 하나의 요청 안에서 거의 전부 만난다.</p>
<pre><code class="language-text">Client
  │
  ▼
HTTP Request
  │
  ▼
DispatcherServlet
  │
  ▼
Controller
  │
  ├─ DTO
  └─ Validation
  │
  ▼
Service Proxy
  │
  ├─ AOP
  └─ @Transactional
  │
  ▼
Service
  │
  ▼
Repository
  │
  ▼
Spring Data JPA
  │
  ▼
EntityManager
  │
  ▼
Persistence Context
  │
  ├─ Entity 관리
  ├─ 연관관계
  ├─ Dirty Checking
  └─ Flush
  │
  ▼
Hibernate
  │
  ▼
JDBC
  │
  ▼
Database
  │
  ├─ Transaction
  └─ Concurrency Control</code></pre>
<p>처음에는 <code>Controller</code>, <code>Service</code>, <code>Repository</code>, <code>@Transactional</code>, <code>@ManyToOne</code> 같은 것들이 각각 독립적인 Spring 기능처럼 보인다.</p>
<p>하지만 전체 요청 흐름으로 보면 결국 하나의 구조다.</p>
<p>Spring Boot가 대신해주는 것이 많아서 코드가 간단해 보일 뿐, 그 아래에서는 IoC와 DI가 객체를 연결하고, Proxy와 AOP가 호출을 가로채고, JPA가 Entity를 관리하며, Transaction이 Database 변경의 경계를 지키고 있다.</p>
<p>이 구조를 이해하고 나면 Spring Boot를 단순히 Annotation을 붙여 사용하는 Framework가 아니라, <strong>각 계층과 실행 원리가 어떻게 연결되어 하나의 Backend Application을 만드는지</strong>로 바라볼 수 있게 된다.</p>