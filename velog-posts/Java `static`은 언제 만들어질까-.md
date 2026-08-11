<p>Java에서 <code>static</code>을 설명할 때 가장 많이 듣는 말은 아마 이것일 것이다.</p>
<blockquote>
<p><code>static</code>은 객체를 생성하지 않아도 사용할 수 있고, 모든 객체가 공유한다.</p>
</blockquote>
<p>사용법을 설명하기에는 충분하다. 하지만 한 가지 의문이 남는다.</p>
<p>객체가 만들어지지도 않았는데 <code>static</code>은 <strong>언제 만들어진 걸까?</strong></p>
<pre><code class="language-java">class Counter {
    static int total = 0;
    int count = 0;
}

public class Main {
    public static void main(String[] args) {
        System.out.println(Counter.total);

        Counter c1 = new Counter();
        Counter c2 = new Counter();
    }
}</code></pre>
<p><code>c1</code>, <code>c2</code>가 만들어지기 전에도 <code>Counter.total</code>에는 접근할 수 있다.</p>
<p>반면 <code>count</code>는 반드시 객체가 있어야 한다.</p>
<pre><code class="language-java">c1.count;
c2.count;</code></pre>
<p>이 차이는 단순히 <code>static은 공유된다</code>는 특징에서 생기는 것이 아니다.</p>
<p><strong>static과 instance는 애초에 생성되는 기준과 시점이 다르다.</strong></p>
<hr />
<h2 id="객체의-생성과-클래스의-초기화">객체의 생성과 클래스의 초기화</h2>
<p>일반 필드는 객체의 일부다.</p>
<pre><code class="language-java">class Counter {
    int count = 10;
}</code></pre>
<p>따라서 <code>count</code>는 <code>Counter</code>라는 클래스가 존재한다는 이유만으로 개별 값이 만들어지지 않는다.</p>
<pre><code class="language-java">Counter c1 = new Counter();
Counter c2 = new Counter();</code></pre>
<p><code>new Counter()</code>가 실행될 때마다 새로운 객체가 생성되고, 각 객체에 <code>count</code>가 존재한다.</p>
<pre><code class="language-text">Heap

Counter Object A
┌────────────┐
│ count = 10 │
└────────────┘

Counter Object B
┌────────────┐
│ count = 10 │
└────────────┘</code></pre>
<p>인스턴스 변수의 초기화는 인스턴스가 생성될 때마다 수행된다.</p>
<p><code>static</code>은 다르다.</p>
<pre><code class="language-java">class Counter {
    static int total = 10;
}</code></pre>
<p><code>total</code>은 <code>Counter</code> 인스턴스에 속하지 않는다.</p>
<p><strong>Counter라는 클래스 자체에 속하는 class variable</strong>이다.</p>
<p>그래서 객체를 열 개 만들더라도 <code>total</code>이 열 개 만들어지는 것이 아니다.</p>
<pre><code class="language-text">Counter Class
└── static total

     ↑      ↑
     │      │
Object A  Object B</code></pre>
<p>그렇다면 실제 생성 시점을 확인해보자.</p>
<hr />
<h2 id="static-초기화">static 초기화</h2>
<p>JVM이 클래스를 실행 가능한 상태로 만드는 과정은 크게 다음과 같이 진행된다.</p>
<pre><code class="language-text">Loading
   ↓
Linking
   ├─ Verification
   ├─ Preparation
   └─ Resolution
   ↓
Initialization</code></pre>
<p><code>static</code>을 이해할 때 중요한 것은 <strong>Preparation과 Initialization을 구분하는 것</strong>이다.</p>
<p>다음 코드가 있다고 하자.</p>
<pre><code class="language-java">class Counter {
    static int total = 100;
}</code></pre>
<p>Preparation 단계에서는 static field를 위한 공간이 준비되고 우선 기본값이 설정된다. 명시적으로 작성한 초기화 코드는 아직 실행되지 않는다. </p>
<pre><code class="language-text">Preparation

total = 0</code></pre>
<p>이후 클래스 Initialization이 진행되면서 작성해둔 static 초기화 코드가 실행된다. </p>
<pre><code class="language-text">Initialization

total = 100</code></pre>
<p>따라서 개념적으로는 다음 순서다.</p>
<pre><code class="language-text">Counter 클래스 사용
        ↓
Loading
        ↓
Preparation
static total = 0
        ↓
Initialization
static total = 100
        ↓
사용 가능</code></pre>
<p>이 흐름을 알고 나면 <code>static</code>이 객체 없이 존재할 수 있는 이유가 명확해진다.</p>
<p><strong>객체의 생성보다 클래스 자체의 준비와 초기화가 먼저 존재하기 때문이다.</strong></p>
<hr />
<h3 id="예제로-이해하기">예제로 이해하기</h3>
<p>초기화 시점을 출력해보자.</p>
<pre><code class="language-java">class Counter {

    static int total = initStatic();

    int count = initInstance();

    static int initStatic() {
        System.out.println(&quot;static 초기화&quot;);
        return 100;
    }

    int initInstance() {
        System.out.println(&quot;instance 초기화&quot;);
        return 10;
    }
}</code></pre>
<p>그리고 객체를 두 개 만든다.</p>
<pre><code class="language-java">public class Main {

    public static void main(String[] args) {

        System.out.println(&quot;start&quot;);

        Counter c1 = new Counter();
        Counter c2 = new Counter();
    }
}</code></pre>
<p>실행 흐름은 다음과 같다.</p>
<pre><code class="language-text">start

static 초기화

instance 초기화
instance 초기화</code></pre>
<p><code>static</code> 초기화는 클래스 초기화 과정에서 한 번 실행된다.</p>
<p>반면 instance 초기화는 객체를 생성할 때마다 실행된다. 클래스의 static initializer와 static field initializer는 클래스 초기화 과정에서 수행되고, instance field initializer는 인스턴스 생성마다 수행된다.</p>
<p>이 한 번의 차이가 <code>static</code>의 대부분의 특징을 만든다.</p>
<pre><code class="language-text">Class
 └── static   → 클래스 단위

new
 ├── Object A → instance
 ├── Object B → instance
 └── Object C → instance</code></pre>
<hr />
<h2 id="초기화-시점">초기화 시점</h2>
<p>여기서 흔히 하는 오해가 하나 있다.</p>
<pre><code class="language-text">프로그램 실행
=
모든 static 즉시 초기화</code></pre>
<p>는 아니다.</p>
<p>클래스 초기화는 해당 클래스가 처음 <strong>적극적으로 사용(active use)</strong> 될 때 발생한다.</p>
<p>대표적으로 객체를 생성하거나, static 메서드를 호출하거나, non-constant static field를 읽거나 쓰는 경우가 이에 해당한다. JVM 수준에서는 <code>new</code>, <code>getstatic</code>, <code>putstatic</code>, <code>invokestatic</code> 등의 실행이 클래스 초기화를 유발할 수 있다. </p>
<pre><code class="language-java">class A {
    static {
        System.out.println(&quot;A 초기화&quot;);
    }
}</code></pre>
<p><code>A</code>가 프로그램에 존재한다고 해서 반드시 프로그램 시작 즉시 위 코드가 실행되는 것은 아니다.</p>
<pre><code class="language-java">new A();</code></pre>
<p>처럼 실제 사용이 발생하면 클래스 초기화가 필요해진다.</p>
<p>그래서 <code>static</code>을</p>
<blockquote>
<p>프로그램 시작부터 끝까지 존재하는 변수</p>
</blockquote>
<p>라고 외우는 것보다는</p>
<blockquote>
<p><strong>클래스의 생명주기에 귀속된 변수</strong></p>
</blockquote>
<p>라고 이해하는 편이 정확하다.</p>
<hr />
<h1 id="static을-이해하는-기준">static을 이해하는 기준</h1>
<p><code>static</code>과 일반 필드의 차이는 결국 다음 흐름으로 정리된다.</p>
<pre><code class="language-text">           Class
             │
     Loading / Linking
             │
       Preparation
             │
     static 기본값 준비
             │
      Initialization
             │
    static 초기화 수행
             │
       ┌─────┴─────┐
       │           │
   new Object   new Object
       │           │
   instance     instance</code></pre>
<p><code>static</code>은 <strong>클래스를 기준으로 한 번 준비되고 초기화된다.</strong></p>
<p>일반 필드는 <strong>객체를 기준으로 객체가 생성될 때마다 만들어지고 초기화된다.</strong></p>
<p><strong>처음부터 객체가 아니라 클래스에 귀속되어 있기 때문에 나타나는 결과다.</strong></p>
<p>결국 Java에서 <code>static</code>을 판단하는 가장 좋은 기준은</p>
<blockquote>
<p>객체 없이 호출할 수 있는가?</p>
</blockquote>
<p>보다</p>
<blockquote>
<p><strong>이 상태와 동작의 주인은 객체인가, 클래스인가?</strong></p>
</blockquote>
<p>에 가깝다.</p>