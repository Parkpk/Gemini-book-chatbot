# article_summarizer.py

from dotenv import load_dotenv
import os
from google.generativeai import GenerativeModel, configure

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
configure(api_key=api_key)  # ✅ 추가 설정

model = GenerativeModel("gemini-1.5-pro")

def summarize_article(text):
    """
    웹에서 수집한 추천 글 전체(text)를 받아
    핵심만 3~5문장으로 요약해서 반환한다.
    """
    prompt = f"""
다음 글은 도서 추천 블로그나 뉴스 기사입니다. 글의 요점을 3~5문장으로 요약해주세요.

글 내용:
{text[:4000]}  # 너무 길면 앞부분만 사용
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# 예시 실행용 테스트
if __name__ == "__main__":
    sample_text = """
    최근 증여세에 대한 관심이 높아지고 있다. 많은 전문가들은 상속과 증여를 적절히 활용하는 것이 절세의 핵심이라고 말한다. 
    특히 '국세청도 모르는 상속 증여의 기술'이라는 책은 이러한 내용을 실전 사례 중심으로 다룬다. 
    자녀에게 교육비를 증여할 때 어떻게 하면 비과세로 처리할 수 있는지, 가족 간의 자산 이전 시 주의사항 등도 담고 있다.
    """
    summary = summarize_article(sample_text)
    print("요약 결과:\n", summary)

"""
사용 예시
from article_summarizer import summarize_article

text = get_article_text(url)  # 예: 웹 크롤러로 가져온 본문
summary = summarize_article(text)
"""

