from web_scraper import search_cse
from article_parser import extract_main_text_from_url
from article_summarizer import summarize_article
from yes24_search import search_yes24_book
from toc_parser import extract_toc_from_yes24, extract_intro_from_yes24, extract_author_from_yes24
from prompt_builder import build_prompt
from gemini_book_extractor import extract_book_titles
from article_selector import select_top_articles
from google.generativeai import GenerativeModel, configure

import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()
# 환경 변수에서 키 가져오기
CSE_API_KEY = os.getenv("CSE_API_KEY")
CSE_CX_ID = os.getenv("CSE_CX_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 모델 설정
configure(api_key=GEMINI_API_KEY)
model = GenerativeModel("gemini-1.5-pro")

def extract_search_keywords(user_question: str) -> str:
    """Gemini를 사용하여 질문에서 핵심 키워드 2개를 추출하고, '책'을 붙여 반환합니다."""
    prompt = f"""
다음 문장에서 도서 검색에 사용할 핵심 키워드 **2개**만 뽑아서 공백으로 구분된 한 줄로 출력해주세요.
불필요한 조사나 어미 없이 명사 위주로만 뽑아야 합니다.
'추천', '좋은' 등의 **일반적 검색어**는 포함하지 마세요.
문장: "{user_question}"
"""
    response = model.generate_content(prompt)
    # 모델이 반환한 키워드 문자열
    keywords = response.text.strip().replace("\n", " ")
    # 안전하게 두 단어만 취해 사용
    parts = keywords.split()
    top2 = parts[:2] if len(parts) >= 2 else parts
    return "".join(top2) + " 책"

def run_pipeline(user_question: str) -> dict:
    output = {
        "question": user_question,
        "recommendations": [],
        "fallback": None,
        "errors": []
    }
    try:
        # 1. 검색 키워드 생성
        keyword_query = extract_search_keywords(user_question)
        search_query = f"{keyword_query} 추천 -filetype:pdf"

        # 2. 추천 글 링크 수집
        search_results = search_cse(search_query, CSE_API_KEY, CSE_CX_ID)
        if not search_results:
            output["errors"].append("❌ 관련 추천 글을 찾을 수 없습니다.")
            return output

        # 3. 본문 크롤링
        articles = []
        for r in search_results:
            try:
                text = extract_main_text_from_url(r["url"])
                articles.append({"title": r["title"], "url": r["url"], "text": text})
            except Exception:
                output["errors"].append(f"⚠️ 크롤링 실패: {r['url']}")

        # 4. 적절한 글 선택
        selected_articles = select_top_articles(user_question, articles, top_k=3)
        if not selected_articles:
            output["errors"].append("❌ 적절한 글을 판단하지 못했습니다.")
            return output

        # 5. 추천 도서 추출 및 상세 정보 수집
        for result in selected_articles:
            article_summary = summarize_article(result['text'])
            candidate_titles = extract_book_titles(article_summary)
            if not candidate_titles:
                continue

            for book_title in candidate_titles:
                book_url = search_yes24_book(book_title)
                if not book_url:
                    continue

                author = extract_author_from_yes24(book_url)
                toc = extract_toc_from_yes24(book_url)
                if not toc:
                    continue
                intro = extract_intro_from_yes24(book_url)

                prompt = build_prompt(
                    user_question,
                    article_summary,
                    book_title,
                    author,
                    intro,
                    toc
                )
                response = model.generate_content(prompt)
                output["recommendations"].append({
                    "book_title": book_title,
                    "author": author,
                    "reason": response.text.strip(),
                    "url": book_url
                })

        # 6. fallback 로직: 추천 결과가 없을 때
        if not output["recommendations"]:
            # 키워드 쿼리를 그대로 YES24 검색
            fallback_url = search_yes24_book(keyword_query)
            if not fallback_url:
                output["errors"].append("❌ 적절한 도서를 찾지 못했습니다.")
                return output

            author = extract_author_from_yes24(fallback_url)
            toc = extract_toc_from_yes24(fallback_url) or []
            intro = extract_intro_from_yes24(fallback_url)
            title_tag = BeautifulSoup(
                requests.get(fallback_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).text,
                "html.parser"
            ).select_one("h2.gd_name")
            fallback_title = title_tag.get_text(strip=True) if title_tag else keyword_query

            prompt = build_prompt(
                user_question,
                "",
                fallback_title,
                author,
                intro,
                toc
            )
            response = model.generate_content(prompt)
            output["fallback"] = {
                "book_title": fallback_title,
                "author": author,
                "reason": response.text.strip(),
                "url": fallback_url
            }
    except Exception as e:
        output["errors"].append(f"❌ 처리 중 오류 발생: {str(e)}")

    return output

if __name__ == "__main__":
    from pprint import pprint
    pprint(run_pipeline("철학에 입문하고 싶은데 추천해주세요."))
