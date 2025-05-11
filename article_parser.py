
import requests
from bs4 import BeautifulSoup

def extract_main_text_from_url(url):
    """
    주어진 URL에서 본문 텍스트를 추출한다.
    HTML 구조가 다양할 수 있으므로 전체 텍스트를 단순히 긁고 후처리한다.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=5)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # 가능한 본문 추정: 가장 긴 div, p, article 조합 텍스트 선택
    candidates = soup.find_all(['article', 'section', 'div', 'p'])
    longest_block = max(candidates, key=lambda tag: len(tag.get_text(strip=True)), default=None)

    if longest_block:
        return longest_block.get_text(separator="\n", strip=True)
    else:
        return soup.get_text(separator="\n", strip=True)
    

# 예시 실행용 테스트
if __name__ == "__main__":
    test_url = "https://brunch.co.kr/@autumnpiece/28"  # 예시 URL (실제 유효한 페이지 필요)
    text = extract_main_text_from_url(test_url)
    print("추출된 본문:\n", text[:2000])
