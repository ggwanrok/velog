<h2 id="들어가며">들어가며</h2>
<p>지금까지 배웠던 쿠버네티스 환경에서의 리소스들을 kubectl 환경에서 사용해보며 복습해보는 시간을 가져보자.</p>
<h1 id="node">Node</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a0c68397-c241-4e89-ba62-a544e7a1c8ae/image.png" /></p>
<h2 id="노드-관리">노드 관리</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/98439307-0689-4479-89fd-73204f02f5c2/image.png" /></p>
<p>실습에더 사용하던 클러스터의 마스터 노드의 상세정보를 확인해보면,</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fa36353f-bb03-4a04-924b-f6203f67226c/image.png" /></p>
<ul>
<li>Taint라는 필드를 통해서 별도의 파드 배포가 이뤄지지 않도록 설정되어 있는 것을 확인할 수 있다.</li>
</ul>
<h3 id="cordon">Cordon</h3>
<ul>
<li>특정 노드에 새로운 파드가 스케줄 되지 않도록 하는 기능</li>
<li>기존에 실행 중이던 파드에는 영향을 주지 않고 새로운 파드의 배포를 막는다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/838e6703-fd51-43c7-a3b2-f4c18f3e4293/image.png" /></p>
<ul>
<li>별도의 작업을 통해서 Taint 필드에 따로 배포 억제를 해두지 않았던 워커노드에 <strong>cordon</strong> 명령을 통해서 배포가 이뤄지지 않도록 설정해줄 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0ac2f99c-5657-40e9-a153-f3052c3788b6/image.png" /></p>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
  name: secloudit-deployment
  namespace: default  
spec:
  selector:
    matchLabels:
      apps: apps
  replicas: 1  
  template:
    metadata:
      labels:
        apps: apps
    spec:
      containers:
      - name: container
        image: nginx:latest
        ports:
        - containerPort: 80
          protocol: TCP</code></pre><p>이후 위와 같은 yaml 파일을 배포해준다면</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1965778f-8f26-4566-875d-2042fcc0d123/image.png" /></p>
<p>cordon 지정해둔 노드에서는 스케쥴링이 발생하지 않는 것을 확인할 수 있다.</p>
<h3 id="uncordon">Uncordon</h3>
<ul>
<li>Cordon이 적용된 노드가 다시 정상적으로 스케줄 되도록 하는 기능</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/519cab0a-9966-49bc-8b51-4332196a8f86/image.png" /></p>
<p>uncordon 작업을 해준 뒤에는 
당연하게도 2번 노드에도 스케쥴링이 될 것이다.</p>
<p>여기서 새로운 명령어 하나를 알아보자.</p>
<h3 id="drain">Drain</h3>
<ul>
<li>특정 노드의 유지보수 또는 점검을 위해 실행 중인 파드들을 다른 노드로 이동시키는 기능</li>
<li>Drain 실행 시 해당 노드는 자동으로 Cordon 되어 새로운 파드가 스케줄 되지 않음</li>
<li>DaemonSet으로 배포된 파드는 모든 노드에서 실행을 보장해야 하는 파드이므로 Drain시 DaemonSet 파드는 삭제가 되지 않기 때문에 무시해야 한다.</li>
</ul>
<p>앞선 배포가 'mgr-cluster3'에서 많이 진행되었기에,
해당 노드를 drain 삼아 해당 노드에 스케줄링 되었던 파드들이
만들어질 수 있는 노드 (mgr-cluster2 노드 포함)에서 새로 생기는 것을 확인해보자.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6883512a-0d40-4604-ba78-76ca40021a5f/image.png" /> <img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0b0ea1fc-d6cc-4a15-befb-adcb56857cdb/image.png" /></p>
<p>파드들이 잘 넘어가는 것을 확인할 수 있다.</p>
<h3 id="toleration">Toleration</h3>
<ul>
<li>Toleration 동일한 값의 Taint가 설정된 Node에 Pod를 배포할 수 있도록 Pod에 설정하는 기능</li>
<li>Toleration이 적용된 Pod는 Taint가 없는 Node에도 배치가 가능하다.</li>
</ul>
<p>Taint 필드를 통해 설정하는 값을 effect라고 한다.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9e724f90-8b1d-43a8-8015-da967b8eb373/image.png" /></p>
<p>cordon/uncordon은 노드단위로 지정하는 성격이라고 할 수 있다.</p>
<p>여기서 toleration의 차이를 알 수 있는데,
toleration은 <strong>파드</strong>단위로 설정할 수 있는 느낌이다.</p>
<p>toleration에서 taint의 필드값을 지정하여 파드를 만들어주고자 한다면 해당 속성에 대해서만 파드를 생성하는 것이 가능해진다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e188538b-8337-4b3a-a05f-1ab42c1eb79a/image.png" /></p>
<h3 id="정리">정리</h3>
<p>cordon, uncordon, drain, taint, toleration 을 통해서 Node를 관리할 수 있다.</p>
<h1 id="namespace">Namespace</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/70ee0d42-7115-4ca3-89d4-15b0ffc75fca/image.png" /></p>
<ul>
<li>리소스를 논리적으로 나누기 위한 리로스</li>
<li>네임스페이스를 지정하지 않으면 default 네임스페이스에 할당</li>
<li>논리적인 그룹에 대한 권한 관리, CPU &amp; Memory 등 리소스 제한이 가능</li>
<li>kube-system 네임스페이스는 쿠버네티스 시스템이 동작하기 위한 리소스들의 그룹</li>
</ul>
<p>** 생성 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/91a0d7c6-f0b2-46e5-a544-e35cbfda01c2/image.png" /></p>
<p>** 조회 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f4518092-48de-4b68-aea2-5a84c87faa0b/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/bf2861f0-ca2d-415e-adf3-593e9664f010/image.png" /></p>
<p>Namespace에 대해서는 이미 많이 다뤘기에, context 위주로 알아보자.</p>
<h2 id="context">Context</h2>
<ul>
<li>Config 파일을 사용하여 여러 개의 클러스터에 접근할 수 있도록 등록</li>
<li>사용할 클러스터, 사용자, 네임스페이스를 하나로 묶어 어떤 클러스터에 어떤 사용자로 접근할지 설정</li>
</ul>
<p>** 생성 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e163e381-60d6-4418-bf66-1084f6b9e919/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/16fd0acc-17eb-4141-89ec-d69987dfa670/image.png" /></p>
<p>기존 사용환경 context 이외에도 별도의 context를 만들 수 있다는 것을 확인할 수 있다.</p>
<p>** Context 변경 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ee4f5a6a-c803-45ab-8db8-3e383560f6fb/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/2941245f-23e7-4631-9563-d9fc68af24fa/image.png" /></p>
<p>** 차이점 확인 **</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c588cac8-2eb1-4f0d-9610-f93b19475b81/image.png" /></p>
<p>새로 만든 context에서는 기존 context의 리소스에 접근되지 않는 것을 확인할 수 있다.</p>
<h2 id="번외">번외</h2>
<h3 id="resourcequata">ResourceQuata</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c7e6f84d-ede3-466e-802a-aba5c9af9d48/image.png" /></p>
<ul>
<li>특정 Namespace 에서 사용할 수 있는 총 리소스 양을 제한하는 리소스</li>
<li>해당 Namespace에 리소스의 생성 및 개수 제한</li>
</ul>
<p><strong>예시 yaml코드</strong></p>
<pre><code>apiVersion: v1
kind: ResourceQuota
metadata:
  name: secloudit-resourcequota
  namespace: secloudit-namespace
spec:
  hard:
    pods: &quot;10&quot;
    requests.cpu: &quot;4&quot;
    requests.memory: &quot;8Gi&quot;
    limits.cpu: &quot;6&quot;
    limits.memory: &quot;10G&quot;  

---
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-resourcequota-pod
  namespace: secloudit-namespace
spec:
  containers:
  - name: secloudit-container
    image: nginx
    resources:
      requests:
        memory: &quot;8Gi&quot;
        cpu: &quot;4&quot;
      limits:
        memory: &quot;10Gi&quot;
        cpu: &quot;6&quot;

---
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-resourcequota-pod
  namespace: secloudit-namespace
spec:
  containers:
  - name: secloudit-container
    image: nginx
    resources:
      requests:
        memory: &quot;8Gi&quot;
        cpu: &quot;7&quot;
      limits:
        memory: &quot;10Gi&quot;
        cpu: &quot;5&quot;</code></pre><h3 id="limitrange">LimitRange</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6b6fbd9c-156a-47cc-9433-322b9cd216f9/image.png" /></p>
<ul>
<li>특정 Namespace에서 사용할 수 있는 총 리소스의 최소값, 최대값, 기본값을 설정</li>
<li>파드에서 리소스 소비에 대한 제한을 설정</li>
</ul>
<p><strong>예시 yaml코드</strong></p>
<pre><code>apiVersion: v1
kind: LimitRange
metadata:
  name: secloudit-limitrange
  namespace: secloudit-namespace
spec:
  limits:
  - type: Container
    max:
      cpu: 2
      memory: 1Gi
    min:
      cpu: 200m
      memory: 256Mi
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 300m
      memory: 256Mi

---
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-limitrange-pod
  namespace: secloudit-namespace
spec:
  containers:
  - name: secloudit-container
    image: nginx
    resources:
      requests:
        memory: &quot;256Mi&quot;
        cpu: &quot;200m&quot;
      limits:
        memory: &quot;1Gi&quot;
        cpu: &quot;2&quot;

---
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-limitrange-pod
  namespace: secloudit-namespace
spec:
  containers:
  - name: secloudit-container
    image: nginx
    resources:
      requests:
        memory: &quot;2&quot;
        cpu: &quot;200m&quot;
      limits:
        memory: &quot;2Gi&quot;
        cpu: &quot;2&quot;    </code></pre>