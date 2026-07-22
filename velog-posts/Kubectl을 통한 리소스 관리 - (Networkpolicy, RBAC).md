<h1 id="networkpolicy">Networkpolicy</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0c3d9c5e-de91-438b-a4cc-8f4c9f2a89da/image.png" /></p>
<p>서비스 네트워킹을 할 때,
파드간의 네트워크 트래픽을 제어 단위는 네임스페이스이다.</p>
<p>클러스터 내에서 트래픽을 제어할 수 있는 방화벽 역할을 수행하는 개념을 <strong>네트워크 폴리시</strong>라고 한다.</p>
<pre><code>apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: secloudit-networkpolicy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          purpose: production
    ports:
    - protocol: TCP
      port: 80</code></pre><ul>
<li>app: web 이라는 <strong>key-value 를 가지는 label</strong>의 <strong>파드들에 접근</strong>을 하기 위해선,<ul>
<li><strong>namespace</strong>에 <strong>purpose: production 의 label</strong>이 부여되어 있는 상태일 때,</li>
<li>tcp 연결을 통해서 80 포트로 접근할 수 있다.</li>
</ul>
</li>
</ul>
<p>라는 의미를 가지는 yaml 파일이다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0ff44270-25ca-49c1-9cb7-276a4ac73a77/image.png" /></p>
<p>네임스페이스를 만들어준 뒤에 각 네임스페이스에 pair 형태의 label을 부여해주고 위의 yaml 파일을 배포해준다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fb39bf68-31c8-437e-878b-5d3c4e6580a6/image.png" /></p>
<p>각 네임스페이스에 해당되는 파드들을 생성해준 뒤, 각 파드들에서 app: web 이 label로 설정되어 있는 파드에 접근을 시도한다면,</p>
<p>키-밸류 값이 모두 일치한 경우에만 정상적으로 응답을 받고,
그렇지 않다면 응답을 받지 못해 요청을 취소하고 종료해야 한다는 것을 확인할 수 있다.</p>
<blockquote>
<p>** label 검색 방법 **</p>
</blockquote>
<ul>
<li>namespace에 label을 부여하줬다면,
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/75a339c0-2307-4068-9a43-3d15abc3b0d7/image.png" /></li>
<li>** -L {label.key} ** 를 추가하여 등록된 라벨정보를 확인할 수 있다.
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/294b3142-a9c1-4b79-86c6-0f44a751c83d/image.png" /></li>
</ul>
<h1 id="rbac">RBAC</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ba4aa813-da50-4989-b6a9-f087b5686982/image.png" /></p>
<h2 id="account">Account</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/cb4005c7-2d83-4d89-86ab-9e19b7f3a16b/image.png" /></p>
<h2 id="service-account">Service Account</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f5ae539c-b56b-4206-a44c-625b95f68983/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0ec5d091-f3bf-40c6-a014-ffd1a904e151/image.png" /></p>
<p><strong>주의</strong>
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ebaec5b8-6c27-4bf1-8439-3f644b1b74ec/image.png" /></p>
<h4 id="해결방법-1">해결방법 1</h4>
<ul>
<li>시크릿 리소스 사용</li>
</ul>
<pre><code>apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: secloudit-secret
  namespace: default
  annotations:
    kubernetes.io/service-account.name: &quot;secloudit-serviceaccount&quot;</code></pre><pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: secloudit-namespace
spec:
  serviceAccountName: secloudit-serviceaccount
  containers:
  - name: secloudit-container
    image: busybox
    volumeMounts:
      - name: secloudit-token
        mountPath: &quot;/var/run/secrets/kubernetes.io/serviceaccount&quot;
        readOnly: true
  volumes:
    - name: secloudit-token
      secret:  
        secretName: secloudit-secret # 사용할 시크릿 객체의 이름 지정</code></pre><p>시크릿 타입 리소스의 토큰발급처를 구성해둔 뒤, 서비스어카운트를 사용하고자 할 때마다 해당 시크릿을 통해 토큰을 발급받아 사용한다.</p>
<h4 id="해결방법-2">해결방법 2</h4>
<ul>
<li>projected 볼륨 사용</li>
</ul>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: secloudit-namespace
spec:
  serviceAccountName: secloudit-serviceaccount
  containers:
  - name: secloudit-container
    image: busybox
    volumeMounts:
      - name: secloudit-token
        mountPath: &quot;/var/run/secrets/kubernetes.io/serviceaccount&quot;
        readOnly: true
  volumes:
    - name: secloudit-token
      projected:
        sources:
          - serviceAccountToken:
              path: token
              expirationSeconds: 3600
              audience: &quot;&lt;https://kubernetes.default.svc&gt;&quot;</code></pre><p>projected 사용 방식은 <strong>TokenRequest API</strong> 기술을 사용하여 물리적인 시크릿파일 없이 토큰을 발급하여 사용할 수 있도록 한다.</p>
<h3 id="clusterrole">ClusterRole</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/11da6d83-1058-49c7-b185-ccf41ee35894/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/287e26e9-3b76-4d63-a9c1-c417d56fa2bd/image.png" /></p>
<ul>
<li>클러스터롤은 접근권한에 대한 관리를 네임스페이스 단위로 하는 것이 아니라, 클러스터 단위로 제어하고자 하는 일에 대한 처리를 담당한다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e6b7036d-3fad-4805-87fc-b1d5234870d7/image.png" /></p>
<p>위와 같은 상황이 대표적으로 클러스터롤을 부여받아 클러스터 전체에 영향력을 행사할 수 있는 부분들이라고 할 수 있다.</p>
<h3 id="clusterrolebinding">ClusterRoleBinding</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/abe7d553-a55b-4807-a388-4064b3c636b4/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3c303319-6e1f-43f2-b11c-a5a4a62bb70d/image.png" /></p>
<p>이를 위해선 클러스터롤바인딩이 필요하다.</p>
<p>클러스터롤바인딩에서 클러스터와 유저를 바인딩해주는 일이 수행된다.</p>
<h3 id="실습">실습</h3>
<h4 id="클러스터롤-생성">클러스터롤 생성</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dd076cfa-049c-42d3-8b6b-720cefbd217e/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c3808eaf-3d45-46fd-81d8-95acda9773fe/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a40eba0d-8c04-4333-a1f3-10e79409a3c2/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/eea4583f-f2de-4c94-8337-6fb7c0c9e3b5/image.png" /></p>
<h4 id="서비스어카운트-생성">서비스어카운트 생성</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c556df05-bd21-44c0-a087-be128a2d9728/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0900c022-d15c-4ff2-a9e3-7081065af9db/image.png" /></p>
<h4 id="클러스터롤바인딩-생성">클러스터롤바인딩 생성</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ffc4cb0e-075a-4ed9-8fc0-37b923db3302/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3a664a58-e2da-443c-921a-c74fc759384c/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9761eeef-cb36-47b6-9c96-bb95d6452914/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c84c18f1-3da1-4c50-8c0c-7138c10b5661/image.png" /></p>
<h4 id="사용-방법">사용 방법</h4>
<p>클러스터롤, 서비스어카운트를 만들어준 뒤, 클러스터롤바인딩을 통해서 위 둘을 서로 바인딩해준다.</p>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: powerful-pod
  namespace: secloudit-namespace
spec:
  serviceAccountName: secloudit-serviceaccount  # &lt;--- 여기가 핵심!
  containers:
  - name: nginx
    image: nginx</code></pre><p>위와 같이 파드를 배포해줄 때, <strong>serviceAccountName Field</strong>를 통해서 해당 파드에서 클러스터 전역에 부여받은 클러스터롤을 행사할 수 있게 된다.</p>
<h3 id="role">Role</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/33324b85-975d-4fd5-a5e8-bcb52baf6d66/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/96be0527-b7f7-4cf3-93bc-b065563c46af/image.png" /></p>
<ul>
<li>Role 또한 허용범위와 허용권한을 설정하는 것은 동일하지만, RoleBinding과 세트로 묶여 네임스페이스 범위를 넘어서지는 못한다.</li>
</ul>
<h3 id="rolebinding">RoleBinding</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/586a602b-6610-43d5-8698-668c1589ac5e/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/215e8e2a-24bb-45e1-bbf2-bf4a7e29ec60/image.png" /></p>
<h3 id="실습-1">실습</h3>
<h4 id="롤-생성">롤 생성</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/250fd052-1ac0-4ec0-869d-3666b8387957/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e69c453d-ab29-48db-a9bb-414f9dfb24f1/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/835332f3-1575-42aa-afbd-dbdd9d6b70f1/image.png" /></p>
<h4 id="서비스어카운트-생성-1">서비스어카운트 생성</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/188566a3-71a8-4b54-8080-f39c05e068ad/image.png" /></p>
<h4 id="롤바인딩-생성">롤바인딩 생성</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/05f50085-9c8c-48d3-a551-c704bb3e95c6/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f7cf9547-dbdd-4545-a0c3-f50cfa12efb3/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/15170430-9bbb-4ca2-8050-a2afabd8fb6d/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/29f37e93-be46-4cad-ba71-c57fb252a641/image.png" /></p>
<ul>
<li>특이한 점으로는 클러스터롤과는 다르게, <strong>롤과 롤바인딩을 생성할 때에는 Namespace를 지정해줘야 한다.</strong></li>
</ul>
<h4 id="주의점">주의점</h4>
<ul>
<li><p>Role - RoleBinding 은 서로 같은 namespace 에 속해야 한다.</p>
</li>
<li><p>그리고 본질적으로 해당 서비스어카운트를 부여받은 대상이 <strong>Role</strong>의 권한을 행사할 수 있는 범위는 <strong>RoleBinding의 Namespace</strong>이다.</p>
</li>
</ul>
<h2 id="user">User</h2>
<p>진짜 유저를 생성해본 뒤,
해당 유저에게 역할을 부여해보자.</p>
<h3 id="유저-생성">유저 생성</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8c99bdd9-a128-4f08-9344-514d34cfa15e/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d40412fa-a7a2-464f-b9df-130b56cbb49d/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/cf9852c6-cdc3-4805-97ce-8a0a5283e6ed/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c75597e7-119b-4fa2-b909-408c82313a55/image.png" /></p>
<ul>
<li>만들어진 사용자가 하나의 유저로 등록되기 위해서 config-set 작업(크레덴셜 작업)이 수행되어야 한다.</li>
</ul>
<h3 id="롤--롤바인딩-생성">롤 &amp; 롤바인딩 생성</h3>
<pre><code>apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secloudit-role
  namespace: secloudit-namespace
rules:
  - apiGroups:
      - &quot;&quot;            # core api
      - &quot;extensions&quot;
      - &quot;apps&quot;
    resources:
      - &quot;deployments&quot;
      - &quot;replicasets&quot;
      - &quot;pods&quot;
      - &quot;services&quot;
    verbs:
      - &quot;get&quot;
      - &quot;list&quot;
      - &quot;watch&quot;
      - &quot;create&quot;
      - &quot;update&quot;
      - &quot;patch&quot;
      - &quot;delete&quot;</code></pre><pre><code>apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secloudit-rolebinding
  namespace: secloudit-namespace
subjects:
  - kind: User         # User or ServiceAccount
    name: secloudit
roleRef:
  kind: Role
  name: secloudit-role
  apiGroup: rbac.authorization.k8s.io</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/13c85022-3d06-4dad-ba21-3bf89d08ae27/image.png" /></p>
<h3 id="유저-접속">유저 접속</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6fa35e7c-4279-462c-8beb-b50bfa68ec47/image.png" /></p>
<p>유저가 접근할 컨텍스트를 만들어주고 해당 컨텍스트로 접근해보면,</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ef1ba486-24b0-4663-be44-cd55b8527237/image.png" /></p>
<p>부여받은 권한과 범위에 대해서만 이용이 가능해진다.</p>