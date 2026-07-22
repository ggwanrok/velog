<h1 id="github에서-수행한-작업">GitHub에서 수행한 작업</h1>
<p>이 CI/CD가 동작하려면 GitHub Repository에서도 몇 가지 설정이 필요하다.</p>
<hr />
<h2 id="github-secrets-등록">GitHub Secrets 등록</h2>
<p>Repository Settings에서 다음 Secrets를 등록했다.</p>
<pre><code class="language-text">EC2_HOST
EC2_USER
EC2_SSH_KEY
GHCR_USERNAME
GHCR_PAT</code></pre>
<p>경로는 다음과 같다.</p>
<pre><code class="language-text">Repository
  → Settings
  → Secrets and variables
  → Actions
  → New repository secret</code></pre>
<p>각 Secret의 의미는 다음과 같다.</p>
<pre><code class="language-text">EC2_HOST
→ EC2 퍼블릭 IP 또는 도메인

EC2_USER
→ EC2 SSH 접속 사용자
→ Ubuntu 기준 ubuntu

EC2_SSH_KEY
→ EC2 접속용 private key 전체 내용

GHCR_USERNAME
→ GHCR 로그인에 사용할 GitHub 계정명

GHCR_PAT
→ EC2에서 GHCR 이미지를 pull하기 위한 Personal Access Token</code></pre>
<p><code>EC2_SSH_KEY</code>를 등록할 때는 private key 파일 내용을 그대로 넣어야 한다.</p>
<pre><code class="language-text">-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----</code></pre>
<p>이 값을 코드에 직접 작성하면 안 되기 때문에 GitHub Secrets를 사용했다.</p>
<hr />
<h2 id="ghcr-접근-권한">GHCR 접근 권한</h2>
<p>GitHub Actions에서 GHCR에 이미지를 push할 때는 <code>GITHUB_TOKEN</code>을 사용한다.</p>
<pre><code class="language-yaml">password: ${{ secrets.GITHUB_TOKEN }}</code></pre>
<p><code>GITHUB_TOKEN</code>은 GitHub Actions에서 자동으로 제공되므로 직접 등록할 필요가 없다.</p>
<p>하지만 EC2는 GitHub Actions 내부 환경이 아니기 때문에 <code>GITHUB_TOKEN</code>을 사용할 수 없다.</p>
<p>따라서 EC2가 GHCR에서 private image를 pull하기 위해 별도의 Personal Access Token을 발급하고, 이를 <code>GHCR_PAT</code>로 등록했다.</p>
<p>정리하면 다음과 같다.</p>
<pre><code class="language-text">GitHub Actions
→ GHCR에 이미지 push
→ GITHUB_TOKEN 사용

EC2
→ GHCR에서 이미지 pull
→ GHCR_PAT 사용</code></pre>
<hr />