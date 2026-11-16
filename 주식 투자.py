import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# 페이지 설정 (와이드 모드 적용)
st.set_page_config(
    page_title="맞춤형 투자 성향 진단 및 테마별 자산 배분",
    page_icon="📈",
    layout="wide",
)

# --- [커스텀 CSS 디자인] ---
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1f2937;
    }
    .card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("맞춤형 투자 성향 진단 및 미래 성장 테마 대시보드 (Pro)")
st.caption(
    "설문을 통해 나의 투자 성향을 진단하고, 멀티탭과 백테스팅이 강화된 최적"
    " 포트폴리오를 탐색하세요."
)


# --- [야후 파이낸스 데이터 일괄 연동 및 최적화 함수] ---
@st.cache_data(ttl=3600)
def get_portfolio_data(tickers, period="1y"):
  try:
    data = yf.download(tickers, period=period, progress=False)["Close"]
    if isinstance(data, pd.Series):
      data = data.to_frame()
    return data
  except Exception:
    return pd.DataFrame()


# --- [9가지 투자 성향 데이터베이스] ---
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

# --- [10가지 미래 성장 테마 데이터베이스] ---
THEME_DATABASE = {
    "AI 반도체 및 인프라": [
        ("엔비디아", "NVDA", "yahoo"),
        ("브로드컴", "AVGO", "yahoo"),
        ("마이크론", "MU", "yahoo"),
        ("삼성전자", "005930", "naver"),
        ("SK하이닉스", "000660", "naver"),
        ("한미반도체", "042700", "naver"),
    ],
    "빅테크 및 클라우드 소프트웨어": [
        ("마이크로소프트", "MSFT", "yahoo"),
        ("알파벳", "GOOGL", "yahoo"),
        ("아마존", "AMZN", "yahoo"),
        ("메타", "META", "yahoo"),
        ("애플", "AAPL", "yahoo"),
        ("NAVER", "035420", "naver"),
    ],
    "전력 인프라 및 원자력": [
        ("이튼", "ETN", "yahoo"),
        ("GE버노바", "GEV", "yahoo"),
        ("콘스텔레이션 에너지", "CEG", "yahoo"),
        ("HD현대일렉트릭", "267260", "naver"),
        ("효성중공업", "298040", "naver"),
        ("두산에너빌리티", "034020", "naver"),
    ],
    "방위산업": [
        ("록히드 마틴", "LMT", "yahoo"),
        ("RTX 코퍼레이션", "RTX", "yahoo"),
        ("팔란티어", "PLTR", "yahoo"),
        ("한화에어로스페이스", "012450", "naver"),
        ("현대로템", "064350", "naver"),
        ("LIG넥스원", "079550", "naver"),
    ],
    "조선 및 해양 인프라": [
        ("헌팅턴잉걸스 인더스트리스", "HII", "yahoo"),
        ("HD한국조선해양", "009540", "naver"),
        ("삼성중공업", "010140", "naver"),
        ("HD현대중공업", "329180", "naver"),
        ("한화오션", "042660", "naver"),
        ("HJ중공업", "097230", "naver"),
    ],
    "우주항공 및 양자 테크": [
        ("스페이스X", "SPCX", "yahoo"),
        ("로켓랩", "RKLB", "yahoo"),
        ("아이온큐", "IONQ", "yahoo"),
        ("리게티 컴퓨팅", "RGTI", "yahoo"),
        ("디웨이브 퀀텀", "QBTS", "yahoo"),
        ("이노스페이스", "462350", "naver"),
    ],
    "2차전지 및 에너지저장장치(ESS)": [
        ("테슬라", "TSLA", "yahoo"),
        ("앨버마일", "ALB", "yahoo"),
        ("퀀텀스케이프", "QS", "yahoo"),
        ("LG에너지솔루션", "373220", "naver"),
        ("삼성SDI", "006400", "naver"),
        ("POSCO홀딩스", "005490", "naver"),
    ],
    "바이오 및 헬스케어": [
        ("일라이 릴리", "LLY", "yahoo"),
        ("노보 노디스크", "NVO", "yahoo"),
        ("머크", "MRK", "yahoo"),
        ("삼성바이오로직스", "207940", "naver"),
        ("셀트리온", "068270", "naver"),
        ("알테오젠", "196170", "naver"),
    ],
    "에너지 서비스 및 전통 자원": [
        ("엑슨모빌", "XOM", "yahoo"),
        ("셰브론", "CVX", "yahoo"),
        ("슐룸베르거", "SLB", "yahoo"),
        ("S-Oil", "010950", "naver"),
        ("SK이노베이션", "096770", "naver"),
        ("포스코인터내셔널", "047050", "naver"),
    ],
    "핀테크, 보안 및 가상자산 인프라": [
        ("코인베이스", "COIN", "yahoo"),
        ("블록", "SQ", "yahoo"),
        ("마이크로스트래티지", "MSTR", "yahoo"),
        ("로빈후드", "HOOD", "yahoo"),
        ("카카오페이", "377300", "naver"),
        ("NHN한국사이버결제", "060250", "naver"),
    ],
}

# --- [사이드바 영역] ---
with st.sidebar:
  st.header("🔍 미래 성장 테마 탐색")
  st.divider()

  selected_theme = st.selectbox(
      "관심 있는 테마를 선택하세요:",
      ["선택 안 함 (기본 보기)"] + list(THEME_DATABASE.keys()),
  )
  st.divider()
  st.info(
      "💡 사이드바에서 테마를 선택하시면 하단에 해당 글로벌 및 국내 대표 종목들의"
      " 실시간 링크 카드가 표시됩니다."
  )

# 세션 상태 초기화
if "submitted" not in st.session_state:
  st.session_state.submitted = False

# 제출 전 (설문 화면)
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
    s1 = 1 if "원금 손실은 절대" in q1 else (2 if "어느 정도의 시장 변동" in q1 else 3)
    s2 = 1 if "은퇴 및 노후" in q2 else (2 if "내집 마련" in q2 else 3)
    s3 = 1 if "바로 매도" in q3 else (2 if "지켜보며 회복" in q3 else 3)

    if s1 == 1:
      user_type = (
          "보수형 - 노후 안정 지향형"
          if s2 == 1
          else (
              "보수형 - 목돈 마련 안정형"
              if s2 == 2
              else "보수형 - 단기 자금 파킹형"
          )
      )
    elif s1 == 2:
      user_type = (
          "중립형 - 은퇴 준비 밸런스형"
          if s2 == 1
          else (
              "중립형 - 6:4 표준 성장형"
              if s2 == 2
              else "중립형 - 단기 스윙 밸런스형"
          )
      )
    else:
      user_type = (
          "공격형 - 장기 기술주 집중형"
          if s2 == 1
          else (
              "공격형 - 고성장 시드머니형"
              if s2 == 2
              else "공격형 - 초고위험 트레이딩형"
          )
      )

    st.session_state.diagnosed_type = user_type
    st.session_state.selected_type = user_type
    st.session_state.submitted = True
    st.rerun()

# 제출 후 (결과 대시보드 화면)
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

  # 데이터 가져오기
  assets = TYPE_DATABASE[st.session_state.selected_type]
  names = [item["name"] for item in assets]
  tickers = [item["ticker"] for item in assets]
  weights = [item["weight"] for item in assets]

  price_df = get_portfolio_data(tickers, period=selected_period)

  returns = []
  for item in assets:
    t = item["ticker"]
    fallback = item["fallback"]
    try:
      if t in price_df and not price_df[t].dropna().empty:
        s_series = price_df[t].dropna()
        start, latest = s_series.iloc[0], s_series.iloc[-1]
        if selected_period == "3y" and start > 0:
          ret = round(
              (pow(latest / start, 1 / 3) - 1) * 100,
              2,
          )
        elif selected_period == "5y" and start > 0:
          ret = round(
              (pow(latest / start, 1 / 5) - 1) * 100,
              2,
          )
        else:
          ret = round(((latest - start) / start) * 100, 2)
      else:
        ret = fallback
    except Exception:
      ret = fallback
    returns.append(ret)

  portfolio_return = sum((w / 100) * r for w, r in zip(weights, returns))

  # 성과 강조 카드
  st.markdown(
      f"""
    <div style="background-color: #f0f4f8; padding: 20px; border-radius: 10px; border-left: 5px solid #1a73e8; margin-bottom: 20px;">
        <h4 style="margin: 0; color: #1a73e8;">[{st.session_state.selected_type}] 포트폴리오 요약</h4>
        <p style="font-size: 22px; font-weight: bold; margin: 10px 0 0 0; color: #333;">{period_label} 환산 종합 성과: +{round(portfolio_return, 2)}%</p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # --- [멀티탭 구조 도입] ---
  tab1, tab2, tab3 = st.tabs(
      [
          "📊 자산 배분 및 구성 비중",
          "📈 포트폴리오 백테스팅 (수익률 추이)",
          "🎯 맞춤 추천 자산 링크",
      ]
  )

  with tab1:
    col_t1, col_t2 = st.columns([1.3, 1])
    df_data = {
        "자산군": names,
        "대표 ETF 상품 (티커)": tickers,
        "비중(%)": weights,
        f"{period_label} 성과(%)": returns,
    }
    df = pd.DataFrame(df_data)
    df.index = range(1, len(df) + 1)

    with col_t1:
      st.write(f"### 자산군별 비중 및 {period_label} 성과")
      st.dataframe(df, use_container_width=True)

    with col_t2:
      st.write("### 자산 배분 비중 분석")
      fig_pie = px.pie(
          df,
          values="비중(%)",
          names="자산군",
          hole=0.4,
          color_discrete_sequence=px.colors.qualitative.Set3,
      )
      fig_pie.update_layout(
          margin=dict(t=10, b=10, l=10, r=10),
          height=260,
          legend=dict(orientation="h"),
      )
      st.plotly_chart(fig_pie, use_container_width=True)

  with tab2:
    st.write(f"### 📉 포트폴리오 누적 수익률 추이 ({period_label})")
    try:
      if not price_df.empty:
        norm_df = price_df.dropna()
        if not norm_df.empty:
          norm_df = norm_df / norm_df.iloc[0]
          portfolio_series = sum(
              norm_df[t] * (w / 100) for t, w in zip(tickers, weights) if t in norm_df
          )
          st.line_chart(portfolio_series)
        else:
          st.info(
              "선택한 기간의 시계열 차트 데이터를 계산할 수 없습니다 (Fallback"
              " 모드)."
          )
      else:
        st.info("데이터 로딩 중...")
    except Exception as e:
      st.warning(f"차트 생성 중 오류가 발생했습니다: {e}")

  with tab3:
    st.write(
        f"### 🎯 [{st.session_state.selected_type}] 맞춤 추천 자산 및 관련 링크"
    )
    cols = st.columns(len(assets))
    for idx, item in enumerate(assets):
      with cols[idx]:
        st.markdown(
            f"""
                <div class="card">
                    <b>{item['name']}</b><br>
                    <span style="color: #666; font-size: 13px;">티커: {item['ticker']} ({item['weight']}%)</span><br><br>
                    <a href="https://finance.yahoo.com/quote/{item['ticker']}/" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: bold; font-size: 14px;">🔗 야후 파이낸스 보기</a>
                </div>
                """,
            unsafe_allow_html=True,
        )

# --- [사이드바 선택 테마별 종목 탐색 카드 섹션] ---
if selected_theme != "선택 안 함 (기본 보기)":
  st.markdown("---")
  st.markdown(f"### 🚀 미래 성장 테마 탐색: [{selected_theme}]")
  theme_stocks = THEME_DATABASE[selected_theme]
  t_cols = st.columns(3)

  for idx, (s_name, s_code, s_type) in enumerate(theme_stocks):
    if s_type == "yahoo":
      link = f"https://finance.yahoo.com/quote/{s_code}/"
      link_html = f'<a href="{link}" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: bold; font-size: 14px;">🔗 야후 파이낸스 바로가기</a>'
    else:
      link = f"https://finance.naver.com/item/main.naver?code={s_code}"
      link_html = f'<a href="{link}" target="_blank" style="text-decoration: none; color: #1a73e8; font-weight: bold; font-size: 14px;">🔗 네이버 증권 바로가기</a>'

    with t_cols[idx % 3]:
      st.markdown(
          f"""
            <div class="card">
                <b style="font-size: 16px; color: #1f2937;">{s_name}</b><br>
                <span style="color: #666; font-size: 13px;">코드/티커: {s_code}</span><br><br>
                {link_html}
            </div>
            """,
          unsafe_allow_html=True,
      )

# 다시 하기 버튼
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
  if st.button(
      "🔄 처음부터 설문 다시 진단하기", type="secondary", use_container_width=True
  ):
    st.session_state.submitted = False
    st.rerun()
