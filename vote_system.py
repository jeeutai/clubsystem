import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json, timedelta
import json

class VoteSystem:
    def __init__(self):
        self.votes_file = 'data/votes.csv'
        self.vote_responses_file = 'data/vote_responses.csv'
        self.initialize_vote_files()

    def initialize_vote_files(self):
        """Initialize vote-related CSV files"""
        # Initialize votes.csv
        if not st.session_state.data_manager.load_csv('votes').empty is False:
            votes_structure = ['id', 'title', 'description', 'options', 'club', 'creator', 'end_date', 'status', 'allow_multiple', 'created_date']
            empty_df = pd.DataFrame(columns=votes_structure)
            st.session_state.data_manager.save_csv('votes', empty_df)

        # Initialize vote_responses.csv
        if not st.session_state.data_manager.load_csv('vote_responses').empty is False:
            responses_structure = ['id', 'vote_id', 'username', 'selected_options', 'voted_date']
            empty_df = pd.DataFrame(columns=responses_structure)
            st.session_state.data_manager.save_csv('vote_responses', empty_df)

    def show_vote_interface(self, user):
        """Display the vote interface"""
        st.markdown("### 🗳️ 투표")

        if user['role'] in ['선생님', '회장', '부회장']:
            tabs = st.tabs(["🗳️ 투표 목록", "➕ 투표 생성", "📊 결과 분석"])
        else:
            tabs = st.tabs(["🗳️ 투표 목록", "📈 내 투표"])

        with tabs[0]:
            self.show_vote_list(user)

        if user['role'] in ['선생님', '회장', '부회장']:
            with tabs[1]:
                self.show_vote_creation(user)

            with tabs[2]:
                self.show_vote_analytics(user)
        else:
            with tabs[1]:
                self.show_my_votes(user)

    def show_vote_list(self, user):
        """Display list of votes"""
        st.markdown("#### 🗳️ 진행 중인 투표")

        votes_df = st.session_state.data_manager.load_csv('votes')

        if votes_df.empty:
            st.info("등록된 투표가 없습니다.")
            return

        # Filter votes based on user's clubs
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = ["전체"] + user_clubs['club_name'].tolist()
            votes_df = votes_df[
                (votes_df['club'].isin(user_club_names)) |
                (votes_df['creator'] == user['name'])
            ]

        # Sort by end date
        votes_df['end_date'] = pd.to_datetime(votes_df['end_date'])
        votes_df = votes_df.sort_values('end_date')

        # Separate active and ended votes
        now = datetime.now()
        active_votes = votes_df[
            (votes_df['end_date'] > now) & 
            (votes_df['status'] == '활성')
        ]
        ended_votes = votes_df[
            (votes_df['end_date'] <= now) | 
            (votes_df['status'] == '종료')
        ]

        # Display active votes
        if not active_votes.empty:
            st.markdown("##### 🔥 진행 중인 투표")
            for _, vote in active_votes.iterrows():
                self.show_vote_card(vote, user, is_active=True)

        # Display ended votes
        if not ended_votes.empty:
            st.markdown("##### 📊 종료된 투표")
            for _, vote in ended_votes.iterrows():
                self.show_vote_card(vote, user, is_active=False)

        if active_votes.empty and ended_votes.empty:
            st.info("참여할 수 있는 투표가 없습니다.")

    def show_vote_card(self, vote, user, is_active=True):
        """Display a single vote card"""
        # Calculate time until end
        end_date = pd.to_datetime(vote['end_date'])
        now = datetime.now()
        time_diff = end_date - now

        if is_active and time_diff.total_seconds() > 0:
            if time_diff.days > 0:
                time_status = f"{time_diff.days}일 후 마감"
                status_color = "#28a745"
            elif time_diff.seconds > 3600:
                hours = time_diff.seconds // 3600
                time_status = f"{hours}시간 후 마감"
                status_color = "#ffc107"
            else:
                minutes = time_diff.seconds // 60
                time_status = f"{minutes}분 후 마감"
                status_color = "#fd7e14"
        else:
            time_status = "투표 종료"
            status_color = "#6c757d"

        # Check if user has voted
        responses_df = st.session_state.data_manager.load_csv('vote_responses')
        user_response = responses_df[
            (responses_df['vote_id'] == vote['id']) & 
            (responses_df['username'] == user['username'])
        ]
        has_voted = not user_response.empty

        # Parse options
        try:
            options = json.loads(vote['options']) if isinstance(vote['options'], str) else vote['options']
        except:
            options = []

        with st.container():
            st.markdown(f"""
            <div class="club-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #333;">{vote['title']}</h4>
                        <div style="margin: 10px 0;">
                            <span style="background-color: {status_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px;">
                                {time_status}
                            </span>
                            {f'<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; margin-left: 10px;">✅ 투표함</span>' if has_voted else ''}
                        </div>
                    </div>
                </div>

                <p style="color: #666; line-height: 1.6; margin: 15px 0;">{vote['description']}</p>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div><strong>🏷️ 동아리:</strong> {vote['club']}</div>
                        <div><strong>👤 주최자:</strong> {vote['creator']}</div>
                        <div><strong>📅 마감일:</strong> {vote['end_date'].strftime('%Y-%m-%d %H:%M')}</div>
                        <div><strong>🔄 복수선택:</strong> {'가능' if vote.get('allow_multiple', False) else '불가능'}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Voting interface
            if is_active and not has_voted and options:
                st.markdown("**투표 선택지:**")

                with st.form(f"vote_form_{vote['id']}"):
                    selected_options = []

                    if vote.get('allow_multiple', False):
                        # Multiple choice
                        for i, option in enumerate(options):
                            if st.checkbox(option, key=f"vote_option_{vote['id']}_{i}"):
                                selected_options.append(option)
                    else:
                        # Single choice
                        selected_option = st.radio("선택하세요", options, key=f"vote_radio_{vote['id']}")
                        if selected_option:
                            selected_options = [selected_option]

                    submit_vote = st.form_submit_button("🗳️ 투표하기", use_container_width=True)

                    if submit_vote:
                        if selected_options:
                            if self.submit_vote(vote['id'], user['username'], selected_options):
                                st.success("투표가 완료되었습니다!")
                                st.rerun()
                            else:
                                st.error("투표 제출에 실패했습니다.")
                        else:
                            st.error("선택지를 선택해주세요.")

            elif has_voted:
                # Show user's vote
                user_selections = json.loads(user_response.iloc[0]['selected_options'])
                st.markdown("**내 선택:**")
                for selection in user_selections:
                    st.markdown(f"✅ {selection}")

            # Action buttons for managers
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📊 결과", key=f"results_{vote['id']}"):
                    st.session_state[f'show_vote_results_{vote["id"]}'] = True

            with col2:
                if user['role'] in ['선생님', '회장', '부회장'] or user['name'] == vote['creator']:
                    if st.button("⚙️ 관리", key=f"manage_vote_{vote['id']}"):
                        st.session_state[f'manage_vote_{vote["id"]}'] = True

            with col3:
                if user['role'] in ['선생님', '회장', '부회장'] or user['name'] == vote['creator']:
                    if is_active:
                        if st.button("🔒 종료", key=f"end_vote_{vote['id']}"):
                            if self.end_vote(vote['id']):
                                st.success("투표가 종료되었습니다.")
                                st.rerun()

            with col4:
                if st.button("💬 댓글", key=f"comment_vote_{vote['id']}"):
                    st.session_state[f'show_vote_comments_{vote["id"]}'] = True

            # Show results if requested
            if st.session_state.get(f'show_vote_results_{vote["id"]}', False):
                self.show_vote_results(vote)

    def show_vote_creation(self, user):
        """Display vote creation form"""
        st.markdown("#### ➕ 새 투표 생성")

        # Initialize options in session state
        if 'vote_options' not in st.session_state:
            st.session_state.vote_options = []

        # Option management outside of form
        st.markdown("##### 📝 선택지 관리")

        col1, col2 = st.columns([3, 1])
        with col1:
            new_option = st.text_input("새 선택지", placeholder="새 선택지를 입력하세요", key="new_vote_option")
        with col2:
            if st.button("➕ 추가"):
                if new_option.strip() and new_option not in st.session_state.vote_options:
                    st.session_state.vote_options.append(new_option.strip())
                    st.success(f"선택지가 추가되었습니다! (총 {len(st.session_state.vote_options)}개)")
                    st.rerun()
                elif new_option in st.session_state.vote_options:
                    st.warning("이미 존재하는 선택지입니다.")

        # Show added options
        if st.session_state.vote_options:
            st.markdown("##### 등록된 선택지")
            for i, option in enumerate(st.session_state.vote_options):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {option}")
                with col2:
                    if st.button("🗑️", key=f"del_option_{i}"):
                        st.session_state.vote_options.pop(i)
                        st.rerun()

        st.divider()

        # Vote creation form
        with st.form("create_vote_form"):
            # Get user's clubs for club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="vote_club_select_unique")
            title = st.text_input("📝 투표 제목", placeholder="투표 제목을 입력하세요", key="vote_title_input")
            description = st.text_area("📄 투표 설명", placeholder="투표에 대한 설명을 입력하세요", height=100, key="vote_desc_input")

            # End date and time
            col1, col2 = st.columns(2)
            with col1:
                end_date = st.date_input("📅 마감일", min_value=date.today(), key="vote_end_date_unique")
            with col2:
                end_time = st.time_input("⏰ 마감 시간", value=datetime.now().time(), key="vote_end_time_unique")

            allow_multiple = st.checkbox("🔄 복수 선택 허용")

            submit_button = st.form_submit_button("🗳️ 투표 생성", use_container_width=True)

            if submit_button:
                if title and description and selected_club and len(st.session_state.vote_options) >= 2:
                    end_datetime = datetime.combine(end_date, end_time)

                    vote_data = {
                        'title': title,
                        'description': description,
                        'options': json.dumps(st.session_state.vote_options, ensure_ascii=False),
                        'club': selected_club,
                        'creator': user['name'],
                        'end_date': end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': '활성',
                        'allow_multiple': allow_multiple,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('votes', vote_data):
                        st.success("투표가 생성되었습니다!")
                        st.session_state.vote_options = []  # Clear options
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 투표: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 투표를 등록했습니다. 마감일: {end_date}"
                        )
                        st.rerun()
                    else:
                        st.error("투표 생성에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력하고 최소 2개 이상의 선택지를 등록해주세요.")

    def submit_vote(self, vote_id, username, selected_options):
        """Submit a vote"""
        try:
            response_data = {
                'vote_id': vote_id,
                'username': username,
                'selected_options': json.dumps(selected_options, ensure_ascii=False),
                'voted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return st.session_state.data_manager.add_record('vote_responses', response_data)
        except Exception as e:
            st.error(f"투표 제출 중 오류가 발생했습니다: {e}")
            return False

    def end_vote(self, vote_id):
        """End a vote"""
        try:
            return st.session_state.data_manager.update_record('votes', vote_id, {'status': '종료'})
        except Exception as e:
            st.error(f"투표 종료 중 오류가 발생했습니다: {e}")
            return False

    def show_vote_results(self, vote):
        """Show vote results"""
        st.markdown("---")
        st.markdown(f"#### 📊 {vote['title']} 투표 결과")

        # Get responses
        responses_df = st.session_state.data_manager.load_csv('vote_responses')
        vote_responses = responses_df[responses_df['vote_id'] == vote['id']]

        if vote_responses.empty:
            st.info("아직 투표한 사람이 없습니다.")
            return

        # Parse options
        try:
            options = json.loads(vote['options']) if isinstance(vote['options'], str) else vote['options']
        except:
            options = []

        # Count votes for each option
        option_counts = {option: 0 for option in options}
        total_voters = len(vote_responses)

        for _, response in vote_responses.iterrows():
            try:
                selected_options = json.loads(response['selected_options'])
                for option in selected_options:
                    if option in option_counts:
                        option_counts[option] += 1
            except:
                continue

        # Display results
        st.markdown(f"**총 투표자 수: {total_voters}명**")

        # Results chart
        results_data = []
        for option, count in option_counts.items():
            percentage = (count / total_voters * 100) if total_voters > 0 else 0
            results_data.append({
                '선택지': option,
                '득표 수': count,
                '득표율': f"{percentage:.1f}%"
            })

        results_df = pd.DataFrame(results_data)
        results_df = results_df.sort_values('득표 수', ascending=False)

        # Display as chart
        st.bar_chart(results_df.set_index('선택지')['득표 수'])

        # Display as table
        st.dataframe(results_df, use_container_width=True)

        # Winner announcement
        if results_data:
            winner = results_df.iloc[0]
            if winner['득표 수'] > 0:
                st.success(f"🏆 1위: {winner['선택지']} ({winner['득표 수']}표, {winner['득표율']})")

        if st.button("❌ 결과 닫기", key=f"close_results_{vote['id']}"):
            st.session_state[f'show_vote_results_{vote["id"]}'] = False
            st.rerun()

    def show_vote_analytics(self, user):
        """Display vote analytics for managers"""
        st.markdown("#### 📊 투표 분석")

        votes_df = st.session_state.data_manager.load_csv('votes')
        responses_df = st.session_state.data_manager.load_csv('vote_responses')

        if votes_df.empty:
            st.info("분석할 투표가 없습니다.")
            return

        # Filter votes based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            votes_df = votes_df[
                (votes_df['club'].isin(user_club_names)) |
                (votes_df['creator'] == user['name'])
            ]

        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 투표 수", len(votes_df))

        with col2:
            active_votes = len(votes_df[votes_df['status'] == '활성'])
            st.metric("진행 중", active_votes)

        with col3:
            ended_votes = len(votes_df[votes_df['status'] == '종료'])
            st.metric("종료된 투표", ended_votes)

        with col4:
            total_responses = len(responses_df)
            st.metric("총 투표 참여", total_responses)

        # Participation rate by vote
        st.markdown("##### 📊 투표별 참여율")

        participation_data = []
        for _, vote in votes_df.iterrows():
            vote_responses = responses_df[responses_df['vote_id'] == vote['id']]
            participation_count = len(vote_responses)

            # Get potential voters (club members)
            if vote['club'] == '전체':
                users_df = st.session_state.data_manager.load_csv('users')
                potential_voters = len(users_df)
            else:
                users_df = st.session_state.data_manager.load_csv('users')
                club_users = users_df[users_df['club_name'] == vote['club']]
                potential_voters = len(club_users)

            participation_rate = (participation_count / potential_voters * 100) if potential_voters > 0 else 0

            participation_data.append({
                '투표명': vote['title'],
                '동아리': vote['club'],
                '참여자': participation_count,
                '대상자': potential_voters,
                '참여율': f"{participation_rate:.1f}%",
                '상태': vote['status']
            })

        if participation_data:
            participation_df = pd.DataFrame(participation_data)
            participation_df = participation_df.sort_values('참여율', ascending=False)
            st.dataframe(participation_df, use_container_width=True)

        # Most active voters
        st.markdown("##### 👥 활발한 투표 참여자")

        if not responses_df.empty:
            user_vote_counts = responses_df['username'].value_counts().head(10)
            users_df = st.session_state.data_manager.load_csv('users')

            active_voters = []
            for username, count in user_vote_counts.items():
                user_info = users_df[users_df['username'] == username]
                user_name = user_info['name'].iloc[0] if not user_info.empty else username
                user_club = user_info['club_name'].iloc[0] if not user_info.empty else "알 수 없음"

                active_voters.append({
                    '이름': user_name,
                    '동아리': user_club,
                    '투표 참여 수': count
                })

            active_voters_df = pd.DataFrame(active_voters)
            st.dataframe(active_voters_df, use_container_width=True)

    def show_my_votes(self, user):
        """Display user's voting history"""
        st.markdown("#### 📈 내 투표 기록")

        responses_df = st.session_state.data_manager.load_csv('vote_responses')
        user_responses = responses_df[responses_df['username'] == user['username']]

        if user_responses.empty:
            st.info("참여한 투표가 없습니다.")
            return

        # Get vote details
        votes_df = st.session_state.data_manager.load_csv('votes')

        # Calculate statistics
        total_votes = len(user_responses)
        recent_votes = len(user_responses[pd.to_datetime(user_responses['voted_date']) >= (datetime.now() - timedelta(days=30))])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 참여 투표", total_votes)
        with col2:
            st.metric("최근 30일 참여", recent_votes)

        st.markdown("##### 📋 투표 참여 내역")

        # Sort by voting date (recent first)
        user_responses['voted_date'] = pd.to_datetime(user_responses['voted_date'])
        user_responses = user_responses.sort_values('voted_date', ascending=False)

        for _, response in user_responses.iterrows():
            vote_info = votes_df[votes_df['id'] == response['vote_id']]

            if not vote_info.empty:
                vote = vote_info.iloc[0]
                selected_options = json.loads(response['selected_options'])

                st.markdown(f"""
                <div class="club-card">
                    <h4>{vote['title']} ({vote['club']})</h4>
                    <p><strong>투표일:</strong> {response['voted_date'].strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>내 선택:</strong> {', '.join(selected_options)}</p>
                    <p><strong>상태:</strong> {vote['status']}</p>
                </div>
                """, unsafe_allow_html=True)
    def show_vote_creation(self, user):
        """Display vote creation form"""
        st.markdown("#### ➕ 새 투표 생성")

        # Initialize options in session state
        if 'vote_options' not in st.session_state:
            st.session_state.vote_options = []

        # Option management outside of form
        st.markdown("##### 📝 선택지 관리")

        col1, col2 = st.columns([3, 1])
        with col1:
            new_option = st.text_input("새 선택지", placeholder="새 선택지를 입력하세요", key="new_vote_option")
        with col2:
            if st.button("➕ 추가"):
                if new_option.strip() and new_option not in st.session_state.vote_options:
                    st.session_state.vote_options.append(new_option.strip())
                    st.success(f"선택지가 추가되었습니다! (총 {len(st.session_state.vote_options)}개)")
                    st.rerun()
                elif new_option in st.session_state.vote_options:
                    st.warning("이미 존재하는 선택지입니다.")

        # Show added options
        if st.session_state.vote_options:
            st.markdown("##### 등록된 선택지")
            for i, option in enumerate(st.session_state.vote_options):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {option}")
                with col2:
                    if st.button("🗑️", key=f"del_option_{i}"):
                        st.session_state.vote_options.pop(i)
                        st.rerun()

        st.divider()

        # Vote creation form
        with st.form("create_vote_form"):
            # Get user's clubs for club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="vote_club_select_unique")
            title = st.text_input("📝 투표 제목", placeholder="투표 제목을 입력하세요", key="vote_title_input")
            description = st.text_area("📄 투표 설명", placeholder="투표에 대한 설명을 입력하세요", height=100, key="vote_desc_input")

            # End date and time
            col1, col2 = st.columns(2)
            with col1:
                end_date = st.date_input("📅 마감일", min_value=date.today(), key="vote_end_date_unique")
            with col2:
                end_time = st.time_input("⏰ 마감 시간", value=datetime.now().time(), key="vote_end_time_unique")

            allow_multiple = st.checkbox("🔄 복수 선택 허용")

            submit_button = st.form_submit_button("🗳️ 투표 생성", use_container_width=True)

            if submit_button:
                if title and description and selected_club and len(st.session_state.vote_options) >= 2:
                    end_datetime = datetime.combine(end_date, end_time)

                    vote_data = {
                        'title': title,
                        'description': description,
                        'options': json.dumps(st.session_state.vote_options, ensure_ascii=False),
                        'club': selected_club,
                        'creator': user['name'],
                        'end_date': end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': '활성',
                        'allow_multiple': allow_multiple,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('votes', vote_data):
                        st.success("투표가 생성되었습니다!")
                        st.session_state.vote_options = []  # Clear options
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 투표: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 투표를 등록했습니다. 마감일: {end_date}"
                        )
                        st.rerun()
                    else:
                        st.error("투표 생성에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력하고 최소 2개 이상의 선택지를 등록해주세요.")
    def show_vote_creation(self, user):
        """Display vote creation form"""
        st.markdown("#### ➕ 새 투표 생성")

        # Initialize options in session state
        if 'vote_options' not in st.session_state:
            st.session_state.vote_options = []

        # Option management outside of form
        st.markdown("##### 📝 선택지 관리")

        col1, col2 = st.columns([3, 1])
        with col1:
            new_option = st.text_input("새 선택지", placeholder="새 선택지를 입력하세요", key="new_vote_option")
        with col2:
            if st.button("➕ 추가"):
                if new_option.strip() and new_option not in st.session_state.vote_options:
                    st.session_state.vote_options.append(new_option.strip())
                    st.success(f"선택지가 추가되었습니다! (총 {len(st.session_state.vote_options)}개)")
                    st.rerun()
                elif new_option in st.session_state.vote_options:
                    st.warning("이미 존재하는 선택지입니다.")

        # Show added options
        if st.session_state.vote_options:
            st.markdown("##### 등록된 선택지")
            for i, option in enumerate(st.session_state.vote_options):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {option}")
                with col2:
                    if st.button("🗑️", key=f"del_option_{i}"):
                        st.session_state.vote_options.pop(i)
                        st.rerun()

        st.divider()

        # Vote creation form
        with st.form("create_vote_form"):
            # Get user's clubs for club selection
            if user['role'] == '선생님':
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_options = ["전체"] + clubs_df['name'].tolist() if not clubs_df.empty else ["전체"]
            else:
                user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
                club_options = user_clubs['club_name'].tolist()

            selected_club = st.selectbox("🏷️ 동아리 선택", club_options, key="vote_club_select_unique")
            title = st.text_input("📝 투표 제목", placeholder="투표 제목을 입력하세요", key="vote_title_input")
            description = st.text_area("📄 투표 설명", placeholder="투표에 대한 설명을 입력하세요", height=100, key="vote_desc_input")

            # End date and time
            col1, col2 = st.columns(2)
            with col1:
                end_date = st.date_input("📅 마감일", min_value=date.today(), key="vote_end_date_unique")
            with col2:
                end_time = st.time_input("⏰ 마감 시간", value=datetime.now().time(), key="vote_end_time_unique")

            allow_multiple = st.checkbox("🔄 복수 선택 허용")

            submit_button = st.form_submit_button("🗳️ 투표 생성", use_container_width=True)

            if submit_button:
                if title and description and selected_club and len(st.session_state.vote_options) >= 2:
                    end_datetime = datetime.combine(end_date, end_time)

                    vote_data = {
                        'title': title,
                        'description': description,
                        'options': json.dumps(st.session_state.vote_options, ensure_ascii=False),
                        'club': selected_club,
                        'creator': user['name'],
                        'end_date': end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': '활성',
                        'allow_multiple': allow_multiple,
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if st.session_state.data_manager.add_record('votes', vote_data):
                        st.success("투표가 생성되었습니다!")
                        st.session_state.vote_options = []  # Clear options
                        # Add notification
                        st.session_state.notification_system.add_notification(
                            f"새 투표: {title}",
                            "info",
                            "all",
                            f"{user['name']}님이 새 투표를 등록했습니다. 마감일: {end_date}"
                        )
                        st.rerun()
                    else:
                        st.error("투표 생성에 실패했습니다.")
                else:
                    st.error("모든 필수 항목을 입력하고 최소 2개 이상의 선택지를 등록해주세요.")

        # Vote options
        st.markdown("##### 📋 투표 선택지")

        if 'vote_options' not in st.session_state:
            st.session_state.vote_options = ["", ""]

        for i in range(len(st.session_state.vote_options)):
            st.session_state.vote_options[i] = st.text_input(
                f"선택지 {i+1}", 
                value=st.session_state.vote_options[i],
                key=f"vote_option_create_{i}"
            )

    def submit_vote(self, vote_id, username, selected_options):
        """Submit a vote"""
        try:
            response_data = {
                'vote_id': vote_id,
                'username': username,
                'selected_options': json.dumps(selected_options, ensure_ascii=False),
                'voted_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            return st.session_state.data_manager.add_record('vote_responses', response_data)
        except Exception as e:
            st.error(f"투표 제출 중 오류가 발생했습니다: {e}")
            return False

    def end_vote(self, vote_id):
        """End a vote"""
        try:
            return st.session_state.data_manager.update_record('votes', vote_id, {'status': '종료'})
        except Exception as e:
            st.error(f"투표 종료 중 오류가 발생했습니다: {e}")
            return False

    def show_vote_results(self, vote):
        """Show vote results"""
        st.markdown("---")
        st.markdown(f"#### 📊 {vote['title']} 투표 결과")

        # Get responses
        responses_df = st.session_state.data_manager.load_csv('vote_responses')
        vote_responses = responses_df[responses_df['vote_id'] == vote['id']]

        if vote_responses.empty:
            st.info("아직 투표한 사람이 없습니다.")
            return

        # Parse options
        try:
            options = json.loads(vote['options']) if isinstance(vote['options'], str) else vote['options']
        except:
            options = []

        # Count votes for each option
        option_counts = {option: 0 for option in options}
        total_voters = len(vote_responses)

        for _, response in vote_responses.iterrows():
            try:
                selected_options = json.loads(response['selected_options'])
                for option in selected_options:
                    if option in option_counts:
                        option_counts[option] += 1
            except:
                continue

        # Display results
        st.markdown(f"**총 투표자 수: {total_voters}명**")

        # Results chart
        results_data = []
        for option, count in option_counts.items():
            percentage = (count / total_voters * 100) if total_voters > 0 else 0
            results_data.append({
                '선택지': option,
                '득표 수': count,
                '득표율': f"{percentage:.1f}%"
            })

        results_df = pd.DataFrame(results_data)
        results_df = results_df.sort_values('득표 수', ascending=False)

        # Display as chart
        st.bar_chart(results_df.set_index('선택지')['득표 수'])

        # Display as table
        st.dataframe(results_df, use_container_width=True)

        # Winner announcement
        if results_data:
            winner = results_df.iloc[0]
            if winner['득표 수'] > 0:
                st.success(f"🏆 1위: {winner['선택지']} ({winner['득표 수']}표, {winner['득표율']})")

        if st.button("❌ 결과 닫기", key=f"close_results_{vote['id']}"):
            st.session_state[f'show_vote_results_{vote["id"]}'] = False
            st.rerun()

    def show_vote_analytics(self, user):
        """Display vote analytics for managers"""
        st.markdown("#### 📊 투표 분석")

        votes_df = st.session_state.data_manager.load_csv('votes')
        responses_df = st.session_state.data_manager.load_csv('vote_responses')

        if votes_df.empty:
            st.info("분석할 투표가 없습니다.")
            return

        # Filter votes based on user role
        if user['role'] != '선생님':
            user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
            user_club_names = user_clubs['club_name'].tolist()
            votes_df = votes_df[
                (votes_df['club'].isin(user_club_names)) |
                (votes_df['creator'] == user['name'])
            ]

        # Overall statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 투표 수", len(votes_df))

        with col2:
            active_votes = len(votes_df[votes_df['status'] == '활성'])
            st.metric("진행 중", active_votes)

        with col3:
            ended_votes = len(votes_df[votes_df['status'] == '종료'])
            st.metric("종료된 투표", ended_votes)

        with col4:
            total_responses = len(responses_df)
            st.metric("총 투표 참여", total_responses)

        # Participation rate by vote
        st.markdown("##### 📊 투표별 참여율")

        participation_data = []
        for _, vote in votes_df.iterrows():
            vote_responses = responses_df[responses_df['vote_id'] == vote['id']]
            participation_count = len(vote_responses)

            # Get potential voters (club members)
            if vote['club'] == '전체':
                users_df = st.session_state.data_manager.load_csv('users')
                potential_voters = len(users_df)
            else:
                users_df = st.session_state.data_manager.load_csv('users')
                club_users = users_df[users_df['club_name'] == vote['club']]
                potential_voters = len(club_users)

            participation_rate = (participation_count / potential_voters * 100) if potential_voters > 0 else 0

            participation_data.append({
                '투표명': vote['title'],
                '동아리': vote['club'],
                '참여자': participation_count,
                '대상자': potential_voters,
                '참여율': f"{participation_rate:.1f}%",
                '상태': vote['status']
            })

        if participation_data:
            participation_df = pd.DataFrame(participation_data)
            participation_df = participation_df.sort_values('참여율', ascending=False)
            st.dataframe(participation_df, use_container_width=True)

        # Most active voters
        st.markdown("##### 👥 활발한 투표 참여자")

        if not responses_df.empty:
            user_vote_counts = responses_df['username'].value_counts().head(10)
            users_df = st.session_state.data_manager.load_csv('users')

            active_voters = []
            for username, count in user_vote_counts.items():
                user_info = users_df[users_df['username'] == username]
                user_name = user_info['name'].iloc[0] if not user_info.empty else username
                user_club = user_info['club_name'].iloc[0] if not user_info.empty else "알 수 없음"

                active_voters.append({
                    '이름': user_name,
                    '동아리': user_club,
                    '투표 참여 수': count
                })

            active_voters_df = pd.DataFrame(active_voters)
            st.dataframe(active_voters_df, use_container_width=True)

    def show_my_votes(self, user):
        """Display user's voting history"""
        st.markdown("#### 📈 내 투표 기록")

        responses_df = st.session_state.data_manager.load_csv('vote_responses')
        user_responses = responses_df[responses_df['username'] == user['username']]

        if user_responses.empty:
            st.info("참여한 투표가 없습니다.")
            return

        # Get vote details
        votes_df = st.session_state.data_manager.load_csv('votes')

        # Calculate statistics
        total_votes = len(user_responses)
        recent_votes = len(user_responses[pd.to_datetime(user_responses['voted_date']) >= (datetime.now() - timedelta(days=30))])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 참여 투표", total_votes)
        with col2:
            st.metric("최근 30일 참여", recent_votes)

        st.markdown("##### 📋 투표 참여 내역")

        # Sort by voting date (recent first)
        user_responses['voted_date'] = pd.to_datetime(user_responses['voted_date'])
        user_responses = user_responses.sort_values('voted_date', ascending=False)

        for _, response in user_responses.iterrows():
            vote_info = votes_df[votes_df['id'] == response['vote_id']]

            if not vote_info.empty:
                vote = vote_info.iloc[0]
                selected_options = json.loads(response['selected_options'])

                st.markdown(f"""
                <div class="club-card">
                    <h4>{vote['title']} ({vote['club']})</h4>
                    <p><strong>투표일:</strong> {response['voted_date'].strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>내 선택:</strong> {', '.join(selected_options)}</p>
                    <p><strong>상태:</strong> {vote['status']}</p>
                </div>
                """, unsafe_allow_html=True)