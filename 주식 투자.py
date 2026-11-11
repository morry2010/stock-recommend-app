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
        [
            "원금 보존이 가장 중요함",
            "적정한 수익과 안정성 추구",
            "고수익을 위해 손실 위험 감수",
        ],
    )

    q2 = st.radio(
        "2. 투자 기간은 어느 정도를 생각하고 계신가요?",
        ["1년 미만 단기", "1년~3년 중기", "3년 이상 장기"],
    )

    q3 = st.radio(
        "3. 투자한 자산의 원금 손실이 발생한다면 어떻게 하실 건가요?",
        [
            "바로 매도해서 손실을 최소화함",
            "지켜보며 회복을 기다림",
            "추가 매수 기회로 활용함",
        ],
    )

    if st.button("🚀 내 투자 성향 및 자산 배분 결과 보기"):
        score = 0

        if q1 == "원금 보존이 가장 중요함":
            score += 1
        elif q1 == "적정한 수익과 안정성 추구":
            score += 2
        else:
            score += 3

        if q2 == "1년 미만 단기":
            score += 1
        elif q2 == "1년~3년 중기":
            score += 2
        else:
            score += 3

        if q3 == "바로 매도해서 손실을 최소화함":
            score += 1
        elif q3 == "지켜보며 회복을 기다림":
            score += 2
        else:
            score += 3

        # 성향별 자산 배분 데이터
        if score <= 4:
            user_type = "보수형 (Conservative)"
            data = {
                "자산군": ["대형 우량주", "채권/국고채", "예금/현금"],
                "비중(%)": [40, 40, 20],
                "최근 1년 수익률(%)": [12.5, 4.2, 3.5],
            }
        elif score <= 7:
            user_type = "중립형 (Balanced - 기본 6:4)"
            data = {
                "자산군": ["주식 (성장/대형)", "채권", "원자재/현금"],
                "비중(%)": [60, 30, 10],
                "최근 1년 수익률(%)": [18.2, 4.2, 15.0],
            }
        else:
            user_type = "공격형 (Aggressive)"
            data = {
                "자산군": ["고성장 주식/테크", "가상자산/원자재", "채권"],
                "비중(%)": [80, 15, 5],
                "최근 1년 수익률(%)": [28.5, 35.0, 4.2],
            }

        # 포트폴리오 가중 평균 최근 1년 종합 수익률 계산
        weights = [w / 100 for w in data["비중(%)"]]
        returns = data["최근 1년 수익률(%)"]
        portfolio_return = sum(w * r for w, r in zip(weights, returns))

        # 결과를 세션에 저장
        st.session_state.score = score
        st.session_state.user_type = user_type
        st.session_state.data = data
        st.session_state.portfolio_return = round(portfolio_return, 2)
        st.session_state.submitted = True
        st.rerun()

# 제출을 완료한 상태일 때 (결과 화면)
else:
    st.success("설문 진단이 완료되었습니다!")
    st.subheader(
        f"📊 진단 점수: {st.session_state.score}점 ➔ **{st.session_state.user_type}**"
    )

    # 최근 1년 포트폴리오 종합 수익률 강조 박스
    st.metric(
        label="🔥 이 포트폴리오의 최근 1년 환산 종합 수익률",
        value=f"+{st.session_state.portfolio_return}%",
    )

    df = pd.DataFrame(st.session_state.data)

    # 표의 왼쪽 번호(인덱스)를 1, 2, 3으로 설정
    df.index = range(1, len(df) + 1)

    st.write("### 💡 자산군별 세부 비중 및 최근 1년 수익률")
    st.dataframe(df, use_container_width=True)

    # 1. 도넛 차트 (자산 배분 비중)
    fig_pie = px.pie(
        df,
        values="비중(%)",
        names="자산군",
        title=f"{st.session_state.user_type} 자산 배분 비중",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # 2. 막대 그래프 (자산군별 최근 1년 수익률 비교)
    fig_bar = px.bar(
        df,
        x="자산군",
        y="최근 1년 수익률(%)",
        text="최근 1년 수익률(%)",
        title=f"{st.session_state.user_type} 자산군별 최근 1년 수익률 비교",
        color="자산군",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 3. 나무위키 및 실시간 시세 링크 섹션 (해외 주식 시세 링크 포함)
    st.write("---")
    st.write("### 🔗 추천 자산 설명 및 실시간 시세 바로가기")

    if "보수형" in st.session_state.user_type:
        st.markdown(
            "- 🏢 **현대자동차**: [나무위키](https://namu.wiki/w/%ED%98%84%EB%8C%80%EC%9E%90%EB%8F%99%EC%B0%A8) | [네이버 증권](https://finance.naver.com/item/main.naver?code=005380)"
        )
        st.markdown(
            "- 🏢 **삼성전자**: [나무위키](https://namu.wiki/w/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90) | [네이버 증권](https://finance.naver.com/item/main.naver?code=005930)"
        )
        st.markdown(
            "- 🛡️ **국고채/채권**: [국고채 (나무위키)](https://namu.wiki/w/%EA%B5%AD%EA%B3%A0%EC%B1%84)"
        )
    elif "중립형" in st.session_state.user_type:
        st.markdown(
            "- 📈 **주식/ETF**: [S&P 500 (나무위키)](https://namu.wiki/w/S%26P%20500) | [SCHD (나무위키)](https://namu.wiki/w/SCHD)"
        )
        st.markdown(
            "- 🪙 **금(Gold) 시세**: [금 현물 시세 (네이버 금융)](https://finance.naver.com/marketindex/goldDetail.naver)"
        )
    else:
        st.markdown(
            "- 🚀 **테슬라**: [나무위키](https://namu.wiki/w/%ED%85%8C%EC%8A%AC%EB%9D%BC) | [네이버 증권](https://finance.naver.com/world/sise.naver?symbol=TSLA@US)"
        )
        st.markdown(
            "- 🚀 **엔비디아**: [나무위키](https://namu.wiki/w/%EC%97%94%EB%B9%84%EB%94%94%EC%95%84) | [네이버 증권](https://finance.naver.com/world/sise.naver?symbol=NVDA@US)"
        )
        st.markdown(
            "- 💎 **비트코인**: [나무위키](https://namu.wiki/w/%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8)"
        )

    # 다시 하기 버튼
    if st.button("🔄 다시 진단하기"):
        st.session_state.submitted = False
        st.rerun()
