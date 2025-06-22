import streamlit as st
import pandas as pd
from datetime import datetime, date
import zipfile
import io
import os

class AdminSystem:
    def __init__(self):
        pass

    def show_admin_interface(self, user):
        """Display the admin interface"""
        if user['role'] != '선생님':
            st.error("⛔ 관리자 권한이 필요합니다.")
            return

        st.markdown("### ⚙️ 관리자 도구")

        tabs = st.tabs([
            "👥 사용자 관리", "🏷️ 동아리 관리", "📊 시스템 현황", 
            "💾 데이터 관리", "🔧 시스템 설정", "📈 통계 대시보드"
        ])

        with tabs[0]:
            self.show_user_management()

        with tabs[1]:
            self.show_club_management()

        with tabs[2]:
            self.show_system_status()

        with tabs[3]:
            self.show_data_management()

        with tabs[4]:
            self.show_system_settings()

        with tabs[5]:
            self.show_admin_dashboard()

    def show_user_management(self):
        """Display user management interface"""
        st.markdown("#### 👥 사용자 관리")

        # User management tabs
        sub_tabs = st.tabs(["📋 사용자 목록", "➕ 사용자 추가", "📤 일괄 추가", "🎥 화상회의 관리"])

        with sub_tabs[0]:
            self.show_user_list()

        with sub_tabs[1]:
            self.show_add_user_form()

        with sub_tabs[2]:
            self.show_bulk_user_add()

        with sub_tabs[3]:
            self.show_video_conference_management()

    def show_user_list(self):
        """Display user list with management options"""
        st.markdown("##### 📋 등록된 사용자")

        users_df = st.session_state.data_manager.load_csv('users')

        if users_df.empty:
            st.info("등록된 사용자가 없습니다.")
            return

        # Search and filter
        col1, col2 = st.columns(2)

        with col1:
            search_term = st.text_input("🔍 사용자 검색", placeholder="이름 또는 사용자명 검색...")

        with col2:
            role_filter = st.selectbox("🏷️ 역할 필터", ["전체"] + users_df['role'].unique().tolist())

        # Apply filters
        filtered_users = users_df.copy()

        if search_term:
            filtered_users = filtered_users[
                filtered_users['name'].str.contains(search_term, case=False, na=False) |
                filtered_users['username'].str.contains(search_term, case=False, na=False)
            ]

        if role_filter != "전체":
            filtered_users = filtered_users[filtered_users['role'] == role_filter]

        # Display users with edit capabilities
        st.markdown(f"**총 {len(filtered_users)}명의 사용자**")

        for _, user in filtered_users.iterrows():
            with st.expander(f"👤 {user['name']} ({user['username']}) - {user['role']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**이름:** {user['name']}")
                    st.write(f"**사용자명:** {user['username']}")
                    st.write(f"**역할:** {user['role']}")
                    st.write(f"**동아리:** {user['club_name']}")

                with col2:
                    st.write(f"**동아리 내 역할:** {user['club_role']}")
                    st.write(f"**생성일:** {user['created_date']}")

                # Edit form
                with st.form(f"edit_user_{user['username']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input("이름", value=user['name'])
                        new_password = st.text_input("비밀번호", value=user['password'])

                        roles = ['선생님', '회장', '부회장', '총무', '기록부장', '디자인담당', '동아리원']
                        new_role = st.selectbox("역할", roles, index=roles.index(user['role']) if user['role'] in roles else 0)

                    with col2:
                        clubs_df = st.session_state.data_manager.load_csv('clubs')
                        club_options = clubs_df['name'].tolist() if not clubs_df.empty else []

                        try:
                            club_index = club_options.index(user['club_name']) if user['club_name'] in club_options else 0
                        except:
                            club_index = 0

                        new_club = st.selectbox("동아리", club_options, index=club_index)

                        club_roles = ['회장', '부회장', '총무', '기록부장', '디자인담당', '동아리원', '선생님']
                        new_club_role = st.selectbox("동아리 내 역할", club_roles, 
                                                   index=club_roles.index(user['club_role']) if user['club_role'] in club_roles else 0)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.form_submit_button("💾 수정", use_container_width=True):
                            updates = {
                                'name': new_name,
                                'password': new_password,
                                'role': new_role,
                                'club_name': new_club,
                                'club_role': new_club_role
                            }

                            success, message = st.session_state.auth_manager.update_user(user['username'], updates)
                            if success:
                                st.success("사용자 정보가 수정되었습니다!")
                                st.rerun()
                            else:
                                st.error(f"수정 실패: {message}")

                    with col2:
                        if st.form_submit_button("🗑️ 삭제", use_container_width=True):
                            success, message = st.session_state.auth_manager.delete_user(user['username'])
                            if success:
                                st.success("사용자가 삭제되었습니다!")
                                st.rerun()
                            else:
                                st.error(f"삭제 실패: {message}")

                    with col3:
                        if st.form_submit_button("🔄 비밀번호 초기화", use_container_width=True):
                            reset_updates = {'password': '1234'}
                            success, message = st.session_state.auth_manager.update_user(user['username'], reset_updates)
                            if success:
                                st.success("비밀번호가 '1234'로 초기화되었습니다!")
                            else:
                                st.error(f"초기화 실패: {message}")

    def show_add_user_form(self):
        """Display add user form"""
        st.markdown("##### ➕ 새 사용자 추가")

        with st.form("add_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input("사용자명", placeholder="영문, 숫자 조합")
                password = st.text_input("비밀번호", value="1234")
                name = st.text_input("이름", placeholder="실명 입력")

            with col2:
                roles = ['선생님', '회장', '부회장', '총무', '기록부장', '디자인담당', '동아리원']
                role = st.selectbox("역할", roles)

                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = clubs_df['name'].tolist() if not clubs_df.empty else []
                club_name = st.selectbox("동아리", club_options)

                club_roles = ['회장', '부회장', '총무', '기록부장', '디자인담당', '동아리원', '선생님']
                club_role = st.selectbox("동아리 내 역할", club_roles)

            add_user = st.form_submit_button("👤 사용자 추가", use_container_width=True)

            if add_user:
                if username and name and club_name:
                    success, message = st.session_state.auth_manager.create_user(
                        username, password, name, role, club_name, club_role
                    )

                    if success:
                        st.success("사용자가 성공적으로 추가되었습니다!")

                        # Add welcome notification
                        st.session_state.notification_system.add_notification(
                            "환영합니다!",
                            "info",
                            username,
                            f"{name}님, 폴라리스반 동아리 시스템에 오신 것을 환영합니다!"
                        )
                    else:
                        st.error(f"사용자 추가 실패: {message}")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")

    def show_bulk_user_add(self):
        """Display bulk user addition interface"""
        st.markdown("##### 📤 여러 사용자 일괄 추가")

        st.info("CSV 파일을 업로드하여 여러 사용자를 한번에 추가할 수 있습니다.")

        # Template download
        if st.button("📄 템플릿 다운로드"):
            template_data = {
                'username': ['example1', 'example2'],
                'password': ['1234', '1234'],
                'name': ['홍길동', '김철수'],
                'role': ['동아리원', '동아리원'],
                'club_name': ['코딩', '댄스'],
                'club_role': ['동아리원', '동아리원']
            }

            template_df = pd.DataFrame(template_data)
            csv_data = template_df.to_csv(index=False, encoding='utf-8-sig')

            st.download_button(
                label="💾 템플릿 CSV 다운로드",
                data=csv_data,
                file_name="user_template.csv",
                mime="text/csv"
            )

        # File upload
        uploaded_file = st.file_uploader("📤 사용자 CSV 파일 업로드", type=['csv'])

        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

                # Validate columns
                required_columns = ['username', 'password', 'name', 'role', 'club_name', 'club_role']
                missing_columns = [col for col in required_columns if col not in df.columns]

                if missing_columns:
                    st.error(f"필수 컬럼이 누락되었습니다: {missing_columns}")
                    return

                # Preview data
                st.markdown("**업로드된 데이터 미리보기:**")
                st.dataframe(df, use_container_width=True)

                # Process upload
                if st.button("👥 사용자 일괄 추가", use_container_width=True):
                    success_count = 0
                    error_count = 0
                    errors = []

                    for _, row in df.iterrows():
                        success, message = st.session_state.auth_manager.create_user(
                            row['username'], row['password'], row['name'], 
                            row['role'], row['club_name'], row['club_role']
                        )

                        if success:
                            success_count += 1
                            # Add welcome notification
                            st.session_state.notification_system.add_notification(
                                "환영합니다!",
                                "info",
                                row['username'],
                                f"{row['name']}님, 폴라리스반 동아리 시스템에 오신 것을 환영합니다!"
                            )
                        else:
                            error_count += 1
                            errors.append(f"{row['username']}: {message}")

                    st.success(f"✅ {success_count}명의 사용자가 성공적으로 추가되었습니다!")

                    if error_count > 0:
                        st.warning(f"⚠️ {error_count}명의 사용자 추가에 실패했습니다:")
                        for error in errors:
                            st.write(f"- {error}")

                    if success_count > 0:
                        st.rerun()

            except Exception as e:
                st.error(f"파일 처리 중 오류가 발생했습니다: {e}")

    def show_video_conference_management(self):
        """Display video conference management"""
        st.markdown("##### 🎥 화상회의 관리")

        clubs_df = st.session_state.data_manager.load_csv('clubs')

        if clubs_df.empty:
            st.info("등록된 동아리가 없습니다.")
            return

        st.markdown("**동아리별 화상회의 링크 설정**")

        for _, club in clubs_df.iterrows():
            with st.expander(f"{club['icon']} {club['name']}"):
                current_link = club.get('meet_link', '')

                with st.form(f"meet_link_{club['name']}"):
                    new_link = st.text_input(
                        "화상회의 링크",
                        value=current_link,
                        placeholder="https://meet.google.com/xxx-xxxx-xxx 또는 Zoom 링크"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.form_submit_button("💾 저장"):
                            # Update club data
                            clubs_df.loc[clubs_df['name'] == club['name'], 'meet_link'] = new_link

                            if st.session_state.data_manager.save_csv('clubs', clubs_df):
                                st.success("화상회의 링크가 저장되었습니다!")
                                st.rerun()
                            else:
                                st.error("저장에 실패했습니다.")

                    with col2:
                        if new_link and st.form_submit_button("🔗 링크 테스트"):
                            st.markdown(f'<a href="{new_link}" target="_blank">🎥 화상회의 참여</a>', unsafe_allow_html=True)

    def show_club_management(self):
        """Display club management interface"""
        st.markdown("#### 🏷️ 동아리 관리")

        # Club management tabs
        sub_tabs = st.tabs(["📋 동아리 목록", "➕ 동아리 추가"])

        with sub_tabs[0]:
            self.show_club_list()

        with sub_tabs[1]:
            self.show_add_club_form()

    def show_club_list(self):
        """Display club list with management options"""
        st.markdown("##### 📋 등록된 동아리")

        clubs_df = st.session_state.data_manager.load_csv('clubs')

        if clubs_df.empty:
            st.info("등록된 동아리가 없습니다.")
            return

        for _, club in clubs_df.iterrows():
            # Get member count
            users_df = st.session_state.data_manager.load_csv('users')
            member_count = len(users_df[users_df['club_name'] == club['name']]) if not users_df.empty else 0

            with st.expander(f"{club['icon']} {club['name']} ({member_count}/{club['max_members']}명)"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**설명:** {club['description']}")
                    st.write(f"**회장:** {club['president']}")
                    st.write(f"**생성일:** {club['created_date']}")

                with col2:
                    st.write(f"**최대 인원:** {club['max_members']}명")
                    st.write(f"**현재 인원:** {member_count}명")
                    if pd.notna(club.get('meet_link')) and club['meet_link']:
                        st.markdown(f'🎥 <a href="{club["meet_link"]}" target="_blank">화상회의 참여</a>', unsafe_allow_html=True)

                # Edit form
                with st.form(f"edit_club_{club['name']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_icon = st.text_input("아이콘", value=club['icon'])
                        new_description = st.text_area("설명", value=club['description'])
                        new_president = st.text_input("회장", value=club['president'])

                    with col2:
                        new_max_members = st.number_input("최대 인원", min_value=1, max_value=100, value=int(club['max_members']))
                        new_meet_link = st.text_input("화상회의 링크", value=club.get('meet_link', ''))

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.form_submit_button("💾 수정", use_container_width=True):
                            # Update club data
                            club_index = clubs_df[clubs_df['name'] == club['name']].index[0]

                            clubs_df.loc[club_index, 'icon'] = new_icon
                            clubs_df.loc[club_index, 'description'] = new_description
                            clubs_df.loc[club_index, 'president'] = new_president
                            clubs_df.loc[club_index, 'max_members'] = new_max_members
                            clubs_df.loc[club_index, 'meet_link'] = new_meet_link

                            if st.session_state.data_manager.save_csv('clubs', clubs_df):
                                st.success("동아리 정보가 수정되었습니다!")
                                st.rerun()
                            else:
                                st.error("수정에 실패했습니다.")

                    with col2:
                        if st.form_submit_button("🗑️ 삭제", use_container_width=True):
                            # Check if club has members
                            if member_count > 0:
                                st.error("동아리에 회원이 있어 삭제할 수 없습니다. 먼저 회원을 다른 동아리로 이동시켜주세요.")
                            else:
                                # Delete club
                                clubs_df = clubs_df[clubs_df['name'] != club['name']]

                                if st.session_state.data_manager.save_csv('clubs', clubs_df):
                                    st.success("동아리가 삭제되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("삭제에 실패했습니다.")

    def show_add_club_form(self):
        """Display add club form"""
        st.markdown("##### ➕ 새 동아리 추가")

        with st.form("add_club_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("동아리명", placeholder="동아리 이름 입력")
                icon = st.text_input("아이콘", placeholder="🎨 (이모지 입력)")
                description = st.text_area("설명", placeholder="동아리에 대한 설명을 입력하세요")

            with col2:
                president = st.text_input("회장", placeholder="회장 이름 입력")
                max_members = st.number_input("최대 인원", min_value=1, max_value=100, value=20)
                meet_link = st.text_input("화상회의 링크", placeholder="https://meet.google.com/...")

            if st.form_submit_button("🏷️ 동아리 추가", use_container_width=True):
                if name and icon and description and president:
                    club_data = {
                        'name': name,
                        'icon': icon,
                        'description': description,
                        'president': president,
                        'max_members': max_members,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'meet_link': meet_link
                    }

                    if st.session_state.data_manager.add_record('clubs', club_data):
                        st.success("동아리가 성공적으로 추가되었습니다!")

                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 동아리 개설: {name}",
                            "info",
                            "all",
                            f"새로운 동아리 '{name}'이 개설되었습니다. 회장: {president}"
                        )
                        st.rerun()
                    else:
                        st.error("동아리 추가에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")

    def show_system_status(self):
        """Display system status"""
        st.markdown("#### 📊 시스템 현황")

        # Load all data
        users_df = st.session_state.data_manager.load_csv('users')
        clubs_df = st.session_state.data_manager.load_csv('clubs')
        posts_df = st.session_state.data_manager.load_csv('posts')
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        attendance_df = st.session_state.data_manager.load_csv('attendance')
        notifications_df = st.session_state.data_manager.load_csv('notifications')

        # System metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 사용자 수", len(users_df))

        with col2:
            st.metric("동아리 수", len(clubs_df))

        with col3:
            st.metric("총 게시글", len(posts_df))

        with col4:
            st.metric("총 과제", len(assignments_df))

        # Recent activity
        st.markdown("##### 📈 최근 활동")

        col1, col2 = st.columns(2)

        with col1:
            # Recent 7 days activity
            from datetime import timedelta
            week_ago = datetime.now() - timedelta(days=7)

            recent_posts = 0
            recent_assignments = 0

            if not posts_df.empty:
                posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
                recent_posts = len(posts_df[posts_df['created_date'] >= week_ago])

            if not assignments_df.empty:
                assignments_df['created_date'] = pd.to_datetime(assignments_df['created_date'])
                recent_assignments = len(assignments_df[assignments_df['created_date'] >= week_ago])

            st.metric("최근 7일 게시글", recent_posts)
            st.metric("최근 7일 과제", recent_assignments)

        with col2:
            # Attendance stats
            if not attendance_df.empty:
                today_attendance = len(attendance_df[attendance_df['date'] == date.today().strftime('%Y-%m-%d')])
                total_attendance = len(attendance_df)

                st.metric("오늘 출석 기록", today_attendance)
                st.metric("총 출석 기록", total_attendance)
            else:
                st.metric("오늘 출석 기록", 0)
                st.metric("총 출석 기록", 0)

        # System health
        st.markdown("##### 🔧 시스템 상태")

        # Check data integrity
        integrity_issues = []

        # Check for orphaned records
        if not users_df.empty and not clubs_df.empty:
            club_names = clubs_df['name'].tolist()
            orphaned_users = users_df[~users_df['club_name'].isin(club_names)]
            if not orphaned_users.empty:
                integrity_issues.append(f"소속 동아리가 없는 사용자: {len(orphaned_users)}명")

        if integrity_issues:
            st.warning("⚠️ 데이터 무결성 문제:")
            for issue in integrity_issues:
                st.write(f"- {issue}")
        else:
            st.success("✅ 시스템 상태 정상")

    def show_data_management(self):
        """Display data management interface"""
        st.markdown("#### 💾 데이터 관리")

        # Data management tabs
        sub_tabs = st.tabs(["📥 백업", "📤 복원", "📊 CSV 다운로드", "🔄 데이터 수정"])

        with sub_tabs[0]:
            self.show_backup_interface()

        with sub_tabs[1]:
            self.show_restore_interface()

        with sub_tabs[2]:
            self.show_csv_download()

        with sub_tabs[3]:
            self.show_data_editor()

    def show_backup_interface(self):
        """Display backup interface"""
        st.markdown("##### 📥 데이터 백업")

        st.info("시스템의 모든 데이터를 ZIP 파일로 백업할 수 있습니다.")

        if st.button("💾 전체 백업 생성", use_container_width=True):
            backup_file = self.create_system_backup()

            if backup_file:
                st.success("백업이 성공적으로 생성되었습니다!")

                st.download_button(
                    label="📥 백업 파일 다운로드",
                    data=backup_file,
                    file_name=f"polaris_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
            else:
                st.error("백업 생성에 실패했습니다.")

    def show_restore_interface(self):
        """Display restore interface"""
        st.markdown("##### 📤 데이터 복원")

        st.warning("⚠️ 복원 작업은 현재 데이터를 덮어씁니다. 신중하게 진행해주세요.")

        uploaded_backup = st.file_uploader("📤 백업 파일 업로드", type=['zip'])

        if uploaded_backup is not None:
            st.info("업로드된 백업 파일 정보:")
            st.write(f"파일명: {uploaded_backup.name}")
            st.write(f"파일 크기: {len(uploaded_backup.getvalue())} bytes")

            if st.button("🔄 데이터 복원 실행", use_container_width=True):
                if self.restore_system_backup(uploaded_backup):
                    st.success("데이터가 성공적으로 복원되었습니다!")
                    st.info("시스템을 새로고침해주세요.")
                else:
                    st.error("데이터 복원에 실패했습니다.")

    def show_csv_download(self):
        """Display CSV download interface"""
        st.markdown("##### 📊 CSV 파일 다운로드")

        # List all available CSV files
        csv_files = [
            ('users', '사용자 데이터'),
            ('clubs', '동아리 데이터'),
            ('posts', '게시글 데이터'),
            ('chat_logs', '채팅 로그'),
            ('assignments', '과제 데이터'),
            ('submissions', '제출물 데이터'),
            ('attendance', '출석 데이터'),
            ('schedule', '일정 데이터'),
            ('votes', '투표 데이터'),
            ('notifications', '알림 데이터'),
            ('badges', '배지 데이터')
        ]

        for file_key, file_name in csv_files:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"📄 {file_name}")

            with col2:
                df = st.session_state.data_manager.load_csv(file_key)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')

                st.download_button(
                    label="⬇️ 다운로드",
                    data=csv_data,
                    file_name=f"{file_key}.csv",
                    mime="text/csv",
                    key=f"download_{file_key}"
                )

    def show_data_editor(self):
        """Display data editor interface"""
        st.markdown("##### 🔄 데이터 수정")

        st.warning("⚠️ 직접 데이터를 수정할 때는 주의해주세요. 잘못된 수정은 시스템 오류를 일으킬 수 있습니다.")

        # Select data type to edit
        data_types = {
            'users': '사용자',
            'clubs': '동아리',
            'posts': '게시글',
            'assignments': '과제',
            'attendance': '출석',
            'schedule': '일정'
        }

        selected_type = st.selectbox("수정할 데이터 선택", list(data_types.keys()), format_func=lambda x: data_types[x])

        # Load and display data for editing
        df = st.session_state.data_manager.load_csv(selected_type)

        if df.empty:
            st.info(f"{data_types[selected_type]} 데이터가 없습니다.")
        else:
            st.markdown(f"**{data_types[selected_type]} 데이터 편집**")

            # Use Streamlit's data editor
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 변경사항 저장", use_container_width=True):
                    if st.session_state.data_manager.save_csv(selected_type, edited_df):
                        st.success("데이터가 성공적으로 저장되었습니다!")
                        st.rerun()
                    else:
                        st.error("데이터 저장에 실패했습니다.")

            with col2:
                if st.button("🔄 원본으로 되돌리기", use_container_width=True):
                    st.rerun()

    def show_system_settings(self):
        """Display system settings"""
        st.markdown("#### 🔧 시스템 설정")

        # System notification settings
        st.markdown("##### 🔔 시스템 알림 설정")

        with st.form("system_notifications"):
            send_system_notification = st.checkbox("시스템 알림 발송", value=True)

            col1, col2 = st.columns(2)

            with col1:
                notification_title = st.text_input("알림 제목", placeholder="시스템 공지사항")
                notification_type = st.selectbox("알림 유형", ["info", "success", "warning", "error", "announcement"])

            with col2:
                target_club = st.selectbox("대상 동아리", ["전체"] + self.get_club_list())
                notification_message = st.text_area("알림 내용", placeholder="모든 사용자에게 전달할 메시지를 입력하세요")

            if st.form_submit_button("📢 알림 발송", use_container_width=True):
                if notification_title and notification_message:
                    if target_club == "전체":
                        success = st.session_state.notification_system.send_system_notification(
                            notification_title, notification_message, notification_type
                        )
                    else:
                        success = st.session_state.notification_system.send_club_notification(
                            target_club, notification_title, notification_message, notification_type
                        )

                    if success:
                        st.success("시스템 알림이 발송되었습니다!")
                    else:
                        st.error("알림 발송에 실패했습니다.")
                else:
                    st.error("제목과 내용을 모두 입력해주세요.")

        # Automated system maintenance
        st.markdown("##### ⚙️ 자동 시스템 관리")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔔 과제 마감일 알림 확인", use_container_width=True):
                st.session_state.notification_system.check_assignment_deadlines()
                st.success("과제 마감일 알림을 확인했습니다!")

        with col2:
            if st.button("📅 일정 알림 확인", use_container_width=True):
                st.session_state.notification_system.check_schedule_reminders()
                st.success("일정 알림을 확인했습니다!")

    def show_admin_dashboard(self):
        """Display admin dashboard with statistics"""
        st.markdown("#### 📈 관리자 대시보드")

        # Load all data for analytics
        users_df = st.session_state.data_manager.load_csv('users')
        posts_df = st.session_state.data_manager.load_csv('posts')
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        attendance_df = st.session_state.data_manager.load_csv('attendance')

        # User activity analysis
        st.markdown("##### 👥 사용자 활동 분석")

        if not users_df.empty:
            # Role distribution
            role_counts = users_df['role'].value_counts()
            st.bar_chart(role_counts)

            # Club membership distribution
            club_counts = users_df['club_name'].value_counts()
            st.bar_chart(club_counts)

        # Content activity analysis
        st.markdown("##### 📊 콘텐츠 활동 분석")

        if not posts_df.empty:
            # Posts by club
            posts_by_club = posts_df['club'].value_counts()
            st.bar_chart(posts_by_club)

            # Posts over time
            posts_df['created_date'] = pd.to_datetime(posts_df['created_date'])
            posts_by_date = posts_df.groupby(posts_df['created_date'].dt.date).size()
            st.line_chart(posts_by_date)

        # Attendance analysis
        st.markdown("##### ✅ 출석 현황 분석")

        if not attendance_df.empty:
            # Attendance rate by club
            attendance_by_club = attendance_df.groupby(['club', 'status']).size().unstack(fill_value=0)

            if 'present' in attendance_by_club.columns:
                attendance_rates = attendance_by_club['출석'] / attendance_by_club.sum(axis=1) * 100
                st.bar_chart(attendance_rates)

        # System usage statistics
        st.markdown("##### 📈 시스템 사용 통계")

        usage_stats = {
            '총 사용자': len(users_df),
            '총 게시글': len(posts_df),
            '총 과제': len(assignments_df),
            '총 출석 기록': len(attendance_df)
        }

        for stat_name, stat_value in usage_stats.items():
            st.metric(stat_name, stat_value)

    def create_system_backup(self):
        """Create system backup ZIP file"""
        try:
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add all CSV files
                data_files = [
                    'users.csv', 'clubs.csv', 'posts.csv', 'chat_logs.csv',
                    'assignments.csv', 'submissions.csv', 'attendance.csv',
                    'schedule.csv', 'votes.csv', 'badges.csv', 'notifications.csv',
                    'quizzes.csv', 'quiz_responses.csv', 'vote_responses.csv'
                ]

                for filename in data_files:
                    file_path = f'data/{filename}'
                    if os.path.exists(file_path):
                        zip_file.write(file_path, filename)

            zip_buffer.seek(0)
            return zip_buffer.getvalue()

        except Exception as e:
            st.error(f"백업 생성 중 오류가 발생했습니다: {e}")
            return None

    def restore_system_backup(self, uploaded_file):
        """Restore system from backup ZIP file"""
        try:
            # Extract ZIP file
            with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
                # Create temporary directory for extraction
                temp_dir = 'temp_restore'
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                zip_file.extractall(temp_dir)

                # Move extracted files to data directory
                for filename in zip_file.namelist():
                    if filename.endswith('.csv'):
                        source_path = os.path.join(temp_dir, filename)
                        dest_path = os.path.join('data', filename)

                        if os.path.exists(source_path):
                            # Read and validate CSV
                            df = pd.read_csv(source_path, encoding='utf-8-sig')
                            df.to_csv(dest_path, index=False, encoding='utf-8-sig')

                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir)

            return True

        except Exception as e:
            st.error(f"복원 중 오류가 발생했습니다: {e}")
            return False

    def get_club_list(self):
        """Get list of all clubs"""
        try:
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            return clubs_df['name'].tolist() if not clubs_df.empty else []
        except:
            return []