<h1 id="rdbms의-벡터검색">RDBMS의 벡터검색</h1>
<p>관계형 데이터베이스는 원래 값을 기준으로 데이터를 찾는다.</p>
<pre><code class="language-sql">WHERE category = '계약서'
WHERE created_at &gt;= '2026-01-01'
WHERE price BETWEEN 10000 AND 50000</code></pre>
<p>하지만 AI 서비스에서는 이런 질문도 처리해야 한다.</p>
<pre><code class="language-text">“일방적으로 계약을 해지하는 내용과 비슷한 조항을 찾아줘.”</code></pre>
<p>정확한 단어나 값은 모르지만, <strong>의미가 비슷한 데이터</strong>를 찾고 싶은 것이다.</p>
<p>PostgreSQL의 <code>pgvector</code>는 기존 관계형 데이터베이스에 이러한 의미 검색 기능을 추가한다.</p>
<hr />
<h2 id="벡터-컬럼-사용법">벡터 컬럼 사용법</h2>
<ul>
<li>pgvector 확장을 활성화한다.</li>
</ul>
<pre><code class="language-sql">CREATE EXTENSION vector;</code></pre>
<ul>
<li>기존 테이블에 임베딩을 저장할 벡터 컬럼을 추가한다.</li>
</ul>
<pre><code class="language-sql">CREATE TABLE contract_clauses (
    clause_id       bigint PRIMARY KEY,
    contract_type   varchar(30),
    risk_level      varchar(10),
    content         text,
    embedding       vector(1536)
);</code></pre>
<p>하나의 행은 다음처럼 구성된다.</p>
<pre><code class="language-text">조항 ID
계약서 종류
위험 등급
조항 원문
조항의 임베딩 벡터</code></pre>
<blockquote>
<p>임베딩은 데이터베이스가 직접 만드는 것이 아니다.</p>
</blockquote>
<pre><code class="language-text">조항 원문
  ↓
Transformer 기반 임베딩 모델
  ↓
[0.12, -0.31, 0.74, ...]
  ↓
embedding 컬럼에 저장</code></pre>
<p>즉, 임베딩 모델이 의미를 숫자로 표현하고, 데이터베이스는 그 결과를 보관한다.</p>
<hr />
<h2 id="가까운-의미-데이터-찾기">가까운 의미 데이터 찾기</h2>
<p>사용자의 질문도 같은 임베딩 모델로 벡터화한다.</p>
<pre><code class="language-text">“마음대로 계약을 해지할 수 있나요?”
  ↓
질문 벡터</code></pre>
<p>이후 SQL로 가까운 조항을 찾을 수 있다.</p>
<pre><code class="language-sql">SELECT
    clause_id,
    content,
    1 - (embedding &lt;=&gt; :query_embedding) AS similarity
FROM contract_clauses
ORDER BY embedding &lt;=&gt; :query_embedding
LIMIT 5;</code></pre>
<p><code>&lt;=&gt;</code>는 코사인 거리를 계산하는 연산자다.</p>
<p>인덱스가 없다면 데이터베이스는 질문 벡터를 모든 행의 벡터와 비교한다.</p>
<pre><code class="language-text">질문 ↔ 1번 조항
질문 ↔ 2번 조항
질문 ↔ 3번 조항
...</code></pre>
<p>정확하지만 데이터가 많아지면 느려진다.</p>
<p>따라서 벡터 검색에도 인덱스를 사용한다.</p>
<hr />
<h1 id="벡터검색-인덱스">벡터검색 인덱스</h1>
<h2 id="hnsw-가까운-벡터를-연결한-길">HNSW: 가까운 벡터를 연결한 길</h2>
<p>HNSW는 가까운 벡터끼리 연결한 다층 그래프다.</p>
<pre><code class="language-text">상위 계층
A ───────── F

중간 계층
A ── C ─── F

하위 계층
A-B-C-D-E-F</code></pre>
<p>먼 거리에서는 상위 계층을 이용해 빠르게 이동하고, 목적지 근처에서는 하위 계층을 자세히 탐색한다.</p>
<pre><code class="language-text">고속도로로 목적지 근처까지 이동
→ 골목길에서 가까운 데이터 탐색</code></pre>
<p>PostgreSQL에서는 다음과 같이 만든다.</p>
<pre><code class="language-sql">CREATE INDEX idx_clause_embedding_hnsw
ON contract_clauses
USING hnsw (embedding vector_cosine_ops);</code></pre>
<p>HNSW는 일반적으로 검색 속도와 재현율이 좋지만, 인덱스를 만들고 유지하는 데 메모리를 많이 사용한다.</p>
<hr />
<h2 id="ivf-가까운-구역부터-탐색">IVF: 가까운 구역부터 탐색</h2>
<p>IVF는 전체 벡터 공간을 여러 구역으로 나눈다.</p>
<pre><code class="language-text">전체 벡터 공간

┌─────────┬─────────┐
│ 구역 A   │ 구역 B   │
│ ● ● ●   │ ●   ●   │
├─────────┼─────────┤
│ 구역 C   │ 구역 D   │
│ ●   ●   │ ● ● ●   │
└─────────┴─────────┘</code></pre>
<p>질문 벡터가 들어오면 가까운 구역 몇 개만 골라서 탐색한다.</p>
<pre><code class="language-text">질문 벡터
→ 가까운 구역 선택
→ 해당 구역 내부만 비교</code></pre>
<p><code>IVFFlat</code>은 IVF로 구역을 나눈 뒤, 선택된 구역 안에서는 원본 벡터를 직접 비교하는 방식이다.</p>
<pre><code class="language-sql">CREATE INDEX idx_clause_embedding_ivfflat
ON contract_clauses
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);</code></pre>
<p>간단히 비교하면 이렇다.</p>
<table>
<thead>
<tr>
<th>방식</th>
<th>핵심 아이디어</th>
<th>특징</th>
</tr>
</thead>
<tbody><tr>
<td>HNSW</td>
<td>가까운 벡터를 그래프로 연결</td>
<td>빠르고 재현율이 좋지만 메모리 사용량이 큼</td>
</tr>
<tr>
<td>IVFFlat</td>
<td>벡터 공간을 구역으로 분할</td>
<td>비교적 단순하고 가볍지만 튜닝에 민감함</td>
</tr>
</tbody></table>
<blockquote>
<p><strong>다만 HNSW와 IVFFlat은 모든 벡터를 비교하지 않는 근사 최근접 이웃 검색 방식이므로,
속도를 얻는 대신 일부 검색 정확도, 즉 재현율을 양보할 수 있다.</strong></p>
</blockquote>
<hr />
<h1 id="rdbms의-벡터-활용-이점">RDBMS의 벡터 활용 이점</h1>
<h2 id="데이터-중복성-이슈">데이터 중복성 이슈</h2>
<p>전용 벡터 DB를 따로 사용하면 데이터가 나뉜다.</p>
<pre><code class="language-text">PostgreSQL
→ 계약서 원문

Vector DB
→ 계약서 임베딩</code></pre>
<p>계약 내용이 바뀌면 양쪽을 모두 수정해야 한다.</p>
<p>반면 pgvector를 사용하면 원문과 임베딩을 같은 데이터베이스에서 관리할 수 있다.</p>
<pre><code class="language-sql">UPDATE contract_clauses
SET
    content = :new_content,
    embedding = :new_embedding
WHERE clause_id = :clause_id;</code></pre>
<p>같은 데이터베이스에 저장한다고 임베딩이 자동으로 갱신되는 것은 아니다.
다만 원문과 새 임베딩을 하나의 트랜잭션에서 함께 수정할 수 있어,
별도 데이터베이스 사이의 동기화 구조를 줄이고 정합성을 관리하기 쉬워진다.</p>
<hr />
<h2 id="검색-기능의-확장">검색 기능의 확장</h2>
<p>의미적으로 비슷한 모든 조항을 찾는 것이 아니라, 특정 조건을 만족하는 조항만 검색할 수 있다.</p>
<pre><code class="language-sql">SELECT
    clause_id,
    content
FROM contract_clauses
WHERE contract_type = '근로계약서'
  AND risk_level = 'HIGH'
ORDER BY embedding &lt;=&gt; :query_embedding
LIMIT 5;</code></pre>
<p>즉, 다음 조건을 동시에 처리한다.</p>
<pre><code class="language-text">근로계약서이며
위험도가 높고
질문과 의미적으로 비슷한 조항</code></pre>
<p>JOIN과 사용자 권한 검사도 그대로 사용할 수 있다.</p>
<p>이것이 관계형 DB에서 벡터를 사용할 때 가장 큰 장점이다.</p>
<hr />
<h2 id="확장성">확장성</h2>
<p>새로운 벡터 데이터베이스를 바로 도입하지 않아도 된다.</p>
<pre><code class="language-text">기존 상품 테이블
+ 임베딩 컬럼
+ 벡터 인덱스
= 의미 기반 상품 추천</code></pre>
<p>따라서 다음 상황에 잘 맞는다.</p>
<pre><code class="language-text">벡터 검색이 서비스의 일부 기능인 경우
MVP에서 AI 기능을 빠르게 검증하는 경우
기존 업무 데이터와 임베딩의 관계가 중요한 경우</code></pre>
<hr />
<h1 id="유의할-점">유의할 점</h1>
<h2 id="기존-서비스와의-자원-경쟁">기존 서비스와의 자원 경쟁</h2>
<p>벡터는 일반적인 숫자나 문자열보다 훨씬 큰 데이터다.</p>
<p>예를 들어 <code>vector(1536)</code> 컬럼은 하나의 행마다 1536개의 실수 값을 저장한다.</p>
<pre><code class="language-text">일반 컬럼
→ ID, 상태, 날짜, 가격

벡터 컬럼
→ 수백~수천 차원의 실수 배열</code></pre>
<p>여기에 HNSW나 IVFFlat 같은 벡터 인덱스까지 생성하면 디스크 저장 공간뿐 아니라 메모리와 인덱스 관리 비용도 함께 증가한다.</p>
<pre><code class="language-text">원문 데이터
+ 임베딩 벡터
+ 벡터 인덱스
+ 기존 관계형 인덱스</code></pre>
<p>문제는 벡터 검색이 기존 SQL과 동일한 데이터베이스 자원을 사용한다는 점이다.</p>
<pre><code class="language-text">일반 트랜잭션
+ JOIN과 집계
+ 벡터 유사도 검색
+ 임베딩 대량 갱신
+ 벡터 인덱스 관리</code></pre>
<p>벡터 검색 요청이 많아지거나 대량의 임베딩을 갱신하면 CPU, 메모리, 디스크 I/O를 두고 기존 업무 쿼리와 경쟁하게 된다.</p>
<p>특히 임베딩 모델이 변경되면 기존 데이터도 새로운 모델로 다시 임베딩해야 한다.</p>
<pre><code class="language-text">임베딩 모델 변경
→ 전체 데이터 재임베딩
→ 벡터 컬럼 대량 갱신
→ 벡터 인덱스 재구성</code></pre>
<p>이 작업이 업무용 데이터베이스에서 수행되면 AI 검색 기능의 변경이 사용자 조회, 주문 처리, 데이터 수정과 같은 기존 서비스에도 영향을 줄 수 있다.</p>
<p>따라서 벡터 검색 규모가 커질수록 검색 속도뿐 아니라 <strong>기존 트랜잭션과 검색 워크로드를 같은 데이터베이스에서 처리해도 되는지</strong> 함께 고려해야 한다.</p>
<hr />
<h2 id="조건-검색은-rdbms만의-장점은-아니다">조건 검색은 RDBMS만의 장점은 아니다</h2>
<p>관계형 데이터베이스에서 벡터를 사용하는 직관적인 장점은 일반 조건과 의미 검색을 하나의 SQL로 결합할 수 있다는 것이다.</p>
<pre><code class="language-sql">SELECT
    clause_id,
    content
FROM contract_clauses
WHERE contract_type = '근로계약서'
  AND risk_level = 'HIGH'
ORDER BY embedding &lt;=&gt; :query_embedding
LIMIT 5;</code></pre>
<p>하지만 메타데이터 조건과 벡터 검색을 함께 사용하는 기능 자체가 관계형 데이터베이스에만 존재하는 것은 아니다.</p>
<p>Qdrant 같은 전용 벡터 데이터베이스도 벡터와 함께 <code>Payload</code>라는 메타데이터를 저장할 수 있다.</p>
<pre><code class="language-json">{
  &quot;contract_type&quot;: &quot;근로계약서&quot;,
  &quot;risk_level&quot;: &quot;HIGH&quot;,
  &quot;company_id&quot;: 10
}</code></pre>
<p>검색할 때 Payload 필터를 적용하면 다음과 같은 검색이 가능하다.</p>
<pre><code class="language-text">근로계약서이며
위험도가 높고
질문과 의미적으로 비슷한 조항</code></pre>
<pre><code class="language-text">PostgreSQL
→ WHERE 조건 + 벡터 검색

Qdrant
→ Payload 필터 + 벡터 검색</code></pre>
<p>따라서 카테고리, 사용자 ID, 위험 등급, 날짜 범위처럼 단순한 메타데이터 조건을 사용하기 위해 반드시 RDBMS에 벡터를 저장해야 하는 것은 아니다.</p>
<p>두 방식의 차이는 단순히 조건 검색의 가능 여부보다 <strong>데이터 관계와 정합성을 어느 수준까지 관리해야 하는가</strong>에 있다.</p>
<pre><code class="language-text">단순 메타데이터 필터
→ 전용 벡터 DB에서도 처리 가능

복잡한 JOIN, 외래 키, 트랜잭션, 권한 검사
→ 관계형 DB가 강함</code></pre>
<p>전용 벡터 DB의 Payload가 관계형 데이터베이스의 모든 기능을 대체하는 것은 아니다. 여러 테이블 사이의 관계, 외래 키, 복잡한 JOIN, 트랜잭션 기반 정합성이 중요하다면 RDBMS가 더 자연스러운 선택이 될 수 있다.</p>
<hr />
<h1 id="선택-기준">선택 기준</h1>
<p>pgvector와 전용 벡터 데이터베이스는 모두 의미 검색을 구현할 수 있다.</p>
<p>따라서 선택 기준은 벡터 검색의 가능 여부가 아니라, <strong>서비스에서 벡터 검색이 차지하는 역할</strong>이다.</p>
<table>
<thead>
<tr>
<th>기준</th>
<th>pgvector</th>
<th>전용 벡터 데이터베이스</th>
</tr>
</thead>
<tbody><tr>
<td>벡터 검색의 역할</td>
<td>기존 서비스의 일부 기능</td>
<td>서비스의 핵심 기능</td>
</tr>
<tr>
<td>데이터 구조</td>
<td>관계형 데이터와 밀접하게 연결</td>
<td>벡터와 메타데이터 중심</td>
</tr>
<tr>
<td>검색 조건</td>
<td>JOIN, 권한, 트랜잭션과 결합</td>
<td>Payload 기반 필터에 강함</td>
</tr>
<tr>
<td>운영 구조</td>
<td>기존 PostgreSQL에 통합</td>
<td>검색 워크로드를 별도로 운영</td>
</tr>
<tr>
<td>확장 방식</td>
<td>업무 DB와 함께 확장</td>
<td>벡터 검색을 독립적으로 확장</td>
</tr>
<tr>
<td>적합한 상황</td>
<td>MVP, 기존 서비스 기능 추가</td>
<td>대규모 검색, 높은 검색 트래픽</td>
</tr>
</tbody></table>
<p>기존 관계형 데이터베이스에 AI 검색 기능을 가볍게 추가하거나, 벡터 검색이 전체 서비스의 보조 기능이라면 pgvector가 좋은 선택이 될 수 있다.</p>
<pre><code class="language-text">기존 서비스에 의미 검색을 추가하는 경우
AI 기능의 가능성을 빠르게 검증하는 경우
원문과 임베딩을 하나의 트랜잭션으로 관리해야 하는 경우
복잡한 JOIN과 권한 검사가 중요한 경우</code></pre>
<p>반대로 검색 요청이 많아지고 벡터 검색 성능이 서비스 품질을 결정하기 시작한다면 검색 워크로드를 분리할 필요가 있다.</p>
<pre><code class="language-text">대규모 문서 검색이 핵심 기능인 경우
벡터 검색 트래픽이 지속적으로 증가하는 경우
임베딩과 인덱스를 독립적으로 확장해야 하는 경우
기존 업무 데이터베이스와 검색 부하를 분리해야 하는 경우</code></pre>
<p>이때는 전용 벡터 데이터베이스를 별도로 운영하는 편이 더 적합할 수 있다.</p>
<blockquote>
<p><strong>벡터 검색이 기존 서비스에 추가되는 기능인지, 아니면 서비스 자체를 구성하는 핵심 기능인지가 중요하다.</strong></p>
</blockquote>
<pre><code class="language-text">기존 데이터베이스의 탐색 기준에 의미를 추가한다
→ pgvector

의미 검색을 독립적인 워크로드로 운영하고 확장한다
→ 전용 벡터 데이터베이스</code></pre>