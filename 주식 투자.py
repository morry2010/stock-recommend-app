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
        "1. 투자 과정에서 마주할 수 있는 시장 변동성과 손실 위험에 대한 본인의 태도는 어느 쪽에 가까우신가요?",
        [
            "원금 손실은 절대 방어해야 하며, 안정적으로 자산을 지키는 것이 최우선입니다.",
            "어느 정도의 시장 변동이나 소폭의 손실은 감수하겠지만, 무리한 위험은 피하고 싶습니다.",
            "더 높은 기대 수익을 얻을 수 있다면, 원금의 단기 하락이나 큰 변동성은 충분히 감수할 수 있습니다.",
        ],
    )

    q2 = st.radio(
        "2. 현재 자금을 모으거나 투자하려는 주된 목적은 무엇인가요?",
        [
            "은퇴 및 노후 대비 (장기적이고 안정적인 자산 증식)",
            "내집 마련, 결혼 자금 등 특정 시점에 필요한 목돈(시드머니) 마련",
            "단기 유휴 자금 활용 및 적극적인 자본 차익 추구",
        ],
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
        # Q1 (위험 성향): 1~3점
        if "원금 손실은 절대" in q1:
            s1 = 1
        elif "어느 정도의 시장 변동" in q1:
            s1 = 2
        else:
            s1 = 3

        # Q2 (투자 목적): 1~3점
        if "은퇴 및 노후" in q2:
            s2 = 1
        elif "내집 마련" in q2:
            s2 = 2
        else:
            s2 = 3

        # Q3 (손실 대응): 1~3점
        if "바로 매도" in q3:
            s3 = 1
        elif "지켜보며 회복" in q3:
            s3 = 2
        else:
            s3 = 3

        # 총 9가지 세부 유형 분기 로직 (특수문자 제거 버전)
        if s1 == 1:
            if s2 == 1:
                user_type = "보수형 - 노후 안정 지향형"
                data = {
                    "자산군": ["국고채/안전채권", "대형 우량주", "금(Gold)/현금"],
                    "비중(%)": [50, 30, 20],
                    "최근 1년 수익률(%)": [4.2, 12.5, 18.5],
                }
            elif s2 == 2:
                user_type = "보수형 - 목돈 마련 안정형"
                data = {
                    "자산군": ["채권형 ETF", "배당주 펀드", "단기 예적금"],
                    "비중(%)": [40, 40, 20],
                    "최근 1년 수익률(%)": [5.0, 10.0, 3.5],
                }
            else:
                user_type = "보수형 - 단기 자금 파킹형"
                data = {
                    "자산군": ["CMA/MMF (현금)", "단기 국채", "우량 회사채"],
                    "비중(%)": [60, 20, 20],
                    "최근 1년 수익률(%)": [3.6, 4.0, 5.2],
                }
        elif s1 == 2:
            if s2 == 1:
                user_type = "중립형 - 은퇴 준비 밸런스형"
                data = {
                    "자산군": ["S&P 500 ETF", "종합 채권", "금(Gold)"],
                    "비중(%)": [50, 40, 10],
                    "최근 1년 수익률(%)": [18.2, 4.2, 18.5],
                }
            elif s2 == 2:
                user_type = "중립형 - 6:4 표준 성장형"
                data = {
                    "자산군": ["주식 (성장/대형)", "채권", "원자재/현금"],
                    "비중(%)": [60, 30, 10],
                    "최근 1년 수익률(%)": [18.2, 4.2, 15.0],
                }
            else:
                user_type = "중립형 - 단기 스윙 밸런스형"
                data = {
                    "자산군": ["섹터별 주도주", "채권", "현금성 자산"],
                    "비중(%)": [50, 20, 30],
                    "최근 1년 수익률(%)": [20.0, 4.2, 3.5],
                }
        else:
            if s2 == 1:
                user_type = "공격형 - 장기 기술주 집중형"
                data = {
                    "자산군": ["글로벌 빅테크/AI", "혁신 성장 ETF", "채권"],
                    "비중(%)": [80, 15, 5],
                    "최근 1년 수익률(%)": [30.0, 25.0, 4.2],
                }
            elif s2 == 2:
                user_type = "공격형 - 고성장 시드머니형"
                data = {
                    "자산군": ["미국 성장주", "가상자산/원자재", "채권"],
                    "비중(%)": [75, 20, 5],
                    "최근 1년 수익률(%)": [28.5, 35.0, 4.2],
                }
            else:
                user_type = "공격형 - 초고위험 트레이딩형"
                data = {
                    "자산군": ["가상자산(코인)", "테마형 고변동성 주식", "현금"],
                    "비중(%)": [70, 20, 10],
                    "최근 1년 수익률(%)": [45.0, 30.0, 3.5],
                }

        # 포트폴리오 가중 평균 최근 1년 종합 수익률 계산
        weights = [w / 100 for w in data["비중(%)"]]
        returns = data["최근 1년 수익률(%)"]
        portfolio_return = sum(w * r for w, r in zip(weights, returns))

        # 결과를 세션에 저장
        st.session_state.score = s1 + s2 + s3
        st.session_state.user_type = user_type
        st.session_state.data = data
        st.session_state.portfolio_return = round(portfolio_return, 2)
        st.session_state.submitted = True
        st.rerun()

# 제출을 완료한 상태일 때 (결과 화면)
else:
    st.success("설문 진단이 완료되었습니다!")
    st.subheader(
        f"📊 맞춤 진단 결과 ➔ **{st.session_state.user_type}**"
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

    # 도넛 차트 (자산 배분 비중)
    fig_pie = px.pie(
        df,
        values="비중(%)",
        names="자산군",
        title=f"{st.session_state.user_type} 자산 배분 비중",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # 나무위키 및 실시간 시세 링크 섹션
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
            "- 🪙 **금(Gold)**: [나무위키](https://namu.wiki/w/%EA%B8%88) | [네이버 금시세](https://finance.naver.com/marketindex/goldDetail.naver)"
        )
    elif "중립형" in st.session_state.user_type:
        st.markdown(
            "- 📈 **S&P 500 ETF**: [나무위키](https://namu.wiki/w/S%26P%20500) | [야후 파이낸스](https://finance.yahoo.com/quote/VOO/)"
        )
        st.markdown(
            "- 🪙 **금(Gold)**: [나무위키](https://namu.wiki/w/%EA%B8%88) | [네이버 금시세](https://finance.naver.com/marketindex/goldDetail.naver)"
        )
    else:
        st.markdown(
            "- 🚀 **테슬라**: [나무위키](https://namu.wiki/w/%ED%85%8C%EC%8A%AC%EB%9D%BC) | [야후 파이낸스](https://finance.yahoo.com/quote/TSLA/)"
        )
        st.markdown(
            "- 🚀 **엔비디아**: [나무위키](https://namu.wiki/w/%EC%97%94%EB%B9%84%EB%94%94%EC%95%84) | [야후 파이낸스](https://finance.yahoo.com/quote/NVDA/)"
        )
        st.markdown(
            "- 💎 **비트코인**: [나무위키](https://namu.wiki/w/%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8) | [야후 파이낸스](https://finance.yahoo.com/quote/BTC-USD/)"
        )

    # 다시 하기 버튼
    if st.button("🔄 다시 진단하기"):
        st.session_state.submitted = False
        st.rerun()
