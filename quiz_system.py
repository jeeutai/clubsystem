import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import random


class QuizSystem:

    def __init__(self):
        self.quizzes_file = 'data/quizzes.csv'
        self.quiz_responses_file = 'data/quiz_responses.csv'
        self.initialize_quiz_files()

    def initialize_quiz_files(self):
        """Initialize quiz-related CSV files"""
        # Initialize quizzes.csv
        if not st.session_state.data_manager.load_csv(
                'quizzes').empty is False:
            quizzes_structure = [
                'id', 'title', 'description', 'club', 'creator', 'questions',
                'time_limit', 'attempts_allowed', 'status', 'created_date'
            ]
            empty_df = pd.DataFrame(columns=quizzes_structure)
            st.session_state.data_manager.save_csv('quizzes', empty_df)

        # Initialize quiz_responses.csv
        if not st.session_state.data_manager.load_csv(
                'quiz_responses').empty is False:
            responses_structure = [
                'id', 'quiz_id', 'username', 'answers', 'score',
                'total_questions', 'completed_date', 'time_taken'
            ]
            empty_df = pd.DataFrame(columns=responses_structure)
            st.session_state.data_manager.save_csv('quiz_responses', empty_df)

    def show_quiz_interface(self, user):
        """Display the quiz interface"""
        st.markdown("### 🧠 퀴즈")

        if user['role'] in ['선생님', '회장', '부회장']:
            tabs = st.tabs(["📝 퀴즈 목록", "➕ 퀴즈 생성", "📊 결과 분석"])
        else:
            tabs = st.tabs(["📝 퀴즈 목록", "📈 내 점수"])

        with tabs[0]:
            self.show_quiz_list(user)

        if user['role'] in ['선생님', '회장', '부회장']:
            with tabs[1]:
                self.show_quiz_creation(user)

            with tabs[2]:
                self.show_quiz_analytics(user)
        else:
            with tabs[1]:
                self.show_my_scores(user)

    def show_quiz_list(self, user):
        """Display available quizzes"""
        st.markdown("#### 📝 사용 가능한 퀴즈")

        quizzes_df = st.session_state.data_manager.load_csv('quizzes')

        if quizzes_df.empty:
            st.info("등록된 퀴즈가 없습니다.")
            return

        # Filter quizzes based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            quizzes_df = quizzes_df[(quizzes_df['club'].isin(user_club_names))
                                    | (quizzes_df['creator'] == user['name'])]

        # Show active quizzes only for students
        if user['role'] not in ['선생님', '회장', '부회장']:
            quizzes_df = quizzes_df[quizzes_df['status'] == '활성']

        for _, quiz in quizzes_df.iterrows():
            self.show_quiz_card(quiz, user)

    def show_quiz_card(self, quiz, user):
        """Display a single quiz card"""
        # Get user's attempts
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_attempts = responses_df[
            (responses_df['quiz_id'] == quiz['id'])
            & (responses_df['username'] == user['username'])]

        attempts_count = len(user_attempts)
        max_attempts = int(quiz['attempts_allowed']) if pd.notna(
            quiz['attempts_allowed']) else 999
        best_score = user_attempts['score'].max(
        ) if not user_attempts.empty else 0

        # Status styling
        if quiz['status'] == '활성':
            status_color = "#28a745"
        elif quiz['status'] == '비활성':
            status_color = "#6c757d"
        else:
            status_color = "#dc3545"

        with st.container():
            st.markdown(f"""
            <div class="club-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #333;">{quiz['title']}</h4>
                        <div style="margin: 10px 0;">
                            <span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                                {quiz['status']}
                            </span>
                        </div>
                    </div>
                </div>

                <p style="color: #666; line-height: 1.6; margin: 15px 0;">{quiz['description']}</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div><strong>🏷️ 동아리:</strong> {quiz['club']}</div>
                        <div><strong>👤 출제자:</strong> {quiz['creator']}</div>
                        <div><strong>⏱️ 제한시간:</strong> {quiz['time_limit']}분</div>
                        <div><strong>🔄 시도 횟수:</strong> {attempts_count}/{max_attempts}</div>
                    </div>
                    {f'<div style="margin-top: 10px;"><strong>🏆 최고 점수:</strong> {best_score}점</div>' if best_score > 0 else ''}
                </div>
            </div>
            """,
                        unsafe_allow_html=True)

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if quiz['status'] == '활성' and attempts_count < max_attempts:
                    if st.button("🚀 시작", key=f"start_quiz_{quiz['id']}"):
                        st.session_state[f'taking_quiz_{quiz["id"]}'] = True
                        st.session_state[
                            f'quiz_start_time_{quiz["id"]}'] = datetime.now()
                        st.rerun()
                elif attempts_count >= max_attempts:
                    st.error("시도 횟수 초과")
                else:
                    st.info("비활성 상태")

            with col2:
                if not user_attempts.empty:
                    if st.button("📊 결과", key=f"results_{quiz['id']}"):
                        st.session_state[f'show_results_{quiz["id"]}'] = True

            with col3:
                if user['role'] in ['선생님', '회장'
                                    ] or user['name'] == quiz['creator']:
                    if st.button("⚙️ 관리", key=f"manage_quiz_{quiz['id']}"):
                        st.session_state[f'manage_quiz_{quiz["id"]}'] = True

            with col4:
                if st.button("ℹ️ 정보", key=f"info_{quiz['id']}"):
                    self.show_quiz_info(quiz)

            # Show quiz taking interface if requested
            if st.session_state.get(f'taking_quiz_{quiz["id"]}', False):
                self.show_quiz_taking_interface(quiz, user)

            # Show results if requested
            if st.session_state.get(f'show_results_{quiz["id"]}', False):
                self.show_quiz_results(quiz, user)

    def show_quiz_creation(self, user):
        """Display quiz creation form"""
        st.markdown("#### ➕ 새 퀴즈 생성")

        with st.form("create_quiz_form"):
            # Get user's clubs for club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist(
                ) if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(
                    user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택",
                                         club_options,
                                         key="quiz_club_select_unique")
            title = st.text_input("📝 퀴즈 제목",
                                  placeholder="퀴즈 제목을 입력하세요",
                                  key="quiz_title_input")
            description = st.text_area("📄 퀴즈 설명",
                                       placeholder="퀴즈에 대한 설명을 입력하세요",
                                       height=100,
                                       key="quiz_desc_input")

            col1, col2 = st.columns(2)
            with col1:
                time_limit = st.number_input("⏱️ 제한시간 (분)",
                                             min_value=1,
                                             max_value=60,
                                             value=10,
                                             key="quiz_time_limit")
            with col2:
                attempts_allowed = st.number_input("🔄 허용 시도 횟수",
                                                   min_value=1,
                                                   max_value=10,
                                                   value=3,
                                                   key="quiz_attempts")

            st.markdown("##### 📝 문제 등록")

            # Initialize questions in session state
            if 'quiz_questions' not in st.session_state:
                st.session_state.quiz_questions = []

            # Question input
            question_text = st.text_input("❓ 문제",
                                          placeholder="문제를 입력하세요",
                                          key="quiz_question_input")

            col1, col2 = st.columns(2)
            with col1:
                option1 = st.text_input("선택지 1", key="quiz_option1")
                option2 = st.text_input("선택지 2", key="quiz_option2")
            with col2:
                option3 = st.text_input("선택지 3", key="quiz_option3")
                option4 = st.text_input("선택지 4", key="quiz_option4")

            correct_answer = st.selectbox("정답",
                                          ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
                                          key="quiz_correct_answer")

            if st.form_submit_button("➕ 문제 추가"):
                if question_text and option1 and option2:
                    question = {
                        'question': question_text,
                        'options':
                        [option1, option2, option3 or "", option4 or ""],
                        'correct': correct_answer
                    }
                    st.session_state.quiz_questions.append(question)
                    st.success(
                        f"문제가 추가되었습니다! (총 {len(st.session_state.quiz_questions)}문제)"
                    )

            # Show added questions
            if st.session_state.quiz_questions:
                st.markdown("##### 등록된 문제 목록")
                for i, q in enumerate(st.session_state.quiz_questions):
                    with st.expander(f"문제 {i+1}: {q['question'][:50]}..."):
                        st.write(f"**문제:** {q['question']}")
                        for j, opt in enumerate(q['options']):
                            if opt:
                                marker = "✅" if f"선택지 {j+1}" == q[
                                    'correct'] else "⭕"
                                st.write(f"{marker} 선택지 {j+1}: {opt}")

                        if st.button(f"🗑️ 삭제", key=f"del_q_{i}"):
                            st.session_state.quiz_questions.pop(i)
                            st.rerun()

            status = st.selectbox("📊 상태", ["활성", "비활성"],
                                  key="quiz_status_select")

            # 저장 옵션
            auto_notify = st.checkbox("📧 자동 알림 발송", value=True)
            backup_data = st.checkbox("💽 백업 생성", value=False)

            col1, col2, col3 = st.columns(3)
            with col1:
                submit_button = st.form_submit_button("📤 퀴즈 생성",
                                                      use_container_width=True)

            if submit_button:
                if title and description and selected_club and st.session_state.quiz_questions:
                    quiz_data = {
                        'title':
                        title,
                        'description':
                        description,
                        'club':
                        selected_club,
                        'creator':
                        user['name'],
                        'questions':
                        json.dumps(st.session_state.quiz_questions,
                                   ensure_ascii=False),
                        'time_limit':
                        time_limit,
                        'attempts_allowed':
                        attempts_allowed,
                        'status':
                        status,
                        'created_date':
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record(
                            'quizzes', quiz_data):
                        st.success("퀴즈가 생성되었습니다!")
                        st.session_state.quiz_questions = []  # Clear questions
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 퀴즈: {title}", "info", "all",
                            f"{user['name']}님이 새 퀴즈를 등록했습니다.")
                        st.rerun()
                    else:
                        st.error("퀴즈 생성에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력하고 최소 1개 이상의 문제를 등록해주세요.")

    def show_quiz_taking_interface(self, quiz, user):
        """Display quiz taking interface"""
        st.markdown("---")
        st.markdown(f"#### 🚀 퀴즈 진행: {quiz['title']}")

        # Parse questions
        try:
            questions = json.loads(quiz['questions'])
        except:
            st.error("퀴즈 데이터에 오류가 있습니다.")
            return

        # Time tracking
        start_time = st.session_state.get(f'quiz_start_time_{quiz["id"]}')
        if start_time:
            elapsed_time = (datetime.now() - start_time).total_seconds() / 60
            remaining_time = int(quiz['time_limit']) - elapsed_time

            if remaining_time <= 0:
                st.error("⏰ 시간이 초과되었습니다!")
                st.session_state[f'taking_quiz_{quiz["id"]}'] = False
                st.rerun()
                return

            st.markdown(f"⏰ **남은 시간: {remaining_time:.1f}분**")

        # Quiz form
        with st.form(f"quiz_form_{quiz['id']}"):
            answers = []

            for i, question in enumerate(questions):
                st.markdown(f"**문제 {i+1}:** {question['question']}")

                # Filter out empty options
                options = [opt for opt in question['options'] if opt.strip()]

                answer = st.radio(f"선택하세요 (문제 {i+1})",
                                  options,
                                  key=f"q_{quiz['id']}_{i}",
                                  label_visibility="collapsed")
                answers.append(answer)
                st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("📤 제출",
                                                      use_container_width=True)
            with col2:
                cancel_quiz = st.form_submit_button("❌ 취소",
                                                    use_container_width=True)

            if submit_button:
                # Calculate score
                score = 0
                for i, question in enumerate(questions):
                    if answers[i] == question['correct']:
                        score += 1

                # Calculate time taken
                time_taken = (datetime.now() - start_time).total_seconds() / 60

                # Save response
                response_data = {
                    'quiz_id': quiz['id'],
                    'username': user['username'],
                    'answers': json.dumps(answers, ensure_ascii=False),
                    'score': score,
                    'total_questions': len(questions),
                    'completed_date':
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time_taken': round(time_taken, 2)
                }

                if st.session_state.data_manager.add_record(
                        'quiz_responses', response_data):
                    st.success(f"퀴즈가 완료되었습니다! 점수: {score}/{len(questions)}점")
                    st.session_state[f'taking_quiz_{quiz["id"]}'] = False

                    # Award badge for perfect score
                    if score == len(questions):
                        badge_data = {
                            'username':
                            user['username'],
                            'badge_name':
                            '퀴즈 마스터',
                            'badge_icon':
                            '🏆',
                            'description':
                            f"{quiz['title']} 만점 달성",
                            'awarded_date':
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'awarded_by':
                            'System'
                        }
                        st.session_state.data_manager.add_record(
                            'badges', badge_data)

                    st.rerun()
                else:
                    st.error("퀴즈 제출에 실패했습니다.")

            if cancel_quiz:
                st.session_state[f'taking_quiz_{quiz["id"]}'] = False
                st.rerun()

    def show_quiz_analytics(self, user):
        """Display quiz analytics for teachers"""
        st.markdown("#### 📊 퀴즈 결과 분석")

        quizzes_df = st.session_state.data_manager.load_csv('quizzes')
        responses_df = st.session_state.data_manager.load_csv('quiz_responses')

        if quizzes_df.empty:
            st.info("분석할 퀴즈가 없습니다.")
            return

        # Filter quizzes based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(
                user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            quizzes_df = quizzes_df[(quizzes_df['club'].isin(user_club_names))
                                    | (quizzes_df['creator'] == user['name'])]

        # Select quiz for analysis
        quiz_options = {
            f"{row['title']} ({row['club']})": row['id']
            for _, row in quizzes_df.iterrows()
        }

        if not quiz_options:
            st.info("분석할 수 있는 퀴즈가 없습니다.")
            return

        selected_quiz = st.selectbox("📊 분석할 퀴즈 선택",
                                     options=list(quiz_options.keys()))

        if selected_quiz:
            quiz_id = quiz_options[selected_quiz]
            quiz_responses = responses_df[responses_df['quiz_id'] == quiz_id]

            if quiz_responses.empty:
                st.info("이 퀴즈에 대한 응답이 없습니다.")
                return

            # Basic statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("총 응답 수", len(quiz_responses))

            with col2:
                unique_users = quiz_responses['username'].nunique()
                st.metric("참여 학생 수", unique_users)

            with col3:
                avg_score = quiz_responses['score'].mean()
                avg_total = quiz_responses['total_questions'].mean()
                st.metric("평균 점수", f"{avg_score:.1f}/{avg_total:.0f}")

            with col4:
                avg_time = quiz_responses['time_taken'].mean()
                st.metric("평균 소요 시간", f"{avg_time:.1f}분")

            # Score distribution
            st.markdown("##### 📊 점수 분포")
            score_counts = quiz_responses['score'].value_counts().sort_index()

            score_data = []
            for score in range(
                    int(quiz_responses['total_questions'].iloc[0]) + 1):
                count = score_counts.get(score, 0)
                score_data.append({'점수': score, '학생 수': count})

            score_df = pd.DataFrame(score_data)
            st.bar_chart(score_df.set_index('점수'))

            # Individual results
            st.markdown("##### 👥 개별 결과")

            display_columns = [
                'username', 'score', 'total_questions', 'completed_date',
                'time_taken'
            ]
            display_df = quiz_responses[display_columns].copy()
            display_df.columns = ['학생명', '점수', '총 문제수', '완료일', '소요시간(분)']
            display_df = display_df.sort_values('점수', ascending=False)

            st.dataframe(display_df, use_container_width=True)

    def show_my_scores(self, user):
        """Display user's quiz scores"""
        st.markdown("#### 📈 내 퀴즈 점수")

        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_responses = responses_df[responses_df['username'] ==
                                      user['username']]

        if user_responses.empty:
            st.info("참여한 퀴즈가 없습니다.")
            return

        # Get quiz details
        quizzes_df = st.session_state.data_manager.load_csv('quizzes')

        # Calculate overall statistics
        total_quizzes = user_responses['quiz_id'].nunique()
        total_attempts = len(user_responses)
        avg_score = (user_responses['score'] /
                     user_responses['total_questions']).mean() * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("참여 퀴즈 수", total_quizzes)
        with col2:
            st.metric("총 시도 횟수", total_attempts)
        with col3:
            st.metric("평균 점수", f"{avg_score:.1f}%")

        st.markdown("##### 📋 퀴즈별 성과")

        for quiz_id in user_responses['quiz_id'].unique():
            quiz_attempts = user_responses[user_responses['quiz_id'] ==
                                           quiz_id]
            quiz_info = quizzes_df[quizzes_df['id'] == quiz_id]

            if not quiz_info.empty:
                quiz = quiz_info.iloc[0]
                best_score = quiz_attempts['score'].max()
                attempts_count = len(quiz_attempts)
                best_time = quiz_attempts.loc[quiz_attempts['score'].idxmax(),
                                              'time_taken']

                st.markdown(f"""
                <div class="club-card">
                    <h4>{quiz['title']}</h4>
                    <div style="margin: 15px 0;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; text-align: center;">
                            <div>
                                <h3 style="color: #FF6B6B; margin: 0;">{best_score}/{quiz_attempts.iloc[0]['total_questions']}</h3>
                                <small>최고 점수</small>
                            </div>
                            <div>
                                <h3 style="color: #4ECDC4; margin: 0;">{attempts_count}</h3>
                                <small>시도 횟수</small>
                            </div>
                            <div>
                                <h3 style="color: #28a745; margin: 0;">{best_time:.1f}분</h3>
                                <small>최단 시간</small>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    def show_quiz_results(self, quiz, user):
        """Show detailed quiz results"""
        st.markdown("---")
        st.markdown(f"#### 📊 {quiz['title']} 결과")

        responses_df = st.session_state.data_manager.load_csv('quiz_responses')
        user_responses = responses_df[
            (responses_df['quiz_id'] == quiz['id'])
            & (responses_df['username'] == user['username'])]

        if user_responses.empty:
            st.info("이 퀴즈에 대한 결과가 없습니다.")
            return

        # Show all attempts
        for _, response in user_responses.iterrows():
            score_percentage = (response['score'] /
                                response['total_questions']) * 100

            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <h5>점수: {response['score']}/{response['total_questions']} ({score_percentage:.1f}%)</h5>
                        <p>완료일: {response['completed_date']}</p>
                        <p>소요 시간: {response['time_taken']}분</p>
                    </div>
                    <div style="text-align: right;">
                        {'🏆' if score_percentage == 100 else '🎯' if score_percentage >= 80 else '📚'}
                    </div>
                </div>
            </div>
            """,
                        unsafe_allow_html=True)

        if st.button("❌ 결과 닫기", key=f"close_results_{quiz['id']}"):
            st.session_state[f'show_results_{quiz["id"]}'] = False
            st.rerun()

    def show_quiz_info(self, quiz):
        """Show detailed quiz information"""
        st.info(f"""
        **퀴즈 정보**
        - 제목: {quiz['title']}
        - 설명: {quiz['description']}
        - 동아리: {quiz['club']}
        - 출제자: {quiz['creator']}
        - 제한시간: {quiz['time_limit']}분
        - 허용 시도: {quiz['attempts_allowed']}회
        - 상태: {quiz['status']}
        - 생성일: {quiz['created_date']}
        """)