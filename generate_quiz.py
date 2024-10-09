import openai
import streamlit as st

# OpenAI API 키 설정
openai.api_key = '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'

# ChatGPT 호출 함수 - 퀴즈 생성
def generate_quiz(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # 최신 모델로 변경
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,  # 응답의 최대 길이
        temperature=0.7  # 창의적 답변을 위한 설정
    )
    return response['choices'][0]['message']['content'].strip()

def parse_quiz_response(response):
    lines = response.split("\n")
    question = ""
    options = {}
    answer = ""
    explanation = ""
    
    for line in lines:
        if line.startswith("Question:"):
            question = line[len("Question:"):].strip()
        elif line.startswith("Option1:"):
            options['A'] = line[len("Option1:"):].strip()
        elif line.startswith("Option2:"):
            options['B'] = line[len("Option2:"):].strip()
        elif line.startswith("Option3:"):
            options['C'] = line[len("Option3:"):].strip()
        elif line.startswith("Option4:"):
            options['D'] = line[len("Option4:"):].strip()
        elif line.startswith("Answer:"):
            answer = line[len("Answer:"):].strip()
        elif line.startswith("Explanation:"):
            explanation = line[len("Explanation:"):].strip()

    return question, options, answer, explanation

# 새로운 문제를 생성하는 함수
# 새로운 문제를 생성하는 함수
def generate_new_quiz():
    # 새로운 문제 생성 요청
    prompt = """
    주식투자에 연관되어있는 경제지표 위주로 경제지표 관련 객관식 문제를 한국어로 하나 만들어줘.
    응답은 다음 형식으로 제공해줘:
    Question: (문제 내용)
    Option1: A) 선택지1 
    Option2: B) 선택지2 
    Option3: C) 선택지3
    Option4: D) 선택지4
    Answer: 정답
    Explanation: 설명
    """
    
    quiz_response = generate_quiz(prompt)  # GPT로부터 퀴즈 생성
    question, options, correct_answer, explanation = parse_quiz_response(quiz_response)

    # 문제 중복 확인 및 저장
    if question not in st.session_state.asked_questions:
        st.session_state.asked_questions.append(question)
        st.session_state.quiz = question
        st.session_state.options = options  # 선택지를 저장
        st.session_state.correct_answer = correct_answer
        st.session_state.explanation = explanation
    else:
        generate_new_quiz()  # 중복된 문제가 나오면 새로 생성

# 퀴즈 페이지
def quiz_page():
    st.title("안전한 투자를 위한 금융경제 퀴즈")
    
    # 퀴즈가 없을 경우 새 문제 생성
    if st.session_state.quiz == "":
        generate_new_quiz()

    # 퀴즈 출력 및 선택지 표시
    st.write(f"문제: {st.session_state.quiz}")

    # 선택지 출력
    options_list = [f"{st.session_state.options['A']}",
                    f"{st.session_state.options['B']}",
                    f"{st.session_state.options['C']}",
                    f"{st.session_state.options['D']}"]
    
    # 라디오 버튼으로 선택지 제공
    st.session_state.answer = st.radio("정답을 선택하세요:", options_list)

    # 정답 제출 버튼
    if st.button("정답 제출"):
        st.session_state.submitted = True  # 정답 제출 여부를 저장
        st.session_state.page = 'answer'  # 정답 페이지로 이동

# 정답 및 설명 페이지
def answer_page():
    st.title("정답 및 설명")

    st.write(f"정답: {st.session_state.correct_answer}")
    st.write("관련 설명:")
    st.write(st.session_state.explanation)

    if st.button("다음 문제"):
        generate_new_quiz()
        st.session_state.page = 'quiz'  # 퀴즈 페이지로 이동

# 페이지 관리 로직
def main():
    # 세션 상태 초기화
    if 'page' not in st.session_state:
        st.session_state.page = 'quiz'
    if 'quiz' not in st.session_state:
        st.session_state.quiz = ""
        st.session_state.show_explanation = False
        st.session_state.answer = ""
        st.session_state.correct_answer = ""
        st.session_state.explanation = ""
        st.session_state.options = {}
        st.session_state.asked_questions = []  # 중복 문제 방지용 리스트
        st.session_state.submitted = False  # 정답 제출 여부

    # 페이지 라우팅
    if st.session_state.page == 'quiz':
        quiz_page()
    elif st.session_state.page == 'answer':
        if st.session_state.submitted:  # 정답 제출 후에만 정답 페이지로 이동
            answer_page()

# 애플리케이션 실행
if __name__ == "__main__":
    main()