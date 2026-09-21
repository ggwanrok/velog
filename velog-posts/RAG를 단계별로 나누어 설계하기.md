<p>기본형 RAG의 흐름은 단순하다.</p>
<pre><code class="language-text">질문
  ↓
검색
  ↓
Context 구성
  ↓
LLM</code></pre>
<p>처음에는 이 구조만으로도 충분하다.</p>
<p>하지만 검색 결과가 부족해지면서 기능이 하나씩 추가된다.</p>
<pre><code class="language-text">질문을 다시 작성한다.

여러 검색어로 검색한다.

Keyword Search와 Vector Search를 결합한다.

검색 결과를 다시 정렬한다.

중복 문서를 제거한다.

문서가 없으면 다른 데이터 소스를 확인한다.

답변 전에 근거를 검증한다.</code></pre>
<p>이 기능들을 하나의 함수 안에 계속 추가하면 RAG의 실행 흐름을 파악하기 어려워진다.</p>
<p>따라서 RAG를 하나의 고정된 검색 과정으로 보기보다, 각각 조정할 수 있는 여러 단계의 Pipeline으로 바라볼 필요가 있다.</p>
<h2 id="기본형-rag의-한계">기본형 RAG의 한계</h2>
<p>초기 구현은 보통 다음과 같다.</p>
<pre><code class="language-pseudo">def answer(question):
    documents = vector_store.search(embed(question))
    prompt = make_prompt(question, documents)
    return llm.generate(prompt)</code></pre>
<p>여기에 기능을 추가하면 다음과 같이 된다.</p>
<pre><code class="language-pseudo">def answer(question):
    question = rewrite(question)
    documents = vector_search(question)
    documents += keyword_search(question)
    documents = remove_duplicates(documents)
    documents = rerank(question, documents)
    context = compress(documents)
    return generate(question, context)</code></pre>
<p>작동은 하지만 각 기능의 입력과 출력이 명확하지 않다.</p>
<p>검색 결과가 나빠졌을 때 Query Rewrite 때문인지, 검색 결과 결합 때문인지, Re-ranking 때문인지 찾기 어렵다.</p>
<h2 id="rag를-단계별로-나누기">RAG를 단계별로 나누기</h2>
<p>RAG를 다음과 같이 구분할 수 있다.</p>
<pre><code class="language-text">Ingest
   ↓
Pre-Retrieval
   ↓
Retrieval
   ↓
Post-Retrieval
   ↓
Generation</code></pre>
<p>각 단계가 담당하는 문제는 서로 다르다.</p>
<pre><code class="language-text">Ingest
→ 어떤 형태의 문서를 검색 대상으로 만들 것인가

Pre-Retrieval
→ 사용자의 질문을 어떤 형태로 검색할 것인가

Retrieval
→ 어떤 방식으로 관련 문서를 찾을 것인가

Post-Retrieval
→ 검색된 후보 중 어떤 근거를 사용할 것인가

Generation
→ 선택된 근거를 이용해 어떻게 답변할 것인가</code></pre>
<p>이처럼 RAG를 여러 모듈로 분리하면 검색 품질이 낮을 때 전체 구조를 한꺼번에 변경할 필요가 없다.</p>
<p>문서 자체의 구조가 문제라면 Ingest를 조정할 수 있다. 질문이 검색에 적합하지 않다면 Pre-Retrieval을 조정할 수 있다. 검색 방식의 한계라면 Retrieval을, 후보의 품질이 낮다면 Post-Retrieval을 개선할 수 있다.</p>
<h3 id="단계는-실행-순서가-아니라-책임으로-나눈다">단계는 실행 순서가 아니라 책임으로 나눈다</h3>
<p>모듈을 나눈다는 것은 함수를 잘게 쪼개는 것만을 의미하지 않는다.</p>
<p>각 단계가 어떤 결정을 내리고, 다음 단계에 어떤 값을 넘기는지를 분리하는 것이다.</p>
<pre><code class="language-text">Ingest
→ 검색할 수 있는 문서를 만든다.

Pre-Retrieval
→ 질문의 의미와 조건을 보존한 채 검색 표현을 만든다.

Retrieval
→ 후보 근거를 넓게 찾는다.

Post-Retrieval
→ 최종 Context에 사용할 근거를 선별한다.

Generation
→ 선택된 근거의 범위 안에서 답변을 만든다.</code></pre>
<p>이 책임이 섞이면 검색 모듈이 답변 형식까지 결정하거나, Generation이 권한 필터를 임의로 판단하는 문제가 생긴다.</p>
<h3 id="ingest">Ingest</h3>
<p>Ingest는 원본 문서를 검색 가능한 형태로 만드는 단계다.</p>
<pre><code class="language-text">원본 문서
   ↓
문서 읽기
   ↓
Parsing
   ↓
Chunking
   ↓
Metadata
   ↓
Embedding
   ↓
Index</code></pre>
<p>이 단계에서 다루는 문제는 다음과 같다.</p>
<ul>
<li>PDF의 문서 구조를 어떻게 복원할 것인가</li>
<li>문서를 어떤 크기의 Chunk로 나눌 것인가</li>
<li>제목과 경로를 어떻게 보존할 것인가</li>
<li>문서 버전과 권한을 어떻게 저장할 것인가</li>
<li>같은 문서를 다시 넣었을 때 중복을 어떻게 막을 것인가</li>
</ul>
<p>문서가 검색하기 좋은 형태가 아니라면 이후 단계에서 검색 전략을 아무리 바꾸어도 한계가 있다.</p>
<p>Ingest의 출력은 단순한 문자열 목록이 아니다.</p>
<pre><code class="language-text">Chunk
├─ id
├─ content
├─ embedding
└─ metadata</code></pre>
<p>다음 단계에서 문서의 버전과 권한과 원문 위치를 확인할 수 있어야 한다. 이 계약이 없으면 Retrieval 이후에 출처와 권한을 복원하기 어렵다.</p>
<h3 id="pre-retrieval">Pre-Retrieval</h3>
<p>Pre-Retrieval은 검색 전에 질문을 처리하는 단계다.</p>
<p>사용자의 질문은 항상 검색 시스템이 이해하기 좋은 형태로 작성되지 않는다.</p>
<pre><code class="language-text">사용자: 휴가 신청은 어떻게 해?
사용자: 그러면 승인은?</code></pre>
<p>두 번째 질문만 검색하면 무엇의 승인인지 알기 어렵다.</p>
<p>이전 대화의 문맥을 사용해 Query를 복원할 수 있다.</p>
<pre><code class="language-text">사용자 질문
    ↓
Query Rewrite
    ↓
검색 가능한 Query
    ↓
검색</code></pre>
<p>하나의 질문을 여러 검색 표현으로 확장하는 Multi-Query도 Pre-Retrieval에 해당한다.</p>
<pre><code class="language-text">회사 노트북 반납 규정
        ↓
퇴사 시 노트북 반환 절차
회사 자산 반납 기한
업무 장비 반환 정책</code></pre>
<p>여러 Query의 결과를 합친 뒤 중복 제거와 Re-ranking을 적용할 수 있다.</p>
<p>질문이 복잡하다면 하위 질문으로 나누는 Query Decomposition을 사용할 수도 있다.</p>
<pre><code class="language-text">2024년과 2025년 정책의 차이와
현재 적용 기준은?

        ↓

2024년 정책 검색
2025년 정책 검색
정책 차이 비교
현재 적용 버전 확인</code></pre>
<p>질문을 바꾸는 단계에서는 검색 성능보다 의미 보존이 먼저다.</p>
<p>고유명사와 숫자와 날짜와 버전과 사용자가 지정한 비교 조건이 사라지면 검색 결과가 좋아 보이더라도 다른 질문에 답하게 된다. Rewrite 결과와 원래 질문을 함께 저장해야 이 변화를 확인할 수 있다.</p>
<h3 id="retrieval">Retrieval</h3>
<p>Retrieval은 질문에 맞는 후보 문서를 찾는 단계다.</p>
<p>질문의 성격에 따라 검색 경로가 달라질 수 있다.</p>
<pre><code class="language-text">정확한 제품 코드
→ Keyword Search

표현이 다양한 질문
→ Vector Search

두 특성이 모두 필요함
→ Hybrid Search

특정 부서와 버전만 필요함
→ Metadata Filter</code></pre>
<p>Retriever를 하나만 두지 않고 질문의 특성에 따라 선택할 수도 있다.</p>
<pre><code class="language-pseudo">def select_retriever(query):
    if contains_exact_identifier(query):
        return keyword_retriever

    if asks_for_policy(query):
        return hybrid_retriever

    return vector_retriever</code></pre>
<p>처음에는 규칙 기반 Router로 시작할 수 있다.</p>
<p>나중에 질문 분류 모델을 추가하더라도 어떤 경로가 선택되었는지를 기록해야 한다.</p>
<p>Retrieval의 출력은 최종 답변이 아니라 후보 목록이다.</p>
<pre><code class="language-text">Candidate
├─ documentId
├─ content
├─ score
├─ searchStrategy
└─ metadata</code></pre>
<p>후보를 찾았다는 이유로 모두 Context에 넣어서는 안 된다. 후보를 넓게 확보하는 Retrieval과 최종 근거를 선택하는 Post-Retrieval을 분리해야 각 단계의 품질을 평가할 수 있다.</p>
<h3 id="post-retrieval">Post-Retrieval</h3>
<p>Retrieval에서 가져온 후보가 모두 최종 Context에 들어가야 하는 것은 아니다.</p>
<p>검색 결과가 같은 문서에 치우치거나, 질문과 관계없는 문서가 포함될 수 있기 때문이다.</p>
<p>Post-Retrieval에서는 다음 작업을 수행할 수 있다.</p>
<pre><code class="language-text">후보 문서
    ↓
중복 제거
    ↓
MMR
    ↓
Re-ranking
    ↓
Parent 또는 인접 Chunk 확장
    ↓
Context Compression
    ↓
최종 근거</code></pre>
<p>빠른 검색으로 후보를 넓게 가져오고, 후처리에서 최종 Context를 좁히는 구조다.</p>
<pre><code class="language-text">Vector Search
    ↓
Top 20
    ↓
Re-ranking
    ↓
Top 5
    ↓
LLM</code></pre>
<p>Context Compression을 사용하면 문서 전체가 아니라 질문과 관련된 문장만 남길 수 있다.</p>
<p>다만 압축 과정에서 조건과 예외가 사라질 수 있으므로, 답변 품질과 함께 평가해야 한다.</p>
<p>Post-Retrieval에는 Context 예산이 있다.</p>
<pre><code class="language-text">후보를 많이 가져오기
→ Recall 확보

최종 문서 수와 토큰 수 제한
→ 비용과 지연 시간 제한

조건과 예외 보존
→ 근거성 유지</code></pre>
<p>가장 관련성이 높은 문장만 남기는 압축이 항상 좋은 것은 아니다. 정책 문서에서는 짧은 결론보다 그 결론의 적용 조건과 예외가 더 중요할 수 있다.</p>
<h3 id="generation">Generation</h3>
<p>Generation은 최종 근거를 이용해 답변을 만드는 단계다.</p>
<pre><code class="language-pseudo">def generate(question, documents):
    if documents is empty:
        return no_evidence_answer()

    context = build_context(documents)

    answer = model.generate(
        question = question,
        context = context,
        instruction = grounded_instruction
    )

    return {
        &quot;answer&quot;: answer,
        &quot;sources&quot;: extract_sources(documents)
    }</code></pre>
<p>Generation 모듈은 어떤 검색기를 사용했는지 알 필요가 없다.</p>
<p>검색 결과가 문서 목록이라는 계약만 지키면 Dense Search든 Hybrid Search든 같은 Generation 모듈에 연결할 수 있다.</p>
<p>이 분리가 있어야 검색기를 교체해도 Prompt와 답변 형식을 다시 작성하지 않는다.</p>
<p>Generation은 다음과 같은 계약을 받을 수 있다.</p>
<pre><code class="language-text">입력
→ 질문
→ 최종 근거
→ 답변 정책

출력
→ 답변
→ 상태
→ 출처
→ 검증 결과</code></pre>
<p>검색기가 어떤 방식으로 후보를 만들었는지는 Generation의 책임이 아니다. 반대로 Generation이 근거에 없는 내용을 추가했다면 Retrieval의 성공 여부와 별도로 Generation을 평가해야 한다.</p>
<h2 id="공통-실행-상태">공통 실행 상태</h2>
<p>여러 모듈을 연결할수록 실행 상태를 명확하게 관리해야 한다.</p>
<pre><code class="language-pseudo">RagState {
    originalQuestion
    currentQuestion
    queryVariants
    selectedStrategy
    candidates
    finalDocuments
    answer
    sources
    rewriteCount
    trace
}</code></pre>
<p>원본 질문과 재작성된 질문을 분리하면 검색 품질을 비교하기 쉽다.</p>
<p>어떤 모듈이 문서를 추가하고 제거했는지도 Trace에 남겨야 최종 답변을 설명할 수 있다.</p>
<p>State에는 현재 값뿐 아니라 변경 이력도 필요하다.</p>
<pre><code class="language-text">originalQuestion
→ 사용자가 입력한 원문

currentQuestion
→ 검색에 사용한 표현

candidates
→ 각 검색기가 반환한 후보

finalDocuments
→ 최종 Context에 선택된 근거</code></pre>
<p><code>documents</code> 하나만 계속 덮어쓰면 어떤 문서가 검색에서 탈락했는지와 어떤 모듈이 최종 근거를 선택했는지를 알 수 없다. 상태를 분리하면 모듈의 효과와 실패 지점을 비교할 수 있다.</p>
<pre><code class="language-json">{
  &quot;originalQuestion&quot;: &quot;그럼 승인은?&quot;,
  &quot;currentQuestion&quot;: &quot;휴가 승인 기준은?&quot;,
  &quot;strategy&quot;: &quot;hybrid&quot;,
  &quot;candidateCount&quot;: 18,
  &quot;finalDocumentCount&quot;: 5,
  &quot;rerankerUsed&quot;: true
}</code></pre>
<h2 id="필요한-모듈만-조합하기">필요한 모듈만 조합하기</h2>
<p>모든 질문에 모든 모듈을 실행할 필요는 없다.</p>
<pre><code class="language-text">단순한 질문
→ 한 번의 Vector Search

정확한 코드 질문
→ Keyword Search

검색 결과가 부족함
→ Query Rewrite

결과가 중복됨
→ MMR

후보의 순위가 아쉬움
→ Re-ranking

여러 조건을 비교함
→ Query Decomposition</code></pre>
<p>모듈을 많이 추가한다고 RAG가 자동으로 좋아지는 것은 아니다.</p>
<p>각 모듈에는 비용과 위험이 있다.</p>
<pre><code class="language-text">Query Rewrite
→ 검색에 적합한 질문으로 보정
→ 고유명사와 조건이 바뀔 수 있음

Multi-Query
→ Recall 증가
→ 검색 횟수 증가

Re-ranking
→ 후보 순위 개선
→ 추가 지연과 비용

Context Compression
→ Context 축소
→ 중요한 조건이 누락될 수 있음</code></pre>
<p>실패 사례가 실제로 발생하는 단계에만 모듈을 추가하는 것이 좋다.</p>
<h2 id="modular-rag를-평가하기">Modular RAG를 평가하기</h2>
<p>모듈형 구조에서는 최종 답변만 평가하면 부족하다.</p>
<p>각 단계의 결과를 함께 기록해야 한다.</p>
<pre><code class="language-text">질문 처리 결과
검색 전략
검색된 후보 수
최종 Context 문서 수
Re-ranking 사용 여부
압축 사용 여부
답변 상태
실패 단계</code></pre>
<p>Golden Set에서 어떤 모듈을 추가했을 때 어떤 질문이 좋아졌는지 확인한다.</p>
<p>검색 결과가 나빠졌다면 Pre-Retrieval인지 Retrieval인지 Post-Retrieval인지 구분할 수 있어야 한다.</p>
<h2 id="마무리">마무리</h2>
<p>Modular RAG는 RAG를 복잡하게 만드는 방법이 아니다.</p>
<p>RAG가 어떤 단계에서 실패하는지 분리해서 확인하고, 해당 단계만 바꿀 수 있도록 만드는 방법이다.</p>
<p>Ingest는 검색 가능한 문서를 만들고, Pre-Retrieval은 질문을 검색에 맞게 준비한다. Retrieval은 관련 후보를 찾고, Post-Retrieval은 최종 근거를 선별한다. Generation은 선택된 근거를 바탕으로 답변을 만든다.</p>
<p>이렇게 단계를 나누면 특정 모델이나 저장소를 바꾸더라도 전체 구조를 다시 작성할 필요가 없다.</p>
<p>다만 모듈은 필요한 만큼만 추가해야 한다.</p>
<p>좋은 Modular RAG는 기능이 많은 RAG가 아니라, 각 기능의 책임과 효과를 설명할 수 있는 RAG다.</p>
<p>다음 글에서는 한 번의 검색으로 충분하지 않은 질문을 처리하는 Self-RAG, Corrective RAG, Agentic RAG를 살펴보자.</p>