<h1 id="configmap">ConfigMap</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3b7e8b51-2c51-4fc1-8eac-f1ea353c6388/image.png" /></p>
<pre><code>apiVersion: v1
kind: ConfigMap
metadata:
  name: secloudit-configmap
  namespace: secloudit-namespace
data:  
  SECLOUDIT: &quot;Platform as a service!&quot; </code></pre><ul>
<li>data 필드 내부에 key-value pair형태로 사용할 데이터를 지정할 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4a490337-8a9b-4e2a-a6d2-48d7160cd4f0/image.png" /></p>
<ul>
<li>이런 방식으로 cli를 활용한 ConfigMap을 만들 수도 있다.</li>
</ul>
<h2 id="configmapkeyref를-사용한-방식">configMapKeyRef를 사용한 방식</h2>
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
    - name: SECLOUDIT_ENV
      valueFrom:
        configMapKeyRef:
          name: secloudit-configmap
          key: SECLOUDIT
    command: [&quot;/bin/sh&quot;]
    args: [&quot;-c&quot;, &quot;while true; do echo $(SECLOUDIT_ENV); sleep 10;done&quot;]
</code></pre><ul>
<li>만들어진 configmap은 위와 같은 방식으로 사용될 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/06f13966-cfe0-45e0-a790-0875018abf47/image.png" /></p>
<ul>
<li>만들어진 configmap은 이런 방식으로 조회할 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ede666f2-a4e6-4ca3-b59b-5acfb28b2240/image.png" /></p>
<ul>
<li>해당 작업이 수행된 pod에 대해서는 이처럼 로그를 확인할 수 있다.</li>
</ul>
<ol>
<li><p>configmap 만들기.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c5e6cc2f-cfb8-443c-839b-e0323a987f66/image.png" /></p>
</li>
<li><p>파드 배포에 해당 정보 사용하기.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/02867528-ead0-4211-bb4e-0f3ff1965bbc/image.png" /></p>
</li>
<li><p>파드 로그조회로 확인하기.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d3e01a3a-7eb9-4bde-bc3f-f0b72bddb8d5/image.png" /></p>
</li>
</ol>
<h2 id="configmapref를-사용한-방식">configMapRef를 사용한 방식</h2>
<p>앞선 방식에서는 특정 key-value값만 가져오는 방식이다.
지금 방식은 ConfigMap에 등록된 모든 key-value를 가져오게 된다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/92f02a63-2ada-4995-9639-fb963a8e815c/image.png" /></p>
<pre><code>apiVersion: v1
kind: ConfigMap
metadata:
  name: secloudit-configmap
  namespace: secloudit-namespace
data:  
  SECLOUDIT: &quot;Platform as a service!&quot; 
  PaaS: &quot;Secloudit&quot; </code></pre><ul>
<li>위의 두가지 방식 중 하나로 configmap을 구성해준 뒤,</li>
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
    envFrom:
    - configMapRef:
        name: secloudit-configmap
    command: [&quot;/bin/sh&quot;]
    args: [&quot;-c&quot;, &quot;while true; do echo $(SECLOUDIT) $(SSU); sleep 10;done&quot;]</code></pre><ul>
<li>자유롭게 사용할 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ff08fbb8-e202-4fd6-ae99-0382c3effd8c/image.png" /></p>
<h1 id="secret">Secret</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1bdfc676-4e16-4670-9d31-7511ea70cc3d/image.png" /></p>
<pre><code>apiVersion: v1
kind: Secret
metadata:
  name: secloudit-secret
  namespace: secloudit-namespace
type: Opaque
data:
  SECLOUDIT: UGxhdGZvcm0gYXMgYSBzZXJ2aWNlIQ==  </code></pre><ul>
<li>위와 같은 yaml 파일 작성을 통해서 클러스터 자체에 해당 시크릿 정보를 메타데이터로 저장해둔 상태로 만들 수 있다.</li>
<li>secret 리소스의 yaml 파일을 작성할 때의 value값은 base-64f로 인코딩된 정보를 기입해야함을 잊지말자.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/49126c6c-115b-46f7-ae1f-4372bcb67d21/image.png" /></p>
<ul>
<li>cli 방식으로도 secret 정보를 저장해둘 수 있는데, 이 때에는 value값을 인코딩하지 않고 넣어야 한다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/da9a4ec4-9f0f-4339-be52-85df2479d6ae/image.png" /></p>
<ul>
<li>configmap과는 다르게, 조회를 시도했을 떄, data 필드가 제한되어 정보제공이 되는 것을 볼 수 있다.<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/910b1d44-07bf-4003-b63a-0e401752aa56/image.png" />
컨피그맵 정보는 보란듯이 노출된다는 것에서의 차이를 확인할 수 있다.</p>
</blockquote>
</li>
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
    - name: SECLOUDIT_ENV
      valueFrom:
        secretKeyRef:
          name: secloudit-secret
          key: SECLOUDIT
    command: [&quot;/bin/sh&quot;]
    args: [&quot;-c&quot;, &quot;while true; do echo $(SECLOUDIT_ENV); sleep 10;done&quot;]</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/7b238005-b60d-40f0-8a6e-1b26ea4aef21/image.png" /></p>
<ul>
<li>이후 이런 형태로 해당 시크릿정보를 불러와서 사용할 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/53ebc21b-dbaf-4c1d-98e4-012825b6aac0/image.png" /></p>
<ul>
<li>해당 시크릿 정보를 통해 배포된 파드의 로그를 통해서 secret 정보가 정상적으로 사용됨을 알 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/52b432fe-913e-48dd-9ee1-2794df8be181/image.png" /></p>
<ul>
<li>또한 해당 파드에 직접 접근하여 환경변수로 secret 정보가 디코딩 된 상태로 잘 불러와졌음을 알 수 있다.</li>
</ul>
<blockquote>
<p>secret 또한 configmap과 같이 여러방식으로 환경변수를 불러올 수 있다.
<strong>실제 사용 방식</strong></p>
</blockquote>
<ul>
<li><strong>여러 key-pair 형태의 시크릿을 준비한다.</strong><pre><code>apiVersion: v1
kind: Secret
metadata:
name: secloudit-secret
namespace: secloudit-namespace
type: Opaque
data:
# hello my name is gwanrok
SECLOUDIT: aGVsbG8gbXkgbmFtZSBpcyBnd2Fucm9r
# my birthday is October 4th.
MOON: bXkgYmlydGhkYXkgaXMgT2N0b2JlciA0dGgu</code></pre></li>
<li>** 방법 1. env 환경에서 여러 secret 정보를 사용하고자 할 때.**<pre><code>apiVersion: v1
kind: Pod
metadata:
name: secloudit-pod
namespace: secloudit-namespace
spec:
containers:
- image: busybox
  name: secloudit-container
  env:
  - name: SECLOUDIT_ENV
    valueFrom:
      secretKeyRef:
        name: secloudit-secret
        key: SECLOUDIT
  - name: MOON_ENV
    valueFrom:
      secretKeyRef:
        name: secloudit-secret
        key: MOON
  command: [&quot;/bin/sh&quot;]
  args: [&quot;-c&quot;, &quot;while true; do echo $(SECLOUDIT_ENV); echo $(MOON_ENV); echo ; sleep 10; done&quot;]</code></pre><ul>
<li>** 방법 2. envFrom 환경에서 환경변수 정보를 한번에 가져와서 사용할 때.**
```
apiVersion: v1
kind: Pod
metadata:
name: secloudit-pod
namespace: secloudit-namespace
spec:
containers:</li>
<li>image: busybox
name: secloudit-container<h1 id="env-대신-envfrom을-사용하여-시크릿-통째로-가져오기">env 대신 envFrom을 사용하여 시크릿 통째로 가져오기</h1>
envFrom:<ul>
<li>secretRef:
  name: secloudit-secret
command: [&quot;/bin/sh&quot;]
args: [&quot;-c&quot;, &quot;while true; do echo &quot;Name: $(SECLOUDIT)&quot;; echo &quot;Birthday: $(MOON)&quot;; echo &quot;이런 형태로 의도한 그대로 텍스트를 출력하도록 한다.&quot;; sleep 10; done&quot;]
```</li>
</ul>
</li>
</ul>
</li>
<li><strong>ConfigMap 과 Secret 모두 사용하는 방법</strong><pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
name: secloudit-deployment
namespace: secloudit-namespace
spec:
replicas: 1
selector:
  matchLabels:
    app: secloudit-app
# [여기서부터 Pod의 스펙이 들어갑니다]
template:
  metadata:
    labels:
      app: secloudit-app
  spec:
    containers:
    - image: busybox
      name: secloudit-container
      env:
      # 1. 시크릿에서 가져오기
      - name: SECRET_ENV
        valueFrom:
          secretKeyRef:
            name: secloudit-secret
            key: SECLOUDIT
      # 2. 컨피그맵에서 가져오기
      - name: CONFIG_ENV
        valueFrom:
          configMapKeyRef:
            name: secloudit-configmap
            key: SECLOUDIT
      command: [&quot;/bin/sh&quot;]
      # (참고: 쉘 변수 출력은 $()가 아니라 ${}를 쓰는 것이 더 안전합니다)
      args: [&quot;-c&quot;, &quot;while true; do echo Secret: ${SECRET_ENV}, Config: ${CONFIG_ENV}; sleep 10;done&quot;]</code></pre></li>
</ul>
<h2 id="응용">응용</h2>
<p>개발자가 직접 모든걸 작업하는 상황이라면, 여기서 멈춰도 된다.</p>
<p>하지만, 요즘은 대부분 상용 소프트웨어를 사용한다.</p>
<p>또한 <strong>대부분의 상용 소프트웨어(Redis, Nginx, MySQL 등)</strong>는 <strong>설정 파일</strong>을 읽도록 구성되어 있다.</p>
<p>레디스를 대표적인 예시로 들면, 레디스는 환경변수 정보를 사용할 정보가 담긴 파일의 경로를 요청하여
<strong>사용하는 이미지에 수정 없이</strong> 끼워넣을 수 있게 된다.</p>
<p>이를 통해서 범용성 좋은 작업을 수행하게 된 것이다.</p>
<h3 id="방법">방법</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0572f67c-95b1-4785-8879-204d485897de/image.png" /></p>
<pre><code>apiVersion: v1
kind: Secret
metadata:
  name: secloudit-secret
  namespace: secloudit-namespace
type: Opaque
data:
  SECLOUDIT: UGxhdGZvcm0gYXMgYSBzZXJ2aWNlIQ==     </code></pre><ul>
<li>앞선 방식과 다를 바 없는 secret을 준비한다.</li>
</ul>
<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d66b6b4c-2e31-4f52-bf96-dc1a80b8d72e/image.png" /></p>
</blockquote>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: secloudit-namespace
spec:
  containers:
  - image: redis
    name: secloudit-container
    volumeMounts:
    - name: secloudit-volume
      mountPath: &quot;/secrets&quot;
      readOnly: true
  volumes:
  - name: secloudit-volume
    secret:
      secretName: secloudit-secret</code></pre><ul>
<li>volumes 필드를 통해서 사용할 파일의 이름과 함꼐 사용할 secret 정보를 알 수 있다.</li>
<li>volumeMount 필드를 통해서 사용할 저장소의 경로, 권한 등을 지정할 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9df6cacc-00b0-404c-881e-2d26195ea989/image.png" /></p>
<ul>
<li>설정한 secret의 key값을 파일명으로 하고, value값을 파일내용으로 하도록 위와 같이 설정되는 결과를 확인할 수 있다.</li>
</ul>