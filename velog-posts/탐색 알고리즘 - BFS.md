<p>그래프나 2차원 맵에서 특정 위치를 탐색하는 대표적인 방법에는 DFS와 BFS가 있다.</p>
<p>그중 <strong>BFS(Breadth-First Search, 너비 우선 탐색)</strong>는 현재 위치에서 가까운 곳부터 차례대로 탐색하는 알고리즘이다.</p>
<pre><code class="language-text">시작점
→ 한 번 이동해서 갈 수 있는 위치
→ 두 번 이동해서 갈 수 있는 위치
→ 세 번 이동해서 갈 수 있는 위치</code></pre>
<p>즉, 하나의 경로를 끝까지 따라가는 것이 아니라 <strong>같은 거리에 있는 위치를 먼저 모두 확인한 뒤 다음 거리로 넘어간다.</strong></p>
<hr />
<h2 id="bfs의-핵심-구조">BFS의 핵심 구조</h2>
<p>BFS는 일반적으로 <code>queue</code>를 사용한다.</p>
<pre><code class="language-text">먼저 발견한 위치
→ 먼저 탐색

나중에 발견한 위치
→ 나중에 탐색</code></pre>
<p>BFS는 시작점에서 가까운 위치를 먼저 발견하기 때문에 큐에 들어간 순서대로 탐색하면 자연스럽게 가까운 위치부터 처리할 수 있다.</p>
<p>예를 들어 다음과 같은 구조가 있다고 생각해보자.</p>
<pre><code class="language-text">        A
      /   \
     B     C
    / \   / \
   D   E F   G</code></pre>
<p>A에서 BFS를 시작하면 다음 순서로 탐색한다.</p>
<pre><code class="language-text">A
→ B, C
→ D, E, F, G</code></pre>
<p>탐색 과정을 큐로 표현하면 다음과 같다.</p>
<pre><code class="language-text">큐: [A]

A 제거
B, C 삽입
큐: [B, C]

B 제거
D, E 삽입
큐: [C, D, E]

C 제거
F, G 삽입
큐: [D, E, F, G]</code></pre>
<p>먼저 발견된 위치가 먼저 처리되기 때문에 깊이가 같은 위치가 모두 처리된 후에야 다음 깊이로 넘어간다.</p>
<hr />
<h2 id="bfs가-최단-거리를-구할-수-있는-이유">BFS가 최단 거리를 구할 수 있는 이유</h2>
<p>BFS는 다음 순서로 탐색한다.</p>
<pre><code class="language-text">거리 0인 위치
→ 거리 1인 위치
→ 거리 2인 위치
→ 거리 3인 위치</code></pre>
<p>따라서 어떤 위치를 처음 방문했다면 그 경로보다 더 짧은 경로가 나중에 발견될 수 없다.</p>
<p>예를 들어 목적지를 세 번 이동해서 처음 발견했다고 생각해보자.</p>
<pre><code class="language-text">시작점
→ 1칸 거리 전부 확인
→ 2칸 거리 전부 확인
→ 3칸 거리에서 목적지 발견</code></pre>
<p>이미 1칸과 2칸으로 갈 수 있는 모든 위치를 확인했으므로 목적지까지 두 번 이하로 이동하는 경로는 존재하지 않는다.</p>
<p>따라서 <strong>모든 이동 비용이 동일한 그래프에서는 BFS로 최단 이동 횟수를 구할 수 있다.</strong></p>
<blockquote>
<p>BFS 에서 목표하는 지점 도달이 최초로 관측된다면, 해당 경로가 최단경로라고 볼 수 있다.</p>
</blockquote>
<pre><code class="language-text">한 칸 이동 비용이 모두 1
→ 먼저 도착한 경로가 최단 경로</code></pre>
<p>반대로 이동마다 비용이 다르다면 단순 BFS만으로는 최단 비용을 보장할 수 없다.</p>
<hr />
<h2 id="방문-처리가-필요한-이유">방문 처리가 필요한 이유</h2>
<p>그래프나 2차원 맵에서는 이미 방문한 위치로 다시 돌아갈 수 있다.</p>
<pre><code class="language-text">A → B
B → A
A → B
B → A
...</code></pre>
<p>방문 여부를 기록하지 않으면 같은 위치가 큐에 계속 들어가면서 불필요한 탐색이 반복될 수 있다.</p>
<p>따라서 BFS에서는 일반적으로 방문 배열을 사용한다.</p>
<pre><code class="language-cpp">vector&lt;vector&lt;int&gt;&gt; is_visited(
    maps.size(),
    vector&lt;int&gt;(maps[0].size(), 0)
);</code></pre>
<p>방문하지 않은 위치는 <code>0</code>, 방문한 위치는 <code>1</code>로 관리한다.</p>
<p>중요한 점은 <strong>큐에서 꺼낼 때가 아니라 큐에 넣을 때 방문 처리해야 한다는 것</strong>이다.</p>
<pre><code class="language-cpp">q.push({x, y});
is_visited[x][y] = 1;</code></pre>
<p>방문 처리를 나중에 하면 하나의 위치가 여러 경로를 통해 큐에 중복으로 들어갈 수 있다.</p>
<hr />
<h1 id="실전-예제-게임-맵-최단거리">실전 예제: 게임 맵 최단거리</h1>
<p>프로그래머스의 <code>게임 맵 최단거리</code> 문제를 BFS로 풀이한 코드를 보면 더 쉽게 이해할 수 있다.</p>
<pre><code>#include &lt;vector&gt;
#include &lt;queue&gt;
#include &lt;algorithm&gt;
using namespace std;

int dx[4] = {0, 0, -1, 1};
int dy[4] = {1, -1, 0, 0};



int solution(vector&lt;vector&lt;int&gt; &gt; maps)
{
    int answer = 0;
    vector&lt;vector&lt;int&gt;&gt; is_visited(maps.size(), vector&lt;int&gt;(maps[0].size(), 0));
    vector&lt;vector&lt;int&gt;&gt; score(maps.size(), vector&lt;int&gt;(maps[0].size(), 10000));
    queue&lt;pair&lt;int, int&gt;&gt; q;
    q.push({0, 0});
    score[0][0] = 1;
    is_visited[0][0] = 1;
    while(!q.empty()){
        int cur_x = q.front().first;
        int cur_y = q.front().second;
        q.pop();
        for(int i=0; i&lt;4; i++){
            int x = cur_x + dx[i];
            int y = cur_y + dy[i];
            if(x &lt; 0 || x &gt;= score.size() || y &lt; 0 || y &gt;= score[x].size()) continue;
            if(maps[x][y] == 0 || is_visited[x][y] != 0) continue;
            q.push({x, y});
            is_visited[x][y] = 1;
            score[x][y] = min(score[cur_x][cur_y] + 1, score[x][y]);
        }
    }

    answer = score[score.size()-1][score[score.size()-1].size()-1] != 10000 ? score[score.size()-1][score[score.size()-1].size()-1] : -1;

    return answer;
}</code></pre><h1 id="정리">정리</h1>
<p>BFS의 핵심은 복잡하지 않다.</p>
<pre><code class="language-text">1. 시작점을 큐에 넣는다.
2. 시작점을 방문 처리한다.
3. 큐의 앞에서 현재 위치를 꺼낸다.
4. 현재 위치와 연결된 위치를 확인한다.
5. 방문하지 않은 위치를 파악한다.
6. 가치가 충분한 요소라면 큐에 넣는다.
7. 큐가 빌 때까지 반복한다.</code></pre>
<p>BFS가 최단 거리를 구할 수 있는 이유는 <strong>가까운 위치부터 거리 순서대로 탐색하기 때문</strong>이다.</p>
<pre><code class="language-text">거리 1인 위치를 모두 탐색
→ 거리 2인 위치를 모두 탐색
→ 거리 3인 위치를 모두 탐색</code></pre>
<p>따라서 이동 비용이 모두 같은 맵에서 어떤 위치를 처음 방문했다면, 그때 기록된 거리가 해당 위치까지의 최단 거리다.</p>
<p>프로그래머스의 <code>게임 맵 최단거리</code> 문제 역시 모든 이동 비용이 <code>1</code>이므로 BFS를 사용해 해결할 수 있다.</p>