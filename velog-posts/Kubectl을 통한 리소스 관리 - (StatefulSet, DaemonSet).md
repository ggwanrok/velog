<h1 id="statefulset">StatefulSet</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f6d15ea3-00e5-4862-8b8f-dc2e92eebd87/image.png" /></p>
<p>파드가 고유한 네트워크 아이피와 스토리지를 가지고 순차적으로 생성되고 순차적으로 삭제되는 구조로, 
msa 에서 활용되기 좋은 구조를 가진다.</p>
<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8f772348-1f84-4dee-a4be-7181a89e1899/image.png" /></p>
</blockquote>
<p>각 스테이트풀 파드는 고유의 역할을 부여받아 수행되기 때문에, deployment-pod의 구조의 로드벨런싱과는 다르다.</p>
<p>이는 <strong>HeadLess Service</strong>를 통해서 사용된다.</p>
<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3226f600-f499-499d-ac60-f303ff802ae7/image.png" /></p>
</blockquote>
<ul>
<li>각각의 파드가 고유의 역할을 부여받고 수행되는 스테이트풀셋은 결국 지목하여 호출되는 구조인 헤드리스 구조가 적합한 구조라고 할 수 있다.</li>
</ul>
<pre><code>apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: secloudit-statefulset
  namespace: secloudit-namespace
spec:
  serviceName: &quot;secloudit-service&quot;
  replicas: 3
  updateStrategy:
    type: OnDelete
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
        image: nginx:1.21
      volumes:
      - name: secloudit-volume
        emptyDir: {}</code></pre><ul>
<li>serviceName 필드를 통해서 헤드리스서비스의 이름을 지정할 수 있게 된다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/cf13c95a-3028-4c79-b2c8-ec680fdbe796/image.png" /></p>
<h2 id="응용">응용</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/de32194a-85f5-4ab8-9cfe-2064d38e7cce/image.png" /></p>
<p>statefulSet 리소스를 이용하여 위와 같은 정적 프로비저닝 구조의 저장소를 구축할 수 있다.</p>
<h3 id="sc">SC</h3>
<pre><code>kind: StorageClass
apiVersion: storage.k8s.io/v1
metadata:
  name: secloudit-storageclass
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer</code></pre><h3 id="pv">PV</h3>
<pre><code># 첫번째 PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv-0
  labels:
    type: local
spec:
  storageClassName: secloudit-storageclass
  claimRef:
    name: seclouditvolume-seclouditsts-0
    namespace: secloudit-namespace
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  local:
    path: /mnt/common
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - edu5-cluster2         
---
# 두번째 PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv-1
  labels:
    type: local
spec:
  storageClassName: secloudit-storageclass
  claimRef:
    name: seclouditvolume-seclouditsts-1
    namespace: secloudit-namespace
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  local:
    path: /mnt/common
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - edu5-cluster3
---
# 세번째 PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv-2
  labels:
    type: local
spec:
  storageClassName: secloudit-storageclass
  claimRef:
    name: seclouditvolume-seclouditsts-2
    namespace: secloudit-namespace
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  local:
    path: /mnt/common
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - edu5-cluster4</code></pre><ul>
<li>물론 해당 PV를 정상적으로 이용하기 위해선 이용하고자 하는 저장소에 <strong>/mnt/common</strong> 경로가 존재하고, 권한을 부여받은 상태여야 한다.</li>
</ul>
<h3 id="pvc">PVC</h3>
<pre><code># 첫번째 PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: seclouditvolume-seclouditsts-0
  namespace: secloudit-namespace
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi

---
# 두번째 PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: seclouditvolume-seclouditsts-1
  namespace: secloudit-namespace
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi

---
# 세번째 PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: seclouditvolume-seclouditsts-2
  namespace: secloudit-namespace
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi</code></pre><h3 id="service">Service</h3>
<pre><code>apiVersion: v1
kind: Service
metadata:
  name: secloudit-service
  namespace: secloudit-namespace
  labels:
    app: nginx
spec:
  ports:
  - port: 80
    name: secloudit-port
  clusterIP: None
  selector:
    app: nginx</code></pre><ul>
<li>StatefulSet을 사용하기 위한 Headless Service 를 배포해준다.<ul>
<li><strong>clusterIP: None</strong>을 통해 헤드리스 서비스로 동작하도록 구성한다.</li>
</ul>
</li>
</ul>
<h3 id="statefulset-1">StatefulSet</h3>
<pre><code>apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: seclouditsts
  namespace: secloudit-namespace
spec:
  serviceName: &quot;secloudit-service&quot;
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
      - name: secloudit-container
        image: busybox
        command: ['sh', '-c', 'echo &quot;Platform as a service!&quot; &gt; /mnt/secloudit.log &amp;&amp; sleep 3600']
        volumeMounts:
        - name: seclouditvolume
          mountPath: /mnt
  volumeClaimTemplates:
  - metadata:
      name: seclouditvolume
    spec:
      accessModes: [ &quot;ReadWriteOnce&quot; ]
      storageClassName: &quot;secloudit-storageclass&quot;
      resources:
        requests:
          storage: 1Gi</code></pre><p>statefulSet까지 배포해준다면 각 statefulset의 pod들과 연결된 저장소에 정보가 잘 저장된다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/be0a528d-2e9d-4019-9862-f9a60a8cc837/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/7fac616f-09b6-43b7-aa82-df9d8f6df5a5/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8a20bb0f-dbb4-4833-b00e-4291c3106c41/image.png" /></p>
<h1 id="daemonset">DaemonSet</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d5d0d1f0-981a-486c-9c51-eb332058677b/image.png" /></p>
<pre><code>apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: secloudit-daemonset
  namespace: kube-system  #로그 수집기는 관리용 파드나 설정에 해당 되므로 kube-system 네임스페이스로 지정
  labels:
    k8s-app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations: # 이 톨러레이션(toleration)은 데몬셋이 컨트롤 플레인 노드에서 실행될 수 있도록 만든다.
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      - key: node-role.kubernetes.io/master
        operator: Exists
        effect: NoSchedule
      containers:
      - name: secloudit-container
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
        volumeMounts:
        - name: secloudit-log
          mountPath: /var/log
      terminationGracePeriodSeconds: 30
      volumes:
      - name: secloudit-log
        hostPath:
          path: /var/log</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f5bee395-9c80-41c0-9704-0fa868fcb02f/image.png" /></p>
<ul>
<li>위의 yaml 파일을 배포하여 사진과 같은 실행 성공을 확인할 수 있다.</li>
</ul>