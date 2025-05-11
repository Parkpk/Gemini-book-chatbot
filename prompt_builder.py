# prompt_builder.py

from typing import List

def build_prompt(user_question: str, article_summary: str, book_title: str, author: str, intro_text: str, toc_lines: List[str]) -> str:
    """
    사용자 질문, 추천글 요약, 도서 제목, 저자, 책소개, 목차 리스트를 받아서
    Gemini에 전달할 프롬프트를 생성한다.
    """
    # 목차가 너무 길어지면 자르기 (예: 최대 30줄)
    MAX_TOC_LINES = 30
    trimmed_toc = toc_lines[:MAX_TOC_LINES]
    toc_text = "\n".join(trimmed_toc)

    # 책소개가 너무 길면 앞부분 1000자까지만 사용
    intro_snippet = intro_text.strip()
    if len(intro_snippet) > 1000:
        intro_snippet = intro_snippet[:1000] + "..."

    prompt = f"""
당신은 도서 추천 전문가입니다. 사용자의 질문과 추천 글, 그리고 도서 정보를 참고하여
정확하고 신뢰할 수 있는 책을 추천해주세요.

(중요: 목차에 없는 챕터명은 절대 지어내지 마세요.)
(중요: 추천 도서 제목은 **{book_title}**, 저자는 **{author}** 로 정확히 통일하여 사용해주세요.)
(중요: 추천 이유의 첫 문장은 "{author}의 '{book_title}'을 추천합니다." 형태로 시작하고, 일반적인 인사나 칭찬 문구는 생략하세요.)
(중요: 각 추천 이유에서 중복되는 문장은 피하세요.)

사용자의 질문:
"{user_question}"

다음은 웹에서 수집한 추천 글 내용입니다:
{article_summary}

다음은 도서 "{book_title}"의 저자입니다:
{author}

다음은 도서 "{book_title}"의 책소개입니다:
{intro_snippet}

다음은 도서 "{book_title}"의 목차입니다:
{toc_text}

이 정보를 참고해서 아래의 기준에 따라 답변을 생성해주세요:
1. 책 제목은 반드시 "{book_title}"으로만 언급하세요.
2. 저자는 반드시 "{author}"로만 명시하세요.
3. 추천 이유를 추천 글과 사용자의 질문을 연결하여 설명하고,
4. 반드시 실제 목차 내용을 인용하여 어떤 챕터가 도움이 되는지 구체적으로 언급하세요.

(주의: 추천글을 언급하지 말고 자연스럽게 답변하고 '사용자' 대신 '독자 님'을 사용하세요.)
(주의: 추천 이유에서 저자는 언급하지 않거나 최대 1번만 언급하세요.)

    """
    return prompt
