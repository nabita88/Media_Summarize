from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import os
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = FastAPI()

# API 키 불러오기
openai_key = os.environ.get("OPENAI_API_KEY")
if not openai_key:
    raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

openai_client = OpenAI(api_key=openai_key)
chat_model = ChatOpenAI(openai_api_key=openai_key)

@app.get("/")
async def home():
    return {"status": "서버 정상 작동 중입니다."}


#오디오 및 비디오에서 텍스트 추출
async def extract_text_from_media(path: str, client) -> str:
    audio_formats = ('.mp3', '.m4a', '.wav', '.flac')
    video_formats = ('.mp4', '.avi', '.mov', '.mkv', '.wmv')

    clip = AudioFileClip(path) if path.endswith(audio_formats) else (
        VideoFileClip(path) if path.endswith(video_formats) else None)

    if not clip:
        raise HTTPException(status_code=400, detail="허용되지 않는 파일 확장자입니다.")

    duration = clip.duration
    slice_length = 130
    current = 0
    combined_text = ''
    temp_audio = "segment.wav"

    try:
        while current < duration:
            segment = clip.subclip(current, min(current + slice_length, duration))
            segment.write_audiofile(temp_audio, codec="pcm_s16le", verbose=False, logger=None)
            with open(temp_audio, "rb") as audio:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
                combined_text += response
            current += slice_length
    finally:
        clip.close()
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

    return combined_text


#텍스트 요약 (map-reduce 방식)
async def perform_detailed_summary(api_key: str, document: str) -> str:
    language_model = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)

    initial_prompt = PromptTemplate(
        template="""다음 텍스트를 읽고 영상/오디오의 내용을 요약해 주세요. 핵심 아이디어, 중요한 사실, 전달하고자 하는 메시지를 중심으로 정리해주세요.
        
        내용:
        {text}
        
        요약 결과는 영어로 작성해주세요.""",
        input_variables=["text"]
    )

    merge_prompt = PromptTemplate(
        template="""다음은 여러 부분의 요약입니다. 이를 바탕으로 전체 내용을 포괄적으로 정리한 문장을 작성해주세요.
        
        요약 모음:
        {text}
        
        요구사항:
        - 주제 및 목적
        - 핵심 메시지
        - 중요 정보
        - 결론 요약
        
        영어로 10문장 이내로 작성하세요.""",
        input_variables=["text"]
    )

    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=0)
    split_docs = splitter.create_documents(splitter.split_text(document))

    summarizer = load_summarize_chain(
        llm=language_model,
        chain_type="map_reduce",
        verbose=False,
        map_prompt=initial_prompt,
        combine_prompt=merge_prompt
    )
    return summarizer.run(split_docs)


# 영어 요약 → 한글 요약
async def translate_and_summarize(client, input_text: str) -> str:
    translated = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "당신은 번역과 요약 전문가입니다. 입력된 영어 텍스트를 한국어로 번역하고 요약해주세요."
            },
            {
                "role": "user",
                "content": input_text
            }
        ]
    )
    return translated.choices[0].message.content


@app.post("/upload/")
async def handle_upload(file: UploadFile = File(...)):
    accepted_exts = ['.mp3', '.m4a', '.wav', '.flac', '.mp4', '.avi', '.mov', '.mkv', '.wmv']
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in accepted_exts:
        raise HTTPException(status_code=400, detail="허용되지 않는 형식입니다.")

    storage = "uploads"
    os.makedirs(storage, exist_ok=True)
    saved_path = os.path.join(storage, file.filename)

    try:
        with open(saved_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        extracted = await extract_text_from_media(saved_path, openai_client)
        eng_summary = await perform_detailed_summary(openai_key, extracted)
        kor_summary = await translate_and_summarize(openai_client, eng_summary)

        return {"요약결과": kor_summary}

    except Exception as err:
        raise HTTPException(status_code=500, detail=f"에러 발생: {str(err)}")

    finally:
        if os.path.exists(saved_path):
            os.remove(saved_path)
