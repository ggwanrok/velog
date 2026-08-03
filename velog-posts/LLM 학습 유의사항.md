<h1 id="transformer-이후-llm은-어떻게-더-좋아지고-효율적으로-발전했을까">Transformer 이후, LLM은 어떻게 더 좋아지고 효율적으로 발전했을까?</h1>
<p>이전 글에서는 Transformer가 입력 토큰의 관계를 파악하고, 문맥을 반영해 다음 토큰을 예측하는 구조를 살펴보았다.</p>
<p>하지만 Transformer 구조를 크게 만들었다고 해서 곧바로 좋은 LLM이 완성되는 것은 아니다.</p>
<p>이번 글에서는 현대 LLM의 학습과 효율화에 사용되는 핵심 기술인 <strong>RLHF, Scaling Law, Knowledge Distillation, MoE</strong>를 살펴본다.</p>
<hr />
<h1 id="rlhf">RLHF</h1>
<h2 id="사람의-선호를-모델에-반영하다">사람의 선호를 모델에 반영하다</h2>
<p><strong>RLHF(Reinforcement Learning from Human Feedback)</strong>는 사람의 피드백을 이용해 LLM이 더욱 유용하고 안전하며, 사용자의 의도에 맞는 답변을 생성하도록 학습하는 방법이다.</p>
<pre><code class="language-text">Reinforcement Learning
→ 강화학습

Human Feedback
→ 사람의 평가와 선호</code></pre>
<h2 id="왜-rlhf가-필요할까">왜 RLHF가 필요할까?</h2>
<p>LLM의 사전학습 목표는 기본적으로 다음 토큰을 잘 예측하는 것이다.</p>
<pre><code class="language-text">입력 문장
→ 다음에 등장할 가능성이 높은 토큰 예측</code></pre>
<p>방대한 데이터를 통해 언어의 문법, 표현, 지식과 패턴을 학습할 수는 있지만, 이것만으로 다음과 같은 기준까지 자연스럽게 학습되는 것은 아니다.</p>
<pre><code class="language-text">사용자의 질문 의도에 제대로 답하기
친절하고 이해하기 쉽게 설명하기
위험하거나 공격적인 답변 피하기
사실을 모르면 모른다고 답하기
요구한 출력 형식 지키기</code></pre>
<p>즉, 사전학습 모델은 <strong>자연스러운 문장을 생성하는 능력</strong>은 뛰어나지만, 반드시 <strong>사람이 좋아하는 방식으로 대답하는 모델</strong>인 것은 아니다.</p>
<p>예를 들어 다음 질문이 있다고 하자.</p>
<blockquote>
<p>파이썬에서 리스트를 뒤집는 방법을 알려줘.</p>
</blockquote>
<p>다음 두 답변은 모두 틀리지 않다.</p>
<pre><code class="language-text">답변 A
reverse()를 사용하면 됩니다.</code></pre>
<pre><code class="language-text">답변 B
리스트를 뒤집는 방법은 두 가지가 있습니다.

1. reverse()
   원본 리스트 자체를 변경합니다.

2. a[::-1]
   원본은 유지하면서 새로운 리스트를 생성합니다.

상황에 따라 적절한 방식을 선택하면 됩니다.</code></pre>
<p>하지만 많은 사용자는 단순히 정답만 던지는 답변보다, 차이점과 사용 상황까지 설명하는 두 번째 답변을 선호할 가능성이 높다.</p>
<p>RLHF는 정답 자체보다는 <strong>어떤 답변을 사람이 더 선호하는가</strong>를 모델에 학습시키는 과정이다.</p>
<blockquote>
<p>RLHF는 새로운 지식을 대량으로 넣는 단계라기보다, 사전학습으로 얻은 능력을 사람이 원하는 방향으로 표현하도록 조정하는 과정에 가깝다.</p>
</blockquote>
<p>솔직히 요즘 토큰값 아끼는 것이 중요해진 시대라 큰 의미는 없는 과정인 기분이 든다..</p>
<hr />
<h2 id="rlhf의-전체-과정">RLHF의 전체 과정</h2>
<p>RLHF는 일반적으로 다음 세 단계로 진행된다.</p>
<pre><code class="language-text">Supervised Fine-Tuning
→ Reward Model
→ Reinforcement Learning</code></pre>
<hr />
<h2 id="1단계-supervised-fine-tuning">1단계: Supervised Fine-Tuning</h2>
<p>먼저 사람이 직접 작성하거나 검수한 모범 답변을 이용해 모델을 지도학습한다.</p>
<pre><code class="language-text">질문
파이썬 리스트를 뒤집는 방법은?

모범 답변
reverse() 또는 슬라이싱 [::-1]을 사용할 수 있습니다.
두 방식은 원본 변경 여부에 차이가 있습니다.</code></pre>
<p>모델은 이러한 질문과 답변 쌍을 학습하며 다음과 같은 기본적인 응답 방식을 익힌다.</p>
<ul>
<li>질문의 의도를 파악하는 방법</li>
<li>답변을 구조화하는 방법</li>
<li>친절하고 자연스럽게 설명하는 방법</li>
<li>지시사항에 맞춰 답변하는 방법</li>
</ul>
<p>이를 <strong>SFT(Supervised Fine-Tuning)</strong>라고 한다.</p>
<pre><code class="language-text">Pretrained Model
+ 모범 답변 데이터
→ SFT Model</code></pre>
<hr />
<h2 id="2단계-reward-model">2단계: Reward Model</h2>
<p>다음으로 하나의 질문에 대해 모델이 여러 답변을 생성한다.</p>
<pre><code class="language-text">질문
이메일을 정중하게 변경해줘.

답변 A
회의 시간을 변경하고 싶습니다.

답변 B
안녕하세요. 부득이한 일정으로 회의 시간 변경을 요청드리고자 합니다.

답변 C
가능하다면 이번 주 목요일로 변경 부탁드립니다.</code></pre>
<p>사람은 이 답변들을 보고 선호 순위를 매긴다.</p>
<pre><code class="language-text">B &gt; C &gt; A</code></pre>
<p>이러한 선호 데이터를 학습하여 <strong>어떤 답변을 사람이 더 좋아할지 점수화하는 모델</strong>을 만든다.</p>
<p>이 모델이 <strong>Reward Model</strong>, 즉 보상 모델이다.</p>
<pre><code class="language-text">질문 + 답변
→ Reward Model
→ 사람의 선호를 나타내는 보상 점수</code></pre>
<p>보상 모델은 정답을 직접 생성하는 모델이 아니다.</p>
<p>현재 생성된 답변이 사람의 선호에 얼마나 가까운지를 평가하는 역할을 한다.</p>
<hr />
<h2 id="3단계-reinforcement-learning">3단계: Reinforcement Learning</h2>
<p>마지막으로 LLM이 답변을 생성하면 Reward Model이 점수를 부여한다.</p>
<p>LLM은 더 높은 보상을 받을 수 있도록 자신의 답변 생성 정책을 수정한다.</p>
<pre><code class="language-text">현재 LLM
→ 답변 생성
→ Reward Model 평가
→ 보상 점수
→ LLM 정책 업데이트
→ 다시 답변 생성</code></pre>
<p>전통적인 RLHF에서는 이 정책을 수정하는 데 <strong>PPO(Proximal Policy Optimization)</strong>와 같은 강화학습 알고리즘을 사용한다.</p>
<p>이 과정을 반복하면서 모델은 다음 방향으로 변화한다.</p>
<pre><code class="language-text">사람이 선호하는 답변
→ 생성 확률 증가

사람이 선호하지 않는 답변
→ 생성 확률 감소</code></pre>
<hr />
<h2 id="rlhf의-효과">RLHF의 효과</h2>
<p>RLHF를 적용하면 모델의 응답은 다음과 같이 개선될 수 있다.</p>
<ul>
<li>질문 의도에 더 잘 맞는 답변</li>
<li>친절하고 구조화된 설명</li>
<li>일관된 말투와 형식</li>
<li>위험하거나 유해한 출력 감소</li>
<li>지시사항을 따르는 능력 향상</li>
<li>대화형 서비스에 적합한 응답 생성</li>
</ul>
<p>오늘날의 대화형 생성 AI가 단순히 다음 단어만 이어 붙이는 듯한 모델이 아니라, 사용자의 요청에 맞춰 도움을 주는 형태로 동작하는 데에는 이러한 정렬 과정이 큰 역할을 한다.</p>
<hr />
<h2 id="rlhf의-한계">RLHF의 한계</h2>
<h3 id="reward-hacking">Reward Hacking</h3>
<p>모델이 실제로 좋은 답변을 만드는 대신, <strong>보상 모델이 높은 점수를 주는 특징만 공략</strong>할 수 있다.</p>
<pre><code class="language-text">좋은 답변을 생성한다
        X

좋은 답변처럼 보이는 표현을 반복한다
        O</code></pre>
<p>예를 들어 보상 모델이 친절하고 긴 답변에 높은 점수를 주는 경향이 있다면, 모델은 필요 이상으로 장황하거나 과도하게 친절한 답변을 생성할 수 있다.</p>
<hr />
<h3 id="지나친-동조">지나친 동조</h3>
<p>사용자를 만족시키는 방향을 지나치게 학습하면 사용자의 주장에 무조건 동의하는 현상이 나타날 수 있다.</p>
<pre><code class="language-text">사용자 주장
→ 비판적으로 검토하지 않음
→ 과도한 칭찬과 동조</code></pre>
<p>모델은 필요할 때 잘못된 점을 지적해야 하지만, 높은 선호 점수를 받기 위해 지나치게 아부하거나 긍정적인 표현만 사용할 수 있다.</p>
<hr />
<h3 id="사람의-선호도-하나의-편향이다">사람의 선호도 하나의 편향이다</h3>
<p>사람마다 선호하는 답변은 다르다.</p>
<pre><code class="language-text">간결한 답변을 선호하는 사람
자세한 답변을 선호하는 사람
직접적인 표현을 선호하는 사람
부드러운 표현을 선호하는 사람</code></pre>
<p>또한 평가자의 문화, 언어, 가치관에 따라 Reward Model의 기준도 달라질 수 있다.</p>
<p>따라서 다음 질문이 발생한다.</p>
<blockquote>
<p>누구의 선호를 모델의 기준으로 삼아야 하는가?</p>
</blockquote>
<hr />
<h3 id="높은-데이터-구축-비용">높은 데이터 구축 비용</h3>
<p>답변을 직접 작성하고, 여러 답변을 비교하고, 선호 순위를 기록하려면 많은 인력과 시간이 필요하다.</p>
<p>특히 전문적인 법률, 의료, 금융 분야에서는 일반 평가자가 아니라 해당 분야 전문가의 검수가 필요할 수 있다.</p>
<hr />
<h2 id="rlhf에서-기억할-점">RLHF에서 기억할 점</h2>
<blockquote>
<p>RLHF는 모델을 무조건 똑똑하게 만드는 기술이라기보다, 모델의 답변 행동을 사람의 기대에 맞게 정렬하는 기술이다.</p>
</blockquote>
<pre><code class="language-text">사전학습
→ 언어와 지식 학습

RLHF
→ 답변 태도와 행동 정렬</code></pre>
<hr />
<h1 id="scaling-law">Scaling Law</h1>
<h2 id="모델은-무조건-크게-만들면-좋을까">모델은 무조건 크게 만들면 좋을까?</h2>
<p>초기 LLM 경쟁에서는 파라미터 수가 모델 성능을 대표하는 지표처럼 사용되었다.</p>
<pre><code class="language-text">파라미터 수 증가
→ 표현할 수 있는 패턴 증가
→ 모델 성능 향상</code></pre>
<p>실제로 모델의 규모를 늘리면 일정 구간에서 성능이 향상된다.</p>
<p>하지만 모델 크기만 늘린다고 반드시 효율적인 학습이 이루어지는 것은 아니다.</p>
<pre><code class="language-text">매개변수는 매우 많음
데이터는 부족함
학습 연산량은 제한됨

→ 거대한 모델을 충분히 학습하지 못함</code></pre>
<p>이 문제를 다루는 개념이 <strong>Scaling Law</strong>다.</p>
<hr />
<h2 id="scaling-law란">Scaling Law란?</h2>
<p>Scaling Law는 모델의 성능이 다음 요소의 규모에 따라 비교적 일정한 패턴으로 변화한다는 경험 법칙이다.</p>
<pre><code class="language-text">Parameters
→ 모델의 매개변수 수

Data
→ 학습에 사용한 토큰 수

Compute
→ 학습에 사용한 연산량</code></pre>
<p>일정한 조건에서 이 값들을 증가시키면 Loss가 감소하고 성능이 향상되는 경향이 나타난다.</p>
<pre><code class="language-text">Parameters ↑
Data ↑
Compute ↑
→ Loss ↓
→ 성능 ↑</code></pre>
<p>이 관계는 무작위로 움직이기보다 일정 구간에서 <strong>Power Law 형태</strong>를 보인다.</p>
<p>따라서 작은 규모의 실험 결과를 바탕으로 더 큰 모델의 예상 성능과 필요한 자원을 추정할 수 있다.</p>
<hr />
<h2 id="scaling-law가-중요한-이유">Scaling Law가 중요한 이유</h2>
<p>거대 모델 학습에는 막대한 비용이 들어간다.</p>
<p>모델을 학습한 뒤에야 설계가 잘못되었다는 사실을 발견하면 이미 상당한 GPU 비용과 시간이 소비된 상태다.</p>
<p>Scaling Law를 이용하면 본 학습 이전에 다음을 판단할 수 있다.</p>
<pre><code class="language-text">주어진 연산 예산에서 적절한 모델 크기는 얼마인가?
데이터가 얼마나 필요한가?
모델을 더 키우는 것이 유리한가?
데이터를 더 확보하는 것이 유리한가?
예상 Loss는 어느 정도인가?</code></pre>
<p>즉, Scaling Law는 단순히 “크게 만들면 좋아진다”가 아니라, <strong>주어진 비용 안에서 모델·데이터·연산량을 어떻게 배분할 것인가</strong>를 다루는 개념이다.</p>
<hr />
<h2 id="chinchilla-scaling-law">Chinchilla Scaling Law</h2>
<p>Scaling Law의 대표적인 사례가 Google DeepMind의 <strong>Chinchilla</strong>다.</p>
<p>기존에는 모델의 파라미터를 크게 늘리는 방식이 중요하게 여겨졌다.</p>
<p>하지만 Chinchilla 연구에서는 다음과 같은 관찰을 제시했다.</p>
<blockquote>
<p>매우 큰 모델을 적은 데이터로 학습하는 것보다, 적절한 크기의 모델을 훨씬 많은 데이터로 학습하는 편이 더 나을 수 있다.</p>
</blockquote>
<table>
<thead>
<tr>
<th>모델</th>
<th align="right">파라미터</th>
<th align="right">학습 토큰</th>
<th>특징</th>
</tr>
</thead>
<tbody><tr>
<td>GPT-3</td>
<td align="right">175B</td>
<td align="right">약 300B</td>
<td>모델은 크지만 학습 데이터가 상대적으로 부족</td>
</tr>
<tr>
<td>Chinchilla</td>
<td align="right">70B</td>
<td align="right">약 1.4T</td>
<td>모델은 더 작지만 충분한 데이터로 학습</td>
</tr>
</tbody></table>
<p>Chinchilla는 GPT-3보다 파라미터 수가 적지만 더 많은 토큰을 학습함으로써 더 우수한 성능을 보였다. </p>
<p>핵심은 다음과 같다.</p>
<pre><code class="language-text">큰 모델 + 부족한 데이터
보다

적절한 모델 + 충분한 데이터
가 더 효율적일 수 있다.</code></pre>
<hr />
<h2 id="scaling-law에서-주의할-점">Scaling Law에서 주의할 점</h2>
<h3 id="파라미터만-늘리면-안-된다">파라미터만 늘리면 안 된다</h3>
<p>파라미터 수를 늘렸다면 그만큼 학습할 데이터와 연산량도 함께 확보해야 한다.</p>
<pre><code class="language-text">모델 크기만 증가
→ 각 파라미터가 충분히 학습되지 않음
→ 계산 예산 낭비</code></pre>
<hr />
<h3 id="데이터의-양만큼-품질도-중요하다">데이터의 양만큼 품질도 중요하다</h3>
<p>Scaling Law는 데이터의 규모를 중요한 요소로 다루지만, 모든 토큰이 동일한 학습 가치를 가지는 것은 아니다.</p>
<p>중복, 오류, 스팸, 편향이 많은 데이터를 무작정 늘리면 모델의 품질을 보장하기 어렵다.</p>
<pre><code class="language-text">많은 데이터
≠ 반드시 좋은 데이터</code></pre>
<hr />
<h3 id="성능은-계속-오르지만-효율은-감소한다">성능은 계속 오르지만 효율은 감소한다</h3>
<p>규모를 확대할수록 성능은 좋아질 수 있지만, 같은 수준의 성능 향상을 얻기 위해 필요한 비용은 점점 커진다.</p>
<pre><code class="language-text">초기의 규모 확대
→ 큰 성능 향상

이미 거대한 모델의 추가 확대
→ 막대한 비용 대비 작은 향상</code></pre>
<p>따라서 성능뿐 아니라 학습 비용과 추론 비용을 함께 고려해야 한다.</p>
<hr />
<h3 id="학습-성능과-서비스-효율은-다르다">학습 성능과 서비스 효율은 다르다</h3>
<p>거대한 모델이 벤치마크에서 높은 성능을 보이더라도 실제 서비스에서는 다음 문제가 발생할 수 있다.</p>
<ul>
<li>응답 시간이 길어짐</li>
<li>GPU 메모리 사용량 증가</li>
<li>요청당 비용 증가</li>
<li>동시 사용자 처리량 감소</li>
<li>배포 가능한 환경 제한</li>
</ul>
<p>Scaling 단계부터 학습 성능뿐 아니라 최종 배포 환경도 고려해야 한다.</p>
<hr />
<h2 id="scaling-law의-핵심">Scaling Law의 핵심</h2>
<blockquote>
<p>좋은 LLM은 가장 큰 모델이 아니라, 주어진 연산량에서 모델 크기와 데이터가 균형 있게 배분된 모델이다.</p>
</blockquote>
<pre><code class="language-text">Model
+
Data
+
Compute
=
효율적인 Scaling</code></pre>
<hr />
<h1 id="knowledge-distillation">Knowledge Distillation</h1>
<h2 id="좋은-거대-모델을-이용해-작은-모델을-만들다">좋은 거대 모델을 이용해 작은 모델을 만들다</h2>
<p>높은 성능의 거대 모델은 강력하지만 비용도 크다.</p>
<pre><code class="language-text">높은 추론 성능
긴 응답 시간
높은 GPU 메모리 사용량
큰 운영 비용</code></pre>
<p>그렇다면 이미 잘 학습된 거대 모델의 능력을 더 작은 모델에 전달할 수는 없을까?</p>
<p>이를 위한 기술이 <strong>Knowledge Distillation</strong>, 즉 지식 증류다.</p>
<hr />
<h2 id="teacher와-student">Teacher와 Student</h2>
<p>Knowledge Distillation에서는 두 모델이 등장한다.</p>
<pre><code class="language-text">Teacher Model
→ 크고 성능이 뛰어난 모델

Student Model
→ 더 작고 빠르게 동작할 모델</code></pre>
<p>Teacher Model이 생성한 출력과 판단 정보를 이용하여 Student Model을 학습한다.</p>
<pre><code class="language-text">Teacher Model
→ 답변 또는 확률분포 생성
→ Student Model 학습</code></pre>
<p>단순히 파일을 압축하듯 거대한 모델의 파라미터를 줄이는 것은 아니다.</p>
<p>Teacher가 학습한 <strong>출력 패턴과 판단 기준을 Student가 따라 배우도록 하는 지식 전달 과정</strong>이다.</p>
<hr />
<h2 id="정답만-배우는-것과-판단을-배우는-것">정답만 배우는 것과 판단을 배우는 것</h2>
<p>일반적인 지도학습은 정답 레이블만 제공한다.</p>
<pre><code class="language-text">고양이
→ [1, 0, 0]</code></pre>
<p>이러한 정답을 <strong>Hard Label</strong>이라고 한다.</p>
<p>Hard Label은 정답이 무엇인지는 알려주지만, 다른 후보와 얼마나 비슷한지는 알려주지 않는다.</p>
<p>반면 Teacher Model은 각 후보에 대한 확률을 제공할 수 있다.</p>
<pre><code class="language-text">고양이 0.7
개     0.2
여우   0.1</code></pre>
<p>이를 <strong>Soft Label</strong>이라고 한다.</p>
<p>Soft Label에는 Teacher가 학습한 클래스 간 관계가 포함되어 있다.</p>
<pre><code class="language-text">고양이는 자동차보다는 개와 더 비슷하다.
고양이와 개는 여우와도 어느 정도 관련이 있다.</code></pre>
<p>따라서 Student는 정답만 외우는 것이 아니라, Teacher가 각 후보를 어떻게 구분하는지도 학습할 수 있다.</p>
<table>
<thead>
<tr>
<th>구분</th>
<th>Hard Label</th>
<th>Soft Label</th>
</tr>
</thead>
<tbody><tr>
<td>형태</td>
<td>확정된 정답</td>
<td>후보별 확률분포</td>
</tr>
<tr>
<td>예시</td>
<td>고양이 = 1, 나머지 = 0</td>
<td>고양이 0.7, 개 0.2, 여우 0.1</td>
</tr>
<tr>
<td>정보</td>
<td>정답 자체</td>
<td>정답과 후보 간 관계</td>
</tr>
<tr>
<td>특징</td>
<td>정보량이 적음</td>
<td>Teacher의 판단 정보 포함</td>
</tr>
</tbody></table>
<hr />
<h2 id="llm에서의-distillation">LLM에서의 Distillation</h2>
<p>LLM에서는 Teacher Model이 질문에 대한 답변을 생성하고, 이를 이용해 작은 Student Model을 학습할 수 있다.</p>
<pre><code class="language-text">질문
→ Teacher Model
→ 고품질 답변 생성
→ Student Model Fine-Tuning</code></pre>
<p>추론 모델의 경우 Teacher가 생성한 문제 풀이 데이터나 단계적인 설명을 학습 데이터로 사용할 수도 있다.</p>
<pre><code class="language-text">문제
→ Teacher의 답변과 추론 데이터
→ Synthetic Reasoning Dataset
→ Student Model 학습</code></pre>
<p>강의 자료에서는 거대 추론 모델이 생성한 대량의 합성 추론 데이터를 이용하여 기존의 더 작은 오픈 모델을 Fine-Tuning하는 흐름을 Distillation 사례로 설명한다. </p>
<hr />
<h2 id="distillation의-장점">Distillation의 장점</h2>
<h3 id="더-작은-모델로-유사한-성능-확보">더 작은 모델로 유사한 성능 확보</h3>
<p>Student Model은 Teacher보다 파라미터 수가 적으므로 완전히 동일한 능력을 갖기는 어렵다.</p>
<p>하지만 특정 업무에서는 훨씬 작은 모델로도 Teacher에 가까운 성능을 확보할 수 있다.</p>
<hr />
<h3 id="빠른-추론">빠른 추론</h3>
<p>모델이 작아지면 다음과 같은 이점이 생긴다.</p>
<ul>
<li>응답 속도 향상</li>
<li>GPU 메모리 사용량 감소</li>
<li>동시 처리량 증가</li>
<li>요청당 비용 감소</li>
<li>모바일·엣지 환경 배포 가능성 증가</li>
</ul>
<hr />
<h3 id="학습-안정성과-일반화">학습 안정성과 일반화</h3>
<p>Soft Label은 단순한 정답 외에도 후보 간 유사성 정보를 제공한다.</p>
<p>Student가 정답 하나만 과도하게 외우는 것을 줄이고, 더 부드러운 의사결정 경계를 학습하는 데 도움을 줄 수 있다.</p>
<hr />
<h2 id="distillation에서-주의할-점">Distillation에서 주의할 점</h2>
<p>다음은 Distillation 구조에서 자연스럽게 따라오는 실무상 유의점이다.</p>
<h3 id="teacher의-오류도-전달된다">Teacher의 오류도 전달된다</h3>
<p>Teacher가 잘못된 답변, 편향 또는 환각을 생성하면 Student도 이를 학습할 수 있다.</p>
<pre><code class="language-text">Teacher의 잘못된 지식
→ 합성 데이터에 포함
→ Student가 반복 학습</code></pre>
<p>따라서 Teacher가 생성한 데이터라고 해서 무조건 정답으로 취급하면 안 된다.</p>
<p>가능하다면 규칙, 정답 데이터, 외부 검증기 또는 전문가 검수로 품질을 확인해야 한다.</p>
<hr />
<h3 id="작은-모델의-수용-능력에는-한계가-있다">작은 모델의 수용 능력에는 한계가 있다</h3>
<p>Student의 크기가 지나치게 작으면 Teacher가 가진 복잡한 지식을 모두 담을 수 없다.</p>
<pre><code class="language-text">Teacher의 능력
&gt; Student의 표현 능력

→ 일부 지식과 추론 능력 손실</code></pre>
<p>따라서 목표 업무에 필요한 성능과 배포 비용 사이에서 Student 크기를 결정해야 한다.</p>
<hr />
<h3 id="합성-데이터의-다양성이-필요하다">합성 데이터의 다양성이 필요하다</h3>
<p>Teacher가 비슷한 표현과 풀이 방식만 반복하면 Student의 출력도 단조로워질 수 있다.</p>
<p>다양한 난이도, 도메인, 표현 방식과 실패 사례를 포함해야 한다.</p>
<hr />
<h3 id="긴-설명이-항상-좋은-학습-데이터는-아니다">긴 설명이 항상 좋은 학습 데이터는 아니다</h3>
<p>Teacher가 생성한 추론 과정이 자연스럽고 길다는 사실만으로 정확하다고 볼 수는 없다.</p>
<p>추론 단계 사이에 오류가 없는지, 최종 답과 논리가 일치하는지 별도로 검증할 필요가 있다.</p>
<hr />
<h2 id="distillation의-핵심">Distillation의 핵심</h2>
<blockquote>
<p>Distillation은 거대 모델을 단순히 잘라내는 것이 아니라, Teacher가 학습한 출력과 판단 정보를 작은 Student에게 전달하는 과정이다.</p>
</blockquote>
<pre><code class="language-text">큰 모델의 능력
→ 학습 데이터와 Soft Label로 표현
→ 작은 모델에 전달
→ 더 낮은 비용으로 활용</code></pre>
<hr />
<h1 id="moe">MoE</h1>
<h2 id="모든-파라미터를-매번-사용할-필요가-있을까">모든 파라미터를 매번 사용할 필요가 있을까?</h2>
<p>일반적인 Dense Transformer에서는 하나의 토큰을 처리할 때 각 계층의 모든 파라미터가 계산에 참여한다.</p>
<pre><code class="language-text">입력 토큰
→ 전체 Transformer Layer 활성화
→ 모든 FFN 파라미터 사용
→ 출력</code></pre>
<p>모델의 파라미터 수가 증가하면 모델의 표현 능력은 커지지만, 토큰 하나를 처리하는 연산량도 함께 증가한다.</p>
<p>이를 개선하기 위해 등장한 구조가 <strong>MoE(Mixture of Experts)</strong>다.</p>
<hr />
<h2 id="필요한-전문가만-활성화한다">필요한 전문가만 활성화한다</h2>
<p>MoE는 여러 개의 Expert를 두고, 입력 토큰마다 적절한 Expert 일부만 선택해 계산한다.</p>
<pre><code class="language-text">입력 토큰
→ Router
→ 관련 Expert 선택
→ 선택된 Expert만 계산
→ 결과 결합</code></pre>
<p>여기서 Expert는 일반적으로 하나의 작은 완성형 LLM을 뜻하지 않는다.</p>
<p>Transformer 블록의 <strong>FFN 부분을 여러 개의 Expert FFN으로 구성한 것</strong>에 가깝다.</p>
<pre><code class="language-text">Dense Transformer

Attention
→ 하나의 FFN</code></pre>
<pre><code class="language-text">MoE Transformer

Attention
→ Router
→ Expert FFN 1
→ Expert FFN 2
→ Expert FFN 3
→ ...</code></pre>
<hr />
<h2 id="dense-model과-moe의-차이">Dense Model과 MoE의 차이</h2>
<h3 id="dense-model">Dense Model</h3>
<p>모든 토큰에 대해 모든 파라미터를 사용한다.</p>
<pre><code class="language-text">Token A → 전체 파라미터 사용
Token B → 전체 파라미터 사용
Token C → 전체 파라미터 사용</code></pre>
<h3 id="moe-model">MoE Model</h3>
<p>각 토큰에 대해 일부 Expert만 사용한다.</p>
<pre><code class="language-text">Token A → Expert 1, Expert 3
Token B → Expert 2, Expert 4
Token C → Expert 1, Expert 4</code></pre>
<p>따라서 전체 파라미터 수는 매우 크더라도, 토큰 하나를 처리할 때 실제로 활성화되는 파라미터 수는 상대적으로 작게 유지할 수 있다.</p>
<hr />
<h2 id="router의-동작">Router의 동작</h2>
<p>Router는 입력 토큰이 어떤 Expert로 이동할지를 결정하는 작은 신경망이다.</p>
<p>입력 토큰 벡터 (x)가 들어오면 각 Expert에 대한 점수를 계산한다.</p>
<pre><code class="language-text">입력 토큰 x
→ Router
→ Expert별 Score 계산</code></pre>
<p>점수에 Softmax를 적용하면 각 Expert를 선택할 확률이 만들어진다.</p>
<pre><code class="language-text">Expert 1: 0.05
Expert 2: 0.70
Expert 3: 0.10
Expert 4: 0.15</code></pre>
<p>이 가운데 확률이 높은 <code>Top-k</code> 또는 <code>Top-n</code> Expert만 활성화한다.</p>
<pre><code class="language-text">Top-2 선택

Expert 2 활성화
Expert 4 활성화
나머지 Expert 비활성화</code></pre>
<p>선택된 Expert의 출력은 Router가 계산한 비중에 따라 결합된다.</p>
<pre><code class="language-text">Output
= Expert 2 결과 × 0.70
+ Expert 4 결과 × 0.15</code></pre>
<p>Router도 학습 가능한 작은 신경망이므로, 학습 과정에서 입력 토큰을 어떤 Expert로 보낼지 함께 학습한다.</p>
<hr />
<h2 id="expert는-어떻게-전문화될까">Expert는 어떻게 전문화될까?</h2>
<p>초기에는 각 Expert가 뚜렷한 전문 분야를 가지고 있지 않다.</p>
<p>하지만 학습이 진행되면서 Router가 비슷한 특징의 토큰을 반복적으로 같은 Expert에 보내게 된다.</p>
<pre><code class="language-text">비슷한 입력
→ 같은 Expert로 Routing
→ 해당 패턴을 반복 학습
→ Expert 전문화</code></pre>
<p>그 결과 일부 Expert는 특정 언어, 코드, 수학적 패턴 또는 특정 표현 방식에 상대적으로 강해질 수 있다.</p>
<p>다만 Expert가 사람이 이해할 수 있는 명확한 분야별 전문가로 반드시 나뉘는 것은 아니다.</p>
<p>Expert의 전문성은 학습 과정에서 형성되는 내부적인 패턴 분리로 이해하는 편이 적절하다.</p>
<hr />
<h2 id="moe의-장점">MoE의 장점</h2>
<h3 id="전체-모델-용량-확대">전체 모델 용량 확대</h3>
<p>실제로 활성화되는 연산량을 제한하면서 전체 파라미터 수를 크게 늘릴 수 있다.</p>
<pre><code class="language-text">많은 전체 파라미터
+
적은 활성 파라미터
=
큰 모델 용량과 계산 효율의 절충</code></pre>
<hr />
<h3 id="토큰당-연산량-절감">토큰당 연산량 절감</h3>
<p>Dense Model은 모든 파라미터를 사용하지만, MoE는 선택된 일부 Expert만 계산한다.</p>
<p>따라서 같은 전체 파라미터 규모의 Dense Model과 비교했을 때 토큰당 계산량을 줄일 수 있다.</p>
<hr />
<h3 id="다양한-패턴-학습">다양한 패턴 학습</h3>
<p>여러 Expert가 서로 다른 특징을 학습할 수 있으므로, 하나의 FFN이 모든 패턴을 처리하는 것보다 모델 용량을 다양하게 사용할 수 있다.</p>
<hr />
<h2 id="moe에서-주의할-점">MoE에서 주의할 점</h2>
<p>다음은 MoE 구조로부터 따라오는 대표적인 실무상 유의점이다.</p>
<h3 id="expert-쏠림-현상">Expert 쏠림 현상</h3>
<p>Router가 일부 Expert만 계속 선택하면 특정 Expert에 요청이 몰릴 수 있다.</p>
<pre><code class="language-text">Expert 1: 거의 사용되지 않음
Expert 2: 요청 과다
Expert 3: 거의 사용되지 않음
Expert 4: 요청 과다</code></pre>
<p>이렇게 되면 일부 Expert만 학습되고 나머지는 제대로 활용되지 않는다.</p>
<p>이를 완화하기 위해 Expert 사용량을 고르게 만들기 위한 <strong>Load Balancing Loss</strong> 등의 추가 제약이 필요할 수 있다.</p>
<hr />
<h3 id="expert-collapse">Expert Collapse</h3>
<p>여러 Expert가 존재하지만 실제로는 비슷한 기능만 학습하거나 일부 Expert만 사용되는 문제가 생길 수 있다.</p>
<p>MoE가 의도한 전문화와 용량 확대 효과를 얻으려면 Router와 Expert가 균형 있게 학습되어야 한다.</p>
<hr />
<h3 id="통신-비용">통신 비용</h3>
<p>Expert가 여러 GPU나 서버에 분산되어 있다면 토큰을 해당 Expert가 있는 장치로 전달해야 한다.</p>
<pre><code class="language-text">GPU 1의 토큰
→ Router 판단
→ GPU 4의 Expert로 전송
→ 계산
→ 다시 결과 반환</code></pre>
<p>계산량은 줄어들더라도 장치 간 데이터 통신이 병목이 될 수 있다.</p>
<hr />
<h3 id="전체-파라미터는-메모리에-존재한다">전체 파라미터는 메모리에 존재한다</h3>
<p>MoE는 모든 Expert를 매번 계산하지 않을 뿐, 전체 Expert의 파라미터 자체가 사라지는 것은 아니다.</p>
<p>따라서 다음 두 개념을 구분해야 한다.</p>
<pre><code class="language-text">Total Parameters
→ 모델 전체가 보유한 파라미터

Active Parameters
→ 토큰 처리 시 실제 계산에 참여한 파라미터</code></pre>
<p>MoE는 활성 연산량을 줄이는 데 유리하지만, 전체 모델을 저장하고 배치하기 위한 메모리와 시스템 설계는 여전히 복잡하다.</p>
<hr />
<h2 id="moe의-핵심">MoE의 핵심</h2>
<blockquote>
<p>MoE는 여러 Expert를 보유하되, 입력 토큰마다 Router가 필요한 일부 Expert만 선택해 사용하는 희소 활성화 구조다.</p>
</blockquote>
<pre><code class="language-text">Dense
→ 모든 토큰이 모든 파라미터 사용

MoE
→ 토큰마다 일부 Expert만 선택</code></pre>
<hr />
<h1 id="마무리">마무리</h1>
<p>Transformer는 토큰 사이의 관계를 효율적으로 계산할 수 있는 기반 구조를 제공했다.</p>
<p>그러나 현대 LLM의 발전은 Transformer 구조만으로 이루어진 것이 아니다.</p>
<pre><code class="language-text">Transformer
→ 문맥을 처리하는 모델 구조

Scaling Law
→ 모델·데이터·연산량의 균형

MoE
→ 큰 용량을 희소하게 사용하는 구조

RLHF
→ 사람의 의도와 선호에 맞춘 행동 정렬

Distillation
→ 거대 모델의 능력을 작은 모델로 전달</code></pre>
<p>결국 좋은 LLM을 만드는 과정은 단순히 파라미터를 늘리는 것이 아니다.</p>
<blockquote>
<p>얼마나 크게 학습할 것인지, 어떤 데이터를 사용할 것인지, 사람의 요구에 어떻게 맞출 것인지, 그리고 실제 서비스에서 어느 비용으로 실행할 것인지까지 함께 설계해야 한다.</p>
</blockquote>
<p>현대의 LLM은 <strong>더 크게 만드는 기술</strong>과 함께, <strong>더 올바르게 답하고 더 효율적으로 실행하기 위한 기술</strong>이 결합된 결과라고 볼 수 있다.</p>