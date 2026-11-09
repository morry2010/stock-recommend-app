import pandas as pd
import plotly.express as px
import streamlit as st

st.title("📈 맞춤형 자산 배분 추천")

# 1. 사용자 투자 성향 선택
option = st.selectbox(
    "당신의 투자 성향을 선택하세요:",
    ["보수형 (Conservative)", "중립형 (Balanced)", "공격형 (Aggressive)"],
)

# 2. 성향에 따른 자산 배분 데이터 설정 (주식 외에 채권, 현금 등 다양한 자산 포함)
if "보수형" in option:
    data = {
        "자산군": ["국채/채권", "예금/현금", "대형주 주식"],
        "비중(%)": [60, 30, 10],
    }
elif "중립형" in option:
    data = {
        "자산군": ["국내/해외 주식", "채권", "현금/원자재"],
        "비중(%)": [40, 40, 20],
    }
else:  # 공격형
    data = {
        "자산군": ["성장주/해외주식", "가상자산/원자재", "채권"],
        "비중(%)": [70, 20, 10],
    }

df = pd.DataFrame(data)

# 3. 데이터 프레임(표) 출력
st.subheader("💡 추천 자산 비중")
st.dataframe(df, use_container_width=True)

# 4. Plotly 도넛 차트(원 다이어그램) 생성 및 출력
fig = px.pie(
    df,
    values="비중(%)",
    names="자산군",
    title=f"{option} 자산 배분 도넛 차트",
    hole=0.4,  # 가운데 구멍을 뚫어 도넛 형태로 만듦
)

# 스트림릿 화면에 차트 출력
st.plotly_chart(fig, use_container_width=True)
