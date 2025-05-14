import streamlit as st
import json
from main import run_pipeline

# 페이지 설정
st.set_page_config(page_title="도서 추천 챗봇", layout="wide")
st.title("📚 AI 도서 추천 with Gemini")
st.write("독자 님이 원하실 만한 책을 추천해드릴게요.")

# 사용자 입력
user_question = st.text_input(
    "자유롭게 질문해주세요:",
    placeholder="예: 철학에 입문하려면 어떤 책이 좋을까요?"
)

# 추천 버튼 클릭 시 로직
if st.button("추천 받기") and user_question.strip():
    with st.spinner("추천 도서를 찾는 중... 최대 1분 정도 소요될 수 있어요."):
        output = run_pipeline(user_question)

    # 에러 출력
    if output.get("errors"):
        for err in output["errors"]:
            st.error(err)

    recs = output.get("recommendations", [])
    fallback = output.get("fallback")

    # 추천 도서가 있을 때
    if recs:
        st.subheader("📚 추천 도서")
        txt_lines = []

        for rec in recs[:3]:  # 최대 3개 도서 추천
            # 좌우 3:1 컬럼
            col_text, col_img = st.columns([3, 1])
            with col_text:
                st.markdown(f"#### [{rec['book_title']}]({rec['url']})")
                st.markdown(f"- **저자:** {rec['author']}")
                st.markdown(f"- **추천 이유:**\n\n{rec['reason']}")
                st.markdown(f"- **도서 페이지:** [{rec['url']}]({rec['url']})")
            with col_img:
                if rec.get("cover_url"):
                    st.image(rec["cover_url"], use_container_width=True)
            st.markdown("---")

            # TXT 다운로드용 텍스트 누적
            txt_lines.extend([
                f"책 제목: {rec['book_title']}",
                f"저자: {rec['author']}",
                f"추천 이유: {rec['reason']}",
                f"YES24 페이지: {rec['url']}",
                ""
            ])

        # TXT 다운로드 버튼만 표시
        st.download_button(
            label="📄 TXT 다운로드",
            data="\n".join(txt_lines),
            file_name="book_recommendations.txt",
            mime="text/plain"
        )

    # 추천 결과가 없고 fallback만 있을 때
    elif fallback:
        st.subheader("📚 대체 추천 도서")
        col_text, col_img = st.columns([3, 1])
        with col_text:
            st.markdown(f"#### [{fallback['book_title']}]({fallback['url']})")
            st.markdown(f"- **저자:** {fallback['author']}")
            st.markdown(f"- **추천 이유:**\n\n{fallback['reason']}")
            st.markdown(f"- **도서 페이지:** [{fallback['url']}]({fallback['url']})")
        with col_img:
            if fallback.get("cover_url"):
                st.image(fallback["cover_url"], use_container_width=True)
        st.markdown("---")

    # 아무 결과도 없을 때
    else:
        st.info("😢 추천 가능한 도서를 찾지 못했습니다.")

# 버튼을 누르지 않았을 때 안내
else:
    st.info("추천받고 싶은 주제를 입력하고 버튼을 눌러보세요!")
