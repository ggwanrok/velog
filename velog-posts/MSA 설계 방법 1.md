<h1 id="클라우드-네이티브-관련-개발-방법론">클라우드 네이티브 관련 개발 방법론</h1>
<h2 id="들어가며">들어가며</h2>
<p>앞서 클라우드 네이티브 개발 방법론에 대해서 분석-설계-구현-테스트 및 이행 절차에 대해서 간단하게 언급한 바 있다.</p>
<p>이번 시간에는 행정안전부에서 규정한 클라우드 네이티브 정보시스템 구축을 위한 개발자 안내서에 소개되어 있는 MSA 설계 방식에 대해서 조금 더 자세하게 알아볼 것이다.</p>
<hr />
<h2 id="클라우드-네이티브-적용을-위한-마이크로서비스-도출">클라우드 네이티브 적용을 위한 마이크로서비스 도출</h2>
<p>분석 단계는 어플리케이션 개발을 위한 초석 역할을 가지며, 이후에 분석된 내용을 구체화하는 설계단계, 구현단계, 테스트 및 이행 단계를 가지게 된다.</p>
<h3 id="마이크로서비스-도출-방안">마이크로서비스 도출 방안</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/425420ed-ba4c-41e9-b6f8-2054a5fec17d/image.png" /></p>
<hr />
<h3 id="마이크로서비스-도출-절차">마이크로서비스 도출 절차</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c30128fa-197c-43a9-9078-aa259e235d19/image.png" /></p>
<ul>
<li>마이크로서비스가 비즈니스 변화에 민첩하게 대응하고, 신속하게 배포되기 위해서는 각각의 마이크로서비스는 독립적으로 도출되어야 한다. 즉 마이크로서비스 간 느슨한 결합과 강한 응집력이 보장될 수 있어야 한다.</li>
</ul>
<hr />
<h4 id="-유비쿼터스-언어-정의-">** 유비쿼터스 언어 정의 **</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/27c317cc-fc9e-4e23-9a36-61c6597b420c/image.png" /></p>
<ul>
<li>유비쿼터스 언어를 정의하는 이유.<ul>
<li>언어 자체를 통일성 있도록 정의하는 작업이기에 중요한 것도 있지만,</li>
<li><em>의뢰자와 수주업체의 접촉*</em>에 대한 강제성을 규정해두기 위함이 크다.<blockquote>
<p>사업이 진행될 때에는 <strong>고객 기업</strong>과 <strong>용역 기업</strong>이 반드시 존재하는데,
용역 기업이 고객 기업과 접촉할 수 있도록 강제하는 보조 장치 역할을 한다.</p>
</blockquote>
<ul>
<li>보통 msa 도입 사업에는 기업의 자발적인 의지보다는 정부사업 등의 영향이 있기에 고객기업 입장에서는 시큰둥한 것이 어쩌면 당연한 기댓값이라고 할 수 있다..?</li>
</ul>
</li>
</ul>
</li>
</ul>
<hr />
<h4 id="-바운디드-컨텍스트-도출-">** 바운디드 컨텍스트 도출 **</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6d80f943-59dc-483c-ba9e-4a6f530b77c1/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/07d2ebe4-ae3e-4a75-8833-7b3b4985eb3d/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/499c014e-9cb9-41e0-bf3b-9cfdb23fc4e9/image.png" /></p>
<p>msa 설계를 진행할 어플리케이션에서의 도메인 추출을 통해서 마이크로서비스를 도출할 수 있다.</p>
<hr />
<h4 id="-이벤트-스토밍-">** 이벤트 스토밍 **</h4>
<p>도메인은 어떤 기준으로 뽑아야 하는가? 도출될 바운디드 컨텍스트는 또 어떻게 규정할 것인가?</p>
<p>명확한 정의 자체가 어려운 개념이기에, 마이크로서비스를 도출하는 과정이 다소 <strong>추상적</strong>으로 느껴질 수 있다.</p>
<p>그렇기에 <strong>이벤트 스토밍</strong>이라는 하나의 방법론을 알아두자.</p>
<blockquote>
<p><strong>이벤트 스토밍</strong>이란, Event + Brain Storming의 합성어로 도메인의 이벤트를 통해 마이크로서비스를 도출하기 위한 브레인스토밍 활동이다.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3b78fccb-5916-4390-b7e6-1b9647f0fc36/image.png" /></p>
</blockquote>
<p>** 이벤트 스토밍의 과정 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c81a9a69-173a-4d35-87b5-54c38d115a39/image.png" /></p>
<p>이 과정은 큰 화이트보드에 각 단계별 고유 색깔을 가진 포스트잇을 사용하는 것을 기준으로 함</p>
<ol>
<li>이벤트 도출
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a0ae4689-8779-449a-8a0d-5c7fd1061802/image.png" /></li>
</ol>
<ul>
<li>요구기능으로 나타날 수 있는 모든 경우를 빠짐없이 붙인다.</li>
</ul>
<ol start="2">
<li>커멘드 도출
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/eb00579b-02ef-4a21-99cd-b2f57709a8ee/image.png" /></li>
</ol>
<ul>
<li>해당 이벤트를 발생시킬 수 있는 <strong>트리거는 무엇인가?</strong>를 따져 커멘트를 도출한다.</li>
</ul>
<ol start="3">
<li>애그리게잇 식별
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/88fcb433-3f78-43b9-9558-98dbaf613bb8/image.png" /></li>
</ol>
<ul>
<li>각 커멘드들을 수행하는 개체인 <strong>엔티티</strong>를 도출한다.</li>
</ul>
<ol start="4">
<li>바운디드 컨텍스트 식별
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e254a496-a2e0-4da7-bd76-a0bc872ec905/image.png" /></li>
</ol>
<ul>
<li>도출된 엔티티들이 포함되도록 경계를 식별하여 <strong>바운디드 컨텍스트</strong>를 도출한다.</li>
</ul>
<ol start="5">
<li>마이크로서비스 도출
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/13e6c3c1-0fba-4375-85e4-da763c9dc8dd/image.png" /></li>
</ol>
<ul>
<li>도출된 바운디드 컨텍스트는 각각의 마이크로서비스로 도출된다.</li>
</ul>
<h4 id="정리">정리</h4>
<p>여기까지 진행한다면 기본적인 방식으로 마이크로서비스 어플리케이션을 설계한 것이라고 할 수 있다.</p>
<p>다음 자료로 마이크로서비스를 실제로 설계하고 분석할 때 추가로 고려해야할 것들을 다뤄보자.</p>