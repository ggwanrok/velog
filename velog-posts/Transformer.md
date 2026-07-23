<h1 id="attention">Attention</h1>
<p>~</p>
<h2 id="self-attention">Self Attention</h2>
<p>~</p>
<h1 id="architecture">Architecture</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b67c8d89-fb8b-42ca-bde1-23cc7d671da0/image.png" /></p>
<p>트랜스포머 모델은 간단하게 인코더와 디코더로 구분된다.</p>
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
<p>Q와 수직변환된 K의 내적 결과 [<strong>A</strong>]</p>
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
<p>일종의 Scailing</p>
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
<p>A와 V의 내적 결과 (Q와 수직변환 K의 결과 행렬은 V행렬과 내적 할 수 있는 구조를 가진 상태이므로 수직변환을 할 필요가 없다.)</p>
<ul>
<li>Attention Output</li>
<li>참고하는 비율에 맞게 각 토큰이 실제 전달할 정보를 담도록 하는 작업</li>
</ul>
<p>이 과정을 통해 완성된 행렬은 <strong>해당 토큰이 문장 속 다른 토큰들의 정보를 필요한 만큼 가져와 만든 새로운 문맥 벡터</strong>를 의미한다.</p>
<p>-해야하는 부분-</p>
<p>근데 이게 이제 여러 관점에서 바라보도록 멀티로 돌리구요
멀티로 돌린 놈들을 합쳐주고 정규화 해줍니다.</p>
<p>더 다채로운 표현할 수 있도록 피드포워드 해주고요</p>
<p>자라란~ 문맥정보를 담은 컨텍스트 완성~</p>
<p>응 내일 더 써~</p>
<h2 id="decoder">Decoder</h2>