<h2 id="msa-설계에서-실질적으로-다-다뤄야-할-것">MSA 설계에서 실질적으로 다 다뤄야 할 것.</h2>
<p>앞서 이벤트 스토밍을 통해서 기본적인 형태의 마이크로서비스를 구상하는 것까지 다뤄보았다.</p>
<p>이제 그렇게 분석된 마이크로서비스가 실질적으로 유용한 마이크로서비스가 되기 위해서 거치면 좋은 경로를 알아보자.</p>
<h3 id="depth-분석">Depth 분석</h3>
<p>마이크로서비스 도출의 완성도를 높이기 위해선 부가적인 작업들을 수행해야 한다.</p>
<h4 id="업무기능-분해">업무기능 분해</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a6d1a688-1a3a-4194-bdb2-52d588e76329/image.png" /></p>
<ul>
<li>앞서 분석된 마이크로서비스로 그래프나, depth표를 만들어 본다.</li>
<li>요구사항들을 하위레벨까지 내려 depth를 확인한다.<ul>
<li>각 기능에 대한 하위레벨을 자세하게 확인하여 혹여나 각 엔티티들이 가지는 <strong>연관성</strong>을 따진다.</li>
</ul>
</li>
</ul>
<blockquote>
<p>이 작업을 통해서 depth를 확인하여 연관성까지 따져본다면, 
이렇게 구성된 depth표만으로도 화면 구성에 대한 설계가지 얼추 완료했다고 볼 수 있다.</p>
</blockquote>
<ul>
<li>depth 분류작업 예시)
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/08609478-9b1b-418b-9c0c-3a0b37a5e558/image.png" /></li>
</ul>
<h3 id="연계-task-구상">연계 Task 구상</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fc0087d3-0512-464b-8e08-6e01067d36ae/image.png" /></p>
<p>마이크로서비스와 연계될 내부/외부 서비스를 따져봐야 한다.</p>
<ul>
<li>만약 지도가 필요하다면, 외부 지도 api는 뭘 사용할 것인지 등..</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/46aee10b-5c0a-408e-9118-c6d37445cbfb/image.png" /></p>
<p>또한 캐시나 관리형 데이터베이스는 무엇을 사용할 것인지 등을 따져봐야하며,</p>
<p>설계한 마이크로서비스를 섬세하게 분석해봐야 한다.</p>
<h3 id="트랜잭션-분석">트랜잭션 분석</h3>
<h4 id="crud를-고려해야-하는-이유">CRUD를 고려해야 하는 이유</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/bc6d852b-06c9-4a02-80d9-400cde1889a6/image.png" /></p>
<ul>
<li><strong>읽기는 빨라야 하고, 쓰기는 정확해야 한다.</strong></li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/66852355-f231-4ca8-bf92-ac796e7f3bd9/image.png" /></p>
<ul>
<li>단순 바운디드 컨텍스트 기반의 마이크로서비스를 구현한다면, 그것은 여러 조각으로 세분화된 <strong>모놀리식 서비스</strong>와 다를 것이 없다.<ul>
<li>물론 이렇게 분할하게 되면서 추가적으로 고려해야할 내용(예: 써킷 브레이커)들이 생기지만, 그럼에도 불구하고 고려해야한다.</li>
</ul>
</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/54b4454b-5e9e-4240-81ec-b8e24801664d/image.png" /></p>
<ul>
<li>배포의 빈도 또한 쓰기가 훨씬 높다. 읽기는 보통 바뀌더라도 프론트만 깔짝 바뀌고 퉁치는 경향이 크다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9fccde59-ddda-44e2-88a4-bbdfa03a38b7/image.png" /></p>
<ul>
<li>Read는 트래픽이 몰릴 경우 스케일 아웃에 최적화된 성격의 기능이지만, Write의 경우에는 복합적인 이벤트 수행이 진행되기에 단순 스케일 아웃만으로 해결이 어려울 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1603955d-cd50-43f6-979a-da41289ed696/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fa610924-7430-45f3-8673-534920545c4b/image.png" /></p>
<ul>
<li>주로 장애는 Write 개념에서 발생하기 일쑤이고, 이를 때에는 <strong>폴백</strong>을 통해 원래 사용해야하는 기능을 그럴듯하게 보여주고, 실질적으로 장애가 발생한 부분들에 대해서는 이벤트 큐에 넣어둔 뒤 나중에 수행하는 등(예: 은행 점검시간의 송금업무)의 일처리를 진행할 수 있지만, Read 가 함께 묶여 빠르게 보여지지 않으면 곤란할 수 있다.</li>
</ul>
<h4 id="circuit-breaker-pattern">Circuit Breaker Pattern</h4>
<p>위와 같은 상황들을 고려하여,
CRUD 빈도에 따라서 논리적으로 분리되어 있거나, 결합되어 있어야 하지만, 실질적인 처리의 효율을 위해서 <strong>커플링/디커플링</strong> 해야하는 상황은 필연적으로 찾아오게 된다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/73ccd2ee-bab5-4aa3-b827-4876227f793c/image.png" /></p>
<p>아무리 잘 분석한 msa라고 하더라도 여러갈래로 분리되어 있는 전체 서비스 양상을 가지기에, CRUD 작업이 진행되다보면, 분리된 어플리케이션 상에서의 장애가 발생할 수 있기에 서킷 브레이커 패턴으로 고려해봐야 한다.</p>
<blockquote>
<p><strong>서킷 브레이커 패턴</strong>이란, 연쇄적인 이벤트가 처리되던 도중 장애가 발생했을시에, 장애가 발생한 요인에 지속적인 이벤트 처리 요청을 보내지 않도록 하는 처리과정이라고 할 수 있다.</p>
</blockquote>
<ul>
<li><strong>서킷 브레이커 패턴 도입의 대표적인 예시</strong>
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fb785b7e-9f2f-45e3-acba-12b288efec11/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d84df977-06b4-449e-b38b-71dcea9c1130/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/cd810af3-d68a-4577-96cb-d650e54f6fb3/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c30a2aca-c63c-47a8-909f-1171c86e2cd0/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d25cac8f-adc2-4819-9fb2-a0262894f899/image.png" /></li>
</ul>
<p>여러 문제가 야기될 수 있는 많은 상황에 대해서 서킷 브레이커 패턴의 도입을 통해 폴백 작업을 해두는 것이 서비스 퀄리티를 높이는 것에 매우 큰 기여를 하기에 몹시 중요한 일처리 중 하나라는 것을 기억하자.</p>
<p>** 이 과정에서의 팁 **</p>
<ul>
<li><strong>다이어그램 그리기</strong>
depth를 나눠 내려가는 방향성에 다이어그램을 도입하여, <strong>비즈니스 연계</strong>를 파악할 수 있다.<ul>
<li>너무 많은 비즈니스 연계를 가지는 요소에 대한 디커플링을 통한 결합도를 낮추는 등의 작업을 수행할 수 있다.<blockquote>
<p>디커플링을 적용할 때에도 서킷브레이커 패턴을 고려해야한다.</p>
</blockquote>
</li>
</ul>
</li>
</ul>
<h4 id="정리">정리</h4>
<p>여기까지 고려하여 msa 설계를 진행했다면,
분석된 자료를 통해서 <strong>api prefix</strong>와 <strong>라우팅 테이플</strong>을 준비하는 것 또한 몹시 수월해진다.</p>
<p>이를 통해서 msa를 설계하고 api-gateway까지 설계를 작업하는 것까지가 올바른 msa 설계라고 할 수 있다.</p>
<hr />
<h4 id="번외">번외</h4>
<blockquote>
<p><strong>서킷브레이커는 표준 템플릿에서도 언급할 정도의 중요성을 가진다.</strong>
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/066db0ed-786c-46bf-8108-f689ccde9de7/image.png" /></p>
</blockquote>
<ul>
<li>msa 템플릿 실행환경에서의 예시이다.</li>
<li>위 사진에서 Reseilience4j 를 제외하고는 편하게 교체할 수 있는 부분들이다.<ul>
<li>(Resilience4j : 서킷브레이커 패턴을 고려하는 자바전용(4j : for java) 오픈소스)
장애 발생으로 인해서 회복해야하는 작업에 대한 시기를 지정하는 서킷브레이커를 구현하기 위해 사용한다.</li>
</ul>
</li>
</ul>
<blockquote>
<p>SAGA 패턴이라는 것이 있다.</p>
</blockquote>
<ul>
<li>서킷 브레이커 패턴을 도입할 때, 이 패턴까지 추가로 고려해서 분석하면 더 정교한 설계가 될 수 있다고 한다.</li>
</ul>