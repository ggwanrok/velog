<h2 id="간단-미리보기">간단 미리보기</h2>
<pre><code class="language-text">PL/pgSQL
→ 함수(Function)
→ 프로시저(Procedure)
→ 트리거(Trigger)</code></pre>
<ul>
<li><strong>PL/pgSQL</strong>: 함수·프로시저·트리거 함수의 내부 로직을 작성하는 언어</li>
<li><strong>Function</strong>: 값을 계산하거나 조회 결과를 반환</li>
<li><strong>Procedure</strong>: 여러 SQL을 하나의 업무 절차로 묶어 실행</li>
<li><strong>Trigger</strong>: 테이블 이벤트가 발생했을 때 자동 실행</li>
</ul>
<hr />
<h1 id="plpgsql">PL/pgSQL</h1>
<p>PL/pgSQL은 일반 SQL에 다음 기능을 추가한 PostgreSQL의 절차형 언어다.</p>
<pre><code class="language-text">변수
조건문
반복문
예외 처리
동적 SQL</code></pre>
<p>기본 구조는 다음과 같다.</p>
<pre><code class="language-sql">DECLARE
    v_total numeric := 0;
BEGIN
    -- 실제 실행 로직

EXCEPTION
    WHEN OTHERS THEN
        -- 오류 처리
END;</code></pre>
<h2 id="블록-구조">블록 구조</h2>
<table>
<thead>
<tr>
<th>구역</th>
<th>역할</th>
</tr>
</thead>
<tbody><tr>
<td><code>DECLARE</code></td>
<td>지역 변수 선언, 생략 가능</td>
</tr>
<tr>
<td><code>BEGIN</code></td>
<td>실행 로직 시작</td>
</tr>
<tr>
<td><code>EXCEPTION</code></td>
<td>발생한 오류 처리, 생략 가능</td>
</tr>
<tr>
<td><code>END</code></td>
<td>블록 종료</td>
</tr>
</tbody></table>
<p>매개변수는 <code>CREATE FUNCTION</code>이나 <code>CREATE PROCEDURE</code>에서 선언하고, 내부에서만 사용할 변수는 <code>DECLARE</code>에 선언한다.</p>
<hr />
<h2 id="조회-결과를-변수에-저장">조회 결과를 변수에 저장</h2>
<pre><code class="language-sql">SELECT total_amount
INTO v_total
FROM orders
WHERE order_id = p_order_id;</code></pre>
<p><code>SELECT INTO</code>는 조회 결과를 화면에 출력하는 것이 아니라 <strong>PL/pgSQL 변수에 저장</strong>한다.</p>
<h3 id="into-strict"><code>INTO STRICT</code></h3>
<pre><code class="language-sql">SELECT *
INTO STRICT v_order
FROM orders
WHERE order_id = p_order_id;</code></pre>
<ul>
<li>결과가 0행이면 <code>NO_DATA_FOUND</code></li>
<li>결과가 2행 이상이면 <code>TOO_MANY_ROWS</code></li>
<li>정확히 1행이어야 정상 처리</li>
</ul>
<hr />
<h2 id="type과-rowtype"><code>%TYPE</code>과 <code>%ROWTYPE</code></h2>
<pre><code class="language-sql">v_price products.unit_price%TYPE;
v_order orders%ROWTYPE;</code></pre>
<ul>
<li><code>%TYPE</code>: 특정 컬럼과 같은 자료형</li>
<li><code>%ROWTYPE</code>: 테이블 한 행 전체와 같은 구조</li>
</ul>
<p>테이블 컬럼 타입이 변경돼도 변수 타입을 일일이 수정할 필요가 줄어든다.</p>
<hr />
<h2 id="found와-perform"><code>FOUND</code>와 <code>PERFORM</code></h2>
<h3 id="found"><code>FOUND</code></h3>
<p>직전에 실행한 SQL이 행을 처리했는지 확인한다.</p>
<pre><code class="language-sql">UPDATE products
SET stock_qty = stock_qty - p_quantity
WHERE product_id = p_product_id
  AND stock_qty &gt;= p_quantity;

IF NOT FOUND THEN
    RAISE EXCEPTION '상품이 없거나 재고가 부족합니다.';
END IF;</code></pre>
<h3 id="perform"><code>PERFORM</code></h3>
<p>함수의 반환값이 필요하지 않고 실행만 필요할 때 사용한다.</p>
<pre><code class="language-sql">PERFORM fn_reserve_stock(p_product_id, p_quantity);</code></pre>
<hr />
<h2 id="조건문과-반복문">조건문과 반복문</h2>
<pre><code class="language-sql">IF p_quantity &lt;= 0 THEN
    RAISE EXCEPTION '수량은 1 이상이어야 합니다.';
ELSIF p_quantity &gt;= 100 THEN
    ...
ELSE
    ...
END IF;</code></pre>
<p>반복문은 <code>LOOP</code>, <code>WHILE</code>, <code>FOR</code> 등을 사용할 수 있다.</p>
<p>다만 여러 행에 같은 처리를 적용한다면 반복문보다 다음과 같은 <strong>집합 기반 SQL</strong>을 우선한다.</p>
<pre><code class="language-sql">UPDATE products
SET unit_price = unit_price * 0.9
WHERE unit_price &gt;= 70000;</code></pre>
<p>반복문은 행마다 서로 다른 판단이나 순차 의존성이 있을 때 사용한다.</p>
<hr />
<h2 id="반환-방식">반환 방식</h2>
<h3 id="return-값"><code>RETURN 값</code></h3>
<p>값 하나를 반환하고 함수를 즉시 종료한다.</p>
<pre><code class="language-sql">RETURN round(v_result, 2);</code></pre>
<h3 id="return-query"><code>RETURN QUERY</code></h3>
<p>SELECT 결과 전체를 함수 결과에 추가한다.</p>
<pre><code class="language-sql">RETURN QUERY
SELECT product_id, product_name, stock_qty
FROM products
WHERE stock_qty &lt; p_threshold;</code></pre>
<p><code>RETURN QUERY</code> 이후에도 다음 문장이 실행될 수 있다.</p>
<h3 id="return-next"><code>RETURN NEXT</code></h3>
<p>현재 출력 변수에 담긴 값을 한 행으로 추가한다.</p>
<pre><code class="language-sql">product_name := '키보드';
discount_percent := 10;
discounted_price := 80000;

RETURN NEXT;</code></pre>
<p>정리하면:</p>
<pre><code class="language-text">RETURN 값
→ 결과 하나 반환 + 함수 종료

RETURN QUERY
→ SELECT 결과 전체 추가 + 함수 계속 실행

RETURN NEXT
→ 현재 행 하나 추가 + 함수 계속 실행</code></pre>
<hr />
<h2 id="raise와-exception"><code>RAISE</code>와 <code>EXCEPTION</code></h2>
<p>둘은 반드시 함께 사용할 필요가 없다.</p>
<pre><code class="language-text">RAISE
→ 메시지나 오류를 발생시킴

EXCEPTION
→ 발생한 오류를 잡아 처리함</code></pre>
<h3 id="직접-오류-발생">직접 오류 발생</h3>
<pre><code class="language-sql">IF p_quantity &lt;= 0 THEN
    RAISE EXCEPTION '수량 오류: %', p_quantity
        USING ERRCODE = '22003';
END IF;</code></pre>
<h3 id="오류를-잡아-대체-처리">오류를 잡아 대체 처리</h3>
<pre><code class="language-sql">BEGIN
    SELECT total_amount
    INTO STRICT v_total
    FROM orders
    WHERE order_id = p_order_id;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        v_total := 0;
END;</code></pre>
<h3 id="오류를-잡은-뒤-다시-전달">오류를 잡은 뒤 다시 전달</h3>
<pre><code class="language-sql">EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '처리 중 오류 발생';
        RAISE;</code></pre>
<p>마지막의 인수 없는 <code>RAISE;</code>는 현재 잡은 원래 오류를 다시 외부로 전달한다.</p>
<hr />
<h1 id="function">Function</h1>
<p>함수는 주로 <strong>값을 계산하거나 데이터를 조회해 결과를 반환</strong>한다.</p>
<pre><code class="language-sql">SELECT fn_name(...);</code></pre>
<p>함수는 SQL 문 안에서 사용할 수 있다.</p>
<pre><code class="language-sql">SELECT
    customer_name,
    fn_grade_discount_rate(customer_grade)
FROM customers;</code></pre>
<hr />
<h2 id="함수의-반환-형태">함수의 반환 형태</h2>
<h3 id="단일-값">단일 값</h3>
<pre><code class="language-sql">RETURNS numeric
RETURNS text
RETURNS jsonb</code></pre>
<pre><code class="language-sql">RETURN v_result;</code></pre>
<h3 id="여러-행과-컬럼">여러 행과 컬럼</h3>
<pre><code class="language-sql">RETURNS TABLE (
    product_id bigint,
    product_name varchar,
    stock_qty integer
)</code></pre>
<p>호출 결과는 일반 테이블처럼 사용할 수 있다.</p>
<pre><code class="language-sql">SELECT *
FROM fn_products_below_stock(70);</code></pre>
<hr />
<h2 id="language-sql과-language-plpgsql"><code>LANGUAGE SQL</code>과 <code>LANGUAGE plpgsql</code></h2>
<h3 id="language-sql"><code>LANGUAGE SQL</code></h3>
<p>한두 개의 단순한 SQL 문으로 끝날 때 적합하다.</p>
<pre><code class="language-sql">CREATE FUNCTION fn_tax_amount(
    p_amount numeric,
    p_rate numeric
)
RETURNS numeric
LANGUAGE sql
AS $$
    SELECT round(p_amount * p_rate, 2);
$$;</code></pre>
<h3 id="language-plpgsql"><code>LANGUAGE plpgsql</code></h3>
<p>다음 기능이 필요할 때 사용한다.</p>
<pre><code class="language-text">지역 변수
IF·CASE
반복문
예외 처리
동적 SQL</code></pre>
<p>가장 복잡한 언어를 쓰는 것이 아니라 <strong>가장 단순하게 표현 가능한 언어를 선택</strong>하는 것이 원칙이다.</p>
<hr />
<h2 id="함수-변동성">함수 변동성</h2>
<p>변동성은 옵티마이저에게 함수의 동작 특성을 알려주는 약속이다.</p>
<table>
<thead>
<tr>
<th>속성</th>
<th>의미</th>
<th>예시</th>
</tr>
</thead>
<tbody><tr>
<td><code>IMMUTABLE</code></td>
<td>같은 입력이면 항상 같은 결과</td>
<td>세금·할인율 계산</td>
</tr>
<tr>
<td><code>STABLE</code></td>
<td>하나의 SQL 문 안에서 결과가 안정적</td>
<td>테이블 조회 함수</td>
</tr>
<tr>
<td><code>VOLATILE</code></td>
<td>호출마다 결과나 DB 상태가 달라질 수 있음</td>
<td>DML, <code>random()</code></td>
</tr>
</tbody></table>
<pre><code class="language-text">순수 계산 → IMMUTABLE
테이블 조회 → STABLE
INSERT·UPDATE·DELETE → VOLATILE</code></pre>
<p>기본값은 <code>VOLATILE</code>이며, 확실할 때만 더 강한 속성을 지정한다.</p>
<hr />
<h2 id="strict"><code>STRICT</code></h2>
<pre><code class="language-sql">STRICT</code></pre>
<p>인자 중 하나라도 <code>NULL</code>이면 함수 본문을 실행하지 않고 바로 <code>NULL</code>을 반환한다.</p>
<p>따라서 <code>NULL</code> 자체를 특별한 의미로 사용해야 하는 함수에는 <code>STRICT</code>를 붙이면 안 된다.</p>
<p>예를 들어:</p>
<pre><code class="language-sql">fn_orders_by_status(NULL)</code></pre>
<p>에서 <code>NULL</code>을 “전체 상태 조회”로 사용한다면 <code>STRICT</code>를 붙이지 않아야 한다.</p>
<hr />
<h2 id="함수도-dml-가능">함수도 DML 가능</h2>
<p>PostgreSQL 함수도 권한이 있다면 데이터를 변경할 수 있다.</p>
<pre><code class="language-sql">UPDATE products
SET stock_qty = stock_qty - p_quantity
WHERE product_id = p_product_id
  AND stock_qty &gt;= p_quantity
RETURNING stock_qty
INTO v_remaining;</code></pre>
<p>다만 <code>SELECT fn_reserve_stock(...)</code>이 실제 데이터를 변경한다는 부작용이 있으므로 이름과 문서에서 명확히 드러내야 한다.</p>
<hr />
<h1 id="procedure">Procedure</h1>
<p>프로시저는 <strong>여러 SQL 문을 하나의 업무 절차로 묶는 객체</strong>다.</p>
<pre><code class="language-sql">CALL pr_name(...);</code></pre>
<p>예를 들어 주문 생성 프로시저는 다음 작업을 순서대로 수행한다.</p>
<pre><code class="language-text">입력값 검증
→ 고객 확인
→ 상품 확인 및 잠금
→ 재고 확인
→ 재고 차감
→ 주문 생성
→ 주문 상세 생성
→ 주문 번호 반환</code></pre>
<hr />
<h2 id="매개변수">매개변수</h2>
<table>
<thead>
<tr>
<th>종류</th>
<th>의미</th>
</tr>
</thead>
<tbody><tr>
<td><code>IN</code></td>
<td>입력값</td>
</tr>
<tr>
<td><code>OUT</code></td>
<td>처리 결과 출력</td>
</tr>
<tr>
<td><code>INOUT</code></td>
<td>입력받은 값을 수정해 출력</td>
</tr>
</tbody></table>
<pre><code class="language-sql">CREATE PROCEDURE pr_create_order(
    IN p_customer_id bigint,
    IN p_product_id bigint,
    IN p_quantity integer,
    INOUT p_order_id bigint
)</code></pre>
<p><code>p_order_id</code>는 호출할 때 입력되지만, 프로시저 내부에서 생성된 주문 번호로 변경되어 반환된다.</p>
<hr />
<h2 id="동시성-제어">동시성 제어</h2>
<p>여러 요청이 같은 상품 재고를 동시에 변경할 수 있다면 행을 잠가야 한다.</p>
<pre><code class="language-sql">SELECT *
INTO v_product
FROM products
WHERE product_id = p_product_id
FOR UPDATE;</code></pre>
<p>이후 재고를 확인하고 차감한다.</p>
<pre><code class="language-text">상품 행 잠금
→ 재고 확인
→ 재고 차감
→ 주문 생성</code></pre>
<p>잠금 없이 조회한 뒤 나중에 수정하면 여러 트랜잭션이 같은 재고를 동시에 사용했다고 판단할 수 있다.</p>
<hr />
<h2 id="트랜잭션-경계">트랜잭션 경계</h2>
<p>기본적으로 프로시저 내부에 <code>COMMIT</code>을 넣지 않고 호출자가 전체 트랜잭션을 관리한다.</p>
<pre><code class="language-sql">BEGIN;

CALL pr_create_order(...);

COMMIT;</code></pre>
<p>중간에 오류가 발생하면:</p>
<pre><code class="language-sql">ROLLBACK;</code></pre>
<p>으로 재고 차감, 주문 생성, 주문 상세 생성을 모두 취소할 수 있다.</p>
<blockquote>
<p>업무의 원자성은 프로시저 자체가 아니라 프로시저를 감싸는 트랜잭션 경계에서 만들어진다.</p>
</blockquote>
<p>프로시저 내부 <code>COMMIT</code>과 <code>ROLLBACK</code>은 최상위 <code>CALL</code> 등 여러 조건을 만족할 때만 가능하므로 일반적인 업무 프로시저에서는 신중하게 사용한다.</p>
<hr />
<h2 id="upsert와-멱등성">UPSERT와 멱등성</h2>
<pre><code class="language-sql">INSERT INTO customers(...)
VALUES (...)
ON CONFLICT (email_normalized)
DO UPDATE
SET customer_name = EXCLUDED.customer_name
RETURNING customer_id;</code></pre>
<p><code>UPSERT</code>를 사용하면 같은 요청이 반복돼도 중복 고객을 생성하지 않을 수 있다.</p>
<p>배치 작업에서는 <code>batch_key</code>를 별도 테이블에 먼저 기록해 같은 배치가 다시 실행되는 것을 막을 수 있다.</p>
<pre><code class="language-text">같은 키 + 같은 조건
→ 재실행하지 않고 기존 결과 반환

같은 키 + 다른 조건
→ 오류 처리</code></pre>
<hr />
<h1 id="trigger">Trigger</h1>
<p>트리거는 테이블에서 특정 이벤트가 발생했을 때 <strong>트리거 함수를 자동 실행</strong>한다.</p>
<pre><code class="language-text">INSERT
UPDATE
DELETE
→ Trigger
→ Trigger Function 실행</code></pre>
<p>트리거는 두 단계로 만든다.</p>
<pre><code class="language-text">1. RETURNS trigger인 함수 작성
2. CREATE TRIGGER로 이벤트와 함수 연결</code></pre>
<hr />
<h2 id="트리거-함수">트리거 함수</h2>
<pre><code class="language-sql">CREATE FUNCTION fn_audit_orders()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    ...
    RETURN NEW;
END;
$$;</code></pre>
<p>트리거 함수에는 일반 매개변수 대신 PostgreSQL이 특별한 값을 제공한다.</p>
<table>
<thead>
<tr>
<th>값</th>
<th>의미</th>
</tr>
</thead>
<tbody><tr>
<td><code>OLD</code></td>
<td>변경 전 행</td>
</tr>
<tr>
<td><code>NEW</code></td>
<td>변경 후 행</td>
</tr>
<tr>
<td><code>TG_OP</code></td>
<td><code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code></td>
</tr>
<tr>
<td><code>TG_TABLE_NAME</code></td>
<td>이벤트가 발생한 테이블</td>
</tr>
<tr>
<td><code>TG_TABLE_SCHEMA</code></td>
<td>테이블의 스키마</td>
</tr>
</tbody></table>
<hr />
<h2 id="실행-시점">실행 시점</h2>
<h3 id="before"><code>BEFORE</code></h3>
<p>원본 작업 전에 실행한다.</p>
<pre><code class="language-text">입력값 수정
유효성 검사
작업 차단</code></pre>
<h3 id="after"><code>AFTER</code></h3>
<p>원본 작업이 성공한 뒤 실행한다.</p>
<pre><code class="language-text">감사 로그
이력 저장
연관 테이블 동기화</code></pre>
<h3 id="instead-of"><code>INSTEAD OF</code></h3>
<p>주로 뷰에서 원래 작업 대신 트리거 로직을 실행한다.</p>
<hr />
<h2 id="실행-단위">실행 단위</h2>
<h3 id="for-each-row"><code>FOR EACH ROW</code></h3>
<p>변경된 각 행마다 실행된다.</p>
<pre><code class="language-sql">FOR EACH ROW</code></pre>
<p>100행이 변경되면 트리거 함수도 최대 100번 호출된다.</p>
<h3 id="for-each-statement"><code>FOR EACH STATEMENT</code></h3>
<p>SQL 문 한 번당 한 번 실행된다.</p>
<pre><code class="language-sql">FOR EACH STATEMENT</code></pre>
<p>대량 작업에서 행마다 다른 판단이 필요 없다면 Statement 트리거나 집합 기반 처리를 검토한다.</p>
<hr />
<h2 id="old와-new"><code>OLD</code>와 <code>NEW</code></h2>
<table>
<thead>
<tr>
<th>작업</th>
<th>OLD</th>
<th>NEW</th>
</tr>
</thead>
<tbody><tr>
<td>INSERT</td>
<td>없음</td>
<td>새 행</td>
</tr>
<tr>
<td>UPDATE</td>
<td>변경 전 행</td>
<td>변경 후 행</td>
</tr>
<tr>
<td>DELETE</td>
<td>삭제 전 행</td>
<td>없음</td>
</tr>
</tbody></table>
<p>예를 들어 감사 로그에서는 다음처럼 사용할 수 있다.</p>
<pre><code class="language-sql">INSERT INTO audit_log(
    operation,
    old_data,
    new_data
)
VALUES (
    TG_OP,
    CASE WHEN TG_OP IN ('UPDATE', 'DELETE')
         THEN to_jsonb(OLD) END,
    CASE WHEN TG_OP IN ('INSERT', 'UPDATE')
         THEN to_jsonb(NEW) END
);</code></pre>
<hr />
<h2 id="대표-사용-사례">대표 사용 사례</h2>
<h3 id="주문-감사-로그">주문 감사 로그</h3>
<pre><code class="language-text">orders INSERT·UPDATE·DELETE
→ OLD·NEW를 JSONB로 변환
→ audit_log에 저장</code></pre>
<h3 id="주문-총액-자동-동기화">주문 총액 자동 동기화</h3>
<pre><code class="language-text">order_items INSERT·UPDATE·DELETE
→ 해당 주문의 line_amount 합계 계산
→ orders.total_amount 갱신</code></pre>
<p><code>UPDATE</code>로 주문 상세의 <code>order_id</code>가 바뀌었다면 이전 주문과 새 주문의 총액을 모두 다시 계산해야 한다.</p>
<hr />
<h1 id="성능과-보안">성능과 보안</h1>
<h2 id="성능">성능</h2>
<p>루틴의 성능은 PL/pgSQL 문법보다 내부 SQL에서 대부분 결정된다.</p>
<pre><code class="language-text">반복문보다 집합 SQL 우선
WHERE 컬럼을 불필요한 함수로 감싸지 않기
동적 SQL 최소화
핵심 SQL을 밖으로 꺼내 EXPLAIN ANALYZE 확인
변동성 속성 정확히 지정</code></pre>
<hr />
<h2 id="보안">보안</h2>
<p>기본값은 호출자의 권한으로 실행하는 <code>SECURITY INVOKER</code>다.</p>
<pre><code class="language-text">SECURITY INVOKER
→ 호출자 권한

SECURITY DEFINER
→ 함수 소유자 권한</code></pre>
<p><code>SECURITY DEFINER</code>를 사용할 때는 <code>search_path</code>도 고정해야 한다.</p>
<pre><code class="language-sql">SET search_path = pg_catalog, proc_lab, pg_temp;</code></pre>
<blockquote>
<p>이걸 통해 코드 수행 여부를 따질 스키마를 한정지어 위험으로부터 보호하고자 한다.</p>
</blockquote>
<p>그리고 불필요한 PUBLIC 실행 권한을 제거하고 필요한 사용자에게만 <code>GRANT EXECUTE</code>를 제공한다.</p>
<hr />
<h1 id="객체-선택-기준">객체 선택 기준</h1>
<table>
<thead>
<tr>
<th>질문</th>
<th>선택</th>
</tr>
</thead>
<tbody><tr>
<td>SELECT 안에서 값이 필요한가?</td>
<td>Function</td>
</tr>
<tr>
<td>여러 SQL을 업무 흐름으로 묶는가?</td>
<td>Procedure</td>
</tr>
<tr>
<td>테이블 변경에 자동 반응해야 하는가?</td>
<td>Trigger</td>
</tr>
<tr>
<td>단순 조회를 재사용하는가?</td>
<td>View 검토</td>
</tr>
<tr>
<td>한 문장 SQL로 충분한가?</td>
<td>별도 루틴 불필요</td>
</tr>
<tr>
<td>단순 무결성 규칙인가?</td>
<td>CHECK·UNIQUE·NOT NULL 우선</td>
</tr>
</tbody></table>
<hr />
<h1 id="정리">정리</h1>
<pre><code class="language-text">PL/pgSQL
→ 변수·조건·반복·예외를 작성하는 언어

Function
→ 값을 계산하거나 조회해 반환
→ SELECT와 SQL 식 안에서 사용 가능

Procedure
→ 여러 SQL을 하나의 업무 절차로 묶음
→ CALL로 실행하며 트랜잭션과 잠금이 중요

Trigger
→ 테이블 이벤트에 자동 반응
→ OLD·NEW·TG_OP를 사용해 감사와 동기화 처리</code></pre>
<blockquote>
<p><strong>함수는 값을 얻기 위한 도구, 프로시저는 업무 흐름을 실행하는 도구, 트리거는 데이터 변경에 자동으로 반응하는 도구다.</strong></p>
</blockquote>
<p>이 구성은 자료의 <strong>PL/pgSQL 문법 → Function → Procedure → Trigger → 성능·보안·테스트</strong> 흐름을 유지하면서 핵심 내용을 압축한 것이다. </p>