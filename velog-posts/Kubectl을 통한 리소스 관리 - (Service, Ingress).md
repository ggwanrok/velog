<h1 id="nerwork">Nerwork</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d1e9629b-b362-4ad0-bf66-e08528ba06cb/image.png" /></p>
<ul>
<li>외부로부터의 파드까지 접근방법은 위와 같다.</li>
</ul>
<p>이를 위해서 service를 nodePort로 붙여줄 것이다.
또한 여기서 그치는 것이 아니라, 로드밸런서를 통해서 외부에서의 접근을 작업할 수 있도록 해볼 것이다.</p>
<p>이를 위해서 service, ingress 리소스에 대해서 더 알아보자.</p>
<h2 id="service">Service</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/27312d18-015a-4ef5-9f05-59de0154103a/image.png" /></p>
<h3 id="실습-1--nodeport를-이용한-nginx-접속">실습 1 : NodePort를 이용한 Nginx 접속</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b7cdf200-09fb-457f-aef8-892e5c8ba53e/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/434e2e80-deec-46d5-b93d-57b06ae13c10/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/98d74567-4fdc-43a7-991d-f438f9674828/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fd6cb32d-0109-4a84-9715-c299abb42aef/image.png" /></p>
<ul>
<li>kubectl get svc 를 통해서 해당 서비스에 부여되어 있는 nodeport 번호와 쿠버네티스 아이피를 통해서 접근할 수 있다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/632a21e8-f41a-4711-ad23-6642d3be3a67/image.png" /></p>
<ul>
<li>또한 <strong>kubectl edit svc {service name}</strong> 명령을 통해 노드포트 번호를 내 의도대로 변경할 수 있다.</li>
</ul>
<h3 id="실습-2--clusterip-타입-사용">실습 2 : ClusterIp 타입 사용</h3>
<p><strong>ClusterIp</strong> : 내부 파드들 네트워킹에서 사용되는 타입이다.</p>
<ul>
<li><p>Deployment</p>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
name: secloudit-deployment
namespace: default
labels:
  app: hello
spec:
replicas: 3
selector:
  matchLabels:
    app: hello
template:
  metadata:
    labels:
      app: hello
  spec:
    containers:
    - name: nginx
      image: nginxdemos/hello:plain-text
      ports:
      - name: http
        containerPort: 80
        protocol: TCP</code></pre></li>
<li><p>Service</p>
<pre><code>apiVersion: v1
kind: Service
metadata:
name: secloudit-service
namespace: default
labels:
  app: hello
spec:
type: ClusterIP
ports:
- name: http
  protocol: TCP
  port: 8080
  targetPort: 80
selector:
  app: hello</code></pre></li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3e220ddd-594d-4c80-8a7f-d6a6990c4ed7/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a4dfd926-7510-481a-8a18-54c0e0441663/image.png" /></p>
<p>위의 yaml 파일을 배포해주면 성공적으로 서비스가 생성된다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/fcc05960-fa85-4b04-880a-6eb22fb515b9/image.png" /></p>
<p>파드가 잘 뜨는 것을 확인할 수 있다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/28cb0476-ddb0-4f6b-add8-28fe71d87a6d/image.png" /></p>
<p>배포한 클러스터에서 접근할 수 있고,</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3ca0135d-e293-4ff4-b7ec-f8dfefa826b1/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a1d31bc7-cd6b-4eba-ada6-20f7af7268e1/image.png" /> 클러스터 내부에서 파드를 만들어 접속을 진행해보면 연결된 deployment에서의 각 pod들에 대해서 잘 접근됨을 확인할 수 있다.</p>
<h3 id="실습-3--loadbalancer-타입-사용">실습 3 : LoadBalancer 타입 사용</h3>
<ul>
<li>Deployment<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
name: secloudit-deployment
namespace: default
labels:
  app: nginx
spec:
replicas: 3
selector:
  matchLabels:
    app: nginx
template:
  metadata:
    labels:
      app: nginx
  spec:
    containers:
    - name: nginx
      image: nginx
      ports:
      - containerPort: 80</code></pre></li>
<li>Service<pre><code>apiVersion: v1
kind: Service
metadata:
name: secloudit-service
namespace: default
spec:
type: LoadBalancer
selector:
  app: nginx
ports:
  - port: 80
    targetPort: 80</code></pre></li>
</ul>
<p>쿠버네티스 실습 초반부에 클러스터 환경을 구축하면서, 마스터 플레인에 두번째 네트워크 인터페이스를 달아줬었는데, 네트워크 인터페이스에 연결된 서비스가 바로 <strong>로드벨런서</strong>이다.</p>
<blockquote>
<p>플로팅 아이피를 통해서 외부 접근을 받은 뒤, 내부 아이피 망을 통해서 클러스터에 접근할 수 있도록 해준 것이 로드벨런서의 역할이다.</p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8738dfde-f7ef-48d8-8e26-ec25ab74ea71/image.png" />
위의 yaml 파일을 배포해주면 위 사진과 같은 형태의 LoadBalancer Service가 생성된다.</p>
<p>여기선 <strong>external-ip</strong>라는 특이점이 존재한다.
이를 통해서 로드밸런서 서비스는 외부에 하나의 ip를 노출하게 되고,
결과적으로 서브넷 대역 ip를 노출하게 되는 것이다.</p>
<p>물론! 이 또한 내부 ip이다.</p>
<p>성공적으로 접속하기 위해선, 해당 ip에 대해서 네트워크 인터페이스를 지정하고, 해당 네트워크 인터페이스에 플로팅아이피를 할당하여 접근하도록 한다.</p>
<blockquote>
<p><strong>실습 자료</strong>
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/43a73d87-4eec-45a9-9072-70a209c3f492/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/e11e7045-c199-4b42-9962-78705b2967a6/image.png" /></p>
</blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/63e92d2f-91eb-432d-b356-796da29af433/image.png" /></p>
<ul>
<li>이를 통해 성공적으로 로드벨런서 서비스를 이용하여 nginx 접속을 진행했다.</li>
</ul>
<h2 id="ingress">Ingress</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b4c95ff3-4ce2-464d-ba85-6e73d89d5f4f/image.png" /></p>
<h3 id="실습-1--nginx-접속하기">실습 1 : Nginx 접속하기</h3>
<blockquote>
<p>실습 1을 진행하기 위해서는 환경변수 파일에 사용할 도메인주소를 등록해둬야 한다.
뒤의 실습으로만 잔행해봐도 충분하다.</p>
</blockquote>
<h4 id="deployment-배포">Deployment 배포</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c0d7b290-c704-4ec1-a419-352125644893/image.png" /></p>
<h4 id="service-배포">Service 배포</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ec3f237a-cc26-4ba8-b247-37c07e8a363f/image.png" /></p>
<h4 id="ingress-배포">Ingress 배포</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3291578a-d115-4c77-88fd-af1e966adbf4/image.png" /></p>
<ul>
<li>사용할 Domain 주소를 rule field를 통해서 채운다.<ul>
<li>/={@@} : 루트 주소에 대한 의미</li>
<li>@@ : 연계될 서비스와 접근 포트번호</li>
</ul>
</li>
</ul>
<h4 id="접속">접속</h4>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/db692fb4-bd35-4324-a2dc-cd0ec13fcf74/image.png" /></p>
<h3 id="실습-2--ingress를-통한-여러-service-연계">실습 2 : Ingress를 통한 여러 Service 연계</h3>
<h4 id="실습-2와-실습-3-실습-4에서-사용할-deployment-service">실습 2와 실습 3, 실습 4에서 사용할 Deployment, Service</h4>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  labels:
    app: &quot;grafana&quot;
spec:
  replicas: 1
  selector:
    matchLabels:
      app: &quot;grafana&quot;
  template:
    metadata:
      labels:
        app: &quot;grafana&quot;
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - name: http
          containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  labels:
    app: &quot;grafana&quot;
spec:
  type: ClusterIP
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 3000
  selector:
    app: &quot;grafana&quot;
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      name: hello
      labels:
        app: hello
    spec:
      containers:
      - name: nginx
        image: nginxdemos/hello:plain-text
        ports:
        - name: http
          containerPort: 80
          protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: hello
  labels:
    app: hello
spec:
  type: ClusterIP
  ports:
  - name: http
    protocol: TCP
    port: 8080
    targetPort: 80
  selector:
    app: hello
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpd
  labels:
    app: &quot;httpd&quot;
spec:
  replicas: 1
  selector:
    matchLabels:
      app: &quot;httpd&quot;
  template:
    metadata:
      labels:
        app: &quot;httpd&quot;
    spec:
      containers:
      - name: httpd
        image: httpd:latest
        ports:
        - name: http
          containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: httpd
  labels:
    app: &quot;httpd&quot;
spec:
  type: ClusterIP
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 80
  selector:
    app: &quot;httpd&quot;</code></pre><h4 id="ingress-배포-1">Ingress 배포</h4>
<pre><code>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /hello
        pathType: Prefix
        backend:
          service:
            name: hello
            port:
              name: http
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              name: http
  - http:
      paths:
      - path: /httpd
        pathType: Prefix
        backend:
          service:
            name: httpd
            port:
              name: http</code></pre><ul>
<li><p>ingressClassName을 nginx로 한다면
어노테이션부터 스펙까지는 쿠버네티스에서 지정한 템플릿이기에 그대로 사용하자.</p>
</li>
<li><p>rules 의 하위 필드들을 통해서 접근 url에 따른 연계 서비스로의 연결을 지원한다.</p>
<ul>
<li>grafana를 루트로 배치하는 이유 : 기본적으로 루트로 받아서 /login 으로 리다이렉트 되는 구조이기 때문이다.</li>
</ul>
</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d6d6ad20-e6c3-4579-aad4-25d808c1206d/image.png" /></p>
<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9e2950ea-4dfa-409f-97b5-433d66b9685b/image.png" /></p>
</blockquote>
<h3 id="실습-3--host를-지정한-ingress">실습 3 : host를 지정한 Ingress</h3>
<pre><code>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: hello.{공인IP주소}.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello
            port:
              name: http
  - host: grafana.{공인IP주소}.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              name: http
  - host: httpd.{공인IP주소}.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: httpd
            port:
              name: http</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c8b54b01-b456-45ef-a8c3-8ca4c31e015f/image.png" /></p>
<h3 id="실습-4--공통된-host-를-사용하여-세부-주소로-서비스를-분할하는-경우">실습 4 : 공통된 Host 를 사용하여 세부 주소로 서비스를 분할하는 경우</h3>
<pre><code>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: ingress-practice.{공인 IP}.nip.io
    http:
      paths:
      - path: /hello
        pathType: Prefix
        backend:
          service:
            name: hello
            port:
              name: http
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              name: http
      - path: /httpd
        pathType: Prefix
        backend:
          service:
            name: httpd
            port:
              name: http
</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dced4d7d-a057-4fdc-8907-6bc415b11c79/image.png" /></p>
<p>이렇게 여러가지 방법으로 게이트웨이 역할을 하는 인그레스의 사용법을 알아보았다.</p>
<blockquote>
<p>아래와 같은 방식으로, 추가로 사용하고 싶은 서비스를 배포해준 뒤 (아래의 경우 Nginx)
Ingress 경로에 의도한 service.name을 기입하여 적용하여 사용할 수 있다.</p>
</blockquote>
<ul>
<li>Deployment &amp; Service<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
name: grafana
labels:
  app: &quot;grafana&quot;
spec:
replicas: 1
selector:
  matchLabels:
    app: &quot;grafana&quot;
template:
  metadata:
    labels:
      app: &quot;grafana&quot;
  spec:
    containers:
    - name: grafana
      image: grafana/grafana:latest
      ports:
      - name: http
        containerPort: 3000</code></pre></li>
</ul>
<hr />
<p>apiVersion: v1
kind: Service
metadata:
  name: grafana
  labels:
    app: &quot;grafana&quot;
spec:
  type: ClusterIP
  ports:</p>
<ul>
<li>name: http
protocol: TCP
port: 80
targetPort: 3000
selector:
app: &quot;grafana&quot;</li>
</ul>
<hr />
<p>apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      name: hello
      labels:
        app: hello
    spec:
      containers:
      - name: nginx
        image: nginxdemos/hello:plain-text
        ports:
        - name: http
          containerPort: 80
          protocol: TCP</p>
<hr />
<p>apiVersion: v1
kind: Service
metadata:
  name: hello
  labels:
    app: hello
spec:
  type: ClusterIP
  ports:</p>
<ul>
<li>name: http
protocol: TCP
port: 8080
targetPort: 80
selector:
app: hello</li>
</ul>
<hr />
<p>apiVersion: apps/v1
kind: Deployment
metadata:
  name: httpd
  labels:
    app: &quot;httpd&quot;
spec:
  replicas: 1
  selector:
    matchLabels:
      app: &quot;httpd&quot;
  template:
    metadata:
      labels:
        app: &quot;httpd&quot;
    spec:
      containers:
      - name: httpd
        image: httpd:latest
        ports:
        - name: http
          containerPort: 80</p>
<hr />
<p>apiVersion: v1
kind: Service
metadata:
  name: httpd
  labels:
    app: &quot;httpd&quot;
spec:
  type: ClusterIP
  ports:</p>
<ul>
<li>name: http
protocol: TCP
port: 80
targetPort: 80
selector:
app: &quot;httpd&quot;</li>
</ul>
<hr />
<p>apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80</p>
<hr />
<p>apiVersion: v1
kind: Service
metadata:
  name: secloudit-service   # Ingress가 가리키는 이름과 일치해야 함
  labels:
    app: nginx
spec:
  type: ClusterIP
  selector:
    app: nginx              # Deployment의 라벨과 일치해야 함
  ports:</p>
<ul>
<li>name: http              # 중요: Ingress에서 port name: http를 찾으므로 꼭 넣어줘야 함!
protocol: TCP
port: 80
targetPort: 80<pre><code>- Ingress</code></pre>apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
name: path
annotations:
nginx.ingress.kubernetes.io/rewrite-target: /
spec:
ingressClassName: nginx
rules:</li>
<li>host: ingress-practice.{공인 IP}.nip.io
http:
  paths:<ul>
<li>path: /hello
pathType: Prefix
backend:
  service:<pre><code>name: hello
port:
  name: http</code></pre></li>
<li>path: /
pathType: Prefix
backend:
  service:<pre><code>name: grafana
port:
  name: http</code></pre></li>
<li>path: /httpd
pathType: Prefix
backend:
  service:<pre><code>name: httpd
port:
  name: http</code></pre></li>
<li>path: /nginx
pathType: Prefix
backend:
  service:<pre><code>name: secloudit-service
port:
  name: http</code></pre><pre><code>- Result
![](https://velog.velcdn.com/images/klmcw1004/post/4e607742-d1a2-48ca-a8d5-eae98082bcd8/image.png)</code></pre></li>
</ul>
</li>
</ul>