<p>동적계획법(DP)은 이전에 계산한 값을 저장하고, 이를 이용해 다음 값을 계산하는 알고리즘이다.</p>
<p>가장 익숙한 형태는 다음과 같다.</p>
<pre><code class="language-text">dp[i] = dp[i-1] + dp[i-2]</code></pre>
<p>이미 계산한 <code>dp[i-1]</code>, <code>dp[i-2]</code>를 사용하기 때문에 같은 값을 반복해서 계산하지 않는다.</p>
<p>하지만 DP라고 해서 항상 빠른 것은 아니다.</p>
<pre><code class="language-text">dp[i] = dp[0] + dp[1] + ... + dp[i-1]</code></pre>
<p>처럼 <strong>하나의 값을 구하기 위해 이전 값을 전부 확인해야 한다면</strong>, DP를 사용하더라도 전체 시간복잡도는 <code>O(N²)</code>이 된다.</p>
<p>이럴 때 이전 값들의 <strong>합 자체를 저장</strong>해둘 수 있다.</p>
<hr />
<h2 id="누적합을-활용한-dp">누적합을 활용한 DP</h2>
<p>예를 들어 매번</p>
<pre><code class="language-text">dp[0] + dp[1] + ... + dp[i]</code></pre>
<p>가 필요하다면 이를 매번 계산하지 않고</p>
<pre><code class="language-cpp">sum += dp[i];</code></pre>
<p>와 같이 지금까지의 합을 저장해둔다.</p>
<p>그러면</p>
<pre><code class="language-text">dp[0] + dp[1] + ... + dp[i]</code></pre>
<p>를 다시 순회할 필요 없이</p>
<pre><code class="language-cpp">sum</code></pre>
<p>만 확인하면 된다.</p>
<p>즉,</p>
<pre><code class="language-text">이전 값을 다시 전부 확인
O(N)</code></pre>
<p>하던 작업을</p>
<pre><code class="language-text">이미 저장한 누적값 사용
O(1)</code></pre>
<p>로 바꿀 수 있다.</p>
<p>전체적으로는</p>
<pre><code class="language-text">O(N²) → O(N)</code></pre>
<p>으로 줄어든다.</p>
<hr />
<h2 id="조건별로-누적하기">조건별로 누적하기</h2>
<p>모든 값을 합치는 것뿐만 아니라 <strong>특정 조건에 따라 나누어 누적</strong>할 수도 있다.</p>
<p>예를 들어 이전 DP 값을 <code>index % 3</code>에 따라 구분해야 한다면</p>
<pre><code class="language-cpp">ll sum[3] = {0, 0, 0};

sum[i % 3] += dp[i];</code></pre>
<p>처럼 저장할 수 있다.</p>
<p>그러면 결과적으로</p>
<pre><code class="language-text">sum[0] = dp[0] + dp[3] + dp[6] + ...
sum[1] = dp[1] + dp[4] + dp[7] + ...
sum[2] = dp[2] + dp[5] + dp[8] + ...</code></pre>
<p>가 된다.</p>
<p>나중에 현재 <code>i</code>와 나머지가 같은 이전 값들의 합이 필요하다면</p>
<pre><code class="language-cpp">sum[i % 3]</code></pre>
<p>하나로 가져올 수 있다.</p>
<p><strong>누적합은 단순히 전체 합만 저장하는 것이 아니라, 반복해서 필요한 정보의 형태에 맞게 묶어서 저장하는 방식으로 활용할 수 있다.</strong></p>
<hr />
<h2 id="적용-예시---아방가르드-타일링">적용 예시 - 아방가르드 타일링</h2>
<p>해당 문제에서는 <code>3 × n</code> 크기의 공간을 타일로 채운다.</p>
<p>작은 길이를 직접 확인하면</p>
<pre><code class="language-text">길이 1 → 1개
길이 2 → 3개
길이 3 → 10개</code></pre>
<p>이므로</p>
<pre><code class="language-cpp">tile[1] = 1;
tile[2] = 3;
tile[3] = 10;</code></pre>
<p>으로 시작할 수 있다.</p>
<p>현재 <code>i</code>를 만들 때 길이 1, 2, 3짜리 패턴은</p>
<pre><code class="language-cpp">tile[i-1]
+ tile[i-2] * 2
+ tile[i-3] * 5</code></pre>
<p>로 처리할 수 있다.</p>
<p>문제는 길이 4 이상부터 존재하는 고유패턴이다.</p>
<p>고유패턴의 수가</p>
<pre><code class="language-text">2, 2, 4,
2, 2, 4,
2, 2, 4 ...</code></pre>
<p>의 규칙을 가진다.</p>
<p>이를</p>
<pre><code class="language-text">2, 2, 4

=

2, 2, 2
+
0, 0, 2</code></pre>
<p>로 바라볼 수 있다.</p>
<p>즉,</p>
<pre><code class="language-text">모든 경우에 기본적으로 2개

+

3의 배수 길이에서는 추가로 2개</code></pre>
<p>이다.</p>
<p>여기서 누적합을 사용할 수 있다.</p>
<hr />
<h3 id="total">total</h3>
<p>길이 4 이상의 패턴과 결합할 수 있는 이전 <code>tile</code> 값들을 전부 누적한다.</p>
<pre><code class="language-cpp">int prev = i - 4;

total += tile[prev];</code></pre>
<p>그러면</p>
<pre><code class="language-cpp">total * 2</code></pre>
<p>만으로 길이 4 이상의 모든 패턴에 존재하는 <strong>기본 2개</strong>를 한 번에 처리할 수 있다.</p>
<hr />
<h3 id="sum">sum</h3>
<p><code>4</code>가 되는 경우에는 추가로 2개가 필요하다.</p>
<p>현재 길이가 <code>i</code>, 이전 길이가 <code>prev</code>라면 붙이는 패턴의 길이는</p>
<pre><code class="language-text">i - prev</code></pre>
<p>이다.</p>
<p>이 값이 3의 배수일 조건은</p>
<pre><code class="language-text">(i - prev) % 3 == 0

→ i % 3 == prev % 3</code></pre>
<p>이다.</p>
<p>따라서 이전 값을 나머지별로 미리 누적한다.</p>
<pre><code class="language-cpp">sum[prev % 3] += tile[prev];</code></pre>
<p>그리고 현재 <code>i</code>에서는</p>
<pre><code class="language-cpp">sum[i % 3]</code></pre>
<p>을 가져오면 된다.</p>
<p>결과적으로 길이 4 이상의 모든 경우는</p>
<pre><code class="language-cpp">ll extra = total * 2 + sum[i % 3] * 2;</code></pre>
<p>로 처리할 수 있다.</p>
<pre><code class="language-text">2 * total
→ 2, 2, 2, 2, 2 ...

2 * sum[i % 3]
→ 필요한 위치에 +2

결과
→ 2, 2, 4, 2, 2, 4 ...</code></pre>
<hr />
<h2 id="구현">구현</h2>
<pre><code class="language-cpp">#include &lt;string&gt;
#include &lt;vector&gt;
#define ll long long
#define mod 1000000007
using namespace std;

int solution(int n) {
    int answer = 0;

    vector&lt;ll&gt; tile(100001, 0);

    tile[0] = 1;
    tile[1] = 1;
    tile[2] = 3;
    tile[3] = 10;

    ll total = 0;
    ll sum[3] = {0, 0, 0};

    for(int i=4; i&lt;=n; i++){
        int prev = i - 4;

        total = (total + tile[prev]) % mod;
        sum[prev % 3] = (sum[prev % 3] + tile[prev]) % mod;

        ll extra = (
            total * 2
            + sum[i % 3] * 2
        ) % mod;

        tile[i] = (
            tile[i-1]
            + tile[i-2] * 2
            + tile[i-3] * 5
            + extra
        ) % mod;
    }

    answer = tile[n] % mod;

    return answer;
}</code></pre>
<hr />
<h1 id="정리">정리</h1>
<p>DP에서는</p>
<pre><code class="language-text">1. 현재 상태를 정의한다.
2. 이전 상태로부터 점화식을 만든다.
3. 계산한 값을 저장하여 재사용한다.</code></pre>
<p>가 기본이다.</p>
<p>여기에 한 단계 더 나아가,</p>
<pre><code class="language-text">현재 값을 구할 때 이전 DP를 계속 순회하고 있는가?</code></pre>
<p>를 확인할 필요가 있다.</p>
<p>반복해서 필요한 값이 이전 DP들의 합이라면</p>
<pre><code class="language-text">누적합</code></pre>
<p>을 저장하고,</p>
<p>특정 조건의 값들만 필요하다면</p>
<pre><code class="language-text">조건별 누적합</code></pre>
<p>을 저장할 수 있다.</p>
<p>이번 문제에서는</p>
<pre><code class="language-text">2, 2, 4</code></pre>
<p>라는 반복 구조를</p>
<pre><code class="language-text">기본 2 + 조건부 추가 2</code></pre>
<p>로 분해했고,</p>
<pre><code class="language-cpp">total
sum[3]</code></pre>
<p>에 필요한 정보를 미리 누적하여 매번 이전 값을 전부 확인하는 과정을 제거했다.</p>
<p>결국 중요한 것은 단순히 DP 값을 저장하는 것에서 끝나는 것이 아니라,</p>
<blockquote>
<p><strong>DP의 상태 전이 과정에서도 반복되는 계산이 있다면, 그 계산 결과 역시 저장할 수 있는지 확인하는 것이다.</strong></p>
</blockquote>