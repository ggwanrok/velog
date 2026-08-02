<h1 id="prompt-engineering을-넘어-context-engineering">Prompt Engineering을 넘어, Context Engineering</h1>
<p>LLM을 활용하기 시작하면서 좋은 답변을 얻기 위한 핵심 기술로 <strong>Prompt Engineering</strong>이 주목받았다.</p>
<pre><code class="language-text">역할을 부여한다.
요청을 구체적으로 작성한다.
예시를 제공한다.
출력 형식을 지정한다.</code></pre>
<p>하지만 LLM이 단순히 질문에 답하는 것을 넘어 문서를 검색하고, 이전 대화를 기억하며, 외부 도구까지 사용하는 <strong>AI Agent</strong>로 발전하면서 Prompt만 잘 작성하는 것으로는 부족해졌다.</p>
<pre><code class="language-text">이전 대화 중 무엇을 기억시킬까?

어떤 문서를 검색해 제공할까?

도구 실행 결과를 어떻게 전달할까?

정보가 너무 많다면 무엇을 제외할까?

Agent의 실행 결과는 어떻게 검증할까?</code></pre>
<p>이제는 하나의 Prompt뿐 아니라 모델이 작업에 사용하는 <strong>전체 정보 환경</strong>과 <strong>실행 구조</strong>를 함께 설계해야 한다.</p>
<pre><code class="language-text">Prompt Engineering
→ 어떻게 요청할 것인가?

Context Engineering
→ 무엇을 알려줄 것인가?

Harness Engineering
→ 어떻게 안전하게 실행시킬 것인가?</code></pre>
<p>이번 글에서는 Prompt를 구성하고 추론을 유도하는 여러 기법부터, Context Engineering과 Harness Engineering으로 확장되는 흐름을 정리한다.</p>
<hr />
<h1 id="context란-무엇인가">Context란 무엇인가?</h1>
<p>Context는 LLM이 현재 답변을 생성할 때 참고할 수 있는 모든 정보를 의미한다.</p>
<pre><code class="language-text">System Prompt
사용자의 현재 요청
이전 대화 내용
사용자 또는 작업에 대한 기억
검색된 문서
데이터베이스 조회 결과
도구 사용 방법과 실행 결과
예시와 출력 형식</code></pre>
<p>즉, Context는 사용자가 마지막으로 입력한 문장만을 의미하지 않는다.</p>
<pre><code class="language-text">모델의 기본 규칙
+
현재 요청
+
이전 대화와 기억
+
외부에서 가져온 정보
+
출력 요구사항
=
현재 응답에 사용되는 Context</code></pre>
<p>예를 들어 사용자가 다음과 같이 요청했다고 하자.</p>
<blockquote>
<p>지난 회의 내용을 바탕으로 고객에게 일정 변경 메일을 작성해줘.</p>
</blockquote>
<p>이 요청을 제대로 처리하려면 단순히 이메일 작성법만 알아서는 부족하다.</p>
<pre><code class="language-text">기존 회의 일정
변경된 일정
고객의 이름과 회사
변경 사유
이전 회의 내용
회사의 이메일 작성 방식</code></pre>
<p>이러한 정보가 함께 제공되어야 LLM이 실제 상황에 맞는 답변을 생성할 수 있다.</p>
<hr />
<h1 id="prompt-engineering과-무엇이-다를까">Prompt Engineering과 무엇이 다를까?</h1>
<p>두 개념의 차이는 다음처럼 정리할 수 있다.</p>
<pre><code class="language-text">Prompt Engineering
→ 모델에게 어떻게 말할 것인가?

Context Engineering
→ 모델에게 무엇을 알려줄 것인가?</code></pre>
<h2 id="prompt-engineering">Prompt Engineering</h2>
<p>Prompt Engineering은 모델에 전달하는 <strong>지시문의 구조와 표현</strong>을 설계한다.</p>
<pre><code class="language-text">당신은 데이터 분석가입니다.

다음 매출 데이터를 분석하고
핵심 특징을 세 가지로 정리하세요.

결과는 마크다운 표로 출력하세요.</code></pre>
<p>주로 다음 항목을 다룬다.</p>
<ul>
<li>모델의 역할</li>
<li>수행할 작업</li>
<li>판단 기준</li>
<li>제한 조건</li>
<li>예시</li>
<li>출력 형식</li>
</ul>
<h2 id="context-engineering">Context Engineering</h2>
<p>Context Engineering은 지시문을 포함해 모델이 판단에 사용할 <strong>전체 정보 상태</strong>를 설계한다.</p>
<pre><code class="language-text">분석 대상 매출 데이터
회사의 매출 지표 정의
지난달 분석 결과
현재 분석 목적
관련 내부 문서
도구 실행 결과
원하는 출력 구조</code></pre>
<p>따라서 Prompt Engineering은 Context Engineering을 구성하는 요소 가운데 하나라고 볼 수 있다.</p>
<table>
<thead>
<tr>
<th>구분</th>
<th>Prompt Engineering</th>
<th>Context Engineering</th>
</tr>
</thead>
<tbody><tr>
<td>중심 질문</td>
<td>어떻게 요청할까?</td>
<td>어떤 정보를 제공할까?</td>
</tr>
<tr>
<td>주요 대상</td>
<td>역할, 지시, 예시, 표현</td>
<td>대화, 기억, 문서, 도구, 상태</td>
</tr>
<tr>
<td>활용 범위</td>
<td>한 번의 질의응답</td>
<td>멀티턴 대화, RAG, AI Agent</td>
</tr>
<tr>
<td>핵심 목적</td>
<td>원하는 응답 유도</td>
<td>올바른 판단 환경 구성</td>
</tr>
</tbody></table>
<hr />
<h1 id="prompt를-구성하는-기본-방법">Prompt를 구성하는 기본 방법</h1>
<h2 id="system-prompt와-user-prompt">System Prompt와 User Prompt</h2>
<p>Prompt는 크게 System Prompt와 User Prompt로 구분할 수 있다.</p>
<h3 id="system-prompt">System Prompt</h3>
<p>시스템 또는 개발자가 모델에 설정하는 초기 지침이다.</p>
<pre><code class="language-text">당신은 전문 요리사입니다.
초보자도 따라 할 수 있는 조리법을 안내하세요.</code></pre>
<p>모델의 역할, 행동 방식, 말투와 기본 원칙을 설정한다.</p>
<h3 id="user-prompt">User Prompt</h3>
<p>사용자가 현재 수행할 작업을 전달하는 입력이다.</p>
<pre><code class="language-text">오늘 저녁으로 만들 수 있는
간단한 파스타를 추천해 주세요.</code></pre>
<pre><code class="language-text">System Prompt
→ 전체 대화에서 유지할 역할과 원칙

User Prompt
→ 현재 처리할 구체적인 요청</code></pre>
<hr />
<h2 id="rice-prompt-framework">RICE Prompt Framework</h2>
<p>자료에서는 Prompt를 구조적으로 작성하는 방법으로 <strong>RICE Framework</strong>를 소개한다.</p>
<pre><code class="language-text">R: Role
I: Instruction
C: Context
E: Examples</code></pre>
<h3 id="role">Role</h3>
<p>모델이 누구의 관점으로 판단할지를 지정한다.</p>
<pre><code class="language-text">당신은 대기업 전략기획팀에서 근무하는
보고서 작성 전문가입니다.</code></pre>
<p>Role을 부여하면 모델은 해당 역할에 적합한 지식, 표현 방식과 판단 기준을 우선적으로 사용한다.</p>
<p>다만 역할만 길게 작성하는 것보다 실제로 필요한 전문성과 업무 범위를 구체적으로 제시하는 것이 좋다.</p>
<hr />
<h3 id="instruction">Instruction</h3>
<p>모델이 무엇을 해야 하는지 명확하게 지정한다.</p>
<pre><code class="language-text">다음 매출 데이터를 분석하고
주요 특징 세 가지와 개선 방향을 제안하세요.</code></pre>
<p>Instruction은 단순히 무엇을 생각하라고 하는 것이 아니라, <strong>어떤 절차와 기준으로 작업해야 하는지</strong>를 알려주는 부분이다.</p>
<pre><code class="language-text">모호한 요청
→ 매출 데이터를 분석해줘.

구체적인 요청
→ 전월 대비 증감률을 계산하고,
  가장 큰 변화가 나타난 항목 세 개를 찾아
  원인과 대응 방안을 제안해줘.</code></pre>
<hr />
<h3 id="context">Context</h3>
<p>질문과 관련된 배경 정보와 참고 지식을 제공한다.</p>
<pre><code class="language-text">우리 회사는 직원 30명 규모의 중소 IT 기업이다.

회의가 많고 문서 정리가 비효율적이며,
업무 효율을 높이는 방안을 검토하고 있다.</code></pre>
<p>Context는 모델의 사고 범위와 판단 기준을 설정한다.</p>
<pre><code class="language-text">배경 정보 없음
→ 일반적인 아이디어 생성

배경 정보 제공
→ 현재 상황에 적합한 아이디어 생성</code></pre>
<p>필요한 Context를 사용자가 정확히 알지 못한다면, 모델이 먼저 질문하도록 만들 수도 있다.</p>
<hr />
<h3 id="examples">Examples</h3>
<p>원하는 응답 형식이나 평가 기준을 예시로 제공한다.</p>
<pre><code class="language-text">다음 형식으로 분석해줘.

[Strength]
도입하려는 기술이 기존 시스템과 쉽게 연동된다.

[Weakness]
실제 운영 환경에서 충분히 검증되지 않았다.</code></pre>
<p>Example은 단순한 샘플 출력을 넘어, 모델에 <strong>채점 기준과 답변 패턴</strong>을 알려주는 역할을 한다.</p>
<hr />
<h2 id="추가적인-prompt-구성-요소">추가적인 Prompt 구성 요소</h2>
<p>RICE 외에도 다음 요소를 함께 지정할 수 있다.</p>
<h3 id="policy와-rule">Policy와 Rule</h3>
<p>응답이 반드시 따라야 할 정책과 규칙을 설정한다.</p>
<pre><code class="language-text">확인되지 않은 내용은 추측하지 않는다.
수치는 제공된 자료에서만 사용한다.
근거가 없다면 확인이 필요하다고 표시한다.</code></pre>
<h3 id="style">Style</h3>
<p>답변의 표현 방식을 지정한다.</p>
<pre><code class="language-text">경영진 보고서처럼 작성한다.
간결하고 논리적으로 작성한다.
전문 용어에는 짧은 설명을 덧붙인다.</code></pre>
<h3 id="constraints">Constraints</h3>
<p>분량이나 개수와 같은 제약사항을 설정한다.</p>
<pre><code class="language-text">500자 이내로 작성한다.
제안은 다섯 개만 제시한다.
각 항목은 두 문장을 넘지 않는다.</code></pre>
<h3 id="format과-structure">Format과 Structure</h3>
<p>답변이 따라야 할 구조를 지정한다.</p>
<pre><code class="language-text">제목과 소제목으로 구분한다.
비교 결과는 표로 작성한다.
마지막에는 핵심 내용을 세 줄로 요약한다.</code></pre>
<p>복잡한 Prompt는 Markdown을 사용해 구조를 구분하면 모델이 각 정보의 역할을 파악하기 쉽다.</p>
<pre><code class="language-markdown"># Role

# Goal

# Context

# Rules

# Output Format</code></pre>
<hr />
<h2 id="예시를-이용한-prompting">예시를 이용한 Prompting</h2>
<h3 id="zero-shot">Zero-shot</h3>
<p>작업 예시 없이 지시만 제공한다.</p>
<pre><code class="language-text">다음 문장의 감정을 긍정 또는 부정으로 분류해줘.

문장: 이 영화는 정말 재미있었다.</code></pre>
<p>모델이 이미 작업 방법을 충분히 학습했다고 판단할 때 사용할 수 있다.</p>
<hr />
<h3 id="one-shot">One-shot</h3>
<p>하나의 예시를 제공한다.</p>
<pre><code class="language-text">예시
입력: 배송이 빠르고 만족스럽습니다.
출력: 긍정

입력: 가격은 비싸지만 성능은 괜찮습니다.
출력:</code></pre>
<p>모델에 답변의 기본 방향과 형식을 전달할 수 있다.</p>
<hr />
<h3 id="few-shot">Few-shot</h3>
<p>여러 개의 예시를 제공한다.</p>
<pre><code class="language-text">입력: 배송이 빠르고 만족스럽습니다.
출력: 긍정

입력: 두 번 사용했는데 고장 났습니다.
출력: 부정

입력: 가격은 비싸지만 성능은 괜찮습니다.
출력:</code></pre>
<p>예시가 많아지면 작업 기준을 구체적으로 전달할 수 있지만, Context Window와 토큰 비용도 함께 증가한다.</p>
<p>또한 예시의 <strong>정답뿐 아니라 형식의 일관성</strong>도 중요하다.</p>
<blockquote>
<p>정답에 대한 예시가 아니더라도, 형식의 일관성이 갖춰질 경우, 응답 정확도가 올라간다는 연구 자료 또한 존재한다.</p>
</blockquote>
<pre><code class="language-text">예시마다 구조가 다름
→ 모델이 패턴을 찾기 어려움

입력과 출력 형식이 일관됨
→ 모델이 작업 구조를 쉽게 파악</code></pre>
<hr />
<h2 id="추론을-유도하는-prompting-기법">추론을 유도하는 Prompting 기법</h2>
<h3 id="chain-of-thought">Chain of Thought</h3>
<p><strong>Chain of Thought, CoT</strong>는 모델이 중간 추론 단계를 거쳐 답을 생성하도록 유도하는 방법이다.</p>
<pre><code class="language-text">문제를 단계별로 나누어 생각해줘.

각 단계의 판단 근거를 확인한 뒤
최종 결론을 제시해줘.</code></pre>
<p>복잡한 수학 문제나 다단계 판단에 도움이 될 수 있다.</p>
<p>다만 모든 문제에서 CoT가 효과적인 것은 아니다.</p>
<pre><code class="language-text">복잡한 추론 문제
→ CoT가 도움될 수 있음

단순 조회나 분류
→ 불필요한 추론이 비용만 늘릴 수 있음</code></pre>
<hr />
<h3 id="step-back-prompting">Step-back Prompting</h3>
<p>바로 세부 문제를 풀기 전에 한 단계 물러나 <strong>더 큰 원리와 맥락</strong>을 먼저 생각하게 한다.</p>
<pre><code class="language-text">이 문제를 바로 해결하기 전에,
관련된 핵심 원칙과 일반적인 해결 방법부터 정리해줘.

그 원칙을 현재 문제에 적용해줘.</code></pre>
<p>복잡한 문제의 표면적인 조건에 매몰되지 않고 근본적인 개념을 먼저 활용하도록 돕는다.</p>
<hr />
<h3 id="self-consistency">Self-Consistency</h3>
<p>하나의 추론만 수행하는 것이 아니라 여러 추론 경로를 생성하고, 가장 일관된 결론을 선택하는 방식이다.</p>
<pre><code class="language-text">서로 다른 접근 방법 세 가지로 문제를 분석해줘.

각 접근의 결론을 비교한 뒤
가장 일관된 답을 최종 결과로 선택해줘.</code></pre>
<p>단일 추론의 우연한 오류를 줄일 수 있지만, 여러 번 추론하므로 비용이 증가한다.</p>
<hr />
<h3 id="devils-advocate-prompting">Devil's Advocate Prompting</h3>
<p>모델이 현재 결론에 반대하는 관점에서 문제를 검토하도록 한다.</p>
<pre><code class="language-text">현재 제안이 실패했다고 가정해줘.

실패 원인과 놓친 위험을 찾아
기존 제안을 비판적으로 검토해줘.</code></pre>
<p>일종의 사전 부검인 <strong>Pre-mortem</strong> 방식으로 활용할 수 있다.</p>
<p>계획의 허점, 숨겨진 위험과 반대 논리를 발견하는 데 유용하다.</p>
<hr />
<h3 id="role-based-multi-persona-prompting">Role-Based Multi-Persona Prompting</h3>
<p>하나의 모델에 여러 역할을 부여하고 서로 다른 관점에서 검토하게 한다.</p>
<pre><code class="language-text">CFO 관점
→ 비용과 투자수익률 검토

COO 관점
→ 운영 가능성과 실행 효율 검토

두 관점의 의견을 비교한 뒤
공통 결론과 남은 쟁점을 정리해줘.</code></pre>
<p>단순히 “좋은 점과 나쁜 점”을 묻는 것보다 실제 이해관계자의 판단 기준을 적용할 수 있다.</p>
<hr />
<h3 id="socratic-prompting">Socratic Prompting</h3>
<p>소크라테스식 문답법을 적용해 모델이 질문을 통해 필요한 Context를 수집하도록 한다.</p>
<pre><code class="language-text">바로 답변하지 말고,
정확한 제안서를 작성하기 위해 필요한 질문을
한 번에 하나씩 물어봐줘.

질문이 끝나면 내 답변 전체를 바탕으로 작성해줘.</code></pre>
<p>사용자도 어떤 정보를 제공해야 하는지 모르는 상황에서 유용하다.</p>
<pre><code class="language-text">부족한 Context
→ 모델이 질문
→ 사용자 답변
→ Context 확장
→ 최종 작업 수행</code></pre>
<hr />
<h3 id="meta-prompting">Meta Prompting</h3>
<p>모델에 문제를 직접 풀게 하는 것이 아니라, 문제를 해결하기 위한 <strong>좋은 Prompt 자체를 설계하도록 요청</strong>한다.</p>
<pre><code class="language-text">다음 작업을 가장 잘 수행할 수 있는
AI Prompt를 작성해줘.

역할, Context, 판단 기준,
출력 구조와 제약조건을 포함해줘.</code></pre>
<pre><code class="language-text">사용자
→ Prompt를 작성하는 Prompt 제공

모델
→ 실제 작업용 Prompt 생성

생성된 Prompt
→ 본 작업에 사용</code></pre>
<hr />
<h1 id="생성-결과를-조절하는-설정">생성 결과를 조절하는 설정</h1>
<p>다음 항목들은 Context 자체라기보다, Context를 바탕으로 모델이 <strong>어떻게 출력을 생성할지 조절하는 설정</strong>이다.</p>
<h2 id="max-tokens">Max Tokens</h2>
<p>모델이 생성할 수 있는 최대 출력 길이를 제한한다.</p>
<p>값을 크게 설정할수록 더 긴 답변을 만들 수 있지만, 응답 시간과 비용도 증가할 수 있다.</p>
<p>Max Tokens를 낮춘다고 모델이 자동으로 핵심만 간결하게 작성하는 것은 아니다. Prompt에서도 원하는 분량과 구조를 명시해야 한다.</p>
<hr />
<h2 id="temperature">Temperature</h2>
<p>다음 토큰을 선택할 때의 무작위성을 조절한다.</p>
<pre><code class="language-text">낮은 Temperature
→ 높은 확률의 토큰 중심
→ 사실적이고 일관된 출력

높은 Temperature
→ 다양한 토큰 선택
→ 창의적이고 다양한 출력</code></pre>
<p>다만 높은 Temperature가 항상 창의성을 높이거나, 낮은 Temperature가 완전한 재현성을 보장하는 것은 아니다.</p>
<hr />
<h2 id="top-k">Top-k</h2>
<p>확률이 높은 상위 <code>k</code>개의 토큰만 후보로 남긴다.</p>
<pre><code class="language-text">Top-k가 작음
→ 후보가 제한됨
→ 보수적인 출력

Top-k가 큼
→ 더 많은 후보 사용
→ 다양한 출력</code></pre>
<hr />
<h2 id="top-p">Top-p</h2>
<p>확률이 높은 순서로 토큰을 모아, 누적 확률이 <code>p</code>에 도달할 때까지의 후보만 사용한다.</p>
<p>문맥에 따라 후보 수가 동적으로 변한다는 점에서 Top-k와 차이가 있다.</p>
<hr />
<h2 id="min-p">Min-p</h2>
<p>등장 확률이 지나치게 낮은 토큰을 후보에서 제외한다.</p>
<p>가능성이 거의 없는 토큰이 선택되어 출력이 불안정해지는 것을 줄이는 데 사용한다.</p>
<hr />
<h2 id="reasoning-effort">Reasoning Effort</h2>
<p>최종 답변을 만들기 전에 모델이 수행할 내부 추론의 수준을 조절한다.</p>
<pre><code class="language-text">낮은 Reasoning Effort
→ 분류, 단순 조회, 빠른 응답

높은 Reasoning Effort
→ 복잡한 분석, 전략 수립, 어려운 코딩</code></pre>
<p>모든 질문에 가장 높은 수준의 추론을 사용하는 것은 비용과 응답 시간 측면에서 비효율적일 수 있다.</p>
<hr />
<h2 id="verbosity">Verbosity</h2>
<p>최종 답변을 얼마나 간결하거나 자세하게 작성할지를 조절한다.</p>
<pre><code class="language-text">낮은 Verbosity
→ 핵심만 짧게 전달

높은 Verbosity
→ 배경과 근거까지 자세히 설명</code></pre>
<p>Reasoning Effort가 생각의 깊이를 조절한다면, Verbosity는 최종 표현의 상세함을 조절한다.</p>
<hr />
<h1 id="context-engineering이-필요한-이유">Context Engineering이 필요한 이유</h1>
<p>좋은 Prompt와 추론 기법을 사용해도 모델에 필요한 정보가 없다면 정확한 결과를 만들기 어렵다.</p>
<pre><code class="language-text">좋은 모델
+
좋은 Prompt
+
부족한 정보
=
그럴듯하지만 부정확한 답변</code></pre>
<p>특히 AI Agent는 하나의 요청을 처리하며 여러 단계를 거친다.</p>
<pre><code class="language-text">사용자 목표 파악
→ 필요한 정보 검색
→ 외부 도구 실행
→ 결과 확인
→ 다음 행동 결정
→ 최종 결과 생성</code></pre>
<p>작업 단계가 진행될 때마다 검색 결과, 도구 결과와 새로운 결정이 추가되므로 Context도 계속 변화한다.</p>
<p>따라서 Context Engineering은 다음을 설계한다.</p>
<pre><code class="language-text">어떤 정보를 수집할 것인가?

어떤 정보를 모델에 제공할 것인가?

어떤 정보는 제외할 것인가?

정보를 어떤 구조와 순서로 배치할 것인가?

오래된 정보는 언제 갱신할 것인가?</code></pre>
<hr />
<h1 id="context-engineering의-주요-구성-요소">Context Engineering의 주요 구성 요소</h1>
<p>자료에서는 Context Engineering의 구성 요소를 네 가지로 정리한다. </p>
<pre><code class="language-text">1. System Prompt 설계
2. 메모리와 히스토리
3. 도구와 외부 지식
4. Few-shot과 포맷</code></pre>
<hr />
<h2 id="system-prompt-설계">System Prompt 설계</h2>
<p>System Prompt에는 Agent가 항상 따라야 할 역할, 목적과 제약사항을 작성한다.</p>
<pre><code class="language-text">당신은 사내 문서 검색 Agent다.

검색된 문서만을 근거로 답변한다.
근거가 부족하면 추측하지 않는다.
충돌하는 문서가 있다면 최신 승인 문서를 우선한다.</code></pre>
<p>모든 업무 지식을 한 번에 넣는 것이 아니라, 항상 적용되는 핵심 원칙을 중심으로 구성한다.</p>
<hr />
<h2 id="memory와-history">Memory와 History</h2>
<h3 id="history">History</h3>
<p>현재까지 사용자와 모델이 주고받은 대화 기록이다.</p>
<pre><code class="language-text">사용자: 부산으로 여행을 가고 싶어.
AI: 일정은 언제인가요?
사용자: 8월 15일부터 17일까지.
사용자: 예산은 숙박 포함 60만 원이야.</code></pre>
<h3 id="memory">Memory</h3>
<p>현재 대화가 끝난 후에도 다시 활용할 가치가 있는 정보다.</p>
<pre><code class="language-text">사용자는 대중교통 여행을 선호한다.
숙소는 조용한 지역을 선호한다.
여행 일정은 여유롭게 구성하는 편이다.</code></pre>
<table>
<thead>
<tr>
<th>구분</th>
<th>의미</th>
</tr>
</thead>
<tbody><tr>
<td>History</td>
<td>현재 대화의 흐름을 이해하기 위한 기록</td>
</tr>
<tr>
<td>Memory</td>
<td>이후 대화에서도 재사용할 정보</td>
</tr>
</tbody></table>
<p>모든 내용을 Memory에 저장하면 오래되거나 잘못된 정보가 이후 답변까지 오염시킬 수 있다. 장기간 유지할 가치가 있는 확정된 정보만 관리해야 한다.</p>
<hr />
<h2 id="외부-지식과-rag">외부 지식과 RAG</h2>
<p>LLM이 학습하지 않은 회사 내부 정보나 최신 정보는 외부에서 가져와야 한다.</p>
<p>대표적인 방식이 <strong>RAG</strong>다.</p>
<pre><code class="language-text">사용자 질문
→ 관련 문서 검색
→ 필요한 부분 선택
→ LLM에 근거로 제공
→ 근거 기반 답변 생성</code></pre>
<p>문서를 많이 넣는 것보다 다음 기준이 중요하다.</p>
<pre><code class="language-text">질문과 관련 있는가?
최신 문서인가?
신뢰할 수 있는 출처인가?
다른 문서와 충돌하지 않는가?</code></pre>
<hr />
<h2 id="tool-사용">Tool 사용</h2>
<p>AI Agent는 웹 검색, 데이터베이스 조회, 코드 실행, 이메일 발송 등의 도구를 사용할 수 있다.</p>
<pre><code class="language-text">사용자 요청
→ 필요한 도구 선택
→ 도구 실행
→ 결과를 Context에 추가
→ 다음 행동 결정</code></pre>
<p>도구를 제공할 때는 다음 내용을 함께 정의해야 한다.</p>
<pre><code class="language-text">언제 사용하는가?
어떤 입력이 필요한가?
무엇을 반환하는가?
오류는 어떻게 처리하는가?
실행 전 사용자 승인이 필요한가?</code></pre>
<hr />
<h2 id="few-shot과-format">Few-shot과 Format</h2>
<p>Few-shot은 모델에 판단 기준과 작업 형식을 전달한다.</p>
<p>Format은 결과를 다음 시스템이 사용할 수 있도록 구조화한다.</p>
<pre><code class="language-json">{
  &quot;clause&quot;: &quot;제3조&quot;,
  &quot;risk_level&quot;: &quot;HIGH&quot;,
  &quot;reason&quot;: &quot;손해배상 범위가 제한되어 있지 않음&quot;,
  &quot;recommendation&quot;: &quot;손해배상 한도를 명시해야 함&quot;
}</code></pre>
<p>다만 JSON 구조가 올바르다고 해서 내용까지 정확한 것은 아니다.</p>
<pre><code class="language-text">형식 검증
→ JSON 구조가 올바른가?

내용 검증
→ 실제 근거와 일치하는가?</code></pre>
<hr />
<h1 id="context-rot">Context Rot</h1>
<p>Context Window가 커졌다고 모든 정보를 넣는 것이 좋은 것은 아니다.</p>
<p>자료에서는 Context 안에 중요하지 않거나 오래되고 불필요한 정보가 쌓여 추론 품질이 저하되는 현상을 <strong>Context Rot</strong>, 즉 Context 부패로 설명한다. </p>
<pre><code class="language-text">필요한 정보 5개
+
관련 없는 정보 100개
=
중요한 정보가 묻힐 수 있음</code></pre>
<p>대화가 길어지면 과거 조건과 현재 조건이 충돌할 수도 있다.</p>
<pre><code class="language-text">과거 예산: 100만 원
현재 예산: 60만 원</code></pre>
<p>전체 대화를 그대로 전달하기보다 현재 상태를 따로 관리하는 것이 좋다.</p>
<pre><code class="language-text">[CURRENT STATE]

여행지: 부산
기간: 8월 15일~17일
현재 예산: 60만 원
교통수단: 대중교통</code></pre>
<p>Context Engineering의 목적은 Context Window를 가득 채우는 것이 아니다.</p>
<blockquote>
<p>현재 작업에 필요한 정보의 밀도를 높이는 것이 핵심이다.</p>
</blockquote>
<hr />
<h1 id="좋은-context를-만드는-기준">좋은 Context를 만드는 기준</h1>
<pre><code class="language-text">현재 질문과 관련 있는가?

출처가 명확한가?

최신 정보인가?

서로 충돌하지 않는가?

중복된 내용은 없는가?

모델이 이해하기 쉽게 구성되었는가?</code></pre>
<p>Context의 역할을 구분해 제공하면 모델이 정보를 더 명확하게 해석할 수 있다.</p>
<pre><code class="language-text">[GOAL]
현재 달성해야 할 목표

[CURRENT STATE]
지금까지 확정된 상태

[INSTRUCTION]
모델이 수행할 작업

[REFERENCE]
검색된 문서와 참고 근거

[TOOLS]
사용할 수 있는 외부 도구

[OUTPUT FORMAT]
결과의 구조</code></pre>
<hr />
<h1 id="context-engineering을-넘어-harness-engineering으로">Context Engineering을 넘어 Harness Engineering으로</h1>
<p>Context Engineering은 Agent에게 필요한 정보를 제공하는 기술이다.</p>
<p>하지만 다음 문제는 Context만으로 해결하기 어렵다.</p>
<pre><code class="language-text">도구가 올바르게 실행되는가?

실패가 발생하면 어떻게 처리하는가?

같은 실수가 반복되지 않는가?

Agent에게 어떤 권한이 있는가?

결과물이 합격 기준을 만족하는가?</code></pre>
<p>이 문제를 다루는 것이 <strong>Harness Engineering</strong>이다.</p>
<p>Harness는 말의 힘을 원하는 방향으로 전달하는 마구를 의미한다.</p>
<pre><code class="language-text">LLM
→ 강력하지만 예측하기 어려운 힘

Harness
→ 힘을 안전하고 유용한 방향으로 전달하는 시스템</code></pre>
<p>자료에서는 Harness Engineering을 <strong>Agent가 실수할 때 같은 실수를 다시 하지 않도록 시스템을 개선하는 것</strong>으로 설명한다. </p>
<hr />
<h2 id="application-legibility">Application Legibility</h2>
<p>Agent가 자신이 수행한 작업의 결과를 직접 확인할 수 있도록 만든다.</p>
<pre><code class="language-text">Agent가 코드 수정
→ 빌드 실행
→ 테스트 실행
→ 결과 확인
→ 실패 시 다시 수정</code></pre>
<p>모델에게 “잘 작성했는지 확인해”라고 말하는 것보다 시스템이 테스트 결과를 숫자와 상태로 제공하는 것이 안전하다.</p>
<hr />
<h2 id="mechanical-hierarchy">Mechanical Hierarchy</h2>
<p>중요한 제약을 Prompt가 아니라 시스템 구조에서 강제한다.</p>
<pre><code class="language-text">Prompt:
운영 데이터를 삭제하지 마세요.</code></pre>
<p>보다 다음 구조가 강력하다.</p>
<pre><code class="language-text">권한:
Agent 계정에는 운영 데이터 삭제 권한이 없음.</code></pre>
<pre><code class="language-text">Prompt의 부탁
&lt;
도구 입력 검증
&lt;
애플리케이션 정책
&lt;
접근 권한
&lt;
실행 자체를 차단하는 구조</code></pre>
<hr />
<h2 id="progressive-disclosure">Progressive Disclosure</h2>
<p>Agent에게 처음부터 모든 문서와 규칙을 제공하지 않고, 필요한 순간에 필요한 정보만 전달한다.</p>
<pre><code class="language-text">작업 시작
→ 핵심 역할과 목표 제공

문서 검색 단계
→ 검색 규칙 제공

코드 수정 단계
→ 코드 스타일과 저장소 규칙 제공

배포 단계
→ 배포 절차와 승인 규칙 제공</code></pre>
<p>Context Rot를 줄이면서 필요한 정보는 유지할 수 있는 방식이다.</p>
<hr />
<h1 id="마무리">마무리</h1>
<p>Prompt Engineering은 LLM에 <strong>요청을 명확하게 전달하는 방법</strong>이다.</p>
<p>Context Engineering은 모델이 올바르게 판단할 수 있도록 <strong>필요한 정보 전체를 구성하는 방법</strong>이다.</p>
<p>Harness Engineering은 모델의 판단이 실제 행동으로 이어질 때 <strong>실행 과정과 결과를 통제하는 방법</strong>이다.</p>
<pre><code class="language-text">Prompt Engineering
→ 어떻게 말할 것인가?

Context Engineering
→ 무엇을 알려줄 것인가?

Harness Engineering
→ 어떻게 안전하게 행동시킬 것인가?</code></pre>
<p>결국 좋은 AI 서비스는 좋은 모델 하나만으로 만들어지지 않는다.</p>
<pre><code class="language-text">모델의 성능
+
구조화된 Prompt
+
관련성 높은 Context
+
신뢰할 수 있는 외부 지식
+
검증 가능한 실행 구조
=
안정적인 AI 서비스</code></pre>
<blockquote>
<p>중요한 것은 정보를 많이 제공하거나 지시를 길게 작성하는 것이 아니다. 필요한 정보를 필요한 순간에 올바른 구조로 전달하고, 그 결과가 안전하게 실행되도록 시스템을 설계하는 것이다.</p>
</blockquote>