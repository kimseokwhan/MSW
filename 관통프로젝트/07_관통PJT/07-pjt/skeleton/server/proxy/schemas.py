"""API 요청과 응답에 사용할 데이터 형식을 정의한다."""
from pydantic import BaseModel


# 도서 추천 요청과 응답
class ChatRequest(BaseModel):
    messages: list[dict]            # [{"role": "user", "content": "..."}, ...]
    use_tier_routing: bool = False  # 기본 코드에 포함된 모델 선택 옵션


class ChatResponse(BaseModel):
    content: str
    model_used: str = ""


# 요청 적절성 검사
class ChatGuardrailRequest(BaseModel):
    prompt: str


class ChatGuardrailResponse(BaseModel):
    is_appropriate: bool


# 텍스트 또는 이미지 처리 경로
class DecideRouteRequest(BaseModel):
    prompt: str


class DecideRouteResponse(BaseModel):
    route: str


# 표지 이미지 생성 요청과 응답
class ImageGenerationRequest(BaseModel):
    prompt: str


class ImageGenerationResponse(BaseModel):
    image_base64: str               # JPEG 이미지를 base64로 변환한 문자열


# 표지 이미지 분석 요청과 응답
class ImageAnalysisRequest(BaseModel):
    image_base64: str               # 업로드한 이미지를 base64로 전달
    question: str


class ImageAnalysisResponse(BaseModel):
    content: str


# 기본 코드에 포함된 답변 평가 형식
class ChatScoreRequest(BaseModel):
    messages: list[dict]
    answer: str


class ChatScoreResponse(BaseModel):
    score: int
    reason: str


# 기본 코드에 포함된 음성 변환 형식
class GenerateSpeechRequest(BaseModel):
    text: str


class GenerateSpeechResponse(BaseModel):
    audio_data: str
