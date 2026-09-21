<p>기본 RAG의 검색 과정은 보통 개발자가 미리 정한 순서를 따라간다.</p>
<pre><code class="language-text">질문
  ↓
검색
  ↓
Context 구성
  ↓
답변</code></pre>
<p>구조는 단순하지만 모든 질문을 한 번의 검색으로 해결할 수 있는 것은 아니다.</p>
<p>검색 결과가 질문과 관계없을 수 있고, 내부 문서에 답이 없을 수도 있다. 질문이 최신 데이터나 외부 시스템을 확인해야 하는 경우도 있다.</p>
<p>이때 검색 결과를 확인한 뒤 다음 행동을 선택하는 구조가 필요하다.</p>
<p>이번 글에서는 Self-RAG, Corrective RAG, Agentic RAG를 중심으로 RAG가 고정된 Pipeline에서 조건부 흐름으로 확장되는 과정을 살펴본다.</p>
<h2 id="한-번의-검색으로-충분하지-않다면">한 번의 검색으로 충분하지 않다면</h2>
<p>기본적인 RAG는 다음처럼 표현할 수 있다.</p>
<pre><code class="language-pseudo">def answer(question):
    documents = retrieve(question)
    return generate(question, documents)</code></pre>
<p>검색 결과가 비어도 답변을 생성한다.</p>
<p>검색 결과가 질문과 관련이 없어도 답변을 생성한다. 오래된 문서와 최신 문서가 섞여도 모델이 알아서 판단하기를 기대한다.</p>
<p>분기가 적을 때는 다음처럼 처리할 수 있다.</p>
<pre><code class="language-pseudo">if documents is empty:
    search_again()

if documents_are_irrelevant(documents):
    rewrite_question()

if answer_is_not_grounded(answer):
    generate_again()</code></pre>
<p>하지만 분기가 늘어나면 실행 흐름을 파악하기 어려워진다.</p>
<p>어떤 조건에서 재검색했는지, 몇 번 반복했는지, 왜 답변을 보류했는지를 확인하려면 상태와 전이를 명시적으로 관리해야 한다.</p>
<h2 id="state와-조건부-흐름">State와 조건부 흐름</h2>
<p>조건부 RAG는 State와 Node와 Edge로 표현할 수 있다.</p>
<h3 id="state">State</h3>
<p>State는 실행 중 전달되는 값이다.</p>
<pre><code class="language-text">RagState
├─ originalQuestion
├─ currentQuestion
├─ conversationHistory
├─ documents
├─ answer
├─ documentsRelevant
├─ answerGrounded
├─ rewriteCount
├─ searchCount
└─ terminationReason</code></pre>
<p>원래 질문과 재작성된 질문을 분리해야 한다.</p>
<p>모델이 어떤 검색어를 만들었는지 확인할 수 있어야 하기 때문이다.</p>
<h3 id="node">Node</h3>
<p>Node는 하나의 작업 단위다.</p>
<pre><code class="language-text">retrieve
gradeDocuments
rewriteQuery
webSearch
generate
verifyAnswer
fallback</code></pre>
<h3 id="edge">Edge</h3>
<p>Edge는 Node 사이의 이동이다.</p>
<pre><code class="language-text">retrieve
    ↓
gradeDocuments
    ├─ 관련 있음 → generate
    └─ 관련 없음 → rewriteQuery
                         ↓
                      retrieve</code></pre>
<p>이동 조건이 명확하면 RAG의 실행 흐름을 로그와 그림으로 설명할 수 있다.</p>
<h2 id="self-rag">Self-RAG</h2>
<p>Self-RAG는 RAG 과정의 필요성과 결과를 스스로 확인하는 방식이다.</p>
<p>대표적으로 다음 질문을 확인한다.</p>
<pre><code class="language-text">이 질문에 검색이 필요한가?

검색 결과가 질문과 관련 있는가?

생성한 답변이 검색된 근거에 연결되어 있는가?</code></pre>
<p>전체 흐름은 다음과 같다.</p>
<pre><code class="language-text">질문
  ↓
검색 필요성 판단
  ├─ 불필요 → 일반 응답
  └─ 필요 → 검색
              ↓
          근거 충분성 판단
              ├─ 충분 → 생성
              └─ 부족 → 재검색 또는 보류
                         ↓
                    답변 근거성 확인
                         ├─ 통과 → 응답
                    └─ 실패 → 수정 또는 보류</code></pre>
<h3 id="self-rag가-확인하는-것">Self-RAG가 확인하는 것</h3>
<p>Self-RAG의 핵심은 답변을 생성한 뒤 한 번 더 생각한다는 의미가 아니다.</p>
<p>RAG 실행 중에 다음 판단을 명시적으로 포함하는 데 있다.</p>
<pre><code class="language-text">검색이 필요한가?
검색 결과가 질문과 관련 있는가?
답변의 주장이 근거에 연결되는가?</code></pre>
<p>이 판단은 서로 다른 실패를 다룬다. 검색이 필요하지 않은 질문에 검색을 수행하는 것은 비용 문제이고, 검색 결과가 질문과 관계없는 것은 Retrieval 문제이며, 근거가 있는데 답변이 벗어나는 것은 Generation 문제다.</p>
<p>모든 질문에 검색을 적용하면 비용과 지연 시간이 늘어난다.</p>
<p>반대로 내부 정책이나 최신 상태에 관한 질문인데 검색을 생략하면 위험하다. 검색 필요성은 질문의 길이보다 최신성, 권한, 사실 확인의 필요성으로 판단하는 편이 좋다.</p>
<p>처음에는 규칙 기반으로 시작할 수 있다.</p>
<pre><code class="language-pseudo">def needs_retrieval(question):
    if contains_internal_policy_term(question):
        return true

    if contains_current_time_expression(question):
        return true

    if asks_for_user_specific_state(question):
        return true

    return false</code></pre>
<h2 id="corrective-rag">Corrective RAG</h2>
<p>Corrective RAG는 검색 결과가 부족하거나 틀렸을 때 검색 과정을 수정하는 방식이다.</p>
<pre><code class="language-text">검색
  ↓
검색 결과 평가
  ├─ Correct → 생성
  └─ 부족 또는 Incorrect
       ├─ 질문 재작성
       ├─ 다른 검색기 사용
       ├─ 검색 범위 변경
       ├─ 다른 데이터 소스 확인
       └─ 답변 보류</code></pre>
<p>여기서 Correct는 문서가 하나라도 존재한다는 뜻이 아니다.</p>
<p>질문에 답하는 데 필요한 근거가 있다는 뜻이다. 문서가 다섯 개 검색되어도 모두 질문과 관계없다면 Correct가 아니다.</p>
<h3 id="관련성-확인">관련성 확인</h3>
<p>관련성은 검색 Score만으로 판단할 수도 있고, Metadata와 규칙과 별도 평가 모델을 함께 사용할 수도 있다.</p>
<pre><code class="language-pseudo">def grade_documents(question, documents):
    if documents is empty:
        return &quot;NO_DOCUMENT&quot;

    if has_high_similarity_document(documents):
        return &quot;RELEVANT&quot;

    if metadata_matches(question, documents):
        return &quot;RELEVANT&quot;

    return &quot;IRRELEVANT&quot;</code></pre>
<p>평가 모델을 사용한다면 자유로운 문장보다 구조화된 결과를 받는 것이 좋다.</p>
<pre><code class="language-json">{
  &quot;label&quot;: &quot;IRRELEVANT&quot;,
  &quot;documentIds&quot;: [],
  &quot;reason&quot;: &quot;문서가 휴가 신청 경로만 설명하고 승인 기준은 설명하지 않는다.&quot;
}</code></pre>
<h3 id="query-rewrite">Query Rewrite</h3>
<p>관련 문서가 없다면 검색용 질문을 다시 만들 수 있다.</p>
<pre><code class="language-pseudo">def rewrite_query(state):
    if state.rewrite_count &gt;= 2:
        return state

    rewritten = query_model.generate(
        original_question = state.original_question,
        current_question = state.current_question,
        history = state.conversation_history
    )

    return state.update(
        current_question = rewritten,
        rewrite_count = state.rewrite_count + 1
    )</code></pre>
<p>재작성할 때 원래 질문에 없는 정보를 추가하면 안 된다.</p>
<p>날짜와 버전과 고유명사와 숫자와 사용자가 지정한 조건은 보존해야 한다.</p>
<h2 id="adaptive-rag">Adaptive RAG</h2>
<p>질문과 상황에 따라 검색 전략을 선택하는 방식도 있다.</p>
<pre><code class="language-text">질문 분류
  ├─ 단순 사실 질문 → 한 번 검색
  ├─ 모호한 질문 → Query Rewrite
  ├─ 비교 질문 → Query Decomposition
  ├─ 키워드 중심 질문 → Keyword 또는 Hybrid
  ├─ 최신 상태 질문 → 최신 문서 또는 도구
  └─ 검색 불필요 → 일반 응답</code></pre>
<p>Adaptive RAG는 모든 질문에 같은 비용을 쓰지 않는다는 점에서 의미가 있다.</p>
<p>다만 Router가 틀리면 처음부터 잘못된 경로로 들어간다. 어떤 질문이 어떤 경로로 분류되었는지와 그 결과를 함께 평가해야 한다.</p>
<h3 id="router는-정책의-일부다">Router는 정책의 일부다</h3>
<p>Adaptive RAG에서 Router는 단순한 편의 기능이 아니다.</p>
<p>어떤 질문을 한 번 검색할지, 여러 번 검색할지, 외부 데이터 소스를 사용할지 결정하기 때문이다.</p>
<pre><code class="language-text">Router 판단
    ↓
실행 경로
    ↓
검색 비용과 지연 시간
    ↓
답변 가능 범위</code></pre>
<p>Router가 최신성 질문을 일반 문서 검색으로 보내면 오래된 문서가 답변에 사용될 수 있다. 반대로 모든 질문을 Agentic 경로로 보내면 불필요한 검색과 모델 호출이 늘어난다.</p>
<p>따라서 Router의 분류 결과도 Golden Set에서 평가하고, 중요한 질문에는 허용 가능한 경로를 제한하는 편이 좋다.</p>
<h2 id="agentic-rag">Agentic RAG</h2>
<p>Agentic RAG는 현재 State를 보고 다음 행동을 선택하는 RAG다.</p>
<p>여기서 Agent라는 표현을 무제한 자율성으로 이해하면 안 된다.</p>
<p>운영 가능한 Agentic RAG에는 다음과 같은 제한이 필요하다.</p>
<pre><code class="language-text">사용할 수 있는 도구의 목록

도구별 입력 검증

최대 검색 횟수

최대 Query Rewrite 횟수

최대 실행 시간

최대 토큰 수

답변 보류 조건</code></pre>
<p>전체 흐름은 다음과 같이 표현할 수 있다.</p>
<pre><code class="language-text">질문
  ↓
라우팅 또는 계획
  ↓
검색
  ↓
검색 결과 평가
  ├─ 충분 → 답변
  ├─ 부족 → Query Rewrite
  ├─ 최신 데이터 필요 → 도구 호출
  └─ 권한 또는 정책 위반 → 중단</code></pre>
<p>자주 발생하는 분기는 명시적인 조건으로 만들고, 예외적인 경우에만 모델 판단을 사용하는 편이 예측 가능하다.</p>
<h3 id="agent에게-허용할-판단의-범위">Agent에게 허용할 판단의 범위</h3>
<p>Agentic RAG에서 모델이 결정할 수 있는 것과 서버가 결정해야 하는 것을 구분해야 한다.</p>
<pre><code class="language-text">모델이 판단할 수 있는 것
→ 질문을 다시 쓸 필요가 있는가
→ 어떤 검색 전략이 적합한가
→ 현재 후보가 질문과 관련 있는가

서버가 결정해야 하는 것
→ 사용자가 볼 수 있는 문서 범위
→ 호출할 수 있는 도구와 인자
→ 최대 실행 시간과 횟수
→ 답변을 외부에 반환할 수 있는가</code></pre>
<p>모델에게 권한과 종료 조건까지 맡기면 Agentic RAG가 검색 시스템을 넘어 권한 우회 경로가 될 수 있다.</p>
<h3 id="web-search와-다른-데이터-소스">Web Search와 다른 데이터 소스</h3>
<p>내부 문서에 답이 없을 때 외부 검색으로 넘어갈 수 있다.</p>
<p>하지만 외부 검색을 항상 허용하면 안 된다.</p>
<pre><code class="language-text">내부 문서 검색 실패
  ↓
외부 검색 정책 확인
  ├─ 금지 → 답변 보류
  └─ 허용 → 외부 검색
                    ↓
                출처와 조회 시각 기록
                    ↓
                  답변 생성</code></pre>
<p>질문의 성격에 따라 적합한 검색 경로도 달라진다.</p>
<pre><code class="language-text">사내 인사 규정
→ 내부 문서

공개 라이브러리 최신 버전
→ 공식 문서와 외부 검색

내 티켓 상태
→ 업무 도구

다른 사용자의 개인정보
→ 권한 확인 또는 거부</code></pre>
<p>내부 정책과 외부 자료가 충돌할 때 어떤 출처를 우선할지도 미리 정해야 한다.</p>
<h3 id="답변-검증">답변 검증</h3>
<p>검색 결과의 관련성이 높아도 생성된 답변이 근거를 벗어날 수 있다.</p>
<pre><code class="language-text">답변 생성
  ↓
답변 검증
  ├─ 근거 있음 → 응답
  ├─ 수정 가능 → 재생성
  └─ 근거 없음 → Fallback</code></pre>
<p>검증할 내용은 다음과 같다.</p>
<ul>
<li>핵심 주장이 검색 문서에 있는가</li>
<li>숫자와 날짜가 문서에 있는가</li>
<li>문서에 없는 조건을 추가하지 않았는가</li>
<li>출처가 실제 문서와 일치하는가</li>
<li>권한 밖의 내용을 포함하지 않았는가</li>
</ul>
<p>재생성 횟수에는 제한을 둬야 한다.</p>
<pre><code class="language-pseudo">if state.verification_count &gt;= 1:
    return fallback(&quot;답변 근거를 확인할 수 없습니다.&quot;)</code></pre>
<p>검증 실패를 숨기고 계속 재생성하면 비용만 늘고 결과는 좋아지지 않을 수 있다.</p>
<h3 id="종료-조건">종료 조건</h3>
<p>Agentic RAG에서는 시작 조건보다 종료 조건이 더 중요하다.</p>
<pre><code class="language-text">최대 반복 횟수
→ 무한 루프 방지

최대 검색 횟수
→ 검색 비용 제한

최대 Rewrite 횟수
→ 무의미한 재검색 방지

최대 도구 호출 횟수
→ 도구 폭주 방지

최대 실행 시간
→ 사용자 지연 제한

최소 관련성 기준
→ 관계없는 답변 방지</code></pre>
<p>실행이 끝난 이유도 기록해야 한다.</p>
<pre><code class="language-text">ANSWERED
NO_EVIDENCE
PERMISSION_DENIED
MAX_REWRITE_EXCEEDED
MAX_TOOL_CALL_EXCEEDED
TIMEOUT
VERIFICATION_FAILED</code></pre>
<p>데이터가 없는 것과 권한이 없는 것과 시스템이 시간 초과된 것은 서로 다른 실패다.</p>
<p>종료 이유를 구분해야 다음 개선 작업도 달라진다.</p>
<p>반복 횟수를 늘리는 것만으로 실패를 해결할 수는 없다. 같은 질문과 같은 문서로 재검색을 반복하면 비용만 증가한다. 재검색을 수행하려면 질문 표현이나 검색기나 데이터 소스 중 적어도 하나가 실제로 달라져야 한다.</p>
<h3 id="관찰-가능성">관찰 가능성</h3>
<p>조건부 RAG는 중간 상태를 기록하지 않으면 디버깅하기 어렵다.</p>
<pre><code class="language-json">{
  &quot;traceId&quot;: &quot;trace-123&quot;,
  &quot;originalQuestion&quot;: &quot;작년에 말한 휴가 기준이 지금도 같아?&quot;,
  &quot;currentQuestion&quot;: &quot;현재 휴가 승인 기준과 변경 이력&quot;,
  &quot;selectedNodes&quot;: [
    &quot;retrieve&quot;,
    &quot;gradeDocuments&quot;,
    &quot;rewriteQuery&quot;,
    &quot;retrieve&quot;,
    &quot;generate&quot;,
    &quot;verifyAnswer&quot;
  ],
  &quot;rewriteCount&quot;: 1,
  &quot;retrievalCount&quot;: 2,
  &quot;terminationReason&quot;: &quot;ANSWERED&quot;
}</code></pre>
<p>문서 원문 전체를 로그로 남기기보다 문서 ID와 제목과 Score와 짧은 미리보기를 저장하는 편이 안전하다.</p>
<h2 id="마무리">마무리</h2>
<p>Self-RAG는 검색 필요성과 근거 충분성과 답변 근거성을 확인한다.</p>
<p>Corrective RAG는 검색 결과가 부족할 때 질문을 다시 쓰거나 다른 검색 경로를 선택한다. Adaptive RAG는 질문의 성격에 따라 필요한 검색 전략을 선택한다.</p>
<p>Agentic RAG는 이러한 분기를 State와 조건부 흐름으로 연결한 구조다.</p>
<p>네 가지 개념은 서로 같은 수준의 기능 이름이 아니다.</p>
<pre><code class="language-text">Self-RAG
→ 검색 필요성과 답변 근거성을 스스로 점검하는 방식

Corrective RAG
→ 검색 결과가 부족할 때 검색 과정을 수정하는 방식

Adaptive RAG
→ 질문의 성격에 따라 경로와 비용을 선택하는 방식

Agentic RAG
→ 여러 판단과 도구 호출을 State와 실행 흐름으로 연결하는 구조</code></pre>
<p>Self-RAG와 Corrective RAG는 Agentic RAG 안에서도 구현할 수 있다. 반대로 검색 필요성 판단이 있다고 해서 곧바로 Agentic RAG가 되는 것은 아니다. 이 관계를 구분하지 않으면 이름만 달라지고 실제 책임은 같은 Pipeline이 반복된다.</p>
<p>중요한 것은 LLM에게 무제한의 권한을 주는 것이 아니다.</p>
<p>어떤 판단을 허용하고, 어떤 도구를 사용할 수 있고, 언제 반드시 멈춰야 하는지를 시스템 안에 명확하게 넣는 것이다.</p>
<p>검색 품질이 좋지 않은 상태에서 Agentic 분기부터 추가하면 나쁜 검색 결과를 더 많은 단계로 처리하게 될 뿐이다.</p>
<p>먼저 Chunking과 Metadata와 Retrieval과 Evaluation을 확인한 뒤, 실제 실패 지점에만 조건부 흐름을 추가하는 것이 좋다.</p>
<p>다음 글에서는 지금까지의 RAG를 실제 서비스에서 운영하기 위해 필요한 아키텍처를 살펴보자.</p>