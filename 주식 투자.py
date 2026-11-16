import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드 적용으로 넓고 시원한 레이아웃 구성)
st.set_page_config(
    page_title="맞춤형 투자 성향 진단 및 자산 배분",
    page_icon="📈",
    layout="wide",
)

# --- [커스텀 CSS 디자인 (깔끔한 핀테크 대시보드 스타일)] ---
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("맞춤형 투자 성향 진단 및 자산 배분 대시보드")
st.caption(
    "설문을 통해 나의 투자 성향을 진단하고, 실시간 글로벌 ETF 데이터 기반의 최적"
    " 포트폴리오를 확인하세요."
)


# --- [야후 파이낸스 데이터 연동 함수] ---
@st.cache_data(ttl=3600)
def get_asset_data(ticker_symbol, period="1y", fallback_return=5.0):
  try:
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)

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


# --- [9가지 전체 유형 데이터베이스 정의] ---
TYPE_DATABASE = {
    "보수형 - 노후 안정 지향형": [
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
    ],
    "보수형 - 목돈 마련 안정형": [
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
    ],
    "보수형 - 단기 자금 파킹형": [
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
    ],
    "중립형 - 은퇴 준비 밸런스형": [
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
    ],
    "중립형 - 6:4 표준 성장형": [
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
    ],
    "중립형 - 단기 스윙 밸런스형": [
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
    ],
    "공격형 - 장기 기술주 집중형": [
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
    ],
    "공격형 - 고성장 시드머니형": [
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
    ],
    "공격형 - 초고위험 트레이딩형": [
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
    ],
}


# --- [사이드바 영역] ---
with st.sidebar:
  st.header("메뉴 및 설정")
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
      "💡 사이드바에서 섹터를 선택하면 화면 하단에 해당 종목과 바로가기 링크가"
      " 표시됩니다."
  )


# 세션 상태 초기화
if "submitted" not in st.session_state:
  st.session_state.submitted = False

# 제출을 안 한 상태일 때만 질문과 버튼을 보여줌
if not st.session_state.submitted:
  st.markdown("### 📋 투자 성향 진단 설문")
  st.write("아래 문항에 응답하신 후 **[결과 확인하기]** 버튼을 눌러주세요.")
  st.markdown("---")

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

  st.markdown("---")
  if st.button("결과 확인하기", type="primary", use_container_width=True):
    if "원금 손실은 절대" in q1:
      s1 = 1
    elif "어느 정도의 시장 변동" in q1:
      s1 = 2
    else:
      s1 = 3

    if "은퇴 및 노후" in q2:
      s2 = 1
    elif "내집 마련" in q2:
      s2 = 2
    else:
      s2 = 3

    if "바로 매도" in q3:
      s3 = 1
    elif "지켜보며 회복" in q3:
      s3 = 2
    else:
      s3 = 3

    if s1 == 1:
      if s2 == 1:
        user_type = "보수형 - 노후 안정 지향형"
      elif s2 == 2:
        user_type = "보수형 - 목돈 마련 안정형"
      else:
        user_type = "보수형 - 단기 자금 파킹형"
    elif s1 == 2:
      if s2 == 1:
        user_type = "중립형 - 은퇴 준비 밸런스형"
      elif s2 == 2:
        user_type = "중립형 - 6:4 표준 성장형"
      else:
        user_type = "중립형 - 단기 스윙 밸런스형"
    else:
      if s2 == 1:
        user_type = "공격형 - 장기 기술주 집중형"
      elif s2 == 2:
        user_type = "공격형 - 고성장 시드머니형"
      else:
        user_type = "공격형 - 초고위험 트레이딩형"

    st.session_state.diagnosed_type = user_type
    st.session_state.selected_type = user_type
    st.session_state.submitted = True
    st.rerun()

# 제출을 완료한 상태일 때 (결과 화면)
else:
  st.success("설문 진단이 완료되었습니다!")

  # 상단 컨트롤 영역
  col_top1, col_top2 = st.columns([2, 1])
  with col_top1:
    all_types = list(TYPE_DATABASE.keys())
    current_index = all_types.index(st.session_state.selected_type)
    selected_view_type = st.selectbox(
        "🔍 다른 투자 성향 포트폴리오 즉시 비교",
        all_types,
        index=current_index,
    )
    st.session_state.selected_type = selected_view_type

  with col_top2:
    period_label = st.selectbox(
        "성과 기간 선택", ["최근 1년", "최근 3년", "최근 5년"]
    )

  period_map = {"최근 1년": "1y", "최근 3년": "3y", "최근 5년": "5y"}
  selected_period = period_map[period_label]

  st.markdown("---")

  # 선택된 유형의 자산 데이터 가져오기
  assets = TYPE_DATABASE[st.session_state.selected_type]
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

  # 성과 지표 강조 카드 박스
  st.markdown(
      f"""
    <div style="background-color: #f0f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #1a73e8; margin-bottom: 25px;">
        <h4 style="margin: 0; color: #1a73e8;">[{st.session_state.selected_type}] 포트폴리오 요약</h4>
        <p style="font-size: 22px; font-weight: bold; margin: 10px 0 0 0; color: #333;">{period_label} 환산 종합 성과: +{round(portfolio_return, 2)}%</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 데이터프레임 구성 및 시각화를 좌우 2단 컬럼으로 배치
  df_data = {
      "자산군": names,
      "대표 ETF 상품 (티커)": tickers,
      "비중(%)": weights,
      f"{period_label} 성과(%)": returns,
      "현재 배당수익률(%)": div_yields,
  }
  df = pd.DataFrame(df_data)
  df.index = range(1, len(df) + 1)

  col_tab1, col_tab2 = st.columns([1.3, 1])

  with col_tab1:
    st.write(f"### 자산군별 비중 및 {period_label} 성과")
    st.dataframe(df, use_container_width=True)
    st.caption(
        "💡 일반 개인이 직접 채권이나 실물 자산을 매수하기 어렵기 때문에, 증권사에서"
        " 쉽게 거래할 수 있는 세계적인 대표 미국 ETF 상품을 연동하고 있습니다."
    )

  with col_tab2:
    st.write("### 자산 배분 비중 분석")
    fig_pie = px.pie(
        df,
        values="비중(%)",
        names="자산군",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig_pie.update_layout(
        margin=dict(t=10, b=10, l=10, r=10), height=280, legend=dict(orientation="h")
    )
    st.plotly_chart(fig_pie, use_container_width=True)

  # --- [맞춤 추천 자산 카드 섹션] ---
  st.markdown("---")
  st.markdown(
      f"### 🎯 [{st.session_state.selected_type}] 맞춤 추천 자산 및 관련 링크"
  )

  cols = st.columns(len(assets))
  for idx, item in enumerate(assets):
    with cols[idx]:
      st.markdown(
          f"""
            <div style="background-color: #ffffff; padding: 16px; border-radius: 8px; border: 1px solid #e0e0e0; height: 100%;">
                <b>{item['name']}</b><br>
                <span style="color: #666; font-size: 13px;">티커: {item['ticker']} ({item['weight']}%)</span><br><br>
                <a href="https://finance.yahoo.com/quote/{item['ticker']}/" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: bold; font-size: 14px;">🔗 야후 파이낸스 보기</a>
            </div>
            """,
          unsafe_allow_html=True,
      )

  # --- [사이드바 섹터 선택 종목 카드 섹션] ---
  if selected_sector != "선택 안 함 (기본 보기)":
    st.markdown("---")
    st.markdown(f"### 🔍 사이드바 선택 섹터: [{selected_sector}]")

    if selected_sector == "반도체":
      sector_items = [
          ("엔비디아", "NVDA", "야후 파이낸스"),
          ("삼성전자", "005930", "네이버 증권"),
          ("SK하이닉스", "000660", "네이버 증권"),
          ("인텔", "INTC", "야후 파이낸스"),
          ("AMD", "AMD", "야후 파이낸스"),
      ]
    elif selected_sector == "테크/빅테크":
      sector_items = [
          ("엔비디아", "NVDA", "야후 파이낸스"),
          ("테슬라", "TSLA", "야후 파이낸스"),
          ("애플", "AAPL", "야후 파이낸스"),
      ]
    elif selected_sector == "2차전지/에너지":
      sector_items = [
          ("LG에너지솔루션", "373220", "네이버 증권"),
          ("삼성SDI", "006400", "네이버 증권"),
      ]
    elif selected_sector == "헬스케어/바이오":
      sector_items = [("삼성바이오로직스", "207940", "네이버 증권")]
    elif selected_sector == "금융/고배당":
      sector_items = [
          ("SCHD ETF", "SCHD", "야후 파이낸스"),
          ("KB금융", "105560", "네이버 증권"),
      ]
    else:
      sector_items = []

    s_cols = st.columns(len(sector_items) if sector_items else 1)
    for idx, (s_name, s_code, s_type) in enumerate(sector_items):
      if s_type == "야후 파이낸스":
        link = f"https://finance.yahoo.com/quote/{s_code}/"
      else:
        link = f"https://finance.naver.com/item/main.naver?code={s_code}"

      with s_cols[idx]:
        st.markdown(
            f"""
                <div style="background-color: #ffffff; padding: 14px; border-radius: 8px; border: 1px solid #e0e0e0; text-align: center;">
                    <b>{s_name}</b><br>
                    <a href="{link}" target="_blank" style="text-decoration: none; color: #1a73e8; font-size: 13px;">🔗 {s_type} 링크</a>
                </div>
                """,
            unsafe_allow_html=True,
        )

  # 다시 하기 버튼
  st.markdown("---")
  col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
  with col_btn2:
    if st.button(
        "🔄 처음부터 설문 다시 진단하기",
        type="secondary",
        use_container_width=True,
    ):
      st.session_state.submitted = False
      st.rerun()
