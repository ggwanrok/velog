<p>LLM은 학습된 지식을 바탕으로 답변을 생성하지만 모든 정보를 알고 있는 것은 아니다.</p>
<p>학습 이후 생성된 정보, 기업 내부 문서, 개인이 보유한 데이터와 같이 모델의 학습 범위 밖에 있는 정보에는 직접 접근할 수 없다.</p>
<p>이러한 한계를 보완하기 위한 대표적인 방법이 RAG(Retrieval-Augmented Generation)다.</p>
<p>RAG는 모델 자체를 다시 학습시키는 대신, 사용자의 질문과 관련된 외부 정보를 검색한 뒤 이를 질문과 함께 LLM에 전달한다.</p>
<pre><code class="language-text">사용자 질문
    ↓
관련 문서 검색
    ↓
질문 + 검색된 근거
    ↓
LLM
    ↓
근거 기반 답변</code></pre>
<p>즉 RAG의 핵심은 모델에게 새로운 지식을 기억시키는 것이 아니라, 답변 시점에 필요한 지식을 찾아 Context로 제공하는 것이다.</p>
<h2 id="rag의-기본-구조">RAG의 기본 구조</h2>
<p>RAG는 크게 문서를 준비하는 Ingest 과정과 실제 질문을 처리하는 Retrieval·Generation 과정으로 나눌 수 있다.</p>
<pre><code class="language-text">                 [Ingest]

원본 문서
   ↓
문서 읽기
   ↓
Chunking
   ↓
Metadata
   ↓
Embedding
   ↓
Vector Store


              [Retrieval]

사용자 질문
   ↓
질문 임베딩
   ↓
문서 검색
   ↓
관련 Chunk


             [Generation]

질문 + 관련 Chunk
   ↓
LLM
   ↓
답변</code></pre>
<p>문서를 저장하는 과정과 질문을 처리하는 과정은 실행 시점이 다르다.</p>
<p>문서는 새로운 파일이 추가되거나 내용이 변경될 때 처리하면 된다. 반면 질문은 사용자가 요청할 때마다 검색하고 답변해야 한다.</p>
<p>이 둘을 분리하면 매 질문마다 모든 문서를 다시 처리하지 않아도 된다.</p>
<h3 id="ingest와-query는-서로-다른-문제다">Ingest와 Query는 서로 다른 문제다</h3>
<p>Ingest의 목표는 원본 문서를 검색 가능한 형태로 안정적으로 저장하는 것이다.</p>
<p>Query의 목표는 현재 질문에 필요한 근거를 제한된 시간 안에 찾아 답변으로 연결하는 것이다.</p>
<p>두 과정은 같은 문서를 사용하지만 실패하는 이유가 다르다.</p>
<pre><code class="language-text">Ingest 실패
→ 문서가 읽히지 않음
→ Chunk 경계가 잘못됨
→ Metadata가 사라짐
→ Embedding과 원문이 서로 다른 버전임

Query 실패
→ 질문과 검색 표현이 맞지 않음
→ 필요한 문서가 상위 결과에 없음
→ 권한 필터가 잘못 적용됨
→ 검색된 근거가 답변 Context에서 사라짐</code></pre>
<p>문서가 잘못 저장된 문제를 Query Rewrite로 해결할 수는 없다. 반대로 질문이 모호한 문제를 Chunk Size만 바꾸어서 해결할 수도 없다.</p>
<p>RAG를 개선할 때 먼저 어느 실행 시점에서 문제가 발생했는지를 나누어야 하는 이유다.</p>
<h2 id="문서를-준비하는-ingest-과정">문서를 준비하는 Ingest 과정</h2>
<p>먼저 PDF, Markdown, HTML, 데이터베이스와 같은 원본을 읽는다.</p>
<p>문서의 형식은 달라도 RAG 내부에서는 다음과 같은 구조로 다룰 수 있다.</p>
<pre><code class="language-text">Document
├─ content
└─ metadata</code></pre>
<p>문서의 내용만 저장하면 나중에 출처와 버전과 권한을 관리하기 어렵다.</p>
<p>따라서 다음과 같은 Metadata를 함께 저장한다.</p>
<pre><code class="language-json">{
  &quot;source&quot;: &quot;hr/leave-policy.pdf&quot;,
  &quot;title&quot;: &quot;휴가 정책&quot;,
  &quot;version&quot;: &quot;2025-03&quot;,
  &quot;documentType&quot;: &quot;POLICY&quot;,
  &quot;department&quot;: &quot;HR&quot;,
  &quot;tenantId&quot;: &quot;company-a&quot;
}</code></pre>
<h3 id="원본-문서와-검색-레코드의-계약">원본 문서와 검색 레코드의 계약</h3>
<p>Vector Store에 저장되는 값은 Vector 하나가 아니다.</p>
<p>검색 결과가 답변의 근거로 사용되려면 원본 문서의 위치와 버전과 권한까지 다시 추적할 수 있어야 한다.</p>
<pre><code class="language-json">{
  &quot;id&quot;: &quot;leave-policy:2025-03:section-2:chunk-3&quot;,
  &quot;documentId&quot;: &quot;leave-policy&quot;,
  &quot;content&quot;: &quot;연차 휴가는 팀 리더의 승인을 받아야 한다.&quot;,
  &quot;embedding&quot;: [0.12, -0.31, 0.88],
  &quot;metadata&quot;: {
    &quot;version&quot;: &quot;2025-03&quot;,
    &quot;sectionPath&quot;: [&quot;휴가 정책&quot;, &quot;승인 기준&quot;],
    &quot;status&quot;: &quot;ACTIVE&quot;,
    &quot;tenantId&quot;: &quot;company-a&quot;
  }
}</code></pre>
<p><code>content</code>는 모델이 읽을 근거이고, <code>metadata</code>는 그 근거를 해석하고 통제하기 위한 값이다.</p>
<p>Embedding을 다시 계산할 수는 있지만, 어떤 원문에서 만들어졌는지 알 수 없는 Vector는 답변의 출처로 사용하기 어렵다. 검색 레코드에는 원문과 Metadata를 함께 보존해야 한다.</p>
<p>이후 긴 문서를 검색에 적합한 크기의 Chunk로 나눈다.</p>
<p>문서 전체를 하나의 Vector로 만들면 문서 안에 포함된 여러 주제가 하나의 의미로 섞일 수 있다. 반대로 너무 작게 나누면 질문에 필요한 문맥이 사라진다.</p>
<p>따라서 Chunking은 단순히 글자 수를 자르는 작업이 아니라, 검색 단위를 설계하는 과정으로 보는 것이 좋다.</p>
<p>각 Chunk는 Embedding Model을 통해 Vector로 변환된다.</p>
<pre><code class="language-text">&quot;휴가 신청 방법&quot;

        ↓

[0.12, -0.31, 0.88, ...]</code></pre>
<p>Vector는 텍스트의 의미를 숫자로 표현한 값이다.</p>
<p>질문도 같은 Embedding Model을 사용해 Vector로 변환한다. 같은 공간에 놓인 질문 Vector와 문서 Vector의 거리를 비교하면 의미적으로 가까운 문서를 찾을 수 있다.</p>
<p>마지막으로 Vector와 원문과 Metadata를 Vector Store에 저장한다.</p>
<pre><code class="language-text">Chunk
  ↓
Embedding
  ↓
Vector + Content + Metadata
  ↓
Vector Store</code></pre>
<h2 id="질문을-처리하는-retrieval-과정">질문을 처리하는 Retrieval 과정</h2>
<p>사용자의 질문이 들어오면 질문을 먼저 Vector로 변환한다.</p>
<pre><code class="language-text">질문
&quot;퇴사할 때 회사 노트북을 어떻게 돌려줘?&quot;

        ↓

질문 Vector

        ↓

Vector Search

        ↓

관련 Chunk
&quot;퇴직자는 지급받은 업무용 장비를 반환해야 한다.&quot;</code></pre>
<p>문자열이 완전히 일치하지 않더라도 의미가 비슷한 문서를 검색할 수 있다는 것이 Vector Search의 핵심이다.</p>
<p>검색 결과에는 보통 문서 내용과 함께 검색 점수와 Metadata가 포함된다.</p>
<pre><code class="language-json">{
  &quot;content&quot;: &quot;퇴직자는 지급받은 업무용 장비를 반환해야 한다.&quot;,
  &quot;score&quot;: 0.84,
  &quot;metadata&quot;: {
    &quot;source&quot;: &quot;asset-policy.pdf&quot;,
    &quot;version&quot;: &quot;2025-03&quot;
  }
}</code></pre>
<p>여기서 score는 답변의 정답 점수가 아니다.</p>
<p>질문 Vector와 문서 Vector가 얼마나 가까운지를 나타내는 값이다. 따라서 score가 높다고 해서 해당 문서가 반드시 질문에 답할 수 있는 것은 아니다.</p>
<h3 id="score는-근거의-충분성을-의미하지-않는다">Score는 근거의 충분성을 의미하지 않는다</h3>
<p>다음 두 문서는 질문과 높은 의미적 유사도를 가질 수 있다.</p>
<pre><code class="language-text">질문: 휴가 승인자는 누구인가?

문서 A: 휴가 신청은 사내 포털에서 진행한다.
문서 B: 휴가 신청은 팀 리더의 승인을 받아야 한다.</code></pre>
<p>문서 A는 휴가라는 주제를 공유하지만 질문의 조건에 답하지 않는다. Vector Search는 주제의 유사성을 계산할 수 있지만, 문서가 질문의 주장을 실제로 뒷받침하는지까지 보장하지 않는다.</p>
<p>따라서 검색 결과는 정답이 아니라 후보 근거다.</p>
<pre><code class="language-text">Score
→ 후보를 정렬하는 신호

관련성 판단
→ 질문에 필요한 내용을 포함하는지 확인

근거성 판단
→ 최종 답변의 주장을 뒷받침하는지 확인</code></pre>
<p>이 세 값을 하나로 취급하면 Score가 높은 문서를 답변에 무조건 포함하게 된다.</p>
<p>검색 결과는 보통 Top-K 방식으로 가져온다.</p>
<pre><code class="language-text">전체 문서
    ↓
질문과 가까운 문서 검색
    ↓
Top-K Chunk</code></pre>
<p>필요하다면 Metadata Filter를 함께 사용할 수 있다.</p>
<pre><code class="language-text">전체 Vector Store
    ↓
department = HR
version = 2025-03
    ↓
Vector Search</code></pre>
<p>특정 부서나 테넌트의 문서만 검색해야 하는 경우 Metadata Filter는 검색 최적화가 아니라 접근 범위를 제어하는 장치가 된다.</p>
<h2 id="검색된-근거를-generation에-전달하기">검색된 근거를 Generation에 전달하기</h2>
<p>검색된 Chunk는 질문과 함께 LLM에 전달된다.</p>
<pre><code class="language-text">[Context]

퇴직자는 지급받은 업무용 장비를
퇴직일까지 반환해야 한다.

[Question]

퇴사할 때 노트북은 언제까지 반납해야 하나요?</code></pre>
<p>이때 생성 모델이 검색된 Context 밖의 내용을 추측하지 않도록 지시해야 한다.</p>
<pre><code class="language-text">제공된 Context를 근거로 답변한다.
Context에 없는 내용은 추측하지 않는다.
답변을 확인할 수 없다면 확인할 수 없다고 말한다.</code></pre>
<p>검색 결과가 없다면 일반적인 답변을 생성하지 않는 것이 좋다.</p>
<pre><code class="language-text">관련 문서를 찾지 못했습니다.
제공된 문서에서는 답변을 확인할 수 없습니다.</code></pre>
<p>문서가 없는데도 LLM을 호출하면 모델의 일반 지식이나 추측이 답변에 섞일 수 있다.</p>
<p>따라서 RAG의 답변 결과에는 답변 내용뿐 아니라 상태와 출처도 함께 포함하는 것이 좋다.</p>
<pre><code class="language-json">{
  &quot;answer&quot;: &quot;퇴직일까지 회사에서 지급받은 노트북을 반환해야 합니다.&quot;,
  &quot;status&quot;: &quot;ANSWERED&quot;,
  &quot;sources&quot;: [
    {
      &quot;source&quot;: &quot;asset-policy.pdf&quot;,
      &quot;version&quot;: &quot;2025-03&quot;
    }
  ]
}</code></pre>
<p>출처는 LLM이 생성한 문장을 그대로 사용하는 것이 아니라, 실제 검색 결과의 Metadata에서 만드는 것이 안전하다.</p>
<h3 id="generation의-입력과-출력-계약">Generation의 입력과 출력 계약</h3>
<p>Generation은 질문과 검색된 문서를 받아 답변을 만든다. 이때 검색된 문서가 있다는 사실만 전달하면 부족하다.</p>
<p>답변에 사용할 수 있는 문서의 범위와 답변할 수 없는 경우와 출처를 반환하는 규칙도 함께 정의해야 한다.</p>
<pre><code class="language-text">Generation 입력
├─ originalQuestion
├─ filteredDocuments
├─ documentMetadata
└─ answerPolicy

Generation 출력
├─ answer
├─ status
├─ sources
└─ unsupportedClaims 또는 verificationResult</code></pre>
<p>답변 문자열만 반환하면 다음 질문에 답하기 어렵다.</p>
<pre><code class="language-text">답변에 사용한 문서는 무엇인가?
근거가 부족해서 답변을 보류한 것인가?
검색 장애 때문에 답변하지 못한 것인가?</code></pre>
<p>RAG의 출력은 문장 하나가 아니라 답변과 상태와 근거를 함께 가진 결과로 보는 편이 안전하다.</p>
<h2 id="rag를-직접-구성해-보면">RAG를 직접 구성해 보면</h2>
<h3 id="ingest">Ingest</h3>
<p>프레임워크와 관계없는 형태로 Ingest 과정을 표현하면 다음과 같다.</p>
<pre><code class="language-pseudo">def ingest(source):
    documents = loader.load(source)

    for document in documents:
        chunks = splitter.split(document.content)

        for index, chunk in enumerate(chunks):
            record = {
                &quot;id&quot;: make_id(document, index),
                &quot;content&quot;: chunk,
                &quot;embedding&quot;: embed(chunk),
                &quot;metadata&quot;: document.metadata
            }

            vector_store.upsert(record)</code></pre>
<h3 id="질문-처리">질문 처리</h3>
<p>질문 처리 과정은 다음과 같다.</p>
<pre><code class="language-pseudo">def answer(question, user_context):
    filters = build_permission_filter(user_context)
    query_vector = embed(question)

    documents = vector_store.search(
        query_vector,
        top_k = 5,
        filters = filters
    )

    if documents is empty:
        return no_evidence_answer()

    context = build_context(documents)
    answer = generator.generate(
        question = question,
        context = context
    )

    return {
        &quot;answer&quot;: answer,
        &quot;sources&quot;: extract_sources(documents)
    }</code></pre>
<h3 id="단계-사이의-계약">단계 사이의 계약</h3>
<p>RAG를 직접 구성한다는 것은 모든 기능을 하나의 함수에 넣는다는 뜻이 아니다.</p>
<p>각 단계가 어떤 값을 받고 어떤 값을 반환하는지 정하는 것이 먼저다.</p>
<pre><code class="language-text">Ingest
→ Chunk + Embedding + Metadata

Retrieval
→ Evidence 후보 + Score + Metadata

Generation
→ Answer + Status + Sources</code></pre>
<p>이 계약이 있으면 Vector Store를 바꾸거나 검색 전략을 추가해도 Generation의 책임은 달라지지 않는다. 반대로 계약이 없으면 검색 결과와 답변 생성이 하나의 코드에 섞이고, 어느 단계에서 실패했는지 확인하기 어려워진다.</p>
<p>이 흐름을 보면 RAG는 결국 다음 두 기능의 결합이라고 볼 수 있다.</p>
<pre><code class="language-text">Retrieval
→ 답변에 필요한 근거를 찾는다.

Generation
→ 찾은 근거를 바탕으로 답변한다.</code></pre>
<h2 id="기본형-rag가-가지는-한계">기본형 RAG가 가지는 한계</h2>
<p>기본 RAG의 구조 자체는 단순하다.</p>
<p>문서를 검색 가능한 형태로 저장한다.
    ↓
질문과 관련된 문서를 찾는다.
    ↓
검색된 근거와 질문을 LLM에 전달한다.
    ↓
답변을 생성한다.</p>
<p>하지만 실제 서비스에서는 이 과정 곳곳에서 검색 실패가 발생할 수 있다.</p>
<p>문서가 검색하기 좋은 형태가 아닐 수 있다.</p>
<p>질문이 검색하기 좋은 형태가 아닐 수 있다.</p>
<p>Vector Search가 정확한 코드나 숫자를 놓칠 수 있다.</p>
<p>검색 결과가 같은 문서를 반복해서 반환할 수 있다.</p>
<p>정답 문서를 찾았지만 오래된 버전일 수 있다.</p>
<p>검색된 문서가 있어도 LLM이 문서에 없는 내용을 추가할 수 있다.</p>
<p>RAG 고도화는 이러한 문제를 한꺼번에 해결하는 과정이 아니다.</p>
<p>어떤 단계에서 실패했는지 확인하고, 해당 단계만 개선하는 과정에 가깝다.</p>
<h2 id="마무리">마무리</h2>
<p>RAG는 단순한 Vector Search나 LLM 호출이 아니다.</p>
<p>문서를 읽고, 검색 가능한 단위로 나누고, 의미를 Vector로 표현하고, 질문과 가까운 근거를 찾은 뒤, 그 근거를 바탕으로 답변을 생성하는 전체 Pipeline이다.</p>
<p>좋은 RAG는 많은 정보를 LLM에게 전달하는 시스템이 아니다.</p>
<p>사용자의 질문에 필요한 정보를 정확하게 찾아 필요한 만큼 전달하는 시스템이다.</p>
<p>다음 글에서는 이 과정에서 가장 먼저 품질을 좌우하는 Chunking과 Metadata를 살펴보자.</p>