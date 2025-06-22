import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid

class VideoConferenceSystem:
    def __init__(self):
        self.data_manager = None
    
    def initialize_conference_files(self):
        """Initialize video conference CSV files"""
        if not hasattr(st.session_state, 'data_manager'):
            return
        
        self.data_manager = st.session_state.data_manager
        
        # Conference CSV structure
        conference_headers = ['id', 'title', 'description', 'club', 'organizer', 'meeting_url', 'password', 'scheduled_date', 'duration', 'status', 'participants', 'created_date']
        
        # Initialize if not exists
        conference_df = self.data_manager.load_csv('video_conferences')
        if conference_df.empty:
            conference_df = pd.DataFrame(columns=conference_headers)
            self.data_manager.save_csv('video_conferences', conference_df)
    
    def show_conference_interface(self, user):
        """Display the video conference interface"""
        self.initialize_conference_files()
        
        st.markdown("### 📹 화상 회의")
        
        tab1, tab2, tab3 = st.tabs(["📅 예정된 회의", "➕ 회의 생성", "📊 회의 기록"])
        
        with tab1:
            self.show_scheduled_meetings(user)
        
        with tab2:
            if user['role'] in ['선생님', '회장', '부회장']:
                self.show_meeting_creation(user)
            else:
                st.info("회의 생성 권한이 없습니다.")
        
        with tab3:
            self.show_meeting_history(user)
    
    def show_scheduled_meetings(self, user):
        """Display scheduled meetings"""
        conferences_df = self.data_manager.load_csv('video_conferences')
        
        if conferences_df.empty:
            st.info("예정된 회의가 없습니다.")
            return
        
        # Filter active meetings
        now = datetime.now()
        active_meetings = conferences_df[conferences_df['status'] == 'scheduled']
        
        if active_meetings.empty:
            st.info("예정된 회의가 없습니다.")
            return
        
        for _, meeting in active_meetings.iterrows():
            self.show_meeting_card(meeting, user)
    
    def show_meeting_card(self, meeting, user):
        """Display a meeting card"""
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 12px; margin: 10px 0; border-left: 4px solid #FF6B6B; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h4 style="margin: 0; color: #FF6B6B;">📹 {meeting['title']}</h4>
            <p style="margin: 5px 0; color: #666;">{meeting['description']}</p>
            <p style="margin: 5px 0;"><strong>동아리:</strong> {meeting['club']}</p>
            <p style="margin: 5px 0;"><strong>주최자:</strong> {meeting['organizer']}</p>
            <p style="margin: 5px 0;"><strong>일시:</strong> {meeting['scheduled_date']}</p>
            <p style="margin: 5px 0;"><strong>예상 시간:</strong> {meeting['duration']}분</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"🔗 회의 참가", key=f"join_{meeting['id']}"):
                # Open meeting URL
                st.markdown(f"""
                <script>
                window.open('{meeting['meeting_url']}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                
                st.success("새 탭에서 회의가 열립니다!")
                if meeting['password']:
                    st.info(f"회의 비밀번호: {meeting['password']}")
        
        with col2:
            if st.button(f"📋 회의 정보", key=f"info_{meeting['id']}"):
                st.info(f"""
                **회의 링크:** {meeting['meeting_url']}
                **비밀번호:** {meeting['password'] if meeting['password'] else '없음'}
                **참가자:** {meeting.get('participants', '없음')}
                """)
        
        with col3:
            if user['username'] == meeting['organizer'] or user['role'] == '선생님':
                if st.button(f"❌ 회의 취소", key=f"cancel_{meeting['id']}"):
                    self.cancel_meeting(meeting['id'])
                    st.success("회의가 취소되었습니다.")
                    st.rerun()
    
    def show_meeting_creation(self, user):
        """Display meeting creation form"""
        st.markdown("#### ➕ 새 회의 생성")
        
        with st.form("create_meeting"):
            title = st.text_input("회의 제목")
            description = st.text_area("회의 설명")
            
            # Club selection
            clubs_df = self.data_manager.load_csv('clubs')
            if user['role'] == '선생님':
                club_options = ["전체"] + clubs_df['name'].tolist()
            else:
                user_clubs = self.data_manager.get_user_clubs(user['username'])
                club_options = user_clubs['club_name'].tolist()
            
            selected_club = st.selectbox("대상 동아리", club_options)
            
            col1, col2 = st.columns(2)
            with col1:
                meeting_date = st.date_input("회의 날짜", min_value=date.today())
                meeting_time = st.time_input("회의 시간")
            
            with col2:
                duration = st.number_input("예상 시간 (분)", min_value=15, max_value=180, value=60)
                platform = st.selectbox("화상 회의 플랫폼", ["Google Meet", "Zoom", "기타"])
            
            meeting_url = st.text_input("회의 링크", placeholder="https://meet.google.com/xxx-xxxx-xxx")
            password = st.text_input("회의 비밀번호 (선택사항)")
            
            if st.form_submit_button("회의 생성"):
                if title and meeting_url:
                    meeting_data = {
                        'id': str(uuid.uuid4())[:8],
                        'title': title,
                        'description': description,
                        'club': selected_club,
                        'organizer': user['username'],
                        'meeting_url': meeting_url,
                        'password': password,
                        'scheduled_date': f"{meeting_date} {meeting_time}",
                        'duration': duration,
                        'status': 'scheduled',
                        'participants': '',
                        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    self.data_manager.add_record('video_conferences', meeting_data)
                    
                    # Send notification
                    if hasattr(st.session_state, 'notification_system'):
                        st.session_state.notification_system.send_club_notification(
                            selected_club, 
                            f"새 회의: {title}",
                            f"{meeting_date} {meeting_time}에 화상 회의가 예정되어 있습니다.",
                            "meeting"
                        )
                    
                    st.success("회의가 생성되었습니다!")
                    st.rerun()
                else:
                    st.error("제목과 회의 링크는 필수입니다.")
    
    def show_meeting_history(self, user):
        """Display meeting history"""
        conferences_df = self.data_manager.load_csv('video_conferences')
        
        if conferences_df.empty:
            st.info("회의 기록이 없습니다.")
            return
        
        # Filter completed meetings
        completed_meetings = conferences_df[conferences_df['status'].isin(['completed', 'cancelled'])]
        
        if completed_meetings.empty:
            st.info("완료된 회의가 없습니다.")
            return
        
        # Sort by date
        completed_meetings = completed_meetings.sort_values('scheduled_date', ascending=False)
        
        for _, meeting in completed_meetings.iterrows():
            status_icon = "✅" if meeting['status'] == 'completed' else "❌"
            status_text = "완료됨" if meeting['status'] == 'completed' else "취소됨"
            
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 3px solid {'#28a745' if meeting['status'] == 'completed' else '#dc3545'};">
                <h5 style="margin: 0;">{status_icon} {meeting['title']}</h5>
                <p style="margin: 5px 0; color: #666;">{meeting['description']}</p>
                <p style="margin: 5px 0; font-size: 12px;">
                    <strong>상태:</strong> {status_text} | 
                    <strong>일시:</strong> {meeting['scheduled_date']} | 
                    <strong>동아리:</strong> {meeting['club']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    def cancel_meeting(self, meeting_id):
        """Cancel a meeting"""
        conferences_df = self.data_manager.load_csv('video_conferences')
        
        # Update status
        conferences_df.loc[conferences_df['id'] == meeting_id, 'status'] = 'cancelled'
        self.data_manager.save_csv('video_conferences', conferences_df)
    
    def complete_meeting(self, meeting_id):
        """Mark meeting as completed"""
        conferences_df = self.data_manager.load_csv('video_conferences')
        
        # Update status
        conferences_df.loc[conferences_df['id'] == meeting_id, 'status'] = 'completed'
        self.data_manager.save_csv('video_conferences', conferences_df)
    
    def get_upcoming_meetings(self, user_club=None):
        """Get upcoming meetings for a specific club or user"""
        conferences_df = self.data_manager.load_csv('video_conferences')
        
        if conferences_df.empty:
            return pd.DataFrame()
        
        # Filter active meetings
        active_meetings = conferences_df[conferences_df['status'] == 'scheduled']
        
        if user_club:
            active_meetings = active_meetings[
                (active_meetings['club'] == user_club) | 
                (active_meetings['club'] == '전체')
            ]
        
        return active_meetings.sort_values('scheduled_date')