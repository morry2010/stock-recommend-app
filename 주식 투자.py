import streamlit as st

# 웹 페이지 기본 설정
st.set_page_config(page_title="맞춤형 주식 추천 앱", page_icon="📈")

# 1. 화면 전환을 위한 상태값 초기화
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "score" not in st.session_state:
    st.session_state.score = 0

# ---------------------------------------------------------
# [화면 A] 설문조사 페이지 (제출하기 전)
# ---------------------------------------------------------
if not st.session_state.submitted:
    st.title("📊 나의 투자 성향 진단 & 주식 추천")
    st.caption("간단한 설문을 통해 당신의 투자 성향을 분석해 드립니다.")
    st.markdown("---")

    with st.form("survey_form"):
        st.subheader("📝 투자 성향 진단 설문")
        
        q1 = st.radio(
            "1. 투자 목적이 무엇인가요?",
            ["원금 보존이 가장 중요하며 소소한 이자 수준 원함", "적당한 위험을 감수하고 은행 금리보다 높은 수익 원함", "고위험을 감수하더라도 단기간 높은 수익 원함"],
            index=0
        )
        
        q2 = st.radio(
            "2. 투자금에 손실이 발생하면 어떻게 하실 건가요?",
            ["-5%만 손실이 나도 바로 매도한다", "-15% 정도까지는 견딜 수 있다", "-30% 이상 손실이 나도 더 살 기회로 본다"],
            index=0
        )
        
        q3 = st.radio(
            "3. 주식/금융 상품 투자 경험은 어느 정도인가요?",
            ["투자가 처음이거나 예/적금만 해봤다", "주식/펀드 투자 경험이 1~3년 정도 있다", "주식/파생상품 등 다양한 고위험 투자 경험이 풍부하다"],
            index=0
        )
        
        q4 = st.radio(
            "4. 이 자금은 언제 사용할 예정인가요?",
            ["1년 이내에 사용해야 하는 긴급 자금", "1년 ~ 3년 이내 사용 예정 자금", "3년 이상 여유 있게 묻어둘 수 있는 자금"],
            index=0
        )

        submitted = st.form_submit_button("결과 확인하기")

    # 제출 버튼을 눌렀을 때
    if submitted:
        score = 0
        if "원금 보존" in q1: score += 1
        elif "적당한 위험" in q1: score += 2
        else: score += 3
            
        if "-5%" in q2: score += 1
        elif "-15%" in q2: score += 2
        else: score += 3
            
        if "처음이거나" in q3: score += 1
        elif "1~3년" in q3: score += 2
        else: score += 3
            
        if "1년 이내" in q4: score += 1
        elif "1년 ~ 3년" in q4: score += 2
        else: score += 3

        # 점수를 저장하고 제출 상태를 True로 바꾼 뒤 화면 새로고침
        st.session_state.score = score
        st.session_state.submitted = True
        st.rerun()

# ---------------------------------------------------------
# [화면 B] 결과 페이지 (제출한 후)
# ---------------------------------------------------------
else:
    st.title("🎉 진단 결과 및 맞춤 주식 추천")
    st.markdown("---")
    
    score = st.session_state.score

    # 점수 기준 유형 판별
    if score <= 6:
        user_type = "안정형 🛡️"
        desc = "원금 손실 위험을 최소화하는 것을 선호하시는군요!"
        recommendations = ["삼성전자 (대표 우량주)", "KODEX 200 (대형주 ETF)", "TIGER 미국S&P500 (지수 추종 ETF)"]
    elif score <= 9:
        user_type = "위험중립형 ⚖️"
        desc = "적절한 위험과 수익의 균형을 중시하시는군요!"
        recommendations = ["NAVER / 카카오 (IT 성장주)", "현대차 / 기아 (실적 우량주)", "KODEX 반도체 (섹터 ETF)"]
    else:
        user_type = "적극투자형 🚀"
        desc = "높은 수익을 위해 위험을 감수할 준비가 되셨군요!"
        recommendations = ["테슬라 / 엔비디아 (해외 고성장주)", "알테오젠 / 바이오 관련주", "KODEX 2차전지산업 (변동성 높은 섹터 ETF)"]

    st.success(f"당신의 투자 성향은 **[{user_type}]** 입니다.")
    st.write(desc)
    
    st.markdown("### 📌 추천 종목 리스트")
    for item in recommendations:
        st.write(f"- {item}")
    
    st.markdown("---")
    
    # 다시 처음으로 돌아가는 버튼
    if st.button("🔄 다시 테스트하기"):
        st.session_state.submitted = False
        st.session_state.score = 0
        st.rerun()
