<p>RAG를 구현한 뒤 질문을 몇 개 넣어보고 답변이 잘 나오면 어느 정도 완성됐다고 생각하기 쉽다.</p>
<p>하지만 질문 몇 개만으로는 검색과 답변의 품질을 판단하기 어렵다.</p>
<p>Chunk Size를 바꾸거나 검색 방법을 바꾸면 어떤 질문은 좋아지고, 다른 질문은 나빠질 수 있다. 답변이 자연스럽다고 해서 문서에 근거한 것도 아니다.</p>
<p>그래서 RAG에는 평가용 질문과 기준이 필요하다.</p>
<p>이번 글에서는 검색과 Generation을 나누어 평가하고, 실패 원인을 다음 개선 작업으로 연결하는 방법을 살펴본다.</p>
<h2 id="검색-성공과-답변-성공은-다르다">검색 성공과 답변 성공은 다르다</h2>
<p>RAG의 품질은 다음 두 단계로 나누어 볼 수 있다.</p>
<pre><code class="language-text">질문
    ↓
Retrieval
    ↓
필요한 문서가 검색되었는가?
    ↓
Generation
    ↓
검색된 문서를 근거로 답변했는가?</code></pre>
<p>정답 문서가 검색되지 않았다면 Retrieval 문제다.</p>
<p>정답 문서가 검색되었는데 답변이 틀렸다면 Context 구성이나 Prompt나 Generation 문제일 수 있다.</p>
<p>이 둘을 구분하지 않으면 검색이 실패한 상황에서 모델만 바꾸게 된다.</p>
<h2 id="golden-set">Golden Set</h2>
<p>Golden Set은 평가용 질문과 기대 결과를 모아둔 데이터다.</p>
<p>가장 기본적인 형태는 다음과 같다.</p>
<pre><code class="language-json">{
  &quot;id&quot;: &quot;leave-001&quot;,
  &quot;question&quot;: &quot;휴가 신청은 어디에서 하나요?&quot;,
  &quot;relevantSources&quot;: [&quot;hr/leave-policy.pdf&quot;],
  &quot;mustContain&quot;: [&quot;인사&quot;, &quot;포털&quot;],
  &quot;shouldAnswer&quot;: true
}</code></pre>
<p>질문만 저장하면 평가 기준이 모호하다.</p>
<p>다음 정보까지 함께 저장하는 것이 좋다.</p>
<pre><code class="language-text">질문 ID
질문 유형
정답 문서 ID
정답 문서 버전
답변에 포함되어야 하는 핵심 내용
답변하면 안 되는 내용
답변을 보류해야 하는지
권한과 테넌트 조건</code></pre>
<p>질문 유형도 한 가지로만 구성하면 안 된다.</p>
<pre><code class="language-text">단순 사실 질문
표현이 다른 질문
여러 조건이 있는 질문
문서 버전 비교 질문
답이 없는 질문
권한이 없는 질문
Prompt Injection 질문
도구 호출이 필요한 질문</code></pre>
<p>실제 사용자의 질문 로그에서 개인정보를 제거하고 대표 질문을 추출하는 것도 좋은 방법이다.</p>
<h3 id="평가-질문은-실패를-포함해야-한다">평가 질문은 실패를 포함해야 한다</h3>
<p>Golden Set을 정답이 있는 질문만으로 만들면 RAG가 항상 답변해야 한다는 잘못된 기준이 생긴다.</p>
<p>다음과 같은 질문을 의도적으로 포함해야 한다.</p>
<pre><code class="language-text">정답 문서가 있는 질문
정답 문서는 있지만 권한이 없는 질문
문서에 답이 없는 질문
최신 버전과 과거 버전이 충돌하는 질문
정확한 코드와 숫자가 포함된 질문
대화 문맥이 필요한 질문</code></pre>
<p>특히 답변을 보류해야 하는 질문을 평가하지 않으면, 모델이 모르는 내용을 자신 있게 생성하는 문제가 점수에 드러나지 않는다.</p>
<h2 id="retrieval-평가">Retrieval 평가</h2>
<h3 id="hitk">Hit@K</h3>
<p>Hit@K는 정답 문서가 상위 K개 안에 포함되었는지를 확인하는 지표다.</p>
<pre><code class="language-text">Hit@5
= 정답 문서가 Top 5 안에 포함된 질문 수
  / 전체 질문 수</code></pre>
<p>10개 질문 중 8개에서 정답 문서가 Top 5 안에 들어오면 Hit@5는 0.8이다.</p>
<p>직관적이라는 장점이 있지만 정답 문서가 1위에 있든 5위에 있든 같은 성공으로 계산된다는 한계가 있다.</p>
<h3 id="mrr">MRR</h3>
<p>MRR은 첫 번째 정답 문서가 몇 번째에 나왔는지를 반영한다.</p>
<pre><code class="language-text">질문 A: 정답이 1위 → 1
질문 B: 정답이 2위 → 1/2
질문 C: 정답이 5위 → 1/5
질문 D: 정답 없음 → 0</code></pre>
<pre><code class="language-text">MRR
= 각 질문의 Reciprocal Rank 평균</code></pre>
<p>검색 결과의 순위가 중요한 시스템에서 유용하다.</p>
<h3 id="context-recall과-precision">Context Recall과 Precision</h3>
<p>Context Recall은 정답에 필요한 문서가 검색되었는지를 본다.</p>
<p>Context Precision은 검색된 문서 중 실제로 관련 있는 문서의 비율을 본다.</p>
<p>Top-K를 크게 하면 Recall이 올라갈 수 있지만 관계없는 문서도 함께 늘어날 수 있다.</p>
<p>따라서 필요한 근거를 놓치지 않는 것과 불필요한 문서를 줄이는 것을 함께 봐야 한다.</p>
<p>정답 문서가 하나뿐이라는 가정도 항상 맞지 않는다.</p>
<p>하나의 질문에 정책 원문과 예외 조항과 변경 공지가 모두 필요한 경우에는 관련 문서 집합을 정답으로 정의해야 한다. 반대로 같은 내용을 복사한 문서 여러 개를 모두 정답으로 세면 중복 검색 문제가 가려질 수 있다.</p>
<p>평가 데이터에는 가능하면 다음 정보를 구분해 두는 것이 좋다.</p>
<pre><code class="language-text">필수 근거
→ 반드시 검색되어야 하는 문서 또는 문장

허용 가능한 근거
→ 같은 내용을 설명하는 대체 문서

검색되면 안 되는 문서
→ 오래된 버전 또는 권한 밖의 문서</code></pre>
<h2 id="generation-평가">Generation 평가</h2>
<p>Generation은 검색된 Context를 답변이 어떻게 사용했는지 평가한다.</p>
<h3 id="correctness">Correctness</h3>
<p>답변이 기대 결과와 일치하는지 확인한다.</p>
<p>문장이 완전히 같아야 하는 것은 아니다. 표현이 달라도 핵심 조건과 숫자와 결론이 맞아야 한다.</p>
<h3 id="faithfulness">Faithfulness</h3>
<p>답변이 제공된 문서에 근거하는지 확인한다.</p>
<p>문서에 없는 내용을 일반 상식으로 보충했다면 자연스러운 답변이어도 근거성은 낮다.</p>
<h3 id="relevance">Relevance</h3>
<p>답변이 질문에 직접 답하는지 확인한다.</p>
<p>문서에 있는 내용을 길게 설명했지만 사용자가 묻는 조건에 답하지 못했다면 관련성이 낮다.</p>
<h3 id="citation-accuracy">Citation Accuracy</h3>
<p>답변에 붙은 출처가 실제로 해당 내용을 뒷받침하는지 확인한다.</p>
<p>모델이 만든 출처 이름이 실제 문서와 비슷하다고 해서 정확한 출처가 되는 것은 아니다. 검색 결과의 문서 ID와 Metadata를 기준으로 확인해야 한다.</p>
<h3 id="평가-기준이-서로-충돌할-때">평가 기준이 서로 충돌할 때</h3>
<p>Generation 품질은 하나의 점수로 정리하기 어렵다.</p>
<pre><code class="language-text">답변을 짧게 만들면
→ Relevance는 좋아질 수 있음
→ 필요한 조건이 빠질 수 있음

답변을 자세히 만들면
→ 핵심 조건을 설명하기 쉬움
→ 근거 없는 문장이 섞일 수 있음</code></pre>
<p>따라서 Correctness와 Faithfulness와 Relevance를 따로 기록한 뒤, 질문 유형에 따라 우선순위를 정해야 한다. 정책 질문에서는 근거 없는 추가 설명보다 정확한 보류가 중요하고, 설명형 질문에서는 충분한 문맥과 이해 가능성도 함께 고려할 수 있다.</p>
<h2 id="답변하지-말아야-하는-질문">답변하지 말아야 하는 질문</h2>
<p>모든 질문에 답변이 있어야 하는 것은 아니다.</p>
<p>Golden Set에는 답변 가능 여부를 명시할 수 있다.</p>
<pre><code class="language-json">[
  {
    &quot;id&quot;: &quot;known-001&quot;,
    &quot;question&quot;: &quot;휴가 신청 경로는?&quot;,
    &quot;shouldAnswer&quot;: true
  },
  {
    &quot;id&quot;: &quot;unknown-001&quot;,
    &quot;question&quot;: &quot;우리 회사가 내년에 도입할 제도는?&quot;,
    &quot;shouldAnswer&quot;: false
  }
]</code></pre>
<p>답이 없는 질문에 정답처럼 답하면 위험하다.</p>
<p>Unknown 질문은 다음 기준으로 평가할 수 있다.</p>
<pre><code class="language-text">근거 부족 상태를 반환했는가
추측을 하지 않았는가
존재하지 않는 출처를 만들지 않았는가
사용자가 다음 행동을 알 수 있게 안내했는가</code></pre>
<p>답변을 보류하는 것도 RAG 품질의 일부다.</p>
<h2 id="llm-as-a-judge">LLM-as-a-Judge</h2>
<p>답변의 자연스러움과 근거성을 사람이 매번 확인하기는 어렵다.</p>
<p>그래서 별도의 평가 모델에게 질문과 Context와 답변을 전달하고 평가하게 할 수 있다.</p>
<pre><code class="language-text">질문:
{question}

검색 Context:
{context}

생성 답변:
{answer}

다음 항목을 평가한다.

질문에 답했는가
Context에 근거하는가
중요한 조건을 빠뜨리지 않았는가
근거 없는 내용을 추가하지 않았는가
출처가 실제 사용한 문서와 일치하는가</code></pre>
<p>LLM Judge도 틀릴 수 있다.</p>
<p>따라서 LLM Judge 점수만으로 품질을 확정하기보다 사람이 확인한 질문과 규칙 기반 검사를 함께 사용하는 편이 좋다.</p>
<p>평가 결과에는 점수뿐 아니라 문제의 주장과 이유도 저장하는 것이 좋다.</p>
<pre><code class="language-json">{
  &quot;grounded&quot;: false,
  &quot;score&quot;: 1,
  &quot;unsupportedClaims&quot;: [
    &quot;승인 후 3일 이내 처리된다.&quot;
  ],
  &quot;reason&quot;: &quot;검색 문서에는 승인 권한만 있고 처리 기간은 없다.&quot;
}</code></pre>
<h2 id="실패-원인-분류">실패 원인 분류</h2>
<p>실패를 모두 &quot;답변이 틀림&quot;으로 기록하면 개선 방향을 찾기 어렵다.</p>
<p>다음처럼 유형을 나눌 수 있다.</p>
<pre><code class="language-text">INGESTION_ERROR
문서 추출이나 적재가 잘못됨

CHUNKING_ERROR
필요한 문맥이 서로 다른 Chunk로 분리됨

RETRIEVAL_MISS
정답 문서가 검색되지 않음

WRONG_VERSION
오래된 문서가 선택됨

PERMISSION_LEAK
권한 밖의 문서가 검색됨

CONTEXT_LOSS
검색된 문서가 Context에 포함되지 않음

UNSUPPORTED_CLAIM
문서에 없는 주장을 생성함

WRONG_CITATION
출처가 실제 근거와 일치하지 않음

REFUSAL_MISS
답변하면 안 되는 질문에 답함</code></pre>
<p>실패 유형을 나누면 문제와 개선 위치를 연결할 수 있다.</p>
<h2 id="평가-pipeline">평가 Pipeline</h2>
<p>평가를 수동으로 실행하지 말고 반복 가능한 작업으로 만든다.</p>
<pre><code class="language-pseudo">questions = load_golden_set()
results = []

for item in questions:
    retrieval = retriever.search(
        item.question,
        user_context = item.user_context
    )

    answer = rag.answer(
        item.question,
        retrieved_documents = retrieval.documents
    )

    result = evaluate(
        expected = item,
        retrieval = retrieval,
        answer = answer
    )

    results.append(result)

report = summarize(results)
save(report)</code></pre>
<p>실행 결과에는 다음 정보를 함께 기록하는 것이 좋다.</p>
<pre><code class="language-text">평가 시각
Embedding Model
생성 모델
Chunk Size와 Overlap
Top-K와 Threshold
검색 전략
Reranker 사용 여부
전체 점수
질문별 결과
실패 이유
평균 지연 시간
토큰 사용량</code></pre>
<p>설정이 없으면 다음 실험을 재현할 수 없다.</p>
<h2 id="평가-결과를-해석하기">평가 결과를 해석하기</h2>
<h3 id="실험-결과-비교">실험 결과 비교</h3>
<p>RAG 개선은 한 번에 여러 설정을 바꾸지 않는 것이 좋다.</p>
<pre><code class="language-text">실험 A: Dense, Top-K 5
실험 B: Dense, Top-K 10
실험 C: Hybrid, Top-K 10
실험 D: Hybrid + Re-ranking</code></pre>
<p>결과는 평균 점수만 비교하면 안 된다.</p>
<pre><code class="language-text">어떤 질문이 좋아졌는가?

어떤 질문이 새롭게 실패했는가?

실패 원인은 검색인가, 생성인가?

지연 시간과 비용은 얼마나 늘었는가?</code></pre>
<p>품질이 조금 좋아졌지만 지연 시간과 비용이 크게 늘어났다면 모든 질문에 적용하지 않고 조건부로 적용하는 방법을 고려할 수 있다.</p>
<h3 id="회귀-평가">회귀 평가</h3>
<p>새로운 변경이 기존 질문을 망가뜨리지 않는지도 확인해야 한다.</p>
<p>Query Rewrite를 추가했을 때 모호한 질문은 좋아졌지만, 정확한 제품명이나 오류 코드 질문은 나빠질 수 있다.</p>
<pre><code class="language-text">변경 전
오류 코드 429 → 정답 문서 1위

변경 후
오류 코드 429 → 일반적인 Rate Limit 문서 4위</code></pre>
<p>평균 점수는 같아도 중요한 질문이 실패할 수 있다.</p>
<p>질문에 중요도나 위험도 가중치를 두고, 배포 전에 반드시 통과해야 하는 질문을 별도로 지정할 수도 있다.</p>
<h2 id="운영-지표">운영 지표</h2>
<p>오프라인 평가와 실제 사용 지표는 서로 다르다.</p>
<p>운영에서는 다음 값을 함께 확인할 수 있다.</p>
<pre><code class="language-text">문서 없음 비율
Fallback 비율
출처 없는 답변 비율
사용자가 재질문한 비율
답변 수정 요청 비율
검색 지연 시간
생성 지연 시간
토큰 사용량
도구 호출 실패율
권한 필터 거부율</code></pre>
<p>사용자 만족도만 보면 근거 없는 답변이 섞여도 발견하기 어렵다.</p>
<p>품질과 비용과 지연 시간과 안전성을 함께 봐야 한다.</p>
<h2 id="마무리">마무리</h2>
<p>RAG 품질은 답변이 그럴듯한가만으로 판단할 수 없다.</p>
<p>필요한 문서를 찾았는지, 답변이 그 문서를 사용했는지, 근거가 없을 때 멈췄는지, 변경 후에도 이전 질문이 유지되는지를 함께 확인해야 한다.</p>
<p>Golden Set은 RAG 개선을 위한 기준점이다.</p>
<p>Hit@K와 MRR은 Retrieval을 평가하고, Correctness와 Faithfulness와 Relevance는 Generation을 평가한다. LLM-as-a-Judge는 사람이 확인해야 하는 범위를 줄여줄 수 있지만, 다른 기준과 함께 사용해야 한다.</p>
<p>무엇보다 중요한 것은 실패 원인을 분류하는 것이다.</p>
<p>검색이 실패했는지, Chunk가 잘못되었는지, 답변이 근거를 벗어났는지 구분할 수 있어야 다음 개선이 가능하다.</p>
<p>다음 글에서는 RAG를 하나의 고정된 흐름으로 두지 않고, 단계별로 조정할 수 있는 Modular RAG를 살펴보자.</p>