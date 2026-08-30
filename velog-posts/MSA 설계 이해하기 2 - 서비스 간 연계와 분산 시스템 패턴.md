<p>앞에서는 Event Storming과 Bounded Context를 통해 비즈니스의 경계를 찾고, 이를 기반으로 Microservice 후보를 도출하는 과정을 살펴봤다.</p>
<pre><code class="language-text">Domain 분석
    ↓
Event Storming
    ↓
Bounded Context
    ↓
Microservice 후보 도출</code></pre>
<p>하지만 Service의 경계를 나눴다고 해서 MSA 설계가 끝나는 것은 아니다.</p>
<p>오히려 Service를 분리한 순간부터 이전에는 크게 신경 쓰지 않아도 됐던 문제들이 나타난다.</p>
<p>Monolithic Application에서는 하나의 Application 내부에서 끝났던 호출이</p>
<pre><code class="language-text">OrderService
    ↓
InventoryService
    ↓
PaymentService</code></pre>
<p>정도였다면, Microservice로 분리한 이후에는 각각의 호출이 Network를 넘어가게 된다.</p>
<pre><code class="language-text">Order Service
      │
      ├── Network ──&gt; Inventory Service
      │
      └── Network ──&gt; Payment Service</code></pre>
<p>단순한 Method Call이 Service 간 Network Call로 바뀌는 것이다.</p>
<p>이제 다음과 같은 문제를 함께 고려해야 한다.</p>
<pre><code class="language-text">Latency
Timeout
Partial Failure
Retry
Data Consistency</code></pre>
<p>또한 각 Service가 독립적인 Database를 가지게 된다면 하나의 Transaction으로 처리하던 작업도 더 이상 쉽게 묶을 수 없다.</p>
<p>결국 MSA 설계는 Service를 잘게 나누는 작업에서 끝나지 않는다.</p>
<blockquote>
<p><strong>나눠진 Service들이 독립성을 유지하면서도 하나의 시스템으로 안정적으로 협력할 수 있도록 만드는 과정이다.</strong></p>
</blockquote>
<hr />
<h2 id="service-boundary-검증">Service Boundary 검증</h2>
<p>Event Storming과 Bounded Context를 통해 Microservice 후보를 만들었다면 실제 구현에 들어가기 전에 각 Service가 담당하게 될 기능과 다른 요소와의 관계를 조금 더 구체적으로 살펴볼 필요가 있다.</p>
<h3 id="업무-기능-분해">업무 기능 분해</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a6d1a688-1a3a-4194-bdb2-52d588e76329/image.png" /></p>
<p>상위 수준에서 하나의 기능처럼 보였던 업무도 세부 기능으로 내려가면 실제로 어떤 책임을 가지고 있는지가 드러난다.</p>
<pre><code class="language-text">대분류
  ↓
중분류
  ↓
세부 기능
  ↓
실제 Use Case</code></pre>
<p>예를 들어 <code>주문</code>이라는 기능을 구체적으로 내려가 보면 다음과 같이 나눌 수 있다.</p>
<pre><code class="language-text">주문
├─ 주문 생성
│   ├─ 상품 확인
│   ├─ 재고 확인
│   └─ 주문 정보 저장
│
├─ 주문 결제
│   ├─ 결제 요청
│   └─ 결제 결과 반영
│
└─ 주문 취소
    ├─ 결제 취소
    └─ 재고 복구</code></pre>
<p>상위 수준에서는 단순히 <code>주문</code> 하나로 보이던 기능이 실제 Use Case까지 내려가면 상품, 재고, 결제와 같은 다른 영역과 연결되어 있다는 것을 확인할 수 있다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/08609478-9b1b-418b-9c0c-3a0b37a5e558/image.png" /></p>
<p>이런 식으로 기능을 구체화하면 처음에 나눈 Bounded Context도 다시 검증할 수 있다.</p>
<p>하나의 Service가 서로 다른 변경 이유를 가진 기능을 지나치게 많이 가지고 있지는 않은지,</p>
<p>반대로 서로 다른 Service로 나눴지만 실제 업무에서는 대부분의 기능이 항상 함께 동작하고 있지는 않은지 확인할 수 있다.</p>
<p>Depth 분석 자체를 정형화된 MSA 설계 기법이라고 보기보다는,</p>
<blockquote>
<p><strong>도출한 Service Boundary가 실제 업무 기능을 기준으로 봐도 적절한지 다시 검증하는 과정</strong></p>
</blockquote>
<p>정도로 이해하는 것이 자연스럽다.</p>
<h3 id="service-dependency-확인">Service Dependency 확인</h3>
<p>Service 내부의 책임을 확인했다면 이제 시야를 Service 밖으로 넓혀야 한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fc0087d3-0512-464b-8e08-6e01067d36ae/image.png" /></p>
<p>Microservice는 다른 Microservice하고만 통신하는 것이 아니다.</p>
<p>실제 시스템에서는 하나의 Service를 중심으로 다양한 요소가 연결된다.</p>
<pre><code class="language-text">Microservice
├─ 다른 Microservice
├─ Database
├─ Cache
├─ Message Broker
├─ Object Storage
└─ External API</code></pre>
<p>예를 들어 위치 기반 기능이 필요하다면 외부 지도 API를 사용할 수 있고, 반복적으로 조회되는 데이터가 많다면 Redis와 같은 Cache를 사용할 수도 있다.</p>
<p>비동기 처리가 필요한 영역이라면 Message Broker가 등장할 수도 있다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/46aee10b-5c0a-408e-9118-c6d37445cbfb/image.png" /></p>
<p>여기서 중요한 것은 단순히 어떤 기술을 사용할지 정하는 것이 아니다.</p>
<pre><code class="language-text">Redis를 사용한다.
Kafka를 사용한다.
외부 API를 사용한다.</code></pre>
<p>보다 먼저 봐야 하는 것은 <strong>하나의 Service를 중심으로 어떤 Dependency가 만들어지는가</strong>이다.</p>
<p>특정 Service가 지나치게 많은 외부 시스템이나 다른 Microservice에 의존하고 있다면 해당 Service가 시스템 전체의 병목이나 장애 전파 지점이 될 수도 있다.</p>
<h3 id="service-요구-특성-확인">Service 요구 특성 확인</h3>
<p>Service Boundary와 Dependency를 확인할 때는 각 기능의 운영 특성도 함께 살펴볼 필요가 있다.</p>
<p>대표적으로 다음과 같은 요소가 있다.</p>
<pre><code class="language-text">Traffic 규모

Read / Write 비율

Latency 요구사항

Data Consistency 수준

Transaction 범위

장애 허용 수준</code></pre>
<p>같은 Service 내부에서도 모든 기능이 동일한 특성을 가지는 것은 아니다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/bc6d852b-06c9-4a02-80d9-400cde1889a6/image.png" /></p>
<p>Read Traffic이 많은 기능에서는 빠른 응답과 많은 요청을 처리할 수 있는 구조가 중요해질 수 있다.</p>
<p>이런 경우에는 Cache를 사용하거나 Instance를 Scale Out하고, 조회 목적에 맞는 Data 구조를 별도로 구성하는 방법을 고려할 수 있다.</p>
<p>반면 Data를 변경하는 작업에서는 Validation, Business Rule, Transaction과 같은 요소가 중요해진다.</p>
<p>특히 하나의 Write가 다른 Microservice까지 연결되기 시작하면 복잡도는 더 높아진다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/66852355-f231-4ca8-bf92-ac796e7f3bd9/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9fccde59-ddda-44e2-88a4-bbdfa03a38b7/image.png" /></p>
<p>다만 이를 단순하게</p>
<pre><code class="language-text">Read는 빠르면 된다.

Write는 Transaction이 중요하다.</code></pre>
<p>정도로 나눌 수는 없다.</p>
<p>Read에서도 강한 Consistency가 필요할 수 있고, Write 역시 일부 후속 처리는 비동기로 분리할 수 있다.</p>
<p>결국 각 기능의 Traffic, Latency, Consistency, 장애 허용 수준을 함께 보고 적절한 구조를 선택해야 한다.</p>
<hr />
<h2 id="service-간-통신">Service 간 통신</h2>
<p>Service Boundary를 잘 나눴더라도 하나의 Business 기능을 처리하기 위해서는 결국 여러 Service가 협력해야 한다.</p>
<p>예를 들어 주문을 처리한다고 해보자.</p>
<pre><code class="language-text">Order Service
     │
     ├── Inventory Service
     │
     └── Payment Service</code></pre>
<p>Order Service는 재고를 확인해야 하고 결제도 수행해야 한다.</p>
<p>Service의 경계를 정했다면 이제 <strong>Service 사이를 어떤 방식으로 연결할 것인지</strong> 결정해야 한다.</p>
<h3 id="통신-방식-선택">통신 방식 선택</h3>
<p>Service 간 통신 방식은 크게 동기와 비동기로 나눌 수 있다.</p>
<pre><code class="language-text">현재 요청에서 결과가 반드시 필요한가?
            │
            ├─ YES
            │   ↓
            │ Synchronous Communication
            │ REST / gRPC
            │
            └─ NO
                ↓
              Asynchronous Communication
              Event / Message Broker</code></pre>
<p>여기서 중요한 것은 동기와 비동기 중 무엇이 더 좋은지를 따지는 것이 아니다.</p>
<p>현재 Business Flow에서 상대 Service의 결과가 언제 필요한지를 보고 선택해야 한다.</p>
<h4 id="동기-통신">동기 통신</h4>
<p>예를 들어 주문 요청을 처리하는 순간 재고가 있는지를 반드시 알아야 한다면 동기 호출이 자연스럽다.</p>
<pre><code class="language-text">Order Service
     │
     │ 재고 확인
     ▼
Inventory Service
     │
     │ 결과 반환
     ▼
Order Service</code></pre>
<p>요청을 보낸 Service는 상대 Service의 결과가 돌아올 때까지 기다린다.</p>
<p>따라서 Business Flow를 직관적으로 구성할 수 있지만 상대 Service의 Latency와 장애에 직접적인 영향을 받는다.</p>
<h4 id="비동기-통신">비동기 통신</h4>
<p>반대로 주문 완료 이후 이메일을 보내거나 통계를 반영하는 작업이라면 현재 주문 요청과 반드시 함께 끝날 필요는 없다.</p>
<pre><code class="language-text">Order Service
      │
      │ OrderCompleted
      ▼
     Kafka
      │
      ├─ Notification Service
      └─ Analytics Service</code></pre>
<p>이렇게 현재 요청과 분리할 수 있는 작업은 Event 기반 비동기 처리로 분리할 수 있다.</p>
<p>동기와 비동기 통신은 각각 서로 다른 특성을 가지며 그에 따라 다뤄야 하는 문제도 달라진다.</p>
<pre><code class="language-text">Synchronous
→ Latency
→ Timeout
→ 장애 전파

Asynchronous
→ Message 유실
→ 중복 처리
→ 처리 순서
→ Eventual Consistency</code></pre>
<hr />
<h2 id="동기-통신의-장애-대응">동기 통신의 장애 대응</h2>
<p>동기 통신에서는 요청을 보낸 Service가 상대 Service의 응답을 기다린다.</p>
<pre><code class="language-text">Service A
    │
    ▼
Service B</code></pre>
<p>문제는 Network와 상대 Service가 항상 정상이라는 보장이 없다는 점이다.</p>
<pre><code class="language-text">Network 지연

Connection 실패

Service 장애

Response 지연</code></pre>
<p>Service B가 이미 장애 상태인데 Service A가 계속 요청을 보낸다고 해보자.</p>
<pre><code class="language-text">A → B 요청
A → B 요청
A → B 요청
A → B 요청
A → B 요청</code></pre>
<p>실패 요청이 계속 누적된다.</p>
<p>Thread와 Connection 같은 Resource가 계속 사용되고 결국 Service A까지 정상적인 요청을 처리하지 못할 수도 있다.</p>
<pre><code class="language-text">B 장애
 ↓
A 요청 적체
 ↓
A 장애
 ↓
A를 호출하는 Service까지 영향</code></pre>
<p>하나의 Service 장애가 다른 Service까지 전달되는 <strong>Cascading Failure</strong>가 발생할 수 있는 것이다.</p>
<p>따라서 분산 시스템에서는 실패가 발생하지 않기를 기대하기보다</p>
<blockquote>
<p><strong>실패가 발생했을 때 어디까지 영향을 허용할 것인지</strong></p>
</blockquote>
<p>를 설계해야 한다.</p>
<h3 id="timeout">Timeout</h3>
<p>가장 먼저 필요한 것은 상대 Service의 응답을 무한정 기다리지 않는 것이다.</p>
<pre><code class="language-text">Request
  ↓
응답 없음
  ↓
일정 시간 경과
  ↓
Timeout</code></pre>
<p>Timeout은 상대 Service의 응답을 <strong>언제까지 기다릴 것인지</strong>를 결정한다.</p>
<p>Timeout 없이 계속 기다리면 요청을 처리하는 Thread나 Connection 같은 Resource가 장시간 점유될 수 있다.</p>
<h3 id="retry">Retry</h3>
<p>장애가 일시적인 Network 문제라면 다시 요청했을 때 성공할 수도 있다.</p>
<pre><code class="language-text">1차 요청 → 실패
2차 요청 → 실패
3차 요청 → 성공</code></pre>
<p>이때 Retry를 사용할 수 있다.</p>
<p>하지만 Retry 역시 무조건 많이 수행한다고 좋은 것은 아니다.</p>
<p>상대 Service가 이미 과부하 상태인데 모든 Client가 Retry를 수행하면 오히려 요청량을 증가시켜 장애를 악화시킬 수 있다.</p>
<pre><code class="language-text">Service 장애
    ↓
대량 Retry
    ↓
Service 부하 증가
    ↓
장애 악화</code></pre>
<p>따라서 Retry 횟수를 제한하고 재시도 사이의 간격을 조정하는 Backoff 전략 등을 함께 고려할 수 있다.</p>
<p>또한 Retry는 동일한 요청이 여러 번 수행될 가능성이 있다는 의미이므로 Write 요청에서는 <strong>Idempotency</strong>도 중요해진다.</p>
<h3 id="circuit-breaker">Circuit Breaker</h3>
<p>상대 Service가 이미 지속적인 장애 상태라면 Retry를 계속 수행하는 것 역시 의미가 없다.</p>
<p>이때 사용할 수 있는 대표적인 Pattern이 Circuit Breaker다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/73ccd2ee-bab5-4aa3-b827-4876227f793c/image.png" /></p>
<p>Circuit Breaker는 전기 회로의 차단기처럼 일정 수준 이상 실패가 발생하면 실제 Service 호출 자체를 잠시 차단한다.</p>
<p>일반적으로 다음 세 상태를 가진다.</p>
<pre><code class="language-text">CLOSED
   │
   │ 실패 누적
   ▼
OPEN
   │
   │ 일정 시간 경과
   ▼
HALF_OPEN
   │
   ├─ 성공 → CLOSED
   └─ 실패 → OPEN</code></pre>
<h4 id="closed">CLOSED</h4>
<p>정상 상태다.</p>
<p>요청을 대상 Service에 그대로 전달한다.</p>
<h4 id="open">OPEN</h4>
<p>실패율이 기준을 넘으면 Circuit을 Open한다.</p>
<p>이 상태에서는 대상 Service에 실제 요청을 보내지 않는다.</p>
<p>이미 장애가 발생한 Service에 계속 요청을 보내며 Resource를 낭비하는 것을 막는다.</p>
<h4 id="half_open">HALF_OPEN</h4>
<p>일정 시간이 지나면 일부 요청을 실제 Service에 보내 복구 여부를 확인한다.</p>
<p>정상 응답이 돌아오면 CLOSED로 복귀하고, 다시 실패하면 OPEN 상태로 돌아간다.</p>
<p>Circuit Breaker가 Service 장애 자체를 해결하는 것은 아니다.</p>
<blockquote>
<p><strong>장애가 다른 Service까지 연쇄적으로 퍼지는 것을 막는 것</strong></p>
</blockquote>
<p>이 핵심이다.</p>
<h4 id="circuit-breaker-동작-흐름">Circuit Breaker 동작 흐름</h4>
<p>정상 상태에서는 요청을 그대로 대상 Service에 전달한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fb785b7e-9f2f-45e3-acba-12b288efec11/image.png" /></p>
<p>이 상태가 <code>CLOSED</code>다.</p>
<p>대상 Service의 호출 실패가 반복되기 시작하면 Circuit Breaker는 실패 상태를 기록한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d84df977-06b4-449e-b38b-71dcea9c1130/image.png" /></p>
<p>실패율이 설정한 기준을 넘어가면 Circuit을 <code>OPEN</code> 상태로 변경한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/cd810af3-d68a-4577-96cb-d650e54f6fb3/image.png" /></p>
<p>이제 대상 Service에 실제 요청을 보내지 않는다.</p>
<p>호출하는 Service의 Resource 사용을 줄일 수 있고, 장애 상태인 Service에도 복구할 시간을 줄 수 있다.</p>
<p>일정 시간이 지나면 <code>HALF_OPEN</code> 상태가 된다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c30a2aca-c63c-47a8-909f-1171c86e2cd0/image.png" /></p>
<p>일부 요청을 실제 Service로 보내 정상적으로 복구됐는지 확인한다.</p>
<p>정상 응답이 확인되면 다시 <code>CLOSED</code> 상태로 돌아간다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d25cac8f-adc2-4819-9fb2-a0262894f899/image.png" /></p>
<p>전체 흐름을 단순하게 정리하면 다음과 같다.</p>
<pre><code class="language-text">장애 발생
    ↓
호출 차단
    ↓
복구 시간 확보
    ↓
일부 요청으로 상태 확인
    ↓
정상화</code></pre>
<h3 id="fallback">Fallback</h3>
<p>Circuit Breaker가 OPEN 상태라면 대상 Service를 실제로 호출하지 않는다.</p>
<p>그렇다면 사용자에게 어떤 결과를 반환할지도 결정해야 한다.</p>
<p>이때 사용할 수 있는 전략이 Fallback이다.</p>
<p>예를 들어 추천 Service에 장애가 발생했다고 해보자.</p>
<pre><code class="language-text">Product Service
      │
      ▼
Recommendation Service</code></pre>
<p>추천 Service가 동작하지 않는다고 상품 페이지 전체를 사용할 수 없게 만드는 것은 좋지 않다.</p>
<p>대신</p>
<pre><code class="language-text">개인화 추천 실패
       ↓
인기 상품 목록 반환</code></pre>
<p>처럼 기능이 일부 제한되더라도 핵심 Service는 계속 사용할 수 있도록 만들 수 있다.</p>
<p>Fallback은 장애를 복구하는 기술이라기보다</p>
<blockquote>
<p><strong>일부 기능의 장애가 전체 사용자 경험까지 무너뜨리지 않도록 만드는 대응 전략</strong></p>
</blockquote>
<p>이다.</p>
<p>동기적인 Service 호출에서 장애 대응을 정리하면 다음과 같이 볼 수 있다.</p>
<pre><code class="language-text">얼마나 기다릴 것인가?
        ↓
Timeout

일시적인 실패인가?
        ↓
Retry

계속 실패하는가?
        ↓
Circuit Breaker

호출할 수 없다면 무엇을 반환할 것인가?
        ↓
Fallback</code></pre>
<h3 id="resilience4j">Resilience4j</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/066db0ed-786c-46bf-8108-f689ccde9de7/image.png" /></p>
<p>Java / Spring 환경에서는 Resilience4j 같은 Library를 이용해 이러한 Resilience Pattern을 구현할 수 있다.</p>
<p>대표적으로 다음 기능을 제공한다.</p>
<pre><code class="language-text">Circuit Breaker
Retry
Rate Limiter
Bulkhead
Time Limiter</code></pre>
<p>Circuit Breaker에서는 Failure Rate, OPEN 상태 유지 시간, HALF_OPEN 상태에서 허용할 요청 수 등을 설정할 수 있다.</p>
<p>다만 Library의 사용 방법보다 중요한 것은 어떤 장애 상황에 어떤 Pattern이 필요한지를 먼저 구분하는 것이다.</p>
<hr />
<h2 id="비동기-event-처리">비동기 Event 처리</h2>
<p>동기 통신이 상대 Service의 결과를 기다리는 구조라면 비동기 통신은 현재 요청과 후속 작업을 분리하는 데 사용할 수 있다.</p>
<h3 id="message-broker를-통한-비동기-처리">Message Broker를 통한 비동기 처리</h3>
<p>예를 들어 주문 완료 이후 다음과 같은 작업이 있다고 해보자.</p>
<pre><code class="language-text">알림 전송
통계 반영
추천 데이터 생성</code></pre>
<p>이를 모두 동기로 연결하면</p>
<pre><code class="language-text">Order
  ↓
Notification
  ↓
Analytics
  ↓
Recommendation
  ↓
Response</code></pre>
<p>하나의 Service가 느려지거나 장애가 발생했을 때 전체 요청에 영향을 줄 수 있다.</p>
<p>반면 Message Broker를 이용하면 현재 요청과 후속 작업을 분리할 수 있다.</p>
<pre><code class="language-text">Order Service
      │
      │ OrderCreated
      ▼
     Kafka
      │
      ├─ Notification Service
      ├─ Analytics Service
      └─ Recommendation Service</code></pre>
<p>Order Service는 자신에게 발생한 Event를 발행한다.</p>
<p>어떤 Service가 해당 Event를 소비하는지는 직접 알 필요가 없다.</p>
<p>새로운 Consumer가 추가되더라도 Producer를 수정하지 않고 확장할 수도 있다.</p>
<pre><code class="language-text">기존

Order
  ↓
Kafka
  ├─ Notification
  └─ Analytics


추가

Order
  ↓
Kafka
  ├─ Notification
  ├─ Analytics
  └─ Recommendation</code></pre>
<p>이런 방식으로 Service 사이의 직접적인 Dependency를 줄일 수 있다.</p>
<p>하지만 Message Broker를 사용한다고 해서 분산 시스템의 문제가 사라지는 것은 아니다.</p>
<p>동기 통신과는 다른 종류의 문제를 다뤄야 한다.</p>
<h3 id="event-발행과-data-정합성">Event 발행과 Data 정합성</h3>
<p>주문 생성 로직을 생각해보자.</p>
<pre><code class="language-text">Order DB 저장
      ↓
OrderCreated Event 발행</code></pre>
<p>Database에는 주문이 정상적으로 저장됐지만 Event를 발행하기 전에 Application이 장애 상태에 빠질 수도 있다.</p>
<pre><code class="language-text">Order DB 저장 성공
      ↓
Application 장애
      ↓
Kafka Event 발행 실패</code></pre>
<p>Order Service에는 주문이 존재하지만 Inventory Service나 Notification Service는 주문이 생성됐다는 사실을 알지 못하게 된다.</p>
<p>즉</p>
<pre><code class="language-text">Database Transaction
+
Message Broker Publish</code></pre>
<p>라는 두 개의 작업 사이에도 일관성 문제가 존재한다.</p>
<h3 id="transactional-outbox">Transactional Outbox</h3>
<p>이 문제를 완화하기 위해 사용할 수 있는 방법 중 하나가 Transactional Outbox Pattern이다.</p>
<p>Business Data와 발행해야 할 Event 정보를 같은 Database Transaction 안에 저장한다.</p>
<pre><code class="language-text">BEGIN

INSERT INTO orders ...
INSERT INTO outbox_events ...

COMMIT</code></pre>
<p>그 뒤 별도의 Publisher가 Outbox에 저장된 Event를 Message Broker로 전달한다.</p>
<pre><code class="language-text">Order DB
 ├─ orders
 └─ outbox_events
        │
        ▼
    Publisher
        │
        ▼
      Kafka</code></pre>
<p>이렇게 하면</p>
<pre><code class="language-text">주문 Data는 저장됐지만
발행해야 할 Event 정보 자체가 사라지는 상황</code></pre>
<p>을 줄일 수 있다.</p>
<p>다만 Outbox를 사용한다고 해서 Message가 반드시 한 번만 전달되는 것은 아니다.</p>
<h3 id="중복-event와-idempotency">중복 Event와 Idempotency</h3>
<p>Consumer가 Event를 처리한 직후 장애가 발생했다고 해보자.</p>
<pre><code class="language-text">Event 수신
   ↓
DB 처리 성공
   ↓
Consumer 장애
   ↓
처리 완료 여부 전달 실패
   ↓
Event 재전달</code></pre>
<p>동일한 Event가 다시 전달될 수 있다.</p>
<p>예를 들어 다음과 같은 처리가 있다면</p>
<pre><code class="language-text">PaymentCompleted
      ↓
Point +1000</code></pre>
<p>같은 Event가 두 번 처리됐을 때 Point가 2000 증가하는 문제가 생길 수 있다.</p>
<p>따라서 Consumer는 가능한 한 <strong>Idempotent</strong>하게 설계할 필요가 있다.</p>
<pre><code class="language-text">Event 수신
    ↓
Event ID 확인
    ↓
이미 처리한 Event?
    │
    ├─ YES → 무시
    │
    └─ NO  → 처리 후 기록</code></pre>
<p>Message Broker는 분산 시스템의 복잡성을 없애주는 것이 아니다.</p>
<p>동기 통신에서 발생하던 직접적인 결합을 줄이는 대신</p>
<pre><code class="language-text">Event 유실
중복
순서
재처리</code></pre>
<p>같은 새로운 문제를 다뤄야 한다.</p>
<h3 id="eventual-consistency">Eventual Consistency</h3>
<p>Event 기반으로 여러 Service가 상태를 전달한다면 모든 Service의 Data가 정확히 같은 순간에 변경되기는 어렵다.</p>
<pre><code class="language-text">Order Service
주문 완료

      ↓ Event

Inventory Service
아직 Event 처리 전</code></pre>
<p>잠시 동안 Service마다 바라보는 상태가 다를 수 있다.</p>
<p>이후 Event가 처리되면서 최종적으로 전체 시스템이 같은 Business 상태를 향해간다.</p>
<pre><code class="language-text">Order Service
주문 완료

      ↓ Event 처리

Inventory Service
재고 반영 완료</code></pre>
<p>이를 <strong>Eventual Consistency</strong>라고 한다.</p>
<p>분산 시스템에서는 모든 Data를 항상 즉시 일치시키려고 하기보다</p>
<pre><code class="language-text">어떤 Data는 즉시 일관성이 필요한가?

어떤 Data는 일정 시간이 지난 뒤
일치해도 되는가?</code></pre>
<p>를 Business 요구사항에 따라 판단할 필요가 있다.</p>
<hr />
<h2 id="분산-data와-transaction">분산 Data와 Transaction</h2>
<p>Service가 자신의 Business 책임뿐 아니라 자신의 Data까지 독립적으로 관리하기 시작하면 또 다른 문제가 나타난다.</p>
<h3 id="database-per-service">Database per Service</h3>
<p>Microservice의 Application만 분리하고 모든 Service가 하나의 Database를 공유한다면 Service의 독립성이 제한될 수 있다.</p>
<pre><code class="language-text">Order Service ─────┐
Payment Service ───┼── Shared Database
Inventory Service ─┘</code></pre>
<p>특정 Schema 변경이 여러 Service에 영향을 줄 수 있기 때문이다.</p>
<p>따라서 MSA에서는 각 Service가 자신의 Data를 직접 관리하는 <strong>Database per Service</strong> 형태를 사용할 수 있다.</p>
<pre><code class="language-text">Order Service
      │
      ▼
   Order DB


Payment Service
      │
      ▼
  Payment DB


Inventory Service
      │
      ▼
Inventory DB</code></pre>
<p>Service의 독립성은 높아진다.</p>
<p>대신 기존에는 하나의 Database Transaction으로 묶을 수 있었던 작업을 더 이상 쉽게 처리할 수 없게 된다.</p>
<h3 id="distributed-transaction">Distributed Transaction</h3>
<p>주문을 예로 들어보자.</p>
<pre><code class="language-text">1. 주문 생성
2. 재고 차감
3. 결제</code></pre>
<p>하나의 Database를 사용한다면 하나의 Transaction으로 처리할 수도 있다.</p>
<pre><code class="language-text">BEGIN

INSERT ORDER
UPDATE INVENTORY
INSERT PAYMENT

COMMIT</code></pre>
<p>중간에 문제가 발생하면 Rollback할 수 있다.</p>
<pre><code class="language-text">주문 저장 성공
재고 차감 성공
결제 실패

↓ Rollback

전체 변경 취소</code></pre>
<p>하지만 Service와 Database가 각각 분리되어 있다면 상황이 달라진다.</p>
<pre><code class="language-text">Order Service       → Order DB
Inventory Service   → Inventory DB
Payment Service     → Payment DB</code></pre>
<p>Order Service가 관리하는 Transaction으로 이미 Commit된 Inventory DB의 변경까지 직접 Rollback할 수는 없다.</p>
<p>이것이 MSA에서 나타나는 대표적인 <strong>분산 Transaction 문제</strong>다.</p>
<h3 id="saga-pattern">Saga Pattern</h3>
<p>Saga Pattern은 하나의 큰 Business Transaction을 여러 Service의 Local Transaction으로 나누어 처리한다.</p>
<pre><code class="language-text">주문 생성
   ↓
재고 차감
   ↓
결제</code></pre>
<p>각 Service는 자신의 Database에 대해서만 Local Transaction을 수행한다.</p>
<pre><code class="language-text">Order Service
   ↓
Order DB Commit

Inventory Service
   ↓
Inventory DB Commit

Payment Service
   ↓
Payment DB Commit</code></pre>
<p>모든 작업이 성공하면 그대로 완료된다.</p>
<p>하지만 Payment에서 실패했다고 해보자.</p>
<pre><code class="language-text">주문 생성    성공
재고 차감    성공
결제         실패</code></pre>
<p>Order와 Inventory의 Local Transaction은 이미 Commit된 상태다.</p>
<p>따라서 일반적인 Database Rollback으로 되돌릴 수 없다.</p>
<p>이때 앞에서 수행한 작업을 Business적으로 취소하는 <strong>Compensating Transaction</strong>을 수행한다.</p>
<pre><code class="language-text">Payment 실패
    ↓
재고 복구
    ↓
주문 취소</code></pre>
<p>결과적으로</p>
<pre><code class="language-text">주문 생성
   ↓
재고 차감
   ↓
결제 실패
   ↓
재고 복구
   ↓
주문 취소</code></pre>
<p>와 같이 전체 Business 상태를 다시 일관된 상태로 만들어간다.</p>
<p>Circuit Breaker와 Saga는 둘 다 분산 시스템에서 등장하지만 해결하는 문제는 다르다.</p>
<pre><code class="language-text">Circuit Breaker
→ Service 장애 전파 방지

Saga
→ 여러 Service에 걸친
  Business Transaction 정합성 관리</code></pre>
<h4 id="choreography">Choreography</h4>
<p>Saga는 여러 Service가 Event를 주고받으며 다음 작업을 이어가는 Choreography 방식으로 구성할 수 있다.</p>
<pre><code class="language-text">Order Service
     │ OrderCreated
     ▼
   Kafka
     │
     ▼
Inventory Service
     │ InventoryReserved
     ▼
   Kafka
     │
     ▼
Payment Service</code></pre>
<p>전체 흐름을 제어하는 중앙 Service는 없다.</p>
<p>각 Service가 Event를 통해 다음 작업을 이어간다.</p>
<p>Service 간 직접적인 결합도가 낮다는 장점이 있지만 참여 Service와 Event가 많아질수록 전체 Business Flow를 파악하기 어려워질 수 있다.</p>
<h4 id="orchestration">Orchestration</h4>
<p>반대로 전체 Saga 흐름을 제어하는 Orchestrator를 둘 수도 있다.</p>
<pre><code class="language-text">             ┌──&gt; Order Service
             │
Orchestrator ├──&gt; Inventory Service
             │
             └──&gt; Payment Service</code></pre>
<p>Orchestrator가 각 Service에 작업을 지시하고 결과에 따라 다음 작업이나 보상 작업을 결정한다.</p>
<p>전체 Flow를 한곳에서 확인하기 쉽지만 Orchestrator가 Business Flow를 많이 알고 있기 때문에 그만큼 책임도 커진다.</p>
<p>어떤 방식이 무조건 좋은 것은 아니다.</p>
<p>Service 수, Business Flow의 복잡도, 제어 수준 등을 고려해서 선택해야 한다.</p>
<hr />
<h2 id="api-gateway">API Gateway</h2>
<p>Service가 많아지면 내부 Service 사이의 관계뿐 아니라 외부 Client가 여러 Service에 접근하는 방식도 정리할 필요가 있다.</p>
<pre><code class="language-text">Order Service       : 8081
Inventory Service   : 8082
Payment Service     : 8083
Member Service      : 8084</code></pre>
<p>Client가 각각의 Service 주소와 Port를 직접 알고 호출하는 구조는 관리하기 어렵다.</p>
<p>이때 외부 요청의 단일 진입점으로 API Gateway를 둘 수 있다.</p>
<pre><code class="language-text">                 ┌─ Order Service
Client ─ Gateway ├─ Inventory Service
                 ├─ Payment Service
                 └─ Member Service</code></pre>
<p>Client는 Gateway 하나만 바라본다.</p>
<pre><code class="language-text">/api/orders
/api/products
/api/payments
/api/members</code></pre>
<p>Gateway는 요청을 적절한 Service로 Routing한다.</p>
<p>필요에 따라</p>
<pre><code class="language-text">Authentication
Authorization
Rate Limiting
Logging
Routing</code></pre>
<p>같이 여러 Service에 공통적으로 필요한 처리도 담당할 수 있다.</p>
<p>API Gateway는 Service 간 장애나 Data Consistency를 직접 해결하는 Pattern이라기보다는</p>
<blockquote>
<p><strong>외부 Client와 여러 Microservice 사이의 Interface를 정리하는 역할</strong></p>
</blockquote>
<p>로 보는 것이 적절하다.</p>
<hr />
<h2 id="observability">Observability</h2>
<p>Service가 하나일 때는 문제가 발생하면 하나의 Application Log부터 확인할 수 있었다.</p>
<p>하지만 MSA에서는 하나의 요청이 여러 Service를 지나갈 수 있다.</p>
<pre><code class="language-text">Client
   ↓
Gateway
   ↓
Order Service
   ↓
Inventory Service
   ↓
Kafka
   ↓
Payment Service
   ↓
Notification Service</code></pre>
<p>사용자 입장에서는 단순히</p>
<pre><code class="language-text">주문이 느리다.</code></pre>
<p>라는 하나의 현상만 보인다.</p>
<p>하지만 실제 원인은 여러 곳에 있을 수 있다.</p>
<pre><code class="language-text">Gateway가 느린가?

Order Service가 느린가?

Inventory 호출에서 Timeout이 발생했나?

Kafka Consumer가 밀렸나?

Payment Service가 느린가?</code></pre>
<p>각 Service의 Log를 하나씩 확인하는 것만으로는 전체 요청의 흐름을 파악하기 어렵다.</p>
<p>Service가 분산되면 Application뿐 아니라 <strong>장애 원인과 요청의 흐름도 함께 분산된다.</strong></p>
<p>따라서 실제 운영 가능한 MSA를 만들기 위해서는 분산된 시스템의 상태를 다시 하나의 관점에서 바라볼 수 있어야 한다.</p>
<p>대표적으로 Logs, Metrics, Traces를 함께 활용한다.</p>
<h3 id="logs">Logs</h3>
<p>각 Service에서 어떤 일이 발생했는지를 확인한다.</p>
<h3 id="metrics">Metrics</h3>
<p>CPU, Memory 같은 Resource뿐 아니라 Request Rate, Error Rate, Latency 등 시스템 상태를 수치로 확인한다.</p>
<h3 id="distributed-tracing">Distributed Tracing</h3>
<p>하나의 요청이 여러 Service를 어떤 순서로 이동했고 각 구간에서 얼마의 시간이 걸렸는지를 추적한다.</p>
<pre><code class="language-text">Request ID: abc123

Gateway           10ms
   ↓
Order Service     30ms
   ↓
Inventory        800ms
   ↓
Payment           50ms</code></pre>
<p>전체 요청이 느렸다는 사실에서 끝나는 것이 아니라 Inventory Service 구간에서 대부분의 시간이 소비됐다는 식으로 병목을 좁힐 수 있다.</p>
<blockquote>
<p><strong>Service가 분산되면 이를 다시 하나의 시스템으로 바라보기 위한 관측 수단도 함께 필요해진다.</strong></p>
</blockquote>
<hr />
<h2 id="msa-설계-흐름-정리">MSA 설계 흐름 정리</h2>
<p>앞선 글에서 Domain을 분석해 Microservice 후보를 도출했다면 이번에는 그 후보를 실제 분산 시스템으로 구성하면서 필요한 문제들을 살펴봤다.</p>
<p>전체 흐름은 다음과 같이 볼 수 있다.</p>
<pre><code class="language-text">Domain 분석
      ↓
Event Storming
      ↓
Bounded Context
      ↓
Microservice 후보
      ↓
Service Boundary 검증
      ↓
Service Dependency 분석
      ↓
Service 요구 특성 확인
      ↓
Service 간 통신 설계</code></pre>
<p>Service 사이의 통신을 설계하고 나면 사용하는 방식에 따라 서로 다른 문제가 나타난다.</p>
<pre><code class="language-text">                 Service Communication
                         │
              ┌──────────┴──────────┐
              │                     │
         Synchronous           Asynchronous
              │                     │
              ▼                     ▼
           Timeout                Event
           Retry              Message Broker
     Circuit Breaker              │
          Fallback                 ├─ Outbox
              │                    ├─ Idempotency
              │                    └─ Eventual Consistency
              │
              └──────────┬─────────┘
                         │
                         ▼
              Distributed System</code></pre>
<p>Data 역시 Service별로 분리하면 별도의 설계 문제가 생긴다.</p>
<pre><code class="language-text">Database per Service
        ↓
Local Transaction
        ↓
Distributed Transaction
        ↓
Saga
   ┌──────────────┐
   │              │
Choreography  Orchestration</code></pre>
<p>그리고 이 구조 전체를 실제 시스템으로 운영하려면 별도의 관점도 함께 필요하다.</p>
<pre><code class="language-text">외부 Client 접근
→ API Gateway

분산된 시스템 상태 파악
→ Logs / Metrics / Distributed Tracing</code></pre>
<p>MSA를 처음 접하면 가장 먼저</p>
<pre><code class="language-text">Service를 어떻게 나눌 것인가?</code></pre>
<p>에 관심을 가지게 된다.</p>
<p>물론 Service Boundary를 잘 찾는 것은 중요하다.</p>
<p>하지만 실제 시스템을 구성하면 그 다음부터 더 많은 문제를 함께 설계해야 한다.</p>
<pre><code class="language-text">Service 사이의 Dependency는 어떻게 구성할 것인가

상대 Service의 결과를 지금 기다려야 하는가

상대 Service가 장애라면 어디까지 영향을 허용할 것인가

현재 요청과 분리할 수 있는 작업은 무엇인가

Event 발행에 실패하면 어떻게 할 것인가

같은 Event가 여러 번 전달되면 어떻게 할 것인가

여러 Service의 Database에 걸친
Business Transaction은 어떻게 처리할 것인가

외부 Client는 여러 Service에 어떻게 접근할 것인가

장애가 발생했을 때
어디에서 문제가 생겼는지 어떻게 찾을 것인가</code></pre>
<p>결국 MSA 설계는 하나의 Application을 여러 개의 작은 Application으로 잘게 나누는 작업이 아니다.</p>
<p><strong>각 Service가 독립적으로 변경되고 배포될 수 있으면서도, 분산 환경에서 발생하는 Network 장애와 Data Consistency 문제를 감당하며 하나의 시스템으로 협력할 수 있도록 만드는 작업이다.</strong></p>
<p>Service를 분리하면 독립적인 변경과 배포, 확장이라는 장점을 얻을 수 있다.</p>
<p>대신 Network, 장애 처리, Event 처리, 분산 Transaction, Observability처럼 Monolith에서는 상대적으로 덜 드러났던 복잡성을 직접 다뤄야 한다.</p>
<p>결국 중요한 것은 Pattern을 많이 사용하는 것이 아니다.</p>
<blockquote>
<p><strong>Service를 분리한 결과 어떤 문제가 발생하는지를 먼저 이해하고, 그 문제에 필요한 구조와 Pattern을 선택하는 것.</strong></p>
</blockquote>
<p>그 과정까지 포함해야 비로소 Service를 단순히 나눈 구조가 아니라 실제로 운영 가능한 Microservice Architecture에 가까워진다.</p>