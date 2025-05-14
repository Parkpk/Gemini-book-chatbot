from google.generativeai import GenerativeModel, configure
import os
from dotenv import load_dotenv

load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))

model = GenerativeModel("gemini-1.5-pro")

def extract_book_titles(article_summary, max_books=3):
    """
    추천 글 요약을 바탕으로 Gemini에게 도서 제목만 추출하게 요청
    """
    prompt = f"""
아래는 도서 추천 블로그 글의 요약입니다. 
이 글에서 추천된 도서 제목만 최대 {max_books}개 추출해줘.
문장은 필요 없고 책 제목만 리스트 형태로 출력해줘.

글 요약:
{article_summary}

응답 예시:
- 책 제목1
- 책 제목2
    """
    response = model.generate_content(prompt)
    lines = response.text.strip().split("\n")
   
    # 중복 제거하며 순서 보존
    seen = set()
    titles = []
    for line in lines:
        title = line.lstrip("- ").strip()
        if not title or title in seen:
            continue
        seen.add(title)
        titles.append(title)
        if len(titles) >= max_books:
            break
    return titles

# 예시 실행 테스트
if __name__ == "__main__":
    test_summary = """
    이 글에서는 증여세와 상속세를 효과적으로 줄이는 방법을 다룬 도서를 추천하고 있다. 
    특히 '국세청도 모르는 상속 증여의 기술'과 '절세 바이블'이 강조된다.
    """
    print("\n📚 추천 도서 목록:")
    for title in extract_book_titles(test_summary):
        print("-", title)

    """
        사용예시
from gemini_book_extractor import extract_book_titles

    book_titles = extract_book_titles(article_summary)
    for title in book_titles:
    """