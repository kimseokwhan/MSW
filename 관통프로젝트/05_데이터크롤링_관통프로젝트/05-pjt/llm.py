"""GMS(OpenAI 호환 API) 호출 및 JSON 배열 응답 해석.

환경 설정 파일 탐색 순서:
1) 05-pjt/.env           (권장 위치)
2) 05-pjt의 상위 폴더/.env (기존 프로젝트 호환)

사용 예:
    from llm import run_llm, parse_json_array
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent

# 기존에는 BASE_DIR.parent만 읽어 05-pjt/.env의 GMS_KEY가 누락될 수 있었음.
# 프로젝트 폴더를 우선 읽고, 없는 변수는 상위 폴더 설정에서 보충함.
# 이미 OS 환경에 설정된 변수는 바꾸지 않음.
load_dotenv(BASE_DIR / '.env', override=False)
load_dotenv(BASE_DIR.parent / '.env', override=False)

GMS_DEFAULT_BASE_URL = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1/'


def run_llm(prompt):
    """GMS에 프롬프트를 보내고 텍스트 응답을 반환한다."""
    api_key = (os.getenv('GMS_KEY') or os.getenv('GMS_API_KEY') or '').strip()
    if not api_key:
        raise RuntimeError(
            'GMS API 키를 찾지 못했습니다. '
            '05-pjt/.env 파일에 GMS_KEY=발급받은키 를 설정한 후 '
            'Django 서버를 다시 실행하세요.'
        )

    base_url = (os.getenv('GMS_BASE_URL') or GMS_DEFAULT_BASE_URL).strip()
    model = (os.getenv('MODEL') or os.getenv('OPENAI_MODEL') or 'gpt-5-nano').strip()

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.responses.create(model=model, input=prompt)
    return response.output_text


def parse_json_array(response):
    """LLM 응답에서 JSON 배열을 꺼낸다. 형식이 틀리면 None."""
    text = response.strip()
    if text.startswith('```'):
        text = text.strip('`').removeprefix('json').strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print('[파싱 실패] 응답이 JSON 형식이 아닙니다:', response[:100])
        return None

    if not isinstance(data, list):
        print('[파싱 실패] 응답이 리스트가 아닙니다:', response[:100])
        return None
    return data


if __name__ == '__main__':
    print(parse_json_array(run_llm('1부터 3까지 숫자를 [1, 2, 3] 형식의 배열로만 답해줘.')))
