<h1 id="job">Job</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/666f4620-6a9b-465c-9ffa-73da8011598d/image.png" /></p>
<p>deployment 리소스에서는 replicaset이 관리할 파드의 갯수를 지정했던 것처럼,
job에서는 <strong>수행하는 일이나, 시점, 방식 등</strong>을 설정할 수 있다.</p>
<h2 id="생성">생성</h2>
<p>** job 실행 당시 시점을 로그로 출력 **
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/da90e240-4442-4905-9dc1-be4ba9de037b/image.png" /></p>
<p>** 10초 대기 후 job 수행 **
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/96ff15d0-499d-4554-8faf-08f8bc978350/image.png" /></p>
<p>** 지정한 문구 출력 **
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b3066c20-466d-4ab4-86a8-d9ee6b8eda38/image.png" /></p>
<h2 id="조회">조회</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/652e4c85-4f6f-4fcb-a7b6-ce8bea8cde31/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dc40ed51-1e12-4938-a859-b985208ad439/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f515e03f-3c4e-4a0d-bdf2-b9bdd373aa2c/image.png" /></p>
<blockquote>
<p>1회성 로깅이기 떄문에 <strong>-f</strong> 옵션을 통해서 지속적으로 볼 필요는 없다.</p>
</blockquote>
<h2 id="yaml-파일-배포를-통한-여러-기능-수행">YAML 파일 배포를 통한 여러 기능 수행</h2>
<pre><code># 실습4) Job(단일잡)
apiVersion: batch/v1
kind: Job
metadata:
  name: secloudit-job
  namespace: secloudit-namespace
spec:
  template:
    spec:
      containers:
      - name: secloudit-container
        image: busybox
        command: [&quot;echo&quot;, &quot;Platform as a service!&quot;]
      restartPolicy: Never

# 실습5) Job(단일잡)
apiVersion: batch/v1
kind: Job
metadata:
  name: secloudit-job
  namespace: secloudit-namespace
spec:
  template:
    spec:
      containers:
      - name: secloudit-container
        image: busybox
        args: [&quot;date&quot;]
      restartPolicy: OnFailure
  backoffLimit: 2

# 실습6) Job(다중잡)
apiVersion: batch/v1
kind: Job
metadata:
  name: secloudit-job
  namespace: secloudit-namespace
spec:
  completions: 3
  template:
    metadata:
      labels:
        app: secloudit
    spec:
      restartPolicy: OnFailure
      containers:
      - name: secloudit-container
        image: busybox
        command: [&quot;sleep&quot;, &quot;30&quot;]

#실습7) Job(병렬잡)
apiVersion: batch/v1
kind: Job
metadata:
  name: secloudit-job
  namespace: secloudit-namespace
spec:
  completions: 3
  parallelism: 3
  template:
    metadata:
      labels:
        app: secloudit
    spec:
      restartPolicy: OnFailure
      containers:
      - name: secloudit-container
        image: quay.io/prometheus/busybox
        command: [&quot;sleep&quot;, &quot;20&quot;]
</code></pre><ul>
<li><p>restartPolicy</p>
<ul>
<li>해당 필드값을 통해서 파드가 실패했을 때의 정책을 설정할 수 있다.<ul>
<li>Never : 한번 실패한 파드를 다시 살리지 마라. 새로운 파드를 파서 실행하도록 함.</li>
<li>OnFailure : 실패했다는 상황에는 해당 파드에서 재시작을 시도해라.</li>
</ul>
</li>
</ul>
</li>
<li><p>completions</p>
<ul>
<li>해당 job을 실행할 파드의 총 갯수 설정<ul>
<li>value 값에 따라서, job이 수행되는 총 횟수가 결정됨.</li>
</ul>
</li>
</ul>
</li>
<li><p>parallelism</p>
<ul>
<li>해당 job을 실행할 때, 동시에 실행될 job의 총 갯수 설정</li>
</ul>
</li>
<li><p>backoffLimit</p>
<ul>
<li>해당 job이 실패하더라도 해당 value 만큼의 재시도를 해라.<ul>
<li>default : 6</li>
<li>해당 숫자가 채워질 때까지 수행실패를 하게된다면, job수행 실패로 완료된다.<ul>
<li>성공을 보장하는게 아닌, 완료를 보장한다는게 이런 뜻이다.</li>
</ul>
</li>
</ul>
</li>
</ul>
</li>
</ul>
<h1 id="cronjob">Cronjob</h1>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/4c297116-d08a-495f-a059-12960dd02f57/image.png" /></p>
<pre><code>apiVersion: batch/v1
kind: CronJob
metadata:
  name: secloudit-cronjob
  namespace: secloudit-namespace
spec:
  schedule: &quot;*/1 * * * *&quot;
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: secloudi-container
            image: kubetm/init
            command: [&quot;sh&quot;, &quot;-c&quot;, &quot;echo 'start';sleep 20; echo 'end'&quot;]
          terminationGracePeriodSeconds: 0
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 1</code></pre><ul>
<li>특징적인 부분 : <strong>schedule</strong> , jobTemplate, successfulJobsHistoryLimit, failedJobsHistoryLimit<ul>
<li>schedule
<img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/3746a884-2a81-4bae-a52f-d4456bcf518f/image.png" /></li>
<li>jobTemplete<ul>
<li>해당 cronjob이 수행할 job에 대한 정보를 담는 필드</li>
</ul>
</li>
<li>successfulJobsHistoryLimit, failedJobsHistoryLimit<ul>
<li>성공/실패한 각각 완료한 job리소스에 대해서 얼마나 기록해둘지 설정하는 필드</li>
</ul>
</li>
</ul>
</li>
</ul>
<h2 id="조회-1">조회</h2>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/18124dbd-61bd-447a-abfc-3c24e5952ada/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/28108498-1c31-4631-9c81-0b5ccdc68f95/image.png" /></p>
<h2 id="생성-1">생성</h2>
<h3 id="상황-1-date-는-무엇인가">상황 1. date 는 무엇인가?</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b7610373-5962-4369-b26f-ff59717d20c5/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/293ac258-7930-4eb2-b3d1-926ca3f566a6/image.png" /></p>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/5b62b0de-8704-4128-ad9a-4e5fe3479d4a/image.png" /></p>
<h3 id="상황-2-수행시작시간으로부터-10초의-유예를-두고-수행">상황 2. 수행시작시간으로부터 10초의 유예를 두고 수행</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/8bb3677d-ce64-433d-ae30-c3d08dbc5d59/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/b1744149-422f-431f-a1c7-988dca398d33/image.png" /></p>
<h3 id="상황-3-지정된-문구-출력">상황 3. 지정된 문구 출력</h3>
<p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/f0a2b835-caa0-44dc-a313-537a4a60d20a/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/7cb558e4-36a6-4cf3-b47f-6c55901620fd/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/978cc014-6e95-4286-81fe-68730dc01fce/image.png" /></p>
<h3 id="상황-4-yaml-을-통한-배포">상황 4. yaml 을 통한 배포</h3>
<pre><code>apiVersion: batch/v1
kind: CronJob
metadata:
  name: secloudit-cronjob
  namespace: secloudit-namespace
spec:
  schedule: &quot;*/1 * * * *&quot;
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: secloudi-container
            image: kubetm/init
            command: [&quot;sh&quot;, &quot;-c&quot;, &quot;echo 'start';sleep 20; echo 'end'&quot;]
          terminationGracePeriodSeconds: 0
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 1</code></pre><ul>
<li>echo 사용방법 인지하기</li>
</ul>
<pre><code>$ kubectl apply -f {cronjob.yaml파일 명} 을 입력하여 배포</code></pre><p><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/67bd53b1-3674-4ac7-bb9d-f482a15830bc/image.png" /><img alt="" src="https://velog.velcdn.com/images/klmcw1004/post/dee758a9-2af5-4d37-be58-51503d711de0/image.png" /></p>