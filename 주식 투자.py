import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.title("맞춤형 투자 성향 진단 및 자산 배분")


# --- [야후 파이낸스 데이터 연동 함수 (배당 오류 수정 반영)] ---
@st.cache_data(ttl=3600)
def get_asset_data(ticker_symbol, period="1y", fallback_return=5.0):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)

        # 기간별 수익률 계산
        ret = fallback_return
        if not hist.empty:
            start = hist["Close"].iloc[0]
            latest = hist["Close"].iloc[-1]
            ret = round(((latest - start) / start) * 100, 2)

        # 배당수익률 가져오기 (단위 버그 방지 처리)
        info = ticker.info
        div_yield = info.get("dividendYield", 0)
        if div_yield is not None:
            if div_yield > 1:
                div_yield = round(div_yield, 2)
            else:
                div_yield = round(div_yield * 100, 2)
        else:
            div_yield = 0.0

        return ret, div_yield
    except Exception:
        return fallback_return, 0.0


# --- [사이드바 영역] ---
with st.sidebar:
    st.header("맞춤형 자산 배분 포트폴리오")
    st.divider()

    st.subheader("섹터별 주요 종목 탐색")
    selected_sector = st.selectbox(
        "관심 있는 섹터를 선택하세요:",
        [
            "선택 안 함 (기본 보기)",
            "반도체",
            "테크/빅테크",
            "2차전지/에너지",
            "헬스케어/바이오",
            "금융/고배당",
        ],
    )
    st.divider()
    st.info(
        "💡 사이드바에서 섹터를 선택하면 아래 결과 화면 하단에 해당 섹터의 종목이"
        " 추가로 표시됩니다!"
    )


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

    if st.button("내 투자 성향 및 자산 배분 결과 보기"):
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

        # 총 9가지 세부 유형별 자산 구성 및 대표 ETF 티커 매핑
        if s1 == 1:
            if s2 == 1:
                user_type = "보수형 - 노후 안정 지향형"
                assets = [
                    {
                        "name": "국고채/안전채권",
                        "weight": 50,
                        "ticker": "IEF",
                        "fallback": 4.2,
                    },
                    {
                        "name": "대형 우량주",
                        "weight": 30,
                        "ticker": "VOO",
                        "fallback": 12.5,
                    },
                    {
                        "name": "금(Gold)/현금",
                        "weight": 20,
                        "ticker": "IAU",
                        "fallback": 18.5,
                    },
                ]
            elif s2 == 2:
                user_type = "보수형 - 목돈 마련 안정형"
                assets = [
                    {
                        "name": "채권형 ETF",
                        "weight": 40,
                        "ticker": "AGG",
                        "fallback": 5.0,
                    },
                    {
                        "name": "배당주 펀드",
                        "weight": 40,
                        "ticker": "SCHD",
                        "fallback": 10.0,
                    },
                    {
                        "name": "단기 예적금",
                        "weight": 20,
                        "ticker": "SHV",
                        "fallback": 3.5,
                    },
                ]
            else:
                user_type = "보수형 - 단기 자금 파킹형"
                assets = [
                    {
                        "name": "CMA/MMF (현금)",
                        "weight": 60,
                        "ticker": "BIL",
                        "fallback": 3.6,
                    },
                    {
                        "name": "단기 국채",
                        "weight": 20,
                        "ticker": "SHY",
                        "fallback": 4.0,
                    },
                    {
                        "name": "우량 회사채",
                        "weight": 20,
                        "ticker": "LQD",
                        "fallback": 5.2,
                    },
                ]
        elif s1 == 2:
            if s2 == 1:
                user_type = "중립형 - 은퇴 준비 밸런스형"
                assets = [
                    {
                        "name": "S&P 500 ETF",
                        "weight": 50,
                        "ticker": "VOO",
                        "fallback": 18.2,
                    },
                    {
                        "name": "종합 채권",
                        "weight": 40,
                        "ticker": "AGG",
                        "fallback": 4.2,
                    },
                    {
                        "name": "금(Gold)",
                        "weight": 10,
                        "ticker": "IAU",
                        "fallback": 18.5,
                    },
                ]
            elif s2 == 2:
                user_type = "중립형 - 6:4 표준 성장형"
                assets = [
                    {
                        "name": "주식 (성장/대형)",
                        "weight": 60,
                        "ticker": "VOO",
                        "fallback": 18.2,
                    },
                    {
                        "name": "채권",
                        "weight": 30,
                        "ticker": "AGG",
                        "fallback": 4.2,
                    },
                    {
                        "name": "원자재/현금",
                        "weight": 10,
                        "ticker": "GSG",
                        "fallback": 15.0,
                    },
                ]
            else:
                user_type = "중립형 - 단기 스윙 밸런스형"
                assets = [
                    {
                        "name": "섹터별 주도주",
                        "weight": 50,
                        "ticker": "XLK",
                        "fallback": 20.0,
                    },
                    {
                        "name": "채권",
                        "weight": 20,
                        "ticker": "AGG",
                        "fallback": 4.2,
                    },
                    {
                        "name": "현금성 자산",
                        "weight": 30,
                        "ticker": "BIL",
                        "fallback": 3.5,
                    },
                ]
        else:
            if s2 == 1:
                user_type = "공격형 - 장기 기술주 집중형"
                assets = [
                    {
                        "name": "글로벌 빅테크/AI",
                        "weight": 80,
                        "ticker": "QQQ",
                        "fallback": 30.0,
                    },
                    {
                        "name": "혁신 성장 ETF",
                        "weight": 15,
                        "ticker": "ARKK",
                        "fallback": 25.0,
                    },
                    {
                        "name": "채권",
                        "weight": 5,
                        "ticker": "AGG",
                        "fallback": 4.2,
                    },
                ]
            elif s2 == 2:
                user_type = "공격형 - 고성장 시드머니형"
                assets = [
                    {
                        "name": "미국 성장주",
                        "weight": 75,
                        "ticker": "QQQ",
                        "fallback": 28.5,
                    },
                    {
                        "name": "가상자산/원자재",
                        "weight": 20,
                        "ticker": "IAU",
                        "fallback": 35.0,
                    },
                    {
                        "name": "채권",
                        "weight": 5,
                        "ticker": "AGG",
                        "fallback": 4.2,
                    },
                ]
            else:
                user_type = "공격형 - 초고위험 트레이딩형"
                assets = [
                    {
                        "name": "가상자산 연계",
                        "weight": 70,
                        "ticker": "BITO",
                        "fallback": 45.0,
                    },
                    {
                        "name": "테마형 고변동성 주식",
                        "weight": 20,
                        "ticker": "TQQQ",
                        "fallback": 30.0,
                    },
                    {
                        "name": "현금",
                        "weight": 10,
                        "ticker": "BIL",
                        "fallback": 3.5,
                    },
                ]

        st.session_state.user_type = user_type
        st.session_state.assets = assets
        st.session_state.submitted = True
        st.rerun()

# 제출을 완료한 상태일 때 (결과 화면)
else:
    st.success("설문 진단이 완료되었습니다!")
    st.subheader(
        f"맞춤 진단 결과 ➔ **{st.session_state.user_type}**"
    )

    # 기간 선택 셀렉트박스 추가 (1년, 3년, 5년)
    col1, col2 = st.columns([2, 1])
    with col2:
        period_label = st.selectbox(
            "수익률 기간 선택", ["최근 1년", "최근 3년", "최근 5년"]
        )

    period_map = {"최근 1년": "1y", "최근 3년": "3y", "최근 5년": "5y"}
    selected_period = period_map[period_label]

    assets = st.session_state.assets
    names = [item["name"] for item in assets]
    weights = [item["weight"] for item in assets]

    returns = []
    div_yields = []
    for item in assets:
        ret, div = get_asset_data(
            item["ticker"], period=selected_period, fallback_return=item["fallback"]
        )
        returns.append(ret)
        div_yields.append(div)

    portfolio_return = sum(
        (w / 100) * r for w, r in zip(weights, returns)
    )

    st.metric(
        label=f"이 포트폴리오의 [{period_label}] 환산 종합 수익률",
        value=f"+{round(portfolio_return, 2)}%",
    )

    df_data = {
        "자산군": names,
        "비중(%)": weights,
        f"{period_label} 수익률(%)": returns,
        "배당수익률(%)": div_yields,
    }
    df = pd.DataFrame(df_data)
    df.index = range(1, len(df) + 1)

    st.write(f"### 자산군별 세부 비중 및 {period_label} 성과 / 배당")
    st.dataframe(df, use_container_width=True)

    fig_pie = px.pie(
        df,
        values="비중(%)",
        names="자산군",
        title=f"{st.session_state.user_type} 자산 배분 비중",
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # --- [영역 1] 내 설문 진단 결과에 따른 맞춤 추천 자산 ---
    st.write("---")
    st.write("### 내 진단 결과 맞춤 추천 자산 및 실시간 시세")

    if st.session_state.user_type == "보수형 - 노후 안정 지향형":
        st.markdown(
            "- **국고채**: [국고채 (나무위키)](https://namu.wiki/w/%EA%B5%AD%EA%B3%A0%EC%B1%84)"
        )
        st.markdown(
            "- **삼성전자**: [나무위키](https://namu.wiki/w/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90) | [네이버 증권](https://finance.naver.com/item/main.naver?code=005930)"
        )
        st.markdown(
            "- **금(Gold)**: [나무위키](https://namu.wiki/w/%EA%B8%88) | [네이버 금시세](https://finance.naver.com/marketindex/goldDetail.naver)"
        )
    elif st.session_state.user_type == "보수형 - 목돈 마련 안정형":
        st.markdown(
            "- **채권형 ETF**: [채권 (나무위키)](https://namu.wiki/w/%EC%B1%84%EA%B6%8C)"
        )
        st.markdown(
            "- **현대자동차**: [나무위키](https://namu.wiki/w/%ED%98%84%EB%8C%80%EC%9E%90%EB%8F%99%EC%B0%A8) | [네이버 증권](https://finance.naver.com/item/main.naver?code=005380)"
        )
    elif st.session_state.user_type == "보수형 - 단기 자금 파킹형":
        st.markdown(
            "- **CMA/MMF**: [CMA (나무위키)](https://namu.wiki/w/CMA) | [MMF (나무위키)](https://namu.wiki/w/MMF)"
        )
        st.markdown(
            "- **단기 국채**: [국고채 (나무위키)](https://namu.wiki/w/%EA%B5%AD%EA%B3%A0%EC%B1%84)"
        )
    elif "중립형" in st.session_state.user_type:
        st.markdown(
            "- **S&P 500 ETF**: [나무위키](https://namu.wiki/w/S%26P%20500) | [야후 파이낸스](https://finance.yahoo.com/quote/VOO/)"
        )
        st.markdown(
            "- **금(Gold)**: [나무위키](https://namu.wiki/w/%EA%B8%88) | [네이버 금시세](https://finance.naver.com/marketindex/goldDetail.naver)"
        )
    else:
        st.markdown(
            "- **테슬라**: [나무위키](https://namu.wiki/w/%ED%85%8C%EC%8A%AC%EB%9D%BC) | [야후 파이낸스](https://finance.yahoo.com/quote/TSLA/)"
        )
        st.markdown(
            "- **엔비디아**: [나무위키](https://namu.wiki/w/%EC%97%94%EB%B9%84%EB%94%94%EC%95%84) | [야후 파이낸스](https://finance.yahoo.com/quote/NVDA/)"
        )
        st.markdown(
            "- **비트코인**: [나무위키](https://namu.wiki/w/%EB%B9%84%ED%8A%B8%EC%BD%94%EC%9D%B8) | [야후 파이낸스](https://finance.yahoo.com/quote/BTC-USD/)"
        )

    # --- [영역 2] 사이드바에서 선택한 섹터별 주요 종목 (별도 분리) ---
    if selected_sector != "선택 안 함 (기본 보기)":
        st.write("---")
        st.write(f"### 사이드바 선택 섹터: [{selected_sector}]")

        if selected_sector == "반도체":
            st.markdown(
                "- **엔비디아**: [나무위키](https://namu.wiki/w/%EC%97%94%EB%B9%84%EB%94%94%EC%95%84) | [야후 파이낸스](https://finance.yahoo.com/quote/NVDA/)"
            )
            st.markdown(
                "- **삼성전자**: [나무위키](https://namu.wiki/w/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90) | [네이버 증권](https://finance.naver.com/item/main.naver?code=005930)"
            )
            st.markdown(
                "- **SK하이닉스**: [나무위키](https://namu.wiki/w/SK%ED%95%98%EC%9D%B4%EB%8B%89%EC%8A%A4) | [네이버 증권](https://finance.naver.com/item/main.naver?code=000660)"
            )
            st.markdown(
                "- **인텔**: [나무위키](https://namu.wiki/w/%EC%9D%B8%ED%85%94) | [야후 파이낸스](https://finance.yahoo.com/quote/INTC/)"
            )
            st.markdown(
                "- **AMD**: [나무위키](https://namu.wiki/w/AMD(기업)) | [야후 파이낸스](https://finance.yahoo.com/quote/AMD/)"
            )
        elif selected_sector == "테크/빅테크":
            st.markdown(
                "- **엔비디아**: [나무위키](https://namu.wiki/w/%EC%97%94%EB%B9%84%EB%94%94%EC%95%84) | [야후 파이낸스](https://finance.yahoo.com/quote/NVDA/)"
            )
            st.markdown(
                "- **테슬라**: [나무위키](https://namu.wiki/w/%ED%85%8C%EC%8A%AC%EB%9D%BC) | [야후 파이낸스](https://finance.yahoo.com/quote/TSLA/)"
            )
            st.markdown(
                "- **애플**: [나무위키](https://namu.wiki/w/%EC%95%A0%ED%94%8C(%EA%B8%B0%EC%97%85)) | [야후 파이낸스](https://finance.yahoo.com/quote/AAPL/)"
            )
        elif selected_sector == "2차전지/에너지":
            st.markdown(
                "- **LG에너지솔루션**: [나무위키](https://namu.wiki/w/LG%EC%97%90%EB%84%88%EC%A7%80%EC%86%94%EB%A3%A8%EC%85%98) | [네이버 증권](https://finance.naver.com/item/main.naver?code=373220)"
            )
            st.markdown(
                "- **삼성SDI**: [나무위키](https://namu.wiki/w/%EC%82%BC%EC%84%B1SDI) | [네이버 증권](https://finance.naver.com/item/main.naver?code=006400)"
            )
        elif selected_sector == "헬스케어/바이오":
            st.markdown(
                "- **삼성바이오로직스**: [나무위키](https://namu.wiki/w/%EC%82%BC%EC%84%B1%EB%B0%94%EC%9D%B4%EC%98%A4%EB%A1%9C%EC%A7%85%EC%8A%A4) | [네이버 증권](https://finance.naver.com/item/main.naver?code=207940)"
            )
        elif selected_sector == "금융/고배당":
            st.markdown(
                "- **SCHD ETF**: [SCHD (나무위키)](https://namu.wiki/w/SCHD) | [야후 파이낸스](https://finance.yahoo.com/quote/SCHD/)"
            )
            st.markdown(
                "- **KB금융**: [나무위키](https://namu.wiki/w/KB%EA%B8%88%EC%9C%B5%EA%B7%B8%EB%A3%B9) | [네이버 증권](https://finance.naver.com/item/main.naver?code=105560)"
            )

    # 다시 하기 버튼
    st.write("---")
    if st.button("다시 진단하기"):
        st.session_state.submitted = False
        st.rerun()
