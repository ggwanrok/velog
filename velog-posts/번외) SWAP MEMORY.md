<h1 id="ec2-환경에서-swap-memory를-설정한-이유와-방법">EC2 환경에서 Swap Memory를 설정한 이유와 방법</h1>
<p>Spring Boot 애플리케이션을 EC2에 배포하면서 Docker, Docker Compose, MySQL, RabbitMQ 등을 함께 실행하다 보면 생각보다 메모리 사용량이 커질 수 있다.</p>
<p>특히 프리티어 또는 저사양 EC2 인스턴스처럼 기본 메모리가 1GB 정도인 환경에서는 다음과 같은 문제가 발생할 수 있다.</p>
<pre><code class="language-text">- Gradle 빌드 중 메모리 부족
- Docker 컨테이너 실행 중 OOM 발생
- MySQL 또는 RabbitMQ 컨테이너 비정상 종료
- 서버가 갑자기 느려지거나 SSH 접속이 불안정해짐</code></pre>
<p>이런 문제를 완화하기 위해 EC2에 <strong>Swap Memory</strong>를 설정할 수 있다.</p>
<hr />
<h1 id="swap-memory란">Swap Memory란?</h1>
<p>Swap Memory는 디스크의 일부 공간을 메모리처럼 사용하는 기능이다.</p>
<p>일반적으로 프로그램은 RAM을 사용해서 실행된다. 하지만 RAM이 부족해지면 운영체제는 사용 빈도가 낮은 메모리 데이터를 디스크의 Swap 영역으로 옮겨서 RAM 공간을 확보할 수 있다.</p>
<p>즉, Swap은 물리 메모리가 부족할 때 사용할 수 있는 <strong>보조 메모리 공간</strong>이라고 볼 수 있다.</p>
<pre><code class="language-text">RAM 부족
  ↓
덜 자주 사용하는 메모리 데이터를 디스크 Swap 영역으로 이동
  ↓
RAM 공간 확보
  ↓
프로세스가 바로 종료되는 상황 완화</code></pre>
<p>다만 Swap은 디스크를 사용하기 때문에 RAM보다 훨씬 느리다. 따라서 Swap은 성능을 높이기 위한 기능이라기보다는, <strong>메모리 부족으로 인한 프로세스 종료를 방지하기 위한 안전장치</strong>에 가깝다.</p>
<hr />
<h1 id="왜-ec2에-swap-memory를-설정했는가">왜 EC2에 Swap Memory를 설정했는가?</h1>
<p>이번 배포 환경에서는 EC2 인스턴스 위에서 Docker Compose를 사용해 여러 컨테이너를 실행한다.</p>
<p>예를 들어 다음과 같은 서비스가 함께 실행될 수 있다.</p>
<pre><code class="language-text">- Spring Boot Application
- MySQL
- RabbitMQ
- Nginx</code></pre>
<p>각 서비스는 독립적인 컨테이너로 실행되지만, 실제 메모리는 모두 하나의 EC2 인스턴스에서 사용한다.</p>
<p>즉, 컨테이너가 여러 개라고 해서 메모리가 분리되어 새로 생기는 것이 아니라, EC2의 제한된 RAM을 나눠 쓰는 구조다.</p>
<pre><code class="language-text">EC2 인스턴스 메모리
  ├─ Spring Boot 컨테이너
  ├─ MySQL 컨테이너
  ├─ RabbitMQ 컨테이너
  └─ Nginx 컨테이너</code></pre>
<p>따라서 EC2의 RAM이 부족하면 컨테이너가 강제로 종료될 수 있다.</p>
<p>이때 Swap Memory를 설정해두면, 순간적인 메모리 부족 상황에서 서버가 바로 죽는 것을 어느 정도 완화할 수 있다.</p>
<hr />
<h1 id="현재-swap-상태-확인">현재 Swap 상태 확인</h1>
<p>먼저 EC2 서버에 접속한 뒤 현재 Swap이 설정되어 있는지 확인한다.</p>
<pre><code class="language-bash">free -h</code></pre>
<p>출력 예시는 다음과 같다.</p>
<pre><code class="language-bash">              total        used        free      shared  buff/cache   available
Mem:          949Mi        350Mi       120Mi        10Mi       478Mi       430Mi
Swap:            0B          0B          0B</code></pre>
<p>여기서 <code>Swap: 0B</code>로 표시된다면 현재 Swap이 설정되어 있지 않은 상태다.</p>
<p>또는 다음 명령어로도 확인할 수 있다.</p>
<pre><code class="language-bash">swapon --show</code></pre>
<p>아무 출력도 없다면 활성화된 Swap 영역이 없는 것이다.</p>
<hr />
<h1 id="swap-파일-생성">Swap 파일 생성</h1>
<p>일반적으로 EC2에서는 별도의 Swap 파티션을 만들기보다, 파일 기반 Swap을 설정하는 방식이 간단하다.</p>
<p>예를 들어 2GB Swap 파일을 생성하려면 다음 명령어를 실행한다.</p>
<pre><code class="language-bash">sudo fallocate -l 2G /swapfile</code></pre>
<p>만약 <code>fallocate</code> 명령이 동작하지 않는 환경이라면 다음 명령어를 사용할 수도 있다.</p>
<pre><code class="language-bash">sudo dd if=/dev/zero of=/swapfile bs=128M count=16</code></pre>
<p>위 명령은 128MB 블록을 16개 생성하므로 총 2GB 크기의 Swap 파일을 만든다.</p>
<pre><code class="language-text">128MB × 16 = 2048MB = 2GB</code></pre>
<hr />
<h1 id="swap-파일-권한-설정">Swap 파일 권한 설정</h1>
<p>Swap 파일은 시스템 메모리와 관련된 민감한 파일이므로 권한을 제한해야 한다.</p>
<pre><code class="language-bash">sudo chmod 600 /swapfile</code></pre>
<p>권한을 확인해보면 다음과 같이 표시된다.</p>
<pre><code class="language-bash">ls -lh /swapfile</code></pre>
<pre><code class="language-bash">-rw------- 1 root root 2.0G May  4 12:00 /swapfile</code></pre>
<p>여기서 <code>rw-------</code>는 root 사용자만 읽고 쓸 수 있다는 의미다.</p>
<hr />
<h1 id="swap-영역으로-변환">Swap 영역으로 변환</h1>
<p>생성한 파일을 Swap 영역으로 사용할 수 있도록 설정한다.</p>
<pre><code class="language-bash">sudo mkswap /swapfile</code></pre>
<p>출력 예시는 다음과 같다.</p>
<pre><code class="language-bash">Setting up swapspace version 1, size = 2 GiB
no label, UUID=...</code></pre>
<p>이제 <code>/swapfile</code>은 일반 파일이 아니라 Swap 용도로 사용할 수 있는 파일이 된다.</p>
<hr />
<h1 id="swap-활성화">Swap 활성화</h1>
<p>다음 명령어로 Swap을 활성화한다.</p>
<pre><code class="language-bash">sudo swapon /swapfile</code></pre>
<p>설정이 잘 되었는지 확인한다.</p>
<pre><code class="language-bash">free -h</code></pre>
<p>예상 출력은 다음과 같다.</p>
<pre><code class="language-bash">              total        used        free      shared  buff/cache   available
Mem:          949Mi        360Mi       110Mi        10Mi       479Mi       420Mi
Swap:         2.0Gi          0B       2.0Gi</code></pre>
<p>또는 다음 명령어로 확인할 수 있다.</p>
<pre><code class="language-bash">swapon --show</code></pre>
<pre><code class="language-bash">NAME       TYPE  SIZE USED PRIO
/swapfile  file    2G   0B   -2</code></pre>
<p>이렇게 나오면 Swap 설정이 정상적으로 적용된 것이다.</p>
<hr />
<h1 id="서버-재부팅-후에도-swap-유지하기">서버 재부팅 후에도 Swap 유지하기</h1>
<p>지금까지의 설정은 현재 실행 중인 세션에서는 적용되지만, 서버를 재부팅하면 Swap 설정이 사라질 수 있다.</p>
<p>재부팅 후에도 자동으로 Swap이 활성화되도록 <code>/etc/fstab</code> 파일에 등록해야 한다.</p>
<pre><code class="language-bash">sudo nano /etc/fstab</code></pre>
<p>파일 맨 아래에 다음 줄을 추가한다.</p>
<pre><code class="language-bash">/swapfile swap swap defaults 0 0</code></pre>
<p>저장 후 종료한다.</p>
<p>이 설정은 서버가 부팅될 때 <code>/swapfile</code>을 Swap 영역으로 자동 마운트하라는 의미다.</p>
<hr />
<h1 id="swap-사용-성향-조정하기">Swap 사용 성향 조정하기</h1>
<p>Linux에는 <code>swappiness</code>라는 설정값이 있다.</p>
<p><code>swappiness</code>는 운영체제가 Swap을 얼마나 적극적으로 사용할지 결정하는 값이다.</p>
<p>값의 범위는 보통 0부터 100까지이며, 값이 클수록 Swap을 더 적극적으로 사용한다.</p>
<p>현재 값을 확인하려면 다음 명령어를 사용한다.</p>
<pre><code class="language-bash">cat /proc/sys/vm/swappiness</code></pre>
<p>기본값은 보통 <code>60</code>인 경우가 많다.</p>
<p>서버 애플리케이션 환경에서는 Swap을 너무 적극적으로 사용하면 성능이 떨어질 수 있기 때문에, 보통 낮은 값으로 조정한다.</p>
<p>예를 들어 <code>10</code>으로 설정할 수 있다.</p>
<pre><code class="language-bash">sudo sysctl vm.swappiness=10</code></pre>
<p>다만 이 설정도 재부팅하면 초기화될 수 있으므로 영구 적용하려면 다음 파일을 수정한다.</p>
<pre><code class="language-bash">sudo nano /etc/sysctl.conf</code></pre>
<p>맨 아래에 다음 내용을 추가한다.</p>
<pre><code class="language-bash">vm.swappiness=10</code></pre>
<p>이렇게 하면 재부팅 후에도 <code>swappiness</code> 값이 유지된다.</p>
<hr />
<h1 id="설정-후-전체-확인">설정 후 전체 확인</h1>
<p>최종적으로 다음 명령어들을 통해 Swap 상태를 확인할 수 있다.</p>
<pre><code class="language-bash">free -h</code></pre>
<pre><code class="language-bash">swapon --show</code></pre>
<pre><code class="language-bash">cat /proc/sys/vm/swappiness</code></pre>
<p>예상 결과는 다음과 같다.</p>
<pre><code class="language-text">Swap 영역이 2GB로 잡혀 있고,
swappiness 값이 10으로 설정되어 있다면 정상적으로 적용된 상태다.</code></pre>
<hr />
<h1 id="주의할-점">주의할 점</h1>
<p>Swap Memory는 RAM을 대체하는 완전한 해결책은 아니다.</p>
<p>Swap은 디스크 공간을 메모리처럼 사용하는 방식이기 때문에 실제 RAM보다 훨씬 느리다. 따라서 Swap 사용량이 계속 높게 유지된다면, 이는 서버의 물리 메모리가 부족하다는 의미다.</p>
<p>즉, Swap은 다음과 같은 용도로 이해하는 것이 좋다.</p>
<pre><code class="language-text">좋은 사용:
- 순간적인 메모리 부족 상황 완화
- OOM으로 인한 프로세스 강제 종료 방지
- 저사양 EC2에서 안정성 보완

나쁜 사용:
- 부족한 RAM을 장기적으로 대체
- 지속적으로 Swap에 의존하는 운영
- 메모리 사용량이 큰 서비스를 무리하게 실행</code></pre>
<p>만약 <code>free -h</code>를 확인했을 때 Swap 사용량이 계속 높다면, 다음과 같은 개선이 필요하다.</p>
<pre><code class="language-text">- EC2 인스턴스 사양 업그레이드
- 컨테이너별 메모리 제한 설정
- MySQL, RabbitMQ 설정 최적화
- 불필요한 서비스 분리
- 애플리케이션 메모리 사용량 분석</code></pre>
<hr />
<h1 id="정리">정리</h1>
<p>EC2 환경에서 Swap Memory를 설정하면 제한된 RAM을 가진 인스턴스에서도 메모리 부족으로 인한 갑작스러운 프로세스 종료를 어느 정도 방지할 수 있다.</p>
<p>이번 배포 환경에서는 Docker Compose를 통해 Spring Boot, MySQL, RabbitMQ 등의 여러 컨테이너를 함께 실행하기 때문에 메모리 사용량이 커질 수 있다. 따라서 Swap Memory를 설정하여 운영 안정성을 보완했다.</p>
<p>전체 설정 흐름은 다음과 같다.</p>
<pre><code class="language-bash">sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo nano /etc/fstab</code></pre>
<p><code>/etc/fstab</code>에는 다음 내용을 추가한다.</p>
<pre><code class="language-bash">/swapfile swap swap defaults 0 0</code></pre>
<p>그리고 Swap 사용 성향을 낮추기 위해 다음 설정을 적용한다.</p>
<pre><code class="language-bash">sudo sysctl vm.swappiness=10</code></pre>
<p>영구 적용을 위해 <code>/etc/sysctl.conf</code>에 다음 내용을 추가한다.</p>
<pre><code class="language-bash">vm.swappiness=10</code></pre>
<p>결과적으로 Swap은 EC2의 부족한 메모리를 보조하는 안전장치 역할을 하며, Docker 기반 배포 환경에서 서버 안정성을 높이는 데 도움이 된다.</p>