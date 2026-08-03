<h1 id="architecture">Architecture</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b67c8d89-fb8b-42ca-bde1-23cc7d671da0/image.png" /></p>
<p>2017년 처음 발표된 원조 Transformer 아키텍처는 크게 Encoder와 Decoder로 구성된다.</p>
<p>이후에는 BERT와 같은 Encoder-only 구조와 GPT와 같은 Decoder-only 구조도 등장했지만,</p>
<p>이 글에서는 원 논문의 Encoder–Decoder 구조를 기준으로 살펴본다.</p>
<p>인코더를 통해서 입력문장이 가지는 토큰들이 해당 문장에서의 맥락정보를 가지게 된 뒤,
그 정보를 기반으로 디코딩 작업을 통해 예측작업을 수행해가며 결과를 산출하게 된다.</p>
<h3 id="positional-encoding">Positional Encoding</h3>
<p>각 토큰의 임베딩 벡터에 같은 차원의 위치 벡터를 원소별로 더해, 해당 토큰이 문장 내 몇 번째 위치에 있는지를 모델 입력에 반영하는 과정</p>
<blockquote>
<ul>
<li>Transformer는 '모든 토큰을 함께 보는 컨셉'으로 토큰 간 순서를 직접 알 수 없다. 
(예: 너는 나를 때렸다 &lt;-&gt; 나는 너를 때렸다)
모든 연관관계를 따지는 Attention 연산이 진행되기에 위치 정보를 알 방도가 없다.
그렇기에 <strong>Positional Encoding</strong> 과정을 통해 위치 정보를 담아 모델이 위치정보를 알 수 있게 한다.</li>
</ul>
</blockquote>
<h2 id="encoder">Encoder</h2>
<blockquote>
<p>한 줄 요약 : 입력문장 토큰들에 대해서, 각 토큰이 해당 문장의 흐름을 반영한 <strong>맥락정보</strong>를 가지게 한다.</p>
</blockquote>
<p>원문을 <strong>토큰화</strong>하여 <strong>Token ID</strong>를 발급하고 <strong>Token Embedding</strong>을 진행한다.
이후, <strong>Positional Encoding</strong> 처리까지 진행한 상태를 주로 <strong>Input Vector</strong> 상태로 취급한다.</p>
<h3 id="self-attention">Self-Attention</h3>
<p>입력벡터는 가중치 연산을 통해 아래의 행렬정보를 담도록 만들어지고, 내적을 통해 결과를 도출한다.</p>
<ul>
<li>Query : 찾고 있는 정보 ( <strong>무엇을 찾을까?</strong> )</li>
<li>Key : 가지고 있는 정보 ( <strong>나는 어떤 정보로 검색될까?</strong> )</li>
<li>Value : 선택되었을 때 전달할 정보 ( <strong>선택된다면 어떤 내용을 전달할까?</strong> )</li>
</ul>
<blockquote>
<p>** 내적의 이유**</p>
</blockquote>
<ul>
<li>내적은 구조적으로 두 벡터가 비슷한 방향으로 정렬될수록 더 큰 값이 나오게 된다.</li>
<li>Attention에서는 학습을 통해 <strong>문맥적으로 관련 있는 Query와 Key가 큰 내적값을 갖도록</strong> 가중치 행렬을 조정한다.</li>
</ul>
<p>Q와 전치변환된 K의 내적 결과 [<strong>A</strong>]</p>
<ul>
<li>Attention Score</li>
<li>[i][j] : i번째 토큰은 j번째 토큰을 얼마나 주목하는가?<ul>
<li>예 : Q(study) * K(ai) -&gt; study가 자신의 표현을 만들 때, ai를 얼마나 관련 있는 토큰으로 판단하는가?</li>
<li>즉, 행정보는 '누구를 참고하는가'를 나타내고, 열정보는 '이 토큰이 얼마나 참고되는가'를 나타낸다.</li>
</ul>
</li>
</ul>
<p>결과값을 보정해준다.</p>
<blockquote>
<p>일종의 Scaling</p>
</blockquote>
<ul>
<li>내적은 각 차원의 곱을 모두 더하는 계산.<ul>
<li>차원이 5개면 5개를 더하고, 512개면 512개를 더한다.
그렇기에 차원이 커질수록 내적값의 분산값도 커지게 된다.</li>
<li>내적값을 표준편차값으로 나눠주게 되면 점수의 크기를 안정적으로 유지할 수 있게 된다.</li>
<li>그리고 표준편차는 <strong>차원의 수의 제곱근</strong> 정도의 크기를 가진다.</li>
</ul>
</li>
</ul>
<p>이후 각 행별로 Softmax를 적용하여 <strong>행 토큰이 열 토큰을 어느 비율로 참고하는가</strong>를 나타내는 가중치 행렬 A를 완성한다.</p>
<p>A와 V의 내적 결과 (Q와 전치변환 K의 결과 행렬은 V행렬과 내적 할 수 있는 구조를 가진 상태이므로 전치변환을 할 필요가 없다.)</p>
<ul>
<li>Attention Output</li>
<li>참고하는 비율에 맞게 각 토큰이 실제 전달할 정보를 담도록 하는 작업</li>
</ul>
<p>이 과정을 통해 완성된 행렬은 <strong>해당 토큰이 문장 속 다른 토큰들의 정보를 필요한 만큼 가져와 만든 새로운 문맥 벡터</strong>를 의미한다.</p>
<p>여기까지의 과정을 <strong>Self-Attention</strong> 이라고 한다.</p>
<h4 id="multi-head-attention">Multi Head Attention</h4>
<p>Transformer는 해당 기법을 하나의 시선에서 바라보는 것이 아니라, <strong>다양한 관점</strong>으로 바라보고 문맥정보를 가질 수 있도록 Self-Attention을 여러번 수행시킨다.
이를 <strong>Multi Head Attention</strong>이라고 한다.</p>
<p>각각의 self-attention에서 Q,K,V를 뽑아내는 가중치를 다르게 하여, 여러 관점에서 맥락을 파악할 수 있도록 동작시킨다.</p>
<blockquote>
<p>Multi Head Attention 작업을 거친 뒤, 결과 벡터들을 concat 해준 뒤, 선형변환 작업을 거쳐 하나의 표현으로 가공한다.</p>
</blockquote>
<h3 id="add--norm">Add &amp; Norm</h3>
<p>multi head attention을 통해 얻어낸 맥락 정보에서는
여러 가공을 거쳤기에, 원문의 정보가 흐려질 우려가 있다.</p>
<h4 id="add">Add</h4>
<p>기존 토큰 정보와 산출물을 더해주는 과정으로
기존 토큰 의미는 유지하면서, Attention이 찾은 문맥 정보만 추가한다.</p>
<h4 id="norm">Norm</h4>
<p>더해주는 과정이 반복되다보니, 값이나 퍼짐정도과 과해질 수 있다.
이를 행단위로 정규화 하여 
<strong>각 토큰 벡터의 평균과 퍼짐을 정돈해 값과 기울기의 규모를 안정시키고,
Transformer가 깊어져도 학습이 원활하게 이루어지도록 돕는다.</strong></p>
<h3 id="feed-forward">Feed Forward</h3>
<p>더 큰차원으로 <strong>비선형 변환</strong>을 진행시켰다가 원래 차원으로 복구시켜
<strong>정보 가공 효과</strong>를 기대한다.</p>
<p>이 단계 이후에도 Add &amp; Norm 작업을 수행해준다.
<strong>이곳에서 Add 단계에서 더해지는 행렬은 초기 행렬이 아니라, 문맥정보가 반영된 행렬이다!!</strong></p>
<p>이 과정까지 수행되면, 산출물로 문맥정보를 담은 행렬을 얻게 되고
Encoding 작업이 완료된다.</p>
<h2 id="decoder">Decoder</h2>
<blockquote>
<p>한 줄 요약 : Encoder 작업을 거친 맥락 정보를 이용해 순차적으로 단어를 예측한다.</p>
</blockquote>
<p><strong>하지만!</strong> Self-Attention 과정은 입력 정보의 모든 상관관계를 따진다!
<strong>그치만!</strong> 예측을 진행할 때, 뒤에 등장할 토큰 정보를 따지면 곤란하겠죠?!</p>
<h3 id="masked-multi-head-attention">Masked Multi Head Attention</h3>
<p>학습할 때는 정답 문장을 한 칸 오른쪽으로 이동시켜 Decoder의 입력으로 사용한다.
그리고 Masked Self-Attention에 Causal Mask를 적용하여 각 위치가 자신보다 뒤에 있는 미래 토큰을 참고하지 못하게 한다.</p>
<blockquote>
<p><strong>Causal Mask</strong>
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1dfb6aa4-e4fa-4721-8c87-b8489ec8d1f6/image.png" /></p>
</blockquote>
<blockquote>
<p>예시 :
원문 - I, Study, AI, (end)
변형 - (start), I, Study, AI</p>
</blockquote>
<ul>
<li>이 구조를 통해 실제 'I'를 예측해야할 때는 (start) 만 바라볼 수 있는 상태로 학습을 진행한다.</li>
<li>물론! Causal Mask를 더해준 상태라 뒷부분은 알 수 없다.</li>
</ul>
<p>Linear 이전의 부분은 Self-Attention 과정을 이미 설명했으니 생략한다.</p>
<blockquote>
<p><strong>Cross Attention</strong> 기법을 적용하여
Decoder의 표현을 Query로 사용하고, Encoder의 최종 출력을 Key와 Value로 사용한다.
이를 통해 Decoder가 입력 문장의 관련 정보를 참고하며 다음 토큰을 예측할 수 있다.</p>
</blockquote>
<h3 id="linear">Linear</h3>
<p>앞선 과정을 통해
요청사항을 고려한 문맥을 바탕으로 <strong>다음에 무엇이 나와야 하는가?</strong></p>
<p>정보가 도출된다.
하지만 이는 어떤 단어를 의미하는지 알 수 없다.</p>
<p><strong>모델의 어휘에 맞게 조정되어야 한다.</strong></p>
<p>Decoder의 최종 출력은 아직 문맥을 담은 벡터일 뿐, 특정 단어 자체를 의미하지는 않는다.</p>
<p>Linear 계층은 이 벡터를 모델의 전체 Vocabulary 크기로 변환한다. 그 결과 Vocabulary에 포함된 각 토큰마다 하나의 점수인 logit이 만들어진다.</p>
<p>이 과정을 통해 모델이 예측한 단어가 무엇인가? 에 대한 점수를 도출할 수 있다.</p>
<h3 id="softmax">Softmax</h3>
<p>Linear가 만든 logits(점수)는 제멋대로인 상태이다.
이 정보에 Softmax를 적용하여 각 단어가 적합할 확률로 변환해준다.</p>