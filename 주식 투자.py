import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.title("맞춤형 투자 성향 진단 및 자산 배분")


# --- [야후 파이낸스 데이터 연동 함수] ---
@st.cache_data(ttl=3600)
def get_asset_data(ticker_symbol, period="1y", fallback_return=5.0):
  try:
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)

    # 기간별 수익률 계산 (3년, 5년은 연환산 복리 수익률(CAGR) 반영)
    ret = fallback_return
    if not hist.empty:
      start = hist["Close"].iloc[0]
      latest = hist["Close"].iloc[-1]
      if period == "3y":
        ret = round(
            (
                (pow(latest / start, 1 / 3) - 1)
                if start > 0
                else fallback_return
            )
            * 100,
            2,
        )
      elif period == "5y":
        ret = round(
            (
                (pow(latest / start, 1 / 5) - 1)
                if start > 0
                else fallback_return
            )
            * 100,
            2,
        )
      else:
        ret = round(((latest - start) / start) * 100, 2)

    # 현재 배당수익률 가져오기 (단위 버그 방지 및 상한선 처리)
    info = ticker.info
    div_yield = info.get("dividendYield", 0)
    if div_yield is not None:
      if div_yield > 1:
        div_yield = round(div_yield, 2)
      else:
        div_yield = round(div_yield * 100, 2)

      if div_yield > 20.0:
        div_yield = 15.0
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
      "1. 투자 과정에서 마주할 수 있는 시장 변동성과 손실 위험에 대한 본인의"
      " 태도는 어느 쪽에 가까우신가요?",
      [
          (
              "원금 손실은 절대 방어해야 하며, 안정적으로 자산을 지키는 것이"
              " 최우선입니다."
          ),
          (
              "어느 정도의 시장 변동이나 소폭의 손실은 감수하겠지만, 무리한"
              " 위험은 피하고 싶습니다."
          ),
          (
              "더 높은 기대 수익을 얻을 수 있다면, 원금의 단기 하락이나 큰"
              " 변동성은 충분히 감수할 수 있습니다."
          ),
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
      ["바로 매도해서 손실을 최소화함", "지켜보며 회복을 기다림", "추가 매수 기회로 활용함"],
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

    # 총 9가지 세부 유형별 자산 구성 및 일반인 친화적 대표 ETF 티커 매핑
    if s1 == 1:
      if s2 == 1:
        user_type = "보수형 - 노후 안정 지향형"
        assets = [
            {
                "name": "국고채/안전채권 (미국 중기국채)",
                "ticker": "IEF",
                "weight": 50,
                "fallback": 4.2,
            },
            {
                "name": "대형 우량주 (S&P 500)",
                "ticker": "VOO",
                "weight": 30,
                "fallback": 12.5,
            },
            {
                "name": "금/현금 (골드 신탁)",
                "ticker": "IAU",
                "weight": 20,
                "fallback": 18.5,
            },
        ]
      elif s2 == 2:
        user_type = "보수형 - 목돈 마련 안정형"
        assets = [
            {
                "name": "채권형 ETF (미국 종합채권)",
                "ticker": "AGG",
                "weight": 40,
                "fallback": 5.0,
            },
            {
                "name": "배당주 펀드 (미국 고배당)",
                "ticker": "SCHD",
                "weight": 40,
                "fallback": 10.0,
            },
            {
                "name": "단기 예적금 (초단기 국채)",
                "ticker": "SHV",
                "weight": 20,
                "fallback": 3.5,
            },
        ]
      else:
        user_type = "보수형 - 단기 자금 파킹형"
        assets = [
            {
                "name": "CMA/MMF (초단기 현금성)",
                "ticker": "BIL",
                "weight": 60,
                "fallback": 3.6,
            },
            {
                "name": "단기 국채 (1~3년 국채)",
                "ticker": "SHY",
                "weight": 20,
                "fallback": 4.0,
            },
            {
                "name": "우량 회사채 (투자등급)",
                "ticker": "LQD",
                "weight": 20,
                "fallback": 5.2,
            },
        ]
    elif s1 == 2:
      if s2 == 1:
        user_type = "중립형 - 은퇴 준비 밸런스형"
        assets = [
            {
                "name": "S&P 500 ETF (대형주)",
                "ticker": "VOO",
                "weight": 50,
                "fallback": 18.2,
            },
            {
                "name": "종합 채권 ETF",
                "ticker": "AGG",
                "weight": 40,
                "fallback": 4.2,
            },
            {
                "name": "금 (골드 신탁)",
                "ticker": "IAU",
                "weight": 10,
                "fallback": 18.5,
            },
        ]
      elif s2 == 2:
        user_type = "중립형 - 6:4 표준 성장형"
        assets = [
            {
                "name": "주식 성장/대형 (S&P 500)",
                "ticker": "VOO",
                "weight": 60,
                "fallback": 18.2,
            },
            {
                "name": "채권 ETF (종합채권)",
                "ticker": "AGG",
                "weight": 30,
                "fallback": 4.2,
            },
            {
                "name": "원자재/현금 (원자재 지수)",
                "ticker": "GSG",
                "weight": 10,
                "fallback": 15.0,
            },
        ]
      else:
        user_type = "중립형 - 단기 스윙 밸런스형"
        assets = [
            {
                "name": "섹터별 주도주 (테크 섹터)",
                "ticker": "XLK",
                "weight": 50,
                "fallback": 20.0,
            },
            {
                "name": "채권 ETF",
                "ticker": "AGG",
                "weight": 20,
                "fallback": 4.2,
            },
            {
                "name": "현금성 자산 (초단기채)",
                "ticker": "BIL",
                "weight": 30,
                "fallback": 3.5,
            },
        ]
    else:
      if s2 == 1:
        user_type = "공격형 - 장기 기술주 집중형"
        assets = [
            {
                "name": "글로벌 빅테크/AI (나스닥 100)",
                "ticker": "QQQ",
                "weight": 80,
                "fallback": 30.0,
            },
            {
                "name": "혁신 성장 ETF (ARKK)",
                "ticker": "ARKK",
                "weight": 15,
                "fallback": 25.0,
            },
            {
                "name": "채권 ETF",
                "ticker": "AGG",
                "weight": 5,
                "fallback": 4.2,
            },
        ]
      elif s2 == 2:
        user_type = "공격형 - 고성장 시드머니형"
        assets = [
            {
                "name": "미국 성장주 (나스닥 100)",
                "ticker": "QQQ",
                "weight": 75,
                "fallback": 28.5,
            },
            {
                "name": "가상자산/원자재 (골드 신탁)",
                "ticker": "IAU",
                "weight": 20,
                "fallback": 35.0,
            },
            {
                "name": "채권 ETF",
                "ticker": "AGG",
                "weight": 5,
                "fallback": 4.2,
            },
        ]
      else:
        user_type = "공격형 - 초고위험 트레이딩형"
        assets = [
            {
                "name": "가상자산 연계 (비트코인 선물)",
                "ticker": "BITO",
                "weight": 70,
                "fallback": 45.0,
            },
            {
                "name": "레버리지 고변동성 (3배 레버리지)",
                "ticker": "TQQQ",
                "weight": 20,
                "fallback": 30.0,
            },
            {
                "name": "현금성 자산",
                "ticker": "BIL",
                "weight": 10,
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
  st.subheader(f"맞춤 진단 결과 ➔ **{st.session_state.user_type}**")

  col1, col2 = st.columns([2, 1])
  with col2:
    period_label = st.selectbox(
        "성과 기간 선택", ["최근 1년", "최근 3년", "최근 5년"]
    )

  period_map = {"최근 1년": "1y", "최근 3년": "3y", "최근 5년": "5y"}
  selected_period = period_map[period_label]

  assets = st.session_state.assets
  names = [item["name"] for item in assets]
  tickers = [item["ticker"] for item in assets]
  weights = [item["weight"] for item in assets]

  returns = []
  div_yields = []
  for item in assets:
    ret, div = get_asset_data(
        item["ticker"], period=selected_period, fallback_return=item["fallback"]
    )
    returns.append(ret)
    div_yields.append(div)

  portfolio_return = sum((w / 100) * r for w, r in zip(weights, returns))

  st.metric(
      label=f"이 포트폴리오의 [{period_label}] 환산 종합 성과",
      value=f"+{round(portfolio_return, 2)}%",
  )

  # 데이터프레임 구성 (자산군, 대표 ETF 상품(티커), 비중, 선택기간 수익률, 배당수익률)
  df_data = {
      "자산군": names,
      "대표 ETF 상품 (티커)": tickers,
      "비중(%)": weights,
      f"{period_label} 성과(%)": returns,
      "현재 배당수익률(%)": div_yields,
  }
  df = pd.DataFrame(df_data)
  df.index = range(1, len(df) + 1)

  st.write(f"### 자산군별 세부 비중 및 {period_label} 성과 / 배당 현황")
  st.markdown(
      "💡 *일반 개인이 직접 장외 채권이나 실물 자산을 매수하기 어렵기 때문에,"
      " 소액으로 증권사에서 쉽게 거래할 수 있는 세계적인 대표 미국 ETF"
      " 상품들을 백그라운드 실시간 연동에 사용하고 있습니다.*"
  )
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
        "- **국고채(IEF)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/IEF/)"
    )
    st.markdown(
        "- **대형 우량주(VOO)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/VOO/)"
    )
    st.markdown(
        "- **금/현금(IAU)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/IAU/)"
    )
  elif st.session_state.user_type == "보수형 - 목돈 마련 안정형":
    st.markdown(
        "- **채권형 ETF(AGG)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/AGG/)"
    )
    st.markdown(
        "- **배당주 펀드(SCHD)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/SCHD/)"
    )
    st.markdown(
        "- **단기 예적금(SHV)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/SHV/)"
    )
  elif st.session_state.user_type == "보수형 - 단기 자금 파킹형":
    st.markdown(
        "- **CMA/MMF(BIL)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/BIL/)"
    )
    st.markdown(
        "- **단기 국채(SHY)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/SHY/)"
    )
    st.markdown(
        "- **우량 회사채(LQD)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/LQD/)"
    )
  elif "중립형" in st.session_state.user_type:
    st.markdown(
        "- **S&P 500 ETF(VOO)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/VOO/)"
    )
    st.markdown(
        "- **종합 채권(AGG)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/AGG/)"
    )
    st.markdown(
        "- **금(IAU)**: [야후 파이낸스](https://finance.yahoo.com/quote/IAU/)"
    )
  else:
    st.markdown(
        "- **나스닥 100(QQQ)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/QQQ/)"
    )
    st.markdown(
        "- **비트코인 연계(BITO)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/BITO/)"
    )
    st.markdown(
        "- **3배 레버리지(TQQQ)**: [야후"
        " 파이낸스](https://finance.yahoo.com/quote/TQQQ/)"
    )

  # --- [영역 2] 사이드바에서 선택한 섹터별 주요 종목 (별도 분리) ---
  if selected_sector != "선택 안 함 (기본 보기)":
    st.write("---")
    st.write(f"### 사이드바 선택 섹터: [{selected_sector}]")

    if selected_sector == "반도체":
      st.markdown(
          "- **엔비디아**: [야후"
          " 파이낸스](https://finance.yahoo.com/quote/NVDA/)"
      )
      st.markdown(
          "- **삼성전자**: [네이버"
          " 증권](https://finance.naver.com/item/main.naver?code=005930)"
      )
      st.markdown(
          "- **SK하이닉스**: [네이버"
          " 증권](https://finance.naver.com/item/main.naver?code=000660)"
      )
      st.markdown(
          "- **인텔**: [야후 파이낸스](https://finance.yahoo.com/quote/INTC/)"
      )
      st.markdown(
          "- **AMD**: [야후 파이낸스](https://finance.yahoo.com/quote/AMD/)"
      )
    elif selected_sector == "테크/빅테크":
      st.markdown(
          "- **엔비디아**: [야후"
          " 파이낸s](https://finance.yahoo.com/quote/NVDA/)"
      )
      st.markdown(
          "- **테슬라**: [야후"
          " 파이낸스](https://finance.yahoo.com/quote/TSLA/)"
      )
      st.markdown(
          "- **애플**: [야후 파이낸스](https://finance.yahoo.com/quote/AAPL/)"
      )
    elif selected_sector == "2차전지/에너지":
      st.markdown(
          "- **LG에너지솔루션**: [네이버"
          " 증권](https://finance.naver.com/item/main.naver?code=373220)"
      )
      st.markdown(
          "- **삼성SDI**: [네이버"
          " 증권](https://finance.naver.com/item/main.naver?code=006400)"
      )
    elif selected_sector == "헬스케어/바이오":
      st.markdown(
          "- **삼성바이오로직스**: [네이버"
          " 증권](https://finance.naver.com/item/main.naver?code=207940)"
      )
    elif selected_sector == "금융/고배당":
      st.markdown(
          "- **SCHD ETF**: [야후 파이낸스](https://finance.yahoo.com/quote/SCHD/)"
      )
      st.markdown(
          "- **KB금융**: [네이버"
          " 증권](https://finance.naver.com/item/main.naver?code=105560)"
      )

  # 다시 하기 버튼
  st.write("---")
  if st.button("다시 진단하기"):
    st.session_state.submitted = False
    st.rerun()
