import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import streamlit.components.v1 as components


class AssignmentSystem:
    def __init__(self):
        self.assignments_file = 'data/assignments.csv'
        self.submissions_file = 'data/submissions.csv'

    def show_assignment_interface(self, user):
        """Display the assignment interface"""
        st.markdown("### 📚 과제")

        if user['role'] in ['선생님', '회장', '부회장']:
            tabs = st.tabs(["📋 과제 목록", "➕ 과제 생성", "📊 제출 현황", "📝 채점"])
        else:
            tabs = st.tabs(["📋 과제 목록", "📤 내 제출물"])

        with tabs[0]:
            self.show_assignment_list(user)

        if user['role'] in ['선생님', '회장', '부회장']:
            with tabs[1]:
                self.show_assignment_creation(user)

            with tabs[2]:
                self.show_submission_status(user)

            with tabs[3]:
                self.show_grading_interface(user)
        else:
            with tabs[1]:
                self.show_my_submissions(user)

    def show_assignment_list(self, user):
        """Display list of assignments"""
        st.markdown("#### 📋 과제 목록")

        assignments_df = st.session_state.data_manager.load_csv('assignments')

        if assignments_df.empty:
            st.info("등록된 과제가 없습니다.")
            return

        # Filter assignments based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            assignments_df = assignments_df[
                (assignments_df['club'].isin(user_club_names)) |
                (assignments_df['creator'] == user['username'])
            ]

        # Sort by due date
        assignments_df['due_date'] = pd.to_datetime(assignments_df['due_date'])
        assignments_df = assignments_df.sort_values('due_date')

        for _, assignment in assignments_df.iterrows():
            self.show_assignment_card(assignment, user)

    def show_assignment_card(self, assignment, user):
        """Display a single assignment card"""
        # Calculate days until due
        due_date = pd.to_datetime(assignment['due_date'])
        days_left = (due_date.date() - date.today()).days

        # Status styling
        if days_left < 0:
            status_color = "#dc3545"
            status_text = f"마감됨 ({abs(days_left)}일 전)"
        elif days_left == 0:
            status_color = "#fd7e14"
            status_text = "오늘 마감"
        elif days_left <= 3:
            status_color = "#ffc107"
            status_text = f"마감 {days_left}일 전"
        else:
            status_color = "#28a745"
            status_text = f"마감 {days_left}일 전"

        # Check if user has submitted first
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        user_submission = submissions_df[
            (submissions_df['assignment_id'] == assignment['id']) &
            (submissions_df['username'] == user['username'])
        ]
        description_html = assignment['description']
        description_html = description_html.replace("\n", "<br>")


        with st.container():
            st.markdown("==========")
            st.markdown(f"""
            <div class="club-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #333;">{assignment['title']}</h4>
                        <div style="margin: 10px 0;">
                            <span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size:12px;">
                                {status_text} 
                            </span>
                            <span style="background-color: #6c757d; color: white; padding: 4px 12px; border-radius: 15px; font-size:12px;">
                                {assignment['status']}
                            </span>

            """, unsafe_allow_html=True)
            st.subheader(f"**📄 설명:** {description_html}")
            st.markdown(f"**🏷️ 동아리:** {assignment['club']}")
            st.markdown(f"**👤 출제자:** {assignment['creator']}")
            st.markdown(f"**📅 마감일:** {due_date.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**📊 상태:** {assignment['status']}")
            st.markdown("==========")



        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if not user_submission.empty:
                st.success("✅ 제출완료")
            else:
                if days_left >= 0:  # Not overdue
                    if st.button("📤 제출", key=f"submit_{assignment['id']}"):
                        if f'show_submission_{assignment["id"]}' not in st.session_state:
                            st.session_state[f'show_submission_{assignment["id"]}'] = True
                            st.rerun()
                else:
                    st.error("⏰ 마감됨")

        with col2:
            if not user_submission.empty:
                if st.button("📝 수정", key=f"edit_submission_{assignment['id']}"):
                    if f'edit_submission_{assignment["id"]}' not in st.session_state:
                        st.session_state[f'edit_submission_{assignment["id"]}'] = True
                        st.rerun()

        with col3:
            if user['role'] in ['선생님', '회장'] or user['username'] == assignment['creator']:
                if st.button("⚙️ 관리", key=f"manage_{assignment['id']}"):
                    if f'manage_assignment_{assignment["id"]}' not in st.session_state:
                        st.session_state[f'manage_assignment_{assignment["id"]}'] = True
                        st.rerun()

        with col4:
            if st.button("📊 현황", key=f"status_{assignment['id']}"):
                self.show_assignment_statistics(assignment['id'])

        # Show submission form if requested
        if st.session_state.get(f'show_submission_{assignment["id"]}', False):
            self.show_submission_form(assignment, user)

        # Show edit submission form if requested
        if st.session_state.get(f'edit_submission_{assignment["id"]}', False) and not user_submission.empty:
            self.show_edit_submission_form(assignment, user, user_submission.iloc[0])

    def show_assignment_creation(self, user):
        """Display assignment creation form"""
        st.markdown("#### ➕ 새 과제 생성")

        with st.form("create_assignment_form"):
            # Get user's clubs for club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="assignment_club_select_unique")
            title = st.text_input("📝 과제 제목", placeholder="과제 제목을 입력하세요", key="assignment_title_input")
            description = st.text_area("📄 과제 설명", placeholder="과제에 대한 자세한 설명을 입력하세요", height=150, key="assignment_desc_input")

            # Due date and time
            col1, col2 = st.columns(2)
            with col1:
                due_date = st.date_input("📅 마감일", min_value=date.today(), key="assignment_due_date_unique")
            with col2:
                due_time = st.time_input("⏰ 마감 시간", value=datetime.now().time(), key="assignment_due_time_unique")

            status = st.selectbox("📊 상태", ["활성", "비활성", "마감"])

            submit_button = st.form_submit_button("📤 과제 생성", use_container_width=True)

            if submit_button:
                if title and description and selected_club:
                    due_datetime = datetime.combine(due_date, due_time)

                    assignment_data = {
                        'title': title,
                        'description': description,
                        'club': selected_club,
                        'creator': user['name'],
                        'due_date': due_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': status,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('assignments', assignment_data):
                        st.success("과제가 생성되었습니다!")
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 과제: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 과제를 등록했습니다. 마감일: {due_date}"
                        )
                        st.rerun()
                    else:
                        st.error("과제 생성에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")

    def show_submission_form(self, assignment, user):
        """Display submission form"""
        st.markdown("---")
        st.markdown(f"#### 📤 과제 제출: {assignment['title']}")

        with st.form(f"submission_form_{assignment['id']}"):
            content = st.text_area("📝 제출 내용", placeholder="과제 답안이나 설명을 입력하세요", height=200)

            # File upload
            uploaded_file = st.file_uploader(
                "📎 파일 첨부", 
                type=['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'],
                help="과제 관련 파일을 첨부하세요"
            )

            col1, col2 = st.columns(2)
            with col1:
                submit_assignment = st.form_submit_button("📤 제출", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("❌ 취소", use_container_width=True)

            if submit_assignment:
                if content.strip():
                    # Process file if uploaded
                    file_path = None
                    if uploaded_file:
                        file_path = self.save_uploaded_file(uploaded_file, assignment['id'], user['username'])

                    submission_data = {
                        'assignment_id': assignment['id'],
                        'username': user['username'],
                        'content': content,
                        'file_path': file_path,
                        'submitted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'grade': None,
                        'feedback': None
                    }

                    if st.session_state.data_manager.add_record('submissions', submission_data):
                        st.success("과제가 성공적으로 제출되었습니다!")
                        st.session_state[f'show_submission_{assignment["id"]}'] = False
                        st.rerun()
                    else:
                        st.error("과제 제출에 실패했습니다.")
                else:
                    st.error("제출 내용을 입력해주세요.")

            if cancel_button:
                st.session_state[f'show_submission_{assignment["id"]}'] = False
                st.rerun()

    def save_uploaded_file(self, uploaded_file, assignment_id, username):
        """Save uploaded file and return file path"""
        try:
            # Create uploads directory if not exists
            uploads_dir = "uploads"
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)

            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{assignment_id}_{username}_{timestamp}_{uploaded_file.name}"
            file_path = os.path.join(uploads_dir, filename)

            # Save file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            return file_path
        except Exception as e:
            st.error(f"파일 저장 중 오류가 발생했습니다: {e}")
            return None

    def show_submission_status(self, user):
        """Display submission status for assignments"""
        st.markdown("#### 📊 제출 현황")

        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')

        if assignments_df.empty:
            st.info("등록된 과제가 없습니다.")
            return

        # Filter assignments based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            assignments_df = assignments_df[
                (assignments_df['club'].isin(user_club_names)) |
                (assignments_df['creator'] == user['username'])
            ]

        for _, assignment in assignments_df.iterrows():
            # Get submissions for this assignment
            assignment_submissions = submissions_df[submissions_df['assignment_id'] == assignment['id']]

            # Get total possible submitters (users in the club)
            if assignment['club'] == '전체':
                users_df = st.session_state.data_manager.load_csv('users')
                total_users = len(users_df)
            else:
                users_df = st.session_state.data_manager.load_csv('users')
                club_users = users_df[users_df['club_name'] == assignment['club']]
                total_users = len(club_users)

            submitted_count = len(assignment_submissions)
            submission_rate = (submitted_count / total_users * 100) if total_users > 0 else 0

            st.markdown(f"""
            <div class="club-card">
                <h4>{assignment['title']}</h4>
                <div style="margin: 15px 0;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; text-align: center;">
                        <div>
                            <h3 style="color: #FF6B6B; margin: 0;">{submitted_count}</h3>
                            <small>제출</small>
                        </div>
                        <div>
                            <h3 style="color: #FFA500; margin: 0;">{total_users - submitted_count}</h3>
                            <small>미제출</small>
                        </div>
                        <div>
                            <h3 style="color: #28a745; margin: 0;">{submission_rate:.1f}%</h3>
                            <small>제출률</small>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def show_grading_interface(self, user):
        """Display grading interface for teachers"""
        st.markdown("#### 📝 채점")

        assignments_df = st.session_state.data_manager.load_csv('assignments')
        submissions_df = st.session_state.data_manager.load_csv('submissions')

        if assignments_df.empty:
            st.info("채점할 과제가 없습니다.")
            return

        # Select assignment to grade
        assignment_options = {f"{row['title']} ({row['club']})": row['id'] for _, row in assignments_df.iterrows()}
        selected_assignment = st.selectbox("📝 채점할 과제 선택", options=list(assignment_options.keys()))

        if selected_assignment:
            assignment_id = assignment_options[selected_assignment]
            assignment_submissions = submissions_df[submissions_df['assignment_id'] == assignment_id]

            if assignment_submissions.empty:
                st.info("이 과제에 대한 제출물이 없습니다.")
                return

            st.markdown(f"**{selected_assignment} 제출물 목록**")

            for _, submission in assignment_submissions.iterrows():
                with st.expander(f"👤 {submission['username']} - {submission['submitted_date'][:16]}"):
                    st.write("**제출 내용:**")
                    st.write(submission['content'])

                    if pd.notna(submission['file_path']) and submission['file_path']:
                        st.write(f"**첨부 파일:** {submission['file_path']}")

                    # Grading form
                    with st.form(f"grade_form_{submission['id']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            grade = st.number_input(
                                "점수", 
                                min_value=0, 
                                max_value=100, 
                                value=int(submission['grade']) if pd.notna(submission['grade']) else 0
                            )

                        with col2:
                            feedback = st.text_area(
                                "피드백", 
                                value=submission['feedback'] if pd.notna(submission['feedback']) else "",
                                height=100
                            )

                        if st.form_submit_button("💾 채점 저장"):
                            updates = {'grade': grade, 'feedback': feedback}
                            if st.session_state.data_manager.update_record('submissions', submission['id'], updates):
                                st.success("채점이 저장되었습니다!")
                                st.rerun()
                            else:
                                st.error("채점 저장에 실패했습니다.")

    def show_my_submissions(self, user):
        """Display user's submissions"""
        st.markdown("#### 📤 내 제출물")

        submissions_df = st.session_state.data_manager.load_csv('submissions')
        user_submissions = submissions_df[submissions_df['username'] == user['username']]

        if user_submissions.empty:
            st.info("제출한 과제가 없습니다.")
            return

        # Get assignment details
        assignments_df = st.session_state.data_manager.load_csv('assignments')

        for _, submission in user_submissions.iterrows():
            assignment = assignments_df[assignments_df['id'] == submission['assignment_id']]

            if not assignment.empty:
                assignment_info = assignment.iloc[0]

                grade_display = f"{submission['grade']}점" if pd.notna(submission['grade']) else "채점 대기중"
                feedback_display = f"**피드백:** {submission['feedback']}" if pd.notna(submission['feedback']) else ""

                st.markdown(f"""
                <div class="club-card">
                    <h4>{assignment_info['title']}</h4>
                    <p><strong>제출일 :</strong> {submission['submitted_date']}</p>
                    <p><strong>내용 :</strong> {submission['content'][:100]}{'...' if len(submission['content']) > 100 else ''}</p>
                    <p><strong>점수 :</strong> {grade_display}</p>
                    <p><strong>피드백 :</strong> {feedback_display}</p>
                </div>
                """, unsafe_allow_html=True)

    def show_assignment_statistics(self, assignment_id):
        """Show statistics for a specific assignment"""
        submissions_df = st.session_state.data_manager.load_csv('submissions')
        assignment_submissions = submissions_df[submissions_df['assignment_id'] == assignment_id]

        if assignment_submissions.empty:
            st.info("제출물이 없습니다.")
            return

        # Calculate statistics
        total_submissions = len(assignment_submissions)
        graded_submissions = len(assignment_submissions[pd.notna(assignment_submissions['grade'])])

        if graded_submissions > 0:
            avg_grade = assignment_submissions['grade'].mean()
            st.write(f"**제출 수:** {total_submissions}")
            st.write(f"**채점 완료:** {graded_submissions}")
            st.write(f"**평균 점수:** {avg_grade:.1f}점")
        else:
            st.write(f"**제출 수:** {total_submissions}")
            st.write("**채점 완료:** 0")

    def show_edit_submission_form(self, assignment, user, submission):
        """Display form to edit existing submission"""
        st.markdown("---")
        st.markdown(f"#### 📝 제출물 수정: {assignment['title']}")

        with st.form(f"edit_submission_form_{submission['id']}"):
            content = st.text_area("📝 제출 내용", value=submission['content'], height=200)

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("💾 수정 저장", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("❌ 취소", use_container_width=True)

            if save_button:
                if content.strip():
                    updates = {
                        'content': content,
                        'submitted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.update_record('submissions', submission['id'], updates):
                        st.success("제출물이 수정되었습니다!")
                        st.session_state[f'edit_submission_{assignment["id"]}'] = False
                        st.rerun()
                    else:
                        st.error("제출물 수정에 실패했습니다.")
                else:
                    st.error("제출 내용을 입력해주세요.")

            if cancel_button:
                st.session_state[f'edit_submission_{assignment["id"]}'] = False
                st.rerun()