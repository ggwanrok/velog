<p>어떤 문제의 모든 경우를 직접 확인하는 가장 단순한 방법은 완전 탐색이다.</p>
<p>하지만 같은 계산이 반복되고, 이전에 구한 결과를 이용해서 다음 결과를 만들 수 있다면 굳이 매번 처음부터 다시 계산할 필요는 없다.</p>
<p>이때 사용할 수 있는 대표적인 방법이 <strong>동적 계획법(Dynamic Programming, DP)</strong> 이다.</p>
<hr />
<h2 id="동적-계획법">동적 계획법</h2>
<p>DP 문제의 풀이 과정은 생각보다 명료하다.</p>
<pre><code class="language-text">1. 값을 특정한다.        → 상태 정의
2. 이전 값으로부터
   다음 값을 구하는
   규칙을 만든다.        → 점화식
3. 필요한 상태를
   순서대로 계산한다.    → 답 도출</code></pre>
<p>결국 핵심은</p>
<blockquote>
<p><strong>현재 답을 이전에 구해놓은 답으로 표현할 수 있는가?</strong></p>
</blockquote>
<p>이다.</p>
<p>예를 들어 어떤 위치까지 이동했을 때의 최댓값을 구한다고 해보자.</p>
<pre><code class="language-text">dp[i] = i번째 위치까지 왔을 때 얻을 수 있는 최대값</code></pre>
<p>처럼 하나의 값을 정해둘 수 있다.</p>
<p>그리고 현재 위치의 값이 이전 위치의 결과를 이용해서</p>
<pre><code class="language-text">dp[i] = max(dp[i - 1], ...) + 현재값</code></pre>
<p>처럼 계산될 수 있다면,</p>
<p>앞에서 계산한 결과를 저장해두고 다음 계산에 그대로 사용할 수 있다.</p>
<p>이처럼 DP에서는 <strong>각 단계에서 무엇을 저장할 것인지 정하는 것</strong>이 가장 중요하다.</p>
<hr />
<h2 id="dp-문제를-알아보는-힌트">DP 문제를 알아보는 힌트</h2>
<p>문제에서 다음과 같은 형태가 보인다면 DP를 한 번 의심해볼 수 있다.</p>
<pre><code class="language-text">최댓값 / 최솟값을 구하라
경우의 수를 구하라
가능한 방법의 수를 구하라
몇 번째까지 도달하는 최적의 값을 구하라
이전 단계의 선택이 다음 단계에 영향을 준다
같은 부분 문제를 여러 번 계산하게 된다</code></pre>
<p>특히</p>
<pre><code class="language-text">현재 상태
    ↓
몇 개의 이전 상태만 확인
    ↓
현재 상태의 최적값 결정</code></pre>
<p>과 같은 구조를 만들 수 있다면 DP로 풀이할 가능성이 높다.</p>
<p>물론 <code>최댓값</code>, <code>최솟값</code>이라는 말이 나온다고 무조건 DP인 것은 아니다.</p>
<p>중요한 것은 <strong>현재 문제를 더 작은 문제의 결과를 이용해서 표현할 수 있는지</strong>이다.</p>
<blockquote>
<p>개인적으로 <strong>몇 개의 이전 상태만 확인</strong>에 대한 직관을 키우는 것이 DP 풀이 실력의 핵심이라고 생각한다.
(복잡해보이는 과정 속에서도, 일관되게 지켜지는 규칙을 찾아내는 힘)</p>
</blockquote>
<hr />
<h2 id="점화식">점화식</h2>
<p>DP에서 가장 중요한 것은 점화식이다.</p>
<p>점화식은 단순히 수학 공식을 만드는 것이 아니라,</p>
<blockquote>
<p><strong>현재 상태의 값을 이전 상태들의 값으로 표현하는 규칙</strong></p>
</blockquote>
<p>이라고 생각하면 된다.</p>
<p>예를 들어</p>
<pre><code class="language-text">현재 위치까지의 최대값
=
이전 위치까지의 최대값
+
현재 값</code></pre>
<p>처럼 표현할 수 있다면 이를 코드로 반복하면서 전체 문제의 답을 구할 수 있다.</p>
<p>즉 DP는</p>
<pre><code class="language-text">작은 문제의 답을 구한다.
        ↓
저장한다.
        ↓
저장된 답을 이용해 더 큰 문제의 답을 구한다.
        ↓
반복한다.</code></pre>
<p>의 구조이다.</p>
<hr />
<h2 id="적용-예시---정수-삼각형">적용 예시 - 정수 삼각형</h2>
<p>프로그래머스의 <a href="https://school.programmers.co.kr/learn/courses/30/lessons/43105">정수 삼각형</a> 문제를 보자.</p>
<p>삼각형의 꼭대기에서 아래로 내려가면서 지나간 숫자의 합 중 가장 큰 값을 구해야 한다.</p>
<p>예를 들어 다음과 같은 삼각형이 있다.</p>
<pre><code class="language-text">        7
      3   8
    8   1   0
  2   7   4   4
4   5   2   6   5</code></pre>
<p>각 위치에 도착할 수 있는 경로를 전부 탐색할 수도 있다.</p>
<p>하지만 각 위치에서 중요한 것은</p>
<blockquote>
<p><strong>이 위치까지 왔을 때 만들 수 있는 최대 합</strong></p>
</blockquote>
<p>하나뿐이다.</p>
<p>따라서 삼각형 자체를 DP 배열처럼 사용할 수 있다.</p>
<pre><code class="language-text">triangle[i][j]
=
(i, j) 위치까지 내려왔을 때 얻을 수 있는 최대 합</code></pre>
<p>이라고 상태를 정의한다.</p>
<hr />
<h3 id="점화식-만들기">점화식 만들기</h3>
<p>현재 위치 <code>(i, j)</code>로 올 수 있는 위치는 바로 위의 두 곳뿐이다.</p>
<pre><code class="language-text">        왼쪽 위      오른쪽 위
             ↘      ↙
             현재 위치</code></pre>
<p>따라서 가운데에 있는 값은</p>
<pre><code class="language-text">triangle[i][j]
=
현재 값
+
max(
    triangle[i-1][j-1],
    triangle[i-1][j]
)</code></pre>
<p>으로 계산할 수 있다.</p>
<p>즉,</p>
<pre><code class="language-text">이 위치까지의 최대합
=
이전 단계에서 올 수 있는 최대합
+
현재 값</code></pre>
<p>이라는 점화식이 만들어진다.</p>
<p>다만 삼각형의 가장 왼쪽과 오른쪽은 올 수 있는 경로가 하나밖에 없다.</p>
<pre><code class="language-text">가장 왼쪽
triangle[i][0]
=
triangle[i][0] + triangle[i-1][0]</code></pre>
<pre><code class="language-text">가장 오른쪽
triangle[i][j]
=
triangle[i][j] + triangle[i-1][j-1]</code></pre>
<p>이렇게 위에서부터 한 줄씩 계산하면 마지막 줄에는</p>
<pre><code class="language-text">각 위치까지 내려왔을 때 얻을 수 있는 최대 합</code></pre>
<p>이 저장된다.</p>
<p>따라서 마지막 줄의 최댓값이 정답이다.</p>
<hr />
<h3 id="코드">코드</h3>
<pre><code class="language-cpp">#include &lt;string&gt;
#include &lt;vector&gt;
#include &lt;algorithm&gt;
using namespace std;

int solution(vector&lt;vector&lt;int&gt;&gt; triangle) {
    int answer = 0;

    for(int i = 1; i &lt; triangle.size(); i++){
        for(int j = 0; j &lt; triangle[i].size(); j++){
            int cur_val = triangle[i][j];

            if(j == 0){
                cur_val += triangle[i-1][j];
            }
            else if(j &gt;= triangle[i].size() - 1){
                cur_val += triangle[i-1][j-1];
            }
            else{
                cur_val += max(
                    triangle[i-1][j-1],
                    triangle[i-1][j]
                );
            }

            triangle[i][j] = max(triangle[i][j], cur_val);
        }
    }

    for(int i = 0; i &lt; triangle[triangle.size()-1].size(); i++){
        answer = max(
            answer,
            triangle[triangle.size()-1][i]
        );
    }

    return answer;
}</code></pre>
<p>이 코드에서 중요한 것은 구현보다 <strong>무엇을 DP 값으로 설정했는가</strong>이다.</p>
<p>각 숫자를 단순한 삼각형의 원소로 보는 것이 아니라,</p>
<pre><code class="language-text">triangle[i][j]
=
해당 위치까지 도달했을 때의 최대 누적합</code></pre>
<p>으로 의미를 바꿨다.</p>
<p>그러면 현재 위치의 값은 바로 위의 결과만으로 결정할 수 있다.</p>
<pre><code class="language-text">이전 결과
   ↓
현재 결과 계산
   ↓
저장
   ↓
다음 계산에서 재사용</code></pre>
<p>이것이 DP의 핵심적인 흐름이다.</p>