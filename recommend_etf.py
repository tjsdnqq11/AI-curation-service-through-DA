import openai
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

openai.api_key = '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'


# GPT API로 점수 계산 요청
def calculate_investor_profile_gpt(responses):
    prompt = f"""
    다음은 사용자의 투자 성향에 대한 응답입니다:
    1. 은퇴 후 목표: {responses[0]}
    2. 위험 감수 성향: {responses[1]}
    3. 소득 창출 중요성: {responses[2]}
    4. 안전 자산 배분: {responses[3]}
    5. 투자 경험: {responses[4]}

    이 정보를 바탕으로 사용자의 투자 성향을 평가하고, 안전성, 수익성, 리스크 수용 성향에 대해 각각 0부터 10까지의 점수를 계산해 주세요.
    또한 각 성향에 맞는 설명을 추가해 주세요.
    결과는 JSON 형식으로 반환해 주세요. 예: {{"scores": {{"안전성": 8, "수익성": 5, "리스크 수용": 7}}, "explanation": "설명 텍스트"}}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial expert who specializes in analyzing investment profiles."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # 응답을 JSON 형식으로 변환
    data = eval(response['choices'][0]['message']['content'].strip())
    return data

# 투자 성향을 스타 그래프로 시각화하는 함수
def plot_investor_profile_radar(scores):
    categories = list(scores.keys())
    values = list(scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='투자 성향'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
        ),
        showlegend=False
    )

    st.plotly_chart(fig)

# GPT로 ETF 추천 받기
def recommend_etf(scores):
    prompt = f"사용자의 투자 성향 분석에 따라 아래 점수를 기반으로 적절한 ETF를 추천해 주세요.\n점수: {scores}"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial advisor who specializes in ETF recommendations."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response['choices'][0]['message']['content'].strip()

# 질문 페이지
def questions_page():
    st.title("생성형 AI를 활용한 중장년층 맞춤 ETF 추천")
    st.markdown("### 투자 성향 분석을 위한 질문")

    responses = []
    
    responses.append(st.text_input("질문 1. 은퇴 후 어떤 목표를 가지고 투자하고 계신가요? (예: 소득 창출, 자산 보전 등)"))
    responses.append(st.radio("질문 2. 시장의 변동성에 대해 어느 정도의 위험을 감수할 준비가 되어 있나요?", 
                              ('매우 낮음', '낮음', '보통', '높음', '매우 높음')))
    responses.append(st.radio("질문 3. 안정적인 현금흐름, 수익률 중 어떤 것이 중요한가요?", 
                              ('안정적인 현금흐름', '수익률')))
    responses.append(st.radio("질문 4. 자산의 안전성을 위해 더 많은 자산을 채권이나 배당주 같은 안전한 자산에 배분할 계획이 있으신가요?", 
                              ('네, 더 많은 비중을 할당할 계획입니다', '일부만 할당할 계획입니다', '안전 자산에 대한 배분을 고려하지 않습니다')))
    responses.append(st.text_input("질문 5. 투자 경험이 어느 정도이신가요? (예: 초보자, 중급자, 고급자)"))

    if st.button("결과 분석"):
        st.session_state.responses = responses
        st.session_state.page = 'result'

# 결과 페이지
def result_page():
    st.title("투자 성향 분석 결과")

    # GPT로부터 투자 성향 점수 및 설명을 계산
    data = calculate_investor_profile_gpt(st.session_state.responses)
    scores = data['scores']
    explanation = data['explanation']

    col1, col2 = st.columns([2, 1])

    # 투자 성향 시각화 (스타 그래프)
    with col1:
        st.markdown("### 투자 성향 분석 결과")
        plot_investor_profile_radar(scores)
        
        # GPT로부터 ETF 추천 받기
        etf_recommendation = recommend_etf(scores)
        st.markdown("### 추천 ETF")
        st.write(etf_recommendation)

    # 투자 성향 설명 및 ETF 추천
    with col2:
        st.markdown("### 투자 성향 분석 설명")
        st.write(explanation)

    

    # 다시 시작하기 버튼
    if st.button("다시 시작하기"):
        st.session_state.page = "main"

# 페이지 전환 로직
def main():
    if st.session_state.page == "main":
        questions_page()
    elif st.session_state.page == "result":
        result_page()

# 애플리케이션 실행
if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = "main"
    main()