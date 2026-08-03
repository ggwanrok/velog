<h2 id="들어가며">들어가며</h2>
<p>SQL을 처음 배우면 주로 <code>SELECT</code>, <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>처럼 데이터를 조회하고 변경하는 기본 문법부터 익히게 된다.</p>
<p>하지만 실제 데이터베이스에서는 단순히 행을 조회하는 것만으로 끝나지 않는다.</p>
<ul>
<li>여러 행을 하나의 통계값으로 요약해야 한다.</li>
<li>여러 테이블을 연결해야 한다.</li>
<li>한 쿼리의 결과를 다른 쿼리에서 활용해야 한다.</li>
<li>복잡한 쿼리를 단계별로 나누거나 반복해서 사용해야 한다.</li>
<li>기존 행을 유지한 채 순위나 누적 합계를 계산해야 한다.</li>
</ul>
<p>이번 글에서는 이러한 문제를 해결하기 위해 사용하는 SQL 기능을 다음 다섯 가지 주제로 정리한다.</p>
<ol>
<li>SQL의 집계 함수</li>
<li>JOIN 실행 알고리즘: NLJ, HJ, SMJ</li>
<li>서브쿼리와 집합 연산자</li>
<li>CTE와 VIEW</li>
<li>윈도우 함수</li>
</ol>
<p>예시는 PostgreSQL의 <code>employees</code>, <code>departments</code> 테이블을 기준으로 작성한다.</p>
<hr />
<h1 id="sql의-집계-함수">SQL의 집계 함수</h1>
<p>집계 함수는 여러 행의 데이터를 하나의 결과값으로 요약할 때 사용한다.</p>
<p>예를 들어 직원 테이블에 여러 직원의 급여가 저장되어 있을 때 다음과 같은 정보를 구할 수 있다.</p>
<ul>
<li>전체 직원 수</li>
<li>전체 급여 합계</li>
<li>평균 급여</li>
<li>최고 급여</li>
<li>최저 급여</li>
</ul>
<h2 id="대표적인-집계-함수">대표적인 집계 함수</h2>
<table>
<thead>
<tr>
<th>함수</th>
<th>역할</th>
</tr>
</thead>
<tbody><tr>
<td><code>COUNT()</code></td>
<td>행 또는 값의 개수를 계산</td>
</tr>
<tr>
<td><code>SUM()</code></td>
<td>값의 합계를 계산</td>
</tr>
<tr>
<td><code>AVG()</code></td>
<td>값의 평균을 계산</td>
</tr>
<tr>
<td><code>MAX()</code></td>
<td>최댓값을 반환</td>
</tr>
<tr>
<td><code>MIN()</code></td>
<td>최솟값을 반환</td>
</tr>
</tbody></table>
<pre><code class="language-sql">SELECT
    COUNT(*) AS employee_count,
    SUM(salary) AS total_salary,
    AVG(salary) AS average_salary,
    MAX(salary) AS maximum_salary,
    MIN(salary) AS minimum_salary
FROM employees;</code></pre>
<p>집계 함수는 여러 행을 입력받지만 하나의 결과 행을 반환한다.</p>
<pre><code class="language-text">여러 직원 행
    ↓
집계 함수
    ↓
전체 직원 수, 급여 합계, 평균 급여</code></pre>
<hr />
<h3 id="count와-countcolumn의-차이">COUNT(*)와 COUNT(column)의 차이</h3>
<p><code>COUNT(*)</code>는 조건을 만족하는 모든 행의 개수를 센다.</p>
<pre><code class="language-sql">SELECT COUNT(*)
FROM employees;</code></pre>
<p>반면 <code>COUNT(column)</code>은 해당 컬럼이 <code>NULL</code>이 아닌 행만 센다.</p>
<pre><code class="language-sql">SELECT
    COUNT(*) AS total_count,
    COUNT(department_id) AS assigned_department_count
FROM employees;</code></pre>
<p>부서가 배정되지 않은 직원의 <code>department_id</code>가 <code>NULL</code>이라면 다음과 같은 차이가 발생한다.</p>
<pre><code class="language-text">전체 직원 수: 107
부서가 배정된 직원 수: 106</code></pre>
<p><code>SUM</code>, <code>AVG</code>, <code>MAX</code>, <code>MIN</code> 역시 기본적으로 <code>NULL</code>을 집계 대상에서 제외한다.</p>
<hr />
<h2 id="group-by">GROUP BY</h2>
<p>전체 데이터를 하나로 집계하는 것이 아니라 특정 기준별로 집계하려면 <code>GROUP BY</code>를 사용한다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS average_salary
FROM employees
GROUP BY department_id;</code></pre>
<p>위 쿼리는 직원을 부서별로 묶은 뒤 각 부서의 직원 수와 평균 급여를 계산한다.</p>
<pre><code class="language-text">employees 전체 행
      ↓ department_id 기준 그룹화
10번 부서 그룹
20번 부서 그룹
30번 부서 그룹
      ↓ 집계
부서별 직원 수와 평균 급여</code></pre>
<hr />
<h3 id="group-by를-사용할-때의-select-규칙">GROUP BY를 사용할 때의 SELECT 규칙</h3>
<p><code>GROUP BY</code>를 사용하는 쿼리의 <code>SELECT</code> 절에는 일반적으로 다음 두 종류의 표현만 사용할 수 있다.</p>
<ol>
<li><code>GROUP BY</code>에 포함된 컬럼</li>
<li>집계 함수가 적용된 컬럼</li>
</ol>
<p>다음 쿼리는 올바르지 않다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    employee_id,
    AVG(salary)
FROM employees
GROUP BY department_id;</code></pre>
<p>하나의 부서에는 여러 직원이 존재하기 때문에 DBMS는 어떤 <code>employee_id</code>를 출력해야 할지 결정할 수 없다.</p>
<p>따라서 다음처럼 작성해야 한다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    AVG(salary) AS average_salary
FROM employees
GROUP BY department_id;</code></pre>
<hr />
<h2 id="where와-having">WHERE와 HAVING</h2>
<p><code>WHERE</code>와 <code>HAVING</code>은 모두 데이터를 필터링하지만 적용되는 시점이 다르다.</p>
<h3 id="where">WHERE</h3>
<p><code>WHERE</code>는 그룹화하기 전의 개별 행을 필터링한다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    AVG(salary) AS average_salary
FROM employees
WHERE salary &gt;= 5000
GROUP BY department_id;</code></pre>
<p>동작 과정은 다음과 같다.</p>
<pre><code class="language-text">1. 급여가 5,000 이상인 직원만 남긴다.
2. 남은 직원을 부서별로 그룹화한다.
3. 부서별 평균 급여를 계산한다.</code></pre>
<h3 id="having">HAVING</h3>
<p><code>HAVING</code>은 그룹화와 집계가 완료된 결과를 필터링한다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    COUNT(*) AS employee_count
FROM employees
GROUP BY department_id
HAVING COUNT(*) &gt;= 5;</code></pre>
<p>직원이 5명 이상인 부서만 결과에 포함된다.</p>
<hr />
<h3 id="where와-having-함께-사용하기">WHERE와 HAVING 함께 사용하기</h3>
<pre><code class="language-sql">SELECT
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS average_salary
FROM employees
WHERE salary &gt;= 3000
GROUP BY department_id
HAVING COUNT(*) &gt;= 5;</code></pre>
<p>이 쿼리는 다음 순서로 이해할 수 있다.</p>
<pre><code class="language-text">FROM employees
    ↓
salary가 3,000 이상인 행만 선택
    ↓
department_id 기준 그룹화
    ↓
직원 수와 평균 급여 집계
    ↓
직원 수가 5명 이상인 그룹만 선택</code></pre>
<p>SQL의 논리적 실행 순서는 대략 다음과 같다.</p>
<pre><code class="language-text">FROM
→ JOIN
→ WHERE
→ GROUP BY
→ HAVING
→ SELECT
→ ORDER BY
→ LIMIT</code></pre>
<p>아직 집계가 수행되지 않은 <code>WHERE</code>에서는 <code>COUNT(*)</code>, <code>AVG()</code> 같은 집계 결과를 조건으로 사용할 수 없다.</p>
<hr />
<h2 id="조건부-집계">조건부 집계</h2>
<p>하나의 그룹 안에서 여러 조건의 통계를 함께 구할 수도 있다.</p>
<h3 id="case를-이용한-조건부-집계">CASE를 이용한 조건부 집계</h3>
<pre><code class="language-sql">SELECT
    department_id,
    COUNT(*) AS total_count,
    COUNT(
        CASE
            WHEN salary &gt;= 10000 THEN 1
        END
    ) AS high_salary_count
FROM employees
GROUP BY department_id;</code></pre>
<h3 id="postgresql의-filter-사용">PostgreSQL의 FILTER 사용</h3>
<p>PostgreSQL에서는 <code>FILTER</code>를 사용해 조건을 더 명확하게 표현할 수 있다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    COUNT(*) AS total_count,
    COUNT(*) FILTER (
        WHERE salary &gt;= 10000
    ) AS high_salary_count,
    COUNT(*) FILTER (
        WHERE salary &lt; 10000
    ) AS normal_salary_count
FROM employees
GROUP BY department_id;</code></pre>
<p><code>WHERE</code>가 전체 집계 대상 행을 결정한다면, <code>FILTER</code>는 각각의 집계 함수에 별도의 조건을 적용한다.</p>
<hr />
<h2 id="rollup과-cube">ROLLUP과 CUBE</h2>
<p>일반적인 <code>GROUP BY</code>는 지정한 컬럼 조합의 집계만 반환한다.</p>
<pre><code class="language-sql">GROUP BY hire_year, department_id</code></pre>
<p>연도별·부서별 상세 집계뿐 아니라 연도 소계와 전체 합계까지 함께 구하려면 <code>ROLLUP</code>을 사용할 수 있다.</p>
<pre><code class="language-sql">SELECT
    EXTRACT(YEAR FROM hire_date) AS hire_year,
    department_id,
    COUNT(*) AS employee_count,
    SUM(salary) AS total_salary
FROM employees
GROUP BY ROLLUP(
    EXTRACT(YEAR FROM hire_date),
    department_id
);</code></pre>
<p><code>ROLLUP(a, b)</code>가 만드는 그룹은 다음과 같다.</p>
<pre><code class="language-text">(a, b)
(a)
전체 합계</code></pre>
<p><code>CUBE(a, b)</code>는 가능한 모든 조합을 만든다.</p>
<pre><code class="language-text">(a, b)
(a)
(b)
전체 합계</code></pre>
<pre><code class="language-sql">SELECT
    EXTRACT(YEAR FROM hire_date) AS hire_year,
    department_id,
    COUNT(*) AS employee_count
FROM employees
GROUP BY CUBE(
    EXTRACT(YEAR FROM hire_date),
    department_id
);</code></pre>
<p>정리하면 다음과 같다.</p>
<pre><code class="language-text">ROLLUP
→ 계층적인 소계가 필요할 때

CUBE
→ 여러 차원의 모든 소계가 필요할 때</code></pre>
<hr />
<h1 id="join-알고리즘">JOIN 알고리즘</h1>
<p>SQL에서 <code>INNER JOIN</code>, <code>LEFT JOIN</code>은 어떤 데이터를 결과에 포함할지를 결정한다.</p>
<pre><code class="language-sql">SELECT
    e.employee_id,
    e.first_name,
    d.department_name
FROM employees e
JOIN departments d
    ON e.department_id = d.department_id;</code></pre>
<p>하지만 DBMS 내부에서는 이 결과를 만들기 위해 별도의 실행 알고리즘을 선택한다.</p>
<p>대표적인 JOIN 알고리즘은 다음과 같다.</p>
<ul>
<li>Nested Loop Join</li>
<li>Hash Join</li>
<li>Sort Merge Join</li>
</ul>
<p>여기서 반드시 구분해야 할 부분이 있다.</p>
<pre><code class="language-text">INNER JOIN, LEFT JOIN
→ 어떤 행을 결과에 포함할 것인가

NLJ, HJ, SMJ
→ 두 테이블을 내부적으로 어떻게 비교할 것인가</code></pre>
<p>동일한 <code>INNER JOIN</code> SQL도 데이터 크기, 인덱스, 통계 정보 등에 따라 서로 다른 알고리즘으로 실행될 수 있다.</p>
<blockquote>
<p>DBMS 가 신경쓸 일이다~</p>
</blockquote>
<hr />
<h2 id="nested-loop-join">Nested Loop Join</h2>
<p>NLJ는 Nested Loop Join의 약자다.</p>
<p>한쪽 테이블의 각 행을 기준으로 다른 테이블에서 조건에 맞는 행을 찾는다.</p>
<p>개념적으로는 중첩 반복문과 비슷하다.</p>
<pre><code class="language-text">for 외부 테이블의 각 행:
    for 내부 테이블의 각 행:
        JOIN 조건 비교</code></pre>
<p>예를 들어 부서 테이블의 각 행을 읽으면서 해당 부서에 속한 직원을 찾는 방식이다.</p>
<pre><code class="language-text">10번 부서 선택
→ employees에서 10번 부서 직원 검색

20번 부서 선택
→ employees에서 20번 부서 직원 검색

30번 부서 선택
→ employees에서 30번 부서 직원 검색</code></pre>
<hr />
<h3 id="nlj의-장점">NLJ의 장점</h3>
<p>NLJ는 다음과 같은 상황에서 유리하다.</p>
<ul>
<li>한쪽 테이블의 조회 결과가 적을 때</li>
<li>내부 테이블의 JOIN 컬럼에 인덱스가 있을 때</li>
<li>최종적으로 반환할 행이 많지 않을 때</li>
<li>첫 번째 결과를 빠르게 반환해야 할 때</li>
</ul>
<p>다음과 같은 인덱스가 있다고 가정하자.</p>
<pre><code class="language-sql">CREATE INDEX idx_employees_department_id
ON employees(department_id);</code></pre>
<p>부서 한 행을 읽을 때마다 전체 직원 테이블을 처음부터 찾는 것이 아니라 인덱스를 이용해 해당 부서의 직원만 찾을 수 있다.</p>
<p>이를 Index Nested Loop Join이라고 볼 수 있다.</p>
<hr />
<h3 id="nlj의-단점">NLJ의 단점</h3>
<p>외부 테이블의 행이 많고 내부 테이블에서 인덱스를 사용할 수 없다면 반복적인 탐색 비용이 커진다.</p>
<pre><code class="language-text">외부 테이블 10,000행
×
내부 테이블 100,000행</code></pre>
<p>최악의 경우 매우 많은 비교가 발생할 수 있다.</p>
<p>따라서 NLJ는 일반적으로 <strong>작은 외부 결과와 효율적인 내부 탐색 수단이 있을 때</strong> 강점을 가진다.</p>
<hr />
<h2 id="hash-join">Hash Join</h2>
<p>HJ는 Hash Join의 약자다.</p>
<p>한쪽 테이블의 JOIN 키를 이용해 해시 테이블을 만들고, 다른 테이블의 값을 해시 테이블에서 탐색한다.</p>
<p>Hash Join은 크게 두 단계로 진행된다.</p>
<pre><code class="language-text">1. Build 단계
2. Probe 단계</code></pre>
<h3 id="build-단계">Build 단계</h3>
<p>일반적으로 비교적 작은 입력으로 해시 테이블을 만든다.</p>
<pre><code class="language-text">departments

10 → Sales
20 → Marketing
30 → IT</code></pre>
<h3 id="probe-단계">Probe 단계</h3>
<p>다른 테이블을 순회하며 JOIN 키를 해시 테이블에서 찾는다.</p>
<pre><code class="language-text">employees.department_id = 20
→ Hash Table에서 20 검색
→ Marketing과 결합</code></pre>
<hr />
<h3 id="hash-join의-장점">Hash Join의 장점</h3>
<p>Hash Join은 다음과 같은 상황에 적합하다.</p>
<ul>
<li>두 테이블의 데이터가 비교적 많을 때</li>
<li>동등 조건으로 JOIN할 때</li>
<li>적절한 인덱스가 없을 때</li>
<li>한쪽 입력으로 해시 테이블을 만들 수 있을 때</li>
</ul>
<pre><code class="language-sql">ON e.department_id = d.department_id</code></pre>
<p>Hash Join은 이와 같은 동등 비교에 강하다.</p>
<hr />
<h3 id="hash-join의-단점">Hash Join의 단점</h3>
<p>Hash Join은 해시 테이블을 메모리에 생성해야 한다.</p>
<p>해시 테이블이 메모리보다 커지면 디스크를 활용하면서 추가 비용이 발생할 수 있다.</p>
<p>또한 기본적으로 해시값을 기준으로 찾기 때문에 다음과 같은 범위 조건에는 적합하지 않다.</p>
<pre><code class="language-sql">ON e.salary &gt; g.minimum_salary</code></pre>
<pre><code class="language-text">Hash Join
→ 주로 동등 조건

범위 조건
→ 다른 JOIN 방식이 더 적합할 수 있음</code></pre>
<hr />
<h2 id="sort-merge-join">Sort Merge Join</h2>
<p>SMJ는 Sort Merge Join의 약자다.</p>
<p>두 입력을 JOIN 키 기준으로 정렬한 뒤, 정렬된 결과를 앞에서부터 비교하며 결합한다.</p>
<p>예를 들어 두 테이블의 JOIN 키가 다음과 같다고 하자.</p>
<pre><code class="language-text">employees:   10 10 20 30 30 40
departments: 10 20 30 50</code></pre>
<p>양쪽 데이터가 정렬되어 있으므로 현재 값을 비교하면서 위치를 이동한다.</p>
<pre><code class="language-text">10과 10 비교 → 일치
20과 20 비교 → 일치
30과 30 비교 → 일치
40과 50 비교 → 40 쪽 이동</code></pre>
<p>이미 지나간 값을 다시 처음부터 검색할 필요가 없다.</p>
<hr />
<h3 id="smj의-장점">SMJ의 장점</h3>
<p>SMJ는 다음과 같은 상황에서 유리하다.</p>
<ul>
<li>두 입력이 이미 JOIN 키 기준으로 정렬되어 있을 때</li>
<li>인덱스를 통해 정렬된 순서로 읽을 수 있을 때</li>
<li>대용량 데이터를 순차적으로 처리할 때</li>
<li>정렬 결과를 다른 연산에서도 활용할 수 있을 때</li>
</ul>
<hr />
<h3 id="smj의-단점">SMJ의 단점</h3>
<p>입력 데이터가 정렬되어 있지 않다면 먼저 정렬 작업을 수행해야 한다.</p>
<pre><code class="language-text">테이블 A 정렬
+
테이블 B 정렬
+
Merge 수행</code></pre>
<p>따라서 정렬 비용이 JOIN 비용보다 더 크게 발생할 수도 있다.</p>
<hr />
<h2 id="join-알고리즘-비교">JOIN 알고리즘 비교</h2>
<table>
<thead>
<tr>
<th>구분</th>
<th>NLJ</th>
<th>HJ</th>
<th>SMJ</th>
</tr>
</thead>
<tbody><tr>
<td>기본 원리</td>
<td>행마다 상대 테이블 탐색</td>
<td>해시 테이블 생성 후 탐색</td>
<td>양쪽을 정렬한 뒤 병합</td>
</tr>
<tr>
<td>유리한 상황</td>
<td>작은 결과와 인덱스</td>
<td>대용량 동등 JOIN</td>
<td>정렬된 대용량 데이터</td>
</tr>
<tr>
<td>인덱스 활용</td>
<td>매우 중요할 수 있음</td>
<td>없어도 동작 가능</td>
<td>정렬 인덱스 활용 가능</td>
</tr>
<tr>
<td>주요 조건</td>
<td>다양한 조건</td>
<td>주로 동등 조건</td>
<td>정렬 가능한 JOIN 조건</td>
</tr>
<tr>
<td>주요 비용</td>
<td>반복 탐색</td>
<td>해시 테이블 메모리</td>
<td>정렬 비용</td>
</tr>
</tbody></table>
<hr />
<h2 id="실행-계획-확인하기">실행 계획 확인하기</h2>
<p>작성자가 JOIN 알고리즘을 SQL 문법으로 직접 지정하는 것이 아니라, 일반적으로 옵티마이저가 실행 계획을 선택한다.</p>
<p>PostgreSQL에서는 <code>EXPLAIN</code>을 사용해 선택된 실행 계획을 확인할 수 있다.</p>
<pre><code class="language-sql">EXPLAIN
SELECT
    e.employee_id,
    d.department_name
FROM employees e
JOIN departments d
    ON e.department_id = d.department_id;</code></pre>
<p>실제 실행 시간과 행 수까지 확인하려면 다음과 같이 작성한다.</p>
<pre><code class="language-sql">EXPLAIN ANALYZE
SELECT
    e.employee_id,
    d.department_name
FROM employees e
JOIN departments d
    ON e.department_id = d.department_id;</code></pre>
<p>JOIN 성능을 이해하려면 SQL 문법만 보는 것이 아니라 다음 요소를 함께 살펴봐야 한다.</p>
<pre><code class="language-text">테이블 크기
인덱스 존재 여부
필터링 이후의 행 수
JOIN 조건
컬럼 값의 분포
DBMS가 보유한 통계 정보</code></pre>
<hr />
<h1 id="서브쿼리와-집합-연산자">서브쿼리와 집합 연산자</h1>
<p>서브쿼리와 집합 연산자는 모두 여러 <code>SELECT</code> 문을 함께 사용한다.</p>
<p>하지만 목적은 다르다.</p>
<pre><code class="language-text">서브쿼리
→ 한 쿼리의 결과를 다른 쿼리의 조건이나 데이터로 사용

집합 연산자
→ 여러 SELECT 결과를 하나의 결과 집합으로 결합</code></pre>
<hr />
<h2 id="서브쿼리">서브쿼리</h2>
<p>서브쿼리는 SQL 문 안에 포함된 또 다른 SQL 문이다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    first_name,
    salary
FROM employees
WHERE salary &gt; (
    SELECT AVG(salary)
    FROM employees
);</code></pre>
<p>안쪽 쿼리가 전체 직원의 평균 급여를 계산하고, 바깥쪽 쿼리가 평균보다 높은 급여를 받는 직원을 조회한다.</p>
<pre><code class="language-text">서브쿼리
→ 평균 급여 계산

메인 쿼리
→ 평균보다 높은 직원 조회</code></pre>
<hr />
<h3 id="스칼라-서브쿼리">스칼라 서브쿼리</h3>
<p>스칼라 서브쿼리는 하나의 행과 하나의 컬럼, 즉 하나의 값을 반환한다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    first_name,
    salary,
    (
        SELECT AVG(salary)
        FROM employees
    ) AS company_average_salary
FROM employees;</code></pre>
<p>각 직원 행 옆에 전체 평균 급여가 표시된다.</p>
<p>스칼라 서브쿼리가 여러 행을 반환하면 단일 값으로 사용할 수 없기 때문에 오류가 발생한다.</p>
<hr />
<h3 id="다중-행-서브쿼리">다중 행 서브쿼리</h3>
<p>여러 값을 반환하는 서브쿼리는 <code>IN</code>, <code>ANY</code>, <code>ALL</code> 등과 함께 사용할 수 있다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    first_name,
    department_id
FROM employees
WHERE department_id IN (
    SELECT department_id
    FROM departments
    WHERE location_id = 1700
);</code></pre>
<p>특정 지역에 존재하는 부서의 직원들을 조회한다.</p>
<hr />
<h3 id="인라인-뷰">인라인 뷰</h3>
<p><code>FROM</code> 절에서 사용하는 서브쿼리를 인라인 뷰 또는 파생 테이블이라고 한다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    employee_count
FROM (
    SELECT
        department_id,
        COUNT(*) AS employee_count
    FROM employees
    GROUP BY department_id
) department_summary
WHERE employee_count &gt;= 5;</code></pre>
<p>동작 과정은 다음과 같다.</p>
<pre><code class="language-text">1. 서브쿼리에서 부서별 직원 수 집계
2. 집계 결과를 임시 테이블처럼 사용
3. 직원이 5명 이상인 부서만 조회</code></pre>
<hr />
<h3 id="상관-서브쿼리">상관 서브쿼리</h3>
<p>상관 서브쿼리는 바깥쪽 쿼리의 현재 행을 참조한다.</p>
<pre><code class="language-sql">SELECT
    e.employee_id,
    e.first_name,
    e.department_id,
    e.salary
FROM employees e
WHERE e.salary &gt; (
    SELECT AVG(sub.salary)
    FROM employees sub
    WHERE sub.department_id = e.department_id
);</code></pre>
<p>각 직원이 자신의 부서 평균보다 높은 급여를 받는지 확인한다.</p>
<p>서브쿼리 내부에서 바깥쪽 쿼리의 <code>e.department_id</code>를 사용하고 있다.</p>
<pre><code class="language-text">현재 직원의 부서 확인
→ 해당 부서의 평균 급여 계산
→ 현재 직원의 급여와 비교</code></pre>
<hr />
<h3 id="exists">EXISTS</h3>
<p><code>EXISTS</code>는 서브쿼리의 실제 반환값보다 행의 존재 여부를 확인할 때 사용한다.</p>
<pre><code class="language-sql">SELECT
    d.department_id,
    d.department_name
FROM departments d
WHERE EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.department_id
);</code></pre>
<p>직원이 한 명 이상 존재하는 부서만 조회한다.</p>
<p>반대로 직원이 없는 부서를 찾으려면 <code>NOT EXISTS</code>를 사용한다.</p>
<pre><code class="language-sql">SELECT
    d.department_id,
    d.department_name
FROM departments d
WHERE NOT EXISTS (
    SELECT 1
    FROM employees e
    WHERE e.department_id = d.department_id
);</code></pre>
<hr />
<h3 id="not-in과-null-주의점">NOT IN과 NULL 주의점</h3>
<p>다음처럼 <code>NOT IN</code>을 이용해 직원이 없는 부서를 찾을 수도 있어 보인다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    department_name
FROM departments
WHERE department_id NOT IN (
    SELECT department_id
    FROM employees
);</code></pre>
<p>하지만 서브쿼리 결과에 <code>NULL</code>이 포함되면 비교 결과가 예상과 다르게 나타날 수 있다.</p>
<p>SQL에서 <code>NULL</code>은 값이 없다는 의미이지 일반적인 값처럼 비교할 수 있는 대상이 아니기 때문이다.</p>
<p>존재하지 않는 데이터를 찾는 경우에는 <code>NOT EXISTS</code>가 의도를 더 명확하게 표현하는 경우가 많다.</p>
<hr />
<h2 id="집합-연산자">집합 연산자</h2>
<p>집합 연산자는 여러 <code>SELECT</code> 문의 결과를 행 단위로 결합한다.</p>
<p>대표적인 집합 연산자는 다음과 같다.</p>
<table>
<thead>
<tr>
<th>연산자</th>
<th>역할</th>
</tr>
</thead>
<tbody><tr>
<td><code>UNION</code></td>
<td>두 결과를 합치고 중복 제거</td>
</tr>
<tr>
<td><code>UNION ALL</code></td>
<td>두 결과를 중복 제거 없이 합침</td>
</tr>
<tr>
<td><code>INTERSECT</code></td>
<td>양쪽 결과에 모두 존재하는 행</td>
</tr>
<tr>
<td><code>EXCEPT</code></td>
<td>첫 번째 결과에만 존재하는 행</td>
</tr>
</tbody></table>
<p>집합 연산자를 사용하려면 일반적으로 다음 조건을 만족해야 한다.</p>
<ul>
<li>각 <code>SELECT</code>가 반환하는 컬럼 수가 같아야 한다.</li>
<li>같은 위치의 컬럼 자료형이 서로 호환되어야 한다.</li>
<li>최종 컬럼명은 첫 번째 <code>SELECT</code>의 컬럼명을 따른다.</li>
</ul>
<hr />
<h3 id="union">UNION</h3>
<p><code>UNION</code>은 두 결과를 합친 뒤 중복 행을 제거한다.</p>
<pre><code class="language-sql">SELECT email
FROM customers

UNION

SELECT email
FROM employees;</code></pre>
<p>고객과 직원의 이메일을 합치되 동일한 이메일은 한 번만 반환한다.</p>
<p>중복 제거를 위해 추가 비교나 정렬 작업이 필요할 수 있다.</p>
<hr />
<h3 id="union-all">UNION ALL</h3>
<p><code>UNION ALL</code>은 중복을 제거하지 않고 두 결과를 그대로 연결한다.</p>
<pre><code class="language-sql">SELECT email
FROM customers

UNION ALL

SELECT email
FROM employees;</code></pre>
<p>중복 제거가 필요하지 않다면 <code>UNION ALL</code>이 불필요한 중복 제거 작업을 수행하지 않기 때문에 더 적합할 수 있다.</p>
<pre><code class="language-text">UNION
→ 합친 뒤 중복 제거

UNION ALL
→ 그대로 합침</code></pre>
<hr />
<h3 id="intersect">INTERSECT</h3>
<p><code>INTERSECT</code>는 두 결과에 모두 존재하는 행만 반환한다.</p>
<pre><code class="language-sql">SELECT email
FROM customers

INTERSECT

SELECT email
FROM employees;</code></pre>
<p>직원이면서 고객으로도 등록된 이메일을 찾는 것과 같은 의미다.</p>
<hr />
<h3 id="except">EXCEPT</h3>
<p><code>EXCEPT</code>는 첫 번째 결과에는 존재하지만 두 번째 결과에는 존재하지 않는 행을 반환한다.</p>
<pre><code class="language-sql">SELECT department_id
FROM departments

EXCEPT

SELECT department_id
FROM employees
WHERE department_id IS NOT NULL;</code></pre>
<p>직원이 배정되지 않은 부서 번호를 찾을 수 있다.</p>
<hr />
<h2 id="join과-집합-연산자의-차이">JOIN과 집합 연산자의 차이</h2>
<p>JOIN과 집합 연산자는 모두 여러 테이블을 활용하지만 결합 방향이 다르다.</p>
<pre><code class="language-text">JOIN
→ 컬럼을 옆으로 결합

집합 연산자
→ 행을 아래로 결합</code></pre>
<p>예를 들어 다음 JOIN은 직원 정보 옆에 부서명을 붙인다.</p>
<pre><code class="language-sql">SELECT
    e.employee_id,
    e.first_name,
    d.department_name
FROM employees e
JOIN departments d
    ON e.department_id = d.department_id;</code></pre>
<p>반면 다음 <code>UNION ALL</code>은 두 조회 결과를 위아래로 이어 붙인다.</p>
<pre><code class="language-sql">SELECT employee_id, first_name
FROM current_employees

UNION ALL

SELECT employee_id, first_name
FROM retired_employees;</code></pre>
<hr />
<h1 id="cte와-view">CTE와 VIEW</h1>
<p>CTE와 VIEW는 모두 쿼리 결과에 이름을 붙여 테이블처럼 사용할 수 있게 한다.</p>
<p>하지만 사용 범위와 목적이 다르다.</p>
<pre><code class="language-text">CTE
→ 하나의 SQL 문 안에서만 사용하는 임시 이름

VIEW
→ 데이터베이스에 저장해 여러 SQL에서 재사용하는 객체</code></pre>
<hr />
<h2 id="cte">CTE</h2>
<p>CTE는 Common Table Expression의 약자다.</p>
<p><code>WITH</code> 절을 사용해 쿼리의 중간 결과에 이름을 지정한다.</p>
<pre><code class="language-sql">WITH department_summary AS (
    SELECT
        department_id,
        COUNT(*) AS employee_count,
        AVG(salary) AS average_salary
    FROM employees
    GROUP BY department_id
)
SELECT
    department_id,
    employee_count,
    average_salary
FROM department_summary
WHERE employee_count &gt;= 5;</code></pre>
<p><code>department_summary</code>는 실제 테이블이 아니라 이 SQL 문이 실행되는 동안만 사용할 수 있는 이름이다.</p>
<hr />
<h3 id="cte를-사용하는-이유">CTE를 사용하는 이유</h3>
<p>복잡한 쿼리를 인라인 뷰로 계속 중첩하면 구조를 파악하기 어려워진다.</p>
<pre><code class="language-sql">SELECT *
FROM (
    SELECT
        department_id,
        COUNT(*) AS employee_count
    FROM employees
    WHERE salary &gt;= 5000
    GROUP BY department_id
) summary
WHERE employee_count &gt;= 5;</code></pre>
<p>CTE를 사용하면 처리 단계에 이름을 붙일 수 있다.</p>
<pre><code class="language-sql">WITH high_salary_employees AS (
    SELECT
        employee_id,
        department_id,
        salary
    FROM employees
    WHERE salary &gt;= 5000
),
department_summary AS (
    SELECT
        department_id,
        COUNT(*) AS employee_count,
        AVG(salary) AS average_salary
    FROM high_salary_employees
    GROUP BY department_id
)
SELECT *
FROM department_summary
WHERE employee_count &gt;= 5;</code></pre>
<p>다음과 같은 흐름이 쿼리 자체에 드러난다.</p>
<pre><code class="language-text">1. 고액 급여 직원 추출
2. 부서별 통계 계산
3. 직원 수 조건 적용</code></pre>
<p>CTE의 가장 큰 장점은 단순히 쿼리를 짧게 만드는 것이 아니라 <strong>복잡한 처리 흐름을 단계별로 읽을 수 있게 만드는 것</strong>이다.</p>
<hr />
<h3 id="여러-cte-연결하기">여러 CTE 연결하기</h3>
<p>하나의 <code>WITH</code> 절에서 여러 CTE를 정의할 수 있다.</p>
<pre><code class="language-sql">WITH employee_base AS (
    SELECT
        employee_id,
        department_id,
        salary,
        EXTRACT(YEAR FROM hire_date) AS hire_year
    FROM employees
),
yearly_summary AS (
    SELECT
        hire_year,
        COUNT(*) AS employee_count,
        SUM(salary) AS total_salary
    FROM employee_base
    GROUP BY hire_year
)
SELECT *
FROM yearly_summary
ORDER BY hire_year;</code></pre>
<p>뒤쪽 CTE에서 앞쪽 CTE의 결과를 사용할 수 있다.</p>
<hr />
<h3 id="재귀-cte">재귀 CTE</h3>
<p>재귀 CTE는 이전 단계에서 생성된 결과를 다시 참조하면서 반복적으로 데이터를 탐색한다.</p>
<p>조직도처럼 계층 구조를 조회할 때 사용할 수 있다.</p>
<pre><code class="language-sql">WITH RECURSIVE organization AS (
    SELECT
        employee_id,
        first_name,
        manager_id,
        1 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT
        e.employee_id,
        e.first_name,
        e.manager_id,
        o.depth + 1
    FROM employees e
    JOIN organization o
        ON e.manager_id = o.employee_id
)
SELECT *
FROM organization
ORDER BY depth, employee_id;</code></pre>
<p>재귀 CTE는 두 부분으로 구성된다.</p>
<pre><code class="language-text">기준 쿼리
→ 탐색의 시작점

재귀 쿼리
→ 이전 결과와 연결되는 다음 데이터 탐색</code></pre>
<p>재귀 CTE는 다음과 같은 데이터에 활용할 수 있다.</p>
<ul>
<li>조직도</li>
<li>카테고리 계층</li>
<li>게시글과 대댓글</li>
<li>폴더 구조</li>
<li>상위·하위 항목 탐색</li>
</ul>
<hr />
<h2 id="view">VIEW</h2>
<p>VIEW는 <code>SELECT</code> 쿼리에 이름을 붙여 데이터베이스 객체로 저장한 것이다.</p>
<pre><code class="language-sql">CREATE VIEW employee_department_view AS
SELECT
    e.employee_id,
    e.first_name,
    e.salary,
    d.department_name
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.department_id;</code></pre>
<p>생성한 VIEW는 테이블처럼 조회할 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM employee_department_view;</code></pre>
<p>일반 VIEW는 조회 결과 자체를 별도로 저장하는 것이 아니라, 조회에 사용할 SQL 정의를 저장한다.</p>
<p>따라서 기반 테이블의 데이터가 변경되면 VIEW 조회 결과에도 반영된다.</p>
<hr />
<h3 id="view를-사용하는-이유">VIEW를 사용하는 이유</h3>
<h4 id="복잡한-쿼리-재사용">복잡한 쿼리 재사용</h4>
<p>여러 SQL에서 반복되는 JOIN이나 계산 로직을 VIEW로 만들 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM employee_department_view
WHERE salary &gt;= 10000;</code></pre>
<h4 id="사용자에게-단순한-구조-제공">사용자에게 단순한 구조 제공</h4>
<p>사용자는 내부의 복잡한 JOIN 구조를 몰라도 VIEW를 일반 테이블처럼 조회할 수 있다.</p>
<h4 id="컬럼-노출-제한">컬럼 노출 제한</h4>
<p>민감하거나 불필요한 컬럼을 제외한 VIEW를 제공할 수 있다.</p>
<pre><code class="language-sql">CREATE VIEW public_employee_view AS
SELECT
    employee_id,
    first_name,
    department_id
FROM employees;</code></pre>
<p>원본 테이블에 급여나 개인 정보가 있더라도 VIEW에서는 필요한 컬럼만 노출할 수 있다.</p>
<hr />
<h3 id="일반-view와-materialized-view">일반 VIEW와 Materialized View</h3>
<p>일반 VIEW는 쿼리 정의를 저장하고 조회할 때마다 기반 테이블을 이용해 결과를 계산한다.</p>
<p>Materialized View는 조회 결과를 실제로 저장한다.</p>
<pre><code class="language-sql">CREATE MATERIALIZED VIEW department_salary_summary AS
SELECT
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS average_salary
FROM employees
GROUP BY department_id;</code></pre>
<p>저장된 결과를 최신 데이터로 갱신하려면 새로고침이 필요하다.</p>
<pre><code class="language-sql">REFRESH MATERIALIZED VIEW department_salary_summary;</code></pre>
<p>두 방식을 비교하면 다음과 같다.</p>
<table>
<thead>
<tr>
<th>구분</th>
<th>일반 VIEW</th>
<th>Materialized View</th>
</tr>
</thead>
<tbody><tr>
<td>저장 대상</td>
<td>SQL 정의</td>
<td>SQL 실행 결과</td>
</tr>
<tr>
<td>데이터 최신성</td>
<td>조회 시 기반 테이블 반영</td>
<td>새로고침 전까지 기존 결과</td>
</tr>
<tr>
<td>조회 속도</td>
<td>원본 쿼리 비용 발생</td>
<td>미리 계산된 결과 조회</td>
</tr>
<tr>
<td>주요 용도</td>
<td>쿼리 재사용과 추상화</td>
<td>복잡한 집계 결과 캐싱</td>
</tr>
</tbody></table>
<hr />
<h2 id="cte와-view-비교">CTE와 VIEW 비교</h2>
<table>
<thead>
<tr>
<th>구분</th>
<th>CTE</th>
<th>VIEW</th>
</tr>
</thead>
<tbody><tr>
<td>사용 범위</td>
<td>하나의 SQL 문</td>
<td>데이터베이스 전체</td>
</tr>
<tr>
<td>유지 기간</td>
<td>SQL 실행 동안</td>
<td>삭제 전까지</td>
</tr>
<tr>
<td>주요 목적</td>
<td>쿼리 단계 구조화</td>
<td>반복 쿼리 재사용</td>
</tr>
<tr>
<td>저장 방식</td>
<td>쿼리 내부 정의</td>
<td>DB 객체로 저장</td>
</tr>
<tr>
<td>재사용성</td>
<td>해당 SQL 안에서만</td>
<td>여러 SQL과 사용자 가능</td>
</tr>
</tbody></table>
<p>복잡한 쿼리 하나를 이해하기 쉽게 나누려면 CTE가 적합하다.</p>
<p>여러 곳에서 동일한 조회 로직을 반복 사용한다면 VIEW가 적합하다.</p>
<hr />
<h1 id="윈도우-함수">윈도우 함수</h1>
<p>집계 함수와 <code>GROUP BY</code>를 사용하면 여러 행이 하나의 그룹 결과로 축약된다.</p>
<pre><code class="language-sql">SELECT
    department_id,
    AVG(salary) AS average_salary
FROM employees
GROUP BY department_id;</code></pre>
<p>이 결과에서는 개별 직원 행이 사라지고 부서별 한 행만 남는다.</p>
<p>하지만 다음과 같은 요구사항이 있을 수 있다.</p>
<blockquote>
<p>직원 정보는 그대로 유지하면서 각 직원 옆에 부서 평균 급여를 표시하고 싶다.</p>
</blockquote>
<p>이때 사용하는 것이 윈도우 함수다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    first_name,
    department_id,
    salary,
    AVG(salary) OVER (
        PARTITION BY department_id
    ) AS department_average_salary
FROM employees;</code></pre>
<p>결과는 직원별 행을 유지하면서 부서 평균을 추가한다.</p>
<pre><code class="language-text">employee_id | department_id | salary | department_average
------------+---------------+--------+-------------------
101         | 10            | 9000   | 8000
102         | 10            | 7000   | 8000
103         | 20            | 6000   | 5500
104         | 20            | 5000   | 5500</code></pre>
<hr />
<h2 id="group-by와-윈도우-함수의-차이">GROUP BY와 윈도우 함수의 차이</h2>
<pre><code class="language-text">GROUP BY
→ 여러 행을 하나의 그룹 결과로 축약

Window Function
→ 기존 행을 유지하면서 분석 결과를 추가</code></pre>
<p>이 차이가 윈도우 함수를 이해하는 가장 중요한 기준이다.</p>
<hr />
<h2 id="윈도우-함수의-기본-구조">윈도우 함수의 기본 구조</h2>
<pre><code class="language-sql">윈도우함수() OVER (
    PARTITION BY 그룹 기준
    ORDER BY 정렬 기준
    ROWS 또는 RANGE 윈도우 범위
)</code></pre>
<p>각 구성 요소의 역할은 다음과 같다.</p>
<h3 id="partition-by">PARTITION BY</h3>
<p>전체 행을 계산 단위별로 나눈다.</p>
<pre><code class="language-sql">AVG(salary) OVER (
    PARTITION BY department_id
)</code></pre>
<p>부서별로 각각 평균을 계산한다.</p>
<p><code>GROUP BY</code>와 비슷하게 그룹을 만들지만, 결과 행을 하나로 줄이지 않는다.</p>
<h3 id="order-by">ORDER BY</h3>
<p>각 파티션 내부의 순서를 정한다.</p>
<pre><code class="language-sql">RANK() OVER (
    PARTITION BY department_id
    ORDER BY salary DESC
)</code></pre>
<p>부서별로 급여가 높은 순서대로 순위를 계산한다.</p>
<h3 id="window-frame">Window Frame</h3>
<p>현재 행을 기준으로 계산에 포함할 행의 범위를 결정한다.</p>
<pre><code class="language-sql">ROWS BETWEEN UNBOUNDED PRECEDING
         AND CURRENT ROW</code></pre>
<p>파티션의 첫 번째 행부터 현재 행까지를 계산 범위로 사용한다.</p>
<hr />
<h2 id="순위-함수">순위 함수</h2>
<p>대표적인 순위 함수는 다음과 같다.</p>
<ul>
<li><code>ROW_NUMBER()</code></li>
<li><code>RANK()</code></li>
<li><code>DENSE_RANK()</code></li>
</ul>
<h3 id="row_number">ROW_NUMBER</h3>
<p>동점 여부와 관계없이 각 행에 고유한 번호를 부여한다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    department_id,
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY department_id
        ORDER BY salary DESC
    ) AS row_number
FROM employees;</code></pre>
<pre><code class="language-text">salary | ROW_NUMBER
-------+-----------
9000   | 1
8000   | 2
8000   | 3
7000   | 4</code></pre>
<h3 id="rank">RANK</h3>
<p>동일한 값에는 같은 순위를 부여하고 다음 순위를 건너뛴다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    salary,
    RANK() OVER (
        ORDER BY salary DESC
    ) AS salary_rank
FROM employees;</code></pre>
<pre><code class="language-text">salary | RANK
-------+-----
9000   | 1
8000   | 2
8000   | 2
7000   | 4</code></pre>
<h3 id="dense_rank">DENSE_RANK</h3>
<p>동일한 값에는 같은 순위를 부여하지만 다음 순위를 건너뛰지 않는다.</p>
<pre><code class="language-text">salary | DENSE_RANK
-------+-----------
9000   | 1
8000   | 2
8000   | 2
7000   | 3</code></pre>
<hr />
<h2 id="순위-함수-비교">순위 함수 비교</h2>
<table>
<thead>
<tr>
<th>함수</th>
<th>동점 처리</th>
<th>다음 순위</th>
</tr>
</thead>
<tbody><tr>
<td><code>ROW_NUMBER()</code></td>
<td>서로 다른 번호</td>
<td>연속</td>
</tr>
<tr>
<td><code>RANK()</code></td>
<td>같은 순위</td>
<td>건너뜀</td>
</tr>
<tr>
<td><code>DENSE_RANK()</code></td>
<td>같은 순위</td>
<td>연속</td>
</tr>
</tbody></table>
<hr />
<h3 id="예시-부서별-급여-상위-3명-조회">[예시] 부서별 급여 상위 3명 조회</h3>
<p>윈도우 함수의 결과를 조건으로 필터링하려면 서브쿼리나 CTE를 사용할 수 있다.</p>
<pre><code class="language-sql">WITH ranked_employees AS (
    SELECT
        employee_id,
        first_name,
        department_id,
        salary,
        ROW_NUMBER() OVER (
            PARTITION BY department_id
            ORDER BY salary DESC
        ) AS salary_rank
    FROM employees
)
SELECT
    employee_id,
    first_name,
    department_id,
    salary
FROM ranked_employees
WHERE salary_rank &lt;= 3;</code></pre>
<p>이 쿼리는 부서별 급여 상위 3명을 조회한다.</p>
<hr />
<h2 id="lag와-lead">LAG와 LEAD</h2>
<p><code>LAG()</code>는 현재 행을 기준으로 이전 행의 값을 가져온다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    hire_date,
    salary,
    LAG(salary) OVER (
        ORDER BY hire_date
    ) AS previous_salary
FROM employees;</code></pre>
<p>이전 행과 현재 행의 차이도 계산할 수 있다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    hire_date,
    salary,
    salary - LAG(salary) OVER (
        ORDER BY hire_date
    ) AS salary_difference
FROM employees;</code></pre>
<p><code>LEAD()</code>는 다음 행의 값을 가져온다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    hire_date,
    salary,
    LEAD(salary) OVER (
        ORDER BY hire_date
    ) AS next_salary
FROM employees;</code></pre>
<p><code>LAG</code>와 <code>LEAD</code>는 다음과 같은 시계열 분석에 활용할 수 있다.</p>
<ul>
<li>전월 대비 매출</li>
<li>전일 대비 접속자 수</li>
<li>이전 주문과의 시간 차이</li>
<li>다음 일정까지 남은 시간</li>
<li>이전 순위와 현재 순위 비교</li>
</ul>
<hr />
<h2 id="누적-합계">누적 합계</h2>
<p>집계 함수도 <code>OVER</code>와 함께 사용하면 윈도우 함수가 된다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    hire_date,
    salary,
    SUM(salary) OVER (
        ORDER BY hire_date
        ROWS BETWEEN UNBOUNDED PRECEDING
                 AND CURRENT ROW
    ) AS cumulative_salary
FROM employees;</code></pre>
<p>첫 번째 행부터 현재 행까지 급여를 누적한다.</p>
<pre><code class="language-text">salary | cumulative_salary
-------+------------------
3000   | 3000
4000   | 7000
5000   | 12000
6000   | 18000</code></pre>
<p>다음처럼 축약해서 작성되는 경우도 있다.</p>
<pre><code class="language-sql">SUM(salary) OVER (
    ORDER BY hire_date
)</code></pre>
<p>다만 계산 범위를 명확하게 표현하고 싶다면 Window Frame을 직접 작성하는 것이 좋다.</p>
<hr />
<h2 id="이동-평균">이동 평균</h2>
<p>현재 행과 주변 행을 범위로 지정하면 이동 평균을 계산할 수 있다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    hire_date,
    salary,
    AVG(salary) OVER (
        ORDER BY hire_date
        ROWS BETWEEN 2 PRECEDING
                 AND CURRENT ROW
    ) AS moving_average
FROM employees;</code></pre>
<p>현재 행과 이전 두 행, 총 세 행의 평균을 계산한다.</p>
<p>이동 평균은 데이터의 단기적인 변화보다 전체적인 흐름을 확인할 때 유용하다.</p>
<hr />
<h2 id="first_value와-last_value">FIRST_VALUE와 LAST_VALUE</h2>
<p><code>FIRST_VALUE()</code>는 윈도우 범위의 첫 번째 값을 가져온다.</p>
<pre><code class="language-sql">SELECT
    employee_id,
    department_id,
    salary,
    FIRST_VALUE(salary) OVER (
        PARTITION BY department_id
        ORDER BY salary DESC
    ) AS department_highest_salary
FROM employees;</code></pre>
<p>부서별 최고 급여를 각 직원 행에 표시한다.</p>
<hr />
<h3 id="last_value의-window-frame-주의점">LAST_VALUE의 Window Frame 주의점</h3>
<p>다음처럼 작성하면 <code>LAST_VALUE()</code>가 예상과 다르게 현재 행의 값을 반환할 수 있다.</p>
<pre><code class="language-sql">LAST_VALUE(salary) OVER (
    PARTITION BY department_id
    ORDER BY salary DESC
)</code></pre>
<p>윈도우의 기본 범위가 현재 행까지만 설정될 수 있기 때문이다.</p>
<p>파티션 전체의 마지막 값을 조회하려면 범위를 직접 지정한다.</p>
<pre><code class="language-sql">LAST_VALUE(salary) OVER (
    PARTITION BY department_id
    ORDER BY salary DESC
    ROWS BETWEEN UNBOUNDED PRECEDING
             AND UNBOUNDED FOLLOWING
)</code></pre>
<p>윈도우 함수를 사용할 때는 함수 이름뿐 아니라 계산 범위가 어디까지인지도 함께 확인해야 한다.</p>
<hr />
<h1 id="요약">요약</h1>
<p>이번에 학습한 기능들은 모두 데이터를 조회하고 가공하기 위해 사용하지만 해결하는 문제가 다르다.</p>
<table>
<thead>
<tr>
<th>기능</th>
<th>주요 역할</th>
</tr>
</thead>
<tbody><tr>
<td>집계 함수</td>
<td>여러 행을 하나의 통계값으로 요약</td>
</tr>
<tr>
<td><code>GROUP BY</code></td>
<td>같은 값을 가진 행을 그룹화</td>
</tr>
<tr>
<td><code>HAVING</code></td>
<td>집계가 완료된 그룹을 필터링</td>
</tr>
<tr>
<td>NLJ</td>
<td>각 행마다 상대 테이블 탐색</td>
</tr>
<tr>
<td>HJ</td>
<td>해시 테이블을 생성해 동등 JOIN 수행</td>
</tr>
<tr>
<td>SMJ</td>
<td>정렬된 두 입력을 순차적으로 병합</td>
</tr>
<tr>
<td>서브쿼리</td>
<td>한 쿼리의 결과를 다른 쿼리에서 사용</td>
</tr>
<tr>
<td>집합 연산자</td>
<td>여러 SELECT 결과를 행 단위로 결합</td>
</tr>
<tr>
<td>CTE</td>
<td>하나의 쿼리를 단계별로 구조화</td>
</tr>
<tr>
<td>VIEW</td>
<td>반복되는 조회 로직을 DB 객체로 저장</td>
</tr>
<tr>
<td>윈도우 함수</td>
<td>행을 유지하며 순위·누적·비교 수행</td>
</tr>
</tbody></table>
<hr />
<pre><code class="language-text">여러 행을 통계값으로 줄여야 하는가?
→ 집계 함수와 GROUP BY

JOIN이 실제로 어떻게 처리되는지 확인해야 하는가?
→ 실행 계획과 NLJ, HJ, SMJ

다른 쿼리의 결과가 필요한가?
→ 서브쿼리

여러 조회 결과를 위아래로 합쳐야 하는가?
→ 집합 연산자

복잡한 쿼리를 단계별로 표현해야 하는가?
→ CTE

반복되는 조회 구조를 재사용해야 하는가?
→ VIEW

기존 행을 유지하면서 순위나 누적값을 계산해야 하는가?
→ 윈도우 함수</code></pre>