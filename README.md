Media Summarizer API (FastAPI + Whisper + LangChain)

업로드한 오디오/비디오 파일에서 음성을 추출해 문자로 전사하고, 전사된 텍스트를 영어로 요약 → 한국어로 번역/요약하여 반환하는 간단한 API 서버입니다.

입력: .mp3, .m4a, .wav, .flac, .mp4, .avi, .mov, .mkv, .wmv

출력: 한국어 요약 문자열(JSON)

스택: FastAPI, MoviePy(FFmpeg), OpenAI Whisper API, LangChain(map-reduce summarization)


주요 기능

오디오/비디오에서 자동으로 오디오 트랙 추출

OpenAI Whisper (whisper-1) 로 전사 (130초 단위 분할 처리)

LangChain Map-Reduce 요약 체인으로 영어 요약

OpenAI Chat Completions로 한국어 번역 및 요약

업로드 파일 및 임시 오디오 파일 정리/삭제


동작 흐름

POST /upload/로 미디어 파일 업로드

MoviePy로 오디오 트랙 로드 → 130초 단위로 나눠 WAV 생성

매 조각을 Whisper API로 전사 → 전체 텍스트 결합

LangChain map_reduce로 영어 요약

Chat Completions로 한국어 번역/요약

JSON으로 결과 반환 ({"요약결과": "..."})


요구사항

Python 3.9+

FFmpeg (MoviePy가 내부적으로 사용)

OpenAI API Key (환경변수 OPENAI_API_KEY)

FFmpeg 설치


Windows (choco)

choco install ffmpeg

설치 & 실행
# 1) 가상환경(권장)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) 의존성 설치
pip install -r requirements.txt

# 3) 환경변수 설정
export OPENAI_API_KEY=YOUR_KEY   # Windows PowerShell: $env:OPENAI_API_KEY="YOUR_KEY"

# 4) 서버 실행
uvicorn main:app --reload --port 8000
