<p>그래프나 2차원 맵에서 특정 위치를 탐색하는 대표적인 방법에는 DFS와 BFS가 있다.</p>
<p>그중 <strong>DFS(Depth-First Search, 깊이 우선 탐색)</strong> 는 현재 위치에서 갈 수 있는 경로를 하나 선택한 뒤, 더 이상 이동할 수 없을 때까지 깊게 탐색하는 알고리즘이다.</p>
<pre><code class="language-text">시작점
→ 연결된 위치로 이동
→ 이어진 연결된 위치로 이동
→ 더 이상 이동할 수 없으면 이전 위치로 돌아감</code></pre>
<p>즉, 현재 위치와 가까운 곳을 모두 확인하는 것이 아니라 <strong>하나의 경로를 끝까지 탐색한 후 다른 경로를 확인한다.</strong></p>
<hr />
<h2 id="dfs의-핵심-구조">DFS의 핵심 구조</h2>
<p>DFS는 일반적으로 <code>stack</code> 또는 <code>재귀 함수</code>를 사용한다.</p>
<pre><code class="language-text">현재 위치에서 다음 위치로 이동
→ 이동한 위치에서 다시 다음 위치로 이동
→ 더 이상 이동할 수 없으면 이전 위치로 복귀</code></pre>
<p>재귀 함수는 함수 호출이 스택에 쌓이는 구조이므로 DFS를 자연스럽게 구현할 수 있다.</p>
<p>예를 들어 다음과 같은 구조가 있다고 생각해보자.</p>
<pre><code class="language-text">        A
      /   \
     B     C
    / \   / \
   D   E F   G</code></pre>
<p>왼쪽에 연결된 위치부터 탐색한다고 가정하면 A에서 시작한 DFS의 탐색 순서는 다음과 같다.</p>
<pre><code class="language-text">A
→ B
→ D
→ E
→ C
→ F
→ G</code></pre>
<p>조금 더 자세히 살펴보면 다음과 같다.</p>
<pre><code class="language-text">A 방문
→ B 방문
   → D 방문
   → 더 이상 이동할 곳이 없으므로 B로 복귀
   → E 방문
   → 더 이상 이동할 곳이 없으므로 B로 복귀
→ B의 탐색이 끝났으므로 A로 복귀
→ C 방문
   → F 방문
   → G 방문</code></pre>
<p>하나의 경로를 가능한 깊게 탐색하고, 더 이상 이동할 수 없을 때 이전 위치로 돌아가는 방식이다.</p>
<p>스택으로 표현하면 다음과 같다.</p>
<pre><code class="language-text">스택: [A]

A 제거
C, B 삽입
스택: [C, B]

B 제거
E, D 삽입
스택: [C, E, D]

D 제거
스택: [C, E]

E 제거
스택: [C]

C 제거
G, F 삽입
스택: [G, F]</code></pre>
<p>스택은 마지막에 들어온 요소를 먼저 처리하는 <code>LIFO(Last In, First Out)</code> 구조이므로 한 방향으로 깊게 탐색할 수 있다.</p>
<blockquote>
<p>스택에 인접한 노드를 넣는 순서에 따라 실제 탐색 순서는 달라질 수 있다.</p>
</blockquote>
<hr />
<h2 id="dfs가-깊은-경로를-먼저-탐색하는-이유">DFS가 깊은 경로를 먼저 탐색하는 이유</h2>
<p>DFS는 현재 위치에서 방문할 수 있는 다음 위치를 발견하면 다른 위치를 확인하기 전에 해당 위치로 즉시 이동한다.</p>
<pre><code class="language-text">현재 위치 방문
→ 인접한 위치 발견
→ 해당 위치로 이동
→ 이동한 위치의 인접한 위치 확인</code></pre>
<p>재귀 함수로 구현하면 다음과 같은 형태가 된다.</p>
<pre><code class="language-cpp">void dfs(int current)
{
    visited[current] = true;

    for (int next : graph[current])
    {
        if (!visited[next])
        {
            dfs(next);
        }
    }
}</code></pre>
<p><code>dfs(next)</code>가 호출되면 현재 함수의 나머지 작업은 잠시 멈춘다. 새롭게 호출된 함수가 자신의 탐색을 모두 끝내야 이전 함수로 돌아올 수 있다.</p>
<pre><code class="language-text">dfs(A)
→ dfs(B)
   → dfs(D)
   → D 탐색 종료
   → dfs(E)
   → E 탐색 종료
→ B 탐색 종료
→ dfs(C)</code></pre>
<p>이러한 재귀 호출 구조 때문에 DFS는 자연스럽게 하나의 경로를 끝까지 탐색한다.</p>
<p>DFS는 특히 다음과 같은 문제에서 자주 사용된다.</p>
<pre><code class="language-text">모든 경로 탐색
연결된 영역 확인
사이클 탐지
백트래킹
조합과 순열 탐색</code></pre>
<p>다만 DFS는 깊이를 우선해서 탐색하므로 처음 발견한 경로가 최단 경로라는 보장은 없다.</p>
<pre><code class="language-text">DFS
→ 하나의 경로를 먼저 끝까지 탐색
→ 더 짧은 경로가 다른 방향에 있을 수 있음</code></pre>
<p>따라서 이동 비용이 동일한 그래프에서 최단 거리를 구해야 한다면 일반적으로 BFS를 사용하는 것이 적합하다.</p>
<hr />
<h2 id="방문-처리가-필요한-이유">방문 처리가 필요한 이유</h2>
<p>그래프나 2차원 맵에서는 하나의 위치가 여러 위치와 연결될 수 있다.</p>
<p>예를 들어 A와 B가 서로 연결되어 있다면 다음과 같은 탐색이 반복될 수 있다.</p>
<pre><code class="language-text">A → B
B → A
A → B
B → A
...</code></pre>
<p>방문 여부를 기록하지 않으면 같은 위치를 계속 탐색하면서 무한 재귀가 발생할 수 있다.</p>
<p>따라서 DFS에서도 일반적으로 방문 배열을 사용한다.</p>
<pre><code class="language-cpp">vector is_visited(n, 0);</code></pre>
<p>방문하지 않은 위치는 <code>0</code>, 방문한 위치는 <code>1</code>로 관리한다.</p>
<pre><code class="language-cpp">is_visited[current] = 1;</code></pre>
<p>중요한 점은 <strong>현재 위치를 탐색하기 시작할 때 바로 방문 처리해야 한다는 것</strong>이다.</p>
<pre><code class="language-cpp">void dfs(int current)
{
    is_visited[current] = 1;

    for (int next : graph[current])
    {
        if (is_visited[next] == 0)
        {
            dfs(next);
        }
    }
}</code></pre>
<p>방문 처리를 하지 않거나 너무 늦게 처리하면 서로 연결된 위치를 반복해서 탐색할 수 있다.</p>
<pre><code class="language-text">A 방문
→ B로 이동
→ B에서 다시 A로 이동
→ A에서 다시 B로 이동</code></pre>
<p>현재 위치에 도착하자마자 방문 처리하면 이미 확인한 위치로 다시 이동하는 것을 방지할 수 있다.</p>
<hr />
<h1 id="실전-예제-네트워크">실전 예제: 네트워크</h1>
<p>프로그래머스의 <code>네트워크</code> 문제를 DFS로 풀이한 코드를 보면 더 쉽게 이해할 수 있다.</p>
<p>이 문제에서는 컴퓨터 사이의 연결 정보를 확인하여 서로 연결된 네트워크의 개수를 구해야 한다.</p>
<p>예를 들어 다음과 같이 컴퓨터가 연결되어 있다고 생각해보자.</p>
<pre><code class="language-text">1 — 2

3 — 4</code></pre>
<p>컴퓨터 <code>1</code>과 <code>2</code>는 하나의 네트워크이고, 컴퓨터 <code>3</code>과 <code>4</code>는 또 다른 네트워크다.</p>
<p>따라서 전체 네트워크의 개수는 <code>2</code>개다.</p>
<p>한 컴퓨터에서 DFS를 시작하면 해당 컴퓨터와 연결된 모든 컴퓨터를 방문할 수 있다.</p>
<pre><code class="language-text">방문하지 않은 컴퓨터 발견
→ 네트워크 개수 증가
→ DFS로 연결된 컴퓨터를 모두 방문 처리</code></pre>
<p>이를 코드로 구현하면 다음과 같다.</p>
<pre><code class="language-cpp">#include &lt;string&gt;
#include &lt;vector&gt;
#include &lt;set&gt;

using namespace std;

set&lt;int&gt; is_in;
vector&lt;set&lt;int&gt;&gt; node;

int dfs(int n){
    int flag = 0;
    for(auto i : node[n]){
        if(is_in.find(i) == is_in.end()){
            flag++;
            is_in.insert(i);
            flag += dfs(i);
        }
    }
    return flag;
}

int solution(int n, vector&lt;vector&lt;int&gt;&gt; computers) {
    int answer = 0;
    node.resize(n);
    for(int i=0; i&lt;computers.size(); i++){
        for(int j=0; j&lt;computers[i].size(); j++){
            if(computers[i][j]){
                node[i].insert(j);
                node[j].insert(i);
            }
        }
    }

    for(int i=0; i&lt;node.size(); i++){
        if(dfs(i)) answer++;
    }

    return answer;
}</code></pre>
<hr />
<h1 id="정리">정리</h1>
<p>DFS의 핵심은 복잡하지 않다.</p>
<pre><code class="language-text">1. 현재 위치를 방문 처리한다.
2. 현재 위치와 연결된 위치를 확인한다.
3. 방문하지 않은 위치를 찾는다.
4. 해당 위치에서 다시 DFS를 실행한다.
5. 더 이상 이동할 위치가 없으면 이전 위치로 돌아간다.
6. 모든 위치를 확인할 때까지 반복한다.</code></pre>
<p>DFS가 깊은 경로를 먼저 탐색하는 이유는 <strong>현재 위치에서 다음 위치를 발견하면 해당 위치의 탐색을 바로 시작하기 때문</strong>이다.</p>
<pre><code class="language-text">현재 위치 탐색
→ 다음 위치로 이동
→ 이동한 위치에서 다시 다음 위치 탐색
→ 막다른 경로에 도달하면 이전 위치로 복귀</code></pre>
<p>프로그래머스의 <code>네트워크</code> 문제 역시 하나의 컴퓨터에서 연결된 모든 컴퓨터를 탐색해야 하므로 DFS를 사용해 해결할 수 있다.</p>
<p>다만 DFS는 하나의 경로를 우선해서 탐색하므로 <strong>처음 발견한 경로가 최단 경로라는 보장은 없다.</strong></p>
<pre><code class="language-text">최단 거리 탐색
→ BFS

연결 관계 또는 모든 경우 탐색
→ DFS</code></pre>
<p>따라서 문제에서 요구하는 것이 최단 거리인지, 연결된 영역이나 모든 경우의 탐색인지 구분하여 DFS와 BFS를 선택해야 한다.</p>