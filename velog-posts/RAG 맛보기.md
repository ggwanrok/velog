<p>LLM은 학습된 지식을 바탕으로 답변을 생성하지만 모든 정보를 알고 있는 것은 아니다. 학습 이후 생성된 정보, 기업 내부 문서, 개인이 보유한 데이터와 같이 모델의 학습 범위 밖에 있는 정보에는 직접 접근할 수 없다.</p>
<p>이러한 한계를 보완하기 위한 대표적인 방법이 <strong>RAG(Retrieval-Augmented Generation)</strong> 이다.</p>
<p>RAG는 모델 자체를 다시 학습시키는 대신, 사용자의 질문과 관련된 외부 정보를 검색한 뒤 이를 질문과 함께 LLM에 전달한다.</p>
<pre><code class="language-text">사용자 질문
    ↓
관련 문서 검색
    ↓
질문 + 검색된 근거
    ↓
LLM
    ↓
근거 기반 답변</code></pre>
<p>즉 RAG의 핵심은 모델에게 새로운 지식을 기억시키는 것이 아니라 <strong>답변 시점에 필요한 지식을 찾아 Context로 제공하는 것</strong>이다.</p>
<hr />
<h1 id="rag의-기본-구조">RAG의 기본 구조</h1>
<p>RAG는 크게 문서를 준비하는 <strong>Ingest 과정</strong>과 실제 질문을 처리하는 <strong>Retrieval·Generation 과정</strong>으로 나눌 수 있다.</p>
<pre><code class="language-text">                [Ingest]

                원본 문서
                   ↓
                Reader
                   ↓
                Chunking
                   ↓
                Metadata
                   ↓
                Embedding
                   ↓
                VectorStore


             [Retrieval]

                사용자 질문
                   ↓
                Embedding
                   ↓
                Vector Search
                   ↓
                관련 Chunk


             [Generation]

                질문 + 관련 Chunk
                   ↓
                  LLM
                   ↓
                  답변</code></pre>
<p>먼저 PDF, 문서, 사내 규정 등의 데이터를 읽은 뒤 검색하기 적절한 크기의 Chunk로 분할한다.</p>
<p>각 Chunk는 Embedding Model을 통해 의미를 표현하는 Vector로 변환되고 VectorStore에 저장된다.</p>
<pre><code class="language-text">&quot;퇴직자는 회사에서 지급받은 장비를 반환해야 한다.&quot;

            ↓

[0.13, -0.42, 0.81, ...]</code></pre>
<p>질문 역시 같은 방식으로 Vector로 변환된다.</p>
<p>이후 VectorStore에서는 질문과 의미적으로 가까운 Chunk를 검색한다.</p>
<pre><code class="language-text">질문
&quot;퇴사할 때 회사 노트북을 어떻게 돌려줘?&quot;

                ↓

Vector Search

                ↓

&quot;퇴직자는 지급받은 업무용 장비를 반환해야 한다.&quot;</code></pre>
<p>문자열이 완전히 일치하지 않더라도 의미가 비슷한 문서를 검색할 수 있다는 것이 Vector Search의 핵심이다.</p>
<p>검색된 Chunk는 사용자 질문과 함께 LLM에 전달된다.</p>
<pre><code class="language-text">[Context]

퇴직자는 지급받은 업무용 장비를
퇴직일까지 반환해야 한다.

[Question]

퇴사할 때 노트북은 언제까지 반납해야 하나요?</code></pre>
<p>따라서 RAG는 본질적으로 다음 두 기능의 결합이라고 볼 수 있다.</p>
<pre><code class="language-text">Retrieval
→ 답변에 필요한 근거를 찾는다.

Generation
→ 찾은 근거를 바탕으로 답변한다.</code></pre>
<hr />
<h1 id="spring-ai로-구현하는-기본-rag">Spring AI로 구현하는 기본 RAG</h1>
<p>Spring AI는 RAG를 구성하는 요소들을 Spring 애플리케이션에서 사용할 수 있도록 추상화한다.</p>
<pre><code class="language-text">문서 읽기           → DocumentReader
문서 분할           → TextSplitter
임베딩              → EmbeddingModel
벡터 저장·검색      → VectorStore
RAG 처리            → Advisor
LLM 호출            → ChatClient</code></pre>
<p>덕분에 개발자는 각 모델이나 Vector DB의 세부 API를 직접 연결하기보다 <strong>RAG Pipeline의 구성 자체에 집중할 수 있다.</strong></p>
<h2 id="문서를-vectorstore에-저장하기">문서를 VectorStore에 저장하기</h2>
<p>가장 기본적인 Ingest 코드는 다음과 같이 구성할 수 있다.</p>
<pre><code class="language-java">@Service
@RequiredArgsConstructor
public class IngestService {

    private final VectorStore vectorStore;

    public void ingest(Resource file) {

        // Read
        List&lt;Document&gt; documents =
                new TikaDocumentReader(file).get();

        // Split
        var splitter = TokenTextSplitter.builder()
                .withChunkSize(800)
                .build();

        List&lt;Document&gt; chunks =
                splitter.apply(documents);

        // Embed + Store
        vectorStore.add(chunks);
    }
}</code></pre>
<p>코드는 간단하지만 실제 흐름은 다음과 같다.</p>
<pre><code class="language-text">DocumentReader
      ↓
Document
      ↓
TextSplitter
      ↓
Chunk
      ↓
EmbeddingModel
      ↓
VectorStore</code></pre>
<p><code>vectorStore.add()</code>를 호출하면 연결되어 있는 Embedding Model을 통해 Document를 Vector로 변환하고 저장하는 과정이 수행된다.</p>
<p>필요하다면 이 과정에서 Metadata를 함께 저장할 수 있다.</p>
<pre><code class="language-java">metadata.put(&quot;source&quot;, file.getFilename());
metadata.put(&quot;documentId&quot;, documentId);
metadata.put(&quot;department&quot;, department);
metadata.put(&quot;version&quot;, version);
metadata.put(&quot;chunkIndex&quot;, chunkIndex);</code></pre>
<p>Metadata는 나중에 특정 문서나 부서, 버전 등으로 검색 범위를 제한하거나 출처를 표시하는 데 활용할 수 있다.</p>
<hr />
<h2 id="질문을-rag로-처리하기">질문을 RAG로 처리하기</h2>
<p>Spring AI에서는 <code>QuestionAnswerAdvisor</code>를 이용해 기본적인 Retrieval과 Context 주입 과정을 추상화할 수 있다.</p>
<pre><code class="language-java">@Configuration
public class AiConfig {

    @Bean
    public ChatClient chatClient(
            ChatClient.Builder builder,
            VectorStore vectorStore) {

        return builder
                .defaultSystem(&quot;&quot;&quot;
                    제공된 문서를 근거로 답변하세요.
                    근거가 없다면 모른다고 답하세요.
                    &quot;&quot;&quot;)
                .defaultAdvisors(
                        QuestionAnswerAdvisor.builder(vectorStore)
                                .build()
                )
                .build();
    }
}</code></pre>
<p>이후 Service에서는 일반적인 <code>ChatClient</code> 호출만 수행한다.</p>
<pre><code class="language-java">@Service
@RequiredArgsConstructor
public class RagService {

    private final ChatClient chatClient;

    public String ask(String question) {

        return chatClient.prompt()
                .user(question)
                .call()
                .content();
    }
}</code></pre>
<p>애플리케이션 코드에서는 단순한 모델 호출처럼 보이지만 내부에서는 다음 흐름이 수행된다.</p>
<pre><code class="language-text">사용자 질문
      ↓
ChatClient
      ↓
QuestionAnswerAdvisor
      ↓
VectorStore 검색
      ↓
관련 Chunk
      ↓
질문 + Context
      ↓
ChatModel
      ↓
답변</code></pre>
<p>즉 Spring AI의 장점은 RAG라는 기술을 숨기는 데 있는 것이 아니라, <strong>RAG의 각 구성 요소를 Spring 방식으로 조립할 수 있도록 추상화한다는 점</strong>에 있다.</p>
<hr />
<h1 id="기본형-rag가-가지는-한계">기본형 RAG가 가지는 한계</h1>
<p>기본 RAG를 가장 단순하게 표현하면 다음과 같다.</p>
<pre><code class="language-text">사용자 질문
     ↓
Vector Search
     ↓
Top-K Chunk
     ↓
LLM</code></pre>
<p>구조는 간단하지만 실제 서비스에서는 이 과정 곳곳에서 검색 실패가 발생할 수 있다.</p>
<p>문제는 크게 다섯 가지 지점에서 발생한다.</p>
<pre><code class="language-text">문서가 검색하기 좋지 않다.
          ↓
질문이 검색하기 좋지 않다.
          ↓
검색 방식이 질문에 적합하지 않다.
          ↓
검색 결과의 품질이 좋지 않다.
          ↓
단순한 유사도 검색만으로 해결하기 어려운 질문이 존재한다.</code></pre>
<p>RAG 고도화는 이 문제들을 하나씩 해결하는 과정이라고 볼 수 있다.</p>
<hr />
<h1 id="modular-rag---rag를-단계별로-바라보기">Modular RAG - RAG를 단계별로 바라보기</h1>
<p>기본형 RAG의 한계를 개선하려면 RAG를 하나의 고정된 검색 과정으로 보기보다, <strong>각각 독립적으로 조정할 수 있는 여러 단계의 파이프라인</strong>으로 바라볼 필요가 있다.</p>
<p>이를 다음과 같이 구분할 수 있다.</p>
<pre><code class="language-text">Ingest
   ↓
Pre-Retrieval
   ↓
Retrieval
   ↓
Post-Retrieval
   ↓
Generation</code></pre>
<p>각 단계가 담당하는 문제는 서로 다르다.</p>
<pre><code class="language-text">Ingest
→ 어떤 형태의 문서를 검색 대상으로 만들 것인가

Pre-Retrieval
→ 사용자의 질문을 어떤 형태로 검색할 것인가

Retrieval
→ 어떤 방식으로 관련 문서를 찾을 것인가

Post-Retrieval
→ 검색된 후보 중 어떤 근거를 사용할 것인가

Generation
→ 선택된 근거를 이용해 어떻게 답변할 것인가</code></pre>
<p>이처럼 RAG를 여러 모듈로 분리하면 검색 품질이 낮을 때 전체 구조를 한꺼번에 변경할 필요가 없다.</p>
<p>문서 자체의 구조가 문제라면 <strong>Chunking, Contextual Retrieval, Parent-Child Retrieval</strong>을 조정할 수 있고, 질문이 검색에 적합하지 않다면 <strong>Rewrite, MultiQuery, HyDE</strong>와 같은 Query Transformation을 적용할 수 있다.</p>
<p>검색 방식의 한계라면 <strong>Metadata Filter나 Hybrid Search</strong>를 고려할 수 있으며, 검색에는 성공했지만 결과의 품질이 낮다면 <strong>MMR이나 Re-ranking</strong>을 통해 후보를 다시 선별할 수 있다.</p>
<p>더 나아가 한 번의 고정된 검색으로 충분한 근거를 확보하기 어렵다면 <strong>Agentic RAG</strong>를 통해 검색 과정을 동적으로 확장할 수 있고, 여러 정보 사이의 관계를 따라가야 하는 질의라면 <strong>GraphRAG</strong>와 같은 별도의 검색 구조를 고려할 수 있다.</p>
<p>즉 RAG의 고도화는 새로운 기능을 무작정 추가하는 것이 아니라,</p>
<blockquote>
<p><strong>검색 실패가 발생하는 지점을 파악하고 해당 단계를 선택적으로 개선하는 과정</strong></p>
</blockquote>
<p>이라고 볼 수 있다.</p>
<hr />
<h2 id="문서가-검색하기-좋지-않다면">문서가 검색하기 좋지 않다면</h2>
<p>검색 품질은 질문이 들어온 순간부터 결정되는 것이 아니다.</p>
<p><strong>어떤 Chunk를 VectorStore에 저장했는지</strong>가 Retrieval의 출발점이 된다.</p>
<h3 id="chunking-전략">Chunking 전략</h3>
<p>Chunk가 지나치게 작으면 문맥이 사라진다.</p>
<pre><code class="language-text">Chunk A
&quot;계약을 해지할 수 있다.&quot;

Chunk B
&quot;단, 서면 통보 후 14일이 경과해야 한다.&quot;</code></pre>
<p>반대로 지나치게 크면 검색에 필요하지 않은 정보까지 함께 포함된다.</p>
<pre><code class="language-text">계약 기간
계약 해지
손해배상
비밀유지
개인정보</code></pre>
<p>따라서 문서를 단순히 동일한 길이로 나누기보다 문서 구조를 고려하는 것이 중요하다.</p>
<pre><code class="language-text">FAQ
→ 질문 + 답변

일반 문서
→ 문장 / 문단

계약서
→ 조항

규정
→ 장 / 절 / 조

기술 문서
→ Section</code></pre>
<p>즉 Chunking은 단순한 전처리가 아니라 <strong>검색 단위를 설계하는 과정</strong>이다.</p>
<hr />
<h3 id="contextual-retrieval">Contextual Retrieval</h3>
<p>Chunking 과정에서 문맥이 사라지는 문제를 보완하는 방식이다.</p>
<p>다음 Chunk만 저장되어 있다고 하자.</p>
<pre><code class="language-text">&quot;이 경우에는 14일 이내에 반환해야 한다.&quot;</code></pre>
<p>문장만 보면 무엇을 반환한다는 것인지 알기 어렵다.</p>
<p>따라서 문서의 Context를 함께 붙여 저장할 수 있다.</p>
<pre><code class="language-text">[퇴직자 자산 반납 규정]

본 문서는 퇴직자가 회사에서 지급받은
업무용 장비를 반환하는 절차를 설명한다.

이 경우에는 14일 이내에 반환해야 한다.</code></pre>
<p>즉 <strong>질문을 수정하는 것이 아니라 검색 대상인 Chunk 자체를 검색하기 좋은 형태로 개선하는 방법</strong>이다.</p>
<hr />
<h3 id="parent-child-retrieval">Parent-Child Retrieval</h3>
<p>Chunk에는 구조적인 Trade-off가 존재한다.</p>
<pre><code class="language-text">작은 Chunk
→ 검색에는 유리
→ 문맥은 부족

큰 Chunk
→ 문맥은 풍부
→ 검색 정밀도는 감소</code></pre>
<p>Parent-Child Retrieval은 검색 단위와 LLM에 전달할 단위를 분리하여 이 문제를 해결한다.</p>
<pre><code class="language-text">Parent

├─ Child
├─ Child
├─ Child
└─ Child</code></pre>
<p>검색은 작은 Child를 사용한다.</p>
<pre><code class="language-text">질문
 ↓
Child 검색</code></pre>
<p>검색된 Child의 <code>parentId</code>를 이용해 더 큰 Parent를 가져와 LLM에 전달한다.</p>
<pre><code class="language-text">Child
 ↓
parentId
 ↓
Parent
 ↓
LLM</code></pre>
<p>즉,</p>
<blockquote>
<p><strong>검색은 작은 단위로 정밀하게 수행하고, 생성에는 충분한 문맥을 제공한다.</strong></p>
</blockquote>
<hr />
<h2 id="질문이-검색하기-좋지-않다면">질문이 검색하기 좋지 않다면</h2>
<p>사용자가 항상 검색 시스템이 이해하기 좋은 질문을 작성하는 것은 아니다.</p>
<p>따라서 실제 검색 전에 Query 자체를 보정할 수 있다.</p>
<h3 id="query-rewrite">Query Rewrite</h3>
<p>다음과 같은 질문은 그대로 검색하기 어렵다.</p>
<pre><code class="language-text">&quot;그럼 퇴사할 때는?&quot;</code></pre>
<p>이전 대화의 문맥을 이용해 다음과 같이 복원한다.</p>
<pre><code class="language-text">&quot;퇴사 시 회사에서 지급받은 노트북은
언제까지 반납해야 하는가?&quot;</code></pre>
<p>흐름은 단순하다.</p>
<pre><code class="language-text">사용자 질문
    ↓
Rewrite
    ↓
검색 가능한 Query
    ↓
VectorStore</code></pre>
<p>Spring AI에서는 <code>RewriteQueryTransformer</code>와 같은 구성 요소를 통해 이러한 Query 변환 과정을 Retrieval Pipeline에 넣을 수 있다.</p>
<hr />
<h3 id="multiquery">MultiQuery</h3>
<p>하나의 질문을 여러 관점으로 표현하여 검색한다.</p>
<pre><code class="language-text">&quot;회사 노트북 반납 규정&quot;

        ↓

&quot;퇴사 시 노트북 반환 절차&quot;

&quot;회사 자산 반납 기한&quot;

&quot;업무 장비 반환 정책&quot;</code></pre>
<p>각 Query가 서로 다른 문서를 찾을 수 있으므로 하나의 표현에 의존하는 것보다 관련 근거를 놓칠 가능성이 줄어든다.</p>
<pre><code class="language-text">            질문
             ↓
          MultiQuery
       ┌─────┼─────┐
       ↓     ↓     ↓
     Query Query Query
       ↓     ↓     ↓
     검색   검색   검색
       └─────┼─────┘
             ↓
          결과 통합</code></pre>
<p>Spring AI에서는 <code>MultiQueryExpander</code>를 통해 이러한 구조를 조립할 수 있다.</p>
<hr />
<h3 id="hyde">HyDE</h3>
<p>HyDE는 조금 다른 접근을 사용한다.</p>
<p>사용자 질문을 바로 검색하지 않고 <strong>LLM에게 가상의 답변을 먼저 만들게 한 뒤, 그 답변으로 검색한다.</strong></p>
<pre><code class="language-text">질문
 ↓
LLM
 ↓
가상의 답변
 ↓
Embedding
 ↓
Vector Search</code></pre>
<p>예를 들어 사용자는 다음과 같이 물어볼 수 있다.</p>
<pre><code class="language-text">&quot;물건 돌려보내려면 며칠 안에 해야 해요?&quot;</code></pre>
<p>실제 문서는 다음처럼 표현되어 있을 수 있다.</p>
<pre><code class="language-text">&quot;상품의 반품 신청은 수령일로부터 7일 이내 가능하다.&quot;</code></pre>
<p>사용자의 구어체 질문보다 LLM이 생성한 가상의 답변이 문서 표현과 더 가까울 수 있다.</p>
<p>HyDE의 가상 답변은 최종 답으로 사용되지 않는다.</p>
<p><strong>검색을 위한 중간 표현</strong>으로만 사용된다.</p>
<hr />
<h2 id="검색-방법-자체가-적합하지-않다면">검색 방법 자체가 적합하지 않다면</h2>
<p>질문을 잘 만들더라도 Vector Search 하나만으로 모든 검색 문제를 해결할 수는 없다.</p>
<h3 id="metadata-filter">Metadata Filter</h3>
<p>질문과 관련된 모든 Vector를 탐색할 필요가 없는 경우 먼저 Metadata를 통해 검색 범위를 제한할 수 있다.</p>
<pre><code class="language-text">전체 VectorStore

      ↓

department = CS
version = 2026

      ↓

Vector Search</code></pre>
<p>특히 사용자 권한이나 특정 문서 집합을 구분해야 한다면 Metadata Filter는 단순한 검색 최적화를 넘어 <strong>검색 가능 범위를 제어하는 장치</strong>가 된다.</p>
<hr />
<h3 id="hybrid-search">Hybrid Search</h3>
<p>Vector Search는 의미 검색에는 강하지만 정확한 문자열에는 상대적으로 취약할 수 있다.</p>
<pre><code class="language-text">SKA-3928
제17조
RFC-9457</code></pre>
<p>이런 값들은 의미보다 정확한 일치가 중요하다.</p>
<p>반대로 Keyword Search는 정확한 문자열에는 강하지만 비슷한 의미의 표현을 찾는 데 한계가 있다.</p>
<p>따라서 두 검색 방식을 결합할 수 있다.</p>
<pre><code class="language-text">                 Query
                  │
       ┌──────────┴──────────┐
       ↓                     ↓
 Keyword Search         Vector Search
       │                     │
       └──────────┬──────────┘
                  ↓
              결과 통합</code></pre>
<p>예를 들어</p>
<pre><code class="language-text">&quot;SKA-3928 배터리 교체 방법&quot;</code></pre>
<p>이라는 질문은</p>
<pre><code class="language-text">SKA-3928
→ Keyword Search

배터리 교체 방법
→ Vector Search</code></pre>
<p>두 특징을 모두 포함한다.</p>
<p>Hybrid Search는 <strong>정확한 단어 검색과 의미 검색의 장점을 결합하는 전략</strong>이다.</p>
<hr />
<h2 id="문서는-찾았지만-결과-품질이-좋지-않다면">문서는 찾았지만 결과 품질이 좋지 않다면</h2>
<p>Retrieval은 성공했지만 상위 결과가 반드시 LLM에 전달하기 가장 좋은 Context라는 보장은 없다.</p>
<p>이 경우 검색 후처리 단계에서 결과를 다시 다듬을 수 있다.</p>
<h3 id="mmr">MMR</h3>
<p>유사도만 기준으로 Top-K를 가져오면 비슷한 문서들이 결과를 독점할 수 있다.</p>
<pre><code class="language-text">휴가 규정 원문
휴가 규정 요약
휴가 규정 FAQ
휴가 규정 복사본</code></pre>
<p>검색 결과는 네 개지만 사실상 같은 내용일 수 있다.</p>
<p>MMR(Maximal Marginal Relevance)은</p>
<pre><code class="language-text">질문과의 관련성
+
결과 간 다양성</code></pre>
<p>을 함께 고려한다.</p>
<pre><code class="language-text">휴가 대상
휴가 기간
신청 절차
급여
복직 절차</code></pre>
<p>처럼 보다 다양한 근거를 구성할 수 있다.</p>
<hr />
<h3 id="re-ranking">Re-ranking</h3>
<p>Vector Search의 순위가 실제 질문에 가장 유용한 순위와 동일하지 않을 수도 있다.</p>
<p>따라서 먼저 후보를 넓게 가져온다.</p>
<pre><code class="language-text">Vector Search
 ↓
Top 20</code></pre>
<p>그다음 별도의 Re-ranker로 다시 평가한다.</p>
<pre><code class="language-text">Top 20
 ↓
Re-ranking
 ↓
Top 4
 ↓
LLM</code></pre>
<p>Vector Search는 <strong>빠르게 후보를 찾는 역할</strong>, Re-ranker는 <strong>후보 중 실제로 중요한 근거를 선별하는 역할</strong>을 담당한다.</p>
<p>즉,</p>
<blockquote>
<p><strong>넓게 찾고, 좁게 넣는다.</strong></p>
</blockquote>
<p>라는 방식이다.</p>
<hr />
<h2 id="한-번의-검색으로-해결하기-어렵다면">한 번의 검색으로 해결하기 어렵다면</h2>
<p>지금까지의 방식은 개발자가 미리 정한 Pipeline을 따라간다.</p>
<pre><code class="language-text">질문
→ 변환
→ 검색
→ 정렬
→ 답변</code></pre>
<p>그러나 어떤 질문은 첫 번째 검색 결과만으로 충분한 답을 얻기 어렵다.</p>
<h3 id="agentic-rag">Agentic RAG</h3>
<p>Agentic RAG는 문서 검색을 LLM이 사용할 수 있는 Tool로 제공한다.</p>
<pre><code class="language-text">사용자 질문
      ↓
LLM
      ↓
검색 필요 판단
      ↓
Search Tool
      ↓
검색 결과
      ↓
충분한가?
 ├─ Yes → 답변
 │
 └─ No
      ↓
  Query 변경
      ↓
    재검색</code></pre>
<p>기본 RAG의 고정된 검색 과정을 <strong>상황에 따라 반복 가능한 검색 과정으로 확장한 형태</strong>이다.</p>
<hr />
<h2 id="단순-유사도가-아니라-관계를-찾아야-한다면">단순 유사도가 아니라 관계를 찾아야 한다면</h2>
<p>Vector RAG는 의미적으로 가까운 정보를 찾는 데 적합하다.</p>
<p>하지만 다음과 같은 질문은 성격이 다르다.</p>
<pre><code class="language-text">&quot;A팀 담당자의 상급자는 누구인가?&quot;</code></pre>
<p>문서가 다음과 같이 흩어져 있다고 가정해보자.</p>
<pre><code class="language-text">A팀 담당자 → 김철수

김철수 소속 → 플랫폼개발부

플랫폼개발부장 → 이영희</code></pre>
<p>정답을 만들기 위해서는 하나의 문서를 찾는 것이 아니라 여러 관계를 따라가야 한다.</p>
<h3 id="graphrag">GraphRAG</h3>
<p>GraphRAG는 문서에서 Entity와 Relationship을 추출하여 다음과 같은 구조로 표현한다.</p>
<pre><code class="language-text">[A팀]
  ↓ 담당자
[김철수]
  ↓ 소속
[플랫폼개발부]
  ↓ 부장
[이영희]</code></pre>
<p>따라서 여러 관계를 연결해야 하는 <strong>Multi-hop 질의</strong>에 적합하다.</p>
<pre><code class="language-text">일반적인 사실 검색
→ Vector RAG

여러 Entity의 관계 추적
→ GraphRAG</code></pre>
<p>다만 Graph 구축과 관리 비용이 추가되므로 GraphRAG가 Vector RAG의 단순한 상위 버전인 것은 아니다.</p>
<p><strong>질문의 성격이 관계 중심일 때 선택하는 별도의 Retrieval 전략</strong>에 가깝다.</p>
<hr />
<h1 id="rag-고도화의-전체-구조">RAG 고도화의 전체 구조</h1>
<p>결국 여러 고도화 기법은 하나의 거대한 RAG에 모두 넣기 위한 기능이 아니다.</p>
<p>각각 <strong>서로 다른 검색 실패를 해결하기 위한 방법</strong>이다.</p>
<pre><code class="language-text">                    사용자 질문

                         │
                         ▼

                질문이 불완전한가?
             Rewrite / MultiQuery / HyDE

                         │
                         ▼

                검색 대상이 나쁜가?
       Chunking / Contextual / Parent-Child

                         │
                         ▼

               검색 방법이 부적절한가?
        Metadata Filter / Hybrid Search

                         │
                         ▼

              검색 결과 품질이 낮은가?
                 MMR / Re-ranking

                         │
                         ▼

               추가 검색이 필요한가?
                    Agentic RAG

                         │
                         ▼

              관계 추적이 필요한가?
                     GraphRAG

                         │
                         ▼

                        LLM</code></pre>
<p>따라서 RAG 고도화의 핵심은 기술을 많이 적용하는 것이 아니다.</p>
<pre><code class="language-text">질문이 애매하다
→ Rewrite

하나의 표현으로 문서를 놓친다
→ MultiQuery

질문과 문서 표현의 차이가 크다
→ HyDE

Chunk 자체의 문맥이 부족하다
→ Contextual Retrieval

검색 정밀도와 문맥을 모두 확보하고 싶다
→ Parent-Child

제품 코드나 고유명사를 놓친다
→ Hybrid Search

검색 결과가 지나치게 중복된다
→ MMR

정답 문서는 찾았지만 순위가 낮다
→ Re-ranking

검색 결과가 부족하면 다시 찾아야 한다
→ Agentic RAG

여러 관계를 연결해야 한다
→ GraphRAG</code></pre>
<p>처럼 <strong>검색 실패의 원인을 먼저 확인하고 해당 단계만 보완하는 것</strong>이 핵심이다.</p>
<hr />
<h1 id="마무리">마무리</h1>
<p>기본 RAG의 구조 자체는 단순하다.</p>
<pre><code class="language-text">문서를 검색 가능한 형태로 저장한다.
        ↓
질문과 관련된 문서를 찾는다.
        ↓
검색된 근거와 질문을 LLM에 전달한다.
        ↓
근거 기반 답변을 생성한다.</code></pre>
<p>Spring AI에서는 이를 <code>DocumentReader</code>, <code>TextSplitter</code>, <code>EmbeddingModel</code>, <code>VectorStore</code>, <code>Advisor</code>, <code>ChatClient</code>와 같은 추상화를 통해 Spring 애플리케이션 안에서 간결하게 구성할 수 있다.</p>
<p>그러나 실제 RAG의 완성도는 단순히 VectorStore와 LLM을 연결했다고 확보되는 것이 아니다.</p>
<p>문서의 Chunk 구조부터 질문의 표현, 검색 방식, 검색 결과의 선별 방법까지 여러 단계가 최종 품질에 영향을 준다.</p>
<p>따라서 RAG를 단순한 <strong>검색 + LLM 호출</strong>로 보기보다,</p>
<blockquote>
<p><strong>좋은 근거를 만들고, 좋은 방식으로 찾고, 필요한 근거만 선택하여 모델에 전달하는 검색 파이프라인</strong></p>
</blockquote>
<p>으로 이해하는 것이 중요하다.</p>
<p>좋은 RAG는 많은 정보를 LLM에게 전달하는 시스템이 아니다.</p>
<p><strong>사용자의 질문에 필요한 정보를 정확하게 찾아 필요한 만큼 전달하는 시스템이다.</strong></p>