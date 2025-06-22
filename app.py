import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
from auth import AuthManager
from data_manager import DataManager
from ui_components import UIComponents
from board_system import BoardSystem
from chat_system import ChatSystem
from assignment_system import AssignmentSystem
from quiz_system import QuizSystem
from attendance_system import AttendanceSystem
from schedule_system import ScheduleSystem
from report_generator import ReportGenerator
from vote_system import VoteSystem
from gallery_system import GallerySystem
from video_conference_system import VideoConferenceSystem
from backup_system import BackupSystem
from notification_system import NotificationSystem
from search_system import SearchSystem
from admin_system import AdminSystem
from ai_assistant import AIAssistant
from gamification_system import GamificationSystem

# Configure page
st.set_page_config(
    page_title="폴라리스반 동아리 관리 시스템",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize systems
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()
if 'ui_components' not in st.session_state:
    st.session_state.ui_components = UIComponents()
if 'board_system' not in st.session_state:
    st.session_state.board_system = BoardSystem()
if 'chat_system' not in st.session_state:
    st.session_state.chat_system = ChatSystem()
if 'assignment_system' not in st.session_state:
    st.session_state.assignment_system = AssignmentSystem()
if 'quiz_system' not in st.session_state:
    st.session_state.quiz_system = QuizSystem()
if 'attendance_system' not in st.session_state:
    st.session_state.attendance_system = AttendanceSystem()
if 'schedule_system' not in st.session_state:
    st.session_state.schedule_system = ScheduleSystem()
if 'report_generator' not in st.session_state:
    st.session_state.report_generator = ReportGenerator()
if 'vote_system' not in st.session_state:
    st.session_state.vote_system = VoteSystem()
if 'notification_system' not in st.session_state:
    st.session_state.notification_system = NotificationSystem()
if 'search_system' not in st.session_state:
    st.session_state.search_system = SearchSystem()
if 'video_conference_system' not in st.session_state:
    st.session_state.video_conference_system = VideoConferenceSystem()
if 'backup_system' not in st.session_state:
    st.session_state.backup_system = BackupSystem()
if 'admin_system' not in st.session_state:
    st.session_state.admin_system = AdminSystem()
if 'ai_assistant' not in st.session_state:
    st.session_state.ai_assistant = AIAssistant()
if 'gamification_system' not in st.session_state:
    st.session_state.gamification_system = GamificationSystem()

# Custom CSS for mobile-first design
st.markdown("""
<style>
    /* Hide sidebar completely */
    .css-1d391kg, [data-testid="stSidebar"] {
        display: none !important;
    }
    
    .main > div {
        padding-top: 0.5rem;
        max-width: 100%;
    }
    
    /* Modern tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
        padding: 4px;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: #6c757d;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 12px;
        min-width: 80px;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        color: #495057;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #FF6B6B;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        border-bottom: 3px solid #FF6B6B;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-top: 0;
    }
    
    /* Card styling */
    .club-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        margin: 12px 0;
        border-left: 6px solid #FF6B6B;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .club-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .role-badge {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
        display: inline-block;
    }
    
    .notification {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(255, 227, 173, 0.3);
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .chat-message-own {
        background: linear-gradient(135deg, #FF6B6B, #ff8a80);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
        box-shadow: 0 3px 12px rgba(255, 107, 107, 0.3);
    }
    
    .chat-message-other {
        background: #f8f9fa;
        color: #333;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 70%;
        margin-right: auto;
        box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 11px;
            padding: 0 8px;
            min-width: 60px;
        }
        
        .club-card {
            padding: 16px;
            margin: 8px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check login status
    if 'user' not in st.session_state:
        show_login()
    else:
        show_main_app()

def show_login():
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="color: #FF6B6B; font-size: 2.5em; margin-bottom: 10px;">🌟 폴라리스반</h1>
        <h2 style="color: #4ECDC4; font-size: 1.8em; margin-bottom: 30px;">동아리 관리 시스템</h2>
        <p style="color: #666; font-size: 1.1em;">6학년 폴라리스반의 동아리 활동을 관리하는 통합 플랫폼입니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 로그인")
            username = st.text_input("👤 사용자명", placeholder="사용자명을 입력하세요")
            password = st.text_input("🔑 비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_button = st.form_submit_button("🚀 로그인", use_container_width=True)
            with col_b:
                demo_button = st.form_submit_button("👀 데모 계정", use_container_width=True)
            
            if login_button:
                user = st.session_state.auth_manager.login(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.notification_system.add_notification(
                        f"{user['name']}님이 로그인했습니다.", "info", user['username']
                    )
                    st.success(f"환영합니다, {user['name']}님!")
                    st.rerun()
                else:
                    st.error("❌ 사용자명 또는 비밀번호가 잘못되었습니다.")
            
            if demo_button:
                # Demo account login
                demo_user = st.session_state.auth_manager.login("조성우", "admin")
                if demo_user:
                    st.session_state.user = demo_user
                    st.success("데모 계정으로 로그인되었습니다!")
                    st.rerun()

def show_main_app():
    user = st.session_state.user
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="padding: 10px 0;">
            <h2 style="margin: 0; color: #FF6B6B;">🌟 폴라리스반 동아리</h2>
            <p style="margin: 5px 0; color: #666;">안녕하세요, <strong>{user['name']}</strong>님! 
            <span class="role-badge">{user['role']}</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Notifications indicator
        notifications = st.session_state.notification_system.get_user_notifications(user['username'])
        unread_count = len([n for n in notifications if not n.get('read', False)])
        if unread_count > 0:
            st.markdown(f"🔔 **{unread_count}개 알림**")
    
    with col3:
        if st.button("🚪 로그아웃", use_container_width=True):
            del st.session_state.user
            st.rerun()
    
    st.divider()
    
    # Main navigation tabs with video conference and backup
    if user['role'] == '선생님':
        tabs = st.tabs([
            "🏠 홈", "📝 게시판", "💬 채팅", "📚 과제", "🧠 퀴즈", 
            "📅 일정", "✅ 출석", "🗳️ 투표", "📹 화상회의", "📊 보고서", 
            "🔍 검색", "🔔 알림", "💾 백업", "⚙️ 관리자"
        ])
    elif user['role'] in ['회장', '부회장']:
        tabs = st.tabs([
            "🏠 홈", "📝 게시판", "💬 채팅", "📚 과제", "🧠 퀴즈", 
            "📅 일정", "✅ 출석", "🗳️ 투표", "📹 화상회의", "📊 보고서", 
            "🔍 검색", "🔔 알림"
        ])
    else:
        tabs = st.tabs([
            "🏠 홈", "📝 게시판", "💬 채팅", "📚 과제", "🧠 퀴즈", 
            "📅 일정", "✅ 출석", "🗳️ 투표", "📹 화상회의", "🔍 검색", "🔔 알림"
        ])
    
    # Tab content
    with tabs[0]:  # 홈
        show_home_dashboard(user)
    
    with tabs[1]:  # 게시판
        st.session_state.board_system.show_board_interface(user)
    
    with tabs[2]:  # 채팅
        st.session_state.chat_system.show_chat_interface(user)
    
    with tabs[3]:  # 과제
        st.session_state.assignment_system.show_assignment_interface(user)
    
    with tabs[4]:  # 퀴즈
        st.session_state.quiz_system.show_quiz_interface(user)
    
    with tabs[5]:  # 일정
        st.session_state.schedule_system.show_schedule_interface(user)
    
    with tabs[6]:  # 출석
        st.session_state.attendance_system.show_attendance_interface(user)
    
    with tabs[7]:  # 투표
        st.session_state.vote_system.show_vote_interface(user)
    
    with tabs[8]:  # 화상회의
        st.session_state.video_conference_system.show_conference_interface(user)
    
    # Additional tabs for higher roles
    if user['role'] in ['선생님', '회장', '부회장']:
        with tabs[9]:  # 보고서
            st.session_state.report_generator.show_report_interface(user)
        
        with tabs[10]:  # 검색
            st.session_state.search_system.show_search_interface(user)
        
        with tabs[11]:  # 알림
            st.session_state.notification_system.show_notification_interface(user)
        
        if user['role'] == '선생님':
            with tabs[12]:  # 백업
                st.session_state.backup_system.show_backup_interface(user)
            
            with tabs[13]:  # 관리자
                st.session_state.admin_system.show_admin_interface(user)
    else:
        with tabs[8]:  # 검색
            st.session_state.search_system.show_search_interface(user)
        
        with tabs[9]:  # 알림
            st.session_state.notification_system.show_notification_interface(user)

def show_home_dashboard(user):
    st.markdown("### 📊 대시보드")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    # Get user's clubs
    user_clubs = st.session_state.data_manager.get_user_clubs(user['username'])
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FF6B6B; margin: 0;">🎯</h3>
            <h2 style="margin: 5px 0;">{}</h2>
            <p style="color: #666; margin: 0;">가입 동아리</p>
        </div>
        """.format(len(user_clubs) if not user_clubs.empty else 0), unsafe_allow_html=True)
    
    with col2:
        assignments_df = st.session_state.data_manager.load_csv('assignments')
        pending_assignments = len(assignments_df) if not assignments_df.empty else 0
        
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #4ECDC4; margin: 0;">📚</h3>
            <h2 style="margin: 5px 0;">{}</h2>
            <p style="color: #666; margin: 0;">진행 중 과제</p>
        </div>
        """.format(pending_assignments), unsafe_allow_html=True)
    
    with col3:
        notifications = st.session_state.notification_system.get_user_notifications(user['username'])
        unread_count = len([n for n in notifications if not n.get('read', False)])
        
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #FFA500; margin: 0;">🔔</h3>
            <h2 style="margin: 5px 0;">{}</h2>
            <p style="color: #666; margin: 0;">읽지 않은 알림</p>
        </div>
        """.format(unread_count), unsafe_allow_html=True)
    
    with col4:
        badges_df = st.session_state.data_manager.load_csv('badges')
        user_badges = badges_df[badges_df['username'] == user['username']] if not badges_df.empty else pd.DataFrame()
        
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">🏅</h3>
            <h2 style="margin: 5px 0;">{}</h2>
            <p style="color: #666; margin: 0;">획득 배지</p>
        </div>
        """.format(len(user_badges)), unsafe_allow_html=True)
    
    st.divider()
    
    # Recent activities and club info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 내 동아리")
        if not user_clubs.empty:
            for _, club_info in user_clubs.iterrows():
                clubs_df = st.session_state.data_manager.load_csv('clubs')
                club_detail = clubs_df[clubs_df['name'] == club_info['club_name']]
                
                if not club_detail.empty:
                    club = club_detail.iloc[0]
                    st.markdown(f"""
                    <div class="club-card">
                        <h4>{club['icon']} {club['name']}</h4>
                        <p>{club['description']}</p>
                        <div style="margin-top: 10px;">
                            <span class="role-badge">{club_info['role']}</span>
                            <small style="color: #666; margin-left: 10px;">
                                회장: {club['president']} | 정원: {club['max_members']}명
                            </small>
                        </div>
                        {f'<a href="{club["meet_link"]}" target="_blank" style="color: #FF6B6B; text-decoration: none;">🎥 화상회의 참여</a>' if pd.notna(club['meet_link']) and club['meet_link'] else ''}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("가입된 동아리가 없습니다.")
    
    with col2:
        st.markdown("#### 📢 최근 알림")
        recent_notifications = notifications[:5] if notifications else []
        
        if recent_notifications:
            for notification in recent_notifications:
                read_status = "✅" if notification.get('read', False) else "🔴"
                st.markdown(f"""
                <div class="notification">
                    {read_status} <strong>{notification['title']}</strong><br>
                    <small style="color: #666;">{notification['created_date']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("새로운 알림이 없습니다.")

if __name__ == "__main__":
    main()
