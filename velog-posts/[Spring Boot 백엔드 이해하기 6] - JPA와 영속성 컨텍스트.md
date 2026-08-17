<p>지난 글에서는 외부에서 들어온 데이터를 DTO로 받고, Validation을 거쳐 Application 내부로 전달하는 과정을 살펴봤다.</p>
<pre><code class="language-text">Client
  │
  ▼
Request DTO
  │
  ▼
Controller
  │
  ▼
Service
  │
  ▼
Entity</code></pre>
<p>여기서 마지막에 <strong>Entity</strong>라는 객체가 등장했다.</p>
<p>DTO가 외부와 데이터를 주고받기 위한 객체라면, Entity는 Application 내부의 데이터를 표현하면서 Database와 연결되는 객체라고 했다.</p>
<p>그런데 아직 중요한 질문이 남아 있다.</p>
<p>다음 코드를 보자.</p>
<pre><code class="language-java">@Transactional
public void changeName(
        Long userId,
        String newName
) {

    User user = userRepository
            .findById(userId)
            .orElseThrow();

    user.changeName(newName);
}</code></pre>
<p>우리는 직접 다음 SQL을 작성하지 않았다.</p>
<pre><code class="language-sql">UPDATE users
SET name = ?
WHERE id = ?;</code></pre>
<p>심지어 변경한 객체를 다시</p>
<pre><code class="language-java">userRepository.save(user);</code></pre>
<p>하지도 않았다.</p>
<p>그런데 Transaction이 정상적으로 종료되면 Database의 <code>name</code>이 변경될 수 있다.</p>
<p>우리가 한 일이라고는</p>
<pre><code class="language-java">user.changeName(newName);</code></pre>
<p>으로 <strong>Java Object의 상태를 변경한 것뿐이다.</strong></p>
<p>어떻게 객체의 변경이 Database의 변경으로 이어지는 걸까?</p>
<p>이번 글에서는 이 질문을 중심으로 JPA를 살펴본다.</p>
<hr />
<h1 id="java-object와-관계형-database">Java Object와 관계형 Database</h1>
<p>Java Application은 데이터를 객체로 다룬다.</p>
<pre><code class="language-java">User user;
Product product;
Order order;</code></pre>
<p>그리고 객체끼리 관계를 맺을 때도 다른 객체를 직접 참조한다.</p>
<pre><code class="language-java">product.getUser();</code></pre>
<p>Java 입장에서는 자연스럽게 다음처럼 생각할 수 있다.</p>
<pre><code class="language-text">Product Object
      │
      │ reference
      ▼
User Object</code></pre>
<p>하지만 관계형 Database는 객체를 알지 못한다.</p>
<p>Database는 데이터를 Table과 Row로 표현한다.</p>
<pre><code class="language-text">users

id | name
---+------
1  | Alice</code></pre>
<pre><code class="language-text">products

id | name     | user_id
---+----------+--------
10 | Keyboard | 1</code></pre>
<p>그리고 두 데이터 사이의 관계도 객체 Reference가 아니라 <strong>Foreign Key</strong>로 표현한다.</p>
<pre><code class="language-text">products.user_id
       │
       ▼
users.id</code></pre>
<p>즉 같은 데이터를 다루고 있지만 두 세계의 표현 방식은 다르다.</p>
<pre><code class="language-text">Java
─────────────────
Object
Reference
Collection</code></pre>
<pre><code class="language-text">Database
─────────────────
Table
Row
Foreign Key</code></pre>
<p>이 차이를 개발자가 직접 해결한다고 생각해보자.</p>
<p>Java에서</p>
<pre><code class="language-java">User user = new User(&quot;Alice&quot;);</code></pre>
<p>라는 객체를 만들었다면 Database에 저장하기 위해 직접 INSERT SQL을 작성해야 한다.</p>
<pre><code class="language-sql">INSERT INTO users(name)
VALUES ('Alice');</code></pre>
<p>객체의 상태를 변경한다면</p>
<pre><code class="language-java">user.changeName(&quot;Bob&quot;);</code></pre>
<p>이번에는 UPDATE SQL을 작성해야 한다.</p>
<pre><code class="language-sql">UPDATE users
SET name = 'Bob'
WHERE id = 1;</code></pre>
<p>Java에서는 객체를 중심으로 개발하고 싶은데 Database와 이야기할 때마다 다시 Table, Column, Foreign Key, SQL의 관점으로 내려가야 한다.</p>
<p>이 둘 사이를 연결하기 위해 등장한 것이 <strong>ORM</strong>이다.</p>
<hr />
<h1 id="orm과-jpa">ORM과 JPA</h1>
<p>ORM은 <strong>Object-Relational Mapping</strong>의 약자다.</p>
<p>말 그대로 객체와 관계형 Database를 연결한다.</p>
<p>예를 들어 Java에 다음 객체가 있다고 하자.</p>
<pre><code class="language-java">public class User {

    private Long id;
    private String name;
    private String email;
}</code></pre>
<p>Database에는 다음 Table이 있다.</p>
<pre><code class="language-text">users

id
name
email</code></pre>
<p>ORM은 둘 사이의 대응 관계를 정의한다.</p>
<pre><code class="language-text">Java                     Database

User                     users
────                     ─────

id       ──────────────▶ id

name     ──────────────▶ name

email    ──────────────▶ email</code></pre>
<p>그러면 Application에서는 Database Row보다 Java Object를 중심으로 코드를 작성할 수 있다.</p>
<pre><code class="language-java">User user = ...;

user.changeName(&quot;Bob&quot;);</code></pre>
<p>ORM이 이 객체와 Database 사이의 관계를 관리한다.</p>
<p>따라서 ORM을 단순히</p>
<blockquote>
<p>SQL을 작성하지 않아도 되는 기술</p>
</blockquote>
<p>이라고만 이해하면 조금 부족하다.</p>
<p>ORM의 더 중요한 목적은</p>
<blockquote>
<p><strong>관계형 Database의 데이터를 Application에서는 객체로 다룰 수 있게 만드는 것</strong></p>
</blockquote>
<p>이다.</p>
<p>Java에서는 이러한 ORM 사용 방법을 표준화한 <strong>JPA</strong>를 사용한다.</p>
<hr />
<h1 id="jpa-hibernate-spring-data-jpa">JPA, Hibernate, Spring Data JPA</h1>
<p>JPA를 공부하면 다음 이름들이 함께 등장한다.</p>
<pre><code class="language-text">Spring Data JPA
JPA
Hibernate
JDBC</code></pre>
<p>비슷해 보이지만 역할은 서로 다르다.</p>
<p><strong>JPA</strong>는 Java에서 ORM을 사용하기 위한 표준이다.</p>
<pre><code class="language-java">@Entity
@Id
@ManyToOne
@OneToMany</code></pre>
<p>같은 Annotation이나</p>
<pre><code class="language-java">EntityManager</code></pre>
<p>같은 핵심 API의 규칙을 정의한다.</p>
<p>하지만 JPA 자체가 실제로 SQL을 만들고 Database와 통신하는 Engine은 아니다.</p>
<p>JPA는</p>
<pre><code class="language-text">&quot;Java ORM은 이런 방식으로 동작하자.&quot;</code></pre>
<p>라는 규칙에 가깝다.</p>
<p>그 규칙을 실제로 구현하는 대표적인 구현체가 <strong>Hibernate</strong>다.</p>
<p>Hibernate는 실제로 Entity의 상태를 관리하고, 필요한 SQL을 만들고, 연관 Entity의 Loading 등을 처리한다.</p>
<p>그리고 최종적으로 Database와 통신할 때는 JDBC를 사용한다.</p>
<pre><code class="language-text">JPA
 │
 │ 표준
 ▼
Hibernate
 │
 │ 구현
 ▼
JDBC
 │
 ▼
Database</code></pre>
<p>Spring에서는 그 위에 <strong>Spring Data JPA</strong>라는 추상화를 하나 더 제공한다.</p>
<p>우리가 흔히 사용하는 것이 바로 Repository다.</p>
<pre><code class="language-java">public interface UserRepository
        extends JpaRepository&lt;User, Long&gt; {
}</code></pre>
<p>구현 Class를 작성하지 않았는데도</p>
<pre><code class="language-java">userRepository.save(user);
userRepository.findById(id);
userRepository.findAll();
userRepository.delete(user);</code></pre>
<p>를 사용할 수 있다.</p>
<p>결국 큰 구조는 다음과 같다.</p>
<pre><code class="language-text">Service
   │
   ▼
Spring Data JPA
   │
   ▼
JPA
   │
   ▼
Hibernate
   │
   ▼
JDBC
   │
   ▼
Database</code></pre>
<p>정리하면</p>
<pre><code class="language-text">Spring Data JPA
→ JPA를 편리하게 사용하기 위한 Spring의 추상화

JPA
→ Java ORM 표준

Hibernate
→ JPA의 대표적인 구현체

JDBC
→ Java와 DB가 실제로 통신하기 위한 API</code></pre>
<p>다.</p>
<hr />
<h1 id="jpa가-관리하는-객체-entity">JPA가 관리하는 객체, Entity</h1>
<p>JPA가 Database와 연결해서 관리하는 Java Object를 <strong>Entity</strong>라고 한다.</p>
<pre><code class="language-java">@Entity
@Table(name = &quot;users&quot;)
public class User {

    @Id
    @GeneratedValue(
        strategy = GenerationType.IDENTITY
    )
    private Long id;

    @Column(nullable = false)
    private String name;

    private String email;
}</code></pre>
<p>이 Entity는 Database의 <code>users</code> Table과 연결된다.</p>
<pre><code class="language-text">User Entity             users Table

id       ─────────────▶ id

name     ─────────────▶ name

email    ─────────────▶ email</code></pre>
<p><code>@Entity</code>는 해당 Class를 JPA Entity로 사용한다는 의미다.</p>
<p><code>@Id</code>는 Entity를 식별할 값을 지정한다.</p>
<pre><code class="language-java">@Id
private Long id;</code></pre>
<p><code>@GeneratedValue</code>를 사용하면 ID 생성 전략도 지정할 수 있다.</p>
<pre><code class="language-java">@Id
@GeneratedValue(
    strategy = GenerationType.IDENTITY
)
private Long id;</code></pre>
<p>Column의 세부 조건도 표현할 수 있다.</p>
<pre><code class="language-java">@Column(
    name = &quot;user_name&quot;,
    nullable = false,
    length = 50
)
private String name;</code></pre>
<p>Enum도 Mapping할 수 있다.</p>
<pre><code class="language-java">@Enumerated(EnumType.STRING)
private ProductStatus status;</code></pre>
<pre><code class="language-java">public enum ProductStatus {

    ON_SALE,
    SOLD_OUT,
    DISCONTINUED
}</code></pre>
<p>그러면 Database에는</p>
<pre><code class="language-text">ON_SALE
SOLD_OUT
DISCONTINUED</code></pre>
<p>처럼 값 자체가 저장된다.</p>
<p>Enum 순서를 숫자로 저장하는 <code>ORDINAL</code>은 Enum의 순서가 바뀌면 기존 데이터의 의미까지 달라질 수 있기 때문에 일반적으로 <code>STRING</code>을 사용하는 편이 안전하다.</p>
<p>여기까지 보면 JPA가</p>
<pre><code class="language-text">Java Field
    ↕

DB Column</code></pre>
<p>을 연결한다는 것은 이해할 수 있다.</p>
<p>하지만 실제 Application의 객체는 혼자 존재하지 않는다.</p>
<p><strong>객체는 다른 객체와 관계를 가진다.</strong></p>
<p>그리고 이 관계를 어떻게 표현하는지가 ORM에서 굉장히 중요하다.</p>
<hr />
<h2 id="entity의-연관관계">Entity의 연관관계</h2>
<p>사용자와 상품이 있다고 해보자.</p>
<p>한 사용자가 여러 상품을 등록할 수 있다.</p>
<p>Database에서는 이런 구조가 된다.</p>
<pre><code class="language-text">users
────────────────
id | name

1  | Alice</code></pre>
<pre><code class="language-text">products
──────────────────────────
id | name     | user_id

10 | Keyboard | 1
11 | Mouse    | 1</code></pre>
<p><code>products.user_id</code>가 <code>users.id</code>를 가리킨다.</p>
<pre><code class="language-text">products.user_id ──────▶ users.id</code></pre>
<p>Database에서는 아주 자연스럽다.</p>
<p>그런데 Java Entity에서도 이 관계를 그대로 ID로 표현한다고 해보자.</p>
<pre><code class="language-java">@Entity
public class Product {

    private Long id;

    private String name;

    private Long userId;
}</code></pre>
<p>이제 Product를 조회했다.</p>
<pre><code class="language-java">Product product = productRepository
        .findById(productId)
        .orElseThrow();</code></pre>
<p>Product를 등록한 사용자가 필요하다.</p>
<p>하지만 Product가 가지고 있는 것은</p>
<pre><code class="language-java">Long userId;</code></pre>
<p>뿐이다.</p>
<p>따라서 다시 User를 조회해야 한다.</p>
<pre><code class="language-java">Long userId = product.getUserId();

User user = userRepository
        .findById(userId)
        .orElseThrow();</code></pre>
<p>코드의 사고방식도 결국 이렇다.</p>
<pre><code class="language-text">이 Product의 사용자는 누구지?
        ↓
user_id가 몇 번이지?
        ↓
그 ID로 User를 다시 조회하자.</code></pre>
<p>Java Object를 사용하고 있지만 여전히 <strong>Database의 Foreign Key를 중심으로 사고하고 있는 것</strong>이다.</p>
<p>ORM을 사용하는 목적을 생각하면 조금 아쉽다.</p>
<p>Product와 User가 실제로 관계가 있다면 Java에서도 그냥 <strong>Product가 User 객체를 참조하도록 만들면 되지 않을까?</strong></p>
<p>JPA의 연관관계 Mapping이 여기서 등장한다.</p>
<hr />
<h3 id="foreign-key를-object-reference로">Foreign Key를 Object Reference로</h3>
<p>Product를 다음과 같이 만들 수 있다.</p>
<pre><code class="language-java">@Entity
public class Product {

    @Id
    @GeneratedValue
    private Long id;

    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = &quot;user_id&quot;)
    private User user;
}</code></pre>
<p>이제 <code>Product</code>는 <code>userId</code>라는 숫자를 가지고 있지 않는다.</p>
<p>대신 실제 <code>User</code> 객체를 참조한다.</p>
<p>Database 구조는 그대로다. Database에서는 여전히 <code>products.user_id</code>라는 Foreign Key가 <code>users.id</code>를 가리킨다.</p>
<p>JPA는 이 두 표현을 연결한다.</p>
<pre><code class="language-text">Java                           Database

Product.user                  products.user_id
     │                              │
     ▼                              ▼
   User                           users.id</code></pre>
<p>즉 <strong>연관관계 Mapping은 Database의 Foreign Key 관계를 Java에서는 Object Reference로 사용할 수 있도록 연결하는 것</strong>이다.</p>
<p>이제 사용자가 필요하면</p>
<pre><code class="language-java">User user = product.getUser();</code></pre>
<p>라고 하면 된다.</p>
<p>이름까지 필요하다면</p>
<pre><code class="language-java">String userName =
        product.getUser().getName();</code></pre>
<p>처럼 객체의 관계를 따라갈 수 있다.</p>
<p>이처럼 연관된 객체를 Reference를 따라 탐색하는 것을 <strong>객체 그래프 탐색</strong>이라고 볼 수 있다.</p>
<p>결국 Database에서는 Foreign Key로 표현되는 관계를 Application에서는 <code>Product → User</code>라는 객체 관계로 사용할 수 있게 되는 것이다.</p>
<h4 id="manytoone은-관계를-바라보는-방향이다">ManyToOne은 관계를 바라보는 방향이다</h4>
<p>한 User가 여러 Product를 등록할 수 있다고 하자.</p>
<pre><code class="language-text">Product ─┐
Product ─┼──▶ User
Product ─┘</code></pre>
<p>Product의 입장에서는 여러 Product가 하나의 User를 참조하므로 <code>ManyToOne</code> 관계다.</p>
<pre><code class="language-java">@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = &quot;user_id&quot;)
private User user;</code></pre>
<p><code>@JoinColumn(name = &quot;user_id&quot;)</code>은 이 객체 관계가 Database에서는 <code>products.user_id</code>라는 Foreign Key로 표현된다는 의미다.</p>
<p>즉 <code>@ManyToOne</code>은 Database의 다대일 관계를 <strong>Product에서 User로 향하는 Object Reference</strong>로 표현하는 방법이다.</p>
<h4 id="반대-방향이-필요하면-onetomany를-추가한다">반대 방향이 필요하면 OneToMany를 추가한다</h4>
<p>현재 <code>Product.user</code>만 존재한다면 객체를 탐색할 수 있는 방향은 다음과 같다.</p>
<pre><code class="language-text">Product ─────▶ User</code></pre>
<p>그런데 반대로</p>
<blockquote>
<p>이 User가 등록한 Product들은 무엇인가?</p>
</blockquote>
<p>도 객체에서 탐색하고 싶을 수 있다.</p>
<p>이 경우 User에도 관계를 추가한다.</p>
<pre><code class="language-java">@Entity
public class User {

    @Id
    private Long id;

    private String name;

    @OneToMany(mappedBy = &quot;user&quot;)
    private List&lt;Product&gt; products
            = new ArrayList&lt;&gt;();
}</code></pre>
<p>이제 <code>user.getProducts()</code>를 통해 반대 방향으로도 탐색할 수 있다.</p>
<pre><code class="language-text">Product ─────▶ User
   ▲            │
   └────────────┘
      products</code></pre>
<p>이처럼 같은 관계를 객체에서 양쪽 방향으로 탐색할 수 있도록 만든 것을 <strong>양방향 연관관계</strong>라고 한다.</p>
<p>여기서 중요한 것은 <strong>Database의 관계까지 두 개가 된 것은 아니라는 점</strong>이다.</p>
<p>Database에서는 여전히 하나의 Foreign Key만 관계를 표현한다.</p>
<pre><code class="language-text">products.user_id ─────▶ users.id</code></pre>
<p>Java에서 같은 관계를 양쪽으로 탐색하기 위해 <code>Product.user</code>와 <code>User.products</code>라는 두 Reference를 둔 것이다.</p>
<p>그렇다면 새로운 문제가 생긴다.</p>
<blockquote>
<p>두 Reference 중 어느 쪽의 변경을 실제 Foreign Key 변경으로 봐야 할까?</p>
</blockquote>
<p>여기서 <strong>연관관계의 주인</strong>이 필요해진다.</p>
<h4 id="왜-연관관계의-주인이-필요할까">왜 연관관계의 주인이 필요할까?</h4>
<p>객체에는 이제 관계가 두 군데 존재한다.</p>
<pre><code class="language-java">Product.user</code></pre>
<pre><code class="language-java">User.products</code></pre>
<p>그런데 Database에서 실제 관계를 결정하는 값은 하나다.</p>
<pre><code class="language-text">products.user_id</code></pre>
<p>그렇다면 JPA 입장에서는 문제가 생긴다.</p>
<p>예를 들어</p>
<pre><code class="language-java">product.setUser(user);</code></pre>
<p>로 <code>Product.user</code>를 변경했다.</p>
<p>동시에</p>
<pre><code class="language-java">user.getProducts().add(product);</code></pre>
<p>로 <code>User.products</code>도 변경할 수 있다.</p>
<p>그러면 JPA는 어느 변경을 기준으로 <code>products.user_id</code>를 수정해야 할까?</p>
<pre><code class="language-text">Product.user 변경
        │
        ├──── 누가 FK를 바꾸지?
        │
User.products 변경</code></pre>
<p>Database의 FK는 하나이기 때문에 <strong>FK 변경의 기준도 하나로 정해야 한다.</strong></p>
<p>이 기준이 바로 <strong>연관관계의 주인</strong>이다.</p>
<p>현재 FK는 <code>products</code> Table에 있다.</p>
<pre><code class="language-text">products.user_id</code></pre>
<p>그래서 이 FK와 직접 연결된</p>
<pre><code class="language-java">@ManyToOne
@JoinColumn(name = &quot;user_id&quot;)
private User user;</code></pre>
<p>즉 <code>Product.user</code>가 관계를 관리한다.</p>
<p>반대쪽은</p>
<pre><code class="language-java">@OneToMany(mappedBy = &quot;user&quot;)
private List&lt;Product&gt; products;</code></pre>
<p>처럼 <code>mappedBy</code>를 사용한다.</p>
<p>여기서</p>
<pre><code class="language-java">mappedBy = &quot;user&quot;</code></pre>
<p>의 <code>user</code>는 <code>Product</code> Class 안에 있는 다음 Field 이름을 의미한다.</p>
<pre><code class="language-java">private User user;</code></pre>
<p>전체 구조를 보면 간단하다.</p>
<pre><code class="language-text">User

@OneToMany(mappedBy = &quot;user&quot;)
List&lt;Product&gt; products
          │
          │ 반대편 관계
          ▼

Product

@ManyToOne
User user
          │
          │ FK 변경 기준
          ▼

products.user_id</code></pre>
<p>즉 <code>mappedBy</code>는</p>
<blockquote>
<p><strong>내가 이 관계의 FK를 직접 관리하는 쪽이 아니다. 실제 관계는 상대 Entity의 <code>user</code> Field가 관리한다.</strong></p>
</blockquote>
<p>라는 뜻이다.</p>
<p>연관관계의 주인은 이름 때문에 중요한 Entity를 고르는 개념처럼 보이지만 사실 훨씬 단순하다.</p>
<blockquote>
<p><strong>Database의 FK 값을 어떤 객체 Field의 변경을 기준으로 수정할 것인가?</strong></p>
</blockquote>
<p>를 결정하는 개념이다.</p>
<hr />
<h3 id="db-관계와-java-객체-상태는-다른-문제다">DB 관계와 Java 객체 상태는 다른 문제다</h3>
<p>여기서 자주 헷갈리는 부분이 하나 있다.</p>
<p>FK를 관리하는 쪽이 <code>Product.user</code>라면 Database 관계를 만들 때는 다음 코드가 중요하다.</p>
<pre><code class="language-java">product.setUser(user);</code></pre>
<p>그런데 실제 JPA 코드를 보면 양쪽을 모두 변경하는 경우가 많다.</p>
<pre><code class="language-java">user.getProducts().add(product);

product.setUser(user);</code></pre>
<p>혹은 아예 편의 Method를 만든다.</p>
<pre><code class="language-java">public void addProduct(Product product) {

    products.add(product);
    product.setUser(this);
}</code></pre>
<p>왜 <code>User.products</code>까지 수정할까?</p>
<p><strong>DB의 Foreign Key를 변경하기 위해서가 아니다.</strong></p>
<p>현재 Java Object의 상태를 일치시키기 위해서다.</p>
<p>예를 들어 이것만 실행했다고 하자.</p>
<pre><code class="language-java">product.setUser(user);</code></pre>
<p>현재 Product에서는 User를 정상적으로 볼 수 있다.</p>
<pre><code class="language-java">product.getUser();</code></pre>
<pre><code class="language-text">Product ─────▶ User</code></pre>
<p>하지만 User 객체의 Collection에는 아직 Product가 없을 수 있다.</p>
<pre><code class="language-java">user.getProducts();</code></pre>
<pre><code class="language-text">User

products = []</code></pre>
<p>즉 현재 Java Heap에서는 같은 관계를 바라보는 두 객체의 상태가 서로 맞지 않는다.</p>
<pre><code class="language-text">Product
   │
   └─────▶ User

User
   │
   └─────▶ products에는 Product 없음</code></pre>
<p>그래서 양방향 관계를 사용한다면 양쪽 Reference를 함께 맞춰준다.</p>
<pre><code class="language-java">public void addProduct(Product product) {

    products.add(product);
    product.setUser(this);
}</code></pre>
<p>그 결과</p>
<pre><code class="language-text">Product ─────▶ User
   ▲             │
   └─────────────┘
     products</code></pre>
<p>처럼 현재 Object Graph도 일관된 상태가 된다.</p>
<p>따라서 두 개를 구분하면 된다.</p>
<pre><code class="language-text">Product.user 변경
→ Database FK 변경의 기준</code></pre>
<pre><code class="language-text">User.products도 함께 변경
→ 현재 Java Object 상태의 일관성 유지</code></pre>
<p><strong>DB에 관계를 두 번 저장하는 것이 아니다.</strong></p>
<blockquote>
<p>실제 데이터베이스에는 연관관계의 주인만을 기준으로 반영된다.</p>
</blockquote>
<p>이 구분이 양방향 연관관계를 이해할 때 가장 중요하다.</p>
<hr />
<h3 id="연관관계는-결국-객체-중심의-코드를-만든다">연관관계는 결국 객체 중심의 코드를 만든다</h3>
<p>결국 연관관계 Mapping의 효과는 단순히 Foreign Key를 감춰주는 데 있지 않다.</p>
<p>연관관계가 없다면 다른 Entity가 필요할 때 ID를 꺼내 다시 Repository를 호출해야 한다.</p>
<pre><code class="language-java">Long userId = product.getUserId();

User user = userRepository
        .findById(userId)
        .orElseThrow();</code></pre>
<p>반면 연관관계가 Mapping되어 있다면 Domain의 관계를 그대로 따라갈 수 있다.</p>
<pre><code class="language-java">User user = product.getUser();</code></pre>
<p>즉 Application의 사고방식이</p>
<pre><code class="language-text">Product
   ↓
userId
   ↓
Repository
   ↓
User</code></pre>
<p>에서</p>
<pre><code class="language-text">Product
   ↓
User</code></pre>
<p>로 바뀐다.</p>
<p><code>product.getUser()</code>처럼 Domain의 관계가 코드에 그대로 드러나면서, 개발자는 Foreign Key를 직접 추적하기보다 객체 그래프를 따라 비즈니스 로직을 작성할 수 있게 된다.</p>
<p>이것이 JPA가 단순한 SQL 생성 도구가 아니라 ORM인 이유 중 하나다.</p>
<h3 id="지연로딩">지연로딩</h3>
<p>연관관계를 만들면서 객체 관점에서는 상당히 편해졌다.</p>
<pre><code class="language-java">product.getUser();</code></pre>
<p>하지만 새로운 문제가 생긴다.</p>
<p>Product를 조회한다고 해서 항상 User 정보까지 필요한 것은 아니다.</p>
<pre><code class="language-java">Product product = productRepository
        .findById(id)
        .orElseThrow();

System.out.println(product.getName());</code></pre>
<p>여기에서는 Product의 이름만 필요하다.</p>
<p>연관관계가 있다는 이유만으로 User까지 항상 조회하면 불필요한 Database 접근이 발생할 수 있다.</p>
<p>그래서 JPA에서는 <strong>연관 Entity를 언제 가져올 것인지</strong>도 결정할 수 있다.</p>
<pre><code class="language-java">@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = &quot;user_id&quot;)
private User user;</code></pre>
<p><code>LAZY</code>는 연관 Entity의 실제 조회를 필요한 시점까지 미룬다.</p>
<p>Product를 조회한 시점에는</p>
<pre><code class="language-text">Product
   │
   ▼
User를 가리킬 수 있음

하지만 실제 User 데이터는
아직 필요하지 않음</code></pre>
<p>상태로 둘 수 있다.</p>
<p>나중에</p>
<pre><code class="language-java">product.getUser().getName();</code></pre>
<p>처럼 실제 User 정보가 필요해지면 그때 데이터를 가져온다.</p>
<p>이 과정에는 Proxy가 사용될 수 있다.</p>
<pre><code class="language-text">Product
   │
   ▼
User Proxy
   │
   │ 실제 정보 필요
   ▼
User Loading</code></pre>
<p>앞에서 공부했던 Spring AOP Proxy와 이름은 같지만 목적은 다르다.</p>
<pre><code class="language-text">Spring AOP Proxy
→ Method 호출을 가로채 부가기능 적용

JPA Lazy Proxy
→ 연관 Entity의 실제 조회 시점을 지연</code></pre>
<p>그리고 여기서 자연스럽게 다음 질문이 생긴다.</p>
<p>우리는 지금</p>
<pre><code class="language-text">User
Product
Product.user
User.products</code></pre>
<p>처럼 여러 Entity와 그 관계를 객체로 다루고 있다.</p>
<p>또 JPA는 어떤 Entity는 이미 조회했다고 기억하고, 어떤 Entity는 나중에 조회하며, 객체의 변경까지 추적한다.</p>
<p><strong>대체 누가 이 Entity들을 계속 관리하고 있는 걸까?</strong></p>
<p>여기서 JPA의 핵심인 <strong>EntityManager와 Persistence Context</strong>가 등장한다.</p>
<hr />
<h1 id="entitymanager와-persistence-context">EntityManager와 Persistence Context</h1>
<p>JPA에서 Entity를 관리하는 핵심 Interface가 <code>EntityManager</code>다.</p>
<p>대표적으로 다음 작업을 수행한다.</p>
<pre><code class="language-java">em.persist(user);</code></pre>
<p>새로운 Entity를 관리 대상으로 만든다.</p>
<pre><code class="language-java">em.find(User.class, id);</code></pre>
<p>Entity를 조회한다.</p>
<pre><code class="language-java">em.remove(user);</code></pre>
<p>Entity를 삭제 대상으로 만든다.</p>
<pre><code class="language-java">em.flush();</code></pre>
<p>현재 변경 내용을 Database와 동기화한다.</p>
<p>하지만 EntityManager 자체를 단순히</p>
<blockquote>
<p>SQL을 실행하는 객체</p>
</blockquote>
<p>라고 이해하면 JPA의 핵심을 놓치게 된다.</p>
<p>EntityManager는 Entity를 <strong>Persistence Context</strong>, 영속성 컨텍스트라는 공간에서 관리한다.</p>
<p>영속성 컨텍스트는 쉽게 말하면</p>
<blockquote>
<p><strong>Entity를 보관하고 상태를 추적하면서 Database와 동기화하기 위한 JPA의 관리 공간</strong></p>
</blockquote>
<p>이다.</p>
<pre><code class="language-text">EntityManager
      │
      ▼
Persistence Context

┌───────────────────────────┐
│                           │
│ User Entity               │
│ Product Entity            │
│                           │
│ 1차 cache                 │
│ 상태 추적                   │
│ 변경 감지                   │
│ 쓰기 지연                   │
│                           │
└───────────────────────────┘
      │
      ▼
Database</code></pre>
<p>이 구조 때문에 JPA는 단순한 SQL Mapper와 다르다.</p>
<p>단순히</p>
<pre><code class="language-text">Method 호출
   ↓
SQL 실행</code></pre>
<p>으로 끝나는 것이 아니다.</p>
<p>JPA는</p>
<pre><code class="language-text">Entity 조회
   ↓
Persistence Context에서 관리
   ↓
Entity 사용
   ↓
상태 변경
   ↓
변경 추적
   ↓
Database와 동기화</code></pre>
<p>라는 흐름을 가진다.</p>
<hr />
<h2 id="entity의-상태">Entity의 상태</h2>
<p>모든 Entity가 항상 Persistence Context의 관리 대상은 아니다.</p>
<p>Entity와 Persistence Context의 관계에 따라 상태가 나뉜다.</p>
<pre><code class="language-text">          persist / find

Transient ─────────────▶ Managed
비영속                    영속
                           │
                     detach / clear
                           │
                           ▼
                        Detached
                         준영속

Managed ── remove ─────▶ Removed
                         삭제</code></pre>
<p>Java에서 객체만 생성한 상태는 <strong>비영속</strong>이다.</p>
<pre><code class="language-java">User user = new User(&quot;Alice&quot;);</code></pre>
<p>아직 JPA는 이 객체를 관리하지 않는다.</p>
<pre><code class="language-text">Java Heap

User</code></pre>
<p>이 Entity를</p>
<pre><code class="language-java">em.persist(user);</code></pre>
<p>로 Persistence Context에 등록하거나</p>
<pre><code class="language-java">em.find(User.class, 1L);</code></pre>
<p>로 Database에서 조회하면 <strong>영속 상태</strong>가 된다.</p>
<pre><code class="language-text">Persistence Context

┌──────────────────┐
│ User(id = 1)     │
└──────────────────┘</code></pre>
<p>영속 상태가 중요한 이유는 <strong>JPA가 이 Entity의 상태를 계속 관리하기 시작하기 때문</strong>이다.</p>
<p>반대로</p>
<pre><code class="language-java">em.detach(user);</code></pre>
<p>하면 특정 Entity를 관리 대상에서 제외할 수 있고,</p>
<pre><code class="language-java">em.clear();</code></pre>
<p>하면 현재 Persistence Context를 비울 수 있다.</p>
<p>객체 자체가 사라지는 것은 아니지만 더 이상 현재 Persistence Context가 상태를 추적하지 않는다.</p>
<hr />
<h2 id="왜-entity를-관리할까">왜 Entity를 관리할까?</h2>
<p>Persistence Context가 굳이 Entity를 계속 관리하는 이유가 있다.</p>
<p>대표적으로 다음 기능이 가능해진다.</p>
<pre><code class="language-text">1차 Cache
Entity 동일성
Dirty Checking
Write-Behind
Lazy Loading</code></pre>
<p>이 기능들은 따로 떨어진 기능처럼 보이지만 사실 모두</p>
<blockquote>
<p><strong>JPA가 Entity를 일회성 데이터가 아니라 관리 중인 객체로 취급한다.</strong></p>
</blockquote>
<p>는 하나의 특징에서 나온다.</p>
<hr />
<h3 id="1차-cache와-동일성">1차 Cache와 동일성</h3>
<p>다음 Entity를 조회한다고 하자.</p>
<pre><code class="language-java">User user1 =
        em.find(User.class, 1L);</code></pre>
<p>Persistence Context에 해당 Entity가 없다면 Database에서 조회한다.</p>
<pre><code class="language-text">Persistence Context
      │
      │ 없음
      ▼
Database
      │
      ▼
User(id = 1)</code></pre>
<p>그리고 가져온 Entity를 Persistence Context에 보관한다.</p>
<pre><code class="language-text">Persistence Context

PK       Entity
──────────────────
1        User(...)</code></pre>
<p>같은 Entity를 다시 조회한다.</p>
<pre><code class="language-java">User user2 =
        em.find(User.class, 1L);</code></pre>
<p>이번에는 Persistence Context에서 먼저 찾을 수 있다.</p>
<pre><code class="language-text">find(User, 1)
      │
      ▼
Persistence Context
      │
      ▼
User(id = 1)</code></pre>
<p>이것이 <strong>1차 Cache</strong>다.</p>
<p>Redis처럼 여러 요청이 공유하는 별도의 Cache와는 다르다.</p>
<p>현재 Persistence Context 안에서 Entity를 관리하기 위한 Cache다.</p>
<p>또 같은 Persistence Context에서 같은 PK를 조회하면 하나의 관리 Entity를 사용한다.</p>
<pre><code class="language-java">User user1 = em.find(User.class, 1L);
User user2 = em.find(User.class, 1L);</code></pre>
<p>일반적으로</p>
<pre><code class="language-java">user1 == user2</code></pre>
<p>가 성립한다.</p>
<p>Database의</p>
<pre><code class="language-text">users.id = 1</code></pre>
<p>이라는 하나의 Record를 Application에서도 하나의 Entity Instance로 관리하는 것이다.</p>
<hr />
<h3 id="dirty-checking">Dirty Checking</h3>
<p>이제 글 처음에 봤던 코드로 돌아가자.</p>
<pre><code class="language-java">@Transactional
public void changeName(
        Long userId,
        String newName
) {

    User user = userRepository
            .findById(userId)
            .orElseThrow();

    user.changeName(newName);
}</code></pre>
<p>조회된 <code>user</code>는 현재 Persistence Context가 관리하는 <strong>Managed Entity</strong>다.</p>
<p>처음 조회한 상태가</p>
<pre><code class="language-text">User

name = Alice</code></pre>
<p>였다고 하자.</p>
<p>Service에서</p>
<pre><code class="language-java">user.changeName(&quot;Bob&quot;);</code></pre>
<p>을 실행한다.</p>
<p>현재 객체의 상태는</p>
<pre><code class="language-text">User

name = Bob</code></pre>
<p>으로 바뀐다.</p>
<p>JPA는 Managed Entity의 상태를 추적하고 있기 때문에 이 변경을 발견할 수 있다.</p>
<pre><code class="language-text">처음 상태
Alice

    ↓

현재 상태
Bob

    ↓

변경 발견</code></pre>
<p>그리고 Database와 동기화하는 과정에서 필요한 UPDATE SQL을 만든다.</p>
<pre><code class="language-sql">UPDATE users
SET name = 'Bob'
WHERE id = 1;</code></pre>
<p>이것이 <strong>Dirty Checking</strong>, 변경 감지다.</p>
<p>따라서 JPA의 수정에서는</p>
<pre><code class="language-text">UPDATE Method를 호출했는가?</code></pre>
<p>보다</p>
<blockquote>
<p><strong>현재 객체가 Managed Entity이고 그 상태가 변경되었는가?</strong></p>
</blockquote>
<p>가 중요하다.</p>
<p>그래서 이미 Managed 상태인 Entity는 수정 후 무조건</p>
<pre><code class="language-java">userRepository.save(user);</code></pre>
<p>를 다시 호출할 필요가 없다.</p>
<hr />
<h3 id="write-behind와-flush">Write-Behind와 Flush</h3>
<p>Entity를 변경했다고 해서 SQL이 항상 즉시 Database로 전달되는 것도 아니다.</p>
<p>JPA는 Persistence Context 안에서 변경 사항을 관리하고 적절한 시점에 Database와 동기화할 수 있다.</p>
<pre><code class="language-text">Entity 저장
Entity 변경
Entity 삭제

      │
      ▼

Persistence Context

      │
      ▼

flush

      │
      ├─ INSERT
      ├─ UPDATE
      └─ DELETE

      ▼
Database</code></pre>
<p>이런 구조를 <strong>쓰기 지연, Write-Behind</strong>와 연결해서 이해할 수 있다.</p>
<p>다만 실제 SQL 실행 시점은 ID 생성 전략이나 Query 실행 등의 상황에 따라 달라질 수 있다.</p>
<p>핵심은</p>
<pre><code class="language-text">Java Object 변경
→ 반드시 즉시 SQL 실행</code></pre>
<p>이 아니라</p>
<blockquote>
<p><strong>JPA가 Entity 상태와 Database 동기화 시점을 관리한다.</strong></p>
</blockquote>
<p>는 것이다.</p>
<p>Persistence Context의 변경 내용을 Database에 동기화하는 과정이 <strong>Flush</strong>다.</p>
<pre><code class="language-text">Persistence Context
      │
      │ flush
      ▼
Database</code></pre>
<p>Dirty Checking 역시 Flush 과정과 연결된다.</p>
<pre><code class="language-text">Managed Entity 변경
       │
       ▼
Dirty Checking
       │
       ▼
flush
       │
       ▼
UPDATE SQL</code></pre>
<p>하지만 반드시 기억해야 할 것이 있다.</p>
<blockquote>
<p><strong>Flush와 Commit은 다르다.</strong></p>
</blockquote>
<p>Flush는 현재 변경 사항을 Database에 전달해 Persistence Context와 Database의 상태를 맞춘다.</p>
<pre><code class="language-text">Transaction BEGIN
      │
      ▼
Entity 변경
      │
      ▼
flush
      │
      ▼
SQL 실행
      │
      ▼
COMMIT</code></pre>
<p>Flush가 수행되었다고 Transaction이 성공한 것은 아니다.</p>
<p>이후 Rollback된다면 변경은 최종 확정되지 않는다.</p>
<p>따라서</p>
<pre><code class="language-text">flush
→ Persistence Context와 DB 동기화

commit
→ Transaction 결과 최종 확정</code></pre>
<p>으로 구분하면 된다.</p>
<hr />
<h1 id="repository-뒤의-entitymanager">Repository 뒤의 EntityManager</h1>
<p>우리가 실제 Application에서 직접 <code>EntityManager</code>를 사용하는 경우는 많지 않을 수 있다.</p>
<p>보통 다음처럼 Repository를 사용한다.</p>
<pre><code class="language-java">userRepository.save(user);</code></pre>
<p>하지만 구조를 내려가 보면 결국 EntityManager가 존재한다.</p>
<pre><code class="language-text">UserRepository
      │
      ▼
Spring Data JPA
      │
      ▼
EntityManager
      │
      ▼
Persistence Context
      │
      ▼
Hibernate
      │
      ▼
JDBC
      │
      ▼
Database</code></pre>
<p>즉 Spring Data JPA가 EntityManager나 Persistence Context를 없앤 것이 아니다.</p>
<p>개발자가 편하게 사용할 수 있도록 그 위에 Repository라는 추상화를 제공한 것이다.</p>
<pre><code class="language-text">JpaRepository
→ 개발자가 사용하는 고수준 API

EntityManager
→ JPA의 Entity 관리 API

Persistence Context
→ Entity가 실제로 관리되는 공간</code></pre>
<p>그래서 JPA를 제대로 이해하려면 Repository Method만 보는 것보다 그 아래에 존재하는 EntityManager와 Persistence Context를 이해하는 것이 중요하다.</p>
<hr />
<h1 id="persistence-context와-transaction">Persistence Context와 Transaction</h1>
<p>마지막으로 한 가지가 남는다.</p>
<p>Persistence Context에서는 지금까지 많은 일이 일어났다.</p>
<pre><code class="language-text">Entity 조회
Entity 관계 탐색
1차 Cache
상태 변경
Dirty Checking
Write-Behind
Lazy Loading</code></pre>
<p>그렇다면 이 관리가 언제 시작되고 언제 끝나야 할까?</p>
<p>예를 들어 주문 생성이라는 하나의 업무가 있다고 하자.</p>
<pre><code class="language-text">상품 조회
   ↓
재고 감소
   ↓
주문 저장</code></pre>
<p>재고 감소만 성공하고 주문 저장은 실패하면 안 된다.</p>
<p>우리가 원하는 것은</p>
<pre><code class="language-text">모두 성공
→ 반영</code></pre>
<p>하거나</p>
<pre><code class="language-text">하나라도 실패
→ 전체 취소</code></pre>
<p>하는 것이다.</p>
<p>그래서 JPA의 Persistence Context는 <strong>Transaction과 강하게 연결된다.</strong></p>
<pre><code class="language-text">Transaction BEGIN
      │
      ▼
Persistence Context
      │
      ├─ Entity 조회
      ├─ 연관관계 탐색
      ├─ Entity 변경
      └─ Dirty Checking
      │
      ▼
flush
      │
      ▼
COMMIT</code></pre>
<p>Spring에서는 주로 <code>@Transactional</code>을 통해 이 Transaction 경계를 만든다.</p>
<pre><code class="language-java">@Transactional
public void changeName(
        Long userId,
        String newName
) {

    User user = userRepository
            .findById(userId)
            .orElseThrow();

    user.changeName(newName);
}</code></pre>
<p>그리고 <code>@Transactional</code>의 동작 방식 역시 앞에서 살펴본 Proxy와 연결된다.</p>
<pre><code class="language-text">Caller
   │
   ▼
Transaction Proxy
   │
   ├─ Transaction BEGIN
   ▼
Service
   │
   ▼
Persistence Context
   │
   ├─ Entity 조회
   ├─ Managed 상태
   ├─ 변경 추적
   └─ Dirty Checking
   │
   ▼
flush
   │
   ▼
Transaction Proxy
   │
   ├─ COMMIT
   ▼
Caller</code></pre>
<p>이제 <code>@Transactional</code>을 단순히</p>
<pre><code class="language-text">Commit / Rollback을 자동으로 해주는 Annotation</code></pre>
<p>으로만 볼 필요가 없다.</p>
<p>JPA의 관점에서는</p>
<blockquote>
<p><strong>Persistence Context가 Entity를 하나의 업무 단위 안에서 관리할 수 있도록 만드는 중요한 경계</strong></p>
</blockquote>
<p>이기도 하다.</p>
<p>Transaction의 전파 방식이나 Rollback 규칙, 동시성 제어는 Transaction 자체를 다룰 때 더 자세히 살펴볼 수 있다.</p>
<hr />
<h1 id="처음의-코드로-돌아가-보자">처음의 코드로 돌아가 보자</h1>
<p>이제 처음의 코드가 완전히 다르게 보인다.</p>
<pre><code class="language-java">@Transactional
public void changeName(
        Long userId,
        String newName
) {

    User user = userRepository
            .findById(userId)
            .orElseThrow();

    user.changeName(newName);
}</code></pre>
<p>겉으로 보면</p>
<pre><code class="language-text">User 조회
   ↓
name 변경</code></pre>
<p>이 전부다.</p>
<p>하지만 그 뒤에서는 다음 흐름이 움직이고 있다.</p>
<pre><code class="language-text">Controller
    │
    ▼
Transaction Proxy
    │
    ├─ Transaction BEGIN
    ▼
Service
    │
    ▼
Repository
    │
    ▼
Spring Data JPA
    │
    ▼
EntityManager
    │
    ▼
Persistence Context
    │
    ├─ User 조회
    ├─ 1차 Cache
    └─ Managed 상태
    │
    ▼
user.changeName()
    │
    ▼
Entity 상태 변경
    │
    ▼
Dirty Checking
    │
    ▼
flush
    │
    ▼
UPDATE SQL
    │
    ▼
Database
    │
    ▼
COMMIT</code></pre>
<p>우리가 직접 UPDATE SQL을 작성하지 않았는데도 Database가 변경될 수 있었던 이유다.</p>
<hr />
<h1 id="정리">정리</h1>
<p>JPA의 출발점은 Java Object와 관계형 Database가 데이터를 바라보는 방식이 다르다는 데 있다.</p>
<pre><code class="language-text">Java
────────────────
Object
Reference

Database
────────────────
Table
Foreign Key</code></pre>
<p>ORM은 이 차이를 연결하고, Java에서는 그 ORM 사용 방법에 대한 표준으로 JPA를 사용한다.</p>
<pre><code class="language-text">Spring Data JPA
      │
      ▼
JPA
      │
      ▼
Hibernate
      │
      ▼
JDBC
      │
      ▼
Database</code></pre>
<p>JPA가 관리하는 Java Object가 Entity다.</p>
<p>Entity는 단순히 Field와 Column만 Mapping하는 것이 아니다.</p>
<pre><code class="language-text">Field
  ↕
Column</code></pre>
<p>객체의 관계와 Database의 관계도 연결한다.</p>
<pre><code class="language-text">Object Reference
       ↕

Foreign Key</code></pre>
<p>예를 들어 Database에서는</p>
<pre><code class="language-text">products.user_id
       │
       ▼
users.id</code></pre>
<p>로 표현되는 관계를 Application에서는</p>
<pre><code class="language-text">Product
   │
   ▼
User</code></pre>
<p>로 사용할 수 있다.</p>
<p>따라서</p>
<pre><code class="language-java">product.getUser();</code></pre>
<p>처럼 객체 관계를 그대로 탐색할 수 있다.</p>
<p>양방향 탐색이 필요하다면</p>
<pre><code class="language-text">Product → User
User → Products</code></pre>
<p>두 Reference를 만들 수 있지만 Database의 FK는 여전히 하나뿐이다.</p>
<p>그래서 FK 변경의 기준이 되는 <strong>연관관계의 주인</strong>을 정한다.</p>
<pre><code class="language-text">User.products
      │
      │ mappedBy
      ▼
Product.user
      │
      │ FK 변경 기준
      ▼
products.user_id</code></pre>
<p>그리고 양쪽 Object Reference를 함께 맞추는 것은 Database에 관계를 두 번 저장하기 위해서가 아니다.</p>
<p><strong>현재 Java Object Graph의 상태를 일관되게 유지하기 위해서다.</strong></p>
<p>JPA는 이렇게 Mapping된 Entity를 단순히 생성하고 끝내지 않는다.</p>
<p>EntityManager와 Persistence Context를 통해 Entity를 계속 관리한다.</p>
<pre><code class="language-text">EntityManager
      │
      ▼
Persistence Context
      │
      ├─ 1차 Cache
      ├─ Entity 동일성
      ├─ Dirty Checking
      ├─ Write-Behind
      └─ Lazy Loading</code></pre>
<p>그래서 Managed Entity의 상태를</p>
<pre><code class="language-java">user.changeName(&quot;Bob&quot;);</code></pre>
<p>처럼 변경하면 JPA가 이를 추적할 수 있다.</p>
<pre><code class="language-text">Managed Entity
      │
      ▼
상태 변경
      │
      ▼
Dirty Checking
      │
      ▼
flush
      │
      ▼
UPDATE</code></pre>
<p>그리고</p>
<pre><code class="language-text">flush
→ Persistence Context의 변경 사항을 DB와 동기화

commit
→ Transaction 결과를 최종 확정</code></pre>
<p>이라는 차이가 있다.</p>
<p>이러한 Entity 관리의 중요한 작업 경계가 Transaction이다.</p>
<pre><code class="language-text">@Transactional
      │
      ▼
Transaction BEGIN
      │
      ▼
Persistence Context
      │
      ├─ Entity 조회
      ├─ 객체 그래프 탐색
      ├─ Entity 변경
      └─ Dirty Checking
      │
      ▼
flush
      │
      ▼
COMMIT / ROLLBACK</code></pre>
<p>결국 JPA를 단순히</p>
<blockquote>
<p>SQL을 자동으로 만들어주는 기술</p>
</blockquote>
<p>이라고 이해하면 핵심을 놓치게 된다.</p>
<p>JPA를 한 문장으로 정리하면 다음과 같다.</p>
<blockquote>
<p><strong>JPA는 Java Object의 상태와 관계를 관계형 Database의 Table과 Foreign Key에 Mapping하고, Entity를 영속성 컨텍스트에서 관리하면서 객체의 상태를 Database와 동기화하기 위한 ORM 표준이다.</strong></p>
</blockquote>
<p>Spring Data JPA는 그 위에서 Repository 사용을 한 단계 더 추상화한다.</p>
<pre><code class="language-text">우리가 작성하는 코드

Service
Repository
Entity
Object Relationship


        ↓


Spring Data JPA / JPA

EntityManager
Persistence Context


        ↓


Hibernate
JDBC


        ↓


Database

Table
Foreign Key</code></pre>
<p>Spring Data JPA가 편한 이유는 이 복잡한 과정이 사라졌기 때문이 아니다.</p>
<p><strong>Database의 Table과 Foreign Key를 Java에서는 Entity와 Object Reference로 다룰 수 있게 하고, 그 객체들의 상태를 JPA가 관리해주기 때문에 개발자는 Database 구조보다 객체와 비즈니스 로직을 중심으로 코드를 작성할 수 있는 것이다.</strong></p>