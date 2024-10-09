import openai
import re
import time
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 샘플 포트폴리오 데이터
portfolio = pd.DataFrame({
    "종목": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "수량": [10, 5, 7, 2],
    "현재가": [150, 300, 2800, 3500],
    "평균 매입 가격": [140, 280, 2600, 3400]
})

# 샘플 수익률 데이터
returns_data = pd.DataFrame({
    "날짜": pd.date_range(start="2023-01-01", periods=10, freq='M'),
    "수익률": [0.02, 0.03, 0.015, 0.05, -0.01, 0.04, 0.03, 0.06, -0.02, 0.05]
})
returns_data.set_index("날짜", inplace=True)

# 총 수익률 계산
total_return = round(returns_data["수익률"].sum() * 100, 2)

# 현금 잔고
cash_balance = 10000

# 첫 페이지 (포트폴리오와 수익률 화면)
def main_page():
    st.markdown("<h1 style='text-align: center; color: navy; font-size: 36px; font-weight: bold;'>나무증권</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 보유현황")
        st.dataframe(portfolio, width=500)
        if st.button("맞춤형 헷지 ETF 추천받기"):
            st.session_state.page = "questions"
    
    with col2:
        st.markdown(f"### 총 수익률: {total_return}%")
        st.line_chart(returns_data)


# 상관계수 추출
def extract_correlation_from_gpt_response(responses):
    try:
        correlation = float(responses)  # 직접 responses[9]에서 상관계수를 추출
        return correlation
    except (ValueError, IndexError):
        return 0.3  # 오류 발생 시 기본값 반환

# ChatGPT API를 사용하여 헷지 전략 추천
def recommend_hedge_strategy():
    responses = st.session_state.responses

    # 사용자의 답변을 기반으로 ChatGPT에게 헷지 전략 추천 요청
    prompt = f"""
    다음은 사용자의 헷지 전략 설문 응답입니다:
    1. 자산군: {responses[0]}
    2. 손실 감수 정도: {responses[1]}
    3. 변동성에 대한 인식: {responses[2]}
    4. 자산 배분 비율: {responses[3]}%
    5. 선호하는 헷지 자산: {responses[4]}
    6. 헷지 유지 기간: {responses[5]}
    7. 해외 자산 또는 지수에 대한 헷지: {responses[6]}
    8. 우려되는 경제적 리스크: {responses[7]}
    9. 헷지 전략의 공격성: {responses[8]}
    10. 희망하는 자산군과 헷지 ETF의 상관계수: {responses[9]}

    이 정보를 바탕으로 적절한 헷지 전략을 추천해 주세요. 그리고 사용자에게 추천할 ETF 목록도 제시해 주세요.
    """

    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial expert who specializes in hedge strategies."},
                    {"role": "user", "content": prompt}
                ]
            )

            # GPT 응답 내용
            response_text = response['choices'][0]['message']['content'].strip()

            # 상관계수 추출
            etf_correlation = extract_correlation_from_gpt_response(responses[9])

            return response_text, etf_correlation  # 상관계수와 응답 텍스트 반환

        except openai.error.RateLimitError:
            st.error("API 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
            time.sleep(60)

# 시나리오 분석을 통한 방어율 계산 함수
def calculate_defensive_performance(etf_correlation, market_drop_percentages=[10, 20, 30]):
    performance = {}
    for drop in market_drop_percentages:
        etf_defensive_rate = (1 - etf_correlation) * drop / 100  # 상관관계가 낮을수록 더 많은 방어율 제공
        performance[drop] = etf_defensive_rate * 100  # 백분율로 변환
    return performance

# 시각화 함수 (방어율 그래프)
def plot_defensive_performance(performance):
    fig = go.Figure()

    market_drops = list(performance.keys())
    defense_rates = list(performance.values())

    fig.add_trace(go.Bar(
        x=market_drops,
        y=defense_rates,
        name='방어율',
        marker_color='green'
    ))

    fig.update_layout(
        title="시장 급락 시 예상 방어율",
        xaxis_title="시장 급락 (%)",
        yaxis_title="방어율 (%)",
        bargap=0.5,
        template="plotly_dark"
    )

    st.plotly_chart(fig)

# 헷지 전략 수립을 위한 질문 페이지
def hedge_questions_page():
    st.title("헷지 전략 수립을 위한 질문")

    responses = []
    
    # 질문 1: 자산군
    responses.append(st.text_input("질문 1. 현재 포트폴리오의 자산군은 무엇인가요? (예: 주식, 채권, 부동산, 금, 현금 등)"))

    # 질문 2: 손실 감수 정도
    responses.append(st.radio("질문 2. 시장 하락 시 어느 정도의 손실을 감수할 수 있나요?", 
                              ('전혀 감수할 수 없음', '10%까지', '20%까지', '30% 이상')))
    
    # 질문 3: 포트폴리오의 변동성 인식
    responses.append(st.radio("질문 3. 포트폴리오의 변동성에 대해 어떻게 생각하시나요?", 
                              ('매우 불안함', '약간 불안함', '괜찮음', '안정적이라고 생각함')))
    
    # 질문 4: 헷지 자산 배분 비율
    responses.append(st.slider("질문 4. 시장 하락을 대비한 자산 배분 비율을 얼마나 원하시나요?", 
                               min_value=10, max_value=50, step=1))
    
    # 질문 5: 선호하는 헷지 자산
    responses.append(st.radio("질문 5. 어떤 헷지 자산을 선호하시나요?", 
                              ('금', '변동성 ETF', '채권', '달러', '기타')))
    
    # 질문 6: 헷지 유지 기간
    responses.append(st.radio("질문 6. 포트폴리오의 리스크를 줄이기 위해 헷지를 얼마나 유지할 계획인가요?", 
                              ('1개월 이내', '3개월', '6개월', '1년 이상')))
    
    # 질문 7: 해외 자산 또는 특정 지수 헷지
    responses.append(st.radio("질문 7. 해외 자산 또는 특정 지수에 대한 헷지를 원하시나요?", 
                              ('네', '아니요')))
    
    # 질문 8: 우려되는 경제적 리스크
    responses.append(st.radio("질문 8. 현재 경제 상황에서 가장 우려되는 리스크는 무엇인가요?", 
                              ('인플레이션', '금리 상승', '경기 침체', '글로벌 지정학적 리스크')))
    
    # 질문 9: 헷지 전략의 공격성
    responses.append(st.radio("질문 9. 원하시는 헷지 전략의 공격성은 어느 정도인가요?", 
                              ('매우 보수적', '보수적', '중립', '공격적', '매우 공격적')))
    
    # 질문 10: 자산군과 헷지 ETF 간의 희망 상관계수
    responses.append(st.slider("질문 10. 본인의 자산군과 헷지 ETF 간의 희망 상관계수를 설정하세요.", 
                               min_value=-1.0, max_value=1.0, step=0.1))

    # 답변 제출 버튼
    if st.button("헷지 전략 생성"):
        st.session_state.responses = responses
        st.session_state.page = "hedge_recommendation"

# 헷지 전략 추천 결과 페이지
def hedge_recommendation_page():
    st.title("맞춤형 헷지 전략 및 ETF 추천")

    # ChatGPT를 통해 헷지 전략 추천 결과 가져오기
    hedge_recommendation, etf_correlation = recommend_hedge_strategy()
    st.write(hedge_recommendation)

    # GPT로부터 추천받은 ETF의 방어율 분석 및 시각화
    defense_performance = calculate_defensive_performance(etf_correlation)
    plot_defensive_performance(defense_performance)

    # 다시 시작하기 버튼
    if st.button("다시 시작하기"):
        st.session_state.page = "main"

# 초기 상태 설정 함수
def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = "main"  # 기본 페이지를 'main'으로 설정
    if 'responses' not in st.session_state:
        st.session_state.responses = []  # 사용자 응답 리스트 초기화
    if 'hedge_strategy' not in st.session_state:
        st.session_state.hedge_strategy = {}  # 헷지 전략 저장소 초기화

# 페이지 전환 로직
def main():
    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "questions":
        hedge_questions_page()
    elif st.session_state.page == "hedge_recommendation":
        hedge_recommendation_page()

# 애플리케이션 실행
if __name__ == "__main__":
    initialize_session_state()
    main()
