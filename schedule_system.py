import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

class ScheduleSystem:
    def __init__(self):
        self.schedule_file = 'data/schedule.csv'

    def show_schedule_interface(self, user):
        """Display the schedule interface"""
        st.markdown("### 📅 일정")

        if user['role'] in ['선생님', '회장', '부회장']:
            tabs = st.tabs(["📅 일정 보기", "➕ 일정 등록", "📋 일정 관리"])
        else:
            tabs = st.tabs(["📅 일정 보기", "📝 내 일정"])

        with tabs[0]:
            self.show_schedule_view(user)

        if user['role'] in ['선생님', '회장', '부회장']:
            with tabs[1]:
                self.show_schedule_creation(user)

            with tabs[2]:
                self.show_schedule_management(user)
        else:
            with tabs[1]:
                self.show_my_schedule(user)

    def show_schedule_view(self, user):
        """Display schedule view"""
        st.markdown("#### 📅 일정 보기")

        # View mode selection
        view_mode = st.selectbox("📊 보기 모드", ["이번 주", "이번 달", "전체"], key="schedule_view_mode_unique")

        # Club filter
        user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
        club_options = ["전체"] + user_clubs['club_name'].tolist()

        if user['role'] == '선생님':
            clubs_df = st.session_state.data_manager.load_csv('clubs')
            all_clubs = clubs_df['name'].tolist() if not clubs_df.empty else []
            club_options = ["전체"] + all_clubs

        selected_club = st.selectbox("🏷️ 동아리 필터", club_options, key="schedule_view_club_filter")

        # Load schedule data
        schedule_df = st.session_state.data_manager.load_csv('schedule')

        if schedule_df.empty:
            st.info("등록된 일정이 없습니다.")
            return

        # Filter by club
        if selected_club != "전체":
            schedule_df = schedule_df[
                (schedule_df['club'] == selected_club) | 
                (schedule_df['club'] == "전체")
            ]

        # Filter by user's clubs if not teacher
        if user['role'] != '선생님':
            user_club_names = user_clubs['club_name'].tolist() + ["전체"]
            schedule_df = schedule_df[
                schedule_df['club'].isin(user_club_names) |
                (schedule_df['creator'] == user['name'])
            ]

        # Filter by date range
        today = date.today()

        if view_mode == "이번 주":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif view_mode == "이번 달":
            start_date = today.replace(day=1)
            next_month = today.replace(month=today.month % 12 + 1, day=1) if today.month != 12 else today.replace(year=today.year + 1, month=1, day=1)
            end_date = next_month - timedelta(days=1)
        else:  # 전체
            start_date = date.min
            end_date = date.max

        if view_mode != "전체":
            schedule_df['date'] = pd.to_datetime(schedule_df['date']).dt.date
            schedule_df = schedule_df[
                (schedule_df['date'] >= start_date) & 
                (schedule_df['date'] <= end_date)
            ]

        # Sort by date and time
        schedule_df['datetime'] = pd.to_datetime(schedule_df['date'].astype(str) + ' ' + schedule_df['time'].astype(str))
        schedule_df = schedule_df.sort_values('datetime')

        # Display schedules
        if schedule_df.empty:
            st.info(f"{view_mode}에 일정이 없습니다.")
            return

        # Group by date
        for date_group, day_schedules in schedule_df.groupby(schedule_df['datetime'].dt.date):
            st.markdown(f"### 📅 {date_group.strftime('%Y년 %m월 %d일 (%A)')}")

            for _, schedule in day_schedules.iterrows():
                self.show_schedule_card(schedule, user)

    def show_schedule_card(self, schedule, user):
        """Display a single schedule card"""
        # Calculate time until event
        event_datetime = pd.to_datetime(f"{schedule['date']} {schedule['time']}")
        now = datetime.now()
        time_diff = event_datetime - now

        if time_diff.total_seconds() > 0:
            if time_diff.days > 0:
                time_status = f"{time_diff.days}일 후"
                status_color = "#28a745"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_status = f"{hours}시간 후"
                status_color = "#ffc107"
            else:
                minutes = time_diff.seconds // 60
                time_status = f"{minutes}분 후"
                status_color = "#fd7e14"
        else:
            time_status = "지난 일정"
            status_color = "#6c757d"

        with st.container():
            st.markdown(f"""
            <div class="club-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #333;">{schedule['title']}</h4>
                        <div style="margin: 10px 0;">
                            <span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                                {time_status}
                            </span>
                        </div>
                    </div>
                </div>

                <p style="color: #666; line-height: 1.6; margin: 15px 0;">{schedule['description']}</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div><strong>🏷️ 동아리:</strong> {schedule['club']}</div>
                        <div><strong>⏰ 시간:</strong> {schedule['time']}</div>
                        <div><strong>📍 장소:</strong> {schedule['location']}</div>
                        <div><strong>👤 작성자:</strong> {schedule['creator']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons for managers
            if user['role'] in ['선생님', '회장', '부회장'] or user['name'] == schedule['creator']:
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("✏️ 수정", key=f"edit_schedule_{schedule['id']}"):
                        st.session_state[f'edit_schedule_{schedule["id"]}'] = True

                with col2:
                    if st.button("🗑️ 삭제", key=f"delete_schedule_{schedule['id']}"):
                        if self.delete_schedule(schedule['id']):
                            st.success("일정이 삭제되었습니다.")
                            st.rerun()

                with col3:
                    if time_diff.total_seconds() > 0:
                        if st.button("🔔 알림", key=f"notify_schedule_{schedule['id']}"):
                            self.send_schedule_notification(schedule)

                # Show edit form if requested
                if st.session_state.get(f'edit_schedule_{schedule["id"]}', False):
                    self.show_edit_schedule_form(schedule, user)

    def show_schedule_creation(self, user):
        """Display schedule creation form"""
        st.markdown("#### ➕ 새 일정 등록")

        with st.form("create_schedule_form"):
            # Get user's clubs for club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="create_schedule_club_select")
            title = st.text_input("📝 일정 제목", placeholder="일정 제목을 입력하세요", key="schedule_title_input")
            description = st.text_area("📄 일정 설명", placeholder="일정에 대한 자세한 설명을 입력하세요", height=100, key="schedule_desc_input")

            col1, col2 = st.columns(2)
            with col1:
                event_date = st.date_input("📅 날짜", min_value=date.today(), key="schedule_event_date_unique")
            with col2:
                event_time = st.time_input("⏰ 시간", value=datetime.now().time(), key="schedule_event_time_unique")

            location = st.text_input("📍 장소", placeholder="장소를 입력하세요", key="schedule_location_input")

            # Recurring options
            is_recurring = st.checkbox("🔄 반복 일정", key="schedule_is_recurring_unique")
            recurring_type = None
            recurring_count = 1

            if is_recurring:
                col1, col2 = st.columns(2)
                with col1:
                    recurring_type = st.selectbox("반복 주기", ["매일", "매주", "매월"], key="schedule_recurring_type_unique")
                with col2:
                    recurring_count = st.number_input("반복 횟수", min_value=1, max_value=52, value=4, key="schedule_recurring_count_unique")

            add_schedule = st.form_submit_button("📅 일정 등록", use_container_width=True)

            if add_schedule:
                if title and description and selected_club and location:
                    # Create base schedule data
                    schedule_data = {
                        'title': title,
                        'description': description,
                        'club': selected_club,
                        'date': event_date.strftime('%Y-%m-%d'),
                        'time': event_time.strftime('%H:%M'),
                        'location': location,
                        'creator': user['name'],
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    schedules_to_create = [schedule_data]

                    # Create recurring schedules
                    if is_recurring and recurring_type:
                        for i in range(1, recurring_count):
                            recurring_date = event_date

                            if recurring_type == "매일":
                                recurring_date = event_date + timedelta(days=i)
                            elif recurring_type == "매주":
                                recurring_date = event_date + timedelta(weeks=i)
                            elif recurring_type == "매월":
                                try:
                                    if event_date.month + i <= 12:
                                        recurring_date = event_date.replace(month=event_date.month + i)
                                    else:
                                        year_add = (event_date.month + i - 1) // 12
                                        month_new = (event_date.month + i - 1) % 12 + 1
                                        recurring_date = event_date.replace(year=event_date.year + year_add, month=month_new)
                                except ValueError:
                                    # Handle month-end dates
                                    recurring_date = event_date + timedelta(days=30 * i)

                            recurring_schedule = schedule_data.copy()
                            recurring_schedule['date'] = recurring_date.strftime('%Y-%m-%d')
                            schedules_to_create.append(recurring_schedule)

                    # Save all schedules
                    success_count = 0
                    for schedule in schedules_to_create:
                        if st.session_state.data_manager.add_record('schedule', schedule):
                            success_count += 1

                    if success_count == len(schedules_to_create):
                        st.success(f"일정이 등록되었습니다! ({success_count}개)")
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 일정: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 일정을 등록했습니다. 날짜: {event_date}"
                        )
                        st.rerun()
                    else:
                        st.error(f"일정 등록에 부분적으로 실패했습니다. ({success_count}/{len(schedules_to_create)})")
                else:
                    st.error("모든 필수 항목을 입력해주세요.")

    def show_schedule_management(self, user):
        """Display schedule management interface"""
        st.markdown("#### 📋 일정 관리")

        schedule_df = st.session_state.data_manager.load_csv('schedule')

        if schedule_df.empty:
            st.info("관리할 일정이 없습니다.")
            return

        # Filter schedules based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            schedule_df = schedule_df[
                (schedule_df['club'].isin(user_club_names)) |
                (schedule_df['creator'] == user['name'])
            ]

        # Show upcoming schedules
        today = date.today()
        schedule_df['date'] = pd.to_datetime(schedule_df['date']).dt.date
        upcoming_schedules = schedule_df[schedule_df['date'] >= today]

        st.markdown("##### 📅 다가오는 일정")

        if upcoming_schedules.empty:
            st.info("다가오는 일정이 없습니다.")
        else:
            for _, schedule in upcoming_schedules.iterrows():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    st.write(f"**{schedule['title']}** ({schedule['club']})")
                    st.write(f"📅 {schedule['date']} ⏰ {schedule['time']} 📍 {schedule['location']}")

                with col2:
                    if st.button("✏️", key=f"edit_mgmt_{schedule['id']}", help="수정"):
                        st.session_state[f'edit_schedule_{schedule["id"]}'] = True

                with col3:
                    if st.button("🗑️", key=f"delete_mgmt_{schedule['id']}", help="삭제"):
                        if self.delete_schedule(schedule['id']):
                            st.success("삭제됨")
                            st.rerun()

                with col4:
                    if st.button("🔔", key=f"notify_mgmt_{schedule['id']}", help="알림 발송"):
                        self.send_schedule_notification(schedule)
                        st.success("알림 발송됨")

                st.divider()

        # Bulk operations
        st.markdown("##### 🔧 일괄 작업")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📧 모든 일정 알림 발송", use_container_width=True):
                count = 0
                for _, schedule in upcoming_schedules.iterrows():
                    self.send_schedule_notification(schedule)
                    count += 1
                st.success(f"{count}개 일정에 대한 알림을 발송했습니다.")

        with col2:
            if st.button("🗑️ 지난 일정 정리", use_container_width=True):
                past_schedules = schedule_df[schedule_df['date'] < today]
                count = 0
                for _, schedule in past_schedules.iterrows():
                    if self.delete_schedule(schedule['id']):
                        count += 1
                if count > 0:
                    st.success(f"{count}개의 지난 일정을 정리했습니다.")
                    st.rerun()
                else:
                    st.info("정리할 지난 일정이 없습니다.")

    def show_my_schedule(self, user):
        """Display user's personal schedule"""
        st.markdown("#### 📝 내 관련 일정")

        schedule_df = st.session_state.data_manager.load_csv('schedule')

        if schedule_df.empty:
            st.info("등록된 일정이 없습니다.")
            return

        # Get user's clubs
        user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
        user_club_names = user_clubs['club_name'].tolist() + ["전체"]

        # Filter schedules for user's clubs
        my_schedules = schedule_df[
            (schedule_df['club'].isin(user_club_names)) |
            (schedule_df['creator'] == user['name'])
        ]

        if my_schedules.empty:
            st.info("내 관련 일정이 없습니다.")
            return

        # Separate upcoming and past schedules
        today = date.today()
        my_schedules['date'] = pd.to_datetime(my_schedules['date']).dt.date

        upcoming = my_schedules[my_schedules['date'] >= today]
        past = my_schedules[my_schedules['date'] < today]

        # Show upcoming schedules
        st.markdown("##### 📅 다가오는 일정")

        if upcoming.empty:
            st.info("다가오는 일정이 없습니다.")
        else:
            upcoming = upcoming.sort_values('date')

            for _, schedule in upcoming.iterrows():
                # Calculate days until event
                days_until = (schedule['date'] - today).days

                if days_until == 0:
                    time_text = "오늘"
                    time_color = "#dc3545"
                elif days_until == 1:
                    time_text = "내일"
                    time_color = "#fd7e14"
                elif days_until <= 7:
                    time_text = f"{days_until}일 후"
                    time_color = "#ffc107"
                else:
                    time_text = f"{days_until}일 후"
                    time_color = "#28a745"

                st.markdown(f"""
                <div class="club-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0;">{schedule['title']}</h4>
                            <p style="color: #666; margin: 5px 0;">{schedule['description']}</p>
                            <div style="margin: 10px 0;">
                                <span style="background: #e9ecef; padding: 4px 8px; border-radius: 10px; font-size: 12px; margin-right: 10px;">
                                    🏷️ {schedule['club']}
                                </span>
                                <span style="background: #e9ecef; padding: 4px 8px; border-radius: 10px; font-size: 12px; margin-right: 10px;">
                                    📍 {schedule['location']}
                                </span>
                                <span style="background: #e9ecef; padding: 4px 8px; border-radius: 10px; font-size: 12px;">
                                    ⏰ {schedule['time']}
                                </span>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="background: {time_color}; color: white; padding: 6px 12px; border-radius: 15px; font-size: 14px; font-weight: bold;">
                                {time_text}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Show recent past schedules
        if not past.empty:
            st.markdown("##### 📚 최근 지난 일정")

            recent_past = past.sort_values('date', ascending=False).head(5)

            for _, schedule in recent_past.iterrows():
                days_ago = (today - schedule['date']).days

                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; opacity: 0.7;">
                    <h5 style="margin: 0;">{schedule['title']} ({schedule['club']})</h5>
                    <p style="color: #666; margin: 5px 0; font-size: 14px;">
                        📅 {schedule['date']} ⏰ {schedule['time']} 📍 {schedule['location']}
                    </p>
                    <small style="color: #999;">{days_ago}일 전</small>
                </div>
                """, unsafe_allow_html=True)

    def show_edit_schedule_form(self, schedule, user):
        """Display schedule edit form"""
        st.markdown("---")
        st.markdown(f"#### ✏️ 일정 수정: {schedule['title']}")

        with st.form(f"edit_schedule_form_{schedule['id']}"):
            # Pre-fill with existing data
            new_title = st.text_input("제목", value=schedule['title'])
            new_description = st.text_area("설명", value=schedule['description'], height=100)

            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("날짜", value=pd.to_datetime(schedule['date']).date())
            with col2:
                new_time = st.time_input("시간", value=pd.to_datetime(schedule['time']).time())

            new_location = st.text_input("장소", value=schedule['location'])

            col1, col2 = st.columns(2)
            with col1:
                save_button = st.form_submit_button("💾 저장", use_container_width=True)
            with col2:
                cancel_button = st.form_submit_button("❌ 취소", use_container_width=True)

            if save_button:
                updates = {
                    'title': new_title,
                    'description': new_description,
                    'date': new_date.strftime('%Y-%m-%d'),
                    'time': new_time.strftime('%H:%M'),
                    'location': new_location
                }

                if st.session_state.data_manager.update_record('schedule', schedule['id'], updates):
                    st.success("일정이 수정되었습니다!")
                    st.session_state[f'edit_schedule_{schedule["id"]}'] = False
                    st.rerun()
                else:
                    st.error("일정 수정에 실패했습니다.")

            if cancel_button:
                st.session_state[f'edit_schedule_{schedule["id"]}'] = False
                st.rerun()

    def delete_schedule(self, schedule_id):
        """Delete a schedule"""
        return st.session_state.data_manager.delete_record('schedule', schedule_id)

    def send_schedule_notification(self, schedule):
        """Send notification for a schedule"""
        notification_title = f"일정 알림: {schedule['title']}"
        notification_message = f"""
        📅 날짜: {schedule['date']}
        ⏰ 시간: {schedule['time']}
        📍 장소: {schedule['location']}
        🏷️ 동아리: {schedule['club']}

        {schedule['description']}
        """

        # Send to all if club is "전체", otherwise send to club members
        if schedule['club'] == "전체":
            target = "all"
        else:
            target = "all"  # For now, send to all users. Can be refined to specific club members

        st.session_state.notification_system.add_notification(
            notification_title,
            "info",
            target,
            notification_message
        )