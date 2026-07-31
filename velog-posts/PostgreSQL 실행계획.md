<h2 id="sql-처리-과정부터-explain-analyze-스캔·조인·튜닝까지">SQL 처리 과정부터 EXPLAIN ANALYZE, 스캔·조인·튜닝까지</h2>
<p>SQL은 사용자가 원하는 결과를 선언하는 언어다.</p>
<p>사용자는 다음과 같이 작성한다.</p>
<pre><code class="language-sql">SELECT e.employee_id, e.full_name, d.department_name
FROM employees e
JOIN departments d
    ON d.department_id = e.department_id
WHERE e.salary &gt;= 5000;</code></pre>
<p>이 SQL은 다음 내용만 표현한다.</p>
<pre><code class="language-text">어떤 데이터를 원하는가?
어떤 테이블을 연결하는가?
어떤 조건을 적용하는가?</code></pre>
<p>하지만 다음 내용은 직접 지정하지 않는다.</p>
<pre><code class="language-text">어느 테이블부터 읽을 것인가?
전체 테이블을 읽을 것인가?
인덱스를 사용할 것인가?
어떤 조인 알고리즘을 사용할 것인가?
어느 조건을 먼저 적용할 것인가?
정렬은 메모리에서 처리할 것인가?
병렬 처리를 사용할 것인가?</code></pre>
<p>이러한 실행 방법은 DBMS의 옵티마이저가 결정한다.</p>
<pre><code class="language-text">SQL
→ 여러 실행 방법 탐색
→ 각 방법의 예상 비용 계산
→ 가장 비용이 낮다고 판단한 계획 선택
→ 실제 실행</code></pre>
<p>옵티마이저가 선택한 실행 방법을 <strong>실행계획(Query Plan 또는 Execution Plan)</strong>이라고 한다.</p>
<hr />
<h1 id="1-실행계획이란">1. 실행계획이란?</h1>
<p>실행계획은 DBMS가 SQL을 처리하기 위해 선택한 물리적 연산들의 트리다.</p>
<p>예를 들어 다음 SQL이 있다고 하자.</p>
<pre><code class="language-sql">SELECT *
FROM employees
WHERE employee_id = 100;</code></pre>
<p>DBMS는 다음과 같은 방법을 고려할 수 있다.</p>
<pre><code class="language-text">1. employees 테이블 전체를 순차적으로 읽는다.

2. employee_id 인덱스에서 100을 찾고
   해당 행이 저장된 위치로 이동한다.

3. 병렬로 테이블을 나누어 읽는다.

4. 인덱스에서 필요한 컬럼까지 얻어
   테이블 접근을 생략한다.</code></pre>
<p>어떤 방법이 항상 정답인 것은 아니다.</p>
<pre><code class="language-text">테이블 크기
조건을 만족하는 행 수
데이터 분포
인덱스 상태
메모리 크기
캐시 상태
디스크 접근 비용
병렬 처리 가능 여부</code></pre>
<p>에 따라 최적의 실행 방법은 달라진다.</p>
<p>따라서 실행계획을 보는 목적은 단순히 다음을 확인하는 것이 아니다.</p>
<pre><code class="language-text">인덱스를 사용했는가?</code></pre>
<p>더 중요한 질문은 다음과 같다.</p>
<pre><code class="language-text">PostgreSQL이 왜 이 계획을 선택했는가?
예상한 데이터 양과 실제 데이터 양이 일치하는가?
어느 노드에서 가장 많은 작업이 발생했는가?
더 적은 비용으로 같은 결과를 만들 수 있는가?</code></pre>
<hr />
<h1 id="2-논리적-계획과-물리적-계획">2. 논리적 계획과 물리적 계획</h1>
<p>SQL을 실행계획으로 변환할 때는 논리적인 연산과 물리적인 실행 방식을 구분해야 한다.</p>
<hr />
<h2 id="21-논리적-연산">2.1 논리적 연산</h2>
<p>논리적 연산은 SQL이 요구하는 관계형 연산이다.</p>
<pre><code class="language-text">테이블에서 조건에 맞는 행 선택
필요한 컬럼만 추출
두 테이블 결합
그룹별 집계
결과 정렬
중복 제거</code></pre>
<p>예를 들어 다음 SQL:</p>
<pre><code class="language-sql">SELECT department_id, COUNT(*)
FROM employees
WHERE salary &gt;= 5000
GROUP BY department_id;</code></pre>
<p>은 논리적으로 다음 과정을 요구한다.</p>
<pre><code class="language-text">employees에서 salary &gt;= 5000인 행 선택
→ department_id별 그룹화
→ 각 그룹의 행 수 계산</code></pre>
<hr />
<h2 id="22-물리적-연산">2.2 물리적 연산</h2>
<p>같은 논리적 연산도 여러 물리적 방법으로 수행할 수 있다.</p>
<p>조건 검색:</p>
<pre><code class="language-text">Sequential Scan
Index Scan
Index Only Scan
Bitmap Heap Scan
Parallel Sequential Scan</code></pre>
<p>조인:</p>
<pre><code class="language-text">Nested Loop Join
Hash Join
Merge Join</code></pre>
<p>집계:</p>
<pre><code class="language-text">HashAggregate
GroupAggregate
Plain Aggregate</code></pre>
<p>정렬:</p>
<pre><code class="language-text">메모리 Quicksort
Top-N Heapsort
Incremental Sort
디스크 External Merge</code></pre>
<p>옵티마이저는 가능한 물리적 연산의 조합을 평가하고 그중 비용이 가장 낮다고 예상되는 계획을 선택한다.</p>
<hr />
<h1 id="3-sql이-실행되기까지의-과정">3. SQL이 실행되기까지의 과정</h1>
<p>PostgreSQL에서 SQL은 대략 다음 단계를 거친다.</p>
<pre><code class="language-text">SQL 입력
  ↓
Parser
  ↓
Analyzer
  ↓
Rewriter
  ↓
Planner / Optimizer
  ↓
Executor
  ↓
결과 반환</code></pre>
<hr />
<h2 id="31-parser">3.1 Parser</h2>
<p>Parser는 SQL의 문법 구조를 분석한다.</p>
<pre><code class="language-sql">SELECT *
FROM employees
WHERE employee_id = 100;</code></pre>
<p>다음 내용을 구분한다.</p>
<pre><code class="language-text">SELECT 절
FROM 절
WHERE 절
연산자
상수
테이블명
컬럼명</code></pre>
<p>문법이 잘못되면 이 단계에서 오류가 발생한다.</p>
<hr />
<h2 id="32-analyzer">3.2 Analyzer</h2>
<p>Analyzer는 SQL에 등장한 객체와 자료형을 확인한다.</p>
<pre><code class="language-text">employees 테이블이 실제로 존재하는가?
employee_id 컬럼이 존재하는가?
비교되는 값의 자료형이 호환되는가?
사용자에게 접근 권한이 있는가?</code></pre>
<p>문자열로 작성한 테이블명과 컬럼명이 실제 데이터베이스 객체와 연결된다.</p>
<hr />
<h2 id="33-rewriter">3.3 Rewriter</h2>
<p>Rewriter는 규칙과 뷰 정의 등을 바탕으로 쿼리를 다시 작성할 수 있다.</p>
<p>예를 들어 View를 조회하면 View 정의가 실제 기반 테이블 쿼리로 확장될 수 있다.</p>
<pre><code class="language-text">View 조회
→ View 정의 전개
→ 기반 테이블을 대상으로 한 쿼리 생성</code></pre>
<hr />
<h2 id="34-planner와-optimizer">3.4 Planner와 Optimizer</h2>
<p>Planner는 실행 가능한 여러 계획을 탐색한다.</p>
<pre><code class="language-text">어느 테이블부터 읽을 것인가?
어떤 스캔 방식을 사용할 것인가?
어떤 순서로 조인할 것인가?
어떤 조인 알고리즘을 사용할 것인가?
정렬을 먼저 할 것인가?
병렬 처리를 사용할 것인가?</code></pre>
<p>Optimizer는 통계정보와 비용 모델을 이용하여 각 후보 계획의 비용을 계산한다.</p>
<pre><code class="language-text">후보 계획 A: 예상 비용 100
후보 계획 B: 예상 비용 350
후보 계획 C: 예상 비용 80</code></pre>
<p>이 경우 일반적으로 계획 C가 선택된다.</p>
<p>다만 비용은 실제 실행시간이 아니라 <strong>예측값</strong>이다.</p>
<p>통계정보가 부정확하면 가장 낮은 비용으로 선택한 계획이 실제로는 느릴 수 있다.</p>
<hr />
<h2 id="35-executor">3.5 Executor</h2>
<p>Executor는 선택된 실행계획의 노드를 실제로 수행한다.</p>
<pre><code class="language-text">테이블 읽기
인덱스 탐색
조건 검사
정렬
Hash Table 생성
조인
집계
결과 반환</code></pre>
<p>실행계획은 트리 구조이며, 하위 노드가 만든 결과를 상위 노드가 소비한다.</p>
<hr />
<h1 id="4-규칙-기반-최적화와-비용-기반-최적화">4. 규칙 기반 최적화와 비용 기반 최적화</h1>
<p>옵티마이저의 접근 방식은 크게 규칙 기반과 비용 기반으로 구분할 수 있다.</p>
<hr />
<h2 id="41-규칙-기반-최적화">4.1 규칙 기반 최적화</h2>
<p>미리 정의된 우선순위 규칙을 이용한다.</p>
<pre><code class="language-text">인덱스가 있으면 인덱스 사용
작은 테이블을 먼저 읽음
특정 조인 방식 우선</code></pre>
<p>구조는 단순하지만 데이터 분포와 실제 비용을 충분히 반영하기 어렵다.</p>
<hr />
<h2 id="42-비용-기반-최적화">4.2 비용 기반 최적화</h2>
<p>Cost-Based Optimizer는 여러 후보 계획의 예상 비용을 계산한다.</p>
<p>다음 정보를 활용한다.</p>
<pre><code class="language-text">테이블 행 수
테이블 페이지 수
컬럼 값 분포
NULL 비율
고유값 개수
자주 등장하는 값
인덱스 정보
정렬 여부
메모리 설정
CPU 연산 비용
디스크 페이지 접근 비용</code></pre>
<p>PostgreSQL은 비용 기반 옵티마이저를 사용한다.</p>
<p>따라서 인덱스가 존재하더라도 Sequential Scan의 비용이 더 낮다고 판단하면 인덱스를 사용하지 않는다.</p>
<hr />
<h1 id="5-실행계획-확인-명령">5. 실행계획 확인 명령</h1>
<p>PostgreSQL에서는 <code>EXPLAIN</code>과 <code>EXPLAIN ANALYZE</code>를 이용해 실행계획을 확인한다.</p>
<hr />
<h2 id="51-explain">5.1 EXPLAIN</h2>
<pre><code class="language-sql">EXPLAIN
SELECT *
FROM employees
WHERE employee_id = 100;</code></pre>
<p><code>EXPLAIN</code>은 SQL을 실제로 끝까지 실행하지 않고 옵티마이저가 선택한 예상 계획을 보여준다.</p>
<p>예:</p>
<pre><code class="language-text">Index Scan using employees_pkey on employees
  (cost=0.29..8.31 rows=1 width=50)
  Index Cond: (employee_id = 100)</code></pre>
<p>확인할 수 있는 내용:</p>
<pre><code class="language-text">선택된 실행 노드
예상 비용
예상 행 수
예상 행 크기
인덱스 조건
필터 조건
조인 방식</code></pre>
<p>그러나 실제 수행 결과는 알 수 없다.</p>
<pre><code class="language-text">실제 반환 행 수
실제 실행시간
실제 반복 횟수
실제 버퍼 사용량</code></pre>
<p>등은 표시되지 않는다.</p>
<hr />
<h2 id="52-explain-analyze">5.2 EXPLAIN ANALYZE</h2>
<pre><code class="language-sql">EXPLAIN ANALYZE
SELECT *
FROM employees
WHERE employee_id = 100;</code></pre>
<p><code>EXPLAIN ANALYZE</code>는 SQL을 실제로 실행하고 측정값을 추가한다.</p>
<p>예:</p>
<pre><code class="language-text">Index Scan using employees_pkey on employees
  (cost=0.29..8.31 rows=1 width=50)
  (actual time=0.021..0.024 rows=1 loops=1)
  Index Cond: (employee_id = 100)
Planning Time: 0.120 ms
Execution Time: 0.041 ms</code></pre>
<p>이를 통해 다음을 비교할 수 있다.</p>
<pre><code class="language-text">예상 행 수와 실제 행 수
예상 비용과 실제 소요시간
예상 반복 구조와 실제 반복 횟수</code></pre>
<hr />
<h2 id="53-데이터-변경-sql-주의">5.3 데이터 변경 SQL 주의</h2>
<p><code>EXPLAIN ANALYZE</code>는 실제로 SQL을 실행한다.</p>
<p>따라서 다음 명령에 사용하면 실제 데이터가 변경된다.</p>
<pre><code class="language-text">INSERT
UPDATE
DELETE
MERGE</code></pre>
<p>테스트 목적으로 실행할 때는 트랜잭션에서 수행한 뒤 롤백할 수 있다.</p>
<pre><code class="language-sql">BEGIN;

EXPLAIN ANALYZE
UPDATE employees
SET salary = salary + 100
WHERE department_id = 10;

ROLLBACK;</code></pre>
<p>단, Sequence 증가나 외부 함수 호출처럼 트랜잭션 롤백으로 완전히 복원되지 않는 부작용이 있을 수 있으므로 운영 환경에서는 주의해야 한다.</p>
<hr />
<h1 id="6-권장-explain-옵션">6. 권장 EXPLAIN 옵션</h1>
<p>실행계획을 분석할 때 다음 형태가 유용하다.</p>
<pre><code class="language-sql">EXPLAIN (
    ANALYZE,
    BUFFERS,
    TIMING OFF,
    SUMMARY
)
SELECT ...;</code></pre>
<hr />
<h2 id="61-analyze">6.1 ANALYZE</h2>
<p>실제로 쿼리를 실행하여 실제 행 수와 반복 횟수를 측정한다.</p>
<hr />
<h2 id="62-buffers">6.2 BUFFERS</h2>
<p>각 실행 노드가 사용한 데이터 페이지 정보를 보여준다.</p>
<pre><code class="language-text">shared hit
shared read
shared dirtied
shared written
temp read
temp written</code></pre>
<p>실행시간뿐 아니라 실제로 얼마나 많은 페이지를 읽었는지 분석할 수 있다.</p>
<hr />
<h2 id="63-timing-off">6.3 TIMING OFF</h2>
<p>각 노드의 세밀한 시간 측정을 비활성화한다.</p>
<p>실제 행 수와 반복 횟수, 전체 실행시간은 계속 측정한다.</p>
<p>각 행에 대한 시간 측정 오버헤드를 줄일 수 있어 대량 데이터를 처리하는 실행계획 비교에 유용하다.</p>
<p>세부 노드 시간이 필요하다면 <code>TIMING ON</code>을 사용한다.</p>
<hr />
<h2 id="64-summary">6.4 SUMMARY</h2>
<p>Planning Time과 Execution Time 등의 요약 정보를 출력한다.</p>
<p><code>ANALYZE</code>를 사용하면 일반적으로 요약 정보가 함께 표시된다.</p>
<hr />
<h2 id="65-verbose">6.5 VERBOSE</h2>
<p>다음과 같은 추가 정보를 표시한다.</p>
<pre><code class="language-text">출력 컬럼
스키마 이름
내부 별칭
표현식의 상세 구조</code></pre>
<pre><code class="language-sql">EXPLAIN (
    ANALYZE,
    BUFFERS,
    VERBOSE
)
SELECT ...;</code></pre>
<p>복잡한 View, 서브쿼리, 조인 결과의 실제 출력 구조를 확인할 때 유용하다.</p>
<hr />
<h2 id="66-wal">6.6 WAL</h2>
<p>데이터 변경 쿼리에서 생성된 WAL 관련 정보를 보여줄 수 있다.</p>
<pre><code class="language-sql">EXPLAIN (
    ANALYZE,
    BUFFERS,
    WAL
)
UPDATE ...;</code></pre>
<p>다음 정보를 확인하는 데 도움이 된다.</p>
<pre><code class="language-text">WAL Record 수
Full Page Image 수
생성된 WAL 바이트</code></pre>
<hr />
<h2 id="67-settings">6.7 SETTINGS</h2>
<p>현재 계획에 영향을 미친 설정값을 표시할 수 있다.</p>
<pre><code class="language-sql">EXPLAIN (
    ANALYZE,
    SETTINGS
)
SELECT ...;</code></pre>
<p>비기본값으로 변경된 Planner 설정을 확인할 때 유용하다.</p>
<hr />
<h2 id="68-format">6.8 FORMAT</h2>
<p>실행계획 출력 형식을 지정할 수 있다.</p>
<pre><code class="language-text">TEXT
JSON
XML
YAML</code></pre>
<p>예:</p>
<pre><code class="language-sql">EXPLAIN (
    ANALYZE,
    BUFFERS,
    FORMAT JSON
)
SELECT ...;</code></pre>
<p>자동화 도구나 시각화 도구에서 실행계획을 처리할 때 JSON 형식이 유용하다.</p>
<hr />
<h1 id="7-실행계획은-트리다">7. 실행계획은 트리다</h1>
<p>실행계획은 위에서 아래로 실행되는 명령 목록이 아니다.</p>
<p>하위 노드가 데이터를 생성하고 상위 노드가 그 결과를 받는 트리다.</p>
<p>예:</p>
<pre><code class="language-text">Hash Join
  Hash Cond: (e.department_id = d.department_id)
  → Seq Scan on employees e
  → Hash
       → Seq Scan on departments d</code></pre>
<p>실제 데이터 흐름은 다음과 같다.</p>
<pre><code class="language-text">departments Seq Scan
→ departments 데이터로 Hash Table 생성

employees Seq Scan
→ employees 행을 하나씩 읽음

각 employees 행의 department_id로 Hash Table 탐색
→ 일치하는 departments 행과 결합</code></pre>
<p>따라서 실행계획은 일반적으로 <strong>가장 안쪽에 들여쓰기 된 자식 노드부터 읽는다.</strong></p>
<pre><code class="language-text">자식 노드
→ 부모 노드
→ 최상위 노드
→ 사용자에게 결과 반환</code></pre>
<hr />
<h1 id="8-실행계획-읽는-기본-순서">8. 실행계획 읽는 기본 순서</h1>
<p>실행계획을 볼 때 다음 순서가 유용하다.</p>
<pre><code class="language-text">1. 최상위 노드가 무엇인지 확인한다.

2. 가장 깊은 자식 노드부터 읽는다.

3. 각 노드가 몇 행을 만들었는지 확인한다.

4. 예상 rows와 actual rows를 비교한다.

5. loops가 큰 노드를 찾는다.

6. Filter에서 많은 행이 제거되는지 확인한다.

7. Sort나 Hash가 디스크로 내려갔는지 확인한다.

8. Buffers에서 페이지 접근량을 확인한다.

9. 전체 Planning Time과 Execution Time을 확인한다.</code></pre>
<hr />
<h1 id="9-cost의-의미">9. cost의 의미</h1>
<p>다음 실행계획을 보자.</p>
<pre><code class="language-text">Index Scan using employees_pkey on employees
  (cost=0.29..8.31 rows=1 width=50)</code></pre>
<hr />
<h2 id="91-startup-cost">9.1 Startup Cost</h2>
<pre><code class="language-text">0.29</code></pre>
<p>첫 번째 결과 행을 반환하기 전까지 필요한 예상 비용이다.</p>
<p>다음 작업은 Startup Cost가 클 수 있다.</p>
<pre><code class="language-text">전체 정렬
Hash Table 생성
집계 준비
Materialize</code></pre>
<p>반면 인덱스에서 첫 행을 빠르게 찾을 수 있다면 Startup Cost가 낮을 수 있다.</p>
<p><code>LIMIT</code> 쿼리에서는 Startup Cost가 특히 중요하다.</p>
<pre><code class="language-sql">SELECT *
FROM orders
ORDER BY created_at DESC
LIMIT 10;</code></pre>
<p>모든 행을 처리하는 총비용보다 처음 10건을 얼마나 빨리 반환할 수 있는지가 중요하기 때문이다.</p>
<hr />
<h2 id="92-total-cost">9.2 Total Cost</h2>
<pre><code class="language-text">8.31</code></pre>
<p>해당 노드가 예상되는 모든 결과를 반환할 때까지의 총비용이다.</p>
<p>Total Cost에는 Startup Cost가 포함된다.</p>
<pre><code class="language-text">Startup Cost = 0.29
Total Cost   = 8.31</code></pre>
<p>이는 다음처럼 더하는 값이 아니다.</p>
<pre><code class="language-text">0.29 + 8.31</code></pre>
<p>전체 예상 비용은 <code>8.31</code>이다.</p>
<hr />
<h2 id="93-cost는-시간이-아니다">9.3 Cost는 시간이 아니다</h2>
<p>Cost는 밀리초가 아니다.</p>
<p>PostgreSQL 내부의 상대적인 비용 단위다.</p>
<p>다음 요소를 조합하여 계산한다.</p>
<pre><code class="language-text">순차 페이지 읽기
무작위 페이지 읽기
행 처리 CPU 비용
인덱스 엔트리 처리 비용
조건식 계산 비용
함수 실행 비용
정렬 비용
Hash 생성 비용</code></pre>
<p>따라서 다음 비교는 직접적으로 할 수 없다.</p>
<pre><code class="language-text">cost=100
→ 실행시간 100ms</code></pre>
<p>Cost는 후보 계획끼리 비교하기 위한 값이다.</p>
<hr />
<h2 id="94-rows">9.4 rows</h2>
<pre><code class="language-text">rows=1</code></pre>
<p>해당 노드가 반환할 것으로 옵티마이저가 예상한 행 수다.</p>
<p>이는 스캔한 행 수가 아니라 부모 노드로 전달할 것으로 예상한 행 수다.</p>
<pre><code class="language-text">테이블에서 100만 행 읽음
→ Filter로 999,999행 제거
→ rows=1</code></pre>
<p>일 수 있다.</p>
<hr />
<h2 id="95-width">9.5 width</h2>
<pre><code class="language-text">width=50</code></pre>
<p>한 행의 예상 평균 크기를 바이트 단위로 나타낸다.</p>
<p>Width는 다음 비용에 영향을 준다.</p>
<pre><code class="language-text">정렬 메모리
Hash Table 크기
Materialize 크기
네트워크 전송량
중간 결과 크기</code></pre>
<p>불필요한 컬럼을 많이 조회하면 중간 행의 Width가 커질 수 있다.</p>
<pre><code class="language-sql">SELECT *</code></pre>
<p>대신 필요한 컬럼만 조회하는 것이 실행 중 메모리와 데이터 이동 비용을 줄일 수 있다.</p>
<hr />
<h1 id="10-actual-time-rows-loops">10. actual time, rows, loops</h1>
<p><code>EXPLAIN ANALYZE</code>에서는 다음 정보가 추가된다.</p>
<pre><code class="language-text">(actual time=0.021..0.024 rows=1 loops=1)</code></pre>
<hr />
<h2 id="101-actual-time">10.1 actual time</h2>
<p>첫 번째 값:</p>
<pre><code class="language-text">0.021</code></pre>
<p>해당 노드가 첫 번째 행을 반환하기까지 걸린 평균 시간이다.</p>
<p>두 번째 값:</p>
<pre><code class="language-text">0.024</code></pre>
<p>해당 노드가 모든 행을 반환하기까지 걸린 평균 시간이다.</p>
<p>이 시간에는 일반적으로 자식 노드 수행시간도 포함된다.</p>
<p>따라서 부모 노드와 자식 노드의 시간을 단순히 전부 더하면 전체 실행시간보다 커질 수 있다.</p>
<hr />
<h2 id="102-actual-rows">10.2 actual rows</h2>
<pre><code class="language-text">rows=1</code></pre>
<p>한 번의 반복에서 해당 노드가 실제로 반환한 평균 행 수다.</p>
<p><code>loops</code>가 여러 번이면 전체 반환 행 수를 대략 다음처럼 판단할 수 있다.</p>
<pre><code class="language-text">actual rows × loops</code></pre>
<p>예:</p>
<pre><code class="language-text">rows=3 loops=100</code></pre>
<p>대략 300개의 행이 여러 반복에 걸쳐 반환된 것이다.</p>
<hr />
<h2 id="103-loops">10.3 loops</h2>
<pre><code class="language-text">loops=1</code></pre>
<p>해당 노드가 실행된 횟수다.</p>
<p>Nested Loop의 내부 노드는 외부 노드가 반환한 행 수만큼 반복될 수 있다.</p>
<pre><code class="language-text">Nested Loop
  → Seq Scan on departments
       rows=100 loops=1

  → Index Scan on employees
       rows=20 loops=100</code></pre>
<p>내부 Index Scan은 한 번에 평균 20행을 반환하고 총 100번 실행되었다.</p>
<p>대략적인 총 반환 행 수:</p>
<pre><code class="language-text">20 × 100 = 2,000</code></pre>
<p>한 번의 Index Scan이 빠르더라도 반복 횟수가 매우 크면 전체 비용이 커질 수 있다.</p>
<hr />
<h1 id="11-planning-time과-execution-time">11. Planning Time과 Execution Time</h1>
<p>실행계획의 마지막에는 다음 정보가 표시될 수 있다.</p>
<pre><code class="language-text">Planning Time: 1.200 ms
Execution Time: 35.500 ms</code></pre>
<hr />
<h2 id="111-planning-time">11.1 Planning Time</h2>
<p>SQL을 분석하고 실행계획을 선택하는 데 걸린 시간이다.</p>
<pre><code class="language-text">쿼리 분석
후보 계획 탐색
조인 순서 탐색
비용 계산
최종 계획 생성</code></pre>
<p>테이블과 조인이 많고 후보 계획이 복잡하면 Planning Time이 증가할 수 있다.</p>
<hr />
<h2 id="112-execution-time">11.2 Execution Time</h2>
<p>선택된 실행계획을 실제로 수행하는 데 걸린 전체 시간이다.</p>
<pre><code class="language-text">스캔
필터
조인
정렬
집계
결과 생성</code></pre>
<p>이 포함된다.</p>
<p>다만 클라이언트가 전체 결과를 네트워크로 전달받고 화면에 표시하는 시간과 완전히 같지는 않다.</p>
<hr />
<h1 id="12-예상-행-수와-실제-행-수">12. 예상 행 수와 실제 행 수</h1>
<p>실행계획 분석에서 가장 중요한 항목 중 하나는 다음 비교다.</p>
<pre><code class="language-text">estimated rows
vs
actual rows</code></pre>
<p>예:</p>
<pre><code class="language-text">예상 rows = 10
실제 rows = 100,000</code></pre>
<p>옵티마이저는 10행만 처리할 것으로 예상했지만 실제로는 10만 행을 처리했다.</p>
<p>이러한 추정 오류는 잘못된 실행계획 선택으로 이어질 수 있다.</p>
<hr />
<h2 id="121-추정-오류가-조인에-미치는-영향">12.1 추정 오류가 조인에 미치는 영향</h2>
<p>옵티마이저가 외부 결과를 한 행으로 예상하면 Nested Loop를 선택할 수 있다.</p>
<pre><code class="language-text">예상:
외부 1행
×
내부 Index Scan 1회</code></pre>
<p>하지만 실제 외부 결과가 10만 행이라면:</p>
<pre><code class="language-text">실제:
외부 100,000행
×
내부 Index Scan 100,000회</code></pre>
<p>가 된다.</p>
<p>Hash Join이 더 적합한 상황에서도 잘못된 행 수 추정으로 Nested Loop가 선택될 수 있다.</p>
<hr />
<h2 id="122-추정-오류의-대표-원인">12.2 추정 오류의 대표 원인</h2>
<pre><code class="language-text">통계정보가 오래됨
데이터가 특정 값에 집중됨
컬럼 간 강한 상관관계
복잡한 함수 또는 표현식
암시적 형변환
OR 조건
복잡한 서브쿼리
조인 컬럼의 분포 차이
준비된 문장의 일반 계획
테이블 값이 급격히 변경됨</code></pre>
<hr />
<h1 id="13-통계정보">13. 통계정보</h1>
<p>옵티마이저는 테이블 전체 데이터를 매번 직접 확인하지 않는다.</p>
<p>대신 <code>ANALYZE</code>가 수집한 통계정보를 사용한다.</p>
<p>대표적인 통계정보는 다음과 같다.</p>
<pre><code class="language-text">전체 행 수 추정
페이지 수
NULL 비율
고유값 개수
자주 등장하는 값
값의 분포 구간
물리적 저장 순서와 값 순서의 상관관계
평균 컬럼 크기</code></pre>
<p>PostgreSQL에서는 <code>pg_stats</code> View를 통해 일부 통계를 확인할 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM pg_stats
WHERE tablename = 'employees'
  AND attname = 'department_id';</code></pre>
<hr />
<h2 id="131-null_frac">13.1 null_frac</h2>
<p>컬럼 값 중 NULL이 차지하는 비율이다.</p>
<hr />
<h2 id="132-n_distinct">13.2 n_distinct</h2>
<p>서로 다른 값의 개수를 나타내는 통계다.</p>
<p>음수로 표시되면 전체 행 수에 대한 비율 형태의 추정값을 의미할 수 있다.</p>
<hr />
<h2 id="133-most_common_vals">13.3 most_common_vals</h2>
<p>가장 자주 등장하는 값들의 목록이다.</p>
<hr />
<h2 id="134-most_common_freqs">13.4 most_common_freqs</h2>
<p><code>most_common_vals</code>의 각 값이 등장하는 비율이다.</p>
<p>데이터가 특정 값에 몰려 있을 때 옵티마이저가 단순한 균등 분포 가정을 하지 않도록 돕는다.</p>
<hr />
<h2 id="135-histogram_bounds">13.5 histogram_bounds</h2>
<p>자주 등장하는 값을 제외한 나머지 값의 분포를 여러 구간으로 요약한 히스토그램이다.</p>
<p>범위 조건의 선택도를 추정하는 데 사용된다.</p>
<pre><code class="language-sql">WHERE salary BETWEEN 5000 AND 10000</code></pre>
<hr />
<h2 id="136-correlation">13.6 correlation</h2>
<p>컬럼 값의 정렬 순서와 테이블의 물리적 저장 순서가 얼마나 비슷한지를 나타낸다.</p>
<p>값이 1 또는 -1에 가까우면 인덱스 순서로 접근할 때 관련 Heap 페이지도 비교적 순차적으로 접근할 가능성이 높다.</p>
<p>0에 가까우면 값과 물리적 위치의 상관관계가 낮아 무작위 접근이 많아질 수 있다.</p>
<hr />
<h1 id="14-analyze">14. ANALYZE</h1>
<p>통계정보가 오래되었거나 부정확하다면 <code>ANALYZE</code>를 실행할 수 있다.</p>
<pre><code class="language-sql">ANALYZE employees;</code></pre>
<p>특정 컬럼의 통계 수집량을 늘릴 수도 있다.</p>
<pre><code class="language-sql">ALTER TABLE employees
ALTER COLUMN department_id
SET STATISTICS 1000;

ANALYZE employees;</code></pre>
<p>통계 수집량을 늘리면 더 많은 표본과 분포 정보를 저장할 수 있어 선택도 추정이 개선될 수 있다.</p>
<p>하지만 다음 비용도 증가한다.</p>
<pre><code class="language-text">ANALYZE 시간 증가
통계정보 저장량 증가
Planning Time 증가 가능</code></pre>
<p>따라서 무조건 최대값으로 높이는 것이 아니라 추정 오류가 중요한 컬럼에 선택적으로 적용해야 한다.</p>
<hr />
<h1 id="15-다중-컬럼-통계">15. 다중 컬럼 통계</h1>
<p>옵티마이저가 각 컬럼을 독립적이라고 가정하면 실제 결과를 크게 잘못 추정할 수 있다.</p>
<p>예를 들어 다음 두 컬럼이 강하게 연결되어 있다고 하자.</p>
<pre><code class="language-text">country = 'KR'
city = 'Seoul'</code></pre>
<p>각 조건을 별도로 계산해 곱하면 실제 분포와 크게 달라질 수 있다.</p>
<pre><code class="language-sql">WHERE country = 'KR'
  AND city = 'Seoul'</code></pre>
<p>PostgreSQL에서는 Extended Statistics를 이용해 여러 컬럼의 관계를 수집할 수 있다.</p>
<pre><code class="language-sql">CREATE STATISTICS st_customer_location
ON country, city
FROM customers;

ANALYZE customers;</code></pre>
<p>수집 가능한 통계의 예:</p>
<pre><code class="language-text">Dependencies
→ 컬럼 사이의 함수적 의존 관계

NDistinct
→ 컬럼 조합의 고유값 개수

MCV
→ 여러 컬럼 조합에서 자주 등장하는 값</code></pre>
<p>다중 컬럼 조건의 행 수 추정이 크게 틀릴 때 검토할 수 있다.</p>
<hr />
<h1 id="16-sequential-scan">16. Sequential Scan</h1>
<p>Sequential Scan은 테이블의 페이지를 처음부터 끝까지 순차적으로 읽는다.</p>
<p>실행계획:</p>
<pre><code class="language-text">Seq Scan on employees</code></pre>
<p>조건이 있으면 다음과 같이 표시된다.</p>
<pre><code class="language-text">Seq Scan on employees
  Filter: (salary &gt;= 5000)</code></pre>
<hr />
<h2 id="161-seq-scan이-적합한-경우">16.1 Seq Scan이 적합한 경우</h2>
<pre><code class="language-text">테이블이 작음
조회 대상이 전체에서 차지하는 비율이 큼
적절한 인덱스가 없음
대부분의 페이지를 읽어야 함
순차 I/O가 무작위 I/O보다 효율적임</code></pre>
<p>예를 들어 전체 행의 90%를 조회해야 한다면 인덱스로 각 행의 위치를 찾아가는 것보다 테이블을 한 번 순차적으로 읽는 것이 빠를 수 있다.</p>
<hr />
<h2 id="162-seq-scan은-항상-나쁜가">16.2 Seq Scan은 항상 나쁜가?</h2>
<p>그렇지 않다.</p>
<pre><code class="language-text">Seq Scan = 무조건 나쁨</code></pre>
<p>은 잘못된 판단이다.</p>
<p>작은 코드 테이블을 읽는 경우:</p>
<pre><code class="language-text">Seq Scan으로 2페이지 읽기</code></pre>
<p>가 인덱스 탐색과 Heap 접근보다 빠를 수 있다.</p>
<p>중요한 것은 노드 이름이 아니라 다음 정보다.</p>
<pre><code class="language-text">테이블 크기
실제 반환 행 수
읽은 페이지 수
필터 제거 행 수
반복 횟수
전체 실행시간</code></pre>
<hr />
<h1 id="17-parallel-sequential-scan">17. Parallel Sequential Scan</h1>
<p>대용량 테이블은 여러 Worker가 나누어 읽을 수 있다.</p>
<pre><code class="language-text">Gather
  Workers Planned: 2
  Workers Launched: 2
  → Parallel Seq Scan on large_table</code></pre>
<p>동작:</p>
<pre><code class="language-text">Leader와 Worker가 테이블 블록을 나누어 읽음
→ 각 프로세스가 조건 검사
→ Gather가 결과를 모음</code></pre>
<p>확인할 항목:</p>
<pre><code class="language-text">Workers Planned
Workers Launched
각 Worker의 실제 행 수
병렬 처리 시작 비용
Gather 병목</code></pre>
<p>병렬 처리는 항상 빠른 것은 아니다.</p>
<pre><code class="language-text">테이블이 작음
결과가 매우 적음
병렬 프로세스 시작 비용이 큼
Leader가 결과를 모으는 비용이 큼</code></pre>
<p>인 경우 단일 프로세스가 더 효율적일 수 있다.</p>
<hr />
<h1 id="18-index-scan">18. Index Scan</h1>
<p>Index Scan은 인덱스에서 조건에 맞는 행의 위치를 찾고 해당 Heap 페이지로 이동한다.</p>
<pre><code class="language-text">Index Scan using idx_employees_department
  on employees</code></pre>
<p>동작:</p>
<pre><code class="language-text">인덱스 탐색
→ 행 위치 확인
→ Heap 페이지 접근
→ MVCC 가시성 확인
→ 행 반환</code></pre>
<hr />
<h2 id="181-index-cond">18.1 Index Cond</h2>
<pre><code class="language-text">Index Cond: (department_id = 10)</code></pre>
<p>인덱스 탐색 단계에서 사용된 조건이다.</p>
<p>인덱스 검색 범위를 직접 좁힌다.</p>
<hr />
<h2 id="182-filter">18.2 Filter</h2>
<pre><code class="language-text">Filter: (salary &gt;= 5000)</code></pre>
<p>인덱스에서 후보 행을 찾고 Heap 행을 읽은 뒤 적용한 조건이다.</p>
<p>예:</p>
<pre><code class="language-text">Index Cond: (department_id = 10)
Filter: (salary &gt;= 5000)</code></pre>
<p>처리:</p>
<pre><code class="language-text">department_id = 10인 인덱스 범위 탐색
→ 해당 행을 Heap에서 읽음
→ salary &gt;= 5000인지 검사</code></pre>
<p><code>Filter</code>에서 많은 행이 제거된다면 복합 인덱스나 부분 인덱스, SQL 조건 재구성을 검토할 수 있다.</p>
<p>다만 Filter가 존재한다고 무조건 문제가 있는 것은 아니다.</p>
<hr />
<h2 id="183-index-scan이-비효율적일-수-있는-경우">18.3 Index Scan이 비효율적일 수 있는 경우</h2>
<p>조회 행이 많고 데이터가 여러 Heap 페이지에 흩어져 있다면 무작위 페이지 접근이 증가한다.</p>
<pre><code class="language-text">인덱스에서 TID 확인
→ Heap Page 10
→ Heap Page 915
→ Heap Page 42
→ Heap Page 700</code></pre>
<p>이 경우 Sequential Scan이나 Bitmap Scan이 더 효율적일 수 있다.</p>
<hr />
<h1 id="19-index-only-scan">19. Index Only Scan</h1>
<p>Index Only Scan은 필요한 컬럼을 인덱스에서 모두 얻을 수 있을 때 사용될 수 있다.</p>
<pre><code class="language-text">Index Only Scan using idx_employees_department_cover
  on employees</code></pre>
<p>필요 조건:</p>
<pre><code class="language-text">검색 조건에 필요한 컬럼이 인덱스에 있음
결과 반환에 필요한 컬럼도 인덱스에 있음
인덱스 접근 방식이 Index Only Scan을 지원함</code></pre>
<hr />
<h2 id="191-mvcc-가시성-확인">19.1 MVCC 가시성 확인</h2>
<p>PostgreSQL에서는 인덱스 엔트리만 보고 행의 가시성을 항상 판단할 수 있는 것은 아니다.</p>
<p>따라서 Heap 페이지가 Visibility Map에서 <code>all-visible</code>로 표시되어 있지 않으면 Heap을 확인해야 한다.</p>
<pre><code class="language-text">Index Only Scan
  Heap Fetches: 120</code></pre>
<p><code>Heap Fetches</code>가 많다면 실행계획 이름은 Index Only Scan이지만 실제 Heap 접근이 많이 발생한 것이다.</p>
<p>이상적인 형태:</p>
<pre><code class="language-text">Heap Fetches: 0</code></pre>
<p>VACUUM이 적절히 수행되어 Visibility Map이 관리되면 Heap Fetches를 줄일 수 있다.</p>
<hr />
<h1 id="20-bitmap-index-scan과-bitmap-heap-scan">20. Bitmap Index Scan과 Bitmap Heap Scan</h1>
<p>Bitmap Scan은 조회 결과가 적지도 많지도 않은 중간 영역에서 유리할 수 있다.</p>
<p>실행계획:</p>
<pre><code class="language-text">Bitmap Heap Scan on employees
  Recheck Cond: (department_id = 10)
  → Bitmap Index Scan on idx_employees_department
       Index Cond: (department_id = 10)</code></pre>
<p>동작:</p>
<pre><code class="language-text">1. 인덱스에서 조건에 맞는 TID 수집

2. TID를 Bitmap으로 구성

3. Heap 페이지 번호 기준으로 정리

4. 같은 페이지의 행을 묶어서 읽음

5. 필요한 경우 조건 재검사</code></pre>
<p>일반 Index Scan보다 Heap 페이지에 대한 무작위 접근을 줄일 수 있다.</p>
<hr />
<h2 id="201-bitmapand와-bitmapor">20.1 BitmapAnd와 BitmapOr</h2>
<p>여러 인덱스 결과를 결합할 수도 있다.</p>
<pre><code class="language-text">BitmapAnd
  → Bitmap Index Scan on idx_users_region
  → Bitmap Index Scan on idx_users_grade</code></pre>
<pre><code class="language-text">BitmapOr
  → Bitmap Index Scan on idx_orders_paid
  → Bitmap Index Scan on idx_orders_pending</code></pre>
<p>이를 통해 하나의 복합 인덱스가 없어도 여러 단일 인덱스의 결과를 결합할 수 있다.</p>
<p>하지만 항상 복합 인덱스보다 효율적인 것은 아니다.</p>
<hr />
<h2 id="202-exact-bitmap과-lossy-bitmap">20.2 Exact Bitmap과 Lossy Bitmap</h2>
<p>메모리가 충분하면 각 행 위치를 정확하게 저장할 수 있다.</p>
<pre><code class="language-text">Exact Bitmap
→ 정확한 TID 저장</code></pre>
<p>메모리가 부족하면 페이지 단위 정보만 저장할 수 있다.</p>
<pre><code class="language-text">Lossy Bitmap
→ 이 페이지에 후보 행이 있다는 것만 저장</code></pre>
<p>Lossy Bitmap에서는 페이지의 행을 다시 확인해야 한다.</p>
<p>실행계획에 다음 정보가 나타날 수 있다.</p>
<pre><code class="language-text">Heap Blocks: exact=100 lossy=50
Rows Removed by Index Recheck: 1000</code></pre>
<p><code>work_mem</code>이 너무 작거나 후보 행이 지나치게 많을 때 Lossy Bitmap이 증가할 수 있다.</p>
<hr />
<h1 id="21-tid-scan">21. TID Scan</h1>
<p>TID Scan은 행의 물리적 위치를 직접 지정했을 때 사용할 수 있는 특수한 스캔이다.</p>
<pre><code class="language-sql">SELECT *
FROM employees
WHERE ctid = '(10,3)';</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Tid Scan on employees</code></pre>
<p>일반적인 업무 SQL에서 자주 사용할 방식은 아니다.</p>
<p><code>ctid</code>는 행이 갱신되거나 테이블이 재작성되면 변경될 수 있으므로 영구적인 식별자로 사용하면 안 된다.</p>
<hr />
<h1 id="22-조인의-논리와-물리">22. 조인의 논리와 물리</h1>
<p>다음은 논리적 조인 종류다.</p>
<pre><code class="language-text">INNER JOIN
LEFT OUTER JOIN
RIGHT OUTER JOIN
FULL OUTER JOIN
SEMI JOIN
ANTI JOIN</code></pre>
<p>다음은 물리적 조인 알고리즘이다.</p>
<pre><code class="language-text">Nested Loop
Hash Join
Merge Join</code></pre>
<p>둘은 서로 다른 분류다.</p>
<pre><code class="language-text">LEFT JOIN
→ 왼쪽 행을 모두 유지한다는 논리적 의미

Hash Join
→ 실제 행을 매칭하는 물리적 알고리즘</code></pre>
<p>따라서 다음과 같은 실행계획이 모두 가능하다.</p>
<pre><code class="language-text">Nested Loop Left Join
Hash Left Join
Merge Left Join</code></pre>
<hr />
<h1 id="23-nested-loop-join">23. Nested Loop Join</h1>
<p>Nested Loop는 외부 입력의 각 행마다 내부 입력을 반복 탐색한다.</p>
<p>개념:</p>
<pre><code class="language-text">for each outer_row:
    inner에서 일치하는 행 탐색</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Nested Loop
  → Seq Scan on departments d
  → Index Scan on employees e
       Index Cond: (department_id = d.department_id)</code></pre>
<hr />
<h2 id="231-적합한-상황">23.1 적합한 상황</h2>
<pre><code class="language-text">외부 결과 행 수가 적음
내부 테이블에 적절한 인덱스가 있음
내부에서 일치하는 행이 적음
LIMIT으로 빠르게 소수 결과만 필요함</code></pre>
<p>예:</p>
<pre><code class="language-text">부서 3개
×
부서별 employees 인덱스 검색 3회</code></pre>
<hr />
<h2 id="232-위험-신호">23.2 위험 신호</h2>
<pre><code class="language-text">외부 결과 행 수가 예상보다 많음
내부 노드 loops가 매우 큼
내부 인덱스 탐색이 수만~수백만 번 반복됨</code></pre>
<p>예:</p>
<pre><code class="language-text">Index Scan
  actual rows=1 loops=500000</code></pre>
<p>한 번의 인덱스 탐색은 빠르더라도 50만 번 수행하면 전체 비용이 커진다.</p>
<hr />
<h2 id="233-materialize와-nested-loop">23.3 Materialize와 Nested Loop</h2>
<p>내부 결과가 반복적으로 필요하지만 매번 다시 계산할 필요가 없다면 Materialize가 나타날 수 있다.</p>
<pre><code class="language-text">Nested Loop
  → Seq Scan on outer_table
  → Materialize
       → Seq Scan on small_inner_table</code></pre>
<p>Materialize는 자식 결과를 저장해 이후 반복에서 다시 사용한다.</p>
<hr />
<h2 id="234-memoize">23.4 Memoize</h2>
<p>같은 파라미터를 이용한 내부 조회가 반복되는 경우 Memoize가 사용될 수 있다.</p>
<pre><code class="language-text">Nested Loop
  → Seq Scan on orders
  → Memoize
       Cache Key: orders.customer_id
       → Index Scan on customers</code></pre>
<p>같은 <code>customer_id</code>가 반복되면 이전 조회 결과를 캐시에서 재사용할 수 있다.</p>
<p>확인할 항목:</p>
<pre><code class="language-text">Cache Hits
Cache Misses
Evictions
Memory Usage</code></pre>
<hr />
<h1 id="24-hash-join">24. Hash Join</h1>
<p>Hash Join은 한쪽 입력으로 Hash Table을 만들고 다른 쪽 입력의 조인 키로 Hash Table을 탐색한다.</p>
<p>실행계획:</p>
<pre><code class="language-text">Hash Join
  Hash Cond: (e.department_id = d.department_id)
  → Seq Scan on employees e
  → Hash
       → Seq Scan on departments d</code></pre>
<p>동작:</p>
<pre><code class="language-text">1. 일반적으로 작은 쪽 입력을 읽음

2. 조인 키를 기준으로 Hash Table 생성

3. 다른 입력을 순서대로 읽음

4. 각 행의 조인 키로 Hash Table 탐색

5. 일치하는 행 결합</code></pre>
<hr />
<h2 id="241-적합한-상황">24.1 적합한 상황</h2>
<pre><code class="language-text">동등 조인
대량 데이터 조인
Hash Table을 만들 입력이 비교적 작음
양쪽 입력이 정렬되어 있지 않음</code></pre>
<p>Hash Join은 일반적으로 다음 조건에 사용된다.</p>
<pre><code class="language-sql">ON a.key = b.key</code></pre>
<p>부등호 조인에는 일반적으로 사용할 수 없다.</p>
<hr />
<h2 id="242-확인할-정보">24.2 확인할 정보</h2>
<pre><code class="language-text">Buckets
Batches
Memory Usage</code></pre>
<p>예:</p>
<pre><code class="language-text">Hash
  Buckets: 65536
  Batches: 1
  Memory Usage: 2048kB</code></pre>
<p><code>Batches: 1</code>이면 Hash Table이 한 번에 메모리에서 처리되었다는 의미다.</p>
<p>메모리가 부족하면:</p>
<pre><code class="language-text">Batches: 8</code></pre>
<p>처럼 여러 Batch로 나뉠 수 있다.</p>
<p>이 경우 임시 디스크 I/O가 발생하고 성능이 크게 저하될 수 있다.</p>
<hr />
<h2 id="243-hash-join의-startup-cost">24.3 Hash Join의 Startup Cost</h2>
<p>Hash Join은 Probe 입력을 처리하기 전에 Build 입력으로 Hash Table을 만들어야 한다.</p>
<pre><code class="language-text">Build Side 전체 읽기
→ Hash Table 생성
→ 첫 조인 결과 반환</code></pre>
<p>따라서 Nested Loop보다 Startup Cost가 클 수 있다.</p>
<p>하지만 대량 데이터 전체를 처리할 때는 효율적일 수 있다.</p>
<hr />
<h1 id="25-merge-join">25. Merge Join</h1>
<p>Merge Join은 양쪽 입력을 조인 키 순서로 정렬한 뒤 함께 이동하면서 결합한다.</p>
<p>실행계획:</p>
<pre><code class="language-text">Merge Join
  Merge Cond: (a.key = b.key)
  → Sort
       Sort Key: a.key
       → Seq Scan on a
  → Sort
       Sort Key: b.key
       → Seq Scan on b</code></pre>
<p>동작:</p>
<pre><code class="language-text">왼쪽 입력 포인터
오른쪽 입력 포인터

두 키 비교
→ 같으면 결합
→ 작은 쪽 포인터 이동
→ 입력이 끝날 때까지 반복</code></pre>
<hr />
<h2 id="251-적합한-상황">25.1 적합한 상황</h2>
<pre><code class="language-text">양쪽 입력이 이미 조인 키 순서로 정렬됨
대량 데이터 조인
정렬된 결과가 이후에도 필요함
범위 성격의 조인 조건</code></pre>
<p>인덱스를 통해 이미 정렬된 순서로 데이터를 읽을 수 있다면 별도의 Sort를 생략할 수 있다.</p>
<hr />
<h2 id="252-주의점">25.2 주의점</h2>
<p>정렬이 필요하면 정렬 비용이 추가된다.</p>
<pre><code class="language-text">대량 Sort
→ work_mem 초과
→ 임시 디스크 사용
→ 성능 저하</code></pre>
<p>Merge Join 자체보다 입력 정렬이 병목이 될 수 있다.</p>
<hr />
<h1 id="26-join-filter와-rows-removed-by-join-filter">26. Join Filter와 Rows Removed by Join Filter</h1>
<p>실행계획에서 다음과 같이 나타날 수 있다.</p>
<pre><code class="language-text">Hash Join
  Hash Cond: (a.id = b.id)
  Join Filter: (a.created_at &lt; b.expired_at)
  Rows Removed by Join Filter: 100000</code></pre>
<p><code>Hash Cond</code>는 Hash Table 탐색에 사용된 조건이다.</p>
<p><code>Join Filter</code>는 조인 후보를 만든 뒤 추가로 적용한 조건이다.</p>
<pre><code class="language-text">Hash Cond로 후보 결합
→ Join Filter 검사
→ 조건을 만족하지 않으면 제거</code></pre>
<p><code>Rows Removed by Join Filter</code>가 매우 크다면 다음을 검토할 수 있다.</p>
<pre><code class="language-text">더 적합한 조인 조건이 있는가?
조인 전에 데이터를 줄일 수 있는가?
조건을 더 이른 단계에 적용할 수 있는가?
잘못된 조인으로 중간 결과가 폭증하는가?</code></pre>
<hr />
<h1 id="27-semi-join">27. Semi Join</h1>
<p>Semi Join은 왼쪽 행에 대해 오른쪽에 일치하는 행이 존재하는지만 확인한다.</p>
<p>대표적인 SQL:</p>
<pre><code class="language-sql">SELECT *
FROM employees e
WHERE EXISTS (
    SELECT 1
    FROM employee_training t
    WHERE t.employee_id = e.employee_id
);</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Hash Semi Join
Nested Loop Semi Join
Merge Semi Join</code></pre>
<p>오른쪽의 모든 일치 행을 반환할 필요가 없다.</p>
<pre><code class="language-text">첫 번째 일치 확인
→ 왼쪽 행 반환
→ 추가 오른쪽 행 탐색 불필요</code></pre>
<hr />
<h1 id="28-anti-join">28. Anti Join</h1>
<p>Anti Join은 왼쪽 행에 대해 오른쪽에 일치하는 행이 없는 경우만 반환한다.</p>
<p>대표적인 SQL:</p>
<pre><code class="language-sql">SELECT *
FROM employees e
WHERE NOT EXISTS (
    SELECT 1
    FROM employee_training t
    WHERE t.employee_id = e.employee_id
      AND t.completion_status = 'COMPLETED'
);</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Hash Anti Join
Nested Loop Anti Join
Merge Anti Join</code></pre>
<p>다음 SQL도 Anti Join으로 최적화될 수 있다.</p>
<pre><code class="language-sql">SELECT e.*
FROM employees e
LEFT JOIN employee_training t
    ON t.employee_id = e.employee_id
   AND t.completion_status = 'COMPLETED'
WHERE t.employee_id IS NULL;</code></pre>
<hr />
<h1 id="29-not-in과-null">29. NOT IN과 NULL</h1>
<p>다음 쿼리는 주의해야 한다.</p>
<pre><code class="language-sql">SELECT e.*
FROM employees e
WHERE e.employee_id NOT IN (
    SELECT t.employee_id
    FROM employee_training t
);</code></pre>
<p>서브쿼리 결과에 NULL이 포함되면 비교 결과가 UNKNOWN이 될 수 있다.</p>
<pre><code class="language-text">3 NOT IN (1, 2, NULL)

=
3 &lt;&gt; 1
AND 3 &lt;&gt; 2
AND 3 &lt;&gt; NULL

=
TRUE AND TRUE AND UNKNOWN

=
UNKNOWN</code></pre>
<p>WHERE 절은 TRUE인 행만 반환하므로 결과가 예상과 달라질 수 있다.</p>
<p>안티 조인을 표현하려는 경우 일반적으로 <code>NOT EXISTS</code>가 의미적으로 더 안전하고 명확하다.</p>
<hr />
<h1 id="30-sort-노드">30. Sort 노드</h1>
<p>정렬이 필요하면 <code>Sort</code> 노드가 나타난다.</p>
<pre><code class="language-text">Sort
  Sort Key: salary DESC
  → Seq Scan on employees</code></pre>
<p>확인할 항목:</p>
<pre><code class="language-text">Sort Key
Sort Method
Memory
Disk
실제 행 수</code></pre>
<hr />
<h2 id="301-quicksort">30.1 Quicksort</h2>
<pre><code class="language-text">Sort Method: quicksort
Memory: 2048kB</code></pre>
<p>전체 정렬이 메모리 안에서 처리되었다.</p>
<hr />
<h2 id="302-top-n-heapsort">30.2 Top-N Heapsort</h2>
<pre><code class="language-text">Sort Method: top-N heapsort</code></pre>
<p>다음과 같이 정렬 후 일부 행만 필요한 경우 사용할 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM employees
ORDER BY salary DESC
LIMIT 10;</code></pre>
<p>전체 결과를 완전히 정렬하지 않고 상위 N개를 유지한다.</p>
<hr />
<h2 id="303-external-merge">30.3 External Merge</h2>
<pre><code class="language-text">Sort Method: external merge
Disk: 200MB</code></pre>
<p>정렬 데이터가 허용된 메모리를 초과해 임시 디스크 파일을 사용한 것이다.</p>
<p>성능 저하의 중요한 단서다.</p>
<p>검토할 항목:</p>
<pre><code class="language-text">정렬 대상 행을 먼저 줄일 수 있는가?
불필요한 컬럼을 제거할 수 있는가?
ORDER BY를 지원하는 인덱스가 있는가?
work_mem이 지나치게 작은가?
행 수 추정이 잘못되었는가?</code></pre>
<hr />
<h2 id="304-incremental-sort">30.4 Incremental Sort</h2>
<p>입력 데이터가 정렬 키의 앞부분에 대해서 이미 정렬되어 있다면 Incremental Sort를 사용할 수 있다.</p>
<pre><code class="language-text">Incremental Sort
  Sort Key: department_id, salary
  Presorted Key: department_id</code></pre>
<p>입력은 <code>department_id</code> 순서로 정렬되어 있으므로 각 부서 그룹 안에서 <code>salary</code>만 추가로 정렬한다.</p>
<p>전체 데이터를 처음부터 정렬하는 것보다 메모리와 연산량을 줄일 수 있다.</p>
<hr />
<h1 id="31-work_mem-주의">31. work_mem 주의</h1>
<p><code>work_mem</code>은 정렬과 Hash 연산에 사용할 수 있는 메모리 크기에 영향을 준다.</p>
<p>하지만 다음처럼 이해하면 안 된다.</p>
<pre><code class="language-text">쿼리 하나당 work_mem 한 번 사용</code></pre>
<p>하나의 쿼리에 여러 Sort와 Hash 노드가 있으면 각 노드가 별도로 메모리를 사용할 수 있다.</p>
<p>병렬 Worker도 각자 메모리를 사용할 수 있다.</p>
<pre><code class="language-text">Sort 3개
+
Hash 2개
+
Worker 4개</code></pre>
<p>인 경우 전체 메모리 사용량이 크게 증가할 수 있다.</p>
<p>따라서 디스크 Spill이 보인다는 이유만으로 전역 <code>work_mem</code>을 과도하게 높이면 동시 요청이 많은 환경에서 메모리 부족이 발생할 수 있다.</p>
<hr />
<h1 id="32-aggregate-노드">32. Aggregate 노드</h1>
<p>집계는 데이터 형태와 그룹 수에 따라 여러 방식으로 실행된다.</p>
<hr />
<h2 id="321-plain-aggregate">32.1 Plain Aggregate</h2>
<p>그룹이 없는 전체 집계에 사용될 수 있다.</p>
<pre><code class="language-sql">SELECT COUNT(*)
FROM employees;</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Aggregate
  → Seq Scan on employees</code></pre>
<p>하나의 최종 집계 결과를 만든다.</p>
<hr />
<h2 id="322-hashaggregate">32.2 HashAggregate</h2>
<p>그룹 키를 Hash Table에 저장하여 집계한다.</p>
<pre><code class="language-text">HashAggregate
  Group Key: department_id
  → Seq Scan on employees</code></pre>
<p>개념:</p>
<pre><code class="language-text">department_id를 Hash Key로 사용
→ 그룹별 집계 상태 저장
→ 입력 행을 해당 그룹에 누적</code></pre>
<p>장점:</p>
<pre><code class="language-text">입력 정렬이 필요하지 않음</code></pre>
<p>주의점:</p>
<pre><code class="language-text">그룹 수가 많음
행이 큼
메모리 부족</code></pre>
<p>인 경우 여러 Batch와 임시 디스크 사용이 발생할 수 있다.</p>
<pre><code class="language-text">Batches: 8
Memory Usage: ...
Disk Usage: ...</code></pre>
<hr />
<h2 id="323-groupaggregate">32.3 GroupAggregate</h2>
<p>입력이 그룹 키 순서로 정렬되어 있을 때 연속된 행을 집계한다.</p>
<pre><code class="language-text">GroupAggregate
  Group Key: department_id
  → Sort
       Sort Key: department_id
       → Seq Scan on employees</code></pre>
<p>입력이 이미 인덱스나 Merge Append를 통해 정렬되어 있다면 별도 Sort가 필요하지 않을 수 있다.</p>
<hr />
<h2 id="324-partial-aggregate와-finalize-aggregate">32.4 Partial Aggregate와 Finalize Aggregate</h2>
<p>병렬 집계에서는 각 Worker가 일부 집계를 수행하고 Leader가 최종 결과를 결합할 수 있다.</p>
<pre><code class="language-text">Finalize Aggregate
  → Gather
       → Partial Aggregate
            → Parallel Seq Scan</code></pre>
<p>동작:</p>
<pre><code class="language-text">각 Worker
→ 자신의 데이터 범위에서 부분 집계

Gather
→ 부분 결과 수집

Finalize Aggregate
→ 최종 합계 계산</code></pre>
<hr />
<h1 id="33-windowagg">33. WindowAgg</h1>
<p>Window Function을 사용하면 <code>WindowAgg</code> 노드가 나타날 수 있다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    department_id,
    salary,
    RANK() OVER (
        PARTITION BY department_id
        ORDER BY salary DESC
    )
FROM employees;</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">WindowAgg
  → Sort
       Sort Key: department_id, salary DESC
       → Seq Scan on employees</code></pre>
<p>Window Function은 행을 그룹당 한 행으로 줄이지 않는다.</p>
<pre><code class="language-text">GROUP BY
→ 여러 행을 그룹별 한 행으로 축소

Window Function
→ 원래 행을 유지하며 계산 결과 추가</code></pre>
<p>정렬이 필요한 Window 정의가 여러 개라면 여러 Sort가 발생할 수 있다.</p>
<hr />
<h1 id="34-unique-노드">34. Unique 노드</h1>
<p>중복 제거가 필요한 경우 <code>Unique</code> 노드가 나타날 수 있다.</p>
<pre><code class="language-sql">SELECT DISTINCT department_id
FROM employees;</code></pre>
<p>가능한 실행계획:</p>
<pre><code class="language-text">Unique
  → Sort
       Sort Key: department_id
       → Seq Scan on employees</code></pre>
<p>또는 HashAggregate를 이용해 중복을 제거할 수도 있다.</p>
<pre><code class="language-text">HashAggregate
  Group Key: department_id</code></pre>
<p>불필요한 <code>DISTINCT</code>는 정렬이나 Hash 비용을 발생시킬 수 있으므로 조인에서 중복이 발생한 원인을 먼저 확인해야 한다.</p>
<hr />
<h1 id="35-limit-노드">35. Limit 노드</h1>
<pre><code class="language-sql">SELECT *
FROM orders
ORDER BY created_at DESC
LIMIT 10;</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Limit
  → Index Scan Backward using idx_orders_created_at</code></pre>
<p><code>Limit</code>의 자식 노드는 전체 데이터를 모두 반환하지 않고 필요한 행이 충족되면 조기에 멈출 수 있다.</p>
<p>따라서 <code>LIMIT</code> 쿼리에서는 전체 Total Cost보다 Startup Cost와 첫 행 반환 속도가 중요할 수 있다.</p>
<hr />
<h1 id="36-append와-merge-append">36. Append와 Merge Append</h1>
<p>파티션 테이블이나 <code>UNION ALL</code>에서 여러 하위 계획의 결과를 합칠 때 <code>Append</code>가 나타날 수 있다.</p>
<pre><code class="language-text">Append
  → Seq Scan on orders_2025
  → Seq Scan on orders_2026</code></pre>
<p>각 입력이 정렬되어 있고 정렬 순서를 유지하며 합쳐야 한다면 <code>Merge Append</code>가 사용될 수 있다.</p>
<pre><code class="language-text">Merge Append
  Sort Key: created_at
  → Index Scan on orders_2025
  → Index Scan on orders_2026</code></pre>
<hr />
<h2 id="361-partition-pruning">36.1 Partition Pruning</h2>
<p>파티션 키 조건으로 불필요한 파티션을 제외할 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM orders
WHERE ordered_at &gt;= DATE '2026-07-01'
  AND ordered_at &lt; DATE '2026-08-01';</code></pre>
<p>실행계획에서 일부 파티션만 나타나거나 다음 정보가 보일 수 있다.</p>
<pre><code class="language-text">Subplans Removed</code></pre>
<p>확인할 내용:</p>
<pre><code class="language-text">필요한 파티션만 읽는가?
파티션 키 조건이 적절한가?
실행 시점 파티션 프루닝이 적용되는가?
모든 파티션을 반복해서 읽고 있지 않은가?</code></pre>
<hr />
<h1 id="37-materialize">37. Materialize</h1>
<p><code>Materialize</code>는 자식 노드의 결과를 임시로 저장해 반복 사용한다.</p>
<pre><code class="language-text">Materialize
  → Seq Scan on small_table</code></pre>
<p>다음 상황에서 나타날 수 있다.</p>
<pre><code class="language-text">Nested Loop 내부 결과 반복 사용
자식 계획을 매번 다시 실행하는 것보다 저장이 저렴함
재스캔 가능한 결과가 필요함</code></pre>
<p>결과가 메모리를 초과하면 임시 파일을 사용할 수 있다.</p>
<p>Materialize가 있다고 무조건 나쁜 것은 아니다.</p>
<p>반복 계산을 줄여 전체 성능을 높일 수 있다.</p>
<hr />
<h1 id="38-subplan과-initplan">38. SubPlan과 InitPlan</h1>
<p>서브쿼리가 항상 독립적인 SubPlan으로 실행되는 것은 아니다.</p>
<p>옵티마이저는 다음 형태로 변환할 수 있다.</p>
<pre><code class="language-text">일반 Join
Semi Join
Anti Join
InitPlan
SubPlan</code></pre>
<hr />
<h2 id="381-initplan">38.1 InitPlan</h2>
<p>외부 행에 의존하지 않는 서브쿼리를 한 번 실행해 결과를 준비할 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM employees
WHERE salary &gt; (
    SELECT AVG(salary)
    FROM employees
);</code></pre>
<p>실행 개념:</p>
<pre><code class="language-text">InitPlan
→ AVG(salary) 한 번 계산
→ 결과를 파라미터로 저장
→ 외부 Scan에서 사용</code></pre>
<p>서브쿼리가 외부 행과 무관하므로 매 행마다 다시 실행할 필요가 없다.</p>
<hr />
<h2 id="382-subplan">38.2 SubPlan</h2>
<p>서브쿼리가 외부 행을 참조하고 일반 조인으로 변환되지 않으면 SubPlan으로 남을 수 있다.</p>
<pre><code class="language-sql">SELECT e.*
FROM employees e
WHERE e.salary &gt; (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
);</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Seq Scan on employees e
  Filter: (salary &gt; (SubPlan 1))
  SubPlan 1
    → Aggregate
         → Seq Scan on employees e2</code></pre>
<p>외부 행마다 SubPlan이 반복되면 <code>loops</code>가 크게 증가할 수 있다.</p>
<pre><code class="language-text">SubPlan
  loops=100000</code></pre>
<p>이 경우 사전 집계 후 조인하는 방식 등을 검토할 수 있다.</p>
<pre><code class="language-sql">WITH department_avg AS (
    SELECT
        department_id,
        AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT e.*
FROM employees e
JOIN department_avg a
    ON a.department_id = e.department_id
WHERE e.salary &gt; a.avg_salary;</code></pre>
<p>변경 후에는 반드시 실제 실행계획을 다시 측정해야 한다.</p>
<hr />
<h2 id="383-hashed-subplan">38.3 Hashed SubPlan</h2>
<p>상관되지 않은 <code>IN</code> 서브쿼리 결과를 Hash 구조로 저장해 반복 비교할 수 있다.</p>
<pre><code class="language-text">Filter: (hashed SubPlan 1)</code></pre>
<p>서브쿼리 결과를 한 번 만들어 Hash로 조회하므로 매 외부 행마다 서브쿼리를 다시 실행하는 것보다 효율적일 수 있다.</p>
<hr />
<h1 id="39-cte와-실행계획">39. CTE와 실행계획</h1>
<p>CTE는 SQL의 가독성과 재귀 처리에 유용하다.</p>
<pre><code class="language-sql">WITH high_salary AS (
    SELECT *
    FROM employees
    WHERE salary &gt;= 5000
)
SELECT *
FROM high_salary;</code></pre>
<p>현대 PostgreSQL에서는 부작용이 없는 일부 비재귀 CTE가 외부 쿼리와 통합되어 최적화될 수 있다.</p>
<p>실행계획에는 다음 중 하나가 나타날 수 있다.</p>
<pre><code class="language-text">CTE가 외부 쿼리에 Inline됨
CTE Scan으로 별도 실행됨
Materialize됨</code></pre>
<p>명시적으로 제어할 수도 있다.</p>
<pre><code class="language-sql">WITH high_salary AS MATERIALIZED (
    ...
)</code></pre>
<pre><code class="language-sql">WITH high_salary AS NOT MATERIALIZED (
    ...
)</code></pre>
<p>CTE로 바꾸면 무조건 빨라지거나 느려진다고 단정할 수 없다.</p>
<pre><code class="language-text">중간 결과 재사용
필터 Pushdown
Materialize 비용
CTE 실행 횟수</code></pre>
<p>를 실행계획으로 확인해야 한다.</p>
<hr />
<h1 id="40-filter와-rows-removed-by-filter">40. Filter와 Rows Removed by Filter</h1>
<p>다음 실행계획을 보자.</p>
<pre><code class="language-text">Seq Scan on employees
  Filter: (salary &gt;= 5000)
  Rows Removed by Filter: 900000</code></pre>
<p>테이블의 행을 읽은 뒤 90만 행을 Filter에서 제거했다는 뜻이다.</p>
<p>다음 가능성을 검토할 수 있다.</p>
<pre><code class="language-text">조건에 적합한 인덱스가 없는가?
조건이 SARGable하지 않은가?
조회 결과는 실제로 적은가?
통계정보가 잘못되었는가?
Sequential Scan이 여전히 합리적인가?</code></pre>
<p><code>Rows Removed by Filter</code>가 많다고 무조건 인덱스가 필요한 것은 아니다.</p>
<p>전체 1억 건 중 9천만 건을 제거하고 1천만 건을 반환한다면 여전히 Sequential Scan이 합리적일 수 있다.</p>
<hr />
<h1 id="41-buffers-해석">41. BUFFERS 해석</h1>
<pre><code class="language-text">Buffers: shared hit=100 read=20</code></pre>
<hr />
<h2 id="411-shared-hit">41.1 shared hit</h2>
<p>필요한 페이지가 PostgreSQL Shared Buffer에 이미 존재해 메모리에서 찾았다.</p>
<pre><code class="language-text">shared hit=100</code></pre>
<p>100개의 공유 버퍼 페이지를 캐시에서 이용했다.</p>
<hr />
<h2 id="412-shared-read">41.2 shared read</h2>
<p>필요한 페이지가 Shared Buffer에 없어 읽어 왔다.</p>
<pre><code class="language-text">shared read=20</code></pre>
<p>주의할 점은 <code>shared read</code>가 반드시 물리 디스크에서 직접 읽었다는 뜻은 아니라는 것이다.</p>
<p>운영체제 파일 캐시에 존재했을 수도 있다.</p>
<hr />
<h2 id="413-shared-dirtied">41.3 shared dirtied</h2>
<p>실행 중 페이지가 수정되어 Dirty 상태가 되었다.</p>
<pre><code class="language-text">shared dirtied=10</code></pre>
<hr />
<h2 id="414-shared-written">41.4 shared written</h2>
<p>Dirty 페이지가 실행 과정에서 기록되었다.</p>
<pre><code class="language-text">shared written=5</code></pre>
<hr />
<h2 id="415-local">41.5 local</h2>
<p>임시 테이블 등의 Local Buffer 사용량이다.</p>
<pre><code class="language-text">local hit
local read
local dirtied
local written</code></pre>
<hr />
<h2 id="416-temp">41.6 temp</h2>
<p>정렬, Hash, Materialize 등이 메모리를 초과하여 임시 파일을 사용한 경우 나타난다.</p>
<pre><code class="language-text">temp read=5000
temp written=5000</code></pre>
<p>임시 파일 사용은 중요한 성능 저하 신호다.</p>
<p>다음 원인을 검토한다.</p>
<pre><code class="language-text">정렬 대상이 너무 큼
Hash Table이 메모리를 초과함
중간 결과 행 수가 예상보다 많음
work_mem이 부족함
불필요하게 넓은 행을 처리함
잘못된 조인 순서</code></pre>
<hr />
<h1 id="42-캐시-상태와-실행시간">42. 캐시 상태와 실행시간</h1>
<p>같은 쿼리를 연속으로 실행하면 두 번째 실행이 더 빠를 수 있다.</p>
<pre><code class="language-text">첫 번째 실행
→ 페이지를 파일 시스템 또는 디스크에서 읽음

두 번째 실행
→ Shared Buffer 또는 OS Cache에서 읽음</code></pre>
<p>따라서 실행시간 한 번만 비교하면 잘못된 결론을 내릴 수 있다.</p>
<p>성능 비교 시 다음을 함께 확인한다.</p>
<pre><code class="language-text">Execution Time
shared hit
shared read
temp read/write
반복 실행 결과
동일한 파라미터
동일한 데이터 상태</code></pre>
<p>운영 환경의 실제 캐시 상태와 동시 부하도 고려해야 한다.</p>
<hr />
<h1 id="43-jit">43. JIT</h1>
<p>복잡한 표현식 계산이나 대량 집계에서는 JIT 컴파일이 사용될 수 있다.</p>
<p>실행계획에 다음과 같은 정보가 나타날 수 있다.</p>
<pre><code class="language-text">JIT:
  Functions: ...
  Options: Inlining ..., Optimization ..., Expressions ...
  Timing: Generation ..., Optimization ..., Emission ...</code></pre>
<p>JIT는 반복되는 표현식 평가를 기계어로 컴파일해 대량 처리 성능을 높일 수 있다.</p>
<p>하지만 컴파일 자체의 Startup Cost가 발생한다.</p>
<pre><code class="language-text">짧은 쿼리
→ JIT 준비비용이 더 큼

대량 계산 쿼리
→ JIT 비용을 상쇄하고 이점 발생 가능</code></pre>
<p>실행시간이 짧은 쿼리에서 JIT 준비시간이 큰 비율을 차지하는지 확인해야 한다.</p>
<hr />
<h1 id="44-gather와-gather-merge">44. Gather와 Gather Merge</h1>
<p>병렬 실행계획의 결과는 <code>Gather</code> 또는 <code>Gather Merge</code>가 수집한다.</p>
<hr />
<h2 id="441-gather">44.1 Gather</h2>
<pre><code class="language-text">Gather
  Workers Planned: 2
  Workers Launched: 2
  → Parallel Seq Scan</code></pre>
<p>각 Worker가 만든 결과를 순서 보장 없이 모은다.</p>
<hr />
<h2 id="442-gather-merge">44.2 Gather Merge</h2>
<pre><code class="language-text">Gather Merge
  Workers Planned: 2
  → Sort
       → Parallel Seq Scan</code></pre>
<p>각 Worker의 정렬된 결과를 전체 정렬 순서를 유지하면서 병합한다.</p>
<p><code>ORDER BY</code> 결과를 병렬로 처리할 때 나타날 수 있다.</p>
<hr />
<h1 id="45-비용-모델의-주요-설정">45. 비용 모델의 주요 설정</h1>
<p>PostgreSQL의 비용 계산에는 여러 설정값이 사용된다.</p>
<p>대표적인 항목은 다음과 같다.</p>
<pre><code class="language-text">seq_page_cost
random_page_cost
cpu_tuple_cost
cpu_index_tuple_cost
cpu_operator_cost
effective_cache_size
work_mem
parallel_setup_cost
parallel_tuple_cost</code></pre>
<hr />
<h2 id="451-seq_page_cost">45.1 seq_page_cost</h2>
<p>순차 페이지 읽기의 기준 비용이다.</p>
<p>다른 비용 설정의 기준점 역할을 한다.</p>
<hr />
<h2 id="452-random_page_cost">45.2 random_page_cost</h2>
<p>무작위 페이지 읽기의 예상 비용이다.</p>
<p>이 값이 높으면 많은 Heap 페이지를 무작위로 접근하는 Index Scan의 비용이 크게 계산될 수 있다.</p>
<p>스토리지 특성과 캐시 상태를 반영하지 않은 채 임의로 낮추면 옵티마이저가 인덱스를 과도하게 선택할 수 있다.</p>
<hr />
<h2 id="453-effective_cache_size">45.3 effective_cache_size</h2>
<p>PostgreSQL이 직접 확보하는 메모리 크기가 아니다.</p>
<p>옵티마이저에게 운영체제 캐시와 Shared Buffer를 포함해 얼마나 많은 데이터가 캐시될 것으로 기대하는지를 알려주는 추정값이다.</p>
<hr />
<h2 id="454-work_mem">45.4 work_mem</h2>
<p>각 Sort, Hash, Materialize 등의 연산이 사용할 수 있는 메모리에 영향을 준다.</p>
<p>동시 쿼리와 병렬 Worker 수를 고려해 조정해야 한다.</p>
<hr />
<h2 id="455-비용-설정-조정-주의">45.5 비용 설정 조정 주의</h2>
<p>비용 설정은 인덱스를 강제로 사용하기 위한 도구가 아니다.</p>
<p>먼저 다음을 확인해야 한다.</p>
<pre><code class="language-text">SQL 구조
통계정보
행 수 추정
데이터 분포
인덱스 설계
실제 저장장치 특성</code></pre>
<p>비용 설정은 충분한 측정과 시스템 전반의 검토 후 조정해야 한다.</p>
<hr />
<h1 id="46-planner-설정으로-계획-강제하기">46. Planner 설정으로 계획 강제하기</h1>
<p>PostgreSQL에는 다음과 같은 Planner 설정이 있다.</p>
<pre><code class="language-text">enable_seqscan
enable_indexscan
enable_bitmapscan
enable_hashjoin
enable_mergejoin
enable_nestloop</code></pre>
<p>예:</p>
<pre><code class="language-sql">SET enable_seqscan = off;</code></pre>
<p>이는 특정 실행 방법의 비용을 매우 불리하게 만들어 다른 계획을 시험하는 데 사용할 수 있다.</p>
<p>하지만 운영 쿼리의 해결책으로 상시 비활성화하는 것은 일반적으로 적절하지 않다.</p>
<pre><code class="language-text">진단 목적
→ 다른 계획의 가능성 비교

운영 해결책
→ SQL, 통계, 인덱스, 데이터 구조 개선</code></pre>
<p>으로 구분해야 한다.</p>
<hr />
<h1 id="47-실행계획에서-자주-보이는-경고-신호">47. 실행계획에서 자주 보이는 경고 신호</h1>
<p>다음 항목이 나타나면 상세히 확인해야 한다.</p>
<pre><code class="language-text">예상 rows와 actual rows가 크게 다름

Nested Loop 내부 노드의 loops가 지나치게 큼

Rows Removed by Filter가 매우 많음

Rows Removed by Join Filter가 매우 많음

Sort Method가 external merge임

Hash의 Batches가 여러 개임

HashAggregate에서 Disk Usage가 발생함

Index Only Scan인데 Heap Fetches가 많음

Bitmap Heap Scan에서 Lossy Block이 많음

상관 SubPlan이 외부 행마다 반복됨

불필요한 파티션을 모두 읽음

같은 대형 테이블을 여러 번 반복 스캔함

중간 결과의 rows와 width가 지나치게 큼

Workers Planned보다 Workers Launched가 적음</code></pre>
<p>하지만 하나의 신호만 보고 결론을 내리면 안 된다.</p>
<hr />
<h1 id="48-노드-이름만으로-판단하면-안-된다">48. 노드 이름만으로 판단하면 안 된다</h1>
<p>다음과 같은 공식은 성립하지 않는다.</p>
<pre><code class="language-text">Seq Scan = 무조건 나쁨

Index Scan = 무조건 좋음

Nested Loop = 무조건 나쁨

Hash Join = 무조건 좋음

Sort = 무조건 문제

Materialize = 무조건 비효율</code></pre>
<p>예를 들어 작은 테이블의 Sequential Scan은 가장 효율적인 계획일 수 있다.</p>
<p>반대로 Index Scan이 100만 번 반복된다면 큰 병목이 될 수 있다.</p>
<p>항상 다음 정보를 함께 본다.</p>
<pre><code class="language-text">행 수
반복 횟수
버퍼 접근량
필터 제거량
정렬·Hash의 메모리 사용
디스크 Spill
전체 실행시간
통계 추정 정확도</code></pre>
<hr />
<h1 id="49-실행계획이-보여주지-못하는-것">49. 실행계획이 보여주지 못하는 것</h1>
<p>실행계획은 SQL 내부의 데이터 처리 구조를 분석하는 핵심 도구지만 모든 성능 문제를 설명하지는 못한다.</p>
<p>다음 문제는 별도로 확인해야 할 수 있다.</p>
<pre><code class="language-text">잠금 대기
데드락
커넥션 풀 대기
네트워크 지연
클라이언트의 느린 결과 소비
스토리지 장애
CPU 포화
메모리 압박
체크포인트 I/O
다른 쿼리와의 자원 경쟁</code></pre>
<p>실행계획이 단순한데 실행시간이 길다면 다음도 확인한다.</p>
<pre><code class="language-text">현재 세션의 Wait Event
Blocking Transaction
시스템 CPU와 I/O
동시 실행 중인 쿼리
커넥션 상태</code></pre>
<p>실행계획은 성능 분석의 중심이지만 시스템 전체 모니터링을 대체하지 않는다.</p>
<hr />
<h1 id="50-실행계획-분석-예제">50. 실행계획 분석 예제</h1>
<p>다음 쿼리가 있다고 하자.</p>
<pre><code class="language-sql">SELECT
    e.employee_id,
    e.full_name,
    d.department_name
FROM employees e
JOIN departments d
    ON d.department_id = e.department_id
WHERE e.salary &gt;= 5000;</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Hash Join
  (cost=10.00..2000.00 rows=50000 width=80)
  (actual rows=45000 loops=1)
  Hash Cond: (e.department_id = d.department_id)

  → Seq Scan on employees e
       (cost=0.00..1800.00 rows=50000 width=60)
       (actual rows=45000 loops=1)
       Filter: (salary &gt;= 5000)
       Rows Removed by Filter: 55000

  → Hash
       (cost=8.00..8.00 rows=100 width=20)
       (actual rows=100 loops=1)
       Buckets: 1024
       Batches: 1
       Memory Usage: 20kB

       → Seq Scan on departments d
            (cost=0.00..8.00 rows=100 width=20)
            (actual rows=100 loops=1)</code></pre>
<hr />
<h2 id="501-읽는-순서">50.1 읽는 순서</h2>
<p>먼저 가장 안쪽의 <code>departments</code>를 읽는다.</p>
<pre><code class="language-text">Seq Scan on departments
→ 100행 반환</code></pre>
<p>그 결과로 Hash Table을 만든다.</p>
<pre><code class="language-text">Hash
→ department_id 기준 Hash Table 생성
→ Batches: 1
→ 메모리에서 처리</code></pre>
<p>이후 employees를 전체 스캔한다.</p>
<pre><code class="language-text">100,000행 읽기
→ salary &gt;= 5000 필터
→ 55,000행 제거
→ 45,000행 반환</code></pre>
<p>각 employees 행의 <code>department_id</code>로 Hash Table을 탐색한다.</p>
<pre><code class="language-text">Hash Join
→ 45,000행 결과 생성</code></pre>
<hr />
<h2 id="502-판단">50.2 판단</h2>
<p>예상 행 수:</p>
<pre><code class="language-text">50,000</code></pre>
<p>실제 행 수:</p>
<pre><code class="language-text">45,000</code></pre>
<p>추정이 크게 어긋나지 않는다.</p>
<p>departments는 100행으로 작으므로 Sequential Scan과 Hash 생성이 합리적이다.</p>
<p>employees 결과가 45%라면 인덱스로 수많은 Heap 페이지를 방문하는 것보다 Sequential Scan이 합리적일 수 있다.</p>
<p>따라서 이 계획에서 <code>Seq Scan</code>이 나타났다는 이유만으로 인덱스를 추가할 필요는 없다.</p>
<hr />
<h1 id="51-nested-loop-문제-예제">51. Nested Loop 문제 예제</h1>
<p>실행계획:</p>
<pre><code class="language-text">Nested Loop
  → Seq Scan on orders
       (cost=0.00..100.00 rows=10)
       (actual rows=100000 loops=1)

  → Index Scan on order_items
       (cost=0.30..5.00 rows=2)
       (actual rows=3 loops=100000)</code></pre>
<p>옵티마이저 예상:</p>
<pre><code class="language-text">orders 10행
→ order_items 인덱스 탐색 10회</code></pre>
<p>실제:</p>
<pre><code class="language-text">orders 100,000행
→ order_items 인덱스 탐색 100,000회</code></pre>
<p>병목의 핵심은 Index Scan 자체가 아니라 외부 행 수 추정 오류다.</p>
<p>검토할 내용:</p>
<pre><code class="language-text">orders 조건의 통계정보
조건식이 인덱스와 통계에 적합한가?
데이터가 특정 값에 치우쳤는가?
다중 컬럼 통계가 필요한가?
Hash Join이 더 적합한가?
조인 전에 orders를 줄일 수 있는가?</code></pre>
<p>단순히 Nested Loop를 비활성화하는 것보다 추정 오류의 원인을 해결하는 것이 우선이다.</p>
<hr />
<h1 id="52-상관-서브쿼리-문제-예제">52. 상관 서브쿼리 문제 예제</h1>
<pre><code class="language-sql">SELECT e.*
FROM employees e
WHERE e.salary &gt; (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e.department_id
);</code></pre>
<p>실행계획:</p>
<pre><code class="language-text">Seq Scan on employees e
  Filter: (salary &gt; (SubPlan 1))
  SubPlan 1
    → Aggregate
         → Seq Scan on employees e2
              Filter:
              (department_id = e.department_id)</code></pre>
<p>외부 employees가 10만 행이라면 SubPlan도 최대 10만 번 실행될 수 있다.</p>
<pre><code class="language-text">employees 전체 스캔
×
외부 행 수</code></pre>
<p>로 인해 작업량이 폭증한다.</p>
<p>개선 방향:</p>
<pre><code class="language-text">부서별 평균을 한 번 계산
→ employees와 조인</code></pre>
<pre><code class="language-sql">WITH department_avg AS (
    SELECT
        department_id,
        AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT e.*
FROM employees e
JOIN department_avg a
    ON a.department_id = e.department_id
WHERE e.salary &gt; a.avg_salary;</code></pre>
<p>변경 후 실행계획에서 다음을 확인한다.</p>
<pre><code class="language-text">employees 반복 스캔 제거 여부
집계 실행 횟수
Hash Join 또는 Merge Join 사용 여부
전체 Buffer 사용량
Execution Time</code></pre>
<hr />
<h1 id="53-디스크-정렬-문제-예제">53. 디스크 정렬 문제 예제</h1>
<p>실행계획:</p>
<pre><code class="language-text">Sort
  Sort Key: created_at DESC
  Sort Method: external merge
  Disk: 500MB
  → Seq Scan on logs
       actual rows=10000000</code></pre>
<p>분석:</p>
<pre><code class="language-text">1,000만 행 정렬
→ work_mem 초과
→ 500MB 임시 디스크 사용</code></pre>
<p>가능한 개선:</p>
<pre><code class="language-text">정렬 전에 WHERE 조건으로 행 수 감소
필요한 컬럼만 SELECT
LIMIT과 정렬 인덱스 조합
쿼리 단위 work_mem 검토
파티셔닝 검토</code></pre>
<p>예:</p>
<pre><code class="language-sql">SELECT log_id, created_at, message
FROM logs
WHERE service_id = 10
ORDER BY created_at DESC
LIMIT 100;</code></pre>
<p>다음 인덱스를 검토할 수 있다.</p>
<pre><code class="language-sql">CREATE INDEX idx_logs_service_created
ON logs(service_id, created_at DESC);</code></pre>
<p>실행계획이 다음처럼 바뀔 수 있다.</p>
<pre><code class="language-text">Limit
  → Index Scan using idx_logs_service_created</code></pre>
<p>전체 1,000만 행을 정렬하지 않고 인덱스에서 앞부분 100건만 읽을 수 있다.</p>
<hr />
<h1 id="54-성능-개선의-올바른-순서">54. 성능 개선의 올바른 순서</h1>
<p>실행계획 튜닝은 무조건 인덱스를 추가하는 작업이 아니다.</p>
<p>다음 순서로 접근하는 것이 좋다.</p>
<hr />
<h2 id="1단계-sql-결과의-정확성-확인">1단계: SQL 결과의 정확성 확인</h2>
<p>먼저 SQL이 올바른 결과를 반환하는지 확인한다.</p>
<pre><code class="language-text">잘못된 JOIN 조건
중복 행 발생
NOT IN의 NULL 문제
LEFT JOIN 조건 위치 오류
잘못된 GROUP BY
불필요한 DISTINCT</code></pre>
<p>잘못된 결과를 빠르게 반환하는 것은 최적화가 아니다.</p>
<hr />
<h2 id="2단계-실제-환경과-유사한-데이터-준비">2단계: 실제 환경과 유사한 데이터 준비</h2>
<pre><code class="language-text">실제 데이터 양
실제 데이터 분포
대표적인 파라미터
동시 요청 특성</code></pre>
<p>이 다르면 테스트 실행계획도 운영 환경과 달라질 수 있다.</p>
<hr />
<h2 id="3단계-explain-analyze-buffers-수집">3단계: EXPLAIN ANALYZE BUFFERS 수집</h2>
<pre><code class="language-sql">EXPLAIN (
    ANALYZE,
    BUFFERS,
    TIMING OFF,
    SUMMARY
)
SELECT ...;</code></pre>
<p>다음 정보를 기록한다.</p>
<pre><code class="language-text">Planning Time
Execution Time
estimated rows
actual rows
loops
Buffers
Rows Removed by Filter
Heap Fetches
Sort Method
Hash Batches
Disk Usage</code></pre>
<hr />
<h2 id="4단계-데이터-흐름-확인">4단계: 데이터 흐름 확인</h2>
<p>가장 안쪽 노드부터 다음을 추적한다.</p>
<pre><code class="language-text">어디서 데이터를 읽는가?
각 노드는 몇 행을 생성하는가?
어디에서 행 수가 급증하는가?
어디에서 대부분의 행을 제거하는가?</code></pre>
<hr />
<h2 id="5단계-추정-오류-확인">5단계: 추정 오류 확인</h2>
<pre><code class="language-text">estimated rows
vs
actual rows</code></pre>
<p>차이가 크다면 먼저 통계와 조건을 확인한다.</p>
<pre><code class="language-text">ANALYZE
통계 수집량
Extended Statistics
함수와 형변환
데이터 편향</code></pre>
<hr />
<h2 id="6단계-반복-횟수-확인">6단계: 반복 횟수 확인</h2>
<p>특히 Nested Loop와 SubPlan의 내부 노드를 확인한다.</p>
<pre><code class="language-text">loops가 수만~수백만인가?</code></pre>
<p>한 번의 실행은 빨라도 반복 횟수가 크면 병목이 된다.</p>
<hr />
<h2 id="7단계-메모리와-디스크-spill-확인">7단계: 메모리와 디스크 Spill 확인</h2>
<pre><code class="language-text">external merge
temp read/write
Hash Batches &gt; 1
Disk Usage
Lossy Bitmap</code></pre>
<p>가 나타나는지 확인한다.</p>
<hr />
<h2 id="8단계-sql-구조-개선">8단계: SQL 구조 개선</h2>
<pre><code class="language-text">반복 상관 서브쿼리 → 조인 또는 사전 집계
필터를 더 이른 단계에 적용
SELECT * 제거
불필요한 DISTINCT 제거
NOT IN → 의미에 맞는 NOT EXISTS
불필요한 CTE Materialize 제거
중복 조인 제거</code></pre>
<hr />
<h2 id="9단계-인덱스와-데이터-구조-개선">9단계: 인덱스와 데이터 구조 개선</h2>
<p>실제 쿼리 패턴을 기준으로 검토한다.</p>
<pre><code class="language-text">단일 인덱스
복합 인덱스
부분 인덱스
표현식 인덱스
INCLUDE
파티셔닝
물리적 데이터 배치</code></pre>
<hr />
<h2 id="10단계-설정-검토">10단계: 설정 검토</h2>
<p>SQL, 통계, 인덱스를 먼저 검토한 뒤 다음을 고려한다.</p>
<pre><code class="language-text">work_mem
effective_cache_size
random_page_cost
병렬 처리 설정
JIT 설정</code></pre>
<hr />
<h2 id="11단계-동일-조건으로-재측정">11단계: 동일 조건으로 재측정</h2>
<p>개선 전후를 동일한 조건으로 비교한다.</p>
<pre><code class="language-text">Execution Time
Buffers
actual rows
loops
temp I/O
Heap Fetches</code></pre>
<p>인덱스를 사용하게 되었다는 사실보다 실제 페이지 접근량과 실행시간이 줄었는지가 중요하다.</p>
<hr />
<h2 id="12단계-운영-영향-확인">12단계: 운영 영향 확인</h2>
<p>조회 성능 개선이 다음 문제를 만들 수 있다.</p>
<pre><code class="language-text">INSERT·UPDATE·DELETE 비용 증가
인덱스 저장공간 증가
VACUUM 부담 증가
메모리 사용량 증가
다른 쿼리의 계획 변화
동시 사용자 환경의 자원 부족</code></pre>
<p>단일 쿼리만 빠르게 만드는 것이 아니라 시스템 전체의 처리량을 함께 봐야 한다.</p>
<hr />
<h1 id="55-실행계획-분석-체크리스트">55. 실행계획 분석 체크리스트</h1>
<h2 id="기본-정보">기본 정보</h2>
<pre><code class="language-text">Planning Time은 얼마인가?
Execution Time은 얼마인가?
결과 행 수는 몇 개인가?</code></pre>
<h2 id="행-수-추정">행 수 추정</h2>
<pre><code class="language-text">estimated rows와 actual rows가 비슷한가?
차이가 어느 노드부터 커지는가?</code></pre>
<h2 id="반복-구조">반복 구조</h2>
<pre><code class="language-text">loops가 큰 노드는 무엇인가?
Nested Loop 내부가 과도하게 반복되는가?
SubPlan이 행마다 실행되는가?</code></pre>
<h2 id="스캔">스캔</h2>
<pre><code class="language-text">Seq Scan이 합리적인가?
Index Cond가 조건을 충분히 좁히는가?
Filter에서 많은 행을 제거하는가?
Index Only Scan의 Heap Fetches가 많은가?
Bitmap이 Lossy 상태인가?</code></pre>
<h2 id="조인">조인</h2>
<pre><code class="language-text">조인 순서가 적절한가?
Hash Build 입력이 충분히 작은가?
Hash Batches가 증가했는가?
Merge Join 전에 비싼 정렬이 발생하는가?
Join Filter에서 많은 행이 제거되는가?</code></pre>
<h2 id="정렬과-집계">정렬과 집계</h2>
<pre><code class="language-text">Sort가 메모리에서 수행되는가?
external merge가 발생하는가?
HashAggregate가 디스크를 사용하는가?
불필요한 DISTINCT가 있는가?</code></pre>
<h2 id="버퍼">버퍼</h2>
<pre><code class="language-text">shared hit와 read는 얼마인가?
temp read/write가 발생했는가?
같은 테이블을 반복해서 많이 읽는가?</code></pre>
<h2 id="병렬-처리">병렬 처리</h2>
<pre><code class="language-text">Workers Planned와 Launched가 같은가?
병렬 처리 비용보다 이점이 큰가?
Gather가 병목이 아닌가?</code></pre>
<hr />
<h1 id="반드시-기억해야-할-핵심-문장">반드시 기억해야 할 핵심 문장</h1>
<pre><code class="language-text">1. 실행계획은 SQL을 처리하기 위해 DBMS가 선택한
   물리적 연산의 트리다.

2. SQL은 무엇을 원하는지 선언하고,
   실행계획은 그것을 어떻게 얻을지 결정한다.

3. 실행계획은 가장 깊은 자식 노드부터 읽는다.

4. Cost는 실제 시간이 아니라 후보 계획을 비교하기 위한
   상대적인 비용 단위다.

5. Startup Cost는 첫 행을 반환하기 전의 비용이고,
   Total Cost는 전체 결과를 반환하는 비용이다.

6. rows는 스캔한 행 수가 아니라
   해당 노드가 반환할 것으로 예상한 행 수다.

7. actual rows와 actual time은 loops가 여러 번이면
   반복당 평균값으로 표시될 수 있다.

8. 예상 rows와 actual rows의 차이는
   잘못된 실행계획의 가장 중요한 단서 중 하나다.

9. Seq Scan이 나타났다고 무조건 문제가 있는 것은 아니다.

10. Index Scan이 사용되었다고 무조건 빠른 것도 아니다.

11. Index Cond는 인덱스 탐색에 사용된 조건이고,
    Filter는 후보 행을 읽은 뒤 검사한 조건이다.

12. Index Only Scan도 MVCC 가시성 확인 때문에
    Heap Fetch가 발생할 수 있다.

13. Bitmap Scan은 여러 행의 위치를 페이지 단위로 정리해
    무작위 Heap 접근을 줄인다.

14. Nested Loop는 내부 노드의 loops를 반드시 확인해야 한다.

15. Hash Join은 동등 조인과 대량 데이터에 유리하지만,
    메모리를 초과하면 여러 Batch와 임시 I/O가 발생한다.

16. Merge Join은 정렬된 입력에 강하지만
    입력 정렬 비용이 병목이 될 수 있다.

17. Sort의 external merge는 디스크 정렬이 발생했다는 뜻이다.

18. 상관 SubPlan이 외부 행마다 반복되면
    실행 횟수가 폭증할 수 있다.

19. Buffers는 실행시간보다 더 안정적으로
    쿼리의 데이터 접근량을 보여줄 수 있다.

20. shared read는 반드시 물리 디스크 읽기만을 의미하지 않는다.

21. work_mem은 쿼리 전체가 아니라
    각 Sort·Hash 연산과 병렬 Worker에 적용될 수 있다.

22. 실행계획의 노드 이름만 보고 좋고 나쁨을 판단하면 안 된다.

23. 먼저 SQL 정확성을 확인하고,
    실제 실행계획을 측정한 뒤 병목을 찾아야 한다.

24. SQL 구조, 통계, 인덱스, 설정 순서로 검토하고
    변경 후 반드시 다시 측정해야 한다.

25. 실행계획은 SQL 처리 구조를 보여주지만
    잠금 대기와 시스템 자원 문제까지 모두 설명하지는 않는다.</code></pre>
<hr />
<h1 id="최종-정리">최종 정리</h1>
<p>실행계획 분석은 단순히 인덱스 사용 여부를 확인하는 작업이 아니다.</p>
<p>다음 흐름을 분석하는 과정이다.</p>
<pre><code class="language-text">SQL이 요구하는 논리적 연산
→ 옵티마이저가 후보 실행계획 탐색
→ 통계정보를 이용해 행 수와 비용 추정
→ 가장 낮은 비용의 물리적 계획 선택
→ Executor가 계획 트리 실행
→ 각 노드가 행을 생성하고 상위 노드에 전달</code></pre>
<p>실행계획에서 가장 중요한 세 가지는 다음과 같다.</p>
<pre><code class="language-text">행 수
→ 각 단계에서 얼마나 많은 데이터가 이동하는가?

반복 횟수
→ 같은 작업이 몇 번 수행되는가?

페이지 접근
→ 실제로 얼마나 많은 데이터를 읽고 쓰는가?</code></pre>
<p>성능 문제는 대개 다음 중 하나로 나타난다.</p>
<pre><code class="language-text">예상보다 많은 행
과도한 반복
너무 늦게 적용되는 필터
부적절한 조인 순서
메모리를 초과한 정렬과 Hash
불필요한 Heap 접근
반복되는 SubPlan
과도한 페이지 읽기</code></pre>
<p>따라서 실행계획 튜닝의 핵심은 다음과 같다.</p>
<blockquote>
<p>가장 느린 노드를 찾는 것보다, 데이터가 처음 예상보다 커지기 시작한 지점과 그 데이터가 반복 처리되는 구조를 찾는 것이 중요하다.</p>
</blockquote>
<p>최종적인 분석 흐름은 다음과 같이 정리할 수 있다.</p>
<pre><code class="language-text">정확한 SQL 확인
→ EXPLAIN ANALYZE BUFFERS 측정
→ 자식 노드부터 데이터 흐름 추적
→ estimated rows와 actual rows 비교
→ loops와 Filter 확인
→ Sort·Hash·Temp I/O 확인
→ SQL·통계·인덱스·설정 개선
→ 동일 조건으로 재측정</code></pre>
<p>이 흐름을 이해하면 실행계획을 단순한 출력문이 아니라, PostgreSQL이 SQL을 어떻게 해석하고 데이터를 어떻게 이동시키는지를 보여주는 진단 도구로 활용할 수 있다.</p>