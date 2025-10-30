

<h1 id="media-summarizer-api"> Media Summarizer API - 미디어 요약 서버</h1>

<br>

<h2>소개</h2>
<p><strong>Media Summarizer API</strong>는 업로드한 <em>오디오/비디오</em> 파일에서 음성을 추출하고, 
OpenAI <em>Whisper(whisper-1)</em>로 전사한 뒤 <em>LangChain(map-reduce)</em>로 <strong>영어 요약</strong>을 수행하고,
마지막으로 <strong>한국어 번역/요약</strong>까지 자동으로 반환하는 API 서버입니다.</p>

<ul>
  <li>입력 형식: <code>.mp3</code>, <code>.m4a</code>, <code>.wav</code>, <code>.mp4</code>, <code>.avi</code></li>
  <li>출력 형식: <strong>한국어 요약 문자열(JSON)</strong> &rarr; <code>{"요약결과": "..."}</code></li>
  <li>요약 파이프라인: 오디오/비디오 &rarr; 오디오 추출 &rarr; 130초 단위 분할 &rarr; Whisper 전사 &rarr; LangChain 영어 요약 &rarr; Chat Completions 한국어 번역/요약</li>
</ul>

<br>

<h2>🛠 기술 스택</h2>

<h3>Backend</h3>
<div>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Uvicorn-233a42?style=for-the-badge" alt="Uvicorn">
</div>

<h3>AI / Summarization</h3>
<div>
  <img src="https://img.shields.io/badge/OpenAI%20Whisper-whisper--1-000000?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI Whisper">
  <img src="https://img.shields.io/badge/LangChain-map--reduce-0E9F6E?style=for-the-badge" alt="LangChain">
</div>

<h3>Media</h3>
<div>
  <img src="https://img.shields.io/badge/MoviePy-FFmpeg%20backend-FF9A00?style=for-the-badge" alt="MoviePy">
  <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
</div>

<h3>Tools</h3>
<div>
  <img src="https://img.shields.io/badge/Swagger%20UI-/docs-85EA2D?style=for-the-badge&logo=swagger&logoColor=black" alt="Swagger UI">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/cURL-073551?style=for-the-badge&logo=curl&logoColor=white" alt="cURL">
</div>

<br>

<h2>주요 기능</h2>

<h3>핵심 기능</h3>
<ul>
  <li><strong>오디오/비디오에서 오디오 트랙 자동 추출</strong> (MoviePy/FFmpeg)</li>
  <li><strong>130초 단위</strong>로 WAV 분할하여 안정적 전사 처리</li>
  <li><strong>OpenAI Whisper(whisper-1)</strong>로 전사 후 전체 텍스트 병합</li>
  <li><strong>LangChain map_reduce</strong>로 영어 요약</li>
  <li><strong>OpenAI Chat Completions</strong>로 한국어 번역/요약</li>
  <li>작업 중 생성되는 <em>임시 파일 자동 정리</em></li>
</ul>

<br>

<h2>시스템 동작 흐름</h2>
<ol>
  <li><code>POST /upload/</code>로 미디어 파일 업로드 (<code>multipart/form-data</code>, 필드명 <code>file</code>)</li>
  <li>MoviePy로 오디오 트랙 로드 &rarr; <strong>WAV</strong>로 추출</li>
  <li>오디오를 <strong>130초</strong> 단위로 분할(필요 시 샘플레이트/모노 변환)</li>
  <li>각 조각을 Whisper API로 <strong>전사</strong> &rarr; <strong>전체 텍스트 결합</strong></li>
  <li>LangChain <em>map_reduce</em> 체인으로 <strong>영어 요약</strong> 생성</li>
  <li>Chat Completions로 <strong>한국어 번역/요약</strong> 수행</li>
  <li><code>{"요약결과": "..."}</code> JSON으로 응답</li>
</ol>

<pre><code>Client ──multipart──&gt; /upload
  │                     └─&gt; FFmpeg/MoviePy: audio extract -&gt; slice(130s)
  │                     └─&gt; Whisper: chunk STT -&gt; concat text
  │                     └─&gt; LangChain(map_reduce): English summary
  │                     └─&gt; Chat Completions: Korean translate/summary
  └─&lt;────────────────────────────── JSON { "요약결과": "..." }
</code></pre>

<br>

<h2>API 문서 (Swagger)</h2>
<pre><code>http://localhost:8000/docs
http://localhost:8000/redoc
</code></pre>

<br>

<h2>요구사항</h2>
<ul>
  <li>Python 3.9+</li>
  <li>FFmpeg (MoviePy 내부에서 사용)</li>
  <li>OpenAI API Key (<code>OPENAI_API_KEY</code>)</li>
</ul>

<h3>Windows(Chocolatey)</h3>
<pre><code>choco install ffmpeg
</code></pre>

<br>

<h2>설치 및 실행</h2>

<h3>1) 가상환경(권장)</h3>
<pre><code class="language-bash">python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
</code></pre>

<h3>2) 의존성 설치</h3>
<pre><code class="language-bash">pip install -r requirements.txt
</code></pre>

<h3>3) 환경변수 설정</h3>
<pre><code class="language-bash">export OPENAI_API_KEY=YOUR_KEY
# Windows PowerShell
# $env:OPENAI_API_KEY="YOUR_KEY"
</code></pre>

<h3>4) 서버 실행</h3>
<pre><code class="language-bash">uvicorn main:app --reload --port 8000
</code></pre>

<br>

<h2>API 사용법</h2>

<h3>파일 업로드 및 요약</h3>
<p><strong>Endpoint</strong>: <code>POST /upload/</code></p>
<p><strong>Content-Type</strong>: <code>multipart/form-data</code></p>

<table>
  <thead>
    <tr>
      <th>필드명</th>
      <th>타입</th>
      <th>설명</th>
      <th>필수</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>file</code></td>
      <td>binary</td>
      <td>오디오/비디오 파일(.mp3, .m4a, .wav, .mp4, .avi)</td>
      <td>Yes</td>
    </tr>
  </tbody>
</table>

<h4>cURL 예시</h4>
<pre><code class="language-bash">curl -X POST "http://localhost:8000/upload/" \
  -F "file=@./sample.mp4"
</code></pre>

<h4>성공 응답</h4>
<pre><code class="language-json">{
  "요약결과": "업로드한 미디어의 한국어 요약 텍스트..."
}
</code></pre>

<h4>에러 응답</h4>
<ul>
  <li><strong>400</strong>: 허용되지 않는 형식</li>
  <li><strong>500</strong>: 내부 처리 중 예외 발생</li>
</ul>

<br>

<h2>시스템 아키텍처 / 파일 구조</h2>

<h3>디렉터리</h3>
<pre><code>project-root/
├─ main.py              # FastAPI 엔드포인트(/upload), 파이프라인 진입점
├─ prompts.py           # 요약/번역 프롬프트
├─ requirements.txt     # 의존성
├─ Dockerfile           # (선택) 컨테이너 실행
└─ README.html          # (본 문서)
</code></pre>

<h3>요약 파이프라인</h3>
<ul>
  <li><strong>오디오 추출</strong>: MoviePy/FFmpeg로 WAV(16kHz/mono) 생성</li>
  <li><strong>분할</strong>: 130초 단위 WAV 청크 생성</li>
  <li><strong>전사</strong>: Whisper API(<code>whisper-1</code>)로 각 청크 전사 &rarr; 병합</li>
  <li><strong>영어 요약</strong>: LangChain <em>map_reduce</em></li>
  <li><strong>한국어 변환</strong>: OpenAI Chat Completions</li>
</ul>





