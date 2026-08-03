<h1 id="transformer-이전의-인공지능-software-30에서-attention까지">Transformer 이전의 인공지능: Software 3.0에서 Attention까지</h1>
<blockquote>
<p>이 글은 <strong>Software 3.0의 등장과 LLM의 특징을 간단히 살펴본 뒤, 자연어 처리 기술이 Attention 모델에 도달하기까지의 흐름</strong>을 정리한 글이다.
Transformer의 구체적인 구조는 다음 글에서 이어서 다룬다. </p>
</blockquote>
<hr />
<h2 id="소프트웨어는-어떻게-발전해-왔을까">소프트웨어는 어떻게 발전해 왔을까?</h2>
<p>소프트웨어의 발전은 크게 <strong>Software 1.0, 2.0, 3.0</strong>의 흐름으로 정리할 수 있다.</p>
<h3 id="software-10-사람이-규칙을-직접-작성한다">Software 1.0: 사람이 규칙을 직접 작성한다</h3>
<p>Software 1.0은 개발자가 원하는 동작을 코드로 직접 작성하는 방식이다.</p>
<pre><code class="language-text">사람이 규칙 작성
→ 컴파일러 또는 인터프리터
→ 프로그램 실행</code></pre>
<p>예를 들어 사용자의 나이에 따라 회원 등급을 나눈다면 다음과 같이 사람이 조건을 직접 정의한다.</p>
<pre><code class="language-python">if age &gt;= 20:
    grade = &quot;adult&quot;
else:
    grade = &quot;minor&quot;</code></pre>
<p>입력에 대해 어떤 결과를 만들어야 하는지 사람이 명확하게 알고 있으며, 그 규칙을 프로그래밍 언어로 표현한다.</p>
<hr />
<h3 id="software-20-데이터로-규칙을-학습한다">Software 2.0: 데이터로 규칙을 학습한다</h3>
<p>하지만 이미지 분류, 음성 인식, 추천처럼 모든 규칙을 사람이 직접 정의하기 어려운 문제가 등장했다.</p>
<p>예를 들어 고양이 사진을 구분하기 위해 귀의 크기, 털의 색상, 눈의 모양과 같은 조건을 사람이 일일이 작성하는 것은 현실적으로 어렵다.</p>
<p>Software 2.0에서는 사람이 규칙을 작성하는 대신 다음을 제공한다.</p>
<pre><code class="language-text">데이터 + 정답 + 신경망 구조
→ 학습
→ 규칙을 포함한 모델 생성</code></pre>
<p>즉, 사람이 프로그램의 모든 판단 규칙을 직접 만드는 것이 아니라, <strong>모델이 데이터로부터 판단 기준을 학습</strong>하게 되었다.</p>
<p>다만 이 시기의 인공지능은 대부분 특정 문제를 해결하기 위한 <strong>Task-specific AI</strong>였다.</p>
<pre><code class="language-text">이미지 분류 모델
번역 모델
추천 모델
음성 인식 모델
이상 탐지 모델</code></pre>
<p>문제가 달라지면 데이터를 다시 수집하고, 모델을 다시 설계하고, 별도로 학습해야 했다. 결국 <strong>문제 하나당 모델 하나가 필요하다</strong>는 한계가 있었다.</p>
<hr />
<h2 id="software-30-자연어가-코드가-되는-시대">Software 3.0: 자연어가 코드가 되는 시대</h2>
<p>Transformer와 대규모 언어 모델이 등장하면서 새로운 변화가 시작되었다.</p>
<p>Software 3.0에서는 개발자가 모든 처리 절차를 코드로 작성하지 않는다. 대신 자연어로 목표와 역할을 설명하고, LLM이 그 지시에 맞는 결과를 생성하도록 한다.</p>
<pre><code class="language-text">Software 1.0
코드 → 프로그램 실행

Software 2.0
데이터 → 모델 학습 → 예측

Software 3.0
자연어 지시 + 데이터 + 모델
→ AI가 판단하고 결과 생성</code></pre>
<p>예를 들어 과거에는 요약 기능을 만들기 위해 문장 분리, 핵심어 추출, 중요도 계산 등의 로직을 직접 구현해야 했다.</p>
<p>하지만 Software 3.0에서는 다음과 같이 자연어로 요청할 수 있다.</p>
<pre><code class="language-text">이 문서를 세 문단으로 요약하고,
핵심 위험 요소를 표로 정리해줘.</code></pre>
<p>자연어가 소프트웨어와 상호작용하는 새로운 인터페이스가 된 것이다.</p>
<p>이러한 변화는 개발자의 역할도 바꾸었다.</p>
<p>과거의 개발자가 주로 <strong>코드 작성자</strong>였다면, Software 3.0 시대의 개발자는 다음과 같은 역할까지 담당하게 된다.</p>
<ul>
<li>해결할 문제와 목표 정의</li>
<li>필요한 데이터와 문맥 제공</li>
<li>모델이 수행할 역할 설계</li>
<li>결과 검증 및 후처리</li>
<li>기존 코드와 AI 모델의 역할 분리</li>
</ul>
<p>즉, Software 3.0은 기존 소프트웨어를 완전히 없애는 것이 아니라, <strong>결정적인 처리는 기존 코드가 담당하고 추론·판단·생성은 LLM이 담당하는 구조</strong>로 볼 수 있다.</p>
<hr />
<h2 id="software-30-시대의-llm">Software 3.0 시대의 LLM</h2>
<p>LLM은 방대한 텍스트 데이터를 학습하여 사람의 언어를 처리하는 대규모 언어 모델이다.</p>
<p>번역이나 분류처럼 하나의 문제만 해결하는 것이 아니라, 프롬프트와 문맥에 따라 다양한 작업을 수행할 수 있다.</p>
<pre><code class="language-text">질문 답변
문서 요약
번역
문장 생성
코드 작성
정보 추출
분류
추론</code></pre>
<p>이로 인해 인공지능은 다음과 같이 변화했다.</p>
<pre><code class="language-text">Task-specific AI
문제마다 별도의 모델 필요

        ↓

Foundation Model
하나의 대규모 모델을 여러 업무에 활용</code></pre>
<p>대규모 사전학습 모델을 만든 뒤, 프롬프트나 파인튜닝을 통해 새로운 문제에 빠르게 적용할 수 있게 된 것이다.</p>
<p>그러나 LLM은 기존의 결정론적 프로그램과 동작 방식이 다르다. 높은 표현력과 범용성을 얻은 대신 새로운 문제도 함께 나타났다.</p>
<hr />
<h2 id="llm이-가진-대표적인-문제">LLM이 가진 대표적인 문제</h2>
<h3 id="black-box">Black Box</h3>
<p>딥러닝 모델은 수많은 파라미터의 상호작용으로 결과를 만들어낸다.</p>
<p>따라서 어떤 입력에 대해 특정 답변이 나온 이유를 사람이 명확하게 설명하기 어렵다.</p>
<pre><code class="language-text">입력
→ 수많은 파라미터 연산
→ 출력</code></pre>
<p>결과가 잘못되었을 때도 어느 단계에서 문제가 발생했는지 추적하기 쉽지 않다.</p>
<hr />
<h3 id="bias">Bias</h3>
<p>LLM은 학습 데이터에 포함된 정보와 표현 방식을 학습한다.</p>
<p>따라서 데이터에 사회적·문화적 편향이나 오래된 정보가 포함되어 있다면 모델도 이를 답변에 반영할 수 있다.</p>
<p>프롬프트를 잘 작성하더라도 학습 과정에서 형성된 편향을 완전히 제거하기는 어렵다.</p>
<hr />
<h3 id="hallucination">Hallucination</h3>
<p>LLM은 데이터베이스에서 정답을 그대로 검색하는 시스템이 아니다.</p>
<p>주어진 문맥을 바탕으로 <strong>다음에 등장할 가능성이 높은 토큰을 예측</strong>하면서 문장을 생성한다.</p>
<p>따라서 실제로 존재하지 않는 논문, 출처, 수치 또는 코드를 그럴듯하게 생성할 수 있다.</p>
<p>중요한 것은 답변이 자연스럽다는 사실과 답변이 정확하다는 사실은 서로 다르다는 점이다.</p>
<hr />
<h3 id="non-deterministic">Non-deterministic</h3>
<p>일반적인 프로그램은 같은 입력에 대해 같은 결과를 출력한다.</p>
<pre><code class="language-text">동일한 입력
→ 동일한 코드 실행
→ 동일한 결과</code></pre>
<p>반면 LLM은 확률에 따라 다음 토큰을 선택하기 때문에 같은 프롬프트를 입력하더라도 결과가 조금씩 달라질 수 있다.</p>
<pre><code class="language-text">동일한 프롬프트
→ 여러 후보 토큰의 확률 계산
→ 확률적 선택
→ 매번 조금씩 다른 결과</code></pre>
<p>따라서 LLM 기반 서비스를 만들 때는 단순히 프롬프트만 작성하는 것이 아니라, 출력 형식 제한, 결과 검증, 근거 검색, 재시도 정책과 같은 보완 장치가 필요하다.</p>
<hr />
<h1 id="자연어-처리의-시작">자연어 처리의 시작</h1>
<p>LLM이 사람의 언어를 다룰 수 있기까지 자연어 처리 기술은 여러 단계를 거쳐 발전했다.</p>
<p>자연어 처리, 즉 <strong>NLP(Natural Language Processing)</strong>의 근본적인 질문은 다음과 같다.</p>
<blockquote>
<p>사람이 사용하는 언어를 컴퓨터는 어떻게 이해할 수 있을까?</p>
</blockquote>
<p>컴퓨터는 문자를 사람처럼 직접 이해하지 못한다. 결국 언어를 계산 가능한 <strong>숫자 형태로 변환</strong>해야 한다.</p>
<p>먼저 텍스트 데이터 전체를 모은 집합을 <strong>말뭉치, Corpus</strong>라고 한다.</p>
<p>그리고 특정 자연어 처리 작업에서 사용하는 단어의 집합을 <strong>Vocabulary</strong>라고 한다.</p>
<pre><code class="language-text">Corpus
→ 수집한 전체 텍스트

Vocabulary
→ 모델이 사용할 단어의 집합</code></pre>
<hr />
<h2 id="one-hot-vector와-bow">One-hot Vector와 BoW</h2>
<h3 id="one-hot-vector">One-hot Vector</h3>
<p>가장 단순한 방법은 각 단어에 고유한 번호를 부여하는 것이다.</p>
<p>단어가 다섯 개라면 다음과 같이 표현할 수 있다.</p>
<pre><code class="language-text">여기    → [1, 0, 0, 0, 0]
지금    → [0, 1, 0, 0, 0]
아주    → [0, 0, 1, 0, 0]
위험    → [0, 0, 0, 1, 0]
합니다  → [0, 0, 0, 0, 1]</code></pre>
<p>각 단어를 구분할 수 있다는 장점은 있지만, 단어 간 의미 관계는 표현하지 못한다.</p>
<p>예를 들어 <code>자동차</code>와 <code>승용차</code>는 의미가 비슷하지만 One-hot Vector에서는 완전히 다른 벡터로 표현된다.</p>
<hr />
<h3 id="bag-of-words">Bag of Words</h3>
<p>BoW는 문장에 각 단어가 몇 번 등장했는지를 벡터로 표현한다.</p>
<pre><code class="language-text">&quot;아주 아주 위험합니다&quot;

→ 아주: 2
→ 위험: 1
→ 합니다: 1</code></pre>
<p>단어의 등장 횟수는 알 수 있지만 순서는 알 수 없다.</p>
<p>따라서 다음 두 문장이 같은 벡터로 표현될 수 있다.</p>
<pre><code class="language-text">나는 너를 좋아한다.
너는 나를 좋아한다.</code></pre>
<p>단어 구성은 비슷하지만 의미는 완전히 다르다.</p>
<hr />
<h2 id="n-gram과-tf-idf">N-gram과 TF-IDF</h2>
<h3 id="n-gram">N-gram</h3>
<p>BoW가 단어 순서를 무시하는 문제를 보완하기 위해 연속된 여러 단어를 묶는 N-gram이 사용되었다.</p>
<p>예를 들어 다음 문장을 Bigram으로 나누면 두 단어씩 묶는다.</p>
<pre><code class="language-text">I am studying bigram model

→ I am
→ am studying
→ studying bigram
→ bigram model</code></pre>
<p>어느 정도 순서 정보를 보존할 수 있지만, <code>n</code>이 커질수록 가능한 단어 조합이 급격히 증가한다.</p>
<hr />
<h3 id="tf-idf">TF-IDF</h3>
<p>모든 단어가 문서에서 같은 중요도를 가지는 것은 아니다.</p>
<p>TF-IDF는 다음 두 값을 이용해 단어의 중요도를 계산한다.</p>
<ul>
<li><strong>TF:</strong> 특정 문서에서 단어가 얼마나 자주 등장하는가</li>
<li><strong>IDF:</strong> 전체 문서에서 해당 단어가 얼마나 희귀한가</li>
</ul>
<p>한 문서에 자주 등장하지만 다른 문서에서는 잘 등장하지 않는 단어일수록 높은 중요도를 가진다.</p>
<p>문서 검색과 키워드 추출에는 효과적이지만, 여전히 단어의 깊은 의미나 문맥을 이해하는 것은 아니다.</p>
<hr />
<h3 id="빈도-기반-표현의-한계">빈도 기반 표현의 한계</h3>
<p>BoW와 TF-IDF는 텍스트를 수치화할 수 있다는 점에서 의미가 있었지만 다음과 같은 한계를 가졌다.</p>
<h4 id="순서와-문맥을-충분히-표현하지-못한다">순서와 문맥을 충분히 표현하지 못한다</h4>
<p>단어가 어떤 순서와 상황에서 사용되었는지를 제대로 반영하기 어렵다.</p>
<h4 id="차원의-저주가-발생한다">차원의 저주가 발생한다</h4>
<p>Vocabulary에 단어가 10만 개라면 하나의 문장도 10만 차원의 벡터로 표현될 수 있다.</p>
<p>대부분 값이 0인 매우 크고 희소한 벡터가 만들어진다.</p>
<h4 id="단어-간-의미-관계를-표현하지-못한다">단어 간 의미 관계를 표현하지 못한다</h4>
<pre><code class="language-text">동생 ↔ 아우
자동차 ↔ 승용차
기쁨 ↔ 행복</code></pre>
<p>서로 의미가 비슷하더라도 빈도 기반 벡터만으로는 관계를 파악하기 어렵다.</p>
<hr />
<h2 id="사람이-단어-관계를-직접-정의할-수-있을까">사람이 단어 관계를 직접 정의할 수 있을까?</h2>
<p>초기에는 사전이나 시소러스처럼 사람이 단어 관계를 직접 정의하려는 시도도 있었다.</p>
<p>대표적으로 WordNet은 단어들을 동의어 집합으로 묶고, 상위어와 하위어 등의 관계를 그래프로 구성했다.</p>
<pre><code class="language-text">object
└─ motor vehicle
   ├─ car
   ├─ truck
   └─ go-kart</code></pre>
<p>그러나 세상의 모든 단어와 의미 관계를 사람이 직접 정의하기는 어렵다.</p>
<p>새로운 단어가 계속 생기며, 같은 단어도 문맥에 따라 의미가 달라진다. 결국 단어의 의미를 데이터로부터 학습할 필요가 생겼다.</p>
<hr />
<h2 id="분포-가설과-word-embedding">분포 가설과 Word Embedding</h2>
<p>자연어 처리 발전의 중요한 기반이 된 개념이 <strong>분포 가설</strong>이다.</p>
<blockquote>
<p>비슷한 문맥에서 등장하는 단어는 비슷한 의미를 가진다.</p>
</blockquote>
<p>예를 들어 <code>동생</code>과 <code>아우</code>는 다음과 같은 비슷한 문맥에서 사용될 가능성이 높다.</p>
<pre><code class="language-text">나보다 어린 동생
나보다 어린 아우</code></pre>
<p>이처럼 단어의 의미를 사전에 직접 정의하는 대신, <strong>주변에 어떤 단어들이 함께 등장하는지를 통해 의미를 학습</strong>하는 것이다.</p>
<hr />
<h3 id="word2vec">Word2Vec</h3>
<p>Word2Vec은 단어와 주변 단어의 관계를 학습하여 각 단어를 밀집 벡터로 표현한다.</p>
<pre><code class="language-text">One-hot Vector
→ 단어를 구분하기 위한 희소 벡터

Word Embedding
→ 단어의 의미 관계를 포함한 밀집 벡터</code></pre>
<p>비슷한 문맥에서 사용되는 단어는 임베딩 공간에서도 가까운 위치에 배치된다.</p>
<p>그 결과 다음과 같은 의미 관계를 벡터 연산으로 표현할 수 있게 되었다.</p>
<pre><code class="language-text">King - Man + Woman ≈ Queen</code></pre>
<p>이제 모델은 단어를 단순한 번호가 아니라, 의미 관계를 가진 숫자 벡터로 처리할 수 있게 되었다.</p>
<p>다만 Word2Vec의 임베딩은 하나의 단어에 하나의 고정된 벡터를 사용한다.</p>
<p>따라서 <code>은행</code>처럼 여러 의미를 가진 단어의 문맥 차이를 표현하기 어렵다.</p>
<pre><code class="language-text">돈을 맡기는 은행
강가의 둑을 뜻하는 bank</code></pre>
<p>두 문장에서 의미는 다르지만 동일한 단어 벡터가 사용된다.</p>
<hr />
<h1 id="language-model의-등장">Language Model의 등장</h1>
<p>언어 모델은 지금까지 등장한 단어들을 바탕으로 다음 단어의 확률을 계산하는 모델이다.</p>
<p>예를 들어 다음 문장이 있다고 하자.</p>
<pre><code class="language-text">퇴근 후 공항에 택시를 타고 갔는데,
탑승 시간에 늦어서 결국 비행기를 (      )</code></pre>
<p>앞의 문맥을 고려하면 다음과 같은 단어가 높은 확률을 가질 수 있다.</p>
<pre><code class="language-text">놓쳤다
탔다
취소했다
기다렸다</code></pre>
<p>언어 모델은 각 후보에 확률을 부여하고 가장 자연스러운 단어를 선택한다.</p>
<pre><code class="language-text">앞의 단어들
→ 다음 단어별 확률 계산
→ 가장 가능성 높은 단어 선택</code></pre>
<p>현재의 LLM도 규모와 구조는 훨씬 크지만, 근본적으로는 문맥을 바탕으로 다음 토큰을 예측한다는 원리를 가진다.</p>
<hr />
<h2 id="rnn-과거-정보를-기억하다">RNN: 과거 정보를 기억하다</h2>
<p>문장은 단어의 순서가 중요한 시계열 데이터이다.</p>
<p>RNN은 단어를 하나씩 순차적으로 입력받으면서 이전 정보가 담긴 <strong>Hidden State</strong>를 다음 시점으로 전달한다.</p>
<pre><code class="language-text">첫 번째 단어
→ Hidden State

두 번째 단어 + 이전 Hidden State
→ 새로운 Hidden State

세 번째 단어 + 이전 Hidden State
→ 새로운 Hidden State</code></pre>
<p>이를 통해 현재 단어뿐 아니라 이전에 등장한 단어의 정보도 다음 단어 예측에 사용할 수 있었다.</p>
<p>하지만 문장이 길어지면 앞부분의 정보가 뒤까지 제대로 전달되지 않는 문제가 발생했다.</p>
<p>학습 과정에서 기울기가 점점 작아지는 <strong>기울기 소실 문제</strong>가 발생했고, 긴 문장의 장기 의존성을 학습하기 어려웠다.</p>
<hr />
<h2 id="lstm과-gru-기억을-선택적으로-관리하다">LSTM과 GRU: 기억을 선택적으로 관리하다</h2>
<p>RNN의 장기 기억 문제를 개선하기 위해 LSTM과 GRU가 등장했다.</p>
<h3 id="lstm">LSTM</h3>
<p>LSTM은 여러 개의 Gate를 사용하여 정보를 관리한다.</p>
<pre><code class="language-text">어떤 정보를 기억할지
어떤 정보를 버릴지
어떤 정보를 출력할지</code></pre>
<p>필요한 과거 정보는 오래 유지하고 불필요한 정보는 제거할 수 있게 되었다.</p>
<h3 id="gru">GRU</h3>
<p>GRU는 LSTM의 구조를 단순화하여 연산량을 줄인 모델이다.</p>
<p>RNN보다 긴 문맥을 처리할 수 있게 되었지만, 여전히 단어를 순서대로 처리해야 한다는 구조적 한계는 남아 있었다.</p>
<pre><code class="language-text">첫 번째 단어 처리
→ 두 번째 단어 처리
→ 세 번째 단어 처리
→ ...</code></pre>
<p>앞의 계산이 끝나야 다음 계산을 수행할 수 있으므로 병렬 처리가 어렵다.</p>
<hr />
<h2 id="seq2seq-문장을-입력받아-문장을-생성하다">Seq2Seq: 문장을 입력받아 문장을 생성하다</h2>
<p>번역처럼 입력과 출력이 모두 문장인 문제를 해결하기 위해 <strong>Sequence-to-Sequence 모델</strong>이 등장했다.</p>
<p>Seq2Seq는 Encoder와 Decoder로 구성된다.</p>
<pre><code class="language-text">입력 문장
→ Encoder
→ Context Vector
→ Decoder
→ 출력 문장</code></pre>
<p>Encoder는 입력 문장을 읽고 전체 정보를 하나의 Context Vector로 압축한다.</p>
<p>Decoder는 이 Context Vector를 바탕으로 출력 문장을 하나씩 생성한다.</p>
<p>하지만 입력 문장이 길어질수록 모든 정보를 하나의 고정된 벡터에 담아야 했다.</p>
<pre><code class="language-text">짧은 문장
→ 비교적 정보 보존 가능

긴 문장
→ 하나의 벡터에 과도하게 압축
→ 정보 손실</code></pre>
<p>번역 문장을 생성할 때 어떤 단어를 출력하더라도 동일한 Context Vector만 참고한다는 것이 문제였다.</p>
<hr />
<h1 id="attention-필요한-정보를-그때그때-다시-본다">Attention: 필요한 정보를 그때그때 다시 본다</h1>
<p>Seq2Seq의 정보 압축 문제를 해결하기 위해 등장한 것이 <strong>Attention</strong>이다.</p>
<p>Attention의 핵심은 모든 입력 정보를 하나의 벡터에 압축하지 않는 것이다.</p>
<p>Decoder가 단어를 하나 생성할 때마다 Encoder의 전체 Hidden State를 다시 살펴본다.</p>
<pre><code class="language-text">기존 Seq2Seq

입력 전체
→ 하나의 Context Vector
→ 모든 출력에서 동일하게 사용</code></pre>
<pre><code class="language-text">Attention

출력 단어를 생성하는 매 시점마다
→ 입력의 모든 단어를 다시 확인
→ 현재 출력에 중요한 단어에 높은 가중치 부여</code></pre>
<p>예를 들어 번역 모델이 특정 단어를 출력하려 한다면, 입력 문장 전체를 동일하게 보는 것이 아니라 현재 출력과 관련성이 높은 단어에 더 집중한다.</p>
<p>이때 각 입력 단어가 현재 출력에 얼마나 중요한지를 나타내는 값이 <strong>Attention Score</strong>다.</p>
<pre><code class="language-text">현재 출력하려는 단어
        ↓
입력 단어별 관련성 계산
        ↓
중요한 단어에 높은 Attention Score
        ↓
가중합을 이용해 Context 생성</code></pre>
<p>Attention은 다음과 같은 효과를 가져왔다.</p>
<ul>
<li>긴 문장의 정보 손실 완화</li>
<li>출력 시점마다 다른 문맥 활용</li>
<li>입력과 출력 단어 사이 관계 확인</li>
<li>Seq2Seq의 고정 Context Vector 병목 개선</li>
</ul>
<p>즉, Attention은 모델이 문장을 무조건 앞에서부터 기억하는 것에서 벗어나, <strong>현재 필요한 정보가 무엇인지 선택하여 참고할 수 있게 만든 구조</strong>다.</p>
<hr />
<h1 id="마무리">마무리</h1>
<p>자연어 처리 기술의 발전은 결국 다음 질문을 해결해온 과정이라고 볼 수 있다.</p>
<pre><code class="language-text">단어를 어떻게 숫자로 표현할 것인가?
→ One-hot Vector, BoW, TF-IDF

단어의 의미 관계를 어떻게 담을 것인가?
→ 분포 가설, Word Embedding

단어의 순서와 과거 문맥을 어떻게 기억할 것인가?
→ RNN, LSTM, GRU

문장 전체를 어떻게 입력받아 문장을 생성할 것인가?
→ Seq2Seq

긴 문장에서 필요한 정보를 어떻게 선택할 것인가?
→ Attention</code></pre>
<p>그리고 Attention을 중심으로 순환 구조를 제거하고, 문장 전체의 관계를 병렬로 계산하는 방향으로 발전한 모델이 바로 <strong>Transformer</strong>다.</p>
<pre><code class="language-text">BoW / TF-IDF
→ Word Embedding
→ RNN
→ LSTM·GRU
→ Seq2Seq
→ Attention
→ Transformer
→ LLM</code></pre>
<p>다음 글에서는 Attention이 어떻게 <strong>Self-Attention</strong>으로 확장되었으며, 이것이 어떻게 Transformer의 핵심 구조가 되었는지 정리한다.</p>