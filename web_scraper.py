
import requests

JS_DOMAINS = [
    "blog.naver.com",
    "m.blog.naver.com",
    "post.naver.com",
    "velog.io",
    "instagram.com",
    "youtube.com"
]

def is_dynamic_url(url):
    return any(domain in url for domain in JS_DOMAINS)

def search_cse(query, api_key, cx, max_results=5):
    """
    Google CSE API를 통해 도서 추천 관련 글 링크 수집
    - query: 사용자 질문 기반 검색어
    - api_key: Google Cloud에서 발급받은 API 키
    - cx: Programmable Search Engine ID
    - max_results: 검색 결과 개수 제한
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query
    }
    res = requests.get(url, params=params)
    res.raise_for_status()
    results = res.json().get("items", [])

    filtered_links = []
    for item in results:
        link = item.get("link")
        title = item.get("title")
        if link and not is_dynamic_url(link):
            filtered_links.append({"title": title, "url": link})
        if len(filtered_links) >= max_results:
            break

    return filtered_links

# 테스트 코드
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    API_KEY = os.getenv("CSE_API_KEY")
    CX = os.getenv("CSE_CX_ID")

    query = "증여세 절세 전략 책 추천"
    results = search_cse(query, API_KEY, CX)
    for r in results:
        print("\n📘", r["title"])
        print("🔗", r["url"])

"""
사용예시
from web_scraper import search_cse

results = search_cse("증여세 절세 전략 책 추천", api_key, cx)
for r in results:
    print(r["title"], r["url"])
""" 