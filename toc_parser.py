# toc_parser.py
import re
import requests
from bs4 import BeautifulSoup

def extract_toc_from_yes24(url):
    """
    YES24 도서 상세페이지에서 목차 텍스트만 추출한다.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=5)
    res.encoding = "utf-8"  # ✅ 변경
    soup = BeautifulSoup(res.text, "html.parser")

    # ✅ infoWrap_txt → infoSetCont 순으로 시도
    toc_section = soup.select_one("#infoset_toc .infoWrap_txt")
    if not toc_section:
        toc_section = soup.select_one("#infoset_toc .infoSetCont")

    if not toc_section:
        return []

    raw_text = toc_section.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    return lines

def extract_intro_from_yes24(url):
    """YES24 도서 상세페이지에서 책소개(책 설명) 텍스트만 추출한다."""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=5)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    # 책소개 탭(id=infoset_introduce) 안의 텍스트
    intro_section = soup.select_one("#infoset_introduce .infoWrap_txt")
    if not intro_section:
        intro_section = soup.select_one("#infoset_introduce .infoSetCont")

    if not intro_section:
         return ""

    return intro_section.get_text(separator="\n", strip=True)

def extract_author_from_yes24(url):
    """YES24 상세페이지에서 도서 저자명을 추출한다."""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=5)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    # href에 authorNo가 포함된 첫 번째 <a> 를 찾아서 저자명으로 간주
    author_tag = soup.find("a", href=re.compile(r"authorNo="))
    if not author_tag:
        return ""
    return author_tag.get_text(strip=True)

# 테스트 실행
if __name__ == "__main__":
    url = "https://www.yes24.com/product/goods/145317398"
    toc = extract_toc_from_yes24(url)
    intro = extract_intro_from_yes24(url)
    author = extract_author_from_yes24(url)
    print("목차:", toc)
    print("책소개:", intro[:100], "...")
    print("저자:", author)