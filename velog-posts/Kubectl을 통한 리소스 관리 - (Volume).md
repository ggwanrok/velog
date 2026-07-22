<h1 id="volume">Volume</h1>
<h3 id="type">Type</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6e6a8d5b-d3e1-46fc-8be8-2e7df4b2a3a9/image.png" /></p>
<ul>
<li>임시 디스크 : Pod 종속적<ul>
<li>Volume으로 생겨난 pod에만 저장되는 방식으로 파드가 사라지면 저장된 정보도 휘발된다.</li>
</ul>
</li>
<li>로컬 디스크 : 노드 종속적<ul>
<li>해당 volume 파드가 생성된 노드에서도 정보가 저장되도록 구성된다.</li>
<li>파드가 사라지더라도 노드에는 정보가 남아있어 가용성이 조금 올라간다.</li>
</ul>
</li>
<li>네트워크 디스크 <ul>
<li>노드 종속 이슈도 해결된 개념이다.</li>
</ul>
</li>
</ul>
<h3 id="속성">속성</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/eb912122-d221-4f90-a222-0ea932930804/image.png" /></p>
<ul>
<li>pv나 pvc를 만들 때 설정해야 하는 핵심 속성.<ul>
<li>volumeMode는 filesystem이 기본값이라고 한다.</li>
</ul>
</li>
</ul>
<h2 id="storageclass">StorageClass</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1176d0e6-31ef-40e6-99be-9dc8d2e9528b/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/5645d4ac-e44e-489d-b952-f75eb6f01521/image.png" /></p>
<h2 id="pv">PV</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dc9addb0-d92e-45b5-90ef-0f5559dcf499/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0876c1d7-9909-413b-aef0-8e4739c592eb/image.png" /></p>
<h2 id="pvc">PVC</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dc3010dd-ac1d-4f71-a4de-4c94d9b73199/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/99da82e1-9d92-4857-a9c7-af8d475f6ef9/image.png" /></p>
<h2 id="실습-1--임시-디스크">실습 1 : 임시 디스크</h2>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: default
spec:
  volumes:
    - name: secloudit-log-volume
      emptyDir: {}
  containers:
    - name: secloudit-log-writer
      image: busybox
      command: [&quot;/bin/sh&quot;, &quot;-c&quot;]
      args:
        - while true; do
            echo &quot;$(date)&quot; &gt;&gt; /var/log/secloudit.log;
            sleep 5;
          done
      volumeMounts:
        - name: secloudit-log-volume
          mountPath: /var/log
    - name: secloudit-log-reader
      image: busybox
      command: [&quot;/bin/sh&quot;, &quot;-c&quot;]
      args:
        - tail -f /var/log/secloudit.log
      volumeMounts:
        - name: secloudit-log-volume
          mountPath: /var/log</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c81e2854-7c74-4cf4-ad27-a5a7453bcfbd/image.png" />
위 yaml 파일로 생성된 파드로 접속하여 파드에서 정상적으로 volume이 동작하는 것을 확인할 수 있다.</p>
<blockquote>
<p>같은 동작을 디플로이먼트로 배포하였을 경우, 생성된 파드는 독립적으로 각자의 역할을 수행한다.</p>
</blockquote>
<pre><code>apiVersion: apps/v1
kind: Deployment
metadata:
  name: secloudit-deployment
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: secloudit
  template:
    metadata:
      labels:
        app: secloudit
    spec:
      volumes:
        - name: secloudit-log-volume
          emptyDir: {}
      containers:
        - name: secloudit-log-writer
          image: busybox
          command: [&quot;/bin/sh&quot;, &quot;-c&quot;]
          args:
            - while true; do
                echo &quot;$(date)&quot; &gt;&gt; /var/log/secloudit.log;
                sleep 5;
              done
          volumeMounts:
            - name: secloudit-log-volume
              mountPath: /var/log
        - name: secloudit-log-reader
          image: busybox
          command: [&quot;/bin/sh&quot;, &quot;-c&quot;]
          args:
            - tail -f /var/log/secloudit.log
          volumeMounts:
            - name: secloudit-log-volume
              mountPath: /var/log</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/0f2d6716-3b2a-4e16-bcab-f2d11b141fea/image.png" /></p>
<h2 id="실습-2--로컬-디스크">실습 2 : 로컬 디스크</h2>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  namespace: default
spec:
  containers:
  - name: secloudit-log-writer
    image: busybox
    command: [&quot;sh&quot;, &quot;-c&quot;]
    args:
    - while true; do
      echo &quot;$(date)&quot; &gt;&gt; /var/log/secloudit.log;
      sleep 10;
      done
    volumeMounts:
    - name: secloudit-log-volume
      mountPath: /var/log
  volumes:
  - name: secloudit-log-volume
    hostPath:
      path: /var/log/secloudit-logs
      type: DirectoryOrCreate</code></pre><ul>
<li>hostPath 동작 구조상, 해당 파드를 띄운 노드가 마운트 되어, 의도한 동작은 마운트된 노드에서 동작한다.<ul>
<li>/var/log/secloudit.log 파일은 마운트된 노드에 생성된다.</li>
</ul>
</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a6933c53-da40-4d7b-a67a-2d42e374e09d/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/12afea57-7f03-4fa5-b6ac-162239db8405/image.png" /></p>
<p>위의 yaml 파일로 생성된 파드가 생성된 노드를 확인한 뒤,</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f8fb2805-cfb3-487d-9d78-5b254f45fa3e/image.png" /></p>
<p>해당 노드로 접속하여 yaml 파일에 작성한 경로로 접근하면
의도한 대로 동작하고 있음을 확인할 수 있다.</p>
<blockquote>
</blockquote>
<p>여기서 <strong>마운트</strong>라는 개념을 한번 짚고 넘어가면 좋을 것 같다.
파드에 접속을 해서도 컨테이너가 동작하여 저장된 파일 정보를 확인할 수 있다.
단, 이는 파드에서 일을 하는 것이 아닌 <strong>노드의 저장소에 마운트하여 가져온 정보</strong>라는 것을 알아야 한다.</p>
<ul>
<li>노드에 저장소로 사용하던 동일한 경로와 동일한 파일이 남아있을 경우, 파드를 새로 띄운 경우라고 하더라도 이전의 정보까지 파드에서 확인할 수 있게 된다.<ul>
<li>파드에서 확인되는 정보는 파드가 찍은게 아니라, 노드에 마운트하여 거기 있는 정보를 가져오는 형식이기 때문이다.</li>
</ul>
</li>
</ul>
<h2 id="실습-3--정적-프로비저닝">실습 3 : 정적 프로비저닝</h2>
<h3 id="알아둘-점">알아둘 점.</h3>
<p>앞선 개념 공부시간에, '정적 프로비저닝은 동적 프로비저닝에서만 사용되는 <strong>스토리지 클래스</strong>는 사용하지 않는다.' 라고 했었는데, <strong>스토리지의 이름</strong>을 설정하기 위해서 사용하기는 한다.
단, provisioner 필드에 <strong>no-provisioner</strong>라고 등록한 뒤에 사용한다.</p>
<h3 id="전처리-작업">전처리 작업</h3>
<p>정적 프로비저닝인 만큼, pv로 관리자가 만들 실제 volume에 대해서 해당 스토리지 경로를 <strong>미리 구성</strong>해야하고 <strong>권한 부여</strong>를 해둬야 한다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a2920bf4-23d0-452b-a5ad-cd2d31b6e79f/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/725f743c-d89e-42d7-b9bf-e0966ee082b1/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/73fb98c3-6a24-49c0-b11f-de117cebe93f/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/40f4ff45-5f2e-4897-93d6-e16f7063a764/image.png" /></p>
<h3 id="storageclass-생성">StorageClass 생성</h3>
<pre><code>apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: secloudit-storageclass
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
provisioner: kubernetes.io/no-provisioner
reclaimPolicy: Delete
volumeBindingMode: Immediate</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/c0449e7f-fa36-467c-a053-d16b4976f855/image.png" /></p>
<ul>
<li>배포 방법과 확인 방법은 위와 같다.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4c02f2f8-2cb2-4b46-b6c6-155e9b850c7e/image.png" /></p>
<h3 id="pv-생성">PV 생성</h3>
<pre><code># 워커노드 1에 만들어질 저장소에 대한 pv 
apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv1
spec:
  storageClassName: secloudit-storageclass
  persistentVolumeReclaimPolicy: Delete
  capacity:
    storage: 1G
  accessModes:
    - ReadWriteOnce
  local:
    path: /data/volumes/pv1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - mgr-cluster2

# 워커노드 2에 만들어질 저장소에 대한 pv
apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv2
spec:
  storageClassName: secloudit-storageclass
  persistentVolumeReclaimPolicy: Delete
  capacity:
    storage: 2G
  accessModes:
    - ReadWriteOnce
  local:
    path: /data/volumes/pv2
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - mgr-cluster3

# 워커노드 3에 만들어질 저장소에 대한 pv
apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv3
spec:
  storageClassName: secloudit-storageclass
  persistentVolumeReclaimPolicy: Delete
  capacity:
    storage: 3G
  accessModes:
    - ReadWriteOnce
  local:
    path: /data/volumes/pv3
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - mgr-cluster4</code></pre><ul>
<li>nodeAffinity : pv로 사용할 노드패스에 대한 정보를 담은 필드!</li>
<li>values 에 사용할 노드의 Hostname을 기입해 넣어야 한다! ( ex) mgr-cluster4 )</li>
<li>local 필드에 사용할 스토리지 패스를 미리 지정해둬야하는 것을 잊지말자.</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/57913814-911f-4704-a87a-3515b858f12f/image.png" /></p>
<p>배포를 진행해주고, 위와 같은 방법으로 확인할 수 있다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/ac415685-98ba-442a-9f85-a89f39237a48/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/56851160-7cfa-4bba-b983-7095d510e201/image.png" /></p>
<p>정상적으로 PV가 배포된 것을 확인할 수 있다.
단, 현재 PV만 만들어지고, PVC와 연계된 것이 아니기 때문에, <strong>Available</strong> 상태로 머물러 있다.</p>
<h3 id="pvc-생성">PVC 생성</h3>
<pre><code># pvc1 생성 요청
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: secloudit-pvc1
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1G

# pvc2 생성 요청
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: secloudit-pvc2
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 2G

# pvc3 생성 요청
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: secloudit-pvc3
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 3G</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/29ae38c6-2b20-49b5-870e-f0eef82ee166/image.png" /></p>
<p>배포를 진행해주고 위와 같은 방법으로 확인할 수 있다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/21d577d7-97f6-46c9-b786-c6f5904707c8/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/9dea1393-c670-4bba-b13d-26263bc80e06/image.png" /></p>
<p>PVC를 배포해준 뒤에는 PV의 상태가 각 PVC와 배칭되어 <strong>Bound</strong> 상태로 변화했음을 확인할 수 있다.</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f4bc6c48-1371-4e8e-9d6b-10ce3d4be4d8/image.png" /></p>
<p>물론 PVC 또한 위와 같은 상태 확인이 가능하다.</p>
<h3 id="pod-배포">Pod 배포</h3>
<pre><code># pvc1 을 볼륨으로 사용할 파드
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod1
  labels:
    name: app
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo &quot;Platform as a service!&quot; &gt; /mnt/secloudit-1.log &amp;&amp; sleep 3600']
    volumeMounts:
      - name: secloudit-local-volume
        mountPath: /mnt
  volumes:
    - name: secloudit-local-volume
      persistentVolumeClaim:
        claimName: secloudit-pvc1

# pvc2 을 볼륨으로 사용할 파드
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod2
  labels:
    name: app
spec:
  containers:
  - name: app
    image: busybox
    command: [&quot;/bin/sh&quot;, &quot;-c&quot;]
    args:
      - while true; do
          date &gt;&gt; /mnt/secloudit-2.log;
          sleep 5;
        done
    volumeMounts:
      - name: secloudit-local-volume
        mountPath: /mnt
  volumes:
    - name: secloudit-local-volume
      persistentVolumeClaim:
        claimName: secloudit-pvc2

# pvc3 을 볼륨으로 사용할 파드
apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod3
  labels:
    name: app
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
      - name: secloudit-local-volume
        mountPath: /var/log/nginx
  volumes:
    - name: secloudit-local-volume
      persistentVolumeClaim:
        claimName: secloudit-pvc3</code></pre><p>위와 같이 Pod를 띄워줄 수 있다.</p>
<ul>
<li>사용할 Volume에 대해서 volumes.name 과 컨테이너의 VolumeMounts.name 정보가 잘 맞춰져 있어야 한다.</li>
<li>컨테이너 속에서의 마운트 패스는 해당 파드에서 작업될 경로를 의미한다.<ul>
<li>실제 PV에서 선언되어 있는 경로와는 달라도 된다.</li>
</ul>
</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4f8d640e-7853-4254-b4f6-c168a7badf1d/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/31858c67-4e71-461c-a45d-2c598f00f438/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8971f682-3215-4560-80cf-26cee979c7f5/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/6b33e5e9-4b8c-433f-9fdd-728a0df61ff7/image.png" /></p>
<p>이렇게 배포된 Pod는 필드로 선언한 PVC에 마운트된 PV를 볼륨으로 잘 사용하고 있는 것을 확인할 수 있다.</p>
<p>각 워커노드에 잘 기록된 것을 확인할 수 있고, 작업한 파드 자체에서도 확인할 수 있다!</p>
<ul>
<li>파드에서 작업할 일이 수행되는 경로와 노드에서 작업되는 일이 수행되는 경로는 달라도 된다는 것을 인지하자!!<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/377a808c-1ee7-4b3b-bb89-21b6ce24a565/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/91240424-b10e-46af-813f-407d40c38658/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/28ef4f95-0182-4888-b3e2-decab89fa992/image.png" /></p>
</blockquote>
</li>
</ul>
<h2 id="실습-4--정적-프로비저닝-nfs">실습 4 : 정적 프로비저닝 (NFS)</h2>
<h3 id="storageclass-생성-1">StorageClass 생성</h3>
<pre><code>apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: secloudit-storageclass
  annotations:
    storageclass.kubernetes.io/is-default-class: 'true'
provisioner: kubernetes.io/no-provisioner
reclaimPolicy: Delete
volumeBindingMode: Immediate</code></pre><ul>
<li>앞서 배포해뒀다면, 다시 안해도 된다.</li>
</ul>
<h3 id="pv-1">PV</h3>
<pre><code>apiVersion: v1
kind: PersistentVolume
metadata:
  name: secloudit-pv
spec:
  storageClassName: secloudit-storageclass
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  nfs:
    path: &quot;/home/share/nfs&quot;
    server: 192.168.1.23</code></pre><ul>
<li>사용할 NFS의 IP주소를 입력하여 PV를 NFS로 사용할 수 있다.</li>
</ul>
<h3 id="pvc-1">PVC</h3>
<pre><code>apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: secloudit-pvc
spec:
  storageClassName: secloudit-storageclass
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/a2c7c8f7-d80a-4b38-87dd-a2059f0227a3/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/abcbc41d-2863-432b-85b9-2fa1c3a4cd5a/image.png" /></p>
<p>위 파일들을 배포하여 바운드된 것을 확인할 수 있다.</p>
<h3 id="pod-배포-1">Pod 배포</h3>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  labels:
    name: app
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo &quot;Platform as a service!&quot; &gt; /mnt/secloudit-nfs.log &amp;&amp; sleep 3600']
    volumeMounts:
      - name: secloudit-local-volume
        mountPath: /mnt
  volumes:
    - name: secloudit-local-volume
      persistentVolumeClaim:
        claimName: secloudit-pvc</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/42ea027b-a046-4250-a98b-20631160ed15/image.png" /></p>
<p>만들어준 파드가 running이라면,</p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/500935bc-be0f-4945-80c1-3ce40251a152/image.png" /></p>
<p>연결된 nfs에서도 외부스토리지로서의 동작이 정상적으로 수행되는 것을 확인할 수 있다.</p>
<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/32913e0d-cc24-4f48-9d7d-59e8ca776275/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4de18352-0b91-447a-93f9-e383eb187b17/image.png" /></p>
</blockquote>
<h2 id="실습-5--동적-프로비저닝">실습 5 : 동적 프로비저닝</h2>
<p>동적 프로비저닝을 위해선 no-provisioner 가 적힌 스토리지클래스가 아닌,</p>
<p>진짜 스토리지클래스를 사용해야 한다.</p>
<p>본실습 때에는 <strong>Helm Chart</strong>에서 제공하는 스토리지클래스를 사용할 것이다.</p>
<h3 id="storageclass-1">StorageClass</h3>
<pre><code>nfs:
  server: {NFS Server IP}                     # NFS Server IP 입력
  path: /home/share/nfs                       # NFS Export Path (Provisioner가 사용할 디렉터리)

storageClass:
  provisionerName: secloudit-nfs-provisioner  # StorageClass에 사용할 Provisioner 이름 설정
  defaultClass: true                          # 기본 StorageClass로 지정할지 여부
  name: secloudit-storageclass                # 생성할 StorageClass 이름 설정
  reclaimPolicy: Retain                       # PV Reclaim 정책 (Retain: PV 유지, Delete: 자동 삭제)
  allowVolumeExpansion: false                 # PVC 확장 기능 여부
  archiveOnDelete: false                      # PVC 삭제 시 NFS 디렉터리 아카이브 여부</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dfee5c8b-98c5-4a67-a591-2bf673c2fea8/image.png" /></p>
<ul>
<li>위 yaml 파일을 자세히 보면 <strong>apiVersion</strong>이나, <strong>kind</strong>와 같은 기존 kubectl 배포파일과 형태가 다른 것을 확인할 수 있다.</li>
<li>Helm Chart의 스토리지클래스 사용을 위해 <strong>Helm CLI</strong>를 통한 배포를 진행해야 한다.</li>
</ul>
<h4 id="helm-cli-설치-및-sc-배포">Helm CLI 설치 및 SC 배포</h4>
<pre><code># 1. Helm Repo 추가
$ helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner
$ helm repo update nfs-subdir-external-provisioner
# 2. Provisioner 설치
$ helm install secloudit-nfs-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  -f values.yaml --version 4.0.18
# 3. 설치 확인
$ helm list -n default
$ kubectl get all -l app=nfs-subdir-external-provisioner
$ kubectl get storageclass</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d7ea0407-4ec2-4dd2-8ba4-8d69c72cf625/image.png" /></p>
<ul>
<li>helm cli 를 통한 배포를 진행하기 위해서 values.yaml 과 같은 파일이름까지 정해진대로 행동해야 한다.</li>
</ul>
<blockquote>
<p>만약, 반복 연습중이라면 storageclass, pvc 등을 삭제하고 진행한다고 하더라고 
기존 작업이 완전히 삭제되지 않아 추후 pvc 생성 과정에서 pending 될 수 있다.
만약 막힌다면, 아래와 같은 작업을 진행해주도록 하자.</p>
</blockquote>
<pre><code># 1. 기존에 설치된 릴리스 삭제
helm uninstall secloudit-nfs-provisioner
# 2. 혹시 남아있을지 모르는 StorageClass 확인 및 삭제
# (헬름 삭제 시 같이 지워졌을 수도 있지만, 확실하게 하기 위함)
kubectl get sc
# 만약 secloudit-storageclass가 보인다면 아래 명령어로 삭제:
kubectl delete sc secloudit-storageclass</code></pre><h3 id="pvc-2">PVC</h3>
<pre><code>apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: secloudit-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: secloudit-storageclass
  resources:
    requests:
      storage: 1Gi</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b30161a8-728b-4a8d-906f-2502538752f1/image.png" /></p>
<ul>
<li>배포된 pvc를 통해서 동적프로비저너에 의해서 바운드 된 pv를 확인할 수 있다.<ul>
<li>위의 이미지는 앞선 실습을 이어서 하는 과정이기에 pvc 이름에 dynamic이 추가되었다.</li>
<li>이처럼 작성할 경우 아래 pod에서도 사용할 pvc에 대해서 dynamic을 추가하여 작성해야 한다.</li>
</ul>
</li>
</ul>
<pre><code>apiVersion: v1
kind: Pod
metadata:
  name: secloudit-pod
  labels:
    name: app
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'echo &quot;Platform as a service!&quot; &gt; /mnt/secloudit.log &amp;&amp; sleep 3600']
    volumeMounts:
      - name: secloudit-local-volume
        mountPath: /mnt
  volumes:
    - name: secloudit-local-volume
      persistentVolumeClaim:
        claimName: secloudit-pvc</code></pre><ul>
<li>pvc를 지정하여 pod를 배포해준다면,</li>
</ul>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/1dec7b08-7904-47aa-9346-d419b3d12ced/image.png" /></p>
<ul>
<li>조회된 pv로 접근하여 volume으로의 동작을 정상적으로 수행되었음을 확인할 수 있다.</li>
</ul>
<blockquote>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f76d57da-e13c-4f41-93a1-701e997688e3/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/7843f1c7-cf16-4725-b1c0-e5247240e513/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/d163f778-a5ef-43cd-93e1-e1d3726abc18/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f9404f78-1365-4bec-843a-c87f2046f8ea/image.png" /></p>
</blockquote>