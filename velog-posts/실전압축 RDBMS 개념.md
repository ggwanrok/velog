<h1 id="rdbms-핵심-개념-정리">RDBMS 핵심 개념 정리</h1>
<h2 id="테이블을-나누고-키로-연결하고-제약조건으로-지키는-이유">테이블을 나누고, 키로 연결하고, 제약조건으로 지키는 이유</h2>
<p>관계형 데이터베이스를 처음 접하면 흔히 다음과 같은 SQL 문법부터 배우게 된다.</p>
<pre><code class="language-sql">CREATE TABLE
INSERT INTO
SELECT
JOIN</code></pre>
<p>하지만 SQL 문법만 익혀서는 관계형 데이터베이스를 제대로 이해하기 어렵다.</p>
<p>RDBMS에서 더 중요한 질문은 다음과 같다.</p>
<ul>
<li>하나의 정보를 왜 여러 테이블로 나누는가?</li>
<li>나누어진 테이블은 어떻게 다시 연결하는가?</li>
<li>기본키와 외래키는 왜 필요한가?</li>
<li>1:N, N:M 관계는 무엇을 의미하는가?</li>
<li>데이터베이스는 잘못된 데이터를 어떻게 막는가?</li>
<li>NULL은 단순히 값이 비어 있다는 뜻인가?</li>
</ul>
<p>이번 글에서는 학과, 학생, 과목, 수강신청으로 이루어진 학사관리 구조를 예시로 사용하되, 실습 과정이 아니라 <strong>관계형 데이터베이스의 핵심 원리</strong>를 중심으로 정리한다.</p>
<hr />
<h1 id="dbms와-rdbms">DBMS와 RDBMS</h1>
<h2 id="dbms">DBMS</h2>
<p>DBMS는 <strong>Database Management System</strong>, 즉 데이터베이스 관리 시스템이다.</p>
<p>데이터를 저장하는 것뿐 아니라 다음 작업을 제공한다.</p>
<ul>
<li>데이터 생성</li>
<li>조회</li>
<li>수정</li>
<li>삭제</li>
<li>동시 접근 제어</li>
<li>권한 관리</li>
<li>장애 복구</li>
<li>데이터 무결성 관리</li>
</ul>
<p>PostgreSQL, MySQL, Oracle Database 등이 대표적인 DBMS다.</p>
<hr />
<h2 id="rdbms">RDBMS</h2>
<p>RDBMS는 <strong>Relational Database Management System</strong>, 즉 관계형 데이터베이스 관리 시스템이다.</p>
<p>데이터를 행과 열로 이루어진 테이블에 저장하고, 테이블 사이의 관계를 키로 표현한다.</p>
<p>예를 들어 학사관리시스템을 다음처럼 나눌 수 있다.</p>
<pre><code class="language-text">majors       전공 정보
students     학생 정보
courses      과목 정보
enrollments  수강신청 정보</code></pre>
<p>각 테이블은 독립적으로 존재하는 것이 아니라 다음처럼 연결된다.</p>
<pre><code class="language-text">majors.id      → students.major_id

students.id    → enrollments.student_id
courses.id     → enrollments.course_id</code></pre>
<p>즉, 관계형 데이터베이스의 핵심은 단순히 데이터를 표로 저장하는 것이 아니라,</p>
<blockquote>
<p><strong>데이터를 역할별로 분리하고, 키를 통해 의미 있는 관계를 형성하는 것</strong></p>
</blockquote>
<p>에 있다.</p>
<hr />
<h1 id="관계형-모델의-기본-용어">관계형 모델의 기본 용어</h1>
<p>관계형 데이터베이스에서는 테이블을 설명할 때 다음 개념을 사용한다.</p>
<h2 id="릴레이션">릴레이션</h2>
<p>관계형 모델에서 데이터를 표현하는 구조다.</p>
<p>실무에서는 보통 테이블과 비슷한 개념으로 이해한다.</p>
<pre><code class="language-text">students</code></pre>
<p>라는 릴레이션이 있다면, 학생에 대한 속성과 데이터를 가진다.</p>
<hr />
<h2 id="튜플">튜플</h2>
<p>테이블의 한 행이다.</p>
<pre><code class="language-text">1 | 2024001 | 김철수 | kim1@test.com | 1 | 1</code></pre>
<p>이 한 행은 한 명의 학생을 표현한다.</p>
<p>SQL에서는 보통 <code>row</code>라고 부른다.</p>
<hr />
<h2 id="속성">속성</h2>
<p>테이블의 열이다.</p>
<pre><code class="language-text">id
student_no
name
email
major_id
grade</code></pre>
<p>SQL에서는 보통 <code>column</code>이라고 부른다.</p>
<hr />
<h2 id="도메인">도메인</h2>
<p>각 속성에 들어갈 수 있는 값의 범위다.</p>
<p>예를 들어 학년의 도메인은 다음과 같이 정의할 수 있다.</p>
<pre><code class="language-text">1, 2, 3, 4</code></pre>
<p>SQL에서는 데이터 타입과 <code>CHECK</code> 제약조건을 통해 이를 표현할 수 있다.</p>
<pre><code class="language-sql">grade smallint CHECK (grade BETWEEN 1 AND 4)</code></pre>
<p>즉, 도메인은 단순히 <code>smallint</code>라는 타입만 의미하는 것이 아니라, 업무적으로 허용되는 값의 범위까지 포함한다.</p>
<hr />
<h1 id="데이터베이스-스키마-테이블">데이터베이스, 스키마, 테이블</h1>
<p>PostgreSQL에서는 객체가 계층적으로 구성된다.</p>
<pre><code class="language-text">PostgreSQL Server
└── Database
    └── Schema
        └── Table</code></pre>
<p>예를 들어 다음과 같은 구조가 가능하다.</p>
<pre><code class="language-text">PostgreSQL
└── skala_db
    ├── public
    └── app
        ├── majors
        ├── students
        ├── courses
        └── enrollments</code></pre>
<h2 id="데이터베이스">데이터베이스</h2>
<p>서로 독립된 데이터 저장 공간이다.</p>
<p>일반적으로 하나의 서비스나 시스템 단위로 구분할 수 있다.</p>
<hr />
<h2 id="스키마">스키마</h2>
<p>하나의 데이터베이스 안에서 테이블, 뷰, 함수 등의 객체를 논리적으로 묶는 이름 공간이다.</p>
<p>예를 들어 다음 두 테이블은 이름은 같지만 서로 다른 객체가 될 수 있다.</p>
<pre><code class="language-text">public.students
app.students</code></pre>
<p>스키마를 사용하면 다음과 같은 분리가 가능하다.</p>
<pre><code class="language-text">app        서비스 운영 테이블
analytics  분석용 테이블
admin      관리용 테이블</code></pre>
<p><code>search_path</code>는 스키마명을 생략했을 때 PostgreSQL이 객체를 찾는 순서를 의미한다.</p>
<pre><code class="language-sql">SET search_path TO app, public;</code></pre>
<p>이후 다음 쿼리는:</p>
<pre><code class="language-sql">SELECT *
FROM students;</code></pre>
<p>사실상 다음 객체를 우선 탐색한다.</p>
<pre><code class="language-text">app.students</code></pre>
<hr />
<h1 id="왜-테이블을-나누는가">왜 테이블을 나누는가?</h1>
<p>학생, 학과, 과목, 성적 정보를 하나의 테이블에 저장한다고 생각해보자.</p>
<pre><code class="language-text">학번 | 학생명 | 이메일 | 학과명 | 과목명 | 학점 | 점수</code></pre>
<p>김철수가 세 과목을 수강하면 다음처럼 학생 정보가 반복된다.</p>
<pre><code class="language-text">2024001 | 김철수 | kim1@test.com | 컴퓨터공학과 | Java       | 3 | 95.5
2024001 | 김철수 | kim1@test.com | 컴퓨터공학과 | 데이터베이스 | 3 | 91.0
2024001 | 김철수 | kim1@test.com | 컴퓨터공학과 | 머신러닝     | 3 | 92.5</code></pre>
<p>이 구조에는 여러 문제가 생긴다.</p>
<h2 id="수정-이상">수정 이상</h2>
<p>김철수의 이메일이 변경되면 여러 행을 모두 수정해야 한다.</p>
<p>일부 행만 수정되면 같은 학생의 이메일이 서로 다르게 저장된다.</p>
<hr />
<h2 id="삽입-이상">삽입 이상</h2>
<p>아직 수강생이 없는 새로운 과목을 등록하려면 학생 정보까지 함께 넣어야 할 수 있다.</p>
<hr />
<h2 id="삭제-이상">삭제 이상</h2>
<p>학생의 마지막 수강신청 행을 삭제했더니 학생 정보 자체도 함께 사라질 수 있다.</p>
<hr />
<p>이러한 문제를 줄이기 위해 데이터를 역할별로 나눈다.</p>
<pre><code class="language-text">students     학생 자체의 정보
majors       전공 자체의 정보
courses      과목 자체의 정보
enrollments  학생이 과목을 수강한 관계</code></pre>
<p>이 과정은 정규화와 연결된다.</p>
<hr />
<h1 id="정규화란">정규화란?</h1>
<p>정규화는 데이터를 무조건 작은 테이블로 쪼개는 작업이 아니다.</p>
<p>정확히는 다음을 목표로 한다.</p>
<ul>
<li>데이터 중복 감소</li>
<li>수정 이상 방지</li>
<li>삽입 이상 방지</li>
<li>삭제 이상 방지</li>
<li>각 테이블의 책임 명확화</li>
</ul>
<p>예를 들어 학생 테이블에는 학생 자체의 정보만 둔다.</p>
<pre><code class="language-text">학생의 이름
학생의 학번
학생의 이메일
학생의 학년
학생의 소속 전공</code></pre>
<p>과목 테이블에는 과목 자체의 정보만 둔다.</p>
<pre><code class="language-text">과목 코드
과목명
이수 학점</code></pre>
<p>성적은 학생 자체의 속성도 아니고 과목 자체의 속성도 아니다.</p>
<pre><code class="language-text">김철수라는 학생이
데이터베이스라는 과목을 수강한 결과
91점을 받았다.</code></pre>
<p>성적은 <strong>학생과 과목 사이의 관계에서 발생한 속성</strong>이다.</p>
<p>따라서 <code>enrollments</code>에 저장한다.</p>
<pre><code class="language-text">student_id
course_id
score
enrolled_at</code></pre>
<hr />
<h1 id="엔터티와-관계">엔터티와 관계</h1>
<h2 id="엔터티">엔터티</h2>
<p>업무에서 독립적으로 관리할 필요가 있는 대상이다.</p>
<p>학사관리시스템에서는 다음이 엔터티가 될 수 있다.</p>
<pre><code class="language-text">전공
학생
과목</code></pre>
<p>엔터티는 일반적으로 테이블로 변환된다.</p>
<pre><code class="language-text">전공 → majors
학생 → students
과목 → courses</code></pre>
<hr />
<h2 id="관계">관계</h2>
<p>엔터티끼리 어떤 방식으로 연결되는지를 의미한다.</p>
<pre><code class="language-text">학생은 전공에 소속된다.
학생은 과목을 수강한다.</code></pre>
<p>관계는 보통 다음과 같이 분류한다.</p>
<ul>
<li>1:1</li>
<li>1:N</li>
<li>N:M</li>
</ul>
<hr />
<h1 id="11-1n-nm-관계">1:1, 1:N, N:M 관계</h1>
<h2 id="11-관계">1:1 관계</h2>
<p>한쪽의 하나가 다른 쪽의 하나와만 연결되는 관계다.</p>
<p>예를 들면:</p>
<pre><code class="language-text">사용자 1 : 1 사용자 상세정보</code></pre>
<p>반드시 테이블을 분리해야 하는 것은 아니며, 보안이나 선택적 속성 분리 등의 이유가 있을 때 사용한다.</p>
<hr />
<h2 id="1n-관계">1:N 관계</h2>
<p>한쪽의 하나가 다른 쪽의 여러 개와 연결되는 관계다.</p>
<p>학과와 학생 관계가 대표적이다.</p>
<pre><code class="language-text">학과 1 : N 학생</code></pre>
<p>한 학과에는 여러 학생이 소속될 수 있다.</p>
<pre><code class="language-text">컴퓨터공학과
├── 김철수
├── 이영희
└── 박민수</code></pre>
<p>관계형 데이터베이스에서는 N 쪽에 외래키를 둔다.</p>
<pre><code class="language-text">majors.id → students.major_id</code></pre>
<p>왜 학생 테이블에 학과 ID를 둘까?</p>
<p>학생 한 명은 한 개의 <code>major_id</code>를 가지지만, 하나의 학과 ID는 여러 학생 행에서 반복될 수 있기 때문이다.</p>
<hr />
<h2 id="nm-관계">N:M 관계</h2>
<p>양쪽 모두 여러 개와 연결되는 관계다.</p>
<p>학생과 과목의 관계가 대표적이다.</p>
<pre><code class="language-text">학생 N : M 과목</code></pre>
<p>한 학생은 여러 과목을 수강할 수 있다.</p>
<pre><code class="language-text">김철수
├── Java
├── 데이터베이스
└── 머신러닝</code></pre>
<p>하나의 과목도 여러 학생이 수강할 수 있다.</p>
<pre><code class="language-text">데이터베이스
├── 김철수
├── 이영희
└── 박민수</code></pre>
<p>관계형 데이터베이스에서는 N:M 관계를 직접 표현하지 않고, 교차 테이블을 통해 두 개의 1:N 관계로 해소한다.</p>
<pre><code class="language-text">students 1 : N enrollments
courses  1 : N enrollments</code></pre>
<p>전체적으로는:</p>
<pre><code class="language-text">students
    1
    │
    N
enrollments
    N
    │
    1
courses</code></pre>
<p>제공된 학사관리 예제 역시 학생과 과목 사이의 N:M 관계를 <code>enrollments</code>가 연결하는 구조로 설계되어 있다. </p>
<hr />
<h1 id="교차-테이블">교차 테이블</h1>
<p>교차 테이블은 N:M 관계를 표현하기 위한 중간 테이블이다.</p>
<p>학사관리 예제에서는 <code>enrollments</code>가 교차 테이블이다.</p>
<pre><code class="language-text">enrollments
├── student_id
├── course_id
├── score
└── enrolled_at</code></pre>
<p>교차 테이블에는 외래키만 들어가는 것이 아니다.</p>
<p><strong>관계 자체에서 발생하는 속성</strong>도 들어간다.</p>
<pre><code class="language-text">score        해당 학생이 해당 과목에서 받은 점수
enrolled_at  해당 학생이 해당 과목을 신청한 날짜</code></pre>
<p>성적은 학생 자체의 속성이 아니다.</p>
<p>한 학생은 과목마다 다른 성적을 받기 때문이다.</p>
<p>과목 자체의 속성도 아니다.</p>
<p>하나의 과목에서도 학생마다 다른 성적을 받기 때문이다.</p>
<p>따라서 성적은 학생과 과목의 관계인 <code>enrollments</code>에 속한다.</p>
<hr />
<h1 id="키의-종류">키의 종류</h1>
<p>키는 행을 식별하거나 테이블 사이의 관계를 연결하는 속성이다.</p>
<h2 id="슈퍼키">슈퍼키</h2>
<p>행을 유일하게 식별할 수 있는 모든 속성의 집합이다.</p>
<p>예를 들어 학생 테이블에서 다음 조합은 학생을 구분할 수 있다.</p>
<pre><code class="language-text">{id}
{student_no}
{email}
{id, name}
{student_no, email}</code></pre>
<p>불필요한 컬럼까지 포함한 조합도 슈퍼키가 될 수 있다.</p>
<hr />
<h2 id="후보키">후보키</h2>
<p>슈퍼키 중에서 불필요한 속성을 제거한 최소한의 키다.</p>
<pre><code class="language-text">id
student_no
email</code></pre>
<p>각각만으로 학생을 유일하게 식별할 수 있다면 후보키가 된다.</p>
<hr />
<h2 id="기본키">기본키</h2>
<p>후보키 중에서 테이블의 대표 식별자로 선택한 키다.</p>
<pre><code class="language-sql">PRIMARY KEY (id)</code></pre>
<p>기본키는 다음 특징을 가진다.</p>
<ul>
<li>중복 불가</li>
<li>NULL 불가</li>
<li>행을 대표하여 식별</li>
<li>다른 테이블에서 외래키로 참조 가능</li>
</ul>
<hr />
<h2 id="대체키">대체키</h2>
<p>후보키 중 기본키로 선택되지 않은 키다.</p>
<p>학생 테이블에서 <code>id</code>를 기본키로 선택했다면 다음은 대체키가 될 수 있다.</p>
<pre><code class="language-text">student_no
email</code></pre>
<p>보통 <code>UNIQUE</code> 제약조건으로 표현한다.</p>
<hr />
<h2 id="자연키와-업무키">자연키와 업무키</h2>
<p>실제 업무에서 의미를 가진 값이다.</p>
<pre><code class="language-text">학번
이메일
과목 코드
전공 코드</code></pre>
<p>예:</p>
<pre><code class="language-text">student_no = 2024001
course_code = DB201</code></pre>
<p>사람이 이해할 수 있다는 장점이 있지만, 업무 정책에 따라 값이 바뀔 수 있다.</p>
<hr />
<h2 id="대리키">대리키</h2>
<p>업무적 의미 없이 관계 연결을 위해 만든 인공적인 식별자다.</p>
<pre><code class="language-text">id = 1
id = 2
id = 3</code></pre>
<p>보통 자동 증가 값을 사용한다.</p>
<pre><code class="language-sql">id bigint GENERATED BY DEFAULT AS IDENTITY</code></pre>
<p>학사관리 구조에서는 다음처럼 구분할 수 있다.</p>
<pre><code class="language-text">students.id          대리키, 내부 연결용
students.student_no  업무키, 실제 학번

courses.id           대리키
courses.course_code  업무키</code></pre>
<hr />
<h1 id="복합-기본키">복합 기본키</h1>
<p>하나가 아니라 여러 컬럼을 조합하여 기본키를 구성할 수도 있다.</p>
<pre><code class="language-sql">PRIMARY KEY (student_id, course_id)</code></pre>
<p><code>enrollments</code>에서는 <code>student_id</code>만으로는 행을 식별할 수 없다.</p>
<p>한 학생이 여러 과목을 수강하기 때문이다.</p>
<pre><code class="language-text">student_id = 1, course_id = 1
student_id = 1, course_id = 3
student_id = 1, course_id = 5</code></pre>
<p><code>course_id</code>만으로도 식별할 수 없다.</p>
<p>한 과목을 여러 학생이 수강하기 때문이다.</p>
<pre><code class="language-text">student_id = 1, course_id = 3
student_id = 2, course_id = 3
student_id = 4, course_id = 3</code></pre>
<p>하지만 두 컬럼을 묶으면 한 수강신청을 식별할 수 있다.</p>
<pre><code class="language-text">(student_id = 1, course_id = 3)</code></pre>
<p>복합 기본키는 동일 학생이 동일 과목을 중복 신청하는 것도 막는다. 제공된 자료에서도 <code>(student_id, course_id)</code>를 복합 기본키로 사용하여 같은 학생의 같은 과목 중복 신청을 제한한다. </p>
<p>다만 다음과 같은 구조는 표현하기 어렵다.</p>
<pre><code class="language-text">같은 학생이 같은 과목을 다른 학기에 재수강</code></pre>
<p>이 경우에는 다음과 같은 확장이 필요하다.</p>
<pre><code class="language-text">PRIMARY KEY (student_id, course_id, semester)</code></pre>
<p>또는 수강신청용 별도 ID를 둔다.</p>
<pre><code class="language-text">enrollment_id</code></pre>
<p>즉, 키 구조는 업무 규칙에 따라 달라진다.</p>
<hr />
<h1 id="외래키와-참조-무결성">외래키와 참조 무결성</h1>
<p>외래키는 다른 테이블의 기본키 또는 UNIQUE 키를 참조하는 컬럼이다.</p>
<pre><code class="language-sql">FOREIGN KEY (major_id)
REFERENCES majors(id)</code></pre>
<p>이 제약조건은 다음 규칙을 보장한다.</p>
<pre><code class="language-text">students.major_id에 저장되는 값은
majors.id에 실제로 존재해야 한다.</code></pre>
<p>예를 들어 <code>majors</code>에 다음 데이터만 있다고 하자.</p>
<pre><code class="language-text">1 컴퓨터공학과
2 인공지능학과</code></pre>
<p>그렇다면 다음 값은 가능하다.</p>
<pre><code class="language-text">major_id = 1
major_id = 2
major_id = NULL</code></pre>
<p>하지만 다음 값은 입력할 수 없다.</p>
<pre><code class="language-text">major_id = 999</code></pre>
<p>999번 학과가 존재하지 않기 때문이다.</p>
<p>이를 <strong>참조 무결성</strong>이라고 한다.</p>
<p>외래키는 단순히 JOIN을 편하게 하기 위한 컬럼이 아니다.</p>
<blockquote>
<p>존재하지 않는 대상을 참조하지 못하도록 데이터베이스가 관계의 유효성을 보장하는 규칙이다.</p>
</blockquote>
<hr />
<h1 id="무결성의-종류">무결성의 종류</h1>
<p>관계형 데이터베이스에서 무결성은 데이터가 정확하고 일관된 상태를 유지하는 것을 의미한다.</p>
<h2 id="개체-무결성">개체 무결성</h2>
<p>각 행은 유일하게 식별되어야 한다.</p>
<pre><code class="language-sql">PRIMARY KEY</code></pre>
<p>기본키는 NULL이 될 수 없고 중복될 수 없다.</p>
<hr />
<h2 id="참조-무결성">참조 무결성</h2>
<p>외래키는 실제 존재하는 부모 행을 참조해야 한다.</p>
<pre><code class="language-sql">FOREIGN KEY</code></pre>
<p>존재하지 않는 학과, 학생, 과목을 참조하는 데이터를 방지한다.</p>
<hr />
<h2 id="도메인-무결성">도메인 무결성</h2>
<p>각 컬럼에는 정의된 형식과 범위의 값만 들어가야 한다.</p>
<pre><code class="language-sql">CHECK (grade BETWEEN 1 AND 4)
CHECK (score BETWEEN 0 AND 100)</code></pre>
<hr />
<h2 id="사용자-정의-무결성">사용자 정의 무결성</h2>
<p>특정 업무에서만 필요한 규칙이다.</p>
<p>예를 들어:</p>
<pre><code class="language-text">졸업생은 수강신청을 할 수 없다.
전공 필수 과목은 반드시 3학점 이상이어야 한다.
한 학기 최대 신청 학점은 21학점이다.</code></pre>
<p>이러한 규칙은 CHECK, 트리거, 프로시저, 애플리케이션 로직 등으로 표현할 수 있다.</p>
<hr />
<h1 id="제약조건">제약조건</h1>
<p>제약조건은 잘못된 데이터가 저장되는 것을 입력 시점에 막는다.</p>
<p>실습자료에서도 <code>PRIMARY KEY</code>, <code>UNIQUE</code>, <code>FOREIGN KEY</code>, <code>CHECK</code>를 함께 사용하여 데이터 품질을 유지하는 구조를 제시한다. </p>
<h2 id="primary-key">PRIMARY KEY</h2>
<p>행을 유일하게 식별한다.</p>
<pre><code class="language-sql">id bigint PRIMARY KEY</code></pre>
<hr />
<h2 id="unique">UNIQUE</h2>
<p>중복될 수 없는 업무 값을 제한한다.</p>
<pre><code class="language-sql">student_no varchar(20) UNIQUE
email varchar(200) UNIQUE
course_code varchar(20) UNIQUE</code></pre>
<p>기본키와 마찬가지로 중복을 제한하지만, 하나의 테이블에 여러 개의 UNIQUE 제약조건을 둘 수 있다.</p>
<hr />
<h2 id="not-null">NOT NULL</h2>
<p>값이 반드시 존재해야 함을 의미한다.</p>
<pre><code class="language-sql">name varchar(100) NOT NULL</code></pre>
<p>NULL을 허용하지 않는다.</p>
<hr />
<h2 id="check">CHECK</h2>
<p>값이 특정 조건을 만족해야 한다.</p>
<pre><code class="language-sql">CHECK (grade BETWEEN 1 AND 4)</code></pre>
<pre><code class="language-sql">CHECK (credit BETWEEN 1 AND 6)</code></pre>
<pre><code class="language-sql">CHECK (score BETWEEN 0 AND 100)</code></pre>
<hr />
<h2 id="default">DEFAULT</h2>
<p>INSERT 시 값이 생략되었을 때 기본값을 제공한다.</p>
<pre><code class="language-sql">created_at timestamp DEFAULT now()</code></pre>
<p><code>DEFAULT</code>는 필수값 제약이 아니다.</p>
<p>기본값이 있더라도 명시적으로 NULL을 넣을 수 있는지는 <code>NOT NULL</code> 여부에 따라 달라진다.</p>
<hr />
<h1 id="null의-의미">NULL의 의미</h1>
<p>NULL은 다음 중 하나의 의미를 가진다.</p>
<pre><code class="language-text">아직 모름
입력되지 않음
해당 없음
결정되지 않음</code></pre>
<p>NULL은 0도 아니고 빈 문자열도 아니다.</p>
<pre><code class="language-text">0     실제 숫자 0
''    길이가 0인 문자열
NULL  값 자체가 존재하지 않음</code></pre>
<p>예를 들어:</p>
<pre><code class="language-text">score = 0</code></pre>
<p>은 실제 시험 점수가 0점이라는 의미다.</p>
<p>반면:</p>
<pre><code class="language-text">score = NULL</code></pre>
<p>은 아직 성적이 입력되지 않았거나 미응시 상태일 수 있다.</p>
<p>제공된 예제도 <code>score</code>의 NULL과 실제 0점은 서로 다른 의미임을 구분한다. </p>
<hr />
<h1 id="null과-3값-논리">NULL과 3값 논리</h1>
<p>일반적인 조건식은 참과 거짓 두 가지로 생각하기 쉽다.</p>
<p>하지만 SQL은 NULL 때문에 다음 세 가지 논리를 사용한다.</p>
<pre><code class="language-text">TRUE
FALSE
UNKNOWN</code></pre>
<p>예를 들어:</p>
<pre><code class="language-sql">score = 90</code></pre>
<p><code>score</code>가 NULL이면 결과는 FALSE가 아니라 UNKNOWN이다.</p>
<p>따라서 NULL 여부를 확인할 때는 다음처럼 작성해야 한다.</p>
<pre><code class="language-sql">score IS NULL</code></pre>
<p>잘못된 방식:</p>
<pre><code class="language-sql">score = NULL</code></pre>
<p>NULL은 일반 값처럼 <code>=</code>로 비교할 수 없다.</p>
<hr />
<h1 id="삭제-정책">삭제 정책</h1>
<p>부모 데이터가 삭제될 때 외래키를 가진 자식 데이터를 어떻게 처리할지 결정할 수 있다.</p>
<h2 id="restrict-또는-no-action">RESTRICT 또는 NO ACTION</h2>
<p>참조 중인 자식 데이터가 있으면 부모 삭제를 막는다.</p>
<pre><code class="language-text">학생이 소속된 학과는 삭제 불가</code></pre>
<hr />
<h2 id="cascade">CASCADE</h2>
<p>부모가 삭제되면 관련 자식 데이터도 함께 삭제한다.</p>
<pre><code class="language-text">학생 삭제
→ 해당 학생의 수강신청도 삭제</code></pre>
<hr />
<h2 id="set-null">SET NULL</h2>
<p>부모가 삭제되면 외래키 값을 NULL로 변경한다.</p>
<pre><code class="language-text">학과 삭제
→ 학생은 유지
→ 학생의 major_id만 NULL</code></pre>
<p>어떤 정책이 정답인 것은 아니다.</p>
<p>업무적으로 자식 데이터가 부모 없이 존재할 수 있는지를 기준으로 판단해야 한다.</p>
<pre><code class="language-text">학과가 없어져도 학생은 남아야 한다.
→ SET NULL 고려

학생이 없어지면 그 학생의 수강신청은 의미가 없다.
→ CASCADE 고려</code></pre>
<hr />
<h1 id="정규화와-join의-관계">정규화와 JOIN의 관계</h1>
<p>정규화를 통해 테이블을 분리하면 데이터 중복은 줄어든다.</p>
<p>하지만 조회할 때 필요한 정보가 여러 테이블에 흩어진다.</p>
<p>예를 들어 <code>students</code>에는 학과명이 없다.</p>
<pre><code class="language-text">major_id만 존재</code></pre>
<p>실제 학과명은 <code>majors</code>에 있다.</p>
<p>따라서 두 테이블을 연결해야 한다.</p>
<pre><code class="language-sql">SELECT
    students.name,
    majors.name
FROM students
JOIN majors
    ON students.major_id = majors.id;</code></pre>
<p>즉, 관계형 데이터베이스는 다음 전략을 사용한다.</p>
<pre><code class="language-text">저장할 때
→ 중복을 줄이기 위해 분리

조회할 때
→ 필요한 정보를 JOIN으로 조합</code></pre>
<p>JOIN은 단순한 SQL 기능이 아니라, <strong>정규화된 관계형 구조를 다시 의미 있는 정보로 조립하는 연산</strong>이다.</p>
<hr />
<h1 id="join">JOIN</h1>
<h1 id="join-결과-범위에-따른-종류">JOIN 결과 범위에 따른 종류</h1>
<p>JOIN은 <strong>둘 이상의 테이블을 공통된 컬럼이나 조건을 기준으로 연결해 하나의 조회 결과로 만드는 연산</strong>이다.</p>
<p>JOIN의 종류는 어떤 행을 결과에 남길 것인지에 따라 구분할 수 있다.</p>
<hr />
<h2 id="inner-join">INNER JOIN</h2>
<p>두 테이블에서 <strong>JOIN 조건을 만족하는 행만 조회</strong>한다.</p>
<pre><code class="language-sql">SELECT *
FROM students
INNER JOIN majors
    ON students.major_id = majors.id;</code></pre>
<p>학생에게 학과가 배정되어 있고, 해당 학과 정보도 실제로 존재하는 경우에만 결과에 포함된다.</p>
<pre><code class="language-text">students          majors
김철수, major_id=1   id=1, 컴퓨터공학과
이영희, major_id=2   id=2, 인공지능학과
서지훈, major_id=NULL</code></pre>
<p>결과:</p>
<pre><code class="language-text">김철수 | 컴퓨터공학과
이영희 | 인공지능학과</code></pre>
<p><code>major_id</code>가 NULL인 서지훈은 연결할 학과가 없으므로 제외된다.</p>
<p><code>INNER</code>는 생략할 수 있다.</p>
<pre><code class="language-sql">JOIN majors</code></pre>
<p>는 다음과 같은 의미다.</p>
<pre><code class="language-sql">INNER JOIN majors</code></pre>
<h3 id="특징">특징</h3>
<ul>
<li>양쪽 테이블에 일치하는 데이터가 있어야 한다.</li>
<li>일치하지 않는 행은 결과에서 제외된다.</li>
<li>실제 업무에서 가장 자주 사용하는 JOIN이다.</li>
</ul>
<hr />
<h2 id="left-outer-join">LEFT OUTER JOIN</h2>
<p>왼쪽 테이블의 행은 <strong>모두 유지</strong>하고, 오른쪽 테이블에서는 조건이 일치하는 데이터만 연결한다.</p>
<pre><code class="language-sql">SELECT *
FROM students
LEFT JOIN majors
    ON students.major_id = majors.id;</code></pre>
<p>결과:</p>
<pre><code class="language-text">김철수 | 컴퓨터공학과
이영희 | 인공지능학과
서지훈 | NULL</code></pre>
<p>서지훈은 연결되는 학과가 없지만, 왼쪽 테이블인 <code>students</code>의 행은 유지된다. 오른쪽 테이블인 <code>majors</code>의 컬럼만 NULL로 표시된다.</p>
<h3 id="특징-1">특징</h3>
<ul>
<li>왼쪽 테이블의 모든 행을 조회한다.</li>
<li>오른쪽에 일치하는 행이 없으면 오른쪽 컬럼은 NULL이 된다.</li>
<li>미배정, 미등록, 주문하지 않은 고객처럼 관계가 없는 데이터까지 조회할 때 사용한다.</li>
</ul>
<p><code>OUTER</code>는 생략할 수 있다.</p>
<pre><code class="language-sql">LEFT JOIN</code></pre>
<p>과 다음은 같은 의미다.</p>
<pre><code class="language-sql">LEFT OUTER JOIN</code></pre>
<hr />
<h2 id="right-outer-join">RIGHT OUTER JOIN</h2>
<p>오른쪽 테이블의 행은 <strong>모두 유지</strong>하고, 왼쪽 테이블에서는 조건이 일치하는 데이터만 연결한다.</p>
<pre><code class="language-sql">SELECT *
FROM students
RIGHT JOIN majors
    ON students.major_id = majors.id;</code></pre>
<p>예를 들어 경영학과에 소속된 학생이 한 명도 없더라도 경영학과 자체는 결과에 포함된다.</p>
<pre><code class="language-text">김철수 | 컴퓨터공학과
이영희 | 인공지능학과
NULL   | 경영학과</code></pre>
<h3 id="특징-2">특징</h3>
<ul>
<li>오른쪽 테이블의 모든 행을 유지한다.</li>
<li>왼쪽에 일치하는 데이터가 없으면 왼쪽 컬럼이 NULL이 된다.</li>
<li>LEFT JOIN과 방향만 반대다.</li>
</ul>
<p>실무에서는 테이블 순서를 바꾸고 LEFT JOIN으로 표현하는 경우가 많다.</p>
<pre><code class="language-sql">FROM majors
LEFT JOIN students
    ON students.major_id = majors.id;</code></pre>
<p>이 방식이 쿼리를 왼쪽에서 오른쪽으로 읽기 쉬운 경우가 많다.</p>
<hr />
<h2 id="full-outer-join">FULL OUTER JOIN</h2>
<p>왼쪽과 오른쪽 테이블의 행을 <strong>모두 유지</strong>한다.</p>
<pre><code class="language-sql">SELECT *
FROM students
FULL OUTER JOIN majors
    ON students.major_id = majors.id;</code></pre>
<p>JOIN 조건이 일치하는 행은 연결하고, 일치하지 않는 행도 각각 결과에 포함한다.</p>
<pre><code class="language-text">김철수 | 컴퓨터공학과
이영희 | 인공지능학과
서지훈 | NULL
NULL   | 경영학과</code></pre>
<p>여기서:</p>
<ul>
<li>서지훈은 학과가 없는 학생이다.</li>
<li>경영학과는 소속 학생이 없는 학과다.</li>
</ul>
<p>둘 다 결과에서 유지된다.</p>
<h3 id="특징-3">특징</h3>
<ul>
<li>양쪽 테이블의 모든 행을 조회한다.</li>
<li>한쪽에만 존재하는 데이터도 확인할 수 있다.</li>
<li>두 데이터 집합의 차이나 누락 데이터를 비교할 때 유용하다.</li>
</ul>
<hr />
<h3 id="outer-join이란">OUTER JOIN이란?</h3>
<p>다음 세 JOIN을 묶어 OUTER JOIN이라고 한다.</p>
<pre><code class="language-text">LEFT OUTER JOIN
RIGHT OUTER JOIN
FULL OUTER JOIN</code></pre>
<p>OUTER JOIN의 핵심은 <strong>JOIN 조건에 맞지 않는 행도 결과에 남긴다</strong>는 것이다.</p>
<p>반면 INNER JOIN은 일치하지 않는 행을 제거한다.</p>
<pre><code class="language-text">INNER JOIN
→ 양쪽에서 일치하는 행만 유지

OUTER JOIN
→ 일치하지 않는 행도 특정 방향에 따라 유지</code></pre>
<hr />
<h2 id="cross-join">CROSS JOIN</h2>
<p>두 테이블의 모든 행을 가능한 모든 조합으로 연결한다.</p>
<pre><code class="language-sql">SELECT *
FROM students
CROSS JOIN courses;</code></pre>
<p>학생이 10명이고 과목이 6개라면 결과는 다음과 같다.</p>
<pre><code class="language-text">10 × 6 = 60행</code></pre>
<p>결과 개념:</p>
<pre><code class="language-text">김철수 | Java 프로그래밍
김철수 | Python 프로그래밍
김철수 | 데이터베이스
...
이영희 | Java 프로그래밍
이영희 | Python 프로그래밍
...</code></pre>
<h3 id="특징-4">특징</h3>
<ul>
<li>JOIN 조건을 사용하지 않는다.</li>
<li>두 테이블의 데카르트 곱을 만든다.</li>
<li>행 수가 매우 빠르게 증가할 수 있다.</li>
</ul>
<p>주로 다음 상황에서 사용한다.</p>
<ul>
<li>모든 가능한 조합 생성</li>
<li>날짜와 상품의 전체 조합 생성</li>
<li>테스트 데이터 생성</li>
<li>기준값 조합 생성</li>
</ul>
<p>의도하지 않게 JOIN 조건을 빠뜨리면 CROSS JOIN과 비슷하게 행 수가 폭증할 수 있으므로 주의해야 한다.</p>
<hr />
<h2 id="join-조건을-작성하는-방법">JOIN 조건을 작성하는 방법</h2>
<h2 id="using과-비교">USING과 비교</h2>
<h3 id="on">ON</h3>
<pre><code class="language-sql">JOIN majors
    ON students.major_id = majors.major_id</code></pre>
<ul>
<li>연결 조건을 가장 명확하게 표현한다.</li>
<li>서로 다른 이름의 컬럼도 연결할 수 있다.</li>
<li>실무에서 가장 일반적이다.</li>
</ul>
<h3 id="using">USING</h3>
<pre><code class="language-sql">JOIN majors
    USING (major_id)</code></pre>
<ul>
<li>같은 이름의 특정 컬럼을 명시적으로 사용한다.</li>
<li>공통 컬럼은 결과에 한 번만 출력된다.</li>
</ul>
<h3 id="natural-join">NATURAL JOIN</h3>
<pre><code class="language-sql">NATURAL JOIN majors</code></pre>
<ul>
<li>같은 이름의 모든 컬럼을 자동으로 사용한다.</li>
<li>코드가 짧지만 조건이 암묵적이다.</li>
<li>테이블 변경에 따라 동작이 달라질 위험이 있다.</li>
</ul>
<hr />
<h2 id="특수한-join-활용">특수한 JOIN 활용</h2>
<h3 id="self-join">SELF JOIN</h3>
<p>하나의 테이블을 <strong>자기 자신과 JOIN</strong>하는 방식이다.</p>
<p>SELF JOIN은 별도의 SQL 키워드가 아니라, 같은 테이블에 서로 다른 별칭을 붙여 JOIN하는 패턴이다.</p>
<p>예를 들어 직원 테이블에 직원과 상사의 관계가 있다고 하자.</p>
<pre><code class="language-text">employees
- id
- name
- manager_id</code></pre>
<p><code>manager_id</code>는 같은 테이블의 <code>id</code>를 참조한다.</p>
<pre><code class="language-sql">SELECT
    employee.name AS 직원명,
    manager.name AS 상사명
FROM employees employee
LEFT JOIN employees manager
    ON employee.manager_id = manager.id;</code></pre>
<p>같은 <code>employees</code> 테이블을 두 역할로 사용한다.</p>
<pre><code class="language-text">employee
→ 직원 역할

manager
→ 상사 역할</code></pre>
<h3 id="특징-5">특징</h3>
<ul>
<li>계층 구조를 표현할 때 사용한다.</li>
<li>직원과 상사, 카테고리와 상위 카테고리, 댓글과 부모 댓글 등에 활용한다.</li>
<li>같은 테이블을 구분하기 위해 별칭이 중요하다.</li>
</ul>
<hr />
<h1 id="조건에-따른-join-분류">조건에 따른 JOIN 분류</h1>
<p>JOIN은 결과를 유지하는 방식뿐 아니라 <strong>어떤 조건으로 행을 연결하는지</strong>에 따라서도 나눌 수 있다.</p>
<hr />
<h2 id="equi-join">EQUI JOIN</h2>
<p>두 컬럼의 값이 같은지를 기준으로 연결한다.</p>
<pre><code class="language-sql">ON students.major_id = majors.id</code></pre>
<p><code>=</code> 연산자를 사용하는 일반적인 JOIN이다.</p>
<p>대부분의 기본키와 외래키 JOIN이 EQUI JOIN에 해당한다.</p>
<hr />
<h2 id="non-equi-join">NON-EQUI JOIN</h2>
<p>같음이 아니라 범위나 부등호 조건으로 연결한다.</p>
<pre><code class="language-sql">SELECT
    employees.name,
    salary_grade.grade
FROM employees
JOIN salary_grade
    ON employees.salary
       BETWEEN salary_grade.min_salary
           AND salary_grade.max_salary;</code></pre>
<p>직원의 급여가 어느 등급 구간에 포함되는지 조회하는 경우다.</p>
<h3 id="특징-6">특징</h3>
<ul>
<li><code>=</code>이 아닌 비교 조건을 사용한다.</li>
<li><code>&lt;</code>, <code>&gt;</code>, <code>BETWEEN</code> 등을 사용할 수 있다.</li>
<li>가격 구간, 점수 등급, 날짜 범위 등을 연결할 때 사용한다.</li>
</ul>
<hr />
<h1 id="coalesce와-case-when">COALESCE와 CASE WHEN</h1>
<p>엄밀히 말하면 <code>COALESCE</code>, <code>CASE WHEN</code>, 날짜 함수는 <strong>관계 모델 자체의 핵심 개념</strong>은 아니다.</p>
<p>이들은 SQL 조회 결과를 가공하기 위한 표현식과 함수다.</p>
<h2 id="case-when">CASE WHEN</h2>
<p>조건에 따라 출력값을 변환한다.</p>
<pre><code class="language-sql">CASE
    WHEN grade = 1 THEN 'Freshman'
    WHEN grade = 2 THEN 'Sophomore'
END</code></pre>
<hr />
<h2 id="coalesce">COALESCE</h2>
<p>여러 값 중 첫 번째 NULL이 아닌 값을 반환한다.</p>
<pre><code class="language-sql">COALESCE(majors.name, '학과 미배정')</code></pre>
<hr />
<h2 id="extract">EXTRACT</h2>
<p>날짜에서 연도나 월을 추출한다.</p>
<pre><code class="language-sql">EXTRACT(YEAR FROM enrolled_at)</code></pre>
<p>이 기능들은 RDBMS의 데이터 구조를 정의하지는 않는다.</p>
<p>다만 관계형 테이블에서 조회된 데이터를 사용자에게 의미 있는 형태로 표현하는 데 사용된다.</p>
<p>정리하면 다음과 같다.</p>
<pre><code class="language-text">테이블·키·관계·제약조건
→ RDBMS 구조의 핵심

JOIN
→ 관계형 데이터를 조합하는 핵심 연산

CASE·COALESCE·날짜 함수
→ 조회 결과를 표현하고 가공하는 SQL 기능</code></pre>
<hr />
<h1 id="ddl-dml-dql-tcl">DDL, DML, DQL, TCL</h1>
<p>SQL은 목적에 따라 구분할 수 있다.</p>
<h2 id="ddl">DDL</h2>
<p>데이터 구조를 정의한다.</p>
<pre><code class="language-text">CREATE
ALTER
DROP
TRUNCATE</code></pre>
<p>예:</p>
<pre><code class="language-sql">CREATE TABLE students (...);</code></pre>
<hr />
<h2 id="dml">DML</h2>
<p>테이블 내부의 데이터를 변경한다.</p>
<pre><code class="language-text">INSERT
UPDATE
DELETE</code></pre>
<p>예:</p>
<pre><code class="language-sql">INSERT INTO students (...);</code></pre>
<hr />
<h2 id="dql">DQL</h2>
<p>데이터를 조회한다.</p>
<pre><code class="language-text">SELECT</code></pre>
<p>예:</p>
<pre><code class="language-sql">SELECT *
FROM students;</code></pre>
<p>일부 분류에서는 <code>SELECT</code>를 DML에 포함하기도 하지만, 학습 과정에서는 DQL로 분리해서 설명하는 경우가 많다.</p>
<hr />
<h2 id="tcl">TCL</h2>
<p>트랜잭션을 제어한다.</p>
<pre><code class="language-text">COMMIT
ROLLBACK
SAVEPOINT</code></pre>
<hr />
<h1 id="트랜잭션과-acid">트랜잭션과 ACID</h1>
<p>관계형 데이터베이스의 중요한 특징 중 하나는 트랜잭션이다.</p>
<p>트랜잭션은 여러 작업을 하나의 논리적 작업 단위로 묶는다.</p>
<p>예를 들어 수강신청을 처리하면서 다음 작업이 필요할 수 있다.</p>
<pre><code class="language-text">수강신청 행 추가
현재 신청 인원 증가
학생의 신청 학점 증가</code></pre>
<p>중간 작업에서 오류가 발생하면 일부만 반영되어서는 안 된다.</p>
<p>모두 성공하거나 모두 취소되어야 한다.</p>
<hr />
<h2 id="원자성">원자성</h2>
<p>모든 작업이 성공하거나 모두 실패해야 한다.</p>
<hr />
<h2 id="일관성">일관성</h2>
<p>트랜잭션 전후에 데이터베이스 규칙이 유지되어야 한다.</p>
<hr />
<h2 id="격리성">격리성</h2>
<p>동시에 수행되는 트랜잭션이 서로 부적절하게 영향을 주지 않아야 한다.</p>
<hr />
<h2 id="지속성">지속성</h2>
<p>커밋된 결과는 장애가 발생해도 유지되어야 한다.</p>
<p>이 네 가지를 ACID라고 한다.</p>
<hr />
<h1 id="마무리">마무리</h1>
<p>관계형 데이터베이스 설계는 데이터를 무작정 여러 테이블로 나누는 작업이 아니다.</p>
<p>핵심은 다음 세 가지다.</p>
<h2 id="첫째-각-데이터의-책임을-분리한다">첫째, 각 데이터의 책임을 분리한다</h2>
<p>학생 정보, 과목 정보, 전공 정보, 수강 정보를 구분한다.</p>
<hr />
<h2 id="둘째-키를-통해-관계를-표현한다">둘째, 키를 통해 관계를 표현한다</h2>
<p>기본키로 행을 식별하고, 외래키로 테이블을 연결한다.</p>
<hr />
<h2 id="셋째-제약조건으로-업무-규칙을-강제한다">셋째, 제약조건으로 업무 규칙을 강제한다</h2>
<pre><code class="language-text">학번은 중복될 수 없다.
학년은 1~4만 가능하다.
성적은 0~100만 가능하다.
존재하지 않는 학과를 참조할 수 없다.</code></pre>
<p>결국 RDBMS는 단순히 데이터를 저장하는 도구가 아니다.</p>
<blockquote>
<p><strong>현실의 업무 규칙을 테이블, 키, 관계, 제약조건의 형태로 표현하고, 데이터가 그 규칙을 벗어나지 않도록 관리하는 시스템이다.</strong></p>
</blockquote>