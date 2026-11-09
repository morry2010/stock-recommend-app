import pandas as pd
import plotly.express as px
import streamlit as st

st.title("📈 맞춤형 투자 성향 진단 및 자산 배분")

# 세션 상태에 'submitted'가 아직 없다면 False로 초기화
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# 제출을 안 한 상태일 때만 질문과 버튼을 보여줌
if not st.session_state.submitted:
    st.write("아래 질문에 답하고 **[결과 확인하기]** 버튼을 눌러주세요!")
    st.divider()

    q1 = st.radio(
        "1. 당신의 투자 목적은 무엇인가요?",
        ["원금 보존이 가장 중요함 (1점)", "적정한 수익과 안정성 추구 (2점)", "고수익을 위해 손실 위험 감수 (3점)"],
    )

    q2 = st.radio(
        "2. 투자 기간은 어느 정도를 생각하고 계신가요?",
        ["1년 미만 단기 (1점)", "1년~3년 중기 (2점)", "3년 이상 장기 (3점)"],
    )

    q3 = st.radio(
        "3. 투자한 자산의 원금 손실이 발생한다면 어떻게 하실 건가요?",
        ["바로 매도해서 손실을 최소화함 (1점)", "지켜보며 회복을 기다림 (2점)", "추가 매수 기회로 활용함 (3점)"],
    )

    if st.button("🚀 내 투자 성향 및 자산 배분 결과 보기"):
        # 점수 계산
        score = 0
        for q in [q1, q2, q3]:
            if "(1점)" in q:
                score += 1
            elif "(2점)" in q:
                score += 2
            elif "(3점)" in q:
                score += 3

        # 성향 판별 및 상세 종목 포함 데이터 설정
        if score <= 4:
            user_type = "보수형 (Conservative)"
            data = {
                "자산군": ["국채/채권", "예금/현금", "대형주 주식"],
                "비중(%)": [60, 30, 10],
                "추천 예시 상품": [
                    "국고채 ETF / 단기채권",
                    "CMA / 정기예금",
                    "코스피 대형 우량주 (삼성전자 등)",
                ],
            }
        elif score <= 7:
            user_type = "중립형 (Balanced)"
            data = {
                "자산군": ["국내/해외 주식", "채권", "현금/원자재"],
                "비중(%)": [40, 40, 20],
                "추천 예시 상품": [
                    "S&P 500 / 미국 배당 다우존스",
                    "종합 채권 ETF",
                    "달러 예금 / 금(Gold) 현물",
                ],
            }
        else:
            user_type = "공격형 (Aggressive)"
            data = {
                "자산군": ["성장주/해외주식", "가상자산/원자재", "채권"],
                "비중(%)": [70, 20, 10],
                "추천 예시 상품": [
                    "미국 나스닥 100 / 테크 성장주",
                    "원자재 ETF / 가상자산",
                    "단기 국고채",
                ],
            }

        # 결과를 세션에 저장
        st.session_state.score = score
        st.session_state.user_type = user_type
        st.session_state.data = data
        st.session_state.submitted = True
        st.rerun()

# 제출을 완료한 상태일 때 (결과 화면)
else:
    st.success("설문 진단이 완료되었습니다!")
    st.subheader(
        f"📊 진단 점수: {st.session_state.score}점 ➔ **{st.session_state.user_type}**"
    )

    df = pd.DataFrame(st.session_state.data)

    st.write("### 💡 맞춤 추천 포트폴리오 및 종목 예시")
    st.dataframe(df, use_container_width=True)

    # 도넛 차트 출력
    fig = px.pie(
        df,
        values="비중(%)",
        names="자산군",
        title=f"{st.session_state.user_type} 자산 배분 도넛 차트",
        hole=0.4,
    )

    st.plotly_chart(fig, use_container_width=True)

    # 다시 하기 버튼
    if st.button("🔄 다시 진단하기"):
        st.session_state.submitted = False
        st.rerun()
