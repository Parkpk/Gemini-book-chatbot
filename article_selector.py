import re
import ast
from google.generativeai import GenerativeModel, configure
import os
from dotenv import load_dotenv

load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))

model = GenerativeModel("gemini-1.5-pro")

def format_articles(articles):
    """
    수집된 웹 글 목록을 포맷합니다. 본문(text) 길이가
    기준(200자) 미만인 글은 스킵합니다.
    """
    result = ""
    for idx, art in enumerate(articles, start=1):
        text = art.get("text", "")
        # 너무 짧은 본문은 스킵
        if len(text) < 200:
            continue
        snippet = text[:600]
        result += f"{idx}. 제목: {art['title']}\n"
        result += f"링크: {art['url']}\n"
        result += f"본문 발췌: {snippet}...\n\n"
    return result


def select_top_articles(user_question, articles, top_k=3):
    """
    사용자 질문에 맞춰 수집된 웹 글 중 적절한 글을 선택합니다.
    JSON 배열로 인덱스를 응답받아 처리하며, eval 대신
    ast.literal_eval과 정규표현식을 사용해 파싱 오류를 방지합니다.
    """
    formatted = format_articles(articles)
    if not formatted:
        return []

    prompt = f"""
아래는 사용자의 질문과 관련해 수집된 웹 글들입니다.
이 중 도서 추천에 적절한 글을 최대 {top_k}개 골라주세요.

사용자 질문:
"{user_question}"

글 목록:
{formatted}

응답 형식은 JSON 배열 형태로 숫자 리스트만 주세요. 예: [1, 2, 4]
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # 1) JSON 파싱 시도
    try:
        index_list = ast.literal_eval(raw)
    except Exception:
        # 2) 실패 시 숫자만 추출
        nums = re.findall(r"\d+", raw)
        index_list = [int(n) for n in nums]

    # 3) 범위 체크 후 선택
    selected = []
    for i in index_list:
        if 1 <= i <= len(articles):
            selected.append(articles[i-1])
        if len(selected) >= top_k:
            break
    return selected


