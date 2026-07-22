<p>앞선 시간까지 어플리케이션 하나에 대한 ci/cd 배포 실습을 진행해보았다.</p>
<h2 id="msa-구성-배포">MSA 구성 배포</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/38c72c41-6c78-4bb0-93af-00933f0a57bf/image.png" /></p>
<p>MSA 어플리케이션에서는 어떤 식으로 작업해야할지 알아보자.</p>
<blockquote>
<p>각 화면은</p>
</blockquote>
<ul>
<li>msa-sample-ui : 화면 서비스를 담당하는 api</li>
<li>msa-sample-gateway : api 서버 앞단에서 여러 api 서버들의 end-point를 단일화하여 라우팅, 로드벨런싱 등의 역할을 하는 api</li>
<li>msa-sample-api : 메인 화면 정보에 대한 서비스를 담당하는 api</li>
<li>msa-sample-sd-api : side 화면 정보에 대한 서비스를 담당하는 api</li>
</ul>
<p>이번에도 물론 openbao unseal 작업은 선행되어야 작업할 수 있다.</p>
<blockquote>
<p>실습 작업 : <a href="https://github.com/K-PaaS/msa-sample">https://github.com/K-PaaS/msa-sample</a></p>
</blockquote>
<h3 id="환경변수-배포">환경변수 배포</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/12774c94-1e8a-4347-b36c-1ecd3f16f9cb/image.png" /></p>
<p>컨피그맵 정보를 포털을 통해서 등록해준다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3e46d2d1-ce39-44d6-a0c1-f97703a31481/image.png" /></p>
<h3 id="레파지토리-생성">레파지토리 생성</h3>
<p>사용할 마이크로 서비스 어플리케이션의 각 프로젝트들을 담을 수 있도록 레포지토리를 만들어주자.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/62580624-bf4a-425a-b08b-db6600798f90/image.png" /></p>
<ul>
<li><p>$ git clone --mirror {위의 git 주소} 명령을 통해서, 내 클러스터에서 배포할 어플리케이션들을 내려받는다.</p>
</li>
<li><p>만들어진 레포지토리의 주소를 알아둔다.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/10ebff61-7168-4876-ae52-718d3dfab194/image.png" /></p>
</li>
<li><p>$ git push --mirror {만들어진 레포지토리의 주소} 명령을 통해서, 해당 레포지토리에 사용할 어플리케이션을 푸시한다.</p>
<blockquote>
<p>이를 통해서 사용할 어플리케이션을 scm에 푸시까지 진행해준 상태이다.</p>
</blockquote>
</li>
</ul>
<h3 id="파이프라인-설정">파이프라인 설정</h3>
<p>이후 작업은 이전 시간에 진행했던 단일 프로젝트 작업을 병렬적으로 작업해주면 된다.</p>
<blockquote>
<p>알아둘 점.</p>
</blockquote>
<ul>
<li>앞서 portal에 등록해둔 configMap 정보는 여기서 활용한다.</li>
<li>사용하는 yaml 파일의 <strong>enfFrom</strong> 필드를 통해서 세팅된 환경변수를 이용한다.</li>
<li>형상관리 정보를 입력할 때, 포털에 등록해둔 레파지토리의 id/pw 정보를 입력한다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/5e2d43ef-ce34-439f-9556-fd75697f462f/image.png" /></p>
<p>모두 실행해준다면,
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/06b15553-fc2b-4d0b-8ced-a4a8f612d0fd/image.png" /></p>
<p>완성이다.</p>
<h3 id="알아두기">알아두기</h3>
<p>k-paas 설치할 때, 보안상의 이유로 플랫폼에서 제공되는 네임스페이스만 권한을 인정하고 나머지에 대해서는 예외처리해두었기에 실습할 때, 오류가 발생할 수 있다.</p>
<blockquote>
<p>cp-cluster-vars 파일에서
INSTALL_KYVERNO 값을 Y로 두었기 때문.</p>
</blockquote>
<blockquote>
<p>그리고 현재 주어진 순서대로 실습을 진행했을 때, 정상적으로 배포가 안되는 것을 확인할 수 있을텐데,
도커 허브 공식 홈페이지에서 해당 어플리케이션에서 사용할 jdk version을 전부 내렸기 때문에 안된다는 것을 인지하자.</p>
</blockquote>
<ul>
<li>대체 이미지를 사용한 빌드를 진행해야 한다.</li>
</ul>