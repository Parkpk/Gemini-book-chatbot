import streamlit as st
import json
from main import run_pipeline

# Streamlit 앱 설정
st.set_page_config(page_title="AI 도서 추천 챗봇", page_icon="📚", layout="centered")
st.title("📚 AI 도서 추천 챗봇")
st.write("인문, 경제, 과학 등 다양한 분야의 책을 추천받아 보세요.")

# 사용자 질문 입력
user_question = st.text_input(
    "질문을 입력하세요:",
    placeholder="예) 철학 입문에 좋은 책 추천해주세요."
)

if st.button("추천받기"):
    if not user_question.strip():
        st.warning("질문을 입력해주세요.")
    else:
        with st.status("도서 추천 분석 중입니다...", expanded=True) as status:
            result = run_pipeline(user_question)

            # 오류 메시지 출력
            if result.get("errors"):
                for err in result["errors"]:
                    st.error(err)

            # 추천 결과 UI 출력 및 텍스트 저장
            recs = result.get("recommendations", [])
            txt_lines = []

            if recs:
                st.markdown("### 📚 추천 도서")
                for rec in recs:
                    # YES24 도서 페이지 링크로 제목 표시
                    st.markdown(f"#### [{rec['book_title']}]({rec['url']})")
                    st.markdown(f"- **저자:** {rec['author']}")
                    st.markdown(f"- **추천 이유:**\n\n{rec['reason']}")
                    st.markdown(f"- **도서 페이지:** [{rec['url']}]({rec['url']})")
                    st.markdown("---")

                    # 다운로드용 텍스트 누적
                    txt_lines.append(f"책 제목: {rec['book_title']}")
                    txt_lines.append(f"저자: {rec['author']}")
                    txt_lines.append(f"추천 이유: {rec['reason']}")
                    txt_lines.append(f"YES24 페이지: {rec['url']}")
                    txt_lines.append("")

            # fallback 처리
            fb = result.get("fallback")
            if fb:
                st.warning("⚠️ 기본 추천 도서를 안내드립니다.")
                st.markdown(f"#### [{fb['book_title']}]({fb['url']})")
                st.markdown(f"- **저자:** {fb['author']}")
                st.markdown(f"- **추천 이유:**\n\n{fb['reason']}")
                st.markdown(f"- **YES24 페이지:** [{fb['url']}]({fb['url']})")

                txt_lines.append("기본 추천 도서:")
                txt_lines.append(f"책 제목: {fb['book_title']}")
                txt_lines.append(f"저자: {fb['author']}")
                txt_lines.append(f"추천 이유: {fb['reason']}")
                txt_lines.append(f"YES24 페이지: {fb['url']}")
                txt_lines.append("")

            if not recs and not fb:
                st.info("😢 추천 가능한 도서를 찾지 못했습니다.")

       
            # TXT 다운로드 버튼
            txt_data = "\n".join(txt_lines)
            st.download_button(
                label="📄 추천 내용 다운로드",
                data=txt_data,
                file_name="recommendation.txt",
                mime="text/plain"
            )

            status.update(label="✅ 추천이 완료되었습니다!", state="complete", expanded=False)

# 하단 정보
st.markdown("---")
st.markdown("Powered by **Streamlit** & **Gemini API**")