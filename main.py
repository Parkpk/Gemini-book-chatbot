# main.py

from web_scraper import search_cse
from article_parser import extract_main_text_from_url
from article_summarizer import summarize_article
from yes24_search import search_yes24_book
from toc_parser import extract_toc_from_yes24, extract_intro_from_yes24, extract_author_from_yes24
from prompt_builder import build_prompt
from gemini_book_extractor import extract_book_titles
from article_selector import select_top_articles
from google.generativeai import GenerativeModel

import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()
CSE_API_KEY = os.getenv("CSE_API_KEY")
CSE_CX_ID = os.getenv("CSE_CX_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = GenerativeModel("gemini-1.5-pro")

def run_pipeline(user_question):
    output = {
        "question": user_question,
        "recommendations": [],
        "fallback": None,
        "errors": []
    }

    try:
        # 1. 검색 쿼리 및 추천 글 링크 수집
        search_query = f"{user_question} 도서 추천 -filetype:pdf"
        search_results = search_cse(search_query, CSE_API_KEY, CSE_CX_ID)
        if not search_results:
            output["errors"].append("❌ 관련 추천 글을 찾을 수 없습니다.")
            return output

        # 2. 본문 크롤링
        articles = []
        for r in search_results:
            try:
                text = extract_main_text_from_url(r["url"])
                articles.append({"title": r["title"], "url": r["url"], "text": text})
            except Exception:
                output["errors"].append(f"⚠️ 크롤링 실패: {r['url']}")

        # 3. 상위 3개 글 선택
        selected_articles = select_top_articles(user_question, articles, top_k=3)
        if not selected_articles:
            output["errors"].append("❌ 적절한 글을 판단하지 못했습니다.")
            return output

        # 4. 추천 도서 추출 & 상세 정보
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
                    "url": book_url,
                    "source": result["url"],
                    "source_title": result["title"]
                })

        # 5. fallback 로직
        if not output["recommendations"]:
            fallback_url = search_yes24_book(search_query)
            if not fallback_url:
                output["errors"].append("❌ 적절한 도서를 찾지 못했습니다.")
                return output

            author = extract_author_from_yes24(fallback_url)
            toc = extract_toc_from_yes24(fallback_url) or []
            intro = extract_intro_from_yes24(fallback_url)

            res = requests.get(fallback_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            title_tag = soup.select_one("h2.gd_name")
            fallback_title = title_tag.get_text(strip=True) if title_tag else search_query

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
    pprint(run_pipeline("철학에 입문하기 좋은 책 추천해주세요."))
