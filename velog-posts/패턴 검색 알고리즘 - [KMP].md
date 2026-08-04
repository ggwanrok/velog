<p>텍스트에서 특정 패턴이 등장하는 위치를 찾는 가장 단순한 방법은 텍스트의 모든 위치에서 패턴을 하나씩 비교하는 것이다.</p>
<p>예를 들어 다음 텍스트에서 <code>ABABC</code>라는 패턴을 찾는다고 해보자.</p>
<pre><code class="language-text">텍스트:     ABABABABC
패턴:       ABABC</code></pre>
<p>텍스트의 첫 번째 위치부터 비교하면 다음과 같이 진행된다.</p>
<pre><code class="language-text">텍스트:     A B A B A B A B C
패턴:       A B A B C</code></pre>
<p>패턴의 앞부분인 <code>ABAB</code>까지는 일치하지만, 마지막 문자에서 비교가 실패한다.</p>
<pre><code class="language-text">텍스트:     A B A B A
패턴:       A B A B C
                ↑
              불일치</code></pre>
<p>단순 탐색은 비교에 실패하면 패턴을 한 칸 옮긴 뒤, 패턴의 첫 번째 문자부터 다시 비교한다.</p>
<p>하지만 우리는 이미 텍스트와 패턴의 <code>ABAB</code> 부분이 일치했다는 사실을 알고 있다.</p>
<p>KMP 알고리즘은 이 정보를 버리지 않는다.</p>
<blockquote>
<p>지금까지 일치한 패턴의 구조를 이용해, 다시 확인할 필요가 없는 비교를 건너뛴다.</p>
</blockquote>
<hr />
<h2 id="단순-탐색의-문제">단순 탐색의 문제</h2>
<p>텍스트의 길이를 <code>N</code>, 패턴의 길이를 <code>M</code>이라고 하자.</p>
<p>단순 탐색은 텍스트의 각 위치를 패턴의 시작 위치로 가정하고 비교한다.</p>
<pre><code class="language-text">텍스트의 0번 위치부터 최대 M번 비교
텍스트의 1번 위치부터 최대 M번 비교
텍스트의 2번 위치부터 최대 M번 비교
...</code></pre>
<p>최악의 경우 텍스트의 각 위치에서 패턴 전체를 비교하게 된다.</p>
<p>따라서 시간 복잡도는 다음과 같다.</p>
<pre><code class="language-text">O(N × M)</code></pre>
<p>특히 같은 문자가 반복되는 텍스트와 패턴에서는 불필요한 비교가 많이 발생한다.</p>
<pre><code class="language-text">텍스트: AAAAAAAAAAB
패턴:   AAAAAB</code></pre>
<p>패턴의 대부분은 계속 일치하지만, 마지막 부분에서 비교가 실패한다.</p>
<pre><code class="language-text">텍스트: A A A A A A
패턴:   A A A A A B
                  ↑
                불일치</code></pre>
<p>단순 탐색은 패턴을 한 칸 이동한 뒤 다시 첫 번째 <code>A</code>부터 비교한다.</p>
<pre><code class="language-text">텍스트: A A A A A A A A A A B
패턴:   A A A A A B
          A A A A A B
            A A A A A B</code></pre>
<p>이미 여러 번 확인한 텍스트의 <code>A</code>를 반복해서 비교하는 것이다.</p>
<p>KMP는 이전에 일치했던 정보를 이용해 이러한 중복 비교를 줄인다.</p>
<hr />
<h2 id="kmp의-핵심-로직">KMP의 핵심 로직</h2>
<p>KMP는 비교에 실패했을 때 패턴을 무조건 한 칸만 이동하지 않는다.</p>
<p>대신 지금까지 일치했던 <strong>부분 패턴</strong>의 구조를 확인한다.</p>
<p>이때 사용하는 개념이 접두사와 접미사다.</p>
<pre><code class="language-text">접두사: 패턴의 앞에서 시작하는 부분
접미사: 패턴의 끝에서 끝나는 부분</code></pre>
<p>예를 들어 패턴의 앞부분인 <code>ABAB</code>까지 텍스트와 일치했다고 하자.</p>
<pre><code class="language-text">ABAB</code></pre>
<p><code>ABAB</code>의 접두사와 접미사는 다음과 같다.</p>
<pre><code class="language-text">접두사: A, AB, ABA
접미사: B, AB, BAB</code></pre>
<p>접두사와 접미사에 공통으로 포함된 가장 긴 값은 <code>AB</code>이다.</p>
<pre><code class="language-text">ABAB
^^    접두사

ABAB
  ^^  접미사</code></pre>
<p>즉, 지금까지 일치한 부분 패턴의 마지막 <code>AB</code>는 패턴의 시작 부분인 <code>AB</code>와 같다.</p>
<p>이 정보를 이용하면 패턴을 처음부터 다시 비교할 필요가 없다.</p>
<pre><code class="language-text">지금까지 일치한 부분:     A B A B
                         └─ A B

패턴의 앞부분:           A B</code></pre>
<p>텍스트의 뒤쪽 <code>AB</code>가 패턴의 앞쪽 <code>AB</code>와 같다는 것을 이미 알고 있기 때문이다.</p>
<p>따라서 해당 두 문자는 다시 비교하지 않고, 그다음 위치부터 비교를 이어갈 수 있다.</p>
<hr />
<h2 id="접두사--접미사">접두사 &amp; 접미사</h2>
<p>KMP를 이해하려면 패턴 내부의 접두사와 접미사가 무엇인지 알아야 한다.</p>
<p>패턴이 다음과 같다고 하자.</p>
<pre><code class="language-text">ABABA</code></pre>
<h3 id="접두사">접두사</h3>
<p>접두사는 패턴의 첫 번째 문자부터 시작하는 부분 패턴이다.</p>
<pre><code class="language-text">A
AB
ABA
ABAB</code></pre>
<h3 id="접미사">접미사</h3>
<p>접미사는 패턴의 마지막 문자를 포함하는 부분 패턴이다.</p>
<pre><code class="language-text">A
BA
ABA
BABA</code></pre>
<p>접두사와 접미사를 구할 때는 패턴 전체를 포함하지 않는다.</p>
<p>패턴 전체까지 포함하면 모든 패턴이 항상 자기 자신과 일치하므로, 탐색에 활용할 수 있는 정보가 되지 않기 때문이다.</p>
<p><code>ABABA</code>의 접두사와 접미사 중 서로 같은 값은 다음과 같다.</p>
<pre><code class="language-text">A
ABA</code></pre>
<p>이 중 가장 긴 값은 <code>ABA</code>이다.</p>
<pre><code class="language-text">ABABA
^^^    접두사

ABABA
  ^^^  접미사</code></pre>
<p>따라서 <code>ABABA</code>에서 가장 긴 공통 접두사와 접미사의 길이는 <code>3</code>이다.</p>
<hr />
<h2 id="실패-함수와-pi-배열">실패 함수와 <code>pi</code> 배열</h2>
<p>KMP는 패턴의 각 위치까지 확인했을 때, 가장 긴 공통 접두사와 접미사의 길이를 미리 계산한다.</p>
<p>이 정보를 저장한 배열을 일반적으로 다음과 같이 부른다.</p>
<pre><code class="language-text">실패 함수
부분 일치 테이블
pi 배열</code></pre>
<p>예를 들어 패턴이 다음과 같다고 하자.</p>
<pre><code class="language-text">ABABACA</code></pre>
<p>패턴을 앞에서부터 한 문자씩 늘리면서 접두사와 접미사를 확인한다.</p>
<table>
<thead>
<tr>
<th align="right">인덱스</th>
<th>현재까지 확인한 부분 패턴</th>
<th>가장 긴 공통 접두사·접미사</th>
<th align="right">길이</th>
</tr>
</thead>
<tbody><tr>
<td align="right">0</td>
<td><code>A</code></td>
<td>없음</td>
<td align="right">0</td>
</tr>
<tr>
<td align="right">1</td>
<td><code>AB</code></td>
<td>없음</td>
<td align="right">0</td>
</tr>
<tr>
<td align="right">2</td>
<td><code>ABA</code></td>
<td><code>A</code></td>
<td align="right">1</td>
</tr>
<tr>
<td align="right">3</td>
<td><code>ABAB</code></td>
<td><code>AB</code></td>
<td align="right">2</td>
</tr>
<tr>
<td align="right">4</td>
<td><code>ABABA</code></td>
<td><code>ABA</code></td>
<td align="right">3</td>
</tr>
<tr>
<td align="right">5</td>
<td><code>ABABAC</code></td>
<td>없음</td>
<td align="right">0</td>
</tr>
<tr>
<td align="right">6</td>
<td><code>ABABACA</code></td>
<td><code>A</code></td>
<td align="right">1</td>
</tr>
</tbody></table>
<p>따라서 <code>pi</code> 배열은 다음과 같다.</p>
<pre><code class="language-text">패턴:   A B A B A C A
인덱스: 0 1 2 3 4 5 6
pi:    0 0 1 2 3 0 1</code></pre>
<p>예를 들어 다음 값은,</p>
<pre><code class="language-text">pi[4] = 3</code></pre>
<p>패턴의 <code>0번</code>부터 <code>4번</code>까지인 <code>ABABA</code>에서 가장 긴 공통 접두사와 접미사의 길이가 <code>3</code>이라는 뜻이다.</p>
<pre><code class="language-text">ABABA
^^^    접두사 ABA

ABABA
  ^^^  접미사 ABA</code></pre>
<p>즉, <code>pi</code> 배열은 패턴 내부에 어떤 반복 구조가 존재하는지를 나타낸다.</p>
<hr />
<h2 id="pi-배열은-무엇을-알려주는가"><code>pi</code> 배열은 무엇을 알려주는가</h2>
<p><code>pi</code> 배열은 단순히 접두사와 접미사의 길이만 저장하는 배열이 아니다.</p>
<p>텍스트와 패턴의 비교가 실패했을 때, <strong>패턴의 어느 위치부터 비교를 이어갈 수 있는지</strong>를 알려준다.</p>
<p>예를 들어 패턴의 앞 다섯 문자인 <code>ABABA</code>까지 텍스트와 일치했다고 하자.</p>
<pre><code class="language-text">ABABA</code></pre>
<p>그다음 문자에서 비교가 실패했다.</p>
<p>단순 탐색이라면 지금까지 일치한 다섯 문자를 모두 버리고, 패턴을 옮긴 뒤 첫 번째 문자부터 다시 비교한다.</p>
<p>하지만 <code>ABABA</code>에는 다음과 같은 구조가 있다.</p>
<pre><code class="language-text">ABABA
^^^    앞쪽 ABA

ABABA
  ^^^  뒤쪽 ABA</code></pre>
<p>앞쪽 <code>ABA</code>와 뒤쪽 <code>ABA</code>가 같다.</p>
<p>텍스트와 패턴의 <code>ABABA</code>가 일치했다면, 텍스트에 있는 마지막 <code>ABA</code>는 패턴의 시작 부분 <code>ABA</code>와도 같다고 볼 수 있다.</p>
<pre><code class="language-text">텍스트에서 일치한 부분:     A B A B A
                            A B A
                            └──── 패턴의 앞쪽 ABA와 같음</code></pre>
<p>따라서 패턴의 첫 번째 문자부터 다시 비교하지 않아도 된다.</p>
<p>이미 <code>ABA</code>가 일치한 상태라고 보고, 그다음 위치부터 비교를 이어갈 수 있다.</p>
<blockquote>
<p><strong>pi 배열의 값을 통해 뒤로 돌아가 탐색을 이어갈 인덱스를 특정할 수 있게 된다.</strong></p>
</blockquote>
<hr />
<h2 id="kmp-탐색의-흐름">KMP 탐색의 흐름</h2>
<p>다음 텍스트에서 <code>ABABC</code>라는 패턴을 찾는 과정을 살펴보자.</p>
<pre><code class="language-text">텍스트:     A B A B A B A B C
패턴:       A B A B C</code></pre>
<p>텍스트와 패턴을 왼쪽부터 비교한다.</p>
<pre><code class="language-text">텍스트:     A B A B A
패턴:       A B A B C</code></pre>
<p>패턴의 앞부분인 <code>ABAB</code>까지 일치하지만 마지막 문자에서 실패한다.</p>
<pre><code class="language-text">텍스트:     A B A B A
패턴:       A B A B C
                ↑
              불일치</code></pre>
<p>지금까지 일치한 부분 패턴은 <code>ABAB</code>이다.</p>
<p><code>ABAB</code>의 가장 긴 공통 접두사와 접미사는 <code>AB</code>이다.</p>
<pre><code class="language-text">ABAB
^^    접두사 AB

ABAB
  ^^  접미사 AB</code></pre>
<p>따라서 패턴의 앞쪽 <code>AB</code>를 텍스트에서 이미 일치한 뒤쪽 <code>AB</code> 위치에 맞춘다.</p>
<pre><code class="language-text">텍스트:     A B A B A B A B C
패턴:           A B A B C</code></pre>
<p>이때 패턴의 앞쪽 <code>AB</code>는 다시 비교할 필요가 없다.</p>
<p>텍스트의 해당 위치가 패턴의 앞쪽 <code>AB</code>와 같다는 사실을 이미 알고 있기 때문이다.</p>
<pre><code class="language-text">텍스트:     A B A B A B A B C
패턴:           A B A B C
                    ↑
              이 위치부터 비교</code></pre>
<p>비교를 계속 진행하면 패턴 전체가 텍스트와 일치한다.</p>
<pre><code class="language-text">텍스트:     A B A B A B A B C
패턴:             A B A B C</code></pre>
<p>따라서 패턴은 텍스트의 인덱스 <code>4</code>부터 등장한다.</p>
<hr />
<h2 id="구현되는-방식">구현되는 방식</h2>
<p>KMP에서는 두 개의 위치를 사용해 텍스트와 패턴을 비교한다.</p>
<pre><code class="language-text">i: 텍스트에서 현재 확인하고 있는 위치
j: 패턴에서 현재 확인하고 있는 위치</code></pre>
<p>예를 들어 다음 텍스트에서 <code>ABABC</code>라는 패턴을 찾는다고 하자.</p>
<pre><code class="language-text">텍스트:     A B A B A B A B C
인덱스:     0 1 2 3 4 5 6 7 8

패턴:       A B A B C
인덱스:     0 1 2 3 4</code></pre>
<p>처음에는 텍스트와 패턴의 첫 번째 문자를 비교한다.</p>
<pre><code class="language-text">i = 0
j = 0

텍스트:     A B A B A B A B C
        ↑
패턴:       A B A B C
        ↑</code></pre>
<p><code>text[0]</code>과 <code>pattern[0]</code>이 모두 <code>A</code>이므로 일치한다.</p>
<p>따라서 <code>i</code>와 <code>j</code>를 함께 다음 위치로 이동한다.</p>
<pre><code class="language-text">i = 1
j = 1</code></pre>
<p>이후에도 문자가 계속 일치한다.</p>
<pre><code class="language-text">text[1] == pattern[1]  → B == B
text[2] == pattern[2]  → A == A
text[3] == pattern[3]  → B == B</code></pre>
<p>따라서 현재 위치는 다음과 같다.</p>
<pre><code class="language-text">i = 4
j = 4

텍스트:     A B A B A B A B C
                ↑
패턴:       A B A B C
                ↑</code></pre>
<p>현재 비교하는 문자는 다음과 같다.</p>
<pre><code class="language-text">text[4]    = A
pattern[4] = C</code></pre>
<p>두 문자가 다르므로 비교에 실패한다.</p>
<hr />
<p>텍스트 위치 <code>i</code>는 그대로 둔다.</p>
<pre><code class="language-text">i = 4 유지</code></pre>
<p>대신 패턴 위치 <code>j</code>만 <code>pi</code> 배열을 이용해 변경한다.</p>
<p>현재까지 일치한 부분 패턴은 <code>ABAB</code>이다.</p>
<pre><code class="language-text">패턴:  A B A B C
      └─────┘
       ABAB 일치</code></pre>
<p><code>ABAB</code>의 가장 긴 공통 접두사와 접미사는 <code>AB</code>이다.</p>
<pre><code class="language-text">ABAB
^^    접두사 AB

ABAB
  ^^  접미사 AB</code></pre>
<p>따라서 앞의 <code>AB</code> 두 문자는 이미 일치한 것으로 재사용할 수 있다.</p>
<p>패턴 위치 <code>j</code>는 <code>4</code>에서 <code>2</code>로 이동한다.</p>
<pre><code class="language-text">j = pi[3]
j = 2</code></pre>
<p>하지만 텍스트 위치 <code>i</code>는 여전히 <code>4</code>다.</p>
<pre><code class="language-text">i = 4
j = 2

텍스트:     A B A B A B A B C
                ↑ i

패턴:           A B A B C
                ↑ j</code></pre>
<p>이제 같은 텍스트 문자 <code>text[4]</code>를 패턴의 새로운 위치 <code>pattern[2]</code>와 비교한다.</p>
<pre><code class="language-text">text[4]    = A
pattern[2] = A</code></pre>
<p>두 문자가 일치한다.</p>
<p>따라서 다음 위치로 이동한다.</p>
<pre><code class="language-text">i = 5
j = 3</code></pre>
<p>비교를 계속 진행한다.</p>
<pre><code class="language-text">text[5]    = B
pattern[3] = B</code></pre>
<p>다시 일치하므로 이동한다.</p>
<pre><code class="language-text">i = 6
j = 4</code></pre>
<p>다음 비교는 다음과 같다.</p>
<pre><code class="language-text">text[6]    = A
pattern[4] = C</code></pre>
<p>또다시 일치하지 않는다.</p>
<p>이번에도 텍스트 위치 <code>i = 6</code>은 그대로 두고, 패턴 위치 <code>j</code>만 이동한다.</p>
<pre><code class="language-text">j = pi[3]
j = 2</code></pre>
<p>그다음 같은 텍스트 문자와 다시 비교한다.</p>
<pre><code class="language-text">text[6]    = A
pattern[2] = A</code></pre>
<p>이처럼 KMP는 비교에 실패할 때 텍스트 위치를 뒤로 돌리지 않는다.</p>
<pre><code class="language-text">불일치 발생

텍스트 위치 i
→ 현재 위치 유지

패턴 위치 j
→ pi 배열을 이용해 이전 후보로 이동</code></pre>
<p>즉, KMP에서 <code>i</code>는 텍스트를 처음부터 끝까지 한 방향으로 탐색한다.</p>
<p><code>j</code>는 문자가 일치하면 앞으로 이동하고, 불일치하면 <code>pi</code> 배열을 따라 이전 위치로 이동한다.</p>
<pre><code class="language-text">i: 텍스트를 읽으며 계속 앞으로 이동
j: 패턴 안에서 앞으로 가거나 이전 후보로 이동</code></pre>
<p>이 구조 덕분에 KMP는 비교에 실패해도 텍스트의 이전 위치로 돌아가 같은 문자를 처음부터 반복해서 확인하지 않는다.</p>
<hr />
<h2 id="시간-복잡도">시간 복잡도</h2>
<p>텍스트의 길이를 <code>N</code>, 패턴의 길이를 <code>M</code>이라고 하자.</p>
<h3 id="패턴-전처리">패턴 전처리</h3>
<p>먼저 패턴의 접두사와 접미사 구조를 분석해 <code>pi</code> 배열을 만든다.</p>
<pre><code class="language-text">O(M)</code></pre>
<h3 id="텍스트-탐색">텍스트 탐색</h3>
<p>텍스트를 앞에서부터 끝까지 확인한다.</p>
<pre><code class="language-text">O(N)</code></pre>
<p>따라서 전체 시간 복잡도는 다음과 같다.</p>
<pre><code class="language-text">O(N + M)</code></pre>
<p>패턴의 정보를 저장하기 위한 추가 공간 복잡도는 다음과 같다.</p>
<pre><code class="language-text">O(M)</code></pre>
<hr />
<h2 id="단순-탐색과-kmp-비교">단순 탐색과 KMP 비교</h2>
<table>
<thead>
<tr>
<th>구분</th>
<th>단순 탐색</th>
<th>KMP</th>
</tr>
</thead>
<tbody><tr>
<td>비교 실패 시</td>
<td>다음 시작 위치에서 패턴을 처음부터 비교</td>
<td>이전 일치 정보를 이용해 비교 위치 결정</td>
</tr>
<tr>
<td>텍스트 재검사</td>
<td>이미 확인한 부분을 다시 볼 수 있음</td>
<td>텍스트의 위치가 뒤로 가지 않음</td>
</tr>
<tr>
<td>사전 작업</td>
<td>없음</td>
<td>패턴의 <code>pi</code> 배열 생성</td>
</tr>
<tr>
<td>시간 복잡도</td>
<td><code>O(N × M)</code></td>
<td><code>O(N + M)</code></td>
</tr>
<tr>
<td>핵심 아이디어</td>
<td>가능한 모든 위치에서 직접 비교</td>
<td>패턴의 접두사·접미사 구조 활용</td>
</tr>
</tbody></table>
<p>텍스트와 패턴이 짧다면 단순 탐색으로도 충분할 수 있다.</p>
<p>하지만 텍스트가 길거나 패턴에 반복적인 구조가 많다면 KMP가 더 안정적인 탐색 성능을 제공한다.</p>
<hr />