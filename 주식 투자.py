import pandas as pd
import plotly.express as px
import streamlit as st

st.title("📈 맞춤형 투자 성향 진단 및 자산 배분")
st.write("아래 질문에 답하시면 당신에게 딱 맞는 자산 배분 포트폴리오를 추천해 드립니다!")

st.divider()

# 1. 투자 성향 진단 설문지 (라디오 버튼)
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

# 선택지에 따른 점수 계산
score = 0
for q in [q1, q2, q3]:
    if "(1점)" in q:
        score += 1
    elif "(2점)" in q:
        score += 2
    elif "(3점)" in q:
        score += 3

st.divider()

# 2. 점수에 따른 투자 성향 판별 및 자산 배분 데이터 설정
if score <= 4:
    user_type = "보수형 (Conservative)"
    data = {
        "자산군": ["국채/채권", "예금/현금", "대형주 주식"],
        "비중(%)": [60, 30, 10],
    }
elif score <= 7:
    user_type = "중립형 (Balanced)"
    data = {
        "자산군": ["국내/해외 주식", "채권", "현금/원자재"],
        "비중(%)": [40, 40, 20],
    }
else:
    user_type = "공격형 (Aggressive)"
    data = {
        "자산군": ["성장주/해외주식", "가상자산/원자재", "채권"],
        "비중(%)": [70, 20, 10],
    }

# 3. 진단 결과 출력
st.subheader(f"📊 당신의 진단 점수: {score}점 ➔ **{user_type}**")

df = pd.DataFrame(data)

# 표 출력
st.write("### 💡 추천 자산 비중")
st.dataframe(df, use_container_width=True)

# 4. Plotly 도넛 차트 출력
fig = px.pie(
    df,
    values="비중(%)",
    names="자산군",
    title=f"{user_type} 자산 배분 도넛 차트",
    hole=0.4,
)

st.plotly_chart(fig, use_container_width=True)
