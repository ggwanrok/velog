<p>이전 글에서는 RAG를 통해 LLM에게 외부 지식을 가져오는 방법을 살펴봤다.</p>
<p>그런데 <strong>정보를 안다고 해서 일을 할 수 있는 것은 아니다.</strong></p>
<pre><code class="language-text">&quot;배송 규정이 어떻게 돼?&quot;</code></pre>
<p>이런 질문은 문서를 검색하면 된다.</p>
<p>반면</p>
<pre><code class="language-text">&quot;내 주문 지금 어디야?&quot;

&quot;그럼 취소해줘.&quot;</code></pre>
<p>는 다르다.</p>
<p>첫 번째 질문은 현재 주문 데이터를 조회해야 하고, 두 번째 요청은 실제 시스템의 기능을 실행해야 한다.</p>
<p>RAG가 LLM에게 <strong>지식</strong>을 붙여주는 과정이었다면,</p>
<p>이번에는 LLM에게 <strong>행동할 수 있는 수단</strong>을 붙여본다.</p>
<pre><code class="language-text">RAG
→ 외부 지식을 가져온다.

Tool
→ 외부 기능을 사용한다.

Agent
→ 결과를 보고 다음 행동을 다시 결정한다.

MCP
→ 외부 Tool과 연결되는 방식을 표준화한다.

Advisor
→ 이 전체 AI 요청 흐름에 공통 정책을 적용한다.</code></pre>
<p>단순한 모델 호출에서 실제 AI Application으로 넘어가면서 어떤 구조들이 추가되는지 하나씩 살펴보자.</p>
<hr />
<h1 id="tool-calling">Tool Calling</h1>
<p>Tool Calling은 LLM이 Application에 존재하는 기능을 선택해서 사용할 수 있도록 만드는 방식이다.</p>
<p>다만 한 가지를 먼저 분명히 해야 한다.</p>
<blockquote>
<p><strong>무엇을 사용할지는 모델이 판단하지만, 실제 실행은 Application이 한다.</strong></p>
</blockquote>
<p>예를 들어 사용자가 다음과 같이 질문했다고 해보자.</p>
<pre><code class="language-text">&quot;주문번호 12345 배송 상태 알려줘.&quot;</code></pre>
<p>모델에게 <code>getOrderStatus</code>라는 Tool이 제공되어 있다면 모델은 배송 상태를 지어내는 대신 다음과 같은 Tool Call을 만들 수 있다.</p>
<pre><code class="language-text">getOrderStatus({
    &quot;orderId&quot;: &quot;12345&quot;
})</code></pre>
<p>이것은 실제 Java Method가 실행된 것이 아니다.</p>
<p>모델이</p>
<pre><code class="language-text">이 기능을
이 Argument로 실행해줘.</code></pre>
<p>라고 요청한 것이다.</p>
<p>Application은 이 Tool Call을 받아 실제 코드를 실행한다.</p>
<pre><code class="language-java">orderService.getOrderStatus(&quot;12345&quot;);</code></pre>
<p>결과가</p>
<pre><code class="language-text">배송 중, 8월 24일 도착 예정</code></pre>
<p>이라면 해당 결과를 다시 모델에게 전달한다.</p>
<p>모델은 그 결과를 바탕으로 최종 답변을 만든다.</p>
<pre><code class="language-text">&quot;주문번호 12345는 현재 배송 중이며,
8월 24일 도착 예정입니다.&quot;</code></pre>
<p>전체 흐름은 다음과 같다.</p>
<pre><code class="language-text">사용자
    ↓
LLM
    ↓
Tool 필요 여부 판단
    ↓
Tool Call
    ↓
Application
    ↓
실제 코드 실행
    ↓
Tool Result
    ↓
LLM
    ↓
최종 답변</code></pre>
<p>즉 Tool Calling은 LLM이 직접 DB나 API를 사용하는 구조가 아니다.</p>
<pre><code class="language-text">LLM
→ 어떤 기능이 필요한지 판단

Application
→ 실제 기능을 실행</code></pre>
<p>모델의 판단과 Application의 실행을 연결하는 것이 Tool Calling의 출발점이다.</p>
<hr />
<h2 id="tool-정의">Tool 정의</h2>
<p>Spring AI에서는 일반 Java Method에 <code>@Tool</code>을 붙여 모델이 사용할 수 있는 기능으로 노출할 수 있다.</p>
<pre><code class="language-java">@Component
public class OrderTools {

    private final OrderService orderService;

    public OrderTools(OrderService orderService) {
        this.orderService = orderService;
    }

    @Tool(
        description = &quot;주문번호를 이용해 현재 주문의 배송 상태를 조회한다.&quot;
    )
    public String getOrderStatus(
        @ToolParam(description = &quot;조회할 주문번호&quot;)
        String orderId
    ) {
        return orderService.getOrderStatus(orderId);
    }
}</code></pre>
<p>그리고 해당 Tool 객체를 <code>ChatClient</code>에 제공한다.</p>
<pre><code class="language-java">String answer = chatClient.prompt()
    .user(&quot;주문번호 12345 배송 상태 알려줘.&quot;)
    .tools(orderTools)
    .call()
    .content();</code></pre>
<p>개발자가 직접</p>
<pre><code class="language-java">if (question.contains(&quot;배송&quot;)) {
    orderService.getOrderStatus(...);
}</code></pre>
<p>같은 분기문을 작성하는 구조가 아니다.</p>
<p>사용 가능한 Tool을 모델에게 알려주고,</p>
<pre><code class="language-text">Tool이 필요한가?

필요하다면 어떤 Tool인가?

어떤 Argument가 필요한가?</code></pre>
<p>를 모델이 판단하도록 한다.</p>
<p>여러 Tool이 있다면 함께 제공할 수도 있다.</p>
<pre><code class="language-java">chatClient.prompt()
    .user(question)
    .tools(
        orderTools,
        ticketTools,
        weatherTools
    )
    .call()
    .content();</code></pre>
<p>이 경우 모델은 질문에 따라 적절한 Tool을 선택한다.</p>
<pre><code class="language-text">&quot;서울 날씨 알려줘.&quot;
→ Weather Tool

&quot;주문 12345 어디야?&quot;
→ Order Tool

&quot;문의 티켓 만들어줘.&quot;
→ Ticket Tool</code></pre>
<hr />
<h2 id="tool-schema">Tool Schema</h2>
<p>모델은 <code>getOrderStatus()</code>의 Java 구현을 직접 읽지 않는다.</p>
<p>모델에게 필요한 것은 이 Tool을 <strong>어떻게 사용해야 하는지에 대한 정보</strong>다.</p>
<p>대략 다음과 같은 형태다.</p>
<pre><code class="language-text">name
→ getOrderStatus

description
→ 주문번호를 이용해 현재 주문의 배송 상태를 조회한다.

parameters
→ orderId : String</code></pre>
<p>즉 모델 입장에서는</p>
<pre><code class="language-text">어떤 기능인가?

언제 사용하는가?

어떤 값을 넣어야 하는가?</code></pre>
<p>만 알면 된다.</p>
<p>그래서 <code>description</code>은 단순한 코드 설명용 주석이 아니다.</p>
<pre><code class="language-java">@Tool(description = &quot;조회한다.&quot;)</code></pre>
<p>처럼 애매하게 작성하면 모델 입장에서도 이 Tool을 언제 사용해야 하는지 판단하기 어렵다.</p>
<p>반대로</p>
<pre><code class="language-java">@Tool(
    description =
        &quot;사용자가 주문의 현재 배송 상태나 도착 예정일을 묻는 경우 사용한다.&quot;
)</code></pre>
<p>처럼 사용 목적을 명확하게 적으면 Tool 선택의 근거가 분명해진다.</p>
<p>Tool Calling에서는 결국 <strong>Tool Schema가 모델과 Application 사이의 Interface</strong>가 된다.</p>
<hr />
<h2 id="tool의-경계">Tool의 경계</h2>
<p>여기서 Tool을 단순히</p>
<pre><code class="language-text">LLM이 Java Method를 호출하는 기능</code></pre>
<p>으로만 보면 중요한 부분을 놓치기 쉽다.</p>
<p>사용자의 요청은 자연어다.</p>
<pre><code class="language-text">&quot;내 주문 지금 어디야?&quot;</code></pre>
<p>하지만 Application은 자연어 자체를 가지고 업무 Method를 실행하지 않는다.</p>
<pre><code class="language-text">자연어 요청

&quot;내 주문 지금 어디야?&quot;

        ↓

LLM의 판단

        ↓

구조화된 Tool Call

getOrderStatus({
    &quot;orderId&quot;: &quot;12345&quot;
})

        ↓

Application</code></pre>
<p>LLM이 다루는 비정형적인 자연어가 Application 영역으로 넘어오는 순간</p>
<pre><code class="language-text">어떤 기능인가?

어떤 Parameter가 필요한가?

어떤 값을 전달할 것인가?</code></pre>
<p>가 명확해진다.</p>
<p>그래서 Tool은 <strong>LLM의 비정형적인 판단을 기존 Application의 정형화된 기능과 연결하는 경계</strong>라고 볼 수 있다.</p>
<p>기존 Application의 Service나 Repository를 버리고 AI가 새로운 업무 로직을 대신하는 것이 아니다.</p>
<pre><code class="language-text">LLM
      ↓
    Tool
      ↓
Service
      ↓
Repository / API</code></pre>
<p>기존 Application 위에 새로운 입력과 판단 계층이 하나 올라가는 것에 가깝다.</p>
<hr />
<h2 id="tool-실행">Tool 실행</h2>
<p>Tool Calling에서는 첫 번째 모델 호출에서 바로 최종 답변이 나오는 것이 아닐 수 있다.</p>
<p>사용자가</p>
<pre><code class="language-text">&quot;주문번호 12345 배송 상태 알려줘.&quot;</code></pre>
<p>라고 요청했다고 해보자.</p>
<p>첫 번째 모델 호출에서는 다음과 같은 판단이 이루어진다.</p>
<pre><code class="language-text">사용자 질문
    ↓
LLM
    ↓
getOrderStatus가 필요하다.</code></pre>
<p>그리고 모델은 Tool Call을 생성한다.</p>
<pre><code class="language-text">getOrderStatus({
    &quot;orderId&quot;: &quot;12345&quot;
})</code></pre>
<p>Application이 Tool을 실행한다.</p>
<pre><code class="language-text">getOrderStatus(&quot;12345&quot;)
    ↓
&quot;배송 중, 8월 24일 도착 예정&quot;</code></pre>
<p>이 결과를 다시 모델에게 전달한다.</p>
<pre><code class="language-text">기존 질문
+
Tool Result
    ↓
LLM
    ↓
최종 답변</code></pre>
<p>따라서 실제 흐름은 다음과 같다.</p>
<pre><code class="language-text">사용자 질문
    ↓
LLM
    ↓
Tool Call
    ↓
Tool 실행
    ↓
Tool Result
    ↓
LLM
    ↓
최종 답변</code></pre>
<p>Spring AI는 이 왕복 과정에서 Tool Call을 실제 실행 코드와 연결하고 그 결과를 다시 모델 호출에 이어주는 역할을 한다.</p>
<p>개발자가 매번</p>
<pre><code class="language-text">Tool Call 파싱
→ Argument 추출
→ Method 실행
→ 결과를 Prompt에 추가
→ 모델 재호출</code></pre>
<p>하는 코드를 직접 작성할 필요가 없다.</p>
<hr />
<h2 id="toolcallback">ToolCallback</h2>
<p>모델이 반환하는 것은 Java Method 호출이 아니라 Tool Call이다.</p>
<pre><code class="language-text">getOrderStatus({
    &quot;orderId&quot;: &quot;12345&quot;
})</code></pre>
<p>Spring AI 입장에서는 이것을 실제 실행 코드와 연결할 수 있어야 한다.</p>
<p>Tool 하나에는 크게 두 종류의 정보가 필요하다.</p>
<pre><code class="language-text">모델에게 필요한 정보

이름
설명
Input Schema


Application에게 필요한 정보

실제 실행 로직</code></pre>
<p>Spring AI에서는 Tool을 <code>ToolCallback</code>이라는 낮은 수준의 추상화로 다룰 수 있다.</p>
<pre><code class="language-text">Tool Definition
- 이름
- 설명
- Schema

        +

실행 로직

        ↓

ToolCallback</code></pre>
<p>일반적인 경우 개발자가 <code>ToolCallback</code>을 직접 만들 필요는 없다.</p>
<pre><code class="language-java">@Tool
public String getOrderStatus(String orderId) {
    ...
}</code></pre>
<p>처럼 Method를 Tool로 만들고 <code>.tools()</code>에 제공하면 Spring AI가 필요한 연결을 처리한다.</p>
<p><code>ToolCallback</code>이 중요한 이유는 Tool의 형태가 항상 로컬의 <code>@Tool</code> Method만 있는 것은 아니기 때문이다.</p>
<pre><code class="language-text">Local Method
Function
외부 MCP Tool</code></pre>
<p>처럼 출처가 달라질 수 있다.</p>
<p>Spring AI는 이런 Tool들을 공통된 형태로 다룰 수 있다.</p>
<pre><code class="language-text">개발자가 보는 Tool

@Tool Method
Function
MCP Tool

        ↓

Spring AI

ToolCallback

        ↓

ChatClient</code></pre>
<p>즉 <code>@Tool</code>과 <code>ToolCallback</code>은 서로 경쟁하는 기능이 아니다.</p>
<pre><code class="language-text">@Tool
→ Method를 Tool로 정의하기 편한 방식

ToolCallback
→ Tool을 더 낮은 수준에서 표현하고 실행하기 위한 단위</code></pre>
<p>정도로 이해하면 충분하다.</p>
<hr />
<h2 id="toolcontext">ToolContext</h2>
<p>Tool Calling을 사용하면 모델이 Tool의 Argument도 결정한다.</p>
<p>그렇다고 모든 값을 모델에게 맡겨도 되는 것은 아니다.</p>
<p>다음 Tool을 생각해보자.</p>
<pre><code class="language-java">@Tool
public Order getOrder(
        String userId,
        String orderId
) {
    ...
}</code></pre>
<p>사용자가</p>
<pre><code class="language-text">&quot;내 주문 12345 보여줘.&quot;</code></pre>
<p>라고 말했다.</p>
<p><code>orderId</code>는 질문에서 찾을 수 있다.</p>
<pre><code class="language-text">orderId = 12345</code></pre>
<p>하지만 <code>userId</code>는 다르다.</p>
<pre><code class="language-text">userId = ?</code></pre>
<p>현재 로그인한 사용자가 누구인지는 모델이 추론할 값이 아니다.</p>
<p>이미 Application의 인증 시스템이 알고 있는 값이다.</p>
<p>이런 값까지 Tool Parameter로 노출하면 모델이 Tool Call을 만들면서 해당 값까지 생성해야 한다.</p>
<pre><code class="language-text">getOrder({
    &quot;userId&quot;: ???,
    &quot;orderId&quot;: &quot;12345&quot;
})</code></pre>
<p>모델은 인증 시스템이 아니다.</p>
<p>Spring AI에서는 이런 값을 <code>ToolContext</code>를 통해 별도로 전달할 수 있다.</p>
<pre><code class="language-java">@Tool(
    description = &quot;현재 사용자의 주문 상태를 조회한다.&quot;
)
public String getOrderStatus(
        @ToolParam(description = &quot;조회할 주문번호&quot;)
        String orderId,
        ToolContext context
) {

    String userId =
        (String) context
            .getContext()
            .get(&quot;userId&quot;);

    return orderService.getOrderStatus(
        userId,
        orderId
    );
}</code></pre>
<p>모델에게 보이는 Tool Schema에는 <code>orderId</code>만 존재한다.</p>
<pre><code class="language-text">getOrderStatus({
    &quot;orderId&quot;: &quot;12345&quot;
})</code></pre>
<p><code>userId</code>는 Application이 직접 전달한다.</p>
<pre><code class="language-java">chatClient.prompt()
    .user(question)
    .tools(orderTools)
    .toolContext(
        Map.of(
            &quot;userId&quot;,
            authenticatedUserId
        )
    )
    .call()
    .content();</code></pre>
<p>Tool 실행 시점에는 두 종류의 입력이 합쳐진다.</p>
<pre><code class="language-text">                  Tool 실행
                      │
          ┌───────────┴───────────┐
          │                       │
    Tool Argument             ToolContext
          │                       │
     모델이 결정               서버가 전달
          │                       │
 orderId = 12345          userId = user1
          │                       │
          └───────────┬───────────┘
                      ↓
                 OrderService</code></pre>
<p>기준은 단순하다.</p>
<pre><code class="language-text">모델이 판단해야 하는 값
→ Tool Argument

Application이 알고 있는 신뢰 정보
→ ToolContext</code></pre>
<p>예를 들면 다음과 같다.</p>
<pre><code class="language-text">Tool Argument

orderId
검색어
도시
조회 기간


ToolContext

userId
tenantId
role
requestId
인증 정보</code></pre>
<p>Tool Schema에 포함시키지 않아도 되는 값까지 굳이 모델에게 넘길 필요가 없는 것이다.</p>
<hr />
<h2 id="실행-통제">실행 통제</h2>
<p><code>ToolContext</code>로 신뢰할 수 있는 <code>userId</code>를 전달했다고 해서 보안 처리가 끝난 것은 아니다.</p>
<p>ToolContext의 역할은</p>
<pre><code class="language-text">Application이 알고 있는 값을
Tool 실행까지 안전하게 전달</code></pre>
<p>하는 것이다.</p>
<p>실제로 사용자가 해당 주문을 조회하거나 수정할 수 있는지는 기존 업무 계층에서 다시 검증해야 한다.</p>
<p>예를 들어</p>
<pre><code class="language-java">repository.findById(orderId);</code></pre>
<p>로 주문을 찾은 뒤 소유자를 비교하기보다</p>
<pre><code class="language-java">repository.findByIdAndOwnerId(
    orderId,
    userId
);</code></pre>
<p>처럼 애초에 소유권 조건을 함께 적용할 수 있다.</p>
<p>역할을 나누면 다음과 같다.</p>
<pre><code class="language-text">LLM
→ 어떤 Tool이 필요한지 판단

Tool Argument
→ 업무에 필요한 입력 결정

ToolContext
→ Application이 알고 있는 신뢰 정보 전달

Service / Repository
→ 실제 권한과 업무 규칙 검증</code></pre>
<p>모델이 Tool을 선택했다고 해서 그 행동을 무조건 실행해야 하는 것은 아니다.</p>
<p>Application은 여전히</p>
<pre><code class="language-text">이 사용자가 실행 가능한가?

현재 상태에서 가능한 작업인가?

업무 규칙에 위배되지 않는가?</code></pre>
<p>를 판단해야 한다.</p>
<hr />
<h2 id="hitl">HITL</h2>
<p>조회 기능은 상대적으로 위험이 적다.</p>
<p>하지만 다음과 같은 Tool은 이야기가 달라진다.</p>
<pre><code class="language-text">환불

결제

삭제

메일 발송

계정 정지</code></pre>
<p>모델의 판단이 실제 시스템 변경으로 이어지기 때문이다.</p>
<p>이런 작업을</p>
<pre><code class="language-text">LLM 판단
    ↓
즉시 실행</code></pre>
<p>하도록 만들지 않을 수도 있다.</p>
<p>예를 들어 환불 Tool이 실제 환불을 수행하는 대신 승인 요청까지만 생성하도록 만들 수 있다.</p>
<pre><code class="language-java">@Tool(
    description =
        &quot;환불 요청을 생성한다. 실제 환불은 관리자 승인 후 처리된다.&quot;
)
public String requestRefund(
        String orderId,
        String reason,
        ToolContext context
) {

    String userId =
        (String) context
            .getContext()
            .get(&quot;userId&quot;);

    Approval approval =
        approvalService.create(
            orderId,
            reason,
            userId
        );

    return &quot;환불 요청이 접수되었습니다. 요청번호: &quot;
        + approval.getId();
}</code></pre>
<p>실행 구조는 다음처럼 바뀐다.</p>
<pre><code class="language-text">LLM
    ↓
환불 필요 판단
    ↓
환불 요청 Tool
    ↓
승인 요청 생성
    ↓
사람의 확인
    ↓
실제 환불</code></pre>
<p>이런 방식이 HITL(Human In The Loop)이다.</p>
<p>Tool Calling에서 중요한 것은 모델에게 많은 권한을 주는 것이 아니다.</p>
<blockquote>
<p><strong>어디까지 모델에게 판단시키고 어디부터 Application이 통제할 것인지 정하는 것</strong></p>
</blockquote>
<p>이 더 중요하다.</p>
<hr />
<h1 id="ai-agent">AI Agent</h1>
<p>지금까지의 Tool Calling은 비교적 단순했다.</p>
<pre><code class="language-text">질문
    ↓
LLM
    ↓
Tool
    ↓
결과
    ↓
LLM
    ↓
답변</code></pre>
<p>그런데 하나의 Tool 호출만으로 끝나지 않는 요청도 있다.</p>
<pre><code class="language-text">&quot;배송이 아직 시작되지 않았다면
취소 가능한지 확인해줘.&quot;</code></pre>
<p>먼저 현재 주문 상태를 알아야 한다.</p>
<pre><code class="language-text">주문 상태 조회</code></pre>
<p>배송 전이라면 취소 규정을 확인해야 한다.</p>
<pre><code class="language-text">취소 규정 검색</code></pre>
<p>그 결과를 다시 보고 최종 판단을 해야 한다.</p>
<pre><code class="language-text">사용자 요청
     ↓
LLM
     ↓
주문 조회 Tool
     ↓
&quot;결제 완료, 배송 전&quot;
     ↓
LLM 재판단
     ↓
취소 규정 검색 Tool
     ↓
&quot;배송 전에는 취소 가능&quot;
     ↓
LLM
     ↓
최종 답변</code></pre>
<p>여기서 중요한 변화가 생긴다.</p>
<pre><code class="language-text">판단
 ↓
행동
 ↓
결과 확인
 ↓
다시 판단</code></pre>
<p>Tool의 실행 결과를 바탕으로 다음 행동을 다시 선택하기 시작한다.</p>
<p>이 반복 구조가 Agent를 이해하는 핵심이다.</p>
<hr />
<h2 id="react">ReAct</h2>
<p>Agent의 대표적인 패턴 중 하나가 <code>ReAct</code>다.</p>
<p>이름 그대로</p>
<pre><code class="language-text">Reasoning
+
Acting</code></pre>
<p>의 반복이다.</p>
<pre><code class="language-text">현재 상황 판단
      ↓
필요한 행동 선택
      ↓
Tool 실행
      ↓
실행 결과 확인
      ↓
다시 판단
      ↓
다음 행동</code></pre>
<p>Agent를 단순히</p>
<pre><code class="language-text">스스로 생각하는 AI</code></pre>
<p>라고 표현하면 실제 구조가 잘 보이지 않는다.</p>
<p>Application 관점에서는</p>
<blockquote>
<p><strong>행동 결과를 새로운 Context로 받아 다음 행동을 계속 결정하는 실행 구조</strong></p>
</blockquote>
<p>라고 보는 편이 명확하다.</p>
<hr />
<h2 id="context">Context</h2>
<p>Agent가 다음 행동을 결정할 수 있는 이유는 이전 Tool의 결과가 다음 판단의 Context가 되기 때문이다.</p>
<p>첫 번째 Step에서는 다음 정보로 판단한다.</p>
<pre><code class="language-text">Step 1

사용자 요청
+
현재 Context

      ↓

LLM

      ↓

Tool A</code></pre>
<p>Tool이 실행되면 새로운 정보가 생긴다.</p>
<pre><code class="language-text">Tool A Result</code></pre>
<p>다음 Step에서는 이 결과까지 포함해서 다시 모델이 판단한다.</p>
<pre><code class="language-text">Step 2

사용자 요청
+
기존 Context
+
Tool A Result

      ↓

LLM

      ↓

Tool B 또는 종료</code></pre>
<p>다시 Tool B가 실행된다면 그 결과 역시 다음 판단의 Context가 된다.</p>
<pre><code class="language-text">Context
   ↓
판단
   ↓
Tool
   ↓
Observation
   ↓
Context 갱신
   ↓
재판단</code></pre>
<p>결국 Agent Loop는 단순히 모델을 여러 번 호출하는 것이 아니다.</p>
<p><strong>행동으로 얻은 정보를 계속 축적하면서 다음 의사결정을 이어가는 과정</strong>이다.</p>
<hr />
<h2 id="실행-제한">실행 제한</h2>
<p>반복적으로 판단하고 행동할 수 있게 되면 새로운 문제도 생긴다.</p>
<pre><code class="language-text">LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
...</code></pre>
<p>호출이 반복될수록 모델 사용 비용과 실행 시간도 증가한다.</p>
<p>모델이 항상 적절한 시점에 멈춘다고 보장할 수도 없다.</p>
<p>예를 들어 같은 검색을 반복할 수 있다.</p>
<pre><code class="language-text">search(&quot;환불 규정&quot;)
    ↓
결과 부족
    ↓
search(&quot;환불 규정&quot;)
    ↓
결과 부족
    ↓
search(&quot;환불 규정&quot;)
    ↓
...</code></pre>
<p>따라서 Agent에는 실행 범위를 제한하는 장치가 필요하다.</p>
<pre><code class="language-text">최대 Step

최대 Token

최대 실행 시간

동일 Tool + 동일 Argument 반복 제한</code></pre>
<p>Agent Loop의 상한은 단순한 성능 최적화가 아니다.</p>
<p><strong>비용과 안정성을 통제하기 위한 실행 정책</strong>이다.</p>
<p>Tool 실패도 고려해야 한다.</p>
<pre><code class="language-text">Tool 실행
   ↓
성공?
 ├─ Yes → 결과를 바탕으로 재판단
 │
 └─ No
      ↓
 실패 정보
      ↓
 LLM 재판단
      ↓
 다른 Tool / 다른 Argument / 종료</code></pre>
<p>특히 실제 상태를 변경하는 Tool은 반복 실행에 더욱 주의해야 한다.</p>
<pre><code class="language-text">환불
결제
티켓 생성
메일 발송</code></pre>
<p>같은 Tool이 실수로 두 번 실행된다면 단순한 비용 문제가 아니라 실제 데이터의 중복 변경으로 이어질 수 있다.</p>
<p>Agent에서는</p>
<pre><code class="language-text">어떤 행동을 할 수 있는가?</code></pre>
<p>뿐 아니라</p>
<pre><code class="language-text">몇 번까지 할 수 있는가?

실패하면 어떻게 할 것인가?

같은 행동을 다시 실행해도 되는가?

언제 목표가 달성되었다고 볼 것인가?</code></pre>
<p>까지 함께 설계해야 한다.</p>
<hr />
<h2 id="agentic-rag">Agentic RAG</h2>
<p>여기서 이전 글의 RAG와 다시 연결된다.</p>
<p>일반적인 RAG에서는 Retrieval이 Application Pipeline에 고정되어 있다.</p>
<pre><code class="language-text">질문
 ↓
검색
 ↓
Context
 ↓
LLM</code></pre>
<p>Application이</p>
<pre><code class="language-text">질문이 들어오면 검색한다.</code></pre>
<p>라는 흐름을 미리 정해둔 것이다.</p>
<p>모듈형 RAG라면 이 과정을 더 세분화할 수도 있다.</p>
<pre><code class="language-text">Query Rewrite
      ↓
Multi Query
      ↓
Retrieval
      ↓
Post Processing
      ↓
LLM</code></pre>
<p>그래도 전체 흐름을 결정하는 주체는 Application이다.</p>
<p>반면 Retrieval 자체를 Tool로 만들 수도 있다.</p>
<pre><code class="language-java">@Tool(
    description =
        &quot;사내 문서에서 질문과 관련된 근거를 검색한다.&quot;
)
public List&lt;Document&gt; searchDocuments(
        String query
) {

    return vectorStore.similaritySearch(
        SearchRequest.builder()
            .query(query)
            .topK(5)
            .build()
    );
}</code></pre>
<p>이제 검색 여부도 모델의 행동 선택에 포함된다.</p>
<pre><code class="language-text">사용자 질문
      ↓
     LLM
      ↓
검색이 필요한가?
 ├─ No → 바로 답변
 │
 └─ Yes
      ↓
 Search Tool
      ↓
 검색 결과
      ↓
     LLM
      ↓
근거가 충분한가?
 ├─ Yes → 답변
 │
 └─ No
      ↓
 Query 수정
      ↓
 다시 검색</code></pre>
<p>차이는 단순히 Search Method에 <code>@Tool</code>을 붙였다는 데 있지 않다.</p>
<pre><code class="language-text">Pipeline RAG

Application이
검색 시점과 흐름을 결정


Agentic RAG

Model이
검색 여부와 다음 Retrieval을 결정</code></pre>
<p>즉 Retrieval Pipeline의 일부 제어권이 Application의 고정된 흐름에서 모델의 판단으로 이동한다.</p>
<p>그만큼 장단점도 생긴다.</p>
<pre><code class="language-text">고정된 RAG Pipeline

장점
→ 실행 경로가 예측 가능
→ 테스트와 비용 관리가 쉬움

단점
→ 필요 없는 검색도 수행할 수 있음
→ 상황에 따른 경로 변경이 어려움


Agentic RAG

장점
→ 필요한 경우에만 검색 가능
→ 검색 결과를 보고 재검색 가능
→ 다른 Tool과 조합 가능

단점
→ 실행 경로가 유동적
→ 모델 호출 수와 비용 증가
→ 종료와 실패 정책이 중요</code></pre>
<p>Agentic RAG는 단순히 더 고급인 RAG라기보다,</p>
<p><strong>Retrieval 과정의 일부 판단을 Agent에게 맡기는 설계 선택</strong>에 가깝다.</p>
<hr />
<h1 id="mcp">MCP</h1>
<p>Tool을 한 Application 내부에서만 사용한다면 <code>@Tool</code>로도 많은 기능을 만들 수 있다.</p>
<p>그런데 같은 기능을 여러 AI Application에서 사용하기 시작하면 문제가 생긴다.</p>
<pre><code class="language-text">사내 Chatbot
 ├─ File 연동
 ├─ Database 연동
 └─ Ticket 연동

IDE Agent
 ├─ File 연동
 ├─ Database 연동
 └─ Ticket 연동

운영 Assistant
 ├─ Database 연동
 └─ Ticket 연동</code></pre>
<p>각 Application마다 외부 시스템 연동을 다시 구현한다면 Tool을 재사용하기 어렵다.</p>
<p>여기서 MCP가 등장한다.</p>
<p><strong>MCP(Model Context Protocol)</strong>는 AI Application과 외부 Tool이나 Resource가 통신하는 방식을 표준화한다.</p>
<pre><code class="language-text">AI Application
      ↓
MCP Client
      ↓
표준 Protocol
      ↓
MCP Server
      ↓
Tool / Resource</code></pre>
<p>MCP가 새로운 주문 조회나 파일 읽기 기능을 만드는 것은 아니다.</p>
<p>이미 존재하는 기능을</p>
<pre><code class="language-text">AI Application이 어떻게 발견하고

어떤 형식으로 호출하고

어떤 형식으로 결과를 받을 것인가</code></pre>
<p>에 대한 연결 규칙을 맞추는 것이다.</p>
<hr />
<h2 id="consumer와-provider">Consumer와 Provider</h2>
<p>MCP가 가져오는 중요한 변화는 Tool 구현과 AI Application을 분리할 수 있다는 점이다.</p>
<p>기존 구조에서는 AI Application 안에서 각각의 외부 시스템을 직접 연결할 수 있다.</p>
<pre><code class="language-text">Chatbot

├─ Jira API 연동
├─ Database 연동
└─ File System 연동</code></pre>
<p>다른 Agent가 같은 기능을 사용하려면 다시 연결해야 한다.</p>
<pre><code class="language-text">IDE Agent

├─ Jira API 연동
├─ Database 연동
└─ File System 연동</code></pre>
<p>MCP를 사용하면 외부 기능을 별도의 Server가 제공할 수 있다.</p>
<pre><code class="language-text">             Jira MCP Server
            /
Chatbot ─── MCP
            \
             DB MCP Server


IDE Agent ─ MCP</code></pre>
<p>AI Application은 Tool의 내부 구현을 직접 가지고 있을 필요가 없다.</p>
<pre><code class="language-text">AI Application
→ Tool Consumer

MCP Server
→ Tool Provider</code></pre>
<p>가 분리된다.</p>
<p>Tool 구현을 특정 AI Application에 종속시키지 않고 여러 Client가 사용할 수 있는 외부 Capability로 만들 수 있는 것이다.</p>
<hr />
<h2 id="mcp-client">MCP Client</h2>
<p>Spring AI Application이 외부 MCP Server의 Tool을 사용한다고 해보자.</p>
<pre><code class="language-text">Spring AI Application
        ↓
     MCP Client
        ↓
     MCP Server
        ↓
File / DB / Internal API</code></pre>
<p>이 경우 우리 Application 코드에 다음 Method가 존재하지 않을 수도 있다.</p>
<pre><code class="language-java">@Tool
String searchDocument(...) {
    ...
}</code></pre>
<p>Tool 구현은 MCP Server에 존재하기 때문이다.</p>
<p>Application은 MCP Server와 연결한 뒤 해당 Server가 제공하는 Tool들을 받아온다.</p>
<pre><code class="language-text">MCP Server 연결
      ↓
Tool 발견
      ↓
ToolCallback들
      ↓
ToolCallbackProvider
      ↓
ChatClient</code></pre>
<p>Spring AI에서는 MCP Tool들을 <code>ToolCallbackProvider</code> 형태로 <code>ChatClient</code>에 공급할 수 있다.</p>
<pre><code class="language-java">@Bean
ChatClient mcpChatClient(
        ChatClient.Builder builder,
        SyncMcpToolCallbackProvider mcpTools
) {

    return builder
        .defaultToolCallbacks(mcpTools)
        .build();
}</code></pre>
<p>앞에서 살펴본 <code>ToolCallback</code>이 여기서 다시 의미를 가진다.</p>
<pre><code class="language-text">Local @Tool
      │
      ▼
 ToolCallback ───────┐
                     │
                     ├─→ ChatClient
                     │
MCP Tool             │
      │              │
      ▼              │
 ToolCallback ───────┘</code></pre>
<p>Tool이 어디서 왔든 <code>ChatClient</code>가 사용할 수 있는 공통 형태로 연결할 수 있다.</p>
<hr />
<h2 id="mcp-server">MCP Server</h2>
<p>반대 방향도 가능하다.</p>
<p>우리 Application이 가지고 있는 Tool을 다른 AI Application에게 제공할 수 있다.</p>
<p>예를 들어 다음 Tool들이 있다고 해보자.</p>
<pre><code class="language-text">TicketTools
 ├─ @Tool createTicket()
 └─ @Tool findTicket()

KbTools
 └─ @Tool searchKnowledge()</code></pre>
<p><code>MethodToolCallbackProvider</code>를 통해 이 Tool들을 하나의 공급원으로 구성할 수 있다.</p>
<pre><code class="language-java">@Bean
ToolCallbackProvider helpdeskTools(
        TicketTools ticketTools,
        KbTools kbTools
) {

    return MethodToolCallbackProvider.builder()
        .toolObjects(
            ticketTools,
            kbTools
        )
        .build();
}</code></pre>
<p>구조적으로 보면 다음과 같다.</p>
<pre><code class="language-text">@Tool Method들
      ↓
ToolCallback들
      ↓
ToolCallbackProvider
      ↓
MCP Server
      ↓
외부 AI Application</code></pre>
<p><code>ToolCallbackProvider</code>를 사용하는 이유는 단순히 Tool이 여러 개라서가 아니다.</p>
<p>여러 Tool은 <code>.tools()</code>에도 직접 넘길 수 있다.</p>
<pre><code class="language-java">chatClient.prompt()
    .tools(
        orderTools,
        ticketTools
    );</code></pre>
<p>Provider의 역할은 <strong>Tool 집합 자체를 하나의 공급 단위로 만드는 것</strong>에 가깝다.</p>
<pre><code class="language-text">.tools(...)
→ 현재 ChatClient 호출에 Tool들을 직접 제공


ToolCallbackProvider
→ ToolCallback 집합 자체를 하나의 공급원으로 관리</code></pre>
<p>MCP Server에서는</p>
<pre><code class="language-text">이 Server가 어떤 Tool들을 외부에 제공하는가?</code></pre>
<p>라는 Tool 집합이 필요하므로 Provider 구조가 자연스럽게 연결된다.</p>
<p>정리하면 다음과 같다.</p>
<pre><code class="language-text">ToolCallback
→ 하나의 Tool을 다루는 공통 실행 단위

ToolCallbackProvider
→ ToolCallback 집합을 공급

MCP
→ 그 Tool을 Application 밖과 표준 방식으로 연결</code></pre>
<hr />
<h1 id="advisor">Advisor</h1>
<p>지금까지는 주로</p>
<pre><code class="language-text">모델이 어떤 기능을 사용할 수 있는가?</code></pre>
<p>를 살펴봤다.</p>
<p>그런데 실제 AI Application에서는 모델 호출 전후에도 반복되는 작업들이 많다.</p>
<p>예를 들면 다음과 같다.</p>
<pre><code class="language-text">대화 Memory 조회

RAG 검색

입력 안전 검사

Prompt 보강

Logging

Token 측정

응답 후처리</code></pre>
<p>이런 코드를 모든 Service Method에서 직접 처리한다면 AI 관련 공통 로직이 여기저기 흩어지게 된다.</p>
<pre><code class="language-java">checkSafety();

loadMemory();

retrieveDocuments();

chatClient.prompt(...);

saveMemory();

recordUsage();</code></pre>
<p>Spring AI에서는 이런 공통 처리를 <code>Advisor</code>로 분리할 수 있다.</p>
<p>Tool이</p>
<pre><code class="language-text">모델이 무엇을 할 수 있는가</code></pre>
<p>를 확장한다면,</p>
<p>Advisor는</p>
<pre><code class="language-text">모델 호출이 어떤 과정을 거치는가</code></pre>
<p>를 구성하는 쪽에 가깝다.</p>
<pre><code class="language-text">                 ChatClient
                     │
               Advisor Chain
                     │
                     ▼
                    LLM
                     │
              Tool이 필요한가?
                     │
                     ▼
                 Tool Call</code></pre>
<p>Tool과 Advisor는 서로 역할이 다르다.</p>
<pre><code class="language-text">Tool
→ 모델이 선택할 수 있는 행동

Advisor
→ 모델 호출 앞뒤에 적용되는 공통 처리</code></pre>
<hr />
<h2 id="advisor-chain">Advisor Chain</h2>
<p>Advisor는 <code>ChatClient</code> 요청과 응답 흐름을 감싼다.</p>
<pre><code class="language-text">Request
   ↓
Advisor A
   ↓
Advisor B
   ↓
Advisor C
   ↓
ChatModel
   ↓
Advisor C
   ↓
Advisor B
   ↓
Advisor A
   ↓
Response</code></pre>
<p>Spring AOP를 이해하고 있다면 발상 자체는 익숙하다.</p>
<pre><code class="language-text">Spring AOP
→ Business Method 실행 전후에 공통 관심사 적용

Spring AI Advisor
→ AI 요청·응답 흐름 전후에 공통 관심사 적용</code></pre>
<p>두 기능의 구현 구조가 같다는 의미는 아니다.</p>
<p>핵심 기능에서 Logging, Memory, Safety 같은 공통 관심사를 분리한다는 설계 관점이 비슷하다는 뜻이다.</p>
<hr />
<h2 id="before와-after">before와 after</h2>
<p>직접 Advisor를 만들 수도 있다.</p>
<pre><code class="language-java">@Component
public class TermGlossaryAdvisor
        implements BaseAdvisor {

    @Override
    public ChatClientRequest before(
            ChatClientRequest request,
            AdvisorChain chain
    ) {

        String glossary =
            glossaryService.forQuestion(
                request.prompt().getContents()
            );

        if (glossary.isBlank()) {
            return request;
        }

        Prompt augmented =
            request.prompt()
                .augmentSystemMessage(
                    system -&gt;
                        system
                        + &quot;\n\n[사내 용어]\n&quot;
                        + glossary
                );

        return request.mutate()
            .prompt(augmented)
            .build();
    }

    @Override
    public ChatClientResponse after(
            ChatClientResponse response,
            AdvisorChain chain
    ) {
        return response;
    }

    @Override
    public String getName() {
        return &quot;termGlossary&quot;;
    }

    @Override
    public int getOrder() {
        return 250;
    }
}</code></pre>
<p><code>before()</code>는 모델 호출 전에 실행된다.</p>
<p>위 예제에서는 기존 System Message에 사내 용어 정보를 추가한다.</p>
<pre><code class="language-text">기존 Prompt
     ↓
TermGlossaryAdvisor
     ↓
사내 용어 추가
     ↓
변경된 Prompt
     ↓
Model</code></pre>
<p><code>after()</code>는 모델 응답 이후의 처리를 담당할 수 있다.</p>
<p>즉 Framework가</p>
<pre><code class="language-text">이 Advisor는 전처리인가?

후처리인가?</code></pre>
<p>를 추측하는 것이 아니다.</p>
<p>Advisor가 요청과 응답의 처리 지점을 각각 정의한다.</p>
<hr />
<h2 id="실행-순서">실행 순서</h2>
<p>Advisor가 하나라면 순서가 크게 문제되지 않는다.</p>
<p>하지만 실제 Application에서는 여러 Advisor가 함께 붙을 수 있다.</p>
<pre><code class="language-text">Safety

Chat Memory

RAG

Logging</code></pre>
<p>이때는 <strong>어떤 Advisor가 먼저 실행되는가</strong>가 실제 동작을 바꾼다.</p>
<p>예를 들어 위험한 입력을 Memory에 저장하기 전에 차단하고 싶다고 해보자.</p>
<pre><code class="language-text">Safety
   ↓
Memory</code></pre>
<p>순서라면 위험한 요청을 먼저 걸러낼 수 있다.</p>
<p>반대로</p>
<pre><code class="language-text">Memory
   ↓
Safety</code></pre>
<p>라면 이후 요청을 차단하더라도 이미 Memory에 기록된 뒤일 수 있다.</p>
<p>Spring AI에서는 <code>order</code> 값으로 Advisor의 순서를 정할 수 있다.</p>
<pre><code class="language-text">Audit       order 0
Safety      order 100
Memory      order 200
RAG         order 300
Logger      order 400</code></pre>
<p>요청은 낮은 <code>order</code>부터 들어간다.</p>
<pre><code class="language-text">Request
   ↓
Audit
   ↓
Safety
   ↓
Memory
   ↓
RAG
   ↓
Logger
   ↓
Model</code></pre>
<p>응답은 반대 방향으로 빠져나온다.</p>
<pre><code class="language-text">Model
   ↓
Logger
   ↓
RAG
   ↓
Memory
   ↓
Safety
   ↓
Audit
   ↓
Response</code></pre>
<p>따라서 Advisor의 <code>order</code>는 단순한 실행 순번이 아니다.</p>
<p><strong>AI 요청 Pipeline이 어떤 의미를 가지는지를 결정하는 정책</strong>이다.</p>
<hr />
<h2 id="rag와-memory">RAG와 Memory</h2>
<p>Advisor가 흥미로운 이유는 이전에 따로 배웠던 기능들도 이 Pipeline 안에서 다시 볼 수 있기 때문이다.</p>
<p>예를 들어 RAG의 기본 흐름은 다음과 같다.</p>
<pre><code class="language-text">사용자 질문
    ↓
VectorStore 검색
    ↓
관련 Document
    ↓
Prompt에 Context 추가
    ↓
Model</code></pre>
<p>결국 모델 호출 전에</p>
<pre><code class="language-text">검색하고

검색 결과를 Prompt에 넣는다.</code></pre>
<p>는 요청 처리가 추가되는 구조다.</p>
<p>Spring AI에서는 이런 RAG 처리를 <code>QuestionAnswerAdvisor</code>나 <code>RetrievalAugmentationAdvisor</code> 같은 Advisor를 통해 <code>ChatClient</code>에 조립할 수 있다.</p>
<p>Chat Memory 역시 비슷하다.</p>
<pre><code class="language-text">현재 질문
    ↓
이전 대화 조회
    ↓
Context에 대화 이력 추가
    ↓
Model</code></pre>
<p>그래서 하나의 <code>ChatClient</code>에 여러 공통 처리를 조립할 수 있다.</p>
<pre><code class="language-java">@Bean
ChatClient supportClient(
        ChatClient.Builder builder,
        ChatMemory memory,
        VectorStore vectorStore
) {

    return builder
        .defaultAdvisors(
            MessageChatMemoryAdvisor
                .builder(memory)
                .build(),

            QuestionAnswerAdvisor
                .builder(vectorStore)
                .build()
        )
        .build();
}</code></pre>
<p>구조적으로 보면 다음과 같다.</p>
<pre><code class="language-text">사용자 질문
      ↓
Memory Advisor
      ↓
대화 Context 추가
      ↓
RAG Advisor
      ↓
문서 Context 추가
      ↓
LLM</code></pre>
<p>여기서 순서를 바꾸면 모델에게 전달되는 Context를 구성하는 방식 역시 달라질 수 있다.</p>
<p>결국 Advisor는 단순히 Logging을 붙이는 부가기능 정도가 아니다.</p>
<blockquote>
<p><strong>ChatClient 요청이 모델에 도달하기 전 어떤 Context와 정책을 거칠 것인지를 조립하는 Pipeline</strong></p>
</blockquote>
<p>으로 볼 수 있다.</p>
<hr />
<h1 id="하나의-ai-application">하나의 AI Application</h1>
<p>여기까지 오면 처음의 단순한 LLM 호출과는 구조가 상당히 달라진다.</p>
<p>처음에는 이 정도였다.</p>
<pre><code class="language-text">User
 ↓
LLM
 ↓
Response</code></pre>
<p>RAG를 붙이면 외부 지식이 들어온다.</p>
<pre><code class="language-text">User
 ↓
Retrieval
 ↓
LLM
 ↓
Response</code></pre>
<p>Tool을 붙이면 실제 Application 기능을 사용할 수 있다.</p>
<pre><code class="language-text">User
 ↓
LLM
 ↓
Tool
 ↓
Application
 ↓
LLM
 ↓
Response</code></pre>
<p>Agent가 되면 행동 결과를 바탕으로 다음 행동을 다시 결정한다.</p>
<pre><code class="language-text">User
 ↓
LLM
 ↓
Tool
 ↓
Result
 ↓
LLM
 ↓
Tool
 ↓
...
 ↓
Response</code></pre>
<p>MCP를 붙이면 Tool의 구현 위치도 Application 밖으로 확장된다.</p>
<p>그리고 Advisor는 이 전체 모델 호출 Pipeline 앞뒤에 공통 정책을 적용한다.</p>
<p>Spring Application의 구조로 한 번에 보면 다음과 같다.</p>
<pre><code class="language-text">                         User
                          │
                          ▼
                      Controller
                          │
                          ▼
                       Service
                          │
                          ▼
                      ChatClient
                          │
                   Advisor Chain
              ┌───────────┼───────────┐
              │           │           │
           Safety       Memory       RAG
              │           │           │
              └───────────┼───────────┘
                          │
                          ▼
                         LLM
                          │
                   Tool이 필요한가?
                          │
              ┌───────────┼───────────┐
              │           │           │
          Local Tool   Search Tool   MCP Tool
              │           │           │
              └───────────┼───────────┘
                          │
                          ▼
                     Tool Result
                          │
                          ▼
                     LLM 재판단
                          │
                   필요하면 반복
                          │
                          ▼
                     최종 Response</code></pre>
<p>각 요소의 역할도 명확하게 나눌 수 있다.</p>
<pre><code class="language-text">RAG
→ 외부 지식을 가져온다.

Tool
→ Application의 기능을 모델에게 제공한다.

ToolContext
→ 모델이 판단하지 않아야 할 값을 Tool에 전달한다.

Agent
→ 행동 결과를 보고 다음 행동을 다시 결정한다.

MCP
→ Tool과 Resource를 Application 밖과 표준 방식으로 연결한다.

Advisor
→ AI 요청과 응답에 공통 Context와 정책을 적용한다.</code></pre>
<p>Spring AI의 역할은 이 모든 판단을 대신해주는 것이 아니다.</p>
<p>대신 각각 따로 구현하면 복잡해질 AI Application의 요소들을</p>
<pre><code class="language-text">ChatClient

Advisor

RAG

Tool

MCP</code></pre>
<p>같은 추상화를 통해 Spring Application 안에서 조립할 수 있도록 해준다.</p>
<hr />
<h1 id="마무리">마무리</h1>
<p>LLM Application을 처음 접하면 가장 중요한 것은 모델 자체처럼 보인다.</p>
<pre><code class="language-text">어떤 모델을 사용할까?

Prompt를 어떻게 작성할까?</code></pre>
<p>물론 중요하다.</p>
<p>하지만 실제 서비스로 갈수록 다른 질문들이 함께 등장한다.</p>
<pre><code class="language-text">모델에게 어떤 지식을 제공할 것인가?

어떤 기능까지 사용할 수 있게 할 것인가?

어떤 값은 모델에게 맡기지 않을 것인가?

실제 행동의 허용 여부는 어디서 검증할 것인가?

여러 행동이 필요하면 어떻게 반복할 것인가?

그 반복은 언제 멈출 것인가?

외부 Tool은 어떤 방식으로 연결할 것인가?

모든 AI 요청에 적용되는 정책은 어디에 둘 것인가?</code></pre>
<p>이 질문들을 하나씩 해결하면서</p>
<pre><code class="language-text">RAG
Tool
Agent
MCP
Advisor</code></pre>
<p>같은 구조가 등장한다.</p>
<p>이를 가장 크게 보면 다음처럼 정리할 수 있다.</p>
<pre><code class="language-text">RAG
→ Knowledge

Tool
→ Action

Agent
→ Decision Loop

MCP
→ Connection

Advisor
→ Pipeline</code></pre>
<p>결국 AI Service를 만든다는 것은 모델에게 모든 것을 맡기는 것이 아니다.</p>
<p><strong>모델이 잘하는 판단과 Application이 책임져야 할 실행·통제·정책을 나누고, 그 사이를 적절한 추상화로 연결하는 것.</strong></p>
<p>RAG 이후의 AI Application을 이해할 때 중요한 지점은 여기에 있다.</p>