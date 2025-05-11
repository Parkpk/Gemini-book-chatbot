import streamlit as st
from main import run_pipeline

st.set_page_config(page_title="도서 추천 챗봇", layout="wide")
st.title("📚 AI 도서 추천 with Gemini")
st.write("독자 님이 원하실 만한 책을 추천해드릴게요.")

user_question = st.text_input("자유롭게 질문해주세요:", placeholder="예: 철학에 입문하려면 어떤 책이 좋을까요?")

if st.button("추천 받기") and user_question.strip():
    with st.spinner("추천 도서를 찾는 중... 최대 1분 정도 소요될 수 있어요."):
        output = run_pipeline(user_question)

    if output.get("errors"):
        st.error("\n".join(output["errors"]))

    recs = output.get("recommendations", [])
    fallback = output.get("fallback")

    if recs:
        st.subheader("📚 추천 도서 ")
        txt_lines = []  # 다운로드용 텍스트 누적
        for rec in recs[:3]:
            st.markdown(f"#### [{rec['book_title']}]({rec['url']})")
            st.markdown(f"- **저자:** {rec['author']}")
            st.markdown(f"- **추천 이유:**\n\n{rec['reason']}")
            st.markdown(f"- **도서 페이지:** [{rec['url']}]({rec['url']})")
            st.markdown("---")

            txt_lines.append(f"책 제목: {rec['book_title']}")
            txt_lines.append(f"저자: {rec['author']}")
            txt_lines.append(f"추천 이유: {rec['reason']}")
            txt_lines.append(f"YES24 페이지: {rec['url']}")
            txt_lines.append("")

        st.download_button(
            label="📄 추천 결과 저장하기",
            data="\n".join(txt_lines),
            file_name="book_recommendations.txt",
            mime="text/plain"
        )

    elif fallback:
        st.subheader("📚 대체 추천 도서")
        st.markdown(f"#### [{fallback['book_title']}]({fallback['url']})")
        st.markdown(f"- **저자:** {fallback['author']}")
        st.markdown(f"- **추천 이유:**\n\n{fallback['reason']}")
        st.markdown(f"- **도서 페이지:** [{fallback['url']}]({fallback['url']})")

else:
    st.info("추천받고 싶은 주제를 입력하고 버튼을 눌러보세요!")
