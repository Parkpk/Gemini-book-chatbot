#제미나이 호출 테스트

import google.generativeai as genai

# 🔑 여기에 발급받은 API 키 입력
genai.configure(api_key="AIzaSyBcxC2cuuRu-G-EDaTK-NgViYCvuzQ2DoE")

# 모델 선택
model = genai.GenerativeModel("gemini-1.5-pro")

# 간단한 프롬프트로 테스트
prompt = "도서 '국세청도 모르는 상속 증여의 기술'에 대해 한 줄로 요약해줘."

response = model.generate_content(prompt)

print("응답 결과:")
print(response.text)