<p>기본적인 개념은 이미 많이 다뤘기에,</p>
<p>이번 시간에는 kubectl을 통한 여러가지 방식을 사용해보는 시간을 가져볼 것이다.</p>
<p>또한! 클러스터 단위에서의 실습을 진행할 때,
워크노드에 플로팅 아이피를 달아서 작업해줘야할 상황이 올 수 있다.</p>
<p>플로팅아이피 하나당 하나의 vpc 게이트웨이 역할을 해준다.
그렇기에 많이 달아두면 리소스에 대한 접근이 그만큼 편안해져 빠른 일처리를 기대할 수 있게 된다.</p>
<h1 id="pod">Pod</h1>
<h2 id="기본">기본</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fb5d93f6-9d4f-4fcb-9802-2afbfa02e889/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/951d8cc8-e4b1-4441-98cc-b19962dc1e63/image.png" /></p>
<p>** CLI를 이용한 생성 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/2ab89808-f53f-4645-9d26-b120d3b4085b/image.png" /></p>
<p>** CLI를 이용한 조회 ** </p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e7ab2582-5da7-40a7-a895-f8c59ca9cded/image.png" /></p>
<h3 id="yaml-파일을-통한-동작-구성">yaml 파일을 통한 동작 구성</h3>
<ul>
<li>파드 자체에 명령어를 심어서, 로그로 출력되게끔 한다.</li>
</ul>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: secloudit-namespace
spec:
  containers:
  - image: busybox
    name: secloudit-container
    env:
    - name: SECLOUDIT
      value: &quot;Platform as a service!&quot;
    command: [&quot;/bin/sh&quot;]
    args: [&quot;-c&quot;, &quot;while true; do echo $(SECLOUDIT); sleep 10;done&quot;]</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9b4d03ae-e880-43c4-abda-f60a4419af63/image.png" /></p>
<ul>
<li>또한 여러 컨테이너를 띄워서 사용할 수 있다.</li>
</ul>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: secloudit-namespace
spec:
  containers:
  - image: nginx
    name: secloudit-container1
  - image: redis
    name: secloudit-container2
  - image: memcached
    name: secloudit-container3
  - image: consul:1.15
    name: secloudit-container4</code></pre><h1 id="replicaset">Replicaset</h1>
<h2 id="기본-1">기본</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d8f172ba-e37e-4c0d-8ee3-53523c20344b/image.png" />
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dc882a09-c379-405e-9cb4-b73da5d9f50b/image.png" /></p>
<p>** CLI를 이용한 생성 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ec70d00f-f715-4dbc-8fe3-a324637f6ec9/image.png" /></p>
<p>** CLI를 이용한 조회 ** </p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/35b73fed-5d6e-4117-9aa2-14ff1e40fa67/image.png" /></p>
<p>지금까지의 실습에서는 배포 단위를 deployment 단위로 작업했었다.</p>
<p>이번 실습에서는 레플리카셋 단위로 작업을 해볼 것인데,
이런 관리에서는 파드만 관리할 수 있고, 레플리카셋이 죽으면 관리해줄 디플로이먼트가 없다는 것을 알아두자.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/31d7657f-ddd6-4348-b18d-f8df66c7339a/image.png" /></p>
<h2 id="응용">응용</h2>
<h3 id="scale-관리">Scale 관리</h3>
<p>scale 명령어 자체는 여러 방면에서 사용되지만, 레플리카셋을 대표로 학습해볼 것이다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/2fc58942-7295-4638-85d8-4f0cfc6e13aa/image.png" /></p>
<h4 id="실습">실습</h4>
<img height="50%" src="https://velog.velcdn.com/images/klmcw1004/post/7b4e5961-1637-4e89-9eec-3c9077a5ecd5/image.png" width="50%" />

<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/292d8f4a-4a6e-4936-8766-8a448fe0d9ac/image.png" /></p>
<p>파드 3개를 통해 작업하던 레플리카셋이 <strong>scale</strong>명령어를 통해서 6개의 파드를 띄워 관리하는 것을 확인할 수 있다.</p>
<h1 id="deployment">Deployment</h1>
<h2 id="기본-2">기본</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c74c3cba-05bb-452e-bd1c-cb988ca29cce/image.png" />
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f31b7dc7-c1f3-4999-aceb-2ee6f6b5b715/image.png" /></p>
<p>** CLI를 이용한 생성 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b1351e39-eb47-40f8-844d-3f21f2aee6e2/image.png" /></p>
<ul>
<li>CLI를 통한 배포를 진행하고자 한다면, 이미지 정보와 레플리카셋 정보를 반드시 기입해야 한다.</li>
</ul>
<p>** CLI를 이용한 조회 ** </p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/7fb7aa85-437e-4889-be30-334caabaaa0e/image.png" /></p>
<h2 id="응용-1">응용</h2>
<p>앞선 replicaset 과의 차이점을 직접적으로 체감할 수 있는 기능인 <strong>롤링 업데이트</strong>가 어떻게 동작하는지 알아보자.</p>
<h3 id="rollingupdate">RollingUpdate</h3>
<h4 id="방식">방식</h4>
<ol>
<li><p>Deployment를 배포해준다.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/7f030d16-3428-4efd-807f-12335de34905/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b7b1a269-0007-4639-b5cd-1cabba4a179b/image.png" /></p>
</li>
<li><p>배포된 버전을 set 명령어를 통해서 수정해주면서, 기록한다.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/20a92d04-cdc6-411f-b997-ca5bc5f56f7a/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a497ba5a-ef60-4610-b71d-4e30d7dfe2d1/image.png" /></p>
</li>
</ol>
<ol start="3">
<li>변경된 작업이 정상적으로 완료되었는지 확인한다. (히스토리 조회)
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/abe50da9-1c21-4abb-a461-ee3e9b6466a6/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/80321a6d-3435-43e9-ab4d-597ec67c4217/image.png" /></li>
</ol>
<ul>
<li>이미지 업데이트시 <strong>--record</strong> 옵션을 통해서 이력을 남겼기 때문에 롤링 업데이트 명령어가 기록된 것을 확인할 수 있다.</li>
</ul>
<h3 id="rollback">RollBack</h3>
<ul>
<li>기록되어 있는 이전 버전으로 돌아가도록 해줄 수 있다.</li>
</ul>
<p>방법 1. 직전 버전으로 돌아가기.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/5c027024-918b-4a15-8650-187efd476b1f/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f26f1f1f-a1e6-47e9-a2b6-7666e5735ee6/image.png" /></p>
<p>방법 2. 명시한 버전으로 돌아가기.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e049faeb-8627-4ef1-a6a6-8ae2c9687c2d/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/002dc49a-7927-42a0-8842-fb46f0883b63/image.png" /></p>
<ul>
<li>이처럼 현재상태의 revision 직전의 revision으로 돌아가며 새로운 현재상태의 revision을 기록할 수도 있고,</li>
<li>명시된 revision으로 돌아가며 새로운 현재상태의 revision을 기록할 수도 있다.</li>
</ul>