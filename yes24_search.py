
import requests
from bs4 import BeautifulSoup

def search_yes24_book(title):
    """
    YES24 검색 결과 중 가장 상단의 도서 상세페이지 URL을 반환한다.
    """
    search_url = f"https://www.yes24.com/Product/Search?query={requests.utils.quote(title)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(search_url, headers=headers, timeout=5)
    res.encoding = "euc-kr"
    soup = BeautifulSoup(res.text, "html.parser")

    # 검색 결과 영역에서 첫 번째 도서 링크 추출
    book_tag = soup.select_one("ul#yesSchList li .gd_name")

    if book_tag and book_tag.get("href"):
        book_url = book_tag["href"].strip()
        if book_url.startswith("/"):
            book_url = "https://www.yes24.com" + book_url
        return book_url
    else:
        return None

# 테스트용 실행
if __name__ == "__main__":
    result = search_yes24_book("국세청도 모르는 상속 증여의 기술")
    print("📘 상세페이지 URL:", result)
