Media Summarizer API (FastAPI + Whisper + LangChain)
업로드한 오디오/비디오 파일에서 음성을 추출하고, 추출된 텍스트를 영어로 요약한 뒤 한국어로 번역/요약하여 반환하는 API 서버입니다.
•	입력 형식: .mp3, .m4a, .wav, mp4, .avi
•	출력 형식: 한국어 요약 문자열(JSON)
•	기술 스택: FastAPI, MoviePy(FFmpeg), OpenAI Whisper API, LangChain(map-reduce summarization)
________________________________________
주요 기능
•	오디오/비디오에서 오디오 트랙 자동 추출
•	OpenAI Whisper(whisper-1)로 전사 (130초 단위 분할)
•	LangChain map_reduce 체인으로 영어 요약
•	OpenAI Chat Completions로 한국어 번역/요약
•	업로드 및 임시 파일 정리/삭제
________________________________________
동작 흐름
1.	POST /upload/로 미디어 파일 업로드
2.	MoviePy로 오디오 트랙 로드 → 130초 단위로 WAV 생성
3.	각 조각을 Whisper API로 전사 → 전체 텍스트 결합
4.	LangChain map_reduce로 영어 요약
5.	Chat Completions로 한국어 번역/요약
6.	JSON 응답으로 반환 ({"요약결과": "..."})
________________________________________
요구사항
•	Python 3.9+
•	FFmpeg (MoviePy 내부 사용)
•	OpenAI API Key (OPENAI_API_KEY)

Windows (choco)
choco install ffmpeg

설치 및 실행
# 1) 가상환경(권장)
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2) 의존성 설치
pip install -r requirements.txt

# 3) 환경변수 설정
export OPENAI_API_KEY=YOUR_KEY # Windows PowerShell: $env:OPENAI_API_KEY="YOUR_KEY"

# 4) 서버 실행
uvicorn main:app --reload --port 8000

API 사용법
파일 업로드 및 요약
POST /upload/
Content-Type: multipart/form-data
field name: file
curl 예시:
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@./sample.mp4"
성공 응답 예시:
{
  "요약결과": "업로드한 미디어의 한국어 요약 텍스트..."
}
에러 응답:
•	400: 허용되지 않는 형식
•	500: 내부 처리 중 예외 발생
